# Feature Specification: Stock Data Query Service Specifications

**Feature Branch**: `001-spec-api`  
**Created**: 2025-10-24  
**Status**: Draft  
**Input**: User description: "整理当前应用逻辑到spec，比较重要的有API、数据结构、数据库数据结构"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Stock Price Data (Priority: P1)

Users can query historical stock price data from TimescaleDB using a stock symbol and optional date range.

**Why this priority**: This is the core functionality of the service - retrieving historical stock data. Without this, the service cannot fulfill its primary purpose.

**Independent Test**: Users can query price data by sending a GET request with a stock symbol and receive a list of historical price records. This can be tested independently by calling the API endpoint with a valid symbol like "SH.600519".

**Acceptance Scenarios**:

1. **Given** stock data exists in the database for "SH.600519", **When** a user requests data for this symbol with no date filters, **Then** the system returns the most recent 100 records ordered by date descending
2. **Given** stock data exists for "SH.600519" with date range "2024-01-01" to "2024-12-31", **When** a user requests data with both start and end dates, **Then** the system returns only records within that date range
3. **Given** a request with limit parameter set to 50, **When** valid stock data exists, **Then** the system returns exactly 50 records
4. **Given** an invalid stock symbol format (e.g., "600519" without market prefix), **When** a user submits this query, **Then** the system returns a 400 error with a clear message about the correct format

---

### User Story 2 - List Available Stocks (Priority: P1)

Users can retrieve a list of available stocks with filtering options by market, active status, and pagination.

**Why this priority**: Users need to discover what stocks are available before querying specific price data. This is essential for building user interfaces and enabling data exploration.

**Independent Test**: Users can request the stock list with default parameters and receive a paginated response. This can be tested independently by calling the list endpoint without any filters.

**Acceptance Scenarios**:

1. **Given** thousands of stocks exist in the database, **When** a user requests the stock list without parameters, **Then** the system returns the first 100 active stocks with pagination metadata
2. **Given** stocks from SH (Shanghai), SZ (Shenzhen), and BJ (Beijing) markets exist, **When** a user filters by market_code "SH", **Then** the system returns only Shanghai market stocks
3. **Given** a request with limit=500 and offset=100, **When** at least 600 stocks exist, **Then** the system returns records 100-599 (500 total)
4. **Given** a request with limit exceeding 10000, **When** a user submits this query, **Then** the system returns a 400 error preventing excessive data requests

---

### User Story 3 - Get Stock Basic Information (Priority: P2)

Users can retrieve detailed information about a specific stock including name, market, industry, and sync status.

**Why this priority**: After discovering available stocks, users often need detailed information about specific stocks before querying price data.

**Independent Test**: Users can request stock information by symbol and receive a detailed record. This can be tested independently by calling the info endpoint with a valid symbol.

**Acceptance Scenarios**:

1. **Given** stock information exists for "SH.600519" (Kweichow Moutai), **When** a user requests info for this symbol, **Then** the system returns complete stock details including name, market, and industry
2. **Given** a stock symbol that doesn't exist in the database, **When** a user requests info for it, **Then** the system returns a 404 error

---

### User Story 4 - Query Local Stock Information (Priority: P2)

Users can search stock information from local JSON files without requiring database connection, supporting quick lookup and search by keyword.

**Why this priority**: Provides alternative data source and enables fast search capabilities without database overhead. Useful for simple queries and data exploration.

**Independent Test**: Users can search for stocks by name or exchange in local JSON files. This can be tested independently even if the database is offline.

**Acceptance Scenarios**:

1. **Given** JSON files contain stock data for multiple exchanges, **When** a user searches without filters, **Then** the system returns active stocks from all exchanges (up to limit)
2. **Given** a keyword "Moutai" exists in stock names, **When** a user searches with this keyword, **Then** the system returns all matching stocks
3. **Given** exchange code "XSHG" is specified, **When** a user searches, **Then** the system returns only Shanghai Stock Exchange stocks

---

### User Story 5 - Monitor Service Health (Priority: P3)

System administrators can check service health and database connectivity status.

**Why this priority**: Ensures system reliability and enables proactive monitoring. Essential for production deployments.

**Independent Test**: Health check endpoint can be called independently to verify database connectivity. This can be tested anytime without affecting other functionality.

**Acceptance Scenarios**:

1. **Given** the service is running and database is connected, **When** a health check is requested, **Then** the system returns "healthy" status with connection confirmation
2. **Given** the database is unreachable, **When** a health check is requested, **Then** the system returns "unhealthy" status with error details

---

### Edge Cases

