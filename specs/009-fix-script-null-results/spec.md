# Feature Specification: Fix Script Execution Null Results

**Feature Branch**: `009-fix-script-null-results`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: Bug report: "自定义脚本没有返回数据，所有行的自定义列值均为null"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Debug Script Execution Returns Null (Priority: P1)

Custom scripts are returning null for all stocks when called via the list endpoint with script_ids parameter. The system should execute scripts successfully and return calculated values, or provide clear error messages indicating why the script failed.

**Why this priority**: Users cannot use the script calculation feature. This blocks the core functionality of dynamic columns.

**Independent Test**: When calling `/api/stock-price/list?script_ids=[1]` with a valid script ID, the API returns stock data with calculated script results in the `script_results` field (not null).

**Acceptance Scenarios**:

1. **Given** a valid script ID and stock data, **When** API executes the script, **Then** it returns a calculated value (number, float, or proper error message)
2. **Given** a script that requires `get_history()` function, **When** API executes the script, **Then** the script has access to `get_history()` and can retrieve historical data
3. **Given** a script that accesses `row` context (e.g., `row['close_price']`), **When** API executes the script, **Then** the script receives the correct row data structure with expected fields
4. **Given** a script execution fails due to runtime error, **When** API handles the error, **Then** it logs detailed error information and returns null in the response

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Scripts MUST receive correct `row` context data with all expected fields (symbol, close_price, volume, etc.)
- **FR-002**: Scripts MUST have access to `get_history()` function to retrieve historical data
- **FR-003**: API MUST log detailed script execution errors for debugging
- **FR-004**: API MUST return null for failed scripts without blocking the entire response
- **FR-005**: SandboxExecutor MUST expose all required functions to scripts (get_history, math module, globals)

### Key Entities *(include if feature involves data)*

- **Script Context (row)**: Stock data object passed to scripts containing fields like symbol, close_price, volume, price_change_pct, etc.
- **Script Result**: Calculated value returned by script execution
- **Script Error**: Error information when script execution fails

## Success Criteria *(mandurable)*

### Measurable Outcomes

- **SC-001**: Scripts successfully execute and return calculated values (not null) for valid input
- **SC-002**: Scripts using `get_history()` function can retrieve historical data
- **SC-003**: Scripts accessing `row` context receive correct data structure
- **SC-004**: API logs detailed error information when script execution fails
- **SC-005**: Failed scripts return null without blocking the API response

## Investigation Tasks

### Debugging Steps

1. **Check row context data structure**:
   - Verify what fields are passed in `stock` object
   - Compare expected vs actual row structure
   - Check if fields match script expectations

2. **Check get_history() availability**:
   - Verify `get_history()` is exposed in sandbox
   - Test if function can be called from scripts
   - Check function implementation

3. **Check script execution logs**:
   - Add detailed logging to script execution
   - Log script input parameters
   - Log script output and errors

4. **Test with simple script**:
   - Create minimal script: `result = row['close_price'] * 1.1`
   - Verify basic row access works
   - Verify basic calculations work

5. **Test with momentum score script**:
   - Verify `get_history()` access works
   - Check if history data is returned correctly
   - Verify script can process historical data

## Assumptions

- Scripts expect `row` to contain fields like 'symbol', 'close_price', 'volume', etc.
- Scripts may use `get_history()` function for historical data access
- Scripts return values via `result` variable
- SandboxExecutor should expose `get_history()` and other required functions
- All scripts should have access to math module and other basic functions

