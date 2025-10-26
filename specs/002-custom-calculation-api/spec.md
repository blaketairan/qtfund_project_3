# Feature Specification: Custom Calculation API

**Feature Branch**: `002-custom-calculation-api`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "实现后端Python脚本执行API，支持股票量化分析仪表盘的自定义列计算功能"

## Clarifications

### Session 2025-01-27

- Q: Python script execution security - How to sandbox user scripts? → A: Use restrictedpython library with RestrictedPython for safe execution
- Q: Script execution location - Where to execute? → A: Backend service (main Flask app, separate worker process for isolation)
- Q: Script input data - What data should be available to scripts? → A: Stock row data (close_price, volume, turnover, etc.) passed as Python dict
- Q: Error handling - How to handle script errors? → A: Catch all exceptions, return structured error response with line numbers
- Q: Performance - Concurrent execution? → A: Single-threaded execution (Flask context), batch processing for multiple stocks

## User Scenarios & Testing

### User Story 1 - Execute Custom Python Scripts (Priority: P1)

Users submit Python scripts via frontend, backend executes them safely and returns calculated results.

**Why this priority**: This is the core functionality enabling custom quantitative indicators.

**Independent Test**: Send POST request with Python script and stock symbols, receive calculated values.

**Acceptance Scenarios**:

1. **Given** a valid Python script and stock symbols, **When** user submits via API, **Then** backend returns calculated values for each stock
2. **Given** a Python script with syntax errors, **When** user submits via API, **Then** backend returns 400 error with line number
3. **Given** a Python script that raises an exception, **When** user submits via API, **Then** backend returns 400 error with exception message
4. **Given** multiple stocks in one request, **When** script executes, **Then** backend returns results for all stocks

---

### User Story 2 - Sandbox Security (Priority: P1)

All user Python scripts execute in restricted environment preventing unauthorized access.

**Why this priority**: Security is critical to prevent code injection and system access.

**Independent Test**: Attempt to execute malicious Python code (file access, imports, system calls), verify blocked.

**Acceptance Scenarios**:

1. **Given** a script with `import os`, **When** user submits via API, **Then** import is blocked by restrictedpython
2. **Given** a script with `open('file.txt')`, **When** user submits via API, **Then** file access is blocked
3. **Given** a script with `__import__('sys')`, **When** user submits via API, **Then** import is blocked
4. **Given** a script with only safe operations (math, string ops), **When** user submits via API, **Then** script executes successfully

---

### User Story 3 - Script Management (Priority: P1)

Users can save, retrieve, update, and delete Python scripts for reuse without re-typing.

**Why this priority**: Users need to reuse calculation formulas - without script management they must re-enter scripts repeatedly, which is inefficient and error-prone.

**Independent Test**: Users can save a script with a name, retrieve it by name, update it, and delete it. This can be tested independently by calling CRUD endpoints.

**Acceptance Scenarios**:

1. **Given** user submits a valid Python script with a name via POST, **When** script is saved, **Then** system stores script and returns success with script ID
2. **Given** scripts exist for user, **When** user requests GET /api/custom-calculations/scripts, **Then** system returns list of all saved scripts with names and timestamps
3. **Given** saved script with ID, **When** user requests GET /api/custom-calculations/scripts/{id}, **Then** system returns complete script details
4. **Given** saved script exists, **When** user updates script via PUT, **Then** system updates script and preserves creation timestamp
5. **Given** saved script exists, **When** user deletes script via DELETE, **Then** system removes script and confirms deletion
6. **Given** script is saved, **When** user executes using script_id instead of script code, **Then** system loads and executes saved script

---

### User Story 4 - Batch Processing (Priority: P2)

Support executing scripts against multiple stocks in single API call.

**Why this priority**: Efficient processing for table display - calculate all values at once.

**Independent Test**: Submit script with array of 200 stock symbols, receive all calculated values.

**Acceptance Scenarios**:

1. **Given** 200 stock symbols in request, **When** script executes, **Then** results returned for all 200 stocks
2. **Given** mix of valid and invalid stocks, **When** script executes, **Then** valid stocks get results, invalid get null/error
3. **Given** empty stock array, **When** user submits, **Then** API returns 400 error

---

### Edge Cases

- What happens when script runs longer than 10 seconds?
- How does system handle division by zero in scripts?
- What happens when script returns wrong data type (not number)?
- How does system handle very large stock arrays (1000+)?
- What happens if script tries to access undefined stock fields?
- How does system handle concurrent script executions?

## Requirements

### Functional Requirements

#### Script Execution
- **FR-001**: System MUST provide POST endpoint `/api/custom-calculations/execute`
- **FR-002**: System MUST accept Python script code OR script_id in request body
- **FR-003**: System MUST accept array of stock symbols to calculate for
- **FR-004**: System MUST pass stock data (row dict) as input to Python script
- **FR-005**: System MUST execute scripts in secure sandbox (restrictedpython)
- **FR-006**: System MUST block dangerous operations (file access, imports, system calls)
- **FR-007**: System MUST catch all script exceptions and return structured errors
- **FR-008**: System MUST return calculation results for each stock symbol
- **FR-009**: System MUST timeout script execution after 10 seconds
- **FR-010**: System MUST validate Python syntax before execution
- **FR-011**: System MUST return results in JSON format matching frontend expectations

#### Script Management (CRUD)
- **FR-012**: System MUST provide POST endpoint `/api/custom-calculations/scripts` to save scripts with name and description
- **FR-013**: System MUST provide GET endpoint `/api/custom-calculations/scripts` to list all saved scripts
- **FR-014**: System MUST provide GET endpoint `/api/custom-calculations/scripts/{id}` to retrieve specific script
- **FR-015**: System MUST provide PUT endpoint `/api/custom-calculations/scripts/{id}` to update saved scripts
- **FR-016**: System MUST provide DELETE endpoint `/api/custom-calculations/scripts/{id}` to remove saved scripts
- **FR-017**: System MUST store script name, code, description, created_at, updated_at timestamps
- **FR-018**: System MUST validate script name is unique per user (or allow duplicates if specified differently)

### Non-Functional Requirements

- **NFR-001**: Script execution MUST complete within 10 seconds per request
- **NFR-002**: System MUST handle up to 200 concurrent requests
- **NFR-003**: Sandbox MUST prevent all dangerous operations (files, network, system)
- **NFR-004**: Error responses MUST include line numbers for syntax errors
- **NFR-005**: Script environment MUST only expose safe built-ins (dict, list, str, int, float, math)
- **NFR-006**: System MUST log all script executions for debugging

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can submit Python scripts and receive results within 10 seconds
- **SC-002**: Malicious scripts are blocked with 100% success rate
- **SC-003**: Script syntax errors return detailed error messages with line numbers
- **SC-004**: Batch processing handles 200 stocks without timeout
- **SC-005**: All exceptions caught and returned as structured errors (no 500 crashes)
- **SC-006**: System handles 1000 requests/hour without degradation

### Key Entities

- **CustomCalculationRequest**: POST request body with script (or script_id), column_name, stock_symbols
- **CustomCalculationResult**: Response with calculated values per stock, or error details
- **SandboxEnvironment**: Restricted Python execution environment with safe built-ins
- **StockRowData**: Python dict passed to scripts containing stock price/volume data
- **SavedScript**: Database entity storing script metadata (id, name, description, code, created_at, updated_at, user_id if multi-user)

