# Implementation Tasks: Stock Data Display on Dashboard

**Feature**: 004-stock-data-display  
**Created**: 2025-01-27  
**Branch**: 004-stock-data-display  
**Status**: Ready for Implementation

## Summary

Implement enhanced stock list API that returns latest price, change percentage, and volume for each stock. This requires modifying the service layer to add a new method using LATERAL JOIN, and updating the route handler to use this method.

## Implementation Strategy

### MVP Scope
- **Phase 3** covers User Stories 1-3 (all P1): Return price, change %, and volume data
- These are implemented together since they require the same SQL query modification
- User Story 4 (P2) is performance optimization, can follow in Phase 4

### Incremental Delivery
- Complete Phase 3: Core functionality (price data display)
- Verify with manual testing
- Then proceed to Phase 4: Performance optimization if needed

## Dependency Graph

```
Phase 1: Setup (Switching to main branch)
    ↓
Phase 2: Service Enhancement (No dependencies)
    ↓
Phase 3: User Stories 1-3 [P1] (Price, Change%, Volume) - REQUIRES Phase 2
    ↓
Phase 4: User Story 4 [P2] (Performance Optimization) - REQUIRES Phase 3
    ↓
Phase 5: Polish & Testing - REQUIRES Phase 3-4
```

## Independent Test Criteria

### User Story 1 (Price Data)
**Test**: API returns `close_price` field with actual numerical values
- Given: Database has stock price data
- When: Call `/api/stock-price/list`
- Then: Response includes `close_price` field with values

### User Story 2 (Price Change %)
**Test**: API returns `price_change_pct` field with calculated percentage
- Given: Database has daily price data
- When: Call API
- Then: Response includes `price_change_pct` field with correct calculation

### User Story 3 (Volume)
**Test**: API returns `volume` field with trading volume
- Given: Database has volume data
- When: Call API  
- Then: Response includes `volume` field

### User Story 4 (Performance)
**Test**: API responds within 2 seconds for 200+ stocks
- Given: Database has 500+ stocks with price data
- When: Request stock list
- Then: Response time < 2 seconds, query time < 500ms

## Phase 1: Setup

### P1-T001: Switch to Main Branch for Implementation
- [x] P1-T001 Switch from feature branch to main branch per constitution requirement

**Note**: This project follows "Direct Development on Main" constitution principle (Constitution Principle I).

## Phase 2: Service Enhancement

### P2-T002: Add Service Method with LATERAL JOIN
- [x] P2-T002 [P] [US1] [US2] [US3] Add method `list_stocks_with_latest_price()` in app/services/stock_data_service.py

**Implementation Details**:
- Use LATERAL JOIN to fetch latest price data efficiently
- Return: close_price, price_change_pct, volume, latest_trade_date
- Handle NULL values gracefully for stocks without price data
- Apply existing filters (market_code, is_active, limit, offset)

**SQL Pattern** (from research.md):
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
    SELECT close_price, volume, price_change_pct, trade_date
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

## Phase 3: User Stories 1-3 - Price Data Display (P1)

**Goal**: API returns latest price, change percentage, and volume for each stock

### P3-T003: Update Route Handler
- [x] P3-T003 [US1] [US2] [US3] Update `list_stocks()` endpoint in app/routes/stock_price.py to call new service method

**Implementation**:
- Call `service.list_stocks_with_latest_price()` instead of `list_all_stocks_from_db()`
- Maintain existing parameter validation
- Response format includes new price fields

### P3-T004: Format Response Data
- [x] P3-T004 [US1] [US2] [US3] Ensure response includes all required fields (close_price, price_change_pct, volume, latest_trade_date) in app/services/stock_data_service.py

**Validation**:
- Return null (not missing field) when price data unavailable
- Convert DECIMAL to float, BIGINT to int for JSON
- Format dates as YYYY-MM-DD for latest_trade_date
- Format ISO 8601 for last_sync_date

## Phase 4: User Story 4 - Performance Optimization (P2)

**Goal**: Optimize database queries for 200+ stocks

### P4-T005: Verify Query Performance
- [ ] P4-T005 [US4] Test database query execution time for 500+ stocks in app/services/stock_data_service.py

**Acceptance Criteria**:
- Query executes in < 500ms
- API response time < 2 seconds for 200+ stocks
- No N+1 query pattern

