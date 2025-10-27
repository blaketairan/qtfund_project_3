# Implementation Tasks: ETF Support in Data Query API

**Feature**: 006-etf-support  
**Generated**: 2025-10-27  
**Dependencies**: Python 3.11+, Flask 3.x, SQLAlchemy 2.0+, PostgreSQL with TimescaleDB

## Overview

Tasks for adding ETF filtering support to the stock list query API and ensuring custom script calculations work identically for ETFs and stocks.

## MVP Scope

**MVP User Stories**: US1 (ETF filtering), US2 (Script execution), US3 (ETF metadata)  
**Independent Test**: API successfully filters and returns ETF data with script calculation support

## Implementation Strategy

**Approach**: Incremental delivery by user story priority (P1 → P2)  
**Test Strategy**: Manual API testing via curl commands, verify response format matches contracts  
**Deployment**: Direct to main branch per constitution (I. Direct Development on Main)

---

## Phase 1: Setup & Database

- [x] T001 [P] Add is_etf column to stock_info table (database/migrations/)
- [x] T002 [P] Create database migration script for is_etf field (database/migrations/add_is_etf_column.sql)
- [x] T003 Run migration to add is_etf column with default 'N'
- [x] T004 Populate is_etf field based on stock_name pattern ('%ETF%')
- [x] T005 [P] Create indexes for ETF filtering performance (database/migrations/add_etf_indexes.sql)
- [x] T006 Run migration to add idx_symbol_etf and idx_is_etf_active indexes

---

## Phase 2: User Story 1 - ETF Filtering (P1)

**Goal**: Users can filter the API to show only ETFs, only stocks, or both.

**Independent Test**: Query with `is_etf=true` returns only ETFs, `is_etf=false` returns only stocks, no parameter returns both.

**Tasks**:

- [x] T007 [US1] Add is_etf parameter to list_stocks_with_latest_price() method in app/services/stock_data_service.py
- [x] T008 [US1] Add ETF filtering logic to WHERE clause in list_stocks_with_latest_price() in app/services/stock_data_service.py
- [x] T009 [US1] Parse is_etf parameter from request in app/routes/stock_price.py
- [x] T010 [US1] Add is_etf parameter validation (true/false) in app/routes/stock_price.py
- [x] T011 [US1] Pass is_etf parameter to service layer in app/routes/stock_price.py
- [x] T012 [US1] Test ETF-only query via curl (is_etf=true)
- [x] T013 [US1] Test stock-only query via curl (is_etf=false)
- [x] T014 [US1] Test combined query (is_etf + market_code) via curl

---

## Phase 3: User Story 2 - ETF Script Execution (P1)

**Goal**: Custom scripts execute on ETF data with same context as stocks.

**Independent Test**: ETF records receive script calculation results in same format as stocks.

**Tasks**:

- [x] T015 [US2] Verify script execution context includes is_etf field in app/routes/stock_price.py
- [x] T016 [US2] Test ETF script execution with existing momentum_score script
- [x] T017 [US2] Verify ETF script results format matches stock format
- [x] T018 [US2] Test ETF script error handling (null results when data insufficient)

---

## Phase 4: User Story 3 - ETF Metadata (P2)

**Goal**: API response includes ETF marker field for each instrument.

**Independent Test**: Every instrument record includes is_etf boolean field.

**Tasks**:

- [x] T019 [US3] Add is_etf field to response data formatting in app/services/stock_data_service.py
- [x] T020 [US3] Convert CHAR(1) 'Y'/'N' to boolean true/false in response
- [x] T021 [US3] Test ETF marker appears in all API responses
- [x] T022 [US3] Verify is_etf field appears for both stocks and ETFs in responses

---

## Phase 5: Polish & Integration

**Goal**: Complete feature with performance and error handling validation.

**Tasks**:

- [x] T023 Verify API response format matches contracts/api-contracts.json
- [x] T024 Test ETF filtering combines with existing filters (market_code, limit, offset)
- [x] T025 Verify query performance < 500ms for 200+ ETF results
- [x] T026 Test error handling for invalid is_etf parameter values
- [x] T027 Verify backward compatibility (default behavior unchanged when is_etf not provided)
- [x] T028 Commit ETF support implementation to main branch

---

## Dependency Graph

```
Setup (T001-T006)
    ↓
User Story 1: ETF Filtering (T007-T014)
    ↓
User Story 2: Script Execution (T015-T018) ← depends on US1
    ↓
User Story 3: ETF Metadata (T019-T022) ← depends on US1
    ↓
Polish & Integration (T023-T028)
```

**Parallel Opportunities**:
- T001-T006: Database migrations can be run in sequence but scripts are independent
- T015-T018: Can be tested in parallel after US1 completion
- T019-T022: Can be implemented alongside script execution tests

## Independent Test Criteria

**User Story 1**:
- ✅ Call `GET /api/stock-price/list?is_etf=true&limit=5` → Returns only ETFs
- ✅ Call `GET /api/stock-price/list?is_etf=false&limit=5` → Returns only stocks
- ✅ Call `GET /api/stock-price/list?is_etf=true&market_code=SH&limit=5` → Returns Shanghai ETFs only
- ✅ Call `GET /api/stock-price/list?limit=5` → Returns both stocks and ETFs

**User Story 2**:
- ✅ Call `GET /api/stock-price/list?is_etf=true&script_ids=[1]` → ETF records include script_results
- ✅ Script execution for ETF records works without errors
- ✅ ETF script results format matches stock format: `{"1": 0.093}`

**User Story 3**:
- ✅ All API responses include `is_etf` field (boolean)
- ✅ `is_etf: true` for ETF records, `is_etf: false` for stock records
- ✅ Frontend can distinguish ETFs from stocks using is_etf marker

## File Modification Summary

**Modified Files**:
- `app/services/stock_data_service.py` - Add is_etf parameter and filtering logic
- `app/routes/stock_price.py` - Add is_etf parameter parsing and validation

**Database Files**:
- `database/migrations/add_is_etf_column.sql` - Migration script (new)
- `database/migrations/add_etf_indexes.sql` - Index creation (new)

**No Changes Required**:
- `app/models/stock_data.py` - Already supports ETF data structure
- `app/services/sandbox_executor.py` - Script context already compatible
- API contracts - Already defined in contracts/api-contracts.json

## Implementation Notes

1. **Database Migration**: Run migrations before service layer changes to ensure is_etf column exists
2. **Backward Compatibility**: Default behavior (no is_etf param) returns all instruments unchanged
3. **Performance**: ETF filter adds minimal query cost, existing LATERAL JOIN optimization preserved
4. **Script Compatibility**: ETF data uses identical context as stocks, no script modifications needed

