# Data Model: Stock List with Latest Price

**Feature**: 004-stock-data-display  
**Date**: 2025-01-27

## Overview

This feature enhances the stock list API response to include latest price data (price, change %, volume) for each stock.

## Data Entities

### StockInfo (Existing)

**Table**: `stock_info`

**Fields**:
- `symbol` (String, PK): Stock identifier with market prefix (e.g., "SH.600519")
- `stock_name` (String): Full name of stock
- `stock_code` (String): 6-digit stock code without market prefix
- `market_code` (String): Market code (SH/SZ/BJ)
- `stock_type` (String): Type (stock/fund/bond)
- `industry` (String): Industry classification
- `sector` (String): Sector classification
- `list_date` (DateTime): Listing date
- `delist_date` (DateTime): Delisting date
- `is_active` (String): Active status (Y/N)
- `last_sync_date` (DateTime): Last price sync date
- `first_fetch_time` (DateTime): First fetch timestamp
- `created_at` (DateTime): Record creation time
- `updated_at` (DateTime): Record update time

**Indexes**:
- Primary key: `symbol`
- `idx_stock_code` on `stock_code`
- `idx_market_code_info` on `market_code`
- `idx_stock_name_info` on `stock_name`
- `idx_is_active` on `is_active`

### StockDailyData (Existing)

**Table**: `stock_daily_data` (TimescaleDB hypertable)

**Fields**:
- `trade_date` (DateTime, PK): Trading date
- `symbol` (String, PK): Stock identifier
- `stock_name` (String): Stock name at time of trade
- `market_code` (String): Market code
- `close_price` (DECIMAL(10,4)): Closing price
- `open_price` (DECIMAL(10,4)): Opening price
- `high_price` (DECIMAL(10,4)): Highest price
- `low_price` (DECIMAL(10,4)): Lowest price
- `volume` (BIGINT): Trading volume (shares)
- `turnover` (DECIMAL(20,2)): Trading amount (RMB)
- `price_change` (DECIMAL(10,4)): Price change (absolute)
- `price_change_pct` (DECIMAL(8,4)): Price change (percentage)
- `premium_rate` (DECIMAL(8,4)): Premium rate (for funds)
- `created_at` (DateTime): Record creation time
- `updated_at` (DateTime): Record update time

**Indexes**:
- Primary key: (`trade_date`, `symbol`)
- `idx_symbol_date` on (`symbol`, `trade_date`) - **CRITICAL for this feature**
- `idx_market_code` on `market_code`
- `idx_trade_date` on `trade_date`
- `idx_stock_name` on `stock_name`

**TimescaleDB Configuration**:
- Hypertable on `trade_date` column
- Chunk time interval: 1 month
- Compression: 7 days after, segment by `symbol`, order by `trade_date DESC`
- Retention policy: 3 years

## Query Pattern

### Enhanced Stock List Query

**Purpose**: Get list of active stocks with their latest price data

**SQL Pattern**:
```sql
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
  AND (:market_code IS NULL OR si.market_code = :market_code)
ORDER BY si.symbol
LIMIT :limit OFFSET :offset;
```

**Key Features**:
- LATERAL JOIN gets latest price record per stock
- LEFT JOIN ensures stocks without price data still appear
- Filters by is_active and market_code (optional)
- Supports pagination with limit/offset

### Data Retrieval Flow

```
User Request (Frontend)
  ↓
GET /api/stock-price/list?market_code=SH&limit=100
  ↓
Route Handler (app/routes/stock_price.py)
  ↓
Service Method (app/services/stock_data_service.py)
  - list_stocks_with_latest_price()
  ↓
SQL Query Execution
  - LATERAL JOIN query
  ↓
Database (TimescaleDB)
  - Returns: stock_info + latest price data
  ↓
Format Response (app/utils/responses.py)
  - Add price fields to response
  ↓
JSON Response (Frontend)
```

## Response Data Model

### Request Parameters

**Endpoint**: `GET /api/stock-price/list`

**Query Parameters**:
- `market_code` (optional): Filter by market (SH/SZ/BJ)
- `is_active` (optional, default='Y'): Active status filter
- `limit` (optional, default=100): Results per page
- `offset` (optional, default=0): Pagination offset

### Response Structure

**Status**: 200 OK

**Response Body**:
```json
{
  "code": 200,
  "message": "查询成功",
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
    },
    {
      "symbol": "SZ.000001",
      "stock_name": "平安银行",
      "market_code": "SZ",
      "is_active": "Y",
      "last_sync_date": "2025-01-26T00:00:00",
      "close_price": null,
      "price_change_pct": null,
      "volume": null,
      "latest_trade_date": null
    }
  ],
  "total": 250,
  "count": 2
}
```

**Field Descriptions**:
- `symbol`: Stock identifier (e.g., "SH.600519")
- `stock_name`: Full name of stock
- `market_code`: Market code (SH/SZ/BJ)
- `is_active`: Active status (Y/N)
- `last_sync_date`: Last price data sync date (ISO format or null)
- `close_price`: Latest closing price (DECIMAL or null)
- `price_change_pct`: Price change percentage (DECIMAL or null)
- `volume`: Trading volume on latest day (BIGINT or null)
- `latest_trade_date`: Date of latest price data (YYYY-MM-DD or null)

**Null Handling**:
- Missing price data fields return `null` (not omitted)
- Frontend should handle null gracefully (show "N/A" or empty cell)

## Data Validation Rules

### Input Validation
1. `market_code`: Must be one of: "SH", "SZ", "BJ" (case-insensitive)
2. `is_active`: Must be "Y" or "N" (case-sensitive)
3. `limit`: Must be positive integer, max 10000
4. `offset`: Must be non-negative integer

### Output Validation
1. `close_price`: Must be positive DECIMAL when not null
2. `price_change_pct`: Can be negative, zero, or positive DECIMAL when not null
3. `volume`: Must be non-negative BIGINT when not null
4. `last_sync_date` and `latest_trade_date`: Must be valid ISO date format or null

## Relationships

### StockInfo ↔ StockDailyData

**Relationship**: One-to-Many
- One StockInfo can have many StockDailyData records (one per trading day)
- Each StockDailyData record belongs to one StockInfo
- Join key: `symbol` field

**Query Pattern**:
- Latest price: Get most recent StockDailyData for each StockInfo
- Historical data: Get all StockDailyData records for a symbol within date range
- Price change: Compare current price with previous trading day's price

## Performance Considerations

### Query Efficiency
- Use LATERAL JOIN to fetch latest price in single operation (no N+1 queries)
- Leverage TimescaleDB's chunk management for time-series queries
- Existing index `idx_symbol_date` provides optimal path for LATERAL JOIN
- Expected performance: <500ms for 500+ stocks

### Caching Strategy
- No caching required for this iteration
- Database query is already optimized
- TimescaleDB's compression reduces disk I/O

### Scalability
- Query uses indexes and TimescaleDB partitioning
- Can handle 1000+ stocks efficiently
- Pagination reduces memory usage for large result sets
- No JOIN overhead for stocks without price data (LEFT JOIN)

## Migration Notes

### Existing Data
- No database schema changes required
- All fields already exist in tables
- Query enhancement only, no data migration needed

### Backward Compatibility
- Existing response fields preserved
- New fields added without breaking changes
- Frontend can check for field presence before displaying

