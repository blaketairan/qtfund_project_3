# Data Model: ETF Support in Data Query API

**Feature**: 006-etf-support  
**Date**: 2025-10-27

## Entity Overview

### StockInfo (Enhanced with ETF Support)

The existing `StockInfo` entity is extended with an `is_etf` field to distinguish ETFs from regular stocks.

**Table**: `stock_info`  
**Location**: `models/stock_data.py`

**Fields**:
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| symbol | String | No | Unique stock identifier with market prefix (e.g., 'SH.600519', 'SH.510300') |
| stock_name | String | No | Stock/ETF full name |
| market_code | String | No | Market code ('SH', 'SZ', 'BJ') |
| is_active | Char(1) | No | Active status ('Y'/'N') |
| **is_etf** | **Char(1)** | **No** | **ETF indicator ('Y'/'N') - NEW FIELD** |
| created_at | Timestamp | No | Record creation timestamp |
| updated_at | Timestamp | No | Record update timestamp |
| last_sync_date | Date | Yes | Last data synchronization date |

**Indexes**:
```sql
CREATE INDEX idx_symbol_etf ON stock_info(symbol, is_etf);
CREATE INDEX idx_is_etf_active ON stock_info(is_etf, is_active);
```

**Sample Data**:
```python
# Regular stock
{
    'symbol': 'SH.600519',
    'stock_name': '贵州茅台',
    'market_code': 'SH',
    'is_active': 'Y',
    'is_etf': 'N'  # Regular stock
}

# ETF
{
    'symbol': 'SH.510300',
    'stock_name': '沪深300ETF',
    'market_code': 'SH',
    'is_active': 'Y',
    'is_etf': 'Y'  # ETF
}
```

## Query Flow

### Request Processing

1. **User Request**: `GET /api/stock-price/list?is_etf=true&market_code=SH&limit=50`

2. **Parameter Parsing** (in `app/routes/stock_price.py`):
   ```python
   is_etf_param = request.args.get('is_etf')  # 'true' or 'false'
   market_code = request.args.get('market_code')  # 'SH', 'SZ', 'BJ'
   limit = int(request.args.get('limit', 100))
   offset = int(request.args.get('offset', 0))
   ```

3. **Service Layer Query** (in `app/services/stock_data_service.py`):
   ```python
   result = service.list_stocks_with_latest_price(
       market_code='SH',
       is_active='Y',
       is_etf=True,  # NEW parameter
       limit=50,
       offset=0
   )
   ```

4. **SQL Query** (LATERAL JOIN pattern for latest price):
   ```sql
   SELECT 
       s.symbol,
       s.stock_name,
       s.market_code,
       s.is_active,
       s.is_etf,  -- NEW field
       lp.close_price,
       lp.price_change_pct,
       lp.volume,
       lp.trade_date AS latest_trade_date
   FROM stock_info s
   LEFT JOIN LATERAL (
       SELECT close_price, price_change_pct, volume, trade_date
       FROM stock_daily_data d
       WHERE d.symbol = s.symbol
       ORDER BY d.trade_date DESC
       LIMIT 1
   ) lp ON true
   WHERE s.is_active = 'Y'
     AND s.market_code = 'SH'
     AND s.is_etf = 'Y'  -- ETF filter
   ORDER BY s.symbol
   LIMIT 50
   OFFSET 0
   ```

5. **Response Format**:
   ```json
   {
     "code": 200,
     "message": "查询到 50 只ETF",
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
         "latest_trade_date": "2025-10-27"
       }
     ],
     "total": 350,
     "count": 50
   }
   ```

## API Response Data Model

### Enhanced Instrument Record

Each instrument in the `data` array includes the new `is_etf` field:

```typescript
interface InstrumentRecord {
  symbol: string;           // e.g., "SH.510300"
  stock_name: string;        // e.g., "沪深300ETF"
  market_code: string;       // "SH" | "SZ" | "BJ"
  is_active: string;        // "Y" | "N"
  is_etf: boolean;          // true for ETFs, false for stocks - NEW FIELD
  close_price?: number | null;
  price_change_pct?: number | null;
  volume?: number | null;
  latest_trade_date?: string | null;  // ISO date format
  script_results?: { [scriptId: string]: number | null };  // Optional
}
```

**Response Examples**:

**ETF Response** (`is_etf=true`):
```json
{
  "code": 200,
  "message": "查询到 2 只ETF",
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
      "latest_trade_date": "2025-10-27"
    },
    {
      "symbol": "SZ.159919",
      "stock_name": "300ETF",
      "market_code": "SZ",
      "is_active": "Y",
      "is_etf": true,
      "close_price": 3.456,
      "price_change_pct": 0.23,
      "volume": 12300000,
      "latest_trade_date": "2025-10-27"
    }
  ],
  "total": 350,
  "count": 2
}
```

**Stock Response** (`is_etf=false`):
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
      "volume": 5000000,
      "latest_trade_date": "2025-10-27"
    }
  ],
  "total": 5000,
  "count": 5
}
```

## Data Relationships

### StockInfo ↔ StockDailyData

**Relationship**: One-to-Many

- One `StockInfo` record has many `StockDailyData` records (one per trading day)
- Same relationship applies to both stocks and ETFs
- ETF price data structure identical to stock price data

**Stock Data**:
```sql
SELECT * FROM stock_daily_data WHERE symbol = 'SH.510300';  -- ETF
```

**Returns**:
```
symbol      | trade_date | close_price | volume
------------+------------+-------------+--------
SH.510300   | 2025-10-27 | 4.852       | 52000000
SH.510300   | 2025-10-26 | 4.821       | 51000000
```

## Validation Rules

### Input Validation

1. **is_etf Parameter**:
   - Type: Boolean string ('true'/'false')
   - Default: `null` (returns both types)
   - Invalid values return 400 error

2. **Combined Filters**:
   - `is_etf` can be combined with `market_code`, `is_active`, `limit`, `offset`
   - All filters are AND conditions

### Output Validation

1. **is_etf Field**:
   - Must be included in every instrument record
   - Must be boolean (true/false), never null
   - Derived from `stock_info.is_etf` column

2. **Data Consistency**:
   - Records with `is_etf=true` must be ETFs
   - Records with `is_etf=false` must be stocks
   - No ambiguity allowed

## Performance Considerations

### Query Optimization

1. **Indexes**:
   - Add composite index on `(is_etf, is_active, market_code)` for filter queries
   - Existing `idx_symbol_date` on `stock_daily_data` still effective for LATERAL JOIN

2. **Query Patterns**:
   - ETF filter adds one additional WHERE condition
   - No impact on existing LATERAL JOIN performance
   - Estimated query time: < 500ms for 200+ ETF results

3. **Script Execution**:
   - ETF script execution context identical to stocks
   - No additional overhead for ETF script calculations
   - Script timeout (10s) applies to ETFs equally

## Caching Strategy

- ETF filter results can be cached like stock results
- Cache key includes `is_etf` parameter
- Cache invalidation when new ETF data arrives (daily sync)

