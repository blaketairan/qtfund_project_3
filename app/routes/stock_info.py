"""
股票信息查询路由模块

从本地JSON文件查询股票信息
"""

from flask import Blueprint, request
from app.utils.responses import create_success_response, create_error_response, create_data_response
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
stock_info_bp = Blueprint('stock_info', __name__)


@stock_info_bp.route('/local', methods=['GET'])
def query_from_local():
    """从本地JSON文件查询股票信息"""
    try:
        # 获取请求参数
        exchange_code = request.args.get('exchange_code')
        keyword = request.args.get('keyword')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        limit = request.args.get('limit', 100, type=int)
        
        from app.services.stock_info_service import StockInfoService
        service = StockInfoService()
        
        result = service.query_from_local_files(
            exchange_code=exchange_code,
            keyword=keyword,
            is_active=is_active,
            limit=limit
        )
        
        if result['success']:
            return create_data_response(
                data=result['data'],
                message=f"查询到 {result['count']} 只股票"
            )
        else:
            return create_error_response(
                500,
                "查询失败",
                result.get('error', '未知错误')
            )
            
    except Exception as e:
        logger.error(f"从本地文件查询股票信息异常: {e}")
        return create_error_response(500, "查询失败", str(e))


@stock_info_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取股票清单统计信息"""
    try:
        from app.services.stock_info_service import StockInfoService
        service = StockInfoService()
        
        result = service.get_statistics()
        
        if result['success']:
            return create_success_response(
                data=result['data'],
                message="统计信息查询成功"
            )
        else:
            return create_error_response(
                500,
                "查询失败",
                result.get('error', '未知错误')
            )
            
    except Exception as e:
        logger.error(f"获取统计信息异常: {e}")
        return create_error_response(500, "查询失败", str(e))

