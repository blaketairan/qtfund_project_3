# Quickstart Guide: Dynamic Script Columns in List Query

**Feature**: Dynamic Script Columns in List Query  
**Date**: 2025-01-27  
**Status**: Ready for Implementation

## Overview

This feature enhances the `/api/stock-price/list` endpoint to accept optional `script_ids` parameter. When provided, the API executes the specified scripts for each stock in the result set and includes the calculated values in the response.

**Key Changes**:
1. Add `script_ids` query parameter support
2. Load scripts from database
3. Execute scripts for each stock in result set
4. Return results as `script_results` field

---

## Implementation Steps

### Step 1: Modify Stock Price Route

**File**: `app/routes/stock_price.py`  
**Method**: `list_stocks()`

**Changes Required**:

1. **Parse script_ids parameter**:
```python
script_ids_param = request.args.get('script_ids')
script_ids = []
if script_ids_param:
    try:
        script_ids = json.loads(script_ids_param)
        if not isinstance(script_ids, list):
            return create_error_response(400, "参数错误", "script_ids must be array")
        script_ids = [int(sid) for sid in script_ids]
    except (json.JSONDecodeError, ValueError) as e:
        return create_error_response(400, "参数错误", f"Invalid script_ids: {e}")

# Validate script_ids
if len(script_ids) > 50:  # Reasonable limit to prevent abuse
    return create_error_response(400, "参数错误", "Too many scripts requested")
```

2. **Load scripts from database**:
```python
scripts = {}
if script_ids:
    from app.models.custom_script import CustomScript
    from database.connection import db_manager
    
    with db_manager.get_session() as session:
        query = session.query(CustomScript).filter(CustomScript.id.in_(script_ids))
        results = query.all()
        
        # Check all IDs exist
        found_ids = {s.id for s in results}
        missing_ids = set(script_ids) - found_ids
        if missing_ids:
            return create_error_response(404, "脚本不存在", 
                f"Script IDs not found: {list(missing_ids)}")
        
        scripts = {s.id: s.code for s in results}
```

3. **Execute scripts after retrieving stocks**:
```python
from app.services.sandbox_executor import SandboxExecutor

# Get stocks as usual
stocks = service.list_stocks_with_latest_price(
    market_code=market_code,
    is_active=is_active,
    limit=limit,
    offset=offset
)

# Execute scripts if requested
if scripts:
    executor = SandboxExecutor()
    for stock in stocks:
        script_results = {}
        
        for script_id, script_code in scripts.items():
            try:
                # Execute script with stock data as context
                result, error = executor.execute(script_code, context={'row': stock})
                script_results[str(script_id)] = result if error is None else None
            except Exception as e:
                logger.error(f"Script {script_id} execution error: {e}")
                script_results[str(script_id)] = None
        
        # Append results to stock record
        stock['script_results'] = script_results

return create_success_response(data={"items": stocks, "total": len(stocks)})
```

---

## Testing

### Test 1: Basic API Call Without Scripts

```bash
curl "http://localhost:8000/api/stock-price/list?limit=10"
```

**Expected**: Returns stocks with base fields (no `script_results`)

---

### Test 2: API Call With Script IDs

```bash
curl "http://localhost:8000/api/stock-price/list?limit=10&script_ids=[1,2]"
```

**Expected**: Returns stocks with base fields + `script_results` containing results for scripts 1 and 2

**Sample Response**:
```json
{
  "code": 200,
  "message": "查询到 10 只股票",
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "market_code": "SH",
      "is_active": "Y",
      "close_price": 1750.50,
      "price_change_pct": 2.35,
      "volume": 12500000,
      "latest_trade_date": "2025-01-26",
      "script_results": {
        "1": 0.14,
        "2": 225.67
      }
    }
  ]
}
```

---

### Test 3: Invalid Script IDs

```bash
curl "http://localhost:8000/api/stock-price/list?limit=10&script_ids=[999,1000]"
```

**Expected**: Returns 404 error "脚本不存在"

---

### Test 4: Multiple Scripts

```bash
curl "http://localhost:8000/api/stock-price/list?limit=50&script_ids=[1,2,3]"
```

**Expected**: Returns stocks with results for all requested scripts

---

### Test 5: Market Code Filter + Scripts

```bash
curl "http://localhost:8000/api/stock-price/list?market_code=SH&limit=20&script_ids=[1]"
```

**Expected**: Returns only Shanghai stocks with script 1 results

**Verification**: Check that only SH.* stocks are returned, and script calculations match filtered stocks

---

### Test 6: Multiple Scripts

```bash
curl "http://localhost:8000/api/stock-price/list?limit=200&script_ids=[1,2,3]"
```

**Expected**: Successfully returns results for all requested scripts

---

## Validation Checklist

### Functionality

- [ ] API accepts `script_ids` parameter
- [ ] API validates script_ids format (array of integers)
- [ ] API validates script_ids
- [ ] API returns 404 for non-existent script_ids
- [ ] API executes scripts only for stocks in result set
- [ ] API respects limit, offset, market_code filters
- [ ] Script results appear in `script_results` field
- [ ] Failed scripts return null
- [ ] Response time acceptable (< 3s for 200 stocks + 3 scripts)

### Error Handling

- [ ] Invalid script_ids format → 400 error
- [ ] Non-existent script_id → 404 error
- [ ] Script execution error → null in response (doesn't block request)
- [ ] Database error → 500 error

### Edge Cases

- [ ] Empty script_ids array → works normally (no script_results)
- [ ] Single script_id → returns single result
- [ ] All scripts fail → returns all null
- [ ] Mix of success and failure → partial results
- [ ] Empty stock list → returns empty array

---

## Performance Considerations

**Note**: Response time depends on script complexity and database load. Simple calculations typically complete quickly.

---

## Rollback Plan

If issues occur:

1. **Immediate**: Revert to previous code (without script_ids support)
2. **Database**: No schema changes, safe to rollback anytime
3. **API**: No breaking changes, previous behavior still works

---

## Next Steps

1. **Implement Changes**:
   - Modify `app/routes/stock_price.py`
   - Add script_ids parameter parsing
   - Add script loading logic
   - Add script execution loop

2. **Test**:
   - Run all test cases above
   - Verify functionality and error handling

3. **Deploy**:
   - Commit changes
   - Push to main branch (per Constitution)
   - Verify in production

4. **Monitor**:
   - Watch response times
   - Check error logs
   - Ensure frontend compatibility