**Verification Method**:
```sql
EXPLAIN ANALYZE
SELECT ... FROM stock_info si
LEFT JOIN LATERAL (...) lp ON true
WHERE si.is_active = 'Y'
LIMIT 500;
```

### P4-T006: Index Verification
- [ ] P4-T006 [US4] Verify existing indexes are used efficiently (idx_symbol_date, idx_trade_date) in database connection

**Note**: Indexes already exist from models/stock_data.py, just verify usage

## Phase 5: Testing & Validation

### P5-T007: Manual API Testing
- [ ] P5-T007 Test API returns price data for stocks with available data
- [ ] P5-T008 Test API returns null for stocks without price data (not missing)
- [ ] P5-T009 Test price change percentage is calculated correctly
- [ ] P5-T010 Test volume data is included when available
- [ ] P5-T011 Test market filter works correctly (market_code parameter)
- [ ] P5-T012 Test pagination works correctly (limit/offset parameters)

**Commands**:
```bash
# Basic test
curl "http://localhost:5000/api/stock-price/list?limit=10"

# Market filter
curl "http://localhost:5000/api/stock-price/list?market_code=SH&limit=5"

# Pagination
curl "http://localhost:5000/api/stock-price/list?limit=10&offset=10"
```

### P5-T013: Performance Testing
- [ ] P5-T013 [US4] Test API response time with 200+ stocks
- [ ] P5-T014 [US4] Verify response time < 2 seconds

**Command**:
```bash
time curl "http://localhost:5000/api/stock-price/list?limit=250"
```

### P5-T015: Error Handling Verification
- [ ] P5-T015 Test API handles missing price data gracefully
- [ ] P5-T016 Test API returns null values instead of crashing
- [ ] P5-T017 Test API returns appropriate error for invalid parameters

## Task Summary

### Task Count by Phase
- Phase 1: 1 task
- Phase 2: 1 task  
- Phase 3: 2 tasks
- Phase 4: 2 tasks
- Phase 5: 11 tasks

**Total: 17 tasks**

### Task Count by User Story
- User Story 1 (Price): 3 tasks
- User Story 2 (Change %): 3 tasks
- User Story 3 (Volume): 3 tasks
- User Story 4 (Performance): 4 tasks
- Cross-cutting (Setup, Testing): 8 tasks

## Parallel Execution Opportunities

### Can Execute in Parallel (within Phase 3)
- T003 and T004 can be done together (related service and route updates)
- T007-T012 can be done in parallel (different test cases)

### Sequential Dependencies
- T002 must complete before T003 (service method before route update)
- T003 must complete before T005-T006 (implement before performance testing)
- All implementation must complete before T007-T017 (testing phase)

## Files Modified

1. `app/services/stock_data_service.py` (NEW method added)
2. `app/routes/stock_price.py` (UPDATED endpoint)

**No new files created** - only enhancements to existing files

## Implementation Checklist

### Code Changes
- [x] Service layer enhanced with LATERAL JOIN query
- [x] Route handler updated to use new method
- [x] Response format includes all price fields
- [x] NULL handling implemented for missing data

### Testing
- [ ] Manual API testing completed
- [ ] Performance testing passed (< 2s for 200+ stocks)
- [ ] Error handling verified
- [ ] All acceptance scenarios met

### Documentation
- [ ] Code comments added for complex logic
- [ ] Quickstart.md guide followed
- [ ] Constitution compliance verified

## Next Steps After Implementation

1. **Commit Changes**: Independent commit per constitution principle III
2. **Push to Main**: Per constitution principle I (Direct Development on Main)
3. **Frontend Integration**: Frontend can now display price data with Chinese column headers
4. **Monitor Performance**: Track API response times in production
5. **Future Enhancements**: Consider caching if performance degrades with scale

## References

- [spec.md](./spec.md) - Full feature specification
- [plan.md](./plan.md) - Implementation plan
- [research.md](./research.md) - Technical research and SQL patterns
- [data-model.md](./data-model.md) - Data model details  
- [quickstart.md](./quickstart.md) - Implementation guide
- [contracts/api-contracts.json](./contracts/api-contracts.json) - API contract
- [.specify/memory/constitution.md](../../../.specify/memory/constitution.md) - Development principles

