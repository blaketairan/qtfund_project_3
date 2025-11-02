# Backend Filter Optimization - Quickstart

**Feature**: 007-backend-filter-optimization  
**Date**: 2025-10-27

## Overview

Remove default pagination limit from stock list API, verify market filtering is database-level, and configure request timeout to support long-running queries with large datasets.

## Changes Summary

### 1. Remove Default Limit

Modify `app/routes/stock_price.py`:

**Change**:
```python
# Before
limit = request.args.get('limit', 100, type=int)  # Default 100

# After
limit = request.args.get('limit', type=int)  # No default
if limit is None:
    limit = 999999  # Effectively unlimited
```

**Validation Update**:
```python
# Before
if limit > 10000:
    return create_error_response(...)

# After
if limit is not None and limit > 10000:  # Only validate if limit provided
    return create_error_response(...)
```

### 2. Configure Request Timeout

**Option A: Gunicorn Configuration** (Production)

Create `config/gunicorn_config.py`:

```python
"""Gunicorn configuration for production deployment"""

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = 4
worker_class = "sync"  # or "gevent" for async

# Timeouts
timeout = 600  # 10 minutes for long-running queries
graceful_timeout = 630  # Slightly longer for graceful shutdown
keepalive = 5

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
```

**Start Command**:
```bash
gunicorn -c config/gunicorn_config.py start_flask_app:app
```

**Option B: Start Script Update** (Alternative)

Modify `bin/start.sh`:

```bash
#!/bin/bash
# Start with Gunicorn and 10-minute timeout
gunicorn --bind 0.0.0.0:8000 \
         --workers 4 \
         --timeout 600 \
         --graceful-timeout 630 \
         --access-logfile logs/gunicorn_access.log \
         --error-logfile logs/gunicorn_error.log \
         start_flask_app:app
```

### 3. Verify Market Filtering (No Changes)

Market filtering is already database-level in `app/services/stock_data_service.py`:

```python
# Already correct - no changes needed
if market_code:
    query += " AND si.market_code = :market_code"  # Database WHERE clause
```

## Testing

### 1. Test Unlimited Results

```bash
# Query all SH stocks (no limit)
curl "http://localhost:8000/api/stock-price/list?market_code=SH"
```

**Expected**:
- Returns all SH stocks (500+)
- `count` equals `total`
- Response time: 1-5 seconds

### 2. Test Backward Compatibility

```bash
# Query with explicit limit (backward compatible)
curl "http://localhost:8000/api/stock-price/list?market_code=SH&limit=10"
```

**Expected**:
- Returns only 10 stocks
- `count` = 10, `total` > 10

### 3. Test Long-Running Query

```bash
# Query all stocks with multiple scripts
time curl "http://localhost:8000/api/stock-price/list?script_ids=[1,2,3]"
```

**Expected**:
- Completes within 10 minutes
- Returns all stocks with script calculations
- No 504 timeout error

### 4. Test Market Filter Accuracy

```bash
# Query SH market
curl "http://localhost:8000/api/stock-price/list?market_code=SH" | jq '.data[].market_code' | sort -u
```

**Expected Output**:
```
"SH"
```

All records should be SH market only (not SZ or BJ).

### 5. Test ETF + Market Combination

```bash
# Query SH ETFs only
curl "http://localhost:8000/api/stock-price/list?market_code=SH&is_etf=true"
```

**Expected**:
- Returns only SH market ETFs
- All records have `market_code: "SH"` and `is_etf: true`

## Validation Checklist

### API Behavior

- [ ] No limit parameter → Returns all matching records
- [ ] Explicit limit parameter → Honors the limit (backward compatible)
- [ ] market_code filter applied in database (verify with SQL logs)
- [ ] Queries with 500+ results complete successfully
- [ ] Queries with script calculations don't timeout within 10 minutes

### Configuration

- [ ] Gunicorn timeout set to 600 seconds
- [ ] Graceful timeout set to 630 seconds
- [ ] Application starts successfully with new configuration
- [ ] Long-running queries don't cause 504 errors

### Performance

- [ ] Query time scales linearly with result count
- [ ] 2000 records without scripts: < 5 seconds
- [ ] 2000 records with 3 scripts: < 6 minutes
- [ ] Memory usage acceptable (< 500MB for large queries)

### Error Handling

- [ ] Invalid limit values return 400 error
- [ ] Database errors handled gracefully
- [ ] Timeout after 10 minutes returns appropriate error

## Rollback Plan

If issues arise:

1. **Revert route handler**:
   ```bash
   git checkout HEAD~1 app/routes/stock_price.py
   ```

2. **Revert Gunicorn config**:
   ```bash
   git checkout HEAD~1 config/gunicorn_config.py
   # Or restore timeout to 30 seconds
   ```

3. **Restart application**:
   ```bash
   bin/stop.sh
   bin/start.sh
   ```

## Next Steps

1. Update route handler to remove default limit
2. Create Gunicorn configuration file
3. Update start script to use Gunicorn with timeout config
4. Test with progressively larger datasets (100 → 500 → 1000 → 2000)
5. Monitor memory and performance
6. Document expected response times in API docs

