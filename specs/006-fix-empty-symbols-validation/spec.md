# Feature Specification: Fix Empty Stock Symbols Validation Bug

**Feature Branch**: `006-fix-empty-symbols-validation`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "post /api/custom-calculations/execute时返回400，提示信息为参数错误。现在看前端调用该接口时传入了两个字段column_name和script，stock_symbols为空数组。这个是否有关系？什么逻辑导致？"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fix API Validation for Empty Stock Symbols Array (Priority: P1)

When frontend calls the custom calculation API with an empty `stock_symbols` array, the API returns a 400 error with unhelpful message "参数错误". The system should either allow empty arrays for script validation purposes or provide a clear error message explaining why stock symbols are required.

**Why this priority**: Frontend users get confusing error messages and cannot test script syntax without selecting stocks first.

**Independent Test**: Frontend can call the API with empty stock_symbols array and receive a clear response (either success with empty results or clear error message).

**Acceptance Scenarios**:

1. **Given** frontend calls `/api/custom-calculations/execute` with empty `stock_symbols: []`, **When** API processes request, **Then** API returns clear response indicating script validation passed or specific error about needing stock symbols
2. **Given** frontend calls API with valid `stock_symbols`, **When** API processes request, **Then** API executes script for all symbols as before
3. **Given** frontend calls API for script syntax validation only, **When** API receives request, **Then** API validates script and returns syntax check result without requiring stock symbols

### Edge Cases

- What if frontend needs to test script syntax before selecting stocks?
- Should API support dry-run mode for syntax validation?
- How should API handle mixed scenarios (some valid symbols, some invalid)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST provide clear error messages when `stock_symbols` is empty explaining why stock symbols are required
- **FR-002**: API SHOULD support script syntax validation mode when `stock_symbols` is empty (return syntax check result without execution)
- **FR-003**: API MUST validate that when execution is requested, at least one stock symbol must be provided
- **FR-004**: API MUST return helpful error messages indicating which parameter is missing or invalid
- **FR-005**: API MUST distinguish between syntax validation requests and execution requests
- **FR-006**: Error messages MUST guide users to provide correct input (e.g., "请至少选择一个股票" instead of "参数错误")

### Key Entities *(include if feature involves data)*

- **API Request**: Contains script, stock_symbols array, column_name, optional script_id
- **Script Execution Context**: Row data, historical data access, context variables
- **Validation Mode**: Syntax-check-only mode for testing scripts without execution

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API returns clear, actionable error messages for empty stock_symbols array (not generic "参数错误")
- **SC-002**: Frontend can validate script syntax without selecting stocks first
- **SC-003**: Error messages guide users to provide required inputs (specific parameter names)
- **SC-004**: API distinguishes between syntax validation and execution requests
- **SC-005**: API maintains backward compatibility with existing frontend code
- **SC-006**: Invalid request rejection includes specific missing/invalid parameter identification

## Assumptions

- Frontend may need to test script syntax before selecting stocks
- Users expect clear error messages indicating what's missing
- Empty array in stock_symbols indicates user hasn't selected stocks yet
- API should support both execution and validation-only modes
- Existing frontend behavior is intentional but needs better error messaging
