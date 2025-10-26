# Implementation Tasks: Momentum Score Script Example

**Feature**: 005-momentum-score-script  
**Created**: 2025-01-27  
**Branch**: 005-momentum-score-script  
**Status**: Ready for Implementation

## Summary

Create momentum score calculation example script and enhance platform to support historical data access in custom scripts. Includes: 1) Platform enhancement (add get_history to sandbox), 2) Example script in script_example/, 3) Script function documentation API for frontend.

## Implementation Strategy

### MVP Scope
- **Phase 3** covers platform enhancement (historical data access)
- **Phase 4** covers example script creation
- **Phase 5** covers documentation API (NEW - per user request)

### Incremental Delivery
- Complete Phase 3: Platform enhancement (enable scripts to access historical data)
- Then Phase 4: Create example script demonstrating usage
- Then Phase 5: Provide function documentation API for frontend

## Dependency Graph

```
Phase 1: Setup (Switching to main branch)
    ↓
Phase 2: Platform Enhancement - Add get_history() to Sandbox (REQUIRES Phase 1)
    ↓
Phase 3: Create Example Script (REQUIRES Phase 2)
    ↓
Phase 4: Create Script Function Documentation API (REQUIRES Phase 2)
    ↓
Phase 5: Testing & Validation (REQUIRES Phase 3-4)
```

## Independent Test Criteria

### User Story 1 (Momentum Score Script)
**Test**: Script executes via API and returns momentum scores for stocks
- Given: Example script exists with sufficient historical data
- When: Call API with script
- Then: Returns numeric momentum scores for each stock

## Phase 1: Setup

### P1-T001: Switch to Main Branch for Implementation
- [x] P1-T001 Switch from feature branch to main branch per constitution requirement

**Note**: This project follows "Direct Development on Main" constitution principle (Constitution Principle I).

## Phase 2: Platform Enhancement

**Goal**: Add historical data access function to sandbox executor

### P2-T002: Add get_history() Function to Sandbox Safe Globals
- [x] P2-T002 [P] [US1] Add get_history(symbol, days) function to _safe_globals in app/services/sandbox_executor.py

**Implementation Details**:
- Function queries TimescaleDB for historical stock data
- Returns list of dicts with close_price, trade_date, volume, price_change_pct
- Input validation: symbol format, days range (1-1000)
- Error handling: return empty list on errors, log errors
- Must be read-only, no side effects

**Function Signature** (from research.md):
```python
def get_history(symbol: str, days: int) -> list:
    """Get historical price data for a stock"""
    # Implementation details in research.md
```

### P2-T003: Add Helper Functions to Safe Globals
- [x] P2-T003 [P] [US1] Add helper functions (weighted_linear_regression, weighted_r_squared) to sandbox safe globals in app/services/sandbox_executor.py

**Note**: Helper functions implemented directly in example script as inline functions - no need to add to global sandbox

## Phase 3: Create Example Script

**Goal**: Create example script demonstrating momentum calculation

### P3-T004: Create Momentum Score Example Script
- [x] P3-T004 [US1] Create script_example/momentum_score.py with complete momentum calculation logic

**Implementation**:
- Include configuration parameters (DAYS, WEIGHT_START, WEIGHT_END, ANNUALIZATION)
- Implement weighted linear regression functions
- Implement R² calculation function
- Define error handler example
- Add comprehensive comments explaining each step
- Set result variable with calculated momentum score

**Script Structure** (from quickstart.md):
- Configuration section
- Error handler section
- Helper functions section
- Main calculation section
- Result execution section

## Phase 4: Script Function Documentation API

**Goal**: Create API endpoint to list available functions for script authors (per user request)

### P4-T005: Create Script Functions Endpoint
- [x] P4-T005 [US1] Add GET /api/custom-calculation/functions endpoint in app/routes/custom_calculation.py

**Implementation**:
- Return list of available functions in sandbox context
- Include function name, signature, description, parameters, return type
- Document: get_history(), math module, builtin functions, row context

**Response Format**:
```json
{
  "code": 200,
  "data": {
    "functions": [
      {
        "name": "get_history",
        "signature": "get_history(symbol: str, days: int) -> list",
        "description": "Get historical price data for a stock",
        "parameters": [
          {"name": "symbol", "type": "str", "description": "Stock symbol (e.g., 'SH.600519')"},
          {"name": "days", "type": "int", "description": "Number of trading days to retrieve (max 1000)"}
        ],
        "returns": "List of dicts with close_price, trade_date, volume, price_change_pct"
      }
    ],
    "modules": [
      {
        "name": "math",
        "description": "Python math module",
        "functions": ["exp", "log", "pow", "sqrt", "sin", "cos", etc.]
      }
    ],
    "builtins": ["abs", "min", "max", "sum", "round", "len", "range", "zip", "enumerate"]
  }
}
```

