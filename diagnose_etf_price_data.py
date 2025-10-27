#!/usr/bin/env python3
"""
诊断ETF价格数据问题
"""

from database.connection import db_manager
from sqlalchemy import text

def diagnose_etf_data():
    """诊断ETF数据"""
    try:
        with db_manager.get_session() as session:
            print("=" * 60)
            print("ETF数据诊断报告")
            print("=" * 60)
            
            # 1. 检查ETF总数
            result = session.execute(text("SELECT COUNT(*) FROM stock_info WHERE is_etf = 'Y'"))
            total_etfs = result.scalar()
            print(f"\n1. ETF总数: {total_etfs}")
            
            # 2. 检查有价格数据的ETF数量
            result = session.execute(text("""
                SELECT COUNT(DISTINCT si.symbol)
                FROM stock_info si
                INNER JOIN stock_daily_data sd ON sd.symbol = si.symbol
                WHERE si.is_etf = 'Y'
            """))
            etfs_with_data = result.scalar()
            print(f"2. 有价格数据的ETF数: {etfs_with_data}")
            
            if total_etfs > 0:
                coverage = (etfs_with_data / total_etfs * 100) if total_etfs > 0 else 0
                print(f"   覆盖率: {coverage:.1f}%")
            
            # 3. 检查前5个ETF及其价格数据
            print("\n3. 前5个ETF及其价格数据情况:")
            result = session.execute(text("""
                SELECT 
                    si.symbol,
                    si.stock_name,
                    COUNT(sd.trade_date) as price_record_count,
                    MAX(sd.trade_date) as latest_trade_date
                FROM stock_info si
                LEFT JOIN stock_daily_data sd ON sd.symbol = si.symbol
                WHERE si.is_etf = 'Y'
                GROUP BY si.symbol, si.stock_name
                ORDER BY si.symbol
                LIMIT 5
            """))
            for row in result.fetchall():
                print(f"  {row.symbol}: {row.stock_name}")
                print(f"    价格记录数: {row.price_record_count}")
                print(f"    最新交易日: {row.latest_trade_date}")
            
            # 4. 检查LATERAL JOIN查询是否能获取价格
            print("\n4. 测试LATERAL JOIN查询:")
            result = session.execute(text("""
                SELECT 
                    si.symbol,
                    si.stock_name,
                    lp.close_price,
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
                WHERE si.is_etf = 'Y'
                LIMIT 5
            """))
            for row in result.fetchall():
                print(f"  {row.symbol} ({row.stock_name}): price={row.close_price}, date={row.latest_trade_date}")
            
            print("\n" + "=" * 60)
            print("诊断完成")
            print("=" * 60)
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_etf_data()

