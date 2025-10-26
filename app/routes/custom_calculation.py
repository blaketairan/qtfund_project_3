"""
自定义计算路由模块

提供Python脚本执行API用于股票量化分析仪表盘
"""

from flask import Blueprint, request
from app.utils.responses import create_success_response, create_error_response
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# 创建蓝图
custom_calculation_bp = Blueprint('custom_calculation', __name__)


@custom_calculation_bp.route('/execute', methods=['POST'])
def execute_script():
    """执行自定义Python脚本"""
    try:
        # 获取请求参数
        data = request.get_json() or {}
        
        logger.info(f"=== 收到API请求 ===")
        logger.info(f"请求数据: {str(data)[:200] if data else 'empty'}")
        
        script = data.get('script', '')
        script_id = data.get('script_id')
        column_name = data.get('column_name', '')
        stock_symbols = data.get('stock_symbols', [])
        
        logger.info(f"解析参数: script长度={len(script)}, script_id={script_id}, column_name={column_name}, stock_symbols类型={type(stock_symbols)}, stock_symbols值={stock_symbols}")
        
        # 如果提供了script_id，从数据库加载脚本
        if script_id:
            from app.models.custom_script import CustomScriptService
            saved_script = CustomScriptService.get_by_id(script_id)
            if not saved_script:
                return create_error_response(404, "未找到脚本", f"脚本ID {script_id} 不存在")
            script = saved_script.code
            logger.info(f"加载保存的脚本: ID={script_id}, name={saved_script.name}")
        
        # 验证参数
        if not script:
            logger.error(f"参数验证失败: script为空, script_id={script_id}")
            return create_error_response(400, "参数错误", "script或script_id不能为空")
        
        if not column_name:
            logger.error(f"参数验证失败: column_name为空")
            return create_error_response(400, "参数错误", "column_name不能为空")
        
        if stock_symbols is None:
            stock_symbols = []
        
        if not isinstance(stock_symbols, list):
            logger.error(f"参数验证失败: stock_symbols不是数组, 类型={type(stock_symbols)}, 值={stock_symbols}")
            return create_error_response(400, "参数错误", f"stock_symbols必须是数组，当前类型: {type(stock_symbols)}")
        
        # 处理空数组情况：获取所有活跃股票
        if len(stock_symbols) == 0:
            from app.services.stock_data_service import StockDataService
            service = StockDataService()
            all_stocks = service.get_all_active_stocks()
            stock_symbols = all_stocks
            
            if not stock_symbols:
                return create_error_response(404, "未找到股票", "数据库中没有活跃股票")
            logger.info(f"自动获取 {len(stock_symbols)} 只活跃股票")
        
        if len(stock_symbols) > 200:
            return create_error_response(400, "参数错误", "stock_symbols最多支持200个")
        
        logger.info(f"执行自定义计算: column_name={column_name}, stocks={len(stock_symbols)}")
        
        # 调试日志：记录参数信息
        logger.info(f"DEBUG: script长度={len(script)}, column_name={column_name}, stock_symbols数量={len(stock_symbols)}")
        
        # 导入服务
        from app.services.sandbox_executor import SandboxExecutor
        executor = SandboxExecutor()
        
        # 验证脚本语法
        is_valid, syntax_error = executor.validate_syntax(script)
        if not is_valid:
            logger.error(f"脚本语法验证失败: {syntax_error}")
            logger.error(f"问题脚本的前100个字符: {script[:100] if script else 'empty'}")
            return create_error_response(
                400,
                "脚本语法错误",
                f"Script validation failed: {syntax_error}"
            )
        
        # 获取股票数据（TODO: 从数据库获取）
        results = []
        successful = 0
        failed = 0
        
        # 对每个股票执行脚本
        for symbol in stock_symbols:
            try:
                # 获取股票数据
                stock_row = _get_stock_data(symbol)
                
                if stock_row is None:
                    results.append({
                        "symbol": symbol,
                        "value": None,
                        "error": "股票数据不存在"
                    })
                    failed += 1
                    continue
                
                # 执行脚本
                result, error = executor.execute(script, {"row": stock_row})
                
                results.append({
                    "symbol": symbol,
                    "value": result,
                    "error": error
                })
                
                if error:
                    failed += 1
                else:
                    successful += 1
                
            except Exception as e:
                logger.error(f"执行脚本失败，股票: {symbol}, 错误: {e}")
                results.append({
                    "symbol": symbol,
                    "value": None,
                    "error": str(e)
                })
                failed += 1
        
        # 准备响应数据
        response_data = {"results": results}
        
        # 添加执行摘要（当处理多只股票时）
        if len(results) > 1:
            response_data["summary"] = {
                "total": len(results),
                "successful": successful,
                "failed": failed
            }
        
        return create_success_response(
            data=response_data,
            message=f"执行成功，处理 {len(results)} 只股票"
        )
        
    except Exception as e:
        logger.error(f"执行自定义计算失败: {e}")
        return create_error_response(500, "执行失败", str(e))


