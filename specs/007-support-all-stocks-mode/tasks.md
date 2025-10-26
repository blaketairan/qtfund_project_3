# Implementation Tasks: Support All-Stocks Mode for Custom Calculations

**Feature**: 007-support-all-stocks-mode  
**Created**: 2025-01-27  
**Branch**: 007-support-all-stocks-mode  
**Status**: Ready for Implementation

## Summary

Extend custom calculation API to support applying scripts to all active stocks without requiring the stock_symbols array. When stock_symbols is empty, the API automatically fetches all active stocks and applies the script to each stock.

## Implementation Strategy

### MVP Scope
- **Phase 3** covers complete feature (all-stocks mode + backward compatibility)

### Incremental Delivery
- Service layer enhancement (add get_all_active_stocks method)
- API endpoint modification (handle empty array)
- Testing and validation

## Dependency Graph

```
Phase 1: Setup (Switching to main branch)
    ↓
Phase 2: Service Enhancement - Add get_all_active_stocks() (REQUIRES Phase 1)
    ↓
Phase 3: API Modification - Handle Empty Array (REQUIRES Phase 2)
    ↓
Phase 4: Testing & Validation (REQUIRES Phase 3)
```

## Independent Test Criteria

### User Story 1 (All Stocks Mode)
**Test**: API with empty stock_symbols returns results for all active stocks
- Given: API receives empty stock_symbols array
- When: Execute script for all stocks
- Then: Returns results for all active stocks with execution summary

## Phase 1: Setup

### P1-T001: Switch to Main Branch for Implementation
- [x] P1-T001 Switch from feature branch to main branch per constitution requirement

**Note**: This project follows "Direct Development on Main" constitution principle (Constitution Principle I).

## Phase 2: Service Enhancement

**Goal**: Add method to fetch all active stocks from database

### P2-T002: Add get_all_active_stocks() Method
- [x] P2-T002 [US1] Add get_all_active_stocks(market_code) method to app/services/stock_data_service.py

**Implementation Details**:
- Query database for stocks with is_active='Y'
- Return list of stock symbols
- Support optional market_code parameter
- Handle database errors gracefully

**Function Signature** (from research.md and quickstart.md):
```python
def get_all_active_stocks(self, market_code: Optional[str] = None) -> List[str]:
    """Get all active stock symbols from database"""
    # Query stock_info table for is_active='Y'
    # Return list of symbols
```

## Phase 3: API Modification

**Goal**: Modify API endpoint to handle empty stock_symbols array

### P3-T003: Modify Validation Logic
- [x] P3-T003 [US1] Remove rejection of empty stock_symbols array in app/routes/custom_calculation.py

**Implementation**:
- Modify validation to allow empty array
- Change check from "must be non-empty" to "can be empty"
- Keep validation for other parameters (script, column_name)

### P3-T004: Add All-Stocks Fetching Logic
- [x] P3-T004 [US1] Add logic to fetch all active stocks when stock_symbols is empty in app/routes/custom_calculation.py

**Implementation**:
- Check if stock_symbols is empty or None
- If empty: call StockDataService.get_all_active_stocks()
- Assign result to stock_symbols variable
- Handle case when no active stocks found

**Code Pattern** (from quickstart.md):
```python
if not stock_symbols or len(stock_symbols) == 0:
    # Fetch all active stocks
    from app.services.stock_data_service import StockDataService
    service = StockDataService()
    all_stocks = service.get_all_active_stocks()
    stock_symbols = all_stocks
    
    if not stock_symbols:
        return create_error_response(404, "未找到股票", "数据库中没有活跃股票")
```

### P3-T005: Add Execution Summary to Response
- [x] P3-T005 [US1] Add execution summary (total, successful, failed counts) to response in app/routes/custom_calculation.py

**Implementation**:
- Track successful and failed executions
- Add summary object to response when processing multiple stocks
- Include summary in response.data when stock count > 1

