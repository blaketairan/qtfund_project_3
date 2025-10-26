# Research: Support All-Stocks Mode Implementation

**Feature**: 007-support-all-stocks-mode  
**Date**: 2025-01-27  
**Status**: Complete

## Research Questions

### Q1: How to handle empty stock_symbols array?

**Decision**: Allow empty array, interpret as "all active stocks", fetch from database.

**Rationale**:
- Simplifies user experience - no need to specify symbols
- Matches user expectation that script applies to all stocks
- Can reuse existing database queries for active stocks

**Implementation**:
```python
# In app/routes/custom_calculation.py
if not stock_symbols or len(stock_symbols) == 0:
    # Fetch all active stocks
    from app.services.stock_data_service import StockDataService
    service = StockDataService()
    all_stocks = service.get_all_active_stocks()
    stock_symbols = [stock.symbol for stock in all_stocks]
```

**Alternatives considered**:
- Require special "all_stocks" flag: More explicit but adds parameter
- New endpoint `/execute-all`: Duplicates logic unnecessarily
- Frontend passes all symbols: Inefficient for large stock universes

### Q2: How to fetch all active stocks efficiently?

**Decision**: Query database for all stocks with is_active='Y', return symbol list.

**Rationale**:
- TimescaleDB efficiently handles full table scans for small-medium datasets
- Filter by is_active matches user's table display
- Simple query, no complex joins needed

**Implementation**:
```python
# In app/services/stock_data_service.py
def get_all_active_stocks(self, market_code: Optional[str] = None) -> List[str]:
    """Get all active stock symbols"""
    with db_manager.get_session() as session:
        query = session.query(StockInfo.symbol).filter(
            StockInfo.is_active == 'Y'
        )
        if market_code:
            query = query.filter(StockInfo.market_code == market_code)
        
        results = query.all()
        return [row.symbol for row in results]
```

**Performance**: Acceptable for 1000-5000 stocks. Simple query with index on is_active.

**Alternatives considered**:
- Cache stock list: Adds complexity, cache invalidation issues
- Pagination: Not needed initially, can add later if scale demands it

### Q3: How to prevent timeout with large stock universes?

**Decision**: Batch execution into smaller chunks, process sequentially with progress tracking.

**Rationale**:
- Current API processes stocks in sequence
- Batch size of 100-200 stocks prevents timeout
- Keep existing execution flow (no async needed initially)

**Implementation**:
```python
# Batch stocks into groups of 100
BATCH_SIZE = 100
for i in range(0, len(stock_symbols), BATCH_SIZE):
    batch = stock_symbols[i:i + BATCH_SIZE]
    # Process batch
    for symbol in batch:
        # Execute script
    # Log progress
```

**Thresholds**:
- < 500 stocks: Process all at once
- 500-1000 stocks: Warn user, process in batches
- > 1000 stocks: Error message suggesting filtering

**Alternatives considered**:
- Background job with async results: Adds complexity
- Paginated API calls: Changes API contract
- Streaming results: Requires WebSocket or Server-Sent Events

### Q4: How to maintain backward compatibility?

**Decision**: Check if stock_symbols is empty, fetch all stocks only then. Otherwise use provided symbols.

**Rationale**:
- No breaking changes to existing API
- Frontend doesn't need to change
- Clear behavior for both modes

**Implementation**:
```python
# Check if empty, otherwise use provided symbols
if not stock_symbols or len(stock_symbols) == 0:
    stock_symbols = fetch_all_active_stocks()
else:
    # Use provided symbols (existing behavior)
    pass
```

**Backward Compatibility**: ✅ Maintained. Existing calls with specific symbols work unchanged.

## Technology Choices

### Database Query Pattern
- **Decision**: Simple SELECT with WHERE is_active='Y'
- **Why**: Efficient, no joins needed, uses existing index
- **Performance**: < 100ms for 1000 stocks

### Execution Pattern
- **Decision**: Sequential processing in batches
- **Why**: Simple, no async overhead, clear error handling
- **Tradeoff**: Can be slower than parallel but simpler and more reliable

### Error Handling
- **Decision**: Continue on individual stock errors, aggregate at end
- **Why**: Better user experience, see which stocks succeeded/failed
- **Pattern**: Try-except per stock, collect errors in results array

## Integration Points

### Custom Calculation Endpoint
- Modify `/execute` to accept empty stock_symbols
- Fetch all stocks when array is empty
- Execute script for each stock (existing logic)
- Return aggregated results

### Stock Data Service
- Add `get_all_active_stocks()` method
- Query stock_info table for active stocks
- Support optional market_code filter
- Return list of stock symbols

### Response Format
- Same response structure as before
- Results array contains all stocks when stock_symbols is empty
- Include execution summary: total, successful, failed

## Implementation Approach Summary

1. **Modify API Validation** (`app/routes/custom_calculation.py`):
   - Remove or modify check that rejects empty stock_symbols
   - Add logic to fetch all stocks when array is empty
   - Keep existing validation for other parameters

2. **Add Service Method** (`app/services/stock_data_service.py`):
   - Implement `get_all_active_stocks()` method
   - Query for stocks with is_active='Y'
   - Support optional filtering by market_code

3. **Execution Flow**:
   - Check if stock_symbols is empty
   - If empty: fetch all active stocks, assign to stock_symbols
   - If not empty: use provided symbols (existing behavior)
   - Execute script for each symbol (existing logic)
   - Return results

4. **Testing**:
   - Test with empty array
   - Test with specific symbols (backward compatibility)
   - Test with large number of stocks (500+)
   - Test error handling for missing stocks

## Unknowns Resolved

- ✅ Empty stock_symbols handling
- ✅ All-stocks fetching from database
- ✅ Batching strategy for timeout prevention
- ✅ Backward compatibility approach
- ✅ Response format consistency
- ✅ Error handling for large universes

## References

- Existing custom calculation API implementation
- Stock data service patterns
- Database schema (stock_info.is_active field)
- Flask routing and request handling
- API backward compatibility best practices