- What happens when the database connection is temporarily lost during a query?
- How does the system handle invalid date ranges (start_date > end_date)?
- What happens when querying for a symbol that has no historical data?
- How does the system handle empty results when filters match no records?
- What happens when pagination offset exceeds total available records?
- How does the system handle concurrent requests for the same data?
- What happens when the JSON data files are missing or corrupted?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow querying historical stock price data by symbol with optional date range filtering
- **FR-002**: System MUST validate stock symbol format (market.code) before querying
- **FR-003**: System MUST support pagination with configurable limit (1-10000) and offset parameters
- **FR-004**: System MUST return query results ordered by trade date descending (most recent first)
- **FR-005**: System MUST validate date formats (YYYY-MM-DD) and date range logic
- **FR-006**: System MUST support filtering stock lists by market code (SH/SZ/BJ)
- **FR-007**: System MUST support filtering stock lists by active status (Y/N)
- **FR-008**: System MUST return consistent JSON response format for all endpoints
- **FR-009**: System MUST handle and log all errors with appropriate HTTP status codes
- **FR-010**: System MUST support querying from both TimescaleDB (historical data) and local JSON files (stock info)
- **FR-011**: System MUST provide health check endpoint for monitoring system status
- **FR-012**: System MUST provide version information endpoint
- **FR-013**: System MUST enforce maximum query limit (10000 records) to prevent performance issues
- **FR-014**: System MUST include pagination metadata (total count, current count, offset) in list responses
- **FR-015**: System MUST support keyword search in local JSON stock information

### Key Entities *(include if feature involves data)*

- **Stock Daily Data**: Represents historical price data for a specific stock on a specific date. Key attributes include trade_date (primary key), symbol (primary key), prices (open, high, low, close), volume, turnover, price changes, premium rate (for funds), and market code. Related to StockInfo by symbol.

- **Stock Information**: Represents metadata about stocks. Key attributes include symbol (primary key), stock name, stock code, market code, stock type, industry, sector, list/delist dates, active status, and sync tracking information. Used to filter and identify stocks before querying price data.

- **Query Request**: Represents user query parameters. Contains symbol (required), optional date range, and limit/offset for pagination. Validated against business rules.

- **API Response**: Represents standardized response format. Contains status code, message, timestamp, data payload, and error details when applicable. Ensures consistent client interface.

- **Local Stock Data**: Represents stock information from JSON files. Contains ticker, name, exchange code, active status, and metadata. Provides alternative data source without database dependency.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can query historical stock data for any valid symbol and receive results within 2 seconds under normal load
- **SC-002**: System successfully handles 1000 concurrent requests without degradation
- **SC-003**: 95% of valid queries return complete and accurate data within expected time limits
- **SC-004**: All API endpoints provide consistent response formats with proper error handling
- **SC-005**: Pagination works correctly for datasets exceeding 100,000 records
- **SC-006**: Health check endpoint accurately reflects database connectivity status
- **SC-007**: Query results are returned in chronological order (most recent first) with proper date filtering
- **SC-008**: System rejects invalid queries (wrong format, excessive limits) with clear error messages preventing 4xx/5xx cascade

## API Specifications *(mandatory for API features)*

### Endpoint Categories

#### 1. Health & System Endpoints

- **GET /api/health**: Returns service health and database connectivity status
  - No authentication required
  - Returns: health status, timestamp, database connection state
  
- **GET /api/version**: Returns service version and feature information
  - No authentication required
  - Returns: version, framework, database, features list

