# Feature Specification: Stock Data Display on Dashboard

**Feature Branch**: `004-stock-data-display`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "前端dashboard页面目前只展示了股票列表。列表中有price、Change %、Volume等列，但没有数值，似乎后端接口没有返回数据，请增加实现。同时所有列名应使用中文。"

> **Note**: This specification MUST be placed in the target project's `specs/004-stock-data-display/` directory (e.g., `qtfund_project_3/specs/`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Return Latest Stock Prices (Priority: P1)

The API must return the latest available price for each stock in the stock list endpoint, so the frontend can display actual numerical price values.

**Why this priority**: Frontend requires price data to populate the table - without it, users see empty columns.

**Independent Test**: When frontend calls the stock list API, the response includes price data for each stock that can be displayed in the dashboard.

**Acceptance Scenarios**:

1. **Given** database has stock price data, **When** frontend calls `/stock-price/list` API, **Then** response includes `close_price` field with actual numerical values for each stock
2. **Given** a stock has price data in the most recent trading day, **When** API returns that stock, **Then** the price value is included in the response
3. **Given** a stock has no recent price data, **When** API returns that stock, **Then** the price field is null or empty string (not missing from response)

---

### User Story 2 - Return Price Change Percentage (Priority: P1)

The API must calculate and return the price change percentage for the current/latest trading day.

**Why this priority**: Frontend needs change percentage data to display in the dashboard table with color coding.

**Independent Test**: When frontend calls the API, the response includes calculated price change percentage for each stock.

**Acceptance Scenarios**:

1. **Given** database has daily price data, **When** frontend calls the API, **Then** response includes `price_change_pct` field showing percentage change (e.g., 5.23 for +5.23%)
2. **Given** a stock has increased in price, **When** API calculates change, **Then** the value is positive (e.g., 3.45)
3. **Given** a stock has decreased in price, **When** API calculates change, **Then** the value is negative (e.g., -2.18)
4. **Given** a stock's price hasn't changed, **When** API calculates change, **Then** the value is 0.00

---

### User Story 3 - Return Trading Volume (Priority: P1)

The API must return trading volume for the latest available trading day.

**Why this priority**: Frontend needs volume data to display in the dashboard, indicating market activity.

**Independent Test**: When frontend calls the API, the response includes volume data for each stock.

**Acceptance Scenarios**:

1. **Given** database has volume data for latest trading day, **When** frontend calls the API, **Then** response includes `volume` field with actual trading volume values
2. **Given** volume data is available, **When** API returns stock data, **Then** volume is included in the response
3. **Given** volume data is missing or unavailable, **When** API returns stock data, **Then** volume field is null or 0

---

### User Story 4 - Optimize Database Queries (Priority: P2)

The API must efficiently query the database to avoid performance issues when returning stock list with price data.

**Why this priority**: With hundreds of stocks, inefficient queries will cause slow response times and poor user experience.

**Independent Test**: API can return 200+ stocks with price data within acceptable time (under 2 seconds).

**Acceptance Scenarios**:

1. **Given** database contains 500+ stocks with price history, **When** frontend requests stock list, **Then** API responds within 2 seconds with all price data
2. **Given** a request for all active stocks, **When** API queries database, **Then** it uses efficient JOIN queries to get latest prices in single operation
3. **Given** frontend requests filtered stocks (by market), **When** API processes request, **Then** it applies filters efficiently without loading all stocks

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST return `close_price` field for each stock in the `/stock-price/list` endpoint
- **FR-002**: API MUST return `price_change_pct` field showing percentage change for the latest trading day
- **FR-003**: API MUST return `volume` field showing trading volume for the latest trading day
- **FR-004**: API MUST calculate price change percentage as: ((latest_price - previous_price) / previous_price) * 100
- **FR-005**: API MUST return data for the most recent available trading day when historical data exists
- **FR-006**: API MUST use efficient database queries (JOIN or subquery) to fetch latest price in single operation
- **FR-007**: API MUST return null or empty string for missing price/volume data instead of omitting the field
- **FR-008**: API MUST maintain backward compatibility with existing frontend code
- **FR-009**: API MUST support filtering by `market_code` parameter while returning price data
- **FR-010**: API MUST handle cases where stock has no price history gracefully

### Key Entities *(include if feature involves data)*

- **StockInfo**: Basic stock metadata (symbol, name, market_code)
- **StockDailyData**: Daily trading data including close_price, volume, trade_date
- **Latest Price**: The most recent close_price for each stock from StockDailyData table
- **Price Change**: Calculated percentage change compared to previous trading day
- **Volume**: Trading volume from the most recent trading day

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API returns price data for at least 90% of stocks in the list response
- **SC-002**: Price change percentage is calculated correctly (matches manual calculation)
- **SC-003**: Volume data is included for all stocks where available in database
- **SC-004**: API response time is under 2 seconds for 200+ stocks with price data
- **SC-005**: Database query execution time is under 500ms for typical requests
- **SC-006**: API handles missing price data gracefully (returns null, doesn't crash)
- **SC-007**: API maintains response format compatible with existing frontend expectations
- **SC-008**: Database queries use efficient JOINs to minimize query count and time
- **SC-009**: API supports existing filters (market_code, is_active, limit, offset) while returning price data

