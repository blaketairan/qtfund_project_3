# Implementation Tasks: Backend Market Filter and Unlimited Results

**Feature**: 007-backend-filter-optimization  
**Generated**: 2025-10-27  
**Dependencies**: Python 3.11+, Flask 3.x, SQLAlchemy 2.0+, Gunicorn

## Overview

Tasks for removing default pagination limits, verifying market filtering is database-level, and configuring request timeout to support long-running queries.

## MVP Scope

**MVP User Stories**: US1 (Unlimited results), US2 (Backend filtering verification), US3 (Long-running queries)  
**Independent Test**: API returns all matching records without limit and completes large queries within 10 minutes

## Implementation Strategy

**Approach**: Configuration changes + minimal code updates  
**Test Strategy**: Progressive testing with increasing dataset sizes (100 → 500 → 1000 → 2000 records)  
**Deployment**: Direct to main branch per constitution

---

## Phase 1: Setup & Configuration

- [ ] T001 [P] Create Gunicorn configuration file (config/gunicorn_config.py)
- [ ] T002 [P] Add timeout constants to settings (config/settings.py)
- [ ] T003 Update start script to use Gunicorn with timeout config (bin/start.sh)
- [ ] T004 Verify Gunicorn package is installed (requirements.txt)

---

## Phase 2: User Story 1 - Unlimited Results (P1)

**Goal**: API returns all matching records when no limit is specified.

**Independent Test**: Query without limit parameter returns all stocks (500+).

**Tasks**:

- [ ] T005 [US1] Remove default value from limit parameter in app/routes/stock_price.py
- [ ] T006 [US1] Update limit validation to allow None in app/routes/stock_price.py
- [ ] T007 [US1] Set limit to 999999 when None in app/routes/stock_price.py
- [ ] T008 [US1] Update service method to handle very large limit values in app/services/stock_data_service.py
- [ ] T009 [US1] Test unlimited query (no limit param) returns all records
- [ ] T010 [US1] Test explicit limit still works (backward compatibility)

---

## Phase 3: User Story 2 - Backend Market Filtering (P1)

**Goal**: Verify market_code filtering executes at database level (no code changes needed).

**Independent Test**: SQL logs show market_code in WHERE clause, not application filtering.

**Tasks**:

- [ ] T011 [US2] Review existing market_code filtering implementation in app/services/stock_data_service.py
- [ ] T012 [US2] Verify market_code is added to SQL WHERE clause (lines 254-256)
- [ ] T013 [US2] Test market_code=SH returns only SH instruments
- [ ] T014 [US2] Test market_code=SZ returns only SZ instruments
- [ ] T015 [US2] Test combined filters (market_code + is_etf) work correctly
- [ ] T016 [US2] Document that market filtering is already database-level

---

## Phase 4: User Story 3 - Long-Running Queries (P1)

**Goal**: API supports queries taking up to 10 minutes without timeout.

**Independent Test**: Large query with scripts completes without 504 error.

**Tasks**:

- [ ] T017 [US3] Configure Gunicorn timeout to 600 seconds in config/gunicorn_config.py
- [ ] T018 [US3] Configure graceful_timeout to 630 seconds in config/gunicorn_config.py
- [ ] T019 [US3] Update bin/start.sh to use Gunicorn configuration
- [ ] T020 [US3] Test query with 500 records + 1 script (expect < 1 minute)
- [ ] T021 [US3] Test query with 1000 records + 3 scripts (expect 2-5 minutes)
- [ ] T022 [US3] Verify no 504 timeout error for queries < 10 minutes
- [ ] T023 [US3] Add logging for long-running queries (execution time tracking)

---

## Phase 5: Polish & Integration

**Goal**: Complete feature with performance validation and documentation.

**Tasks**:

- [ ] T024 Test API response format matches contracts/api-contracts.json
- [ ] T025 Test offset parameter still works with explicit limit
- [ ] T026 Verify memory usage acceptable for 2000-record queries
- [ ] T027 Document expected response times in quickstart.md
- [ ] T028 Add performance monitoring logs for query size and execution time
- [ ] T029 Verify backward compatibility (explicit limit/offset still work)
- [ ] T030 Commit implementation to main branch

---

## Dependency Graph

```
Setup (T001-T004)
    ↓
User Story 1: Unlimited Results (T005-T010)
    ↓
User Story 2: Backend Filtering (T011-T016) ← verification only, no dependencies
    ↓
User Story 3: Long-Running Queries (T017-T023) ← depends on US1
    ↓
Polish & Integration (T024-T030)
```

**Parallel Opportunities**:
- T001-T004: All setup tasks can run in parallel
- T011-T016: Verification tasks can run alongside US1 implementation
- T020-T022: Performance tests can run in parallel

## Independent Test Criteria

**User Story 1 - Unlimited Results**:
- ✅ Call `GET /api/stock-price/list` (no limit) → Returns all active stocks (1000+)
- ✅ Call `GET /api/stock-price/list?market_code=SH` → Returns all SH stocks (500+)
- ✅ Call `GET /api/stock-price/list?limit=10` → Returns exactly 10 (backward compatible)
- ✅ `count` equals `total` when no limit provided

**User Story 2 - Backend Filtering**:
- ✅ Call `GET /api/stock-price/list?market_code=SH` → All records have `market_code: "SH"`
- ✅ SQL logs show `WHERE si.market_code = 'SH'` in database query
- ✅ No client-side filtering in application code
- ✅ Combined filters (`market_code + is_etf`) both apply in database

**User Story 3 - Long-Running Queries**:
- ✅ Query 2000 records with 3 scripts completes within 10 minutes
- ✅ No 504 timeout error for queries < 10 minutes
- ✅ Gunicorn timeout configured to 600 seconds
- ✅ Long queries return complete results without truncation

## File Modification Summary

**Modified Files**:
- `app/routes/stock_price.py` - Remove default limit, update validation
- `config/gunicorn_config.py` - Create Gunicorn configuration with timeout (NEW)
- `bin/start.sh` - Update to use Gunicorn with config file
- `requirements.txt` - Verify Gunicorn is included

**No Changes**:
- `app/services/stock_data_service.py` - Market filtering already database-level
- Database schema - No changes needed
- API response format - Remains identical

## Implementation Notes

1. **Market Filtering**: Already correct at database level - no changes needed (US2 is verification only)
2. **Backward Compatibility**: Explicit `limit` parameter still works - only default value removed
3. **Performance**: Expected response times documented in quickstart for user expectations
4. **Timeout**: Gunicorn configuration required - development server doesn't support timeout config