# ==================== Script Management Endpoints ====================


@custom_calculation_bp.route('/scripts', methods=['POST'])
def create_script():
    """创建新脚本"""
    try:
        data = request.get_json() or {}
        
        name = data.get('name', '').strip()
        code = data.get('code', '').strip()
        description = data.get('description', '').strip()
        
        # 验证参数
        if not name:
            return create_error_response(400, "参数错误", "name不能为空")
        
        if not code:
            return create_error_response(400, "参数错误", "code不能为空")
        
        # 验证脚本语法
        from app.services.sandbox_executor import SandboxExecutor
        executor = SandboxExecutor()
        is_valid, syntax_error = executor.validate_syntax(code)
        if not is_valid:
            return create_error_response(400, "脚本语法错误", syntax_error)
        
        # 保存脚本
        from app.models.custom_script import CustomScriptService
        script = CustomScriptService.save(name, code, description)
        
        return create_success_response(
            data=script.to_dict(),
            message="脚本创建成功"
        )
        
    except Exception as e:
        logger.error(f"创建脚本失败: {e}")
        return create_error_response(500, "创建失败", str(e))


@custom_calculation_bp.route('/scripts', methods=['GET'])
def list_scripts():
    """获取所有脚本列表"""
    try:
        from app.models.custom_script import CustomScriptService
        
        scripts = CustomScriptService.get_all()
        
        script_list = [script.to_dict() for script in scripts]
        
        return create_success_response(
            data=script_list,
            message=f"查询到 {len(script_list)} 个脚本"
        )
        
    except Exception as e:
        logger.error(f"获取脚本列表失败: {e}")
        return create_error_response(500, "查询失败", str(e))


@custom_calculation_bp.route('/scripts/<int:script_id>', methods=['GET'])
def get_script(script_id: int):
    """获取特定脚本"""
    try:
        from app.models.custom_script import CustomScriptService
        
        script = CustomScriptService.get_by_id(script_id)
        
        if not script:
            return create_error_response(404, "未找到脚本", f"脚本ID {script_id} 不存在")
        
        return create_success_response(
            data=script.to_dict(),
            message="查询成功"
        )
        
    except Exception as e:
        logger.error(f"获取脚本失败: {e}")
        return create_error_response(500, "查询失败", str(e))


@custom_calculation_bp.route('/scripts/<int:script_id>', methods=['PUT'])
def update_script(script_id: int):
    """更新脚本"""
    try:
        data = request.get_json() or {}
        
        name = data.get('name', '').strip() or None
        code = data.get('code', '').strip() or None
        description = data.get('description', '').strip() or None
        
        # 如果更新代码，验证语法
        if code:
            from app.services.sandbox_executor import SandboxExecutor
            executor = SandboxExecutor()
            is_valid, syntax_error = executor.validate_syntax(code)
            if not is_valid:
                return create_error_response(400, "脚本语法错误", syntax_error)
        
        from app.models.custom_script import CustomScriptService
        script = CustomScriptService.update(script_id, name, code, description)
        
        if not script:
            return create_error_response(404, "未找到脚本", f"脚本ID {script_id} 不存在")
        
        return create_success_response(
            data=script.to_dict(),
            message="更新成功"
        )
        
    except Exception as e:
        logger.error(f"更新脚本失败: {e}")
        return create_error_response(500, "更新失败", str(e))


@custom_calculation_bp.route('/scripts/<int:script_id>', methods=['DELETE'])
def delete_script(script_id: int):
    """删除脚本"""
    try:
        from app.models.custom_script import CustomScriptService
        
        success = CustomScriptService.delete(script_id)
        
        if not success:
            return create_error_response(404, "未找到脚本", f"脚本ID {script_id} 不存在")
        
        return create_success_response(
            data=None,
            message="删除成功"
        )
        
    except Exception as e:
        logger.error(f"删除脚本失败: {e}")
        return create_error_response(500, "删除失败", str(e))


