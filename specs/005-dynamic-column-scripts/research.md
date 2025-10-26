# Research & Design Decisions: Dynamic Script Columns

**Feature**: Dynamic Script Columns in List Query  
**Date**: 2025-01-27  
**Status**: Complete

## Research Questions

### Q1: How to integrate script execution into the list query flow?

**Decision**: Execute scripts AFTER retrieving the filtered/paginated stock list, not before.

**Rationale**:
- Matches user expectation: scripts calculate only for visible stocks
- Respects all existing filters (limit, offset, market_code)
- Avoids unnecessary computation for filtered-out stocks
- Maintains query performance and data consistency

**Alternatives Considered**:
- Pre-calculate scripts for all stocks: Rejected - inefficient, doesn't match filtered results
- Calculate in SQL with stored procedures: Rejected - complex, requires schema changes
- Separate API call for script results: Rejected - increases latency, harder for frontend

**Implementation**:
1. Query stocks with existing filters
2. For each stock in result set, execute requested scripts
3. Append script results to stock records
4. Return extended records

---

### Q2: How to optimize script execution performance?

**Decision**: Execute scripts sequentially per stock, batch database operations.

**Rationale**:
- Scripts use RestrictedPython sandbox (already has caching mechanism)
- Sequential execution simplifies error handling and debugging

**Alternatives Considered**:
- Parallel execution with multiprocessing: Rejected - complicates error handling
- Batch script compilation: Already handled by RestrictedPython internal caching
- Pre-caching script results: Rejected - data freshness requirement, too complex

---

### Q3: How to handle script execution errors gracefully?

**Decision**: Return `null` for failed scripts, ensure errors don't block response.

**Rationale**:
- Non-blocking: one stock's script failure doesn't prevent others
- Simple frontend handling: null checks instead of exception handling
- Maintains response structure consistency
- Users can identify problematic stocks

**Alternatives Considered**:
- Return error messages in response: Rejected - adds complexity, pollutes response structure
- Reject entire request on any script error: Rejected - too brittle, degrades user experience
- Log errors only: Rejected - users need to know which calculations failed

**Implementation**:
- Try-catch per script execution
- Store null for failed results
- Log detailed error messages server-side
- Return clean response with null values

---

### Q4: How to validate and scope the script_ids parameter?

**Decision**: Validate existence in database.

**Rationale**:
- Validation prevents errors from non-existent scripts

**Alternatives Considered**:
- No validation: Rejected - could cause runtime errors
- Single script only: Rejected - too restrictive for user needs

**Validation**:
- Check script_ids exist in custom_scripts table
- Return 404 for non-existent scripts
- Enforce array type and integer values

---

## Technical Dependencies

### Existing Components

1. **SandboxExecutor** (`app/services/sandbox_executor.py`):
   - Already handles script execution with RestrictedPython
   - Supports `get_history()` function for historical data
   - Has error handling and timeout mechanisms
   - **Status**: Ready to use, no changes needed

2. **StockDataService** (`app/services/stock_data_service.py`):
   - Already has `list_stocks_with_latest_price()` method
   - Returns filtered stock list based on parameters
   - **Status**: Ready to use, no changes needed

3. **Custom Scripts Model** (`app/models/custom_script.py`):
   - Stores script configurations
   - **Status**: Ready to use

### Required Changes

1. **app/routes/stock_price.py**:
   - Add `script_ids` parameter to `list_stocks()` endpoint
   - After querying stocks, load scripts and execute them
   - Append results to each stock record

2. **Performance Considerations**:
   - Script execution is CPU-bound but lightweight
   - Main bottleneck: database query for script loading (once per request)
   - Each script execution: ~5-10ms for simple calculations
   - Estimate: 200 stocks × 3 scripts × 10ms = 6s worst case

**Optimization Strategy**:
- Load all scripts once at request start (minimize DB queries)
- Reuse SandboxExecutor instance across executions
- Keep script compilation cached

---

## Architecture Decision

### Execution Flow

```
Client Request
  ↓
GET /api/stock-price/list?script_ids=[1,2,3]
  ↓
1. Parse query parameters (limit, offset, market_code, script_ids)
2. Query stock list from database (with filters)
3. Load scripts from custom_scripts table
4. For each stock:
   a. Get stock data context (row)
   b. Execute each script with context
   c. Collect results
5. Append script_results to each stock record
6. Return extended response
```

### Error Handling Strategy

- Script not found: Return 404 for entire request
- Invalid script_ids format: Return 400
- Script execution error for specific stock: Return null for that script
- Database error: Return 500

### Response Structure

```json
{
  "code": 200,
  "message": "查询到 2 只股票",
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      ...base fields...,
      "script_results": {
        "1": 0.14,
        "2": 225.67,
        "3": null  // script failed for this stock
      }
    }
  ]
}
```

---

## Validation

All research questions resolved. No NEEDS CLARIFICATION markers remain.

