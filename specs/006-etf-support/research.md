# Research: ETF Support in Data Query API

**Feature**: 006-etf-support  
**Date**: 2025-10-27  
**Status**: Complete

## Overview

Research conducted to determine how to add ETF (Exchange Traded Fund) filtering support to the stock data query API and ensure custom script calculations work correctly for ETF data.

## Decisions Made

### Decision 1: ETF Data Model Compatibility

**Chosen**: ETFs stored in same `stock_info` and `stock_daily_data` tables as stocks, using existing schema

**Rationale**:
- Database schema already accommodates both stocks and ETFs
- ETFs have symbol prefixes similar to stocks (SH., SZ., BJ.)
- Price data structure (close_price, volume, etc.) is identical
- No separate ETF-specific tables needed

**Evidence**:
- Existing queries return both stocks and ETFs without distinction
- `stock_info` table has symbol, name, market_code fields that work for ETFs
- No schema changes required

**Alternatives Considered**:
- Separate ETF tables: Rejected - unnecessary duplication, complicates queries
- ETF metadata in separate table: Rejected - adds complexity without benefit for current use case

### Decision 2: ETF Filter Parameter Design

**Chosen**: Boolean query parameter `is_etf` (true/false/null)

**Rationale**:
- Simple and intuitive API design
- Follows existing pattern (market_code, is_active are also filters)
- Null/missing parameter returns both types (default behavior)
- Easy to combine with existing filters

**Parameter Values**:
- `is_etf=true`: Return only ETFs
- `is_etf=false`: Return only stocks (not ETFs)
- `is_etf` omitted or `null`: Return both stocks and ETFs

**SQL Implementation**:
```sql
-- Add to WHERE clause when is_etf is provided
AND (
  CASE 
    WHEN :is_etf = true THEN s.symbol IN (SELECT symbol FROM stock_info WHERE is_etf = 'Y')
    WHEN :is_etf = false THEN s.symbol NOT IN (SELECT symbol FROM stock_info WHERE is_etf = 'Y')
    ELSE TRUE
  END
)
```

**Alternatives Considered**:
- String enum ('etf', 'stock', 'all'): Rejected - less intuitive, violates REST conventions for boolean filters
- Separate endpoint: Rejected - violates DRY principle, adds maintenance burden

### Decision 3: ETF Marker in Response

**Chosen**: Include `is_etf` boolean field in each instrument record

**Rationale**:
- Frontend needs to distinguish ETFs from stocks for display/sorting
- Similar to existing fields (is_active, market_code)
- Self-documenting response structure

**Implementation**:
```python
{
    "symbol": "SH.510300",
    "stock_name": "沪深300ETF",
    "market_code": "SH",
    "is_active": "Y",
    "is_etf": true,  # NEW field
    "close_price": 4.852,
    "price_change_pct": 0.65,
    "volume": 52000000
}
```

**Alternatives Considered**:
- Separate response field `instrument_type`: Rejected - overengineering, boolean is clearer
- Only include for ETFs: Rejected - creates inconsistencies, requires null checking

### Decision 4: Script Execution Compatibility

**Chosen**: ETF data uses identical execution context as stock data

**Rationale**:
- ETFs and stocks share the same data fields (close_price, volume, etc.)
- Script context already includes all necessary fields from `row` object
- No script modifications needed for ETF support
- Ensures calculation consistency

**Context Structure** (already compatible):
```python
row = {
    'symbol': 'SH.510300',  # ETF symbol
    'stock_name': '沪深300ETF',
    'market_code': 'SH',
    'is_active': 'Y',
    'is_etf': True,  # NEW - added for completeness
    'close_price': 4.852,
    'price_change_pct': 0.65,
    'volume': 52000000,
    'latest_trade_date': '2025-01-27'
}
```

**Validation**:
- Script `row['close_price']` works for both stocks and ETFs
- Script `get_history(row['symbol'], days)` works for both
- No ETF-specific logic needed in scripts

**Alternatives Considered**:
- ETF-specific script execution: Rejected - unnecessary complexity, no different requirements
- Error if scripts access ETF-only fields: Rejected - no ETF-only fields exist

### Decision 5: Database ETF Detection

**Chosen**: Add `is_etf` column to `stock_info` table

**Rationale**:
- Explicit marker preferred over symbol pattern matching
- More reliable than heuristics (e.g., "ETF" in name)
- Allows for future ETF-specific features
- Simple boolean column

**Database Migration**:
```sql
ALTER TABLE stock_info ADD COLUMN is_etf CHAR(1) DEFAULT 'N';
UPDATE stock_info SET is_etf = 'Y' WHERE stock_name LIKE '%ETF%' OR stock_name LIKE '%etf%';
-- Future: Data sync process sets is_etf flag
```

**Detection Method**:
- Manual initial data: Update based on name patterns
- Future sync process: Use market data API to identify ETFs

**Alternatives Considered**:
- Pattern matching on symbol: Rejected - unreliable, no ETF prefix standard
- Pattern matching on name: Rejected - fragile, name variations exist
- Enum/instrument_type field: Rejected - overengineering, simple boolean sufficient

## Technology Choices

### SQL Filtering

**Implementation**: Modify `list_stocks_with_latest_price()` in `app/services/stock_data_service.py`

**Key Changes**:
- Add `is_etf` parameter to method signature
- Add optional WHERE clause filter based on `is_etf` value
- Use subquery or JOIN to check `stock_info.is_etf` field

**Performance Impact**:
- Minimal - ETF filter adds simple boolean check
- Existing LATERAL JOIN optimization remains
- Query time should remain < 500ms for 200+ results

### API Parameter Validation

**Implementation**: Add to `app/routes/stock_price.py`

**Validation**:
```python
is_etf_param = request.args.get('is_etf')
if is_etf_param is not None:
    is_etf = is_etf_param.lower() == 'true'
    if is_etf_param.lower() not in ('true', 'false'):
        return create_error_response(400, "参数错误", "is_etf must be 'true' or 'false'")
```

## Security Considerations

### ETF Filter Validation

- **Input**: `is_etf` parameter validated as boolean string
- **SQL Injection**: Parameter passed through SQLAlchemy ORM (safe)
- **Script Security**: Script execution context identical for ETFs (no new attack vectors)

## References

- Existing API contracts: `specs/006-etf-support/contracts/api-contracts.json`
- SQL optimization: See `specs/004-stock-data-display/research.md` for LATERAL JOIN pattern
- Script execution: See `specs/002-custom-calculation-api/research.md` for RestrictedPython

