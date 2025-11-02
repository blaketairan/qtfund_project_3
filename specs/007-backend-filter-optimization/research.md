# Research: Backend Market Filter and Unlimited Results

**Feature**: 007-backend-filter-optimization  
**Date**: 2025-10-27  
**Status**: Complete

## Overview

Research conducted to determine how to safely remove pagination limits, verify market filtering is database-level, and configure request timeout for long-running queries.

## Decisions Made

### Decision 1: Market Filtering Verification

**Chosen**: Market filtering is already implemented at database level (no changes needed)

**Rationale**:
- Current implementation in `app/services/stock_data_service.py` already adds market_code to SQL WHERE clause
- Filter applied before data retrieval, not client-side
- Code review confirms correct implementation

**Evidence**:
```python
# In list_stocks_with_latest_price()
if market_code:
    query += " AND si.market_code = :market_code"  # Database level
```

**Conclusion**: No code changes needed for market filtering - already correct.

**Alternatives Considered**:
- Client-side filtering: Already rejected - current implementation is database-level

### Decision 2: Remove Default Limit

**Chosen**: Make `limit` parameter optional with no default value

**Rationale**:
- Current code: `limit = request.args.get('limit', 100, type=int)` defaults to 100
- New behavior: `limit = request.args.get('limit', type=int)` defaults to None
- When limit is None, query returns all matching records
- Maintains backward compatibility - clients can still provide explicit limit

**Implementation**:
```python
# Before
limit = request.args.get('limit', 100, type=int)

# After
limit = request.args.get('limit', type=int)  # No default, None if not provided
if limit is None:
    limit = 999999  # Use very high limit for "all records" behavior
```

**SQL Changes**:
- Use `LIMIT :limit` with very high value (999999) when client doesn't provide limit
- Alternative: Remove LIMIT clause entirely when limit is None

**Alternatives Considered**:
- Remove LIMIT clause completely: Preferred - cleaner SQL, but requires conditional query building
- Use LIMIT ALL: Rejected - not universally supported
- Very high limit (999999): Chosen - simpler implementation, works with existing code

### Decision 3: Request Timeout Configuration

**Chosen**: Configure Flask/Gunicorn timeout to 600 seconds (10 minutes)

**Rationale**:
- Large dataset queries with script calculations may take several minutes
- Default Flask timeout (30s) insufficient
- Gunicorn default (30s) also needs increase

**Configuration Locations**:

1. **Flask Development Server** (`start_flask_app.py`):
   ```python
   # Not applicable - dev server doesn't support timeout config
   # Use Gunicorn for production
   ```

2. **Gunicorn Configuration**:
   ```python
   # gunicorn_config.py or command line
   timeout = 600  # 10 minutes
   graceful_timeout = 630  # Slightly longer for graceful shutdown
   ```

3. **Nginx/Reverse Proxy** (if applicable):
   ```nginx
   proxy_read_timeout 600s;
   proxy_connect_timeout 600s;
   proxy_send_timeout 600s;
   ```

**Implementation Strategy**:
- Add timeout configuration to application startup
- Document timeout in API contracts
- Add logging for long-running queries

**Alternatives Considered**:
- Async/background processing: Rejected - adds complexity, overkill for this use case
- Streaming response: Rejected - frontend expects complete JSON response
- 5-minute timeout: Rejected - insufficient for 2000+ instruments with multiple scripts

### Decision 4: Memory Optimization

**Chosen**: Stream results from database, use generator pattern where possible

**Rationale**:
- Loading 2000+ records into memory may cause issues
- SQLAlchemy's `yield_per()` can stream results
- Format results incrementally to avoid large list accumulation

**Implementation**:
```python
# Option 1: yield_per for large queries (requires changes)
query = query.yield_per(1000)

# Option 2: Process in chunks (simpler for current code)
results = query.all()  # Current approach - acceptable for 5000 records
```

**Decision**: Keep current approach (`all()`) for simplicity
- 5000 records × 200 bytes/record ≈ 1MB memory (acceptable)
- Complexity of streaming not justified for current scale

