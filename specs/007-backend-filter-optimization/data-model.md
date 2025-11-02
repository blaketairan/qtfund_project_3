# Data Model: Backend Market Filter and Unlimited Results

**Feature**: 007-backend-filter-optimization  
**Date**: 2025-10-27

## Overview

This feature is primarily a configuration and query optimization change. No new entities or data model changes are required.

## Existing Data Model (No Changes)

### StockInfo

**Table**: `stock_info`  
**Changes**: None

The existing `stock_info` table already supports all required filtering:
- `market_code` - Already used for database-level filtering
- `is_etf` - Already supports ETF filtering
- `is_active` - Already supports active status filtering

### StockDailyData

**Table**: `stock_daily_data`  
**Changes**: None

Price data table structure remains unchanged. LATERAL JOIN pattern already efficiently retrieves latest price for unlimited result sets.

## Query Flow Changes

### Before (With Default Limit)

**Request**: `GET /api/stock-price/list?market_code=SH`

**Query Execution**:
```python
limit = request.args.get('limit', 100, type=int)  # Default 100
result = service.list_stocks_with_latest_price(
    market_code='SH',
    limit=100  # Artificial limit
)
```

**SQL**:
```sql
SELECT ...
FROM stock_info si
WHERE si.market_code = 'SH'
LIMIT 100  -- Artificial limit, may exclude valid results
```

**Result**: Only first 100 SH stocks returned, even if 500 exist.

### After (Unlimited by Default)

**Request**: `GET /api/stock-price/list?market_code=SH`

**Query Execution**:
```python
limit = request.args.get('limit', type=int)  # No default, None if not provided
if limit is None:
    limit = 999999  # Effectively unlimited
result = service.list_stocks_with_latest_price(
    market_code='SH',
    limit=999999  # Return all
)
```

**SQL**:
```sql
SELECT ...
FROM stock_info si
WHERE si.market_code = 'SH'
LIMIT 999999  -- Effectively returns all matching records
```

**Result**: All SH stocks returned (e.g., 500 records).

## Response Data Model (No Changes)

The response structure remains identical:

```typescript
interface APIResponse {
  code: number;
  message: string;
  timestamp?: string;
  data: InstrumentRecord[];  // May contain 1000+ records now
  total: number;
  count: number;  // Will equal total when limit not provided
}

interface InstrumentRecord {
  symbol: string;
  stock_name: string;
  market_code: string;
  is_active: string;
  is_etf: boolean;
  close_price?: number | null;
  price_change_pct?: number | null;
  volume?: number | null;
  latest_trade_date?: string | null;
  script_results?: { [scriptId: string]: number | null };
}
```

**Key Difference**: `data` array may now contain thousands of records instead of being capped at 100.

## Configuration Changes

### Request Timeout

**Component**: Flask application server (Gunicorn/uWSGI)

**Configuration File**: `config/gunicorn_config.py` or start command

**Settings**:
```python
# config/gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4
timeout = 600  # 10 minutes (NEW)
graceful_timeout = 630  # Slightly longer (NEW)
worker_class = "sync"
keepalive = 5
```

**Environment Variable** (alternative):
```bash
export FLASK_REQUEST_TIMEOUT=600
```

### Database Connection Pool

**Component**: SQLAlchemy engine configuration

**Current**: Default settings (5 connections, 10 overflow)

**Recommended** (if long-running query issues occur):
```python
# database/connection.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Increased from default 5
    max_overflow=20,  # Increased from default 10
    pool_recycle=3600,  # Recycle connections hourly
    pool_pre_ping=True  # Verify connection health
)
```

**Decision**: Keep defaults initially, monitor for connection pool exhaustion.

## Validation Rules

### Input Validation Changes

**Before**:
```python
limit = request.args.get('limit', 100, type=int)
if limit > 10000:
    return error("limit cannot exceed 10000")
```

**After**:
```python
limit = request.args.get('limit', type=int)  # None if not provided
if limit is not None and limit > 10000:
    return error("limit cannot exceed 10000")
# If limit is None, no upper bound check - return all
```

### Output Validation (No Changes)

- Response structure remains identical
- Field types unchanged
- Null handling unchanged

## Performance Impact

### Memory Usage

**Estimate for 2000 records**:
- Each record: ~200 bytes (JSON)
- 2000 records × 200 bytes = 400 KB
- With script results (3 scripts): ~600 KB
- **Conclusion**: Acceptable memory footprint

### Response Time

**Database Query** (unchanged):
- LATERAL JOIN performance: O(n) where n = result count
- 100 records: ~100ms
- 2000 records: ~2 seconds
- **Conclusion**: Scales linearly, acceptable

**Script Execution** (dominant factor):
- Serial execution: 1 script × 1 stock × 10ms average
- 3 scripts × 2000 stocks = 6000 calculations
- 6000 × 0.01s = 60 seconds
- **Conclusion**: Requires 10-minute timeout

**Total Response Time**:
- Query 2000 stocks + run 3 scripts: ~2-5 minutes
- Within 10-minute timeout window

## Risk Assessment

### Risks

1. **Memory Overflow**: Very large queries (10000+ records) may exhaust memory
   - **Mitigation**: Monitor memory usage, add warning logs for large queries

2. **Slow Queries**: Users expect instant results, 5-minute wait may be unexpected
   - **Mitigation**: Document expected response times, consider progress indicators

3. **Connection Pool Exhaustion**: Multiple concurrent long queries
   - **Mitigation**: Increase pool size if needed, monitor connection usage

### Monitoring Recommendations

- Log query sizes (record count)
- Log execution times (database vs script vs total)
- Alert on queries > 5 minutes
- Monitor memory usage per request