def _get_stock_data(symbol: str) -> Optional[Dict[str, Any]]:
    """从TimescaleDB获取最新的股票数据"""
    try:
        from database.connection import db_manager
        from models.stock_data import StockDailyData
        from sqlalchemy import desc
        
        with db_manager.get_session() as session:
            # 查询指定股票的最近一条行情数据
            stock_data = session.query(StockDailyData).filter(
                StockDailyData.symbol == symbol
            ).order_by(desc(StockDailyData.trade_date)).first()
            
            if stock_data is None:
                return None
            
            # 构建stock_row字典
            return {
                "symbol": str(stock_data.symbol),
                "stock_name": str(stock_data.stock_name),
                "trade_date": stock_data.trade_date.strftime('%Y-%m-%d') if stock_data.trade_date else None,
                "open_price": float(stock_data.open_price) if stock_data.open_price is not None else None,
                "high_price": float(stock_data.high_price) if stock_data.high_price is not None else None,
                "low_price": float(stock_data.low_price) if stock_data.low_price is not None else None,
                "close_price": float(stock_data.close_price),
                "volume": int(stock_data.volume),
                "turnover": float(stock_data.turnover),
                "price_change": float(stock_data.price_change) if stock_data.price_change is not None else None,
                "price_change_pct": float(stock_data.price_change_pct) if stock_data.price_change_pct is not None else None,
                "premium_rate": float(stock_data.premium_rate) if stock_data.premium_rate is not None else None,
                "market_code": str(stock_data.market_code)
            }
            
    except Exception as e:
        logger.error(f"获取股票数据失败: {symbol}, 错误: {e}")
        return None


@custom_calculation_bp.route('/functions', methods=['GET'])
def list_available_functions():
    """获取可用于脚本的函数和模块列表（用于前端显示帮助）"""
    try:
        # 定义可用的函数
        functions_data = {
            "functions": [
                {
                    "name": "get_history",
                    "signature": "get_history(symbol: str, days: int) -> list",
                    "description": "获取股票的历史价格数据",
                    "parameters": [
                        {
                            "name": "symbol",
                            "type": "str",
                            "description": "股票代码（如 'SH.600519'）"
                        },
                        {
                            "name": "days",
                            "type": "int",
                            "description": "获取的交易天数（1-1000，默认250）"
                        }
                    ],
                    "returns": "历史价格数据列表，每个元素包含 close_price, trade_date, volume, price_change_pct",
                    "example": "history = get_history('SH.600519', 250)"
                }
            ],
            "modules": [
                {
                    "name": "math",
                    "description": "Python数学模块",
                    "functions": [
                        {
                            "name": "exp",
                            "description": "计算e的x次方"
                        },
                        {
                            "name": "log",
                            "description": "计算自然对数"
                        },
                        {
                            "name": "pow",
                            "description": "计算x的y次方"
                        },
                        {
                            "name": "sqrt",
                            "description": "计算平方根"
                        },
                        {
                            "name": "sin, cos, tan",
                            "description": "三角函数"
                        }
                    ]
                }
            ],
            "builtins": [
                {
                    "name": "abs",
                    "description": "绝对值"
                },
                {
                    "name": "min, max, sum",
                    "description": "数学函数"
                },
                {
                    "name": "round",
                    "description": "四舍五入"
                },
                {
                    "name": "len, range, zip, enumerate",
                    "description": "序列操作函数"
                },
                {
                    "name": "str, int, float, bool, list, dict, tuple, set",
                    "description": "类型转换和构造"
                }
            ],
            "context": {
                "name": "row",
                "description": "当前股票数据对象",
                "properties": [
                    {"name": "symbol", "type": "str", "description": "股票代码"},
                    {"name": "stock_name", "type": "str", "description": "股票名称"},
                    {"name": "close_price", "type": "float", "description": "收盘价"},
                    {"name": "volume", "type": "int", "description": "成交量"},
                    {"name": "price_change_pct", "type": "float", "description": "涨跌幅"},
                    {"name": "trade_date", "type": "str", "description": "交易日期"}
                ],
                "example": "price = row['close_price']"
            }
        }
        
        return create_success_response(
            data=functions_data,
            message="查询成功"
        )
        
    except Exception as e:
        logger.error(f"获取函数列表失败: {e}")
        return create_error_response(500, "查询失败", str(e))

