# Quickstart: Stock Data Display Implementation

**Feature**: 004-stock-data-display  
**Date**: 2025-01-27

## Overview

Enhance the stock list API (`GET /api/stock-price/list`) to return latest price data (close_price, price_change_pct, volume) for each stock.

## What's Changing

### Before
API returned only basic stock information:
```json
{
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "market_code": "SH",
      "is_active": "Y"
    }
  ]
}
```

### After
API now includes latest price data:
```json
{
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "market_code": "SH",
      "is_active": "Y",
      "last_sync_date": "2025-01-26T00:00:00",
      "close_price": 1750.50,
      "price_change_pct": 2.35,
      "volume": 12500000,
      "latest_trade_date": "2025-01-26"
    }
  ]
}
```

## Implementation Steps

### 1. Modify Service Layer

**File**: `app/services/stock_data_service.py`

Add new method `list_stocks_with_latest_price()`:

```python
def list_stocks_with_latest_price(self, 
                                  market_code: Optional[str] = None,
                                  is_active: str = 'Y',
                                  limit: int = 100,
                                  offset: int = 0) -> Dict[str, Any]:
    """
    List stocks with their latest price data using LATERAL JOIN.
    
    Args:
        market_code: Filter by market (SH/SZ/BJ)
        is_active: Filter by active status
        limit: Results per page
        offset: Pagination offset
        
    Returns:
        Dict with success, data, total, count
    """
    try:
        from database.connection import db_manager
        from sqlalchemy import text
        
        with db_manager.get_session() as session:
            query = """
            SELECT 
                si.symbol,
                si.stock_name,
                si.market_code,
                si.is_active,
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
            
            # Add market filter if provided
            if market_code:
                query += " AND si.market_code = :market_code"
            
            query += " ORDER BY si.symbol LIMIT :limit OFFSET :offset"
            
            # Execute query
            result = session.execute(text(query), params)
            rows = result.fetchall()
            
            # Format results
            stock_list = []
            for row in rows:
                stock_list.append({
                    'symbol': row.symbol,
                    'stock_name': row.stock_name,
                    'market_code': row.market_code,
                    'is_active': row.is_active,
                    'last_sync_date': row.last_sync_date.isoformat() if row.last_sync_date else None,
                    'close_price': float(row.close_price) if row.close_price is not None else None,
                    'price_change_pct': float(row.price_change_pct) if row.price_change_pct is not None else None,
                    'volume': int(row.volume) if row.volume is not None else None,
                    'latest_trade_date': row.latest_trade_date.strftime('%Y-%m-%d') if row.latest_trade_date else None
                })
            
            # Get total count (for pagination)
            count_query = """
            SELECT COUNT(*) 
            FROM stock_info si
            WHERE si.is_active = :is_active
            """
            count_params = {'is_active': is_active}
            
            if market_code:
                count_query += " AND si.market_code = :market_code"
            
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
```

### 2. Modify Route Handler

**File**: `app/routes/stock_price.py`

Update the `list_stocks()` endpoint to use new service method:

```python
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
        
        # Use new method that includes price data
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
```

## Testing

### Manual Testing

1. **Start the application**:
```bash
python start_flask_app.py
```

2. **Test API endpoint**:
```bash
curl "http://localhost:5000/api/stock-price/list?limit=10"
```

3. **Expected response**:
```json
{
  "code": 200,
  "message": "查询到 10 只股票",
  "timestamp": "2025-01-27 10:30:45",
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "market_code": "SH",
      "is_active": "Y",
      "last_sync_date": "2025-01-26T00:00:00",
      "close_price": 1750.50,
      "price_change_pct": 2.35,
      "volume": 12500000,
      "latest_trade_date": "2025-01-26"
    }
  ],
  "total": 250,
  "count": 10
}
```

4. **Test with market filter**:
```bash
curl "http://localhost:5000/api/stock-price/list?market_code=SH&limit=5"
```

5. **Test pagination**:
```bash
curl "http://localhost:5000/api/stock-price/list?limit=10&offset=10"
```

### Validation Checklist

- [ ] API returns price data for stocks with available data
- [ ] API returns null for stocks without price data (not missing)
- [ ] Price change percentage is calculated correctly
- [ ] Volume data is included when available
- [ ] Market filter works correctly
- [ ] Pagination (limit/offset) works correctly
- [ ] Response time < 2 seconds for 200+ stocks
- [ ] Database query executes in < 500ms

## Performance Testing

```bash
# Test with 200+ stocks
time curl "http://localhost:5000/api/stock-price/list?limit=250"

# Expected: < 2 seconds total response time
```

## Database Query Verification

Connect to database and run the query manually:
```sql
SELECT 
    si.symbol,
    lp.close_price,
    lp.price_change_pct,
    lp.volume
FROM stock_info si
LEFT JOIN LATERAL (
    SELECT close_price, volume, price_change_pct
    FROM stock_daily_data sd
    WHERE sd.symbol = si.symbol
    ORDER BY sd.trade_date DESC
    LIMIT 1
) lp ON true
WHERE si.is_active = 'Y'
LIMIT 10;
```

## Error Handling

### Missing Price Data
- Returns null for `close_price`, `price_change_pct`, `volume`
- Does not omit stocks from results
- Frontend can display "N/A" for null values

### Invalid Parameters
- Returns 400 error with message
- Limits enforced: max 10000 records

### Database Errors
- Returns 500 error with detail
- Logs error for debugging

## Rollback Plan

If issues occur, revert changes:
```bash
git checkout app/services/stock_data_service.py
git checkout app/routes/stock_price.py
```

## Next Steps

After implementation:
1. Test with frontend integration
2. Verify Chinese column headers display correctly
3. Monitor performance in production
4. Add caching if needed (future enhancement)

## Related Files

- `spec.md` - Full feature specification
- `data-model.md` - Data model details
- `contracts/api-contracts.json` - API contract definition
- `research.md` - Technical research and decisions