**Response Format** (from quickstart.md):
```python
response_data = {"results": results}
if len(results) > 1:
    response_data["summary"] = {
        "total": len(results),
        "successful": successful,
        "failed": failed
    }
```

## Phase 4: Testing & Validation

### P4-T006: Test Empty Array Mode
- [ ] P4-T006 [US1] Test API with empty stock_symbols array returns all active stocks
- [ ] P4-T007 [US1] Verify execution summary is returned correctly
- [ ] P4-T008 [US1] Test with large number of stocks (500+)

**Commands**:
```bash
# Test with empty array
curl -X POST http://localhost:8000/api/custom-calculations/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "result = row[\"close_price\"] * 1.1", "stock_symbols": [], "column_name": "计算列"}'
```

### P4-T009: Test Backward Compatibility
- [ ] P4-T009 Verify specific symbols still work correctly
- [ ] P4-T010 Test API with specific stock_symbols array works as before

**Commands**:
```bash
# Test backward compatibility
curl -X POST http://localhost:8000/api/custom-calculations/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "result = row[\"close_price\"] * 1.1", "stock_symbols": ["SH.600519", "SZ.000001"], "column_name": "计算列"}'
```

### P4-T011: Error Handling Tests
- [ ] P4-T011 Test API handles missing stock data gracefully for all-stocks mode
- [ ] P4-T012 Test API returns appropriate error when no active stocks found
- [ ] P4-T013 Verify partial failures don't stop entire execution

### P4-T014: Performance Testing
- [ ] P4-T014 Test execution time for all stocks (< 60 seconds for 1000 stocks)
- [ ] P4-T015 Verify API response time is acceptable

## Task Summary

### Task Count by Phase
- Phase 1: 1 task
- Phase 2: 1 task
- Phase 3: 3 tasks
- Phase 4: 10 tasks

**Total: 15 tasks**

### Task Count by User Story
- User Story 1 (All Stocks Mode): 15 tasks

## Parallel Execution Opportunities

### Can Execute in Parallel (within Phase 4)
- T006-T008 can be done together (empty array tests)
- T009-T010 can be done together (backward compatibility tests)
- T011-T013 can be done together (error handling tests)

### Sequential Dependencies
- T001 must complete before T002 (need to be on main branch)
- T002 must complete before T003-T005 (need service method before using it)
- T003-T005 must complete before T006-T015 (implementation before testing)
- All implementation must complete before T006-T015 (testing phase)

## Files Modified

1. `app/services/stock_data_service.py` (ENHANCED - add get_all_active_stocks method)
2. `app/routes/custom_calculation.py` (MODIFIED - handle empty stock_symbols array)

**No new endpoints created**: Only modification to existing endpoint

## Implementation Checklist

### Code Changes
- [x] Service method added to fetch all active stocks
- [x] API validation modified to allow empty array
- [x] All-stocks fetching logic implemented
- [x] Execution summary added to response

### Testing
- [ ] Empty array mode tested
- [ ] Backward compatibility verified
- [ ] Error handling validated
- [ ] Performance tested

### Documentation
- [ ] Code comments added
- [ ] API behavior documented
- [ ] Usage examples provided

## Next Steps After Implementation

1. **Commit Changes**: Per constitution principle III
2. **Push to Main**: Per constitution principle I
3. **Frontend Integration**: Frontend can now pass empty array for all stocks
4. **User Documentation**: Provide API usage guide for all-stocks mode

## References

- [spec.md](./spec.md) - Full feature specification
- [plan.md](./plan.md) - Implementation plan
- [research.md](./research.md) - Technical research and decisions
- [data-model.md](./data-model.md) - Data model details
- [quickstart.md](./quickstart.md) - Implementation guide
- [contracts/api-contracts.json](./contracts/api-contracts.json) - API contract
- [.specify/memory/constitution.md](../../../.specify/memory/constitution.md) - Development principles

