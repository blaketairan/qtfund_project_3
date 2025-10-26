# Feature Specification: Dynamic Script Columns in List Query

**Feature Branch**: `005-dynamic-column-scripts`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "现在通过脚本增加列的逻辑比较奇怪，增加列之后，上传脚本的这个接口在对全部股票进行计算，这不是需求设计的初衷。我期望的是上传一个脚本增加一列之后，后续列表查询的时候能增加一列返回给前端展示，计算也是在查询列表时进行(list接口一并返回结果），并且计算范围也局限在列表将要返回的股票范围内（例如limit100，或者过滤了某些交易所的股票，则范围只在其中）。"

> **Note**: This specification MUST be placed in the target project's `specs/005-dynamic-column-scripts/` directory (e.g., `qtfund_project_3/specs/`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accept Script IDs in List Query (Priority: P1)

The stock list endpoint accepts a parameter specifying which scripts to calculate, and returns those calculated values as additional fields in each stock record.

**Why this priority**: This enables dynamic column calculation based on user's current view rather than pre-calculating everything.

**Independent Test**: When frontend calls `/stock-price/list` with `script_ids=[1,2]` parameter, the response includes calculated values for scripts 1 and 2 for each returned stock.

**Acceptance Scenarios**:

1. **Given** a valid request with script_ids parameter, **When** API processes the list query, **Then** it executes the specified scripts for each stock in the result set
2. **Given** script_ids parameter is empty or not provided, **When** API processes the list query, **Then** it returns stock data without script calculations
3. **Given** a request with limit=100 and script_ids=[1], **When** API returns results, **Then** only those 100 stocks have script 1 results, not all stocks in the database
4. **Given** a request with market_code='SH' and script_ids=[1,2], **When** API returns results, **Then** only Shanghai stocks have script 1 and 2 calculations

---

### User Story 2 - Calculate Scripts Only for Query Result Set (Priority: P1)

Script calculations are scoped to the stocks that will be returned in the current query, not all stocks in the database.

**Why this priority**: This ensures efficient calculation and matches user expectation - they only see calculations for the stocks they're viewing.

**Independent Test**: When querying with limit=50, the API calculates scripts only for those 50 stocks, not all stocks in the database.

**Acceptance Scenarios**:

1. **Given** a request with limit=50 and script_ids=[1], **When** the API executes scripts, **Then** it calculates for exactly 50 stocks that match the query
2. **Given** a request with market_code='SZ' and script_ids=[1], **When** the API executes scripts, **Then** it calculates only for Shenzhen stocks matching the query
3. **Given** a request with offset=100 and limit=50, **When** the API executes scripts, **Then** it calculates for stocks 100-150 (the paginated subset), not the entire dataset
4. **Given** filters reduce result set to 20 stocks, **When** the API executes scripts, **Then** it calculates for exactly those 20 stocks

---

### User Story 3 - Return Script Results in List Response (Priority: P1)

The list endpoint response includes calculated script results as additional fields in each stock record.

**Why this priority**: Frontend needs script results in the same response as stock data for efficient rendering.

**Independent Test**: When querying with script_ids=[1,2], the response includes calculated values from scripts 1 and 2 for each stock in the result.

**Acceptance Scenarios**:

1. **Given** stock query returns 100 stocks with script_ids=[1], **When** users view the response, **Then** each stock record includes calculated result from script 1
2. **Given** script execution fails for a specific stock, **When** users view the response, **Then** that stock's script result field is null or contains error message
3. **Given** a request with script_ids=[1,2,3], **When** users view the response, **Then** each stock includes calculated results for all three scripts
4. **Given** a script calculation returns a value, **When** users view the response, **Then** the value is properly formatted and included in the response

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST accept optional `script_ids` parameter in `/stock-price/list` endpoint (array of integers)
- **FR-002**: API MUST execute specified scripts ONLY for stocks in the current query result set
- **FR-003**: API MUST respect all existing query filters (limit, offset, market_code) when scoping script calculations
- **FR-004**: API MUST return calculated script results as additional fields in each stock record
- **FR-005**: API MUST handle script execution errors gracefully (return null or error message for that stock/script)
- **FR-006**: API MUST execute scripts in the same database transaction as the stock query for data consistency
- **FR-007**: API MUST support batch script execution
- **FR-008**: API MUST validate that provided script_ids exist in the database
- **FR-009**: API MUST support multiple scripts being calculated per query
- **FR-010**: API MUST ensure script calculations use the latest stock data from the query result

### Key Entities *(include if feature involves data)*

- **Script Configuration**: Saved scripts from the custom_scripts table (id, name, code)
- **Query Result Set**: Stocks returned by the list query after applying filters and pagination
- **Script Execution Result**: Calculated value from running a script on a specific stock's data
- **Stock Record with Scripts**: Extended stock record containing base fields plus script calculation results

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API executes scripts only for stocks in the query result set (not all stocks in database)
- **SC-002**: Script calculations respect limit parameter (e.g., calculate for 100 stocks when limit=100)
- **SC-003**: Script calculations respect market_code filter (only filtered stocks are calculated)
- **SC-004**: API successfully executes multiple scripts in a single query
- **SC-005**: Script execution errors don't prevent the list query from returning stock data
- **SC-006**: Calculated script results are accurate
- **SC-007**: API validates script_ids and returns error for non-existent IDs

