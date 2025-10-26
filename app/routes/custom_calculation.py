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

