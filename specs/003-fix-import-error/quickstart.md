# Quick Start: Fix Import Error

## Problem

The `/api/stock-price/list` endpoint returns 500 Internal Server Error with message:
```
name 'create_success_response' is not defined
```

## Solution

Add the missing import statement in `app/routes/stock_price.py`.

## Implementation Steps

### Step 1: Locate the File

File: `app/routes/stock_price.py`

### Step 2: Add Missing Import

Find line 8 (current imports):

```python
from app.utils.responses import (
    create_stock_data_response, 
    create_error_response,
    format_stock_price_data,
    validate_date_range,
    validate_symbol_format
)
```

Add `create_success_response`:

```python
from app.utils.responses import (
    create_stock_data_response, 
    create_error_response,
    create_success_response,  # Add this line
    format_stock_price_data,
    validate_date_range,
    validate_symbol_format
)
```

### Step 3: Verify the Fix

#### Manual Testing

1. Start the Flask application:
   ```bash
   python start_flask_app.py
   ```

2. Test the endpoint:
   ```bash
   curl "http://localhost:8000/api/stock-price/list?limit=10"
   ```

3. Expected response (200 OK):
   ```json
   {
     "code": 200,
     "message": "查询到 X 只股票",
     "timestamp": "2025-10-26 19:30:00",
     "data": [...],
     "total": X,
     "count": X
   }
   ```

#### Automated Testing

Run the test suite:
```bash
pytest tests/
```

## Verification Checklist

- [ ] Import statement added to `app/routes/stock_price.py`
- [ ] Application starts without errors
- [ ] `/api/stock-price/list` returns 200 OK
- [ ] Response format matches specification
- [ ] Edge cases (high limit, negative offset) return 400 errors
- [ ] No regressions in other endpoints

## Impact

- **Files Modified**: 1 (`app/routes/stock_price.py`)
- **Lines Added**: 1 (import statement)
- **Breaking Changes**: None
- **API Changes**: None (bug fix only)

## Rollback Plan

If issues occur, revert the single-line change by removing `create_success_response` from the import statement.

