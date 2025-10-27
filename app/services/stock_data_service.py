"""
股票数据查询服务模块

提供从数据库查询股票数据的统一接口
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StockDataService:
    """股票数据查询服务类 - 仅提供数据库查询功能"""

    def __init__(self):
        pass
    
    def query_stock_data_from_db(self, 
                               symbol: str,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None,
                               limit: int = 100) -> Dict[str, Any]:
        """
        从TimescaleDB查询股票数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数限制
            
        Returns:
            Dict: 查询结果
        """
        try:
            from database.connection import db_manager
            from models.stock_data import StockDailyData
            from sqlalchemy import desc
            
            with db_manager.get_session() as session:
                # 构建查询
                query = session.query(StockDailyData).filter(
                    StockDailyData.symbol == symbol
                )
                
                # 添加日期范围过滤
                if start_date:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    query = query.filter(StockDailyData.trade_date >= start_dt)
                
                if end_date:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(StockDailyData.trade_date <= end_dt)
                
                # 按日期降序排列
                query = query.order_by(desc(StockDailyData.trade_date))
                
                # 获取总记录数
                total_count = query.count()
                
                # 限制返回数量
                results = query.limit(limit).all()
                
                return {
                    'success': True,
                    'data': results,
                    'total': total_count,
                    'count': len(results)
                }
                
        except Exception as e:
            logger.error(f"数据库查询错误: {e}")
            return {
                'success': False,
                'data': [],
                'total': 0,
                'count': 0,
                'error': str(e)
            }
    
    def get_stock_info_from_db(self, symbol: str) -> Dict[str, Any]:
        """
        从数据库获取股票基础信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            Dict: 股票信息
        """
        try:
            from database.connection import db_manager
            from models.stock_data import StockInfo
            
            with db_manager.get_session() as session:
                stock_info = session.query(StockInfo).filter(
                    StockInfo.symbol == symbol
                ).first()
                
                if stock_info:
                    return {
                        'success': True,
                        'data': {
                            'symbol': stock_info.symbol,
                            'stock_name': stock_info.stock_name,
                            'stock_code': stock_info.stock_code,
                            'market_code': stock_info.market_code,
                            'stock_type': stock_info.stock_type,
                            'industry': stock_info.industry,
                            'is_active': stock_info.is_active,
                            'last_sync_date': stock_info.last_sync_date.isoformat() if stock_info.last_sync_date else None,
                            'created_at': stock_info.created_at.isoformat() if stock_info.created_at else None
                        }
                    }
                else:
                    return {
                        'success': False,
                        'data': None,
                        'error': '未找到股票信息'
                    }
                    
        except Exception as e:
            logger.error(f"获取股票信息错误: {e}")
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def list_all_stocks_from_db(self, 
                               market_code: Optional[str] = None,
                               is_active: str = 'Y',
                               limit: int = 100,
                               offset: int = 0) -> Dict[str, Any]:
        """
        从数据库列出所有股票
        
        Args:
            market_code: 市场代码过滤
            is_active: 是否活跃
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            Dict: 股票列表
        """
        try:
            from database.connection import db_manager
            from models.stock_data import StockInfo
            
            with db_manager.get_session() as session:
                query = session.query(StockInfo)
                
                if market_code:
                    query = query.filter(StockInfo.market_code == market_code.upper())
                
                if is_active:
                    query = query.filter(StockInfo.is_active == is_active)
                
                total_count = query.count()
                
                stocks = query.offset(offset).limit(limit).all()
                
                stock_list = []
                for stock in stocks:
                    stock_list.append({
                        'symbol': stock.symbol,
                        'stock_name': stock.stock_name,
                        'market_code': stock.market_code,
                        'is_active': stock.is_active,
                        'last_sync_date': stock.last_sync_date.isoformat() if stock.last_sync_date else None
                    })
                
                return {
                    'success': True,
                    'data': stock_list,
                    'total': total_count,
                    'count': len(stock_list)
                }
                
        except Exception as e:
            logger.error(f"列出股票错误: {e}")
            return {
                'success': False,
                'data': [],
                'total': 0,
                'count': 0,
                'error': str(e)
            }
    
    def list_stocks_with_latest_price(self,
                                      market_code: Optional[str] = None,
                                      is_active: str = 'Y',
                                      is_etf: Optional[bool] = None,
                                      limit: int = 100,
                                      offset: int = 0) -> Dict[str, Any]:
        """
        从数据库列出所有股票，包含最新的价格信息
        
        使用 LATERAL JOIN 高效查询每只股票的最新价格、涨跌幅和成交量。
        
        Args:
            market_code: 市场代码过滤（SH/SZ/BJ）
            is_active: 是否活跃（Y/N）
            is_etf: ETF筛选（True-仅ETF, False-仅股票, None-全部）
            limit: 返回数量限制
            offset: 分页偏移量
            
        Returns:
            Dict: 包含股票列表和最新价格数据
        """
        try:
            from database.connection import db_manager
            from sqlalchemy import text
            
            with db_manager.get_session() as session:
                # 构建 LATERAL JOIN 查询
                query = """
                SELECT 
                    si.symbol,
                    si.stock_name,
                    si.market_code,
                    si.is_active,
                    si.is_etf,
                    si.last_sync_date,
                    lp.close_price,
                    lp.volume,
                    lp.price_change_pct,
                    lp.trade_date as latest_trade_date
                FROM stock_info si
                LEFT JOIN LATERAL (
                    SELECT 
                        close_price, 
                        volume, 
                        price_change_pct,
                        trade_date
                    FROM stock_daily_data sd
                    WHERE sd.symbol = si.symbol
                    ORDER BY sd.trade_date DESC
                    LIMIT 1
                ) lp ON true
                WHERE si.is_active = :is_active
                """
                
                params = {
                    'is_active': is_active,
                    'market_code': market_code,
                    'limit': limit,
                    'offset': offset
                }
                
                # 添加市场过滤
                if market_code:
                    query += " AND si.market_code = :market_code"
                
                # 添加ETF过滤
                if is_etf is not None:
                    if is_etf:
                        query += " AND si.is_etf = 'Y'"
                    else:
                        query += " AND si.is_etf = 'N'"
                
                # 添加排序和分页
                query += " ORDER BY si.symbol LIMIT :limit OFFSET :offset"
                
                # 执行查询
                result = session.execute(text(query), params)
                rows = result.fetchall()
                
                # 格式化结果
                stock_list = []
                for row in rows:
                    stock_list.append({
                        'symbol': row.symbol,
                        'stock_name': row.stock_name,
                        'market_code': row.market_code,
                        'is_active': row.is_active,
                        'is_etf': row.is_etf == 'Y',  # Convert CHAR to boolean
                        'last_sync_date': row.last_sync_date.isoformat() if row.last_sync_date else None,
                        'close_price': float(row.close_price) if row.close_price is not None else None,
                        'price_change_pct': float(row.price_change_pct) if row.price_change_pct is not None else None,
                        'volume': int(row.volume) if row.volume is not None else None,
                        'latest_trade_date': row.latest_trade_date.strftime('%Y-%m-%d') if row.latest_trade_date else None
                    })
                
                # 获取总数（用于分页）
                count_query = """
                SELECT COUNT(*) 
                FROM stock_info si
                WHERE si.is_active = :is_active
                """
                count_params = {'is_active': is_active}
                
                if market_code:
                    count_query += " AND si.market_code = :market_code"
                    count_params['market_code'] = market_code
                
                if is_etf is not None:
                    if is_etf:
                        count_query += " AND si.is_etf = 'Y'"
                    else:
                        count_query += " AND si.is_etf = 'N'"
                
                total_count = session.execute(text(count_query), count_params).scalar()
                
                return {
                    'success': True,
                    'data': stock_list,
                    'total': total_count,
                    'count': len(stock_list)
                }
                
        except Exception as e:
            logger.error(f"列出股票错误: {e}")
            return {
                'success': False,
                'data': [],
                'total': 0,
                'count': 0,
                'error': str(e)
            }
    
    def get_all_active_stocks(self, market_code: Optional[str] = None) -> List[str]:
        """
        获取所有活跃股票代码
        
        Args:
            market_code: 市场代码过滤（可选，SH/SZ/BJ）
            
        Returns:
            List[str]: 股票代码列表
        """
        try:
            from database.connection import db_manager
            from models.stock_data import StockInfo
            
            with db_manager.get_session() as session:
                query = session.query(StockInfo.symbol).filter(
                    StockInfo.is_active == 'Y'
                )
                
                if market_code:
                    query = query.filter(StockInfo.market_code == market_code)
                
                results = query.all()
                return [row.symbol for row in results]
                
        except Exception as e:
            logger.error(f"获取所有活跃股票失败: {e}")
            return []

