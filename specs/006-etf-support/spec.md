# Feature Specification: ETF Support in Data Query API

**Feature Branch**: `006-etf-support`  
**Created**: 2025-01-27  
**Status**: ✅ Completed  
**Implemented**: 2025-10-27  
**Input**: User description: "需要在查询API中支持ETF筛选功能，并确保脚本计算功能适用于ETF数据"

> **Note**: This specification MUST be placed in the target project's `specs/006-etf-support/` directory (e.g., `qtfund_project_3/specs/`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter Stocks by ETF/Stock Type (Priority: P1)

Users can query the stock list API and filter results to show only ETFs, only stocks, or both.

**Why this priority**: Users need to distinguish between stocks and ETFs in the dashboard - this is a fundamental filtering capability.

**Independent Test**: Users can call the list API with ETF filter parameter and receive only ETFs (or only stocks, or both).

**Acceptance Scenarios**:

1. **Given** users want to view only ETFs, **When** they call the list API with is_etf=true filter, **Then** response contains only ETFs
2. **Given** users want to view only stocks (not ETFs), **When** they call the list API with is_etf=false filter, **Then** response contains only non-ETF stocks
3. **Given** users want to view both stocks and ETFs, **When** they call the list API without is_etf filter, **Then** response contains both types
4. **Given** users combine ETF filter with market_code filter, **When** they query, **Then** response respects both filters (e.g., Shanghai ETFs only)

---

### User Story 2 - ETF Support in Custom Script Calculations (Priority: P1)

Custom script execution works for ETF data the same way it works for stock data.

**Why this priority**: Users may want to apply quantitative calculations to ETFs just like they do for stocks.

**Independent Test**: Users can provide script IDs in list query and receive calculated results for ETFs in addition to stocks.

**Acceptance Scenarios**:

1. **Given** users query ETFs with script_ids parameter, **When** API processes the request, **Then** ETF records include script calculation results
2. **Given** script execution context includes ETF price data, **When** script runs, **Then** it can access ETF fields (close_price, volume, etc.) just like stock fields
3. **Given** users apply custom scripts to ETF results, **When** they receive response, **Then** calculated columns appear for ETFs with appropriate values
4. **Given** ETF calculation fails for a specific ETF, **When** users view results, **Then** that ETF shows null or error in script_results without breaking the query

---

### User Story 3 - ETF Metadata in Query Results (Priority: P2)

Query results include ETF marker information so frontend can display and filter appropriately.

**Why this priority**: Frontend needs to know whether each record is an ETF or stock for proper display and sorting.

**Independent Test**: API response includes an ETF marker field for each instrument record.

**Acceptance Scenarios**:

1. **Given** users query the stock list, **When** they receive results, **Then** each record includes an ETF indicator field (true/false or type enum)
2. **Given** results include both stocks and ETFs, **When** frontend displays them, **Then** it can distinguish between them using the marker
3. **Given** users sort by ETF indicator, **When** they view results, **Then** ETFs and stocks can be grouped or separated

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST support `is_etf` query parameter in `/stock-price/list` endpoint (boolean or string "true"/"false")
- **FR-002**: API MUST filter results based on `is_etf` parameter when provided
- **FR-003**: API MUST return ETF marker field in each instrument record in the response
- **FR-004**: API MUST support combining `is_etf` filter with existing filters (market_code, limit, offset)
- **FR-005**: API MUST execute custom scripts on ETF data with the same execution context as stocks
- **FR-006**: API MUST ensure ETF price data fields match stock price fields for script compatibility
- **FR-007**: API MUST handle ETF data in script calculations without errors or exceptions specific to ETFs
- **FR-008**: API MUST return ETF script results in the same `script_results` object format as stocks
- **FR-009**: API MUST support querying ETFs when no is_etf filter is provided (return all types)

### Key Entities *(include if feature involves data)*

- **ETF Filter**: Query parameter that filters results by instrument type (ETF vs. stock)
- **ETF Marker in Response**: Field in each record indicating whether it's an ETF
- **ETF Script Execution**: Running custom scripts on ETF price data with same context as stocks
- **Combined Filters**: Using multiple filters together (is_etf + market_code + pagination)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API successfully filters results to show only ETFs when is_etf=true parameter is provided
- **SC-002**: API successfully filters results to show only stocks when is_etf=false parameter is provided
- **SC-003**: API successfully returns both stocks and ETFs when is_etf parameter is not provided
- **SC-004**: ETF records include ETF marker field in query responses
- **SC-005**: Custom scripts execute successfully on ETF data without format or context errors
- **SC-006**: Script calculation results appear for ETFs in the same format as stocks
- **SC-007**: Combining is_etf filter with market_code filter returns correct subset of results
- **SC-008**: Query performance for ETFs matches performance for stocks

