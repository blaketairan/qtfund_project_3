# Feature Specification: Support All-Stocks Mode for Custom Calculations

**Feature Branch**: `007-support-all-stocks-mode`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "这里为什么需要stock_symbols？难道不是脚本对表格中每只股票都生效吗？"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Apply Script to All Stocks (Priority: P1)

Users want to apply custom calculation scripts to all stocks in the table without specifying individual stock symbols. Instead of requiring users to provide a `stock_symbols` array, the system should support applying scripts to all active stocks automatically.

**Why this priority**: Users writing custom calculations typically want to analyze the entire stock universe, not just specific stocks. Requiring stock_symbols array creates unnecessary friction and doesn't match user workflow.

**Independent Test**: User can call the API with empty `stock_symbols` array or a special "all_stocks" flag and the system applies the script to all active stocks, returning results for every stock in the table.

**Acceptance Scenarios**:

1. **Given** a user wants to calculate momentum score for all stocks, **When** they call the API with `stock_symbols: []`, **Then** the system executes the script for all active stocks and returns results
2. **Given** a user provides specific stock symbols, **When** they call the API, **Then** the system executes only for those stocks (backward compatibility)
3. **Given** a user wants to test script syntax, **When** they call API with empty stock_symbols, **Then** the system validates syntax and returns success without execution
4. **Given** a user wants to apply to filtered stocks, **When** they provide filter criteria, **Then** the system applies script to matching stocks

### Edge Cases

- What if there are 10,000 active stocks? Should API have pagination?
- How to handle stocks with missing data during all-stocks execution?
- What if execution takes too long with all stocks?
- Should API support partial execution with checkpoint/resume?
- How to handle rate limiting or timeout with large stock universes?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST support empty `stock_symbols: []` array to indicate "apply to all active stocks"
- **FR-002**: API MUST maintain backward compatibility when stock_symbols array contains specific symbols
- **FR-003**: API MUST fetch all active stocks from database when stock_symbols is empty
- **FR-004**: API SHOULD support pagination or batching when executing for all stocks to prevent timeout
- **FR-005**: API MUST return execution status indicating total stocks processed, successful, and failed
- **FR-006**: API MUST handle missing data gracefully for individual stocks without stopping entire execution
- **FR-007**: API MAY support progressive results (stream results as available) for all-stocks mode
- **FR-008**: API MUST provide clear error messages if all-stocks execution exceeds time limits
- **FR-009**: When executing for all stocks, API MUST use same filtering/ordering as stock table display
- **FR-010**: API MUST track execution progress for long-running all-stocks operations

### Key Entities *(include if feature involves data)*

- **All Active Stocks**: Complete list of stocks marked as active in database (is_active='Y')
- **Execution Batch**: Subset of stocks processed together to prevent timeout
- **Progressive Results**: Results streamed back incrementally as calculations complete
- **Execution Status**: Summary of completed vs failed calculations across all stocks

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can apply custom calculations to all stocks without specifying individual symbols
- **SC-002**: API executes scripts for 1000+ stocks without timeout (within acceptable limits)
- **SC-003**: API maintains backward compatibility with existing stock_symbols parameter usage
- **SC-004**: API returns clear execution status indicating how many stocks were processed
- **SC-005**: API handles missing data for individual stocks without failing entire execution
- **SC-006**: API provides progress feedback during long-running all-stocks operations
- **SC-007**: API execution completes for all stocks within reasonable time (< 60 seconds for 1000 stocks)
- **SC-008**: Users can see which stocks succeeded and which failed with clear error messages

## Assumptions

- Users primarily want to apply calculations to entire stock universe
- Current stock filtering (active, market code, etc.) applies to "all stocks" mode
- Database can efficiently query all active stocks
- Script execution is fast enough (< 2 seconds per stock) to handle large batches
- Progressive results are acceptable for long-running operations
- Most users will use all-stocks mode rather than specific symbol mode
- Backward compatibility is critical to avoid breaking existing frontend
