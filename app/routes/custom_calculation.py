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
        column_name = data.get('column_name', '')
        stock_symbols = data.get('stock_symbols', [])
        
        # 验证参数
        if not script:
            return create_error_response(400, "参数错误", "script不能为空")
        
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
                # TODO: 获取股票数据
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


def _get_stock_data(symbol: str) -> Optional[Dict[str, Any]]:
    """获取股票数据（临时实现，后续从数据库获取）"""
    # TODO: 从TimescaleDB获取最新的股票数据
    return {
        "symbol": symbol,
        "close_price": 100.0,
        "volume": 1000000,
        "turnover": 100000000.0
    }

