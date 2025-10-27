# ETF Support - Quickstart

**Feature**: 006-etf-support  
**Date**: 2025-10-27

## Overview

Add ETF filtering support to the `/api/stock-price/list` endpoint, allowing users to filter results by instrument type (ETF vs. regular stock) while maintaining full compatibility with custom script calculations.

## Changes Summary

### 1. Database Schema Update

Add `is_etf` column to `stock_info` table:

```sql
ALTER TABLE stock_info ADD COLUMN is_etf CHAR(1) DEFAULT 'N';
UPDATE stock_info SET is_etf = 'Y' WHERE stock_name LIKE '%ETF%' OR stock_name LIKE '%etf%';
CREATE INDEX idx_symbol_etf ON stock_info(symbol, is_etf);
CREATE INDEX idx_is_etf_active ON stock_info(is_etf, is_active);
```

### 2. Service Layer Update

Modify `app/services/stock_data_service.py`:

**Update Method Signature**:
```python
def list_stocks_with_latest_price(
    self,
    market_code: Optional[str] = None,
    is_active: str = 'Y',
    is_etf: Optional[bool] = None,  # NEW parameter
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
```

**Add ETF Filtering Logic**:
```python
# Build query
query = session.query(
    # ... existing fields ...
    StockInfo.is_etf,  # NEW field
    # ...
)

# Add ETF filter
if is_etf is not None:
    if is_etf:
        query = query.filter(StockInfo.is_etf == 'Y')
    else:
        query = query.filter(StockInfo.is_etf == 'N')

# Return data
return {
    'symbol': row.symbol,
    'stock_name': row.stock_name,
    'market_code': row.market_code,
    'is_active': row.is_active,
    'is_etf': row.is_etf == 'Y',  # Convert CHAR to boolean
    'close_price': row.close_price,
    'price_change_pct': row.price_change_pct,
    'volume': row.volume,
    'latest_trade_date': row.latest_trade_date.strftime('%Y-%m-%d') if row.latest_trade_date else None
}
```

### 3. Route Handler Update

Modify `app/routes/stock_price.py`:

**Add Parameter Parsing**:
```python
is_etf_param = request.args.get('is_etf')
is_etf = None
if is_etf_param is not None:
    if is_etf_param.lower() not in ('true', 'false'):
        return create_error_response(400, "参数错误", "is_etf must be 'true' or 'false'")
    is_etf = is_etf_param.lower() == 'true'

result = service.list_stocks_with_latest_price(
    market_code=market_code,
    is_active=is_active,
    is_etf=is_etf,  # NEW parameter
    limit=limit,
    offset=offset
)
```

## Testing

### 1. ETF Only Query

```bash
# Query ETFs only
curl "http://localhost:8000/api/stock-price/list?is_etf=true&limit=5"
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "查询到 5 只ETF",
  "data": [
    {
      "symbol": "SH.510300",
      "stock_name": "沪深300ETF",
      "market_code": "SH",
      "is_active": "Y",
      "is_etf": true,
      "close_price": 4.852,
      "price_change_pct": 0.65,
      "volume": 52000000
    }
  ],
  "total": 350,
  "count": 5
}
```

### 2. Stock Only Query

```bash
# Query stocks only (not ETFs)
curl "http://localhost:8000/api/stock-price/list?is_etf=false&limit=5"
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "查询到 5 只股票",
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "market_code": "SH",
      "is_active": "Y",
      "is_etf": false,
      "close_price": 1700.50,
      "price_change_pct": 2.35,
      "volume": 5000000
    }
  ],
  "total": 5000,
  "count": 5
}
```

### 3. Both Stocks and ETFs

```bash
# Query both (default behavior)
curl "http://localhost:8000/api/stock-price/list?limit=10"
```

**Expected Response**: Includes both `is_etf=true` and `is_etf=false` records.

### 4. Combined Filters

```bash
# Query Shanghai ETFs only
curl "http://localhost:8000/api/stock-price/list?is_etf=true&market_code=SH&limit=10"
```

**Expected Response**: Only ETFs from Shanghai market.

### 5. ETF with Custom Scripts

```bash
# Query ETFs with custom script calculation
curl "http://localhost:8000/api/stock-price/list?is_etf=true&script_ids=[1,2]&limit=5"
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "查询到 5 只ETF",
  "data": [
    {
      "symbol": "SH.510300",
      "stock_name": "沪深300ETF",
      "market_code": "SH",
      "is_active": "Y",
      "is_etf": true,
      "close_price": 4.852,
      "price_change_pct": 0.65,
      "volume": 52000000,
      "script_results": {
        "1": 0.093,
        "2": 0.125
      }
    }
  ],
  "total": 350,
  "count": 5
}
```

## Validation Checklist

### API Behavior

- [ ] `is_etf=true` returns only ETFs
- [ ] `is_etf=false` returns only stocks
- [ ] `is_etf` omitted returns both types
- [ ] `is_etf` field present in all response records
- [ ] Combines correctly with `market_code`, `limit`, `offset`
- [ ] Custom script execution works for ETFs
- [ ] Script results format identical for ETFs and stocks

### Error Handling

- [ ] Invalid `is_etf` value returns 400 error
- [ ] Empty result set returns proper structure with empty data array
- [ ] Database errors handled gracefully

### Performance

- [ ] Query time < 500ms for 200+ results
- [ ] ETF filter doesn't impact existing query performance
- [ ] Script execution time < 10s per ETF

## Rollback Plan

If issues arise:

1. **Revert service layer changes**:
   ```bash
   git checkout HEAD~1 app/services/stock_data_service.py
   ```

2. **Revert route handler**:
   ```bash
   git checkout HEAD~1 app/routes/stock_price.py
   ```

3. **Database changes** (optional):
   ```sql
   ALTER TABLE stock_info DROP COLUMN is_etf;
   DROP INDEX idx_symbol_etf;
   DROP INDEX idx_is_etf_active;
   ```

Note: Database schema changes are additive only - no data loss on rollback.

## Next Steps

1. Implement database migration (add `is_etf` column)
2. Update service layer with ETF filtering
3. Update route handler with parameter parsing
4. Test with curl commands above
5. Verify script execution for ETFs
6. Commit and push

