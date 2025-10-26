# Feature Specification: Debug 400 Error with Empty Stock Symbols

**Feature Branch**: `008-debug-400-error`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "依然返回400参数错误，传参stock_symbols为空数组"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Debug 400 Error with Empty Stock Symbols (Priority: P1)

When user calls the custom calculation API with empty `stock_symbols: []` array, the API returns 400 error saying "参数错误" (parameter error). The system should accept empty stock_symbols array and apply the script to all active stocks, or provide a clear error message explaining what's wrong.

**Why this priority**: Users cannot use the all-stocks mode feature we just implemented. This blocks the main functionality.

**Independent Test**: API accepts empty stock_symbols array and successfully executes script for all active stocks, OR returns specific error message indicating what parameter is missing or invalid.

**Acceptance Scenarios**:

1. **Given** user calls API with empty stock_symbols array, **When** API receives request, **Then** API should either execute successfully or return a clear error explaining what's wrong (not generic "参数错误")
2. **Given** user provides valid script and column_name, **When** API receives request, **Then** API should process the request without 400 error
3. **Given** user provides invalid syntax or missing required parameters, **When** API receives request, **Then** API should return specific error message for the failing parameter

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST accept empty stock_symbols array without returning 400 error
- **FR-002**: API MUST return specific error messages indicating which parameter is missing or invalid, not generic "参数错误"
- **FR-003**: API MUST validate each parameter individually and report specific validation failures
- **FR-004**: API MUST distinguish between different error types (missing parameter, invalid type, syntax error, etc.)
- **FR-005**: Error messages MUST guide users to fix the issue with clear descriptions

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API accepts empty stock_symbols array and executes successfully
- **SC-002**: Error messages are specific and actionable (users can fix the issue based on error message)
- **SC-003**: No generic "参数错误" responses - all errors have specific causes
- **SC-004**: Users can determine which parameter caused the error from error message alone

## Assumptions

- 400 error is likely caused by script syntax validation failing
- Need to add better error logging to identify exact failure point
- User's script uses `get_history()` and `math` module which should be available in sandbox
- Error might be in validation logic or script execution
