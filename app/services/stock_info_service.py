"""
股票信息服务模块

从本地JSON文件查询股票信息
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class StockInfoService:
    """股票信息服务类 - 从本地JSON文件查询"""
    
    def __init__(self):
        pass
    
    def query_from_local_files(self,
                               exchange_code: Optional[str] = None,
                               keyword: Optional[str] = None,
                               is_active: bool = True,
                               limit: int = 100) -> Dict[str, Any]:
        """
        从本地JSON文件查询股票信息
        
        Args:
            exchange_code: 交易所代码
            keyword: 搜索关键词
            is_active: 是否只返回活跃股票
            limit: 返回数量限制
            
        Returns:
            Dict: 查询结果
        """
        try:
            from constants.stock_lists_loader import stock_lists_manager
            
            # 获取股票列表
            if exchange_code:
                stocks = stock_lists_manager.get_exchange_stocks(exchange_code.upper())
            else:
                stocks = stock_lists_manager.get_active_stocks() if is_active else list(stock_lists_manager.stocks_by_symbol.values())
            
            # 关键词搜索
            if keyword:
                stocks = [s for s in stocks if keyword.lower() in s.name.lower() or keyword in s.ticker]
            
            # 限制数量
            stocks = stocks[:limit]
            
            # 格式化输出
            stock_list = []
            for stock in stocks:
                stock_list.append({
                    'ticker': stock.ticker,
                    'name': stock.name,
                    'symbol': stock.symbol,
                    'exchange_code': stock.exchange_code,
                    'exchange_name_cn': stock.exchange_name_cn,
                    'is_active': stock.is_active,
                    'country_code': stock.country_code,
                    'currency_code': stock.currency_code,
                    'first_fetch_time': stock.first_fetch_time
                })
            
            return {
                'success': True,
                'data': stock_list,
                'count': len(stock_list),
                'source': 'local_json'
            }
            
        except Exception as e:
            logger.error(f"从本地文件查询股票信息错误: {e}")
            return {
                'success': False,
                'data': [],
                'count': 0,
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取股票清单统计信息"""
        try:
            from constants.stock_lists_loader import stock_lists_manager
            
            stats = stock_lists_manager.get_statistics()
            
            return {
                'success': True,
                'data': stats
            }
            
        except Exception as e:
            logger.error(f"获取统计信息错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }

