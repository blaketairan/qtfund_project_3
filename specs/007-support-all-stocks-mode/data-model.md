# Data Model: Support All-Stocks Mode

**Feature**: 007-support-all-stocks-mode  
**Date**: 2025-01-27

## Overview

This feature extends the custom calculation API to support applying scripts to all active stocks when stock_symbols array is empty. The API automatically fetches all active stocks from the database and applies the script to each stock.

## Data Entities

### All Active Stocks Query

**Table**: `stock_info` (existing table)

**Fields Used**:
- `symbol` (String): Stock identifier
- `is_active` (String): Active status ('Y' or 'N')
- `market_code` (String): Market code (SH/SZ/BJ) - optional filter

**Query Pattern**: `SELECT symbol FROM stock_info WHERE is_active = 'Y'`

### API Request Behavior

**Empty Array Mode**:
```json
POST /api/custom-calculations/execute
{
  "script": "result = row['close_price'] * 1.1",
  "stock_symbols": [],
  "column_name": "计算列"
}
```

**Backward Compatibility Mode**:
```json
POST /api/custom-calculations/execute
{
  "script": "result = row['close_price'] * 1.1",
  "stock_symbols": ["SH.600519", "SZ.000001"],
  "column_name": "计算列"
}
```

### Response Data Model

**Response Structure** (same as before):
```json
{
  "code": 200,
  "message": "执行成功",
  "data": {
    "results": [
      {
        "symbol": "SH.600519",
        "value": 1250.5,
        "error": null
      },
      {
        "symbol": "SZ.000001",
        "value": 15.2,
        "error": null
      }
      // ... more results for all stocks
    ],
    "summary": {
      "total": 1500,
      "successful": 1498,
      "failed": 2
    }
  }
}
```

**Summary Fields**:
- `total`: Total number of stocks processed
- `successful`: Number of stocks with successful execution
- `failed`: Number of stocks with errors

## Execution Flow

### Before Modification

```
User Request (with stock_symbols)
  ↓
API validates: stock_symbols must be non-empty
  ↓
Error if empty (400)
```

### After Modification

```
User Request (empty stock_symbols)
  ↓
API detects empty array
  ↓
Fetch all active stocks from DB
  ↓
Execute script for each stock
  ↓
Return aggregated results
```

## Validation Rules

### Input Validation (Updated)

1. `stock_symbols` can be empty array OR contain specific symbols
2. If empty: API fetches all active stocks automatically
3. If provided: API uses those symbols (backward compatible)
4. Script validation: Same as before
5. column_name: Still required

### Backward Compatibility

**Before (must specify symbols)**:
```json
{"stock_symbols": ["SH.600519", "SZ.000001"]}
```

**After (can be empty for all stocks)**:
```json
{"stock_symbols": []}  // Applies to all stocks
```

**Still Works (backward compatible)**:
```json
{"stock_symbols": ["SH.600519", "SZ.000001"]}  // Still works
```

## Implementation Changes

### Service Layer Enhancement

**New Method**: `get_all_active_stocks()`
- Location: `app/services/stock_data_service.py`
- Purpose: Fetch all active stock symbols
- Parameters: Optional market_code filter
- Returns: List of stock symbols

### Route Handler Modification

**Updated Logic**: `app/routes/custom_calculation.py`
- Remove rejection of empty stock_symbols
- Add conditional logic:
  - If stock_symbols is empty → fetch all active stocks
  - If stock_symbols provided → use those symbols
- Add execution summary to response

### Database Query

**Query**:
```sql
SELECT symbol FROM stock_info WHERE is_active = 'Y'
```

**Optional Filtering**:
```sql
SELECT symbol FROM stock_info 
WHERE is_active = 'Y' AND market_code = 'SH'
```

## Performance Considerations

### Stock Universe Size

- **Small (< 500 stocks)**: Process immediately, no batching
- **Medium (500-1000 stocks)**: Process in batches, warn user
- **Large (> 1000 stocks)**: Consider adding pagination or limiting

### Execution Time

- Current: ~2 seconds per stock
- 100 stocks: ~200 seconds (3+ minutes)
- Strategy: Batch into groups of 100, inform user of progress

### Database Load

- All-stocks query: Simple SELECT, uses existing index
- Expected query time: < 100ms for 1000 stocks
- No performance degradation expected

## Error Handling

### Individual Stock Errors

- Continue execution even if some stocks fail
- Collect errors in results array
- Return summary with success/failure counts

### Missing Stock Data

- Return error for individual stock
- Don't fail entire execution
- User sees which stocks failed

### Execution Timeout

- Batching prevents timeout
- If still exceeds limit, return partial results
- Inform user of incomplete execution

## Integration with Existing Features

### Stock Info Service

- Reuse existing `StockDataService` class
- Add new method `get_all_active_stocks()`
- Maintain existing query patterns

### Custom Calculation API

- Extend existing `/execute` endpoint
- No new endpoints needed
- Maintain backward compatibility

### Response Format

- Same structure as before
- Add optional summary field
- Results array works identically

## Migration Notes

### Database Changes

- **None required**: Uses existing stock_info table
- Uses existing is_active column
- No schema migration needed

### API Changes

- **Backward compatible**: Existing calls work unchanged
- New behavior: Empty array applies to all stocks
- No breaking changes

### Code Changes

- Add `get_all_active_stocks()` method
- Modify validation logic in execute_script()
- Add summary calculation
- No structural changes needed

