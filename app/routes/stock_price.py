"""
股票行情数据查询路由模块

提供从TimescaleDB查询历史数据的接口
"""

from flask import Blueprint, request
from app.utils.responses import (
    create_stock_data_response, 
    create_error_response,
    create_success_response,
    format_stock_price_data,
    validate_date_range,
    validate_symbol_format
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
stock_price_bp = Blueprint('stock_price', __name__)


@stock_price_bp.route('/query', methods=['GET', 'POST'])
def query_from_database():
    """从TimescaleDB查询股票行情数据"""
    try:
        # 获取请求参数
        if request.method == 'POST':
            data = request.get_json() or {}
            symbol = data.get('symbol', '')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            limit = data.get('limit', 100)
        else:
            symbol = request.args.get('symbol', '')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            limit = request.args.get('limit', 100, type=int)
        
        # 验证参数
        if not symbol:
            return create_error_response(400, "股票代码不能为空")
        
        symbol = validate_symbol_format(symbol)
        date_range = validate_date_range(start_date, end_date)
        
        if limit <= 0 or limit > 10000:
            return create_error_response(400, "数据条数限制应在1-10000之间")
        
        # 查询数据库
        from app.services.stock_data_service import StockDataService
        service = StockDataService()
        
        db_result = service.query_stock_data_from_db(
            symbol=symbol,
            start_date=date_range['start_date'],
            end_date=date_range['end_date'],
            limit=limit
        )
        
        if not db_result['success']:
            return create_error_response(
                500, 
                "数据库查询失败", 
                db_result.get('error', '未知错误')
            )
        
        # 格式化响应
        stock_data = [format_stock_price_data(record) for record in db_result['data']]
        
        # 计算日期范围
        actual_date_range = None
        if stock_data:
            dates = [item['trade_date'] for item in stock_data]
            actual_date_range = {
                "start": min(dates),
                "end": max(dates),
                "count": len(stock_data)
            }
        
        return create_stock_data_response(
            data=stock_data,
            symbol=symbol,
            source="database",
            date_range=actual_date_range,
            total=db_result['total']
        )
        
    except ValueError as e:
        return create_error_response(400, "参数错误", str(e))
    except Exception as e:
        logger.error(f"数据库查询异常: {e}")
        return create_error_response(500, "查询失败", str(e))


@stock_price_bp.route('/info/<symbol>', methods=['GET'])
def get_stock_info(symbol: str):
    """获取股票基础信息"""
    try:
        symbol = validate_symbol_format(symbol)
        
        from app.services.stock_data_service import StockDataService
        service = StockDataService()
        
        result = service.get_stock_info_from_db(symbol)
        
        if result['success']:
            return create_success_response(
                data=result['data'],
                message="查询成功"
            )
        else:
            return create_error_response(
                404,
                "未找到股票信息",
                result.get('error', '未知错误')
            )
            
    except ValueError as e:
        return create_error_response(400, "参数错误", str(e))
    except Exception as e:
        logger.error(f"查询股票信息异常: {e}")
        return create_error_response(500, "查询失败", str(e))


@stock_price_bp.route('/list', methods=['GET'])
def list_stocks():
    """列出所有股票（包含最新价格信息）"""
    try:
        market_code = request.args.get('market_code')
        is_active = request.args.get('is_active', 'Y')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 限制最大查询数量，防止性能问题
        if limit > 10000:
            return create_error_response(
                400,
                "参数错误",
                "limit参数不能超过10000，建议使用分页查询"
            )
        
        if limit <= 0:
            return create_error_response(400, "参数错误", "limit必须大于0")
        
        if offset < 0:
            return create_error_response(400, "参数错误", "offset不能为负数")
        
        from app.services.stock_data_service import StockDataService
        service = StockDataService()
        
        # 使用新方法获取包含价格数据的股票列表
        result = service.list_stocks_with_latest_price(
            market_code=market_code,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        if result['success']:
            return create_success_response(
                data=result['data'],
                total=result['total'],
                message=f"查询到 {result['count']} 只股票"
            )
        else:
            return create_error_response(
                500,
                "查询失败",
                result.get('error', '未知错误')
            )
            
    except Exception as e:
        logger.error(f"列出股票异常: {e}")
        return create_error_response(500, "查询失败", str(e))

