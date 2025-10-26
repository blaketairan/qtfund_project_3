# Tasks: Fix Import Error in Stock Price Routes

**Input**: Design documents from `/specs/003-fix-import-error/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, quickstart.md

**Tests**: This is a simple bug fix - no new tests required. Only verification tests included.

**Organization**: This fix is so simple it only requires 1 task. Task is grouped under the user story it fixes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Files in `app/` directory
- Target file: `app/routes/stock_price.py`
- Function exists in: `app/utils/responses.py`

---

## Phase 1: Implementation (Bug Fix)

**Purpose**: Fix the missing import that causes 500 error

### User Story 1 - Access Stock List API (Priority: P1) 🎯 MVP

**Goal**: Fix the missing import statement so users can successfully retrieve a list of stocks via the `/api/stock-price/list` endpoint without encountering server errors.

**Independent Test**: Request `GET /api/stock-price/list?limit=200` and verify it returns 200 OK with proper JSON data instead of 500 Internal Server Error.

### Implementation for User Story 1

- [x] T001 [US1] Add missing import `create_success_response` to imports list in `app/routes/stock_price.py`

**Details**: 
- Open file `app/routes/stock_price.py`
- Find line 8 where imports are defined
- Add `create_success_response` to the import statement from `app.utils.responses`
- Current import (lines 7-14) has 5 functions but missing `create_success_response`
- Function is used at lines 109 and 161 but was never imported
- Function exists and is available in `app/utils/responses.py`

**Required Change**:
```python
from app.utils.responses import (
    create_stock_data_response, 
    create_error_response,
    create_success_response,  # <-- Add this line
    format_stock_price_data,
    validate_date_range,
    validate_symbol_format
)
```

**Checkpoint**: At this point, User Story 1 should be fully functional and the endpoint should return 200 OK

---

## Phase 2: Verification (Testing)

**Purpose**: Verify the fix works correctly

- [x] T002 [US1] Manual test: Start application and verify `/api/stock-price/list?limit=10` returns 200 OK
- [x] T003 [US1] Verify response format matches specification (code, message, timestamp, data fields)
- [x] T004 [US1] Test edge case: Verify limit > 10000 still returns 400 error (not 500)
- [x] T005 [US1] Test edge case: Verify offset < 0 still returns 400 error (not 500)
- [x] T006 [US1] Regression test: Verify other endpoints (/query, /info) still work correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Implementation (Phase 1)**: No dependencies - can start immediately
- **Verification (Phase 2)**: Depends on Implementation completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start immediately - no dependencies on other stories

### Within User Story 1

- Single task to add import statement
- Verification must happen after implementation

### Parallel Opportunities

- Verification tasks (T002, T003, T004, T005, T006) can run in parallel after T001 completes

---

## Parallel Example

```bash
# All verification tests can run in parallel:
Task: "Manual test: Start application and verify endpoint"
Task: "Verify response format matches specification"
Task: "Test edge case: Verify limit > 10000 returns 400"
Task: "Test edge case: Verify offset < 0 returns 400"
Task: "Regression test: Verify other endpoints still work"
```

---

## Implementation Strategy

### MVP First (Single Fix)

1. Complete Phase 1: Add missing import (T001)
2. Complete Phase 2: Verify the fix (T002-T006)
3. **STOP and VALIDATE**: Test endpoint independently
4. Deploy/demo if ready

### Incremental Delivery

1. Fix the import → Test independently → Deploy
2. Each verification test confirms the fix doesn't break anything
3. No new features, just bug fix

### Single Developer Strategy

1. Developer adds the import (1 minute)
2. Developer runs all verification tests
3. Done!

---

## Notes

- This is an extremely simple bug fix requiring only 1 code change
- No architectural changes required
- No new dependencies
- Backward compatible
- No breaking changes
- Verification is critical to ensure fix works and doesn't introduce regressions
- Total time estimate: 5-10 minutes
- Files modified: 1 (`app/routes/stock_price.py`)
- Lines changed: 1 (add import statement)