**Alternatives Considered**:
- Streaming response: Rejected - requires JSON Lines format, frontend changes
- Pagination required: Rejected - contradicts requirement to return all data
- Database cursor: Deferred - may implement if memory issues arise

### Decision 5: Backward Compatibility

**Chosen**: Maintain support for `limit` and `offset` parameters but mark as deprecated

**Rationale**:
- Existing clients may still use limit/offset
- Gradual migration path reduces breaking changes
- Allow both unlimited (default) and limited (explicit) queries

**Behavior**:
- `limit` not provided → Return all records
- `limit` explicitly provided → Honor the limit (backward compatible)
- `offset` only works when `limit` is provided

**Documentation**:
```json
{
  "limit": {
    "type": "integer",
    "required": false,
    "deprecated": true,
    "description": "Optional limit for backwards compatibility. If not provided, returns all records."
  }
}
```

**Alternatives Considered**:
- Remove limit/offset entirely: Rejected - breaks existing clients
- Require limit: Rejected - contradicts unlimited results requirement
- Default to unlimited: Chosen - aligns with requirement

## Technology Choices

### Flask Timeout Configuration

**Production Server**: Gunicorn or uWSGI

**Gunicorn Configuration**:
```python
# config/gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4
timeout = 600  # 10 minutes
graceful_timeout = 630
worker_class = "sync"  # Or "gevent" for async
```

**Start Command**:
```bash
gunicorn -c config/gunicorn_config.py start_flask_app:app
```

**Alternative - uWSGI**:
```ini
[uwsgi]
http-socket = :8000
module = start_flask_app:app
master = true
processes = 4
threads = 2
harakiri = 600  # 10 minutes timeout
```

### Database Connection Pool

**Current**: SQLAlchemy default pool settings

**Consideration**: Long-running queries may hold connections
- Pool size: Default (5) may be insufficient for concurrent long queries
- Pool recycle: Ensure connections don't timeout during long queries

**Recommended**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Increase from default 5
    max_overflow=20,
    pool_recycle=3600,  # 1 hour
    pool_pre_ping=True  # Verify connection before use
)
```

### SQL Query Optimization

**Current Implementation**: Already optimized
- LATERAL JOIN for latest price (efficient)
- Indexes on symbol, market_code, is_etf
- WHERE clause filters applied in database

**No Changes Needed**: Existing query structure supports unlimited results

## Performance Considerations

### Expected Performance

**Small Queries** (< 100 records):
- Database: < 100ms
- Script execution (if any): < 2 seconds
- Total: < 3 seconds

**Medium Queries** (100-500 records):
- Database: < 500ms
- Script execution (3 scripts × 500 stocks): ~30 seconds
- Total: < 1 minute

**Large Queries** (1000+ records):
- Database: < 2 seconds
- Script execution (3 scripts × 2000 stocks): ~5 minutes
- Total: < 6 minutes

### Bottlenecks

1. **Script Execution**: Dominant factor for large queries
   - Serial execution: 1 script × 1 stock × 0.01s = 0.01s per calculation
   - 3 scripts × 2000 stocks = 6000 calculations × 0.01s = 60 seconds minimum

2. **Database Query**: Minimal impact
   - LATERAL JOIN already optimized
   - Returning 2000 records vs 100 records: negligible difference

3. **Network Transfer**: Minimal
   - 2000 records × 500 bytes/record = 1MB JSON response (acceptable)

## Security Considerations

### Resource Limits

**Concern**: Malicious users could request all data with all scripts, causing resource exhaustion

**Mitigation**:
- Script limit already enforced (max 50 scripts per request)
- Database query timeout (inherits from connection pool)
- Server request timeout (600 seconds)
- Monitor for abuse patterns

**No Additional Changes Needed**: Existing safeguards sufficient

## References

- Existing LATERAL JOIN optimization: `specs/004-stock-data-display/research.md`
- Script execution limits: `specs/002-custom-calculation-api/research.md`
- Market filtering implementation: `app/services/stock_data_service.py` lines 254-256

