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
        
        script = data.get('script', '')
        script_id = data.get('script_id')
        column_name = data.get('column_name', '')
        stock_symbols = data.get('stock_symbols', [])
        
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
            return create_error_response(400, "参数错误", "script或script_id不能为空")
        
        if not column_name:
            return create_error_response(400, "参数错误", "column_name不能为空")
        
        if not stock_symbols or not isinstance(stock_symbols, list):
            return create_error_response(400, "参数错误", "stock_symbols必须是非空数组")
        
        if len(stock_symbols) > 200:
            return create_error_response(400, "参数错误", "stock_symbols最多支持200个")
        
        # 导入服务
        from app.services.sandbox_executor import SandboxExecutor
        executor = SandboxExecutor()
        
        # 验证脚本语法
        is_valid, syntax_error = executor.validate_syntax(script)
        if not is_valid:
            return create_error_response(
                400,
                "脚本语法错误",
                syntax_error
            )
        
        # 获取股票数据（TODO: 从数据库获取）
        results = []
        
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
                    continue
                
                # 执行脚本
                result, error = executor.execute(script, {"row": stock_row})
                
                results.append({
                    "symbol": symbol,
                    "value": result,
                    "error": error
                })
                
            except Exception as e:
                logger.error(f"执行脚本失败，股票: {symbol}, 错误: {e}")
                results.append({
                    "symbol": symbol,
                    "value": None,
                    "error": str(e)
                })
        
        return create_success_response(
            data={"results": results},
            message="执行成功"
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

