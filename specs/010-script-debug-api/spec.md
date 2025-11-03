# Feature Specification: Script Debug API

**Feature Branch**: `010-script-debug-api`  
**Created**: 2025-11-03  
**Status**: Draft  
**Input**: User description: "提供一个接口或者别的调试方式，能够让我写好脚本之后指定单只股票代码去执行调试，并尽可能多打印便于调试的日志"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Debug Script with Single Stock (Priority: P1)

Users can test their custom calculation scripts against a specific stock symbol before deploying to production, receiving detailed execution logs and intermediate calculation results. Users can provide either script code directly or reference an existing script ID.

**Why this priority**: Script development requires iterative testing - users need fast feedback on script correctness without querying entire datasets.

**Independent Test**: Users can call debug API with script code/ID and stock symbol, receiving execution result and detailed logs.

**Acceptance Scenarios**:

1. **Given** user writes a new calculation script, **When** they call debug API with script code and stock symbol "SH.600519", **Then** API returns calculation result and detailed execution logs
2. **Given** user has uploaded script with ID=5, **When** they call debug API with script_id=5 and stock symbol "SH.600519", **Then** API loads the script and executes it with detailed logs
3. **Given** script contains syntax errors, **When** debug API executes, **Then** response includes specific syntax error messages with line numbers
4. **Given** script runtime fails (e.g., division by zero), **When** debug API executes, **Then** response includes runtime error with traceback and variable values
5. **Given** script accesses historical data via get_history(), **When** debug API executes, **Then** logs show how many history records were retrieved and their date range

---

### User Story 2 - View Detailed Execution Logs (Priority: P1)

Debug API returns comprehensive logs showing script execution steps, variable values, function calls, and intermediate results.

**Why this priority**: Debugging requires visibility into script execution flow - users need to see what their script is actually doing.

**Independent Test**: Debug response includes execution logs with variable values at each step.

**Acceptance Scenarios**:

1. **Given** script calculates momentum score, **When** debug API executes, **Then** logs show: data retrieval count, price values, regression coefficients, R² value, final score
2. **Given** script uses get_history() function, **When** execution completes, **Then** logs show number of records returned and date range
3. **Given** script has conditional logic, **When** debug API runs, **Then** logs show which branches executed
4. **Given** script execution takes time, **When** debug completes, **Then** logs include execution duration in milliseconds

---

### User Story 3 - Test with Mock or Real Stock Data (Priority: P2)

Users can choose to test scripts with real stock data from database or provide mock data for unit testing.

**Why this priority**: Some testing scenarios require controlled test data rather than real market data.

**Independent Test**: Debug API accepts optional mock data and uses it instead of querying database.

**Acceptance Scenarios**:

1. **Given** user provides mock row data, **When** debug API executes script, **Then** script receives mock data instead of database query
2. **Given** user doesn't provide mock data, **When** debug API runs, **Then** real stock data is queried from database
3. **Given** mock data has specific values, **When** script accesses row fields, **Then** it receives the mock values
4. **Given** user wants to test edge cases (null prices, zero volume), **When** they provide mock data, **Then** script can be tested with these scenarios

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST provide debug endpoint accepting either script code OR script ID as input
- **FR-001a**: API MUST accept stock symbol parameter to identify which stock to test
- **FR-002**: API MUST execute script against specified stock symbol and return calculation result
- **FR-003**: API MUST capture and return detailed execution logs including variable values and function calls
- **FR-004**: API MUST return syntax errors with line numbers when script compilation fails
- **FR-005**: API MUST return runtime errors with full traceback when script execution fails
- **FR-006**: API MUST log all get_history() calls with parameters and return values
- **FR-007**: API MUST include execution duration in response
- **FR-008**: API MUST support optional mock data parameter for testing without database queries
- **FR-009**: API MUST limit debug execution to single stock (no batch processing)
- **FR-010**: API MUST apply same security sandbox as production script execution

### Key Entities

- **Debug Request**: (Script code OR script ID) + stock symbol + optional mock data
- **Script Reference**: Existing uploaded script identified by ID
- **Debug Response**: Execution result + detailed logs + errors + duration
- **Execution Logs**: Step-by-step record of script execution with variable values
- **Mock Data**: Optional test data replacing real database query

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can debug scripts in under 5 seconds per test iteration
- **SC-002**: Debug logs include sufficient detail to identify calculation errors
- **SC-003**: Syntax errors provide line numbers accurate to within 1 line
- **SC-004**: Runtime errors include variable values at point of failure
- **SC-005**: Users can test scripts without affecting production data or performance
- **SC-006**: Debug API response includes all intermediate calculation values
- **SC-007**: Execution duration measurement accurate to milliseconds
- **SC-008**: Mock data testing works for 100% of script types

## Assumptions

1. Debug API is for development/testing only, not production use
2. Debug endpoint has no authentication requirement (same as other endpoints)
3. Single-stock execution is sufficient for debugging purposes
4. Detailed logs may contain sensitive data (stock prices) - no PII concerns
5. Debug requests don't need rate limiting (development use)
6. Execution timeout same as production (10 seconds)

## Out of Scope

- Batch debugging multiple stocks simultaneously
- Persistent debug session storage
- Interactive debugger with breakpoints
- Script performance profiling
- Comparison testing between script versions
- Automated test case generation

## Dependencies

- Existing sandbox executor with logging capabilities
- Stock data query service for real data retrieval
- Custom script validation logic