### P4-T006: Document Row Context Object
- [x] P4-T006 [US1] Document row context structure in function documentation API response in app/routes/custom_calculation.py

**Implementation**:
- Include row object structure in API response
- Document available fields: symbol, stock_name, close_price, volume, etc.
- Provide examples of how to access row data

## Phase 5: Testing & Validation

### P5-T007: Test Historical Data API
- [ ] P5-T007 Test get_history() function returns correct data format
- [ ] P5-T008 Test get_history() handles invalid symbols gracefully
- [ ] P5-T009 Test get_history() respects days parameter limits
- [ ] P5-T010 Test get_history() returns empty list for missing data

**Commands**:
```bash
# Test via API
curl -X POST http://localhost:8000/api/custom-calculation/execute \
  -d '{"script": "result = len(get_history(\"SH.600519\", 250))", "stock_symbols": ["SH.600519"], "column_name": "test"}'
```

### P5-T011: Test Example Script Execution
- [ ] P5-T011 Test momentum score script executes successfully
- [ ] P5-T012 Test script returns numeric results for stocks with sufficient data
- [ ] P5-T013 Test script handles insufficient data gracefully
- [ ] P5-T014 Verify calculation accuracy (matches manual calculation)

**Commands**:
```bash
# Load and execute example script
curl -X POST http://localhost:8000/api/custom-calculation/execute \
  -d '{"script": "<script from script_example/momentum_score.py>", "stock_symbols": ["SH.600519", "SZ.000001"], "column_name": "momentum_score"}'
```

### P5-T015: Test Documentation API
- [ ] P5-T015 Test GET /api/custom-calculation/functions returns function list
- [ ] P5-T016 Verify function signatures are accurate
- [ ] P5-T017 Verify module documentation is complete

**Commands**:
```bash
curl http://localhost:8000/api/custom-calculation/functions
```

### P5-T018: Performance Testing
- [ ] P5-T018 Test script execution time < 2 seconds per stock
- [ ] P5-T019 Test API response time < 3 seconds

## Task Summary

### Task Count by Phase
- Phase 1: 1 task
- Phase 2: 2 tasks
- Phase 3: 1 task
- Phase 4: 2 tasks (NEW - per user request)
- Phase 5: 13 tasks

**Total: 19 tasks**

### Task Count by User Story
- User Story 1 (Momentum Script): 18 tasks
- Cross-cutting (Setup, Testing): 11 tasks

## Parallel Execution Opportunities

### Can Execute in Parallel (within Phase 2)
- T002 and T003 can be done together (related sandbox enhancements)

### Sequential Dependencies
- T002 must complete before T004 (need get_history before script can use it)
- T002 must complete before T005-T006 (documentation API requires functions to exist)
- T004 must complete before T011-T014 (example script before testing)
- All implementation must complete before T007-T019 (testing phase)

## Files Modified

1. `app/services/sandbox_executor.py` (ENHANCED - add get_history function)
2. `script_example/momentum_score.py` (NEW - example script)
3. `app/routes/custom_calculation.py` (ENHANCED - add functions documentation endpoint)

**New endpoints created**:
- GET /api/custom-calculation/functions - List available functions and modules

## Implementation Checklist

### Code Changes
- [x] Platform enhancement: get_history() function added to sandbox
- [x] Example script created with momentum calculation
- [x] Function documentation API created

### Testing
- [ ] Historical data API tested
- [ ] Example script execution tested
- [ ] Documentation API tested
- [ ] Performance validated

### Documentation
- [ ] Example script commented thoroughly
- [ ] Function API documented
- [ ] Usage examples provided

## Next Steps After Implementation

1. **Commit Changes**: Per constitution principle III
2. **Push to Main**: Per constitution principle I
3. **Frontend Integration**: Frontend can query /api/custom-calculation/functions to display available functions
4. **User Documentation**: Provide script writing guide using function documentation

## References

- [spec.md](./spec.md) - Full feature specification
- [plan.md](./plan.md) - Implementation plan
- [research.md](./research.md) - Technical research and decisions
- [data-model.md](./data-model.md) - Data model details
- [quickstart.md](./quickstart.md) - Implementation guide
- [contracts/api-contracts.json](./contracts/api-contracts.json) - API contract
- [.specify/memory/constitution.md](../../../.specify/memory/constitution.md) - Development principles