- **GET /**: Returns service information and available endpoints
  - No authentication required
  - Returns: API documentation in JSON format

#### 2. Stock Price Data Endpoints

- **GET|POST /api/stock-price/query**: Query historical stock price data
  - Parameters: symbol (required), start_date (optional), end_date (optional), limit (default 100, max 10000)
  - Returns: List of price records with trade_date, prices, volume, turnovers, market_code
  - Supports GET query string or POST JSON body
  
- **GET /api/stock-price/info/{symbol}**: Get stock basic information
  - Parameters: symbol (path parameter, required)
  - Returns: Single stock info record with name, market, industry, sync status
  
- **GET /api/stock-price/list**: List available stocks with filtering
  - Parameters: market_code (optional, SH/SZ/BJ), is_active (optional, Y/N default Y), limit (default 100, max 10000), offset (default 0)
  - Returns: Paginated list with total count metadata

#### 3. Stock Information Endpoints (Local JSON)

- **GET /api/stock-info/local**: Query stock information from local JSON files
  - Parameters: exchange_code (optional, XSHG/XSHE/BJSE), keyword (optional), is_active (default true), limit (default 100, max 10000)
  - Returns: List of stock info from JSON files, supports keyword search
  
- **GET /api/stock-info/statistics**: Get statistics about stock data
  - No parameters
  - Returns: Total stocks, active/inactive counts, exchange breakdowns

### Response Format

All endpoints return JSON with standard structure:
```json
{
  "code": 200,
  "message": "success message",
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "data": { /* response payload */ }
}
```

Error responses include:
```json
{
  "code": 4xx/5xx,
  "message": "error message",
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "detail": "detailed error information",
  "error": true
}
```

### Query Parameters & Validation

- **symbol**: Format "MARKET.CODE" (e.g., "SH.600519")
  - Supported markets: SH, SZ, BJ
  - Code must be 6 digits
  
- **start_date / end_date**: Format "YYYY-MM-DD"
  - Must be valid dates
  - start_date must be <= end_date
  
- **limit**: Integer 1-10000
  - Default: 100
  - Enforced maximum to prevent performance issues
  
- **offset**: Integer >= 0
  - Default: 0
  - Used for pagination

## Data Specifications *(mandatory for data features)*

### Database Schema

#### StockDailyData Table (TimescaleDB Hypertable)

**Purpose**: Store historical stock price data as time-series data

**Primary Key**: (trade_date, symbol)

**Columns**:
- trade_date (DateTime, PK): Trading date
- symbol (String 20, PK): Stock identifier (format: MARKET.CODE)
- stock_name (String 100): Stock display name
- open_price (Decimal 10,4): Opening price
- high_price (Decimal 10,4): Highest price
- low_price (Decimal 10,4): Lowest price
- close_price (Decimal 10,4): Closing price
- volume (BigInteger): Trading volume (in hands)
- turnover (Decimal 20,2): Trading amount
- price_change (Decimal 10,4): Price change amount
- price_change_pct (Decimal 8,4): Price change percentage
- premium_rate (Decimal 8,4): Premium rate (for funds)
- market_code (String 10): Market identifier (SH/SZ/BJ)
- created_at (DateTime): Record creation time
- updated_at (DateTime): Record last update time

**Indexes**:
- idx_symbol_date: Composite index on (symbol, trade_date)
- idx_market_code: Market code index
- idx_trade_date: Trading date index
- idx_stock_name: Stock name index

**TimescaleDB Features**:
- Hypertable partitioned by trade_date with 1-month chunks
- Auto-compression after 7 days
- Data retention policy (3 years)

#### StockInfo Table

**Purpose**: Store stock metadata and classification

**Primary Key**: symbol

**Columns**:
- symbol (String 20, PK): Stock identifier
- stock_name (String 100): Stock display name
- stock_code (String 10): Code without market prefix
- market_code (String 10): Market identifier (SH/SZ)
- stock_type (String 20): Type (stock/fund/bond)
- industry (String 100): Industry classification
- sector (String 100): Sector classification
- list_date (DateTime): Listing date
- delist_date (DateTime): Delisting date
- is_active (String 1): Active status (Y/N)
- last_sync_date (DateTime): Last price sync date
- first_fetch_time (DateTime): First data fetch time
- created_at (DateTime): Record creation time
- updated_at (DateTime): Record last update time

**Indexes**:
- idx_stock_code: Stock code index
- idx_market_code_info: Market code index
- idx_stock_name_info: Stock name index
- idx_is_active: Active status index

### Data Access Patterns

**Query Patterns**:
1. Get latest N records for a symbol (most common)
2. Get records within date range for a symbol
3. List all stocks with optional filters (pagination)
4. Search stocks by name or code (local JSON)

**Performance Considerations**:
- Queries use indexed columns (symbol, trade_date)
- Results ordered by trade_date descending
- Pagination prevents full table scans
- Compression reduces storage for older data

### Local Data Structure

**Stock Lists (JSON Files)**:
- Located in constants/stock_lists/
- Files: xshg_stocks.json, xshe_stocks.json, bjse_stocks.json
- Each file contains array of stock objects
- Each object includes: ticker, name, is_active, exchange_code, country_code, currency_code, exchange_name_cn, first_fetch_time

**Loading**:
- Loaded at application startup
- Indexed by symbol and exchange_code
- Enables fast lookup without database

## Assumptions

1. Database (TimescaleDB) is already provisioned and configured
2. Stock price data is synchronized from external source by a separate service (port 7777)
3. This service only provides read access, no write operations
4. Local JSON files are pre-populated and updated externally
5. Database connection pool is sufficient for expected concurrent requests
6. Query performance scales reasonably with current indexing strategy
7. Date-based partitioning (TimescaleDB) handles growth efficiently
8. Chinese timezone (UTC+8) is used for all timestamps
9. Stock symbols follow consistent naming convention (MARKET.CODE)
10. Market codes are standardized (SH=Shanghai, SZ=Shenzhen, BJ=Beijing)

## Dependencies

- TimescaleDB extension must be installed on PostgreSQL
- PostgreSQL 12+ required
- Data must be synchronized by external service (port 7777)
- Environment variables must be configured (SECRET_KEY, database credentials)
- Python 3.9+ runtime environment
- Database connection pool available

## User Interactions

### Primary User Flow

1. User calls list endpoint to discover available stocks
2. User selects stock symbol from list
3. User queries historical price data for selected symbol
4. System validates symbol format and date parameters
5. System queries TimescaleDB with appropriate filters
6. System returns paginated results ordered by date
7. User iterates through pagination for additional data if needed

### Error Handling

- Invalid symbol format returns 400 with format specification
- Invalid date range returns 400 with validation message
- Missing stock data returns empty result array (not error)
- Database connection failures return 503 with error details
- Exceeding maximum limit returns 400 with limit information
