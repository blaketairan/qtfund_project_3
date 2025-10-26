# Tasks: Dynamic Script Columns in List Query

**Input**: Design documents from `specs/005-dynamic-column-scripts/`  
**Feature**: Add `script_ids` parameter support to `/api/stock-price/list` endpoint  
**Estimated Time**: 2-4 hours

**Prerequisites**: All design documents complete (plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md)

---

## Phase 1: Setup (Preparation)

**Purpose**: Review existing code structure and identify modification points

- [ ] T001 Review existing `app/routes/stock_price.py` structure
- [ ] T002 Review existing `app/services/sandbox_executor.py` API
- [ ] T003 Review existing `app/models/custom_script.py` model

---

## Phase 2: User Story - Dynamic Script Columns (Priority: P1) 🎯

**Goal**: Enhance `/api/stock-price/list` to accept `script_ids` parameter and return script calculation results for stocks in the query result set.

**Independent Test**: When calling `/api/stock-price/list?script_ids=[1,2]`, the API returns stock data with `script_results` field containing calculated values from scripts 1 and 2 for each stock in the result set.

### Implementation Tasks

- [ ] T004 [P] Parse `script_ids` query parameter in `app/routes/stock_price.py` `list_stocks()` endpoint
- [ ] T005 [P] Validate `script_ids` format (array of integers, reasonable limit to prevent abuse)
- [ ] T006 Load scripts from database using script_ids in `app/routes/stock_price.py`
- [ ] T007 Validate all script_ids exist in database in `app/routes/stock_price.py`
- [ ] T008 Execute scripts for each stock in result set using SandboxExecutor in `app/routes/stock_price.py`
- [ ] T009 Append script_results to each stock record in `app/routes/stock_price.py`
- [ ] T010 Handle script execution errors gracefully (return null for failed scripts) in `app/routes/stock_price.py`
- [ ] T011 Add logging for script execution operations in `app/routes/stock_price.py`
- [ ] T012 Ensure script calculations respect limit, offset, and market_code filters in `app/routes/stock_price.py`

---

## Phase 3: Testing & Validation

**Purpose**: Verify implementation works correctly

- [ ] T013 Test API with valid script_ids parameter
- [ ] T014 Test API with non-existent script_ids (should return 404)
- [ ] T015 Test API with invalid script_ids format (should return 400)
- [ ] T016 Test script execution only for stocks in query result set (limit, offset, market_code)
- [ ] T017 Test error handling when script execution fails for specific stocks
- [ ] T018 Test response structure matches API contract in `specs/005-dynamic-column-scripts/contracts/api-contracts.json`
- [ ] T019 Verify backward compatibility (API works without script_ids parameter)

---

## Dependencies & Execution Order

### Task Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Implementation (Phase 2)**: 
  - T004-T005: Can be done in parallel (parameter parsing and validation)
  - T006-T007: Must be done after T004-T005 (load and validate scripts)
  - T008-T012: Must be done after T006-T007 (execute scripts and build response)
- **Testing (Phase 3)**: Must be done after all Phase 2 tasks complete

### Execution Flow

```
1. Review existing code (T001-T003) ✓
2. Parse and validate script_ids (T004-T005) ✓
3. Load and validate scripts (T006-T007) ✓
4. Execute scripts for stocks (T008-T012) ✓
5. Test implementation (T013-T019) ✓
```

---

## Parallel Opportunities

- T004 and T005 can be done in parallel (both work on parsing/validation logic)
- T008-T011 can be done in sequence but share the same file (logical grouping)
- Test tasks T013-T019 can be done independently by test scenario

---

## Implementation Strategy

### MVP Scope

Complete all tasks in Phase 1 and Phase 2 to deliver the full feature. This is a small, focused enhancement to an existing API endpoint.

### Incremental Delivery

1. Complete Setup (Phase 1)
2. Complete Implementation (Phase 2)
3. Complete Testing (Phase 3)
4. Deploy to main branch

### Key Implementation Points

1. **Parameter Parsing**: Extract and validate `script_ids` from query string
2. **Script Loading**: Load scripts from `custom_scripts` table by IDs
3. **Script Execution**: Use existing `SandboxExecutor` for each stock
4. **Response Enhancement**: Add `script_results` object to each stock record
5. **Error Handling**: Return null for failed scripts, don't block response

### Files to Modify

- `app/routes/stock_price.py` - Main modification point
  - Add script_ids parameter handling
  - Load scripts from database
  - Execute scripts using SandboxExecutor
  - Build enhanced response with script_results

### No New Files Required

- Uses existing `SandboxExecutor`
- Uses existing `CustomScript` model
- Uses existing database connection

---

## Notes

- This is an additive feature - no breaking changes to existing API
- Backward compatible: API works without script_ids parameter
- Script execution scoped to query result set (respects filters)
- Error handling ensures failed scripts don't block response
- All three user stories (US1, US2, US3) are addressed by the same implementation

