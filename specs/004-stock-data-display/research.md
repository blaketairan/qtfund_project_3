# Research: Stock Data Display Implementation

**Feature**: 004-stock-data-display  
**Date**: 2025-01-27  
**Status**: Complete

## Research Questions

### Q1: How to efficiently query latest price for multiple stocks in single operation?

**Decision**: Use SQL subquery with DISTINCT ON or LATERAL JOIN to get latest trade_date's price for each stock.

**Rationale**:
- TimescaleDB supports efficient time-series queries
- LATERAL JOIN pattern is optimal for "latest record per group"
- PostgreSQL 9.3+ has excellent lateral join performance
- Avoid N+1 query pattern (would require one query per stock)

**SQL Pattern**:
```sql
SELECT 
    si.symbol,
    si.stock_name,
    si.market_code,
    lp.close_price,
    lp.volume,
    lp.price_change_pct
FROM stock_info si
LEFT JOIN LATERAL (
    SELECT close_price, volume, price_change_pct
    FROM stock_daily_data sd
    WHERE sd.symbol = si.symbol
    ORDER BY sd.trade_date DESC
    LIMIT 1
) lp ON true
WHERE si.is_active = 'Y'
ORDER BY si.symbol
LIMIT 100 OFFSET 0;
```

**Performance**: With TimescaleDB's chunk management and proper indexes, this query should execute in <500ms for 500+ stocks.

**Alternatives considered**:
- Window functions (ROW_NUMBER() OVER PARTITION): Similar performance but more complex
- Separate queries for each stock: Would cause N+1 problem, unacceptable for 200+ stocks

### Q2: How to calculate price change percentage (day-over-day)?

**Decision**: Include previous day's price in the SQL query using LATERAL join with offset.

**Rationale**:
- Calculation required: `((today_price - yesterday_price) / yesterday_price) * 100`
- Store in database as pre-calculated field (price_change_pct exists in StockDailyData)
- If not available, calculate at query time using window functions

**Implementation**:
Option A (Preferred): Use existing `price_change_pct` field in StockDailyData if already calculated:
```sql
SELECT price_change_pct FROM stock_daily_data WHERE ... ORDER BY trade_date DESC LIMIT 1
```

Option B (Fallback): Calculate on-the-fly if field is NULL:
```sql
SELECT 
    close_price,
    LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date DESC) as prev_close,
    ((close_price - LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date DESC)) 
     / NULLIF(LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date DESC), 0) * 100) as calculated_pct
FROM stock_daily_data
WHERE symbol = ? 
ORDER BY trade_date DESC 
LIMIT 1;
```

**Alternatives considered**:
- Calculate in Python after query: Less efficient, requires fetching more data
- Calculate in database view: Good for performance but adds complexity

### Q3: How to handle stocks with no price data gracefully?

**Decision**: Use LEFT JOIN so stocks without price data still appear in results with NULL values.

**Rationale**:
- Frontend needs complete stock list even if prices unavailable
- NULL values clearly indicate missing data
- Backward compatible with existing frontend behavior

**Implementation**:
```sql
-- LEFT JOIN ensures stock appears even without price data
LEFT JOIN LATERAL (...) lp ON true
```

Response format:
```json
{
  "symbol": "SH.600519",
  "stock_name": "贵州茅台",
  "market_code": "SH",
  "close_price": null,  // NULL if no data
  "price_change_pct": null,
  "volume": null
}
```

**Alternatives considered**:
- Omit stocks without price data: Would be confusing for users
- Return empty string: Less semantically clear than NULL

### Q4: What indexes are needed for optimal performance?

**Decision**: Existing indexes on `stock_daily_data` should be sufficient.

**Existing Indexes**:
- `idx_symbol_date` on (symbol, trade_date) - CRITICAL for this query
- `idx_trade_date` on (trade_date) - Helps with sort operations
- `idx_market_code` on (market_code) - Helps with market filtering

**Rationale**:
- Compound index (symbol, trade_date) is perfect for "latest price per stock" queries
- TimescaleDB's chunking automatically partitions data by time
- No additional indexes needed

**Query Plan Expected**:
```
Index Scan using idx_symbol_date
-> Limit (actual rows=1)
```

**Performance Target**: <500ms for 500 stocks

### Q5: How to maintain backward compatibility with frontend?

**Decision**: Add new fields without removing existing fields, ensure consistent field names.

**Rationale**:
- Existing response includes: symbol, stock_name, market_code
- Add: close_price, price_change_pct, volume
- Frontend can check for presence of new fields before displaying

**Current Response Structure**:
```json
{
  "code": 200,
  "message": "查询成功",
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

**New Response Structure**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "market_code": "SH",
      "is_active": "Y",
      "close_price": 1750.50,
      "price_change_pct": 2.35,
      "volume": 12500000
    }
  ]
}
```

**Alternatives considered**:
- New endpoint: Unnecessary, would duplicate logic
- Version header: Adds complexity without benefit

### Q6: How to optimize for Chinese column display on frontend?

**Decision**: Frontend maps field names to Chinese labels, backend just returns data.

**Rationale**:
- Separation of concerns: Backend returns data, frontend handles i18n
- Frontend already has column mapping logic
- No changes needed in backend response format

**Frontend Mapping** (implementation not in this repo):
```javascript
const columnMap = {
  'symbol': '股票代码',
  'stock_name': '股票名称',
  'close_price': '价格',
  'price_change_pct': '涨跌幅',
  'volume': '成交量'
};
```

**Alternatives considered**:
- Backend returns Chinese field names: Would break existing code
- Return both English and Chinese: Adds unnecessary data transfer

## Technology Choices

### Database Query Pattern
- **Technology**: PostgreSQL LATERAL JOIN
- **Why**: Optimal for "latest record per group" queries with TimeSeriesDB
- **Performance**: Sub-millisecond per stock when properly indexed

### ORM Usage
- **Decision**: Use SQLAlchemy with raw SQL for complex query, ORM for simpler operations
- **Why**: LATERAL joins not easily expressible in SQLAlchemy ORM
- **Pattern**: `session.execute(text(query))` for complex queries

### Data Type
- **Decision**: Use DECIMAL for prices, BIGINT for volume
- **Why**: Precision critical for financial data, avoid floating point errors
- **From**: Already implemented in StockDailyData model

## Implementation Approach Summary

1. **Modify Service Layer** (`app/services/stock_data_service.py`):
   - Add method `list_stocks_with_latest_price()` that executes LATERAL JOIN query
   - Handle NULL values gracefully
   - Apply existing filters (market_code, is_active, limit, offset)

2. **Modify Route** (`app/routes/stock_price.py`):
   - Update `list_stocks()` endpoint to call new service method
   - Format response to include new price fields
   - Maintain existing response structure

3. **Testing**:
   - Test with stocks that have price data
   - Test with stocks missing price data
   - Test performance with 200+ stocks
   - Verify price change calculation accuracy

## Unknowns Resolved

- ✅ Query pattern for latest price per stock: LATERAL JOIN
- ✅ Price change calculation: Use existing field or calculate with LAG
- ✅ Handling missing data: LEFT JOIN returns NULL
- ✅ Index usage: Existing indexes sufficient
- ✅ Response format: Add fields without breaking changes
- ✅ Frontend integration: No backend changes for i18n

## References

- PostgreSQL LATERAL JOIN documentation
- SQLAlchemy raw SQL execution patterns
- TimescaleDB performance tuning
- Financial data precision best practices

