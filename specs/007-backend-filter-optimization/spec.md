# Feature Specification: Backend Market Filter and Unlimited Results

**Feature Branch**: `007-backend-filter-optimization`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "市场筛选改为后端执行，取消limit限制，支持返回全部数据，调整超时时间为10分钟"

> **Note**: This specification MUST be placed in the target project's `specs/007-backend-filter-optimization/` directory (e.g., `qtfund_project_3/specs/`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Return All Matching Results Without Limit (Priority: P1)

The stock list API returns all records matching the query filters without artificial pagination limits, ensuring users can see all available data.

**Why this priority**: Current limit-based approach causes data visibility issues - users can't see results outside the limit boundary when filtering.

**Independent Test**: Users can query the API and receive all stocks/ETFs matching their filters, regardless of total count.

**Acceptance Scenarios**:

1. **Given** database contains 500 Shanghai stocks, **When** users query with market_code=SH and no limit, **Then** all 500 stocks are returned
2. **Given** database contains 300 ETFs across all markets, **When** users query with is_etf=true and no limit, **Then** all 300 ETFs are returned
3. **Given** users apply multiple filters (SH market + ETFs), **When** query executes, **Then** all matching records are returned without truncation
4. **Given** database contains 1000+ total instruments, **When** users query without filters, **Then** all instruments are returned

---

### User Story 2 - Process Market Filter on Backend (Priority: P1)

Market code filtering is executed in the database query, not client-side, ensuring accurate results regardless of dataset size.

**Why this priority**: Frontend filtering fails when limit returns data from only one market - backend filtering ensures correctness.

**Independent Test**: Users can query with market_code parameter and receive only instruments from that market, even if the full dataset contains instruments from other markets.

**Acceptance Scenarios**:

1. **Given** users query with market_code=SH, **When** backend processes the request, **Then** database WHERE clause filters by market_code before returning results
2. **Given** all returned data happens to be from SZ market within the old limit, **When** users query with market_code=SH, **Then** they still receive SH market data (not empty results)
3. **Given** users switch market filter from SH to SZ, **When** backend processes both requests, **Then** each returns complete data for the respective market
4. **Given** users combine market_code with is_etf filter, **When** query executes, **Then** both filters apply in the database query (not client-side)

---

### User Story 3 - Support Long-Running Queries (Priority: P1)

API supports queries that may take several minutes to complete when returning large datasets (thousands of instruments with script calculations).

**Why this priority**: Removing limit and returning all data with script calculations may take significant time - system must handle this gracefully.

**Independent Test**: API can successfully return 1000+ instruments with script calculations without timing out.

**Acceptance Scenarios**:

1. **Given** users query all instruments with script_ids=[1,2,3], **When** calculation takes 5 minutes, **Then** request completes successfully without timeout
2. **Given** query processes 2000+ instruments, **When** execution time exceeds 2 minutes, **Then** server doesn't terminate the request
3. **Given** long-running query is in progress, **When** users wait for results, **Then** they eventually receive complete data without errors
4. **Given** request timeout is set to 10 minutes, **When** query completes in 8 minutes, **Then** response is successfully returned to client

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST remove default limit constraint from `/stock-price/list` endpoint
- **FR-002**: API MUST return all records matching query filters without artificial pagination
- **FR-003**: API MUST support optional limit parameter for backwards compatibility (if client explicitly provides it)
- **FR-004**: API MUST execute market_code filtering in database WHERE clause, not application layer
- **FR-005**: API MUST ensure market_code filter is applied before returning results
- **FR-006**: API MUST support queries returning 1000+ records without errors
- **FR-007**: API MUST configure request timeout to 10 minutes (600 seconds)
- **FR-008**: API MUST handle long-running script calculations for large datasets
- **FR-009**: API MUST maintain support for all existing filters (market_code, is_etf, is_active, script_ids)
- **FR-010**: API MUST return appropriate HTTP status while query is processing (not premature timeout)

### Key Entities *(include if feature involves data)*

- **Full Result Set**: All database records matching query filters without pagination limits
- **Database Filter**: WHERE clause conditions applied at database level before data retrieval
- **Long-Running Query**: Database + script execution that may take several minutes to complete
- **Request Timeout**: Server configuration allowing up to 10 minutes for query completion

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API successfully returns all matching records when no limit is specified (tested with 500+, 1000+, 2000+ record queries)
- **SC-002**: Market code filter returns correct data even when previous limit would have excluded it
- **SC-003**: Users can query SH market and receive only SH instruments, regardless of dataset composition
- **SC-004**: API successfully completes queries taking up to 10 minutes without timeout errors
- **SC-005**: Script calculations execute successfully on datasets of 1000+ instruments
- **SC-006**: No "empty results" issue when switching markets (each market returns its actual data)
- **SC-007**: Combining market_code + is_etf + script_ids filters works correctly with full dataset
- **SC-008**: API response time scales appropriately with dataset size (acceptable performance degradation)

