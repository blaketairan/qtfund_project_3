# Feature Specification: Momentum Score Calculation Script Example

**Feature Branch**: `005-momentum-score-script`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "在script_example路径下，写一个计算动量分的脚本样例，要能实际执行的。计算动量分的逻辑参考下面这份代码，但注意需要在我们平台能够执行，考虑那些变量取值的写法。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Momentum Score Script Example (Priority: P1)

Developers/users need a working example script that demonstrates how to calculate momentum score for stocks using weighted linear regression, so they can understand and adapt the calculation logic for their custom scripts.

**Why this priority**: Frontend users need a practical reference to understand how to write custom calculation scripts that can be executed safely in the platform's sandbox environment.

**Independent Test**: When users call the script execution API with the momentum score script, it successfully calculates the momentum score for provided stocks and returns numeric results.

**Acceptance Scenarios**:

1. **Given** a momentum score calculation script exists in `script_example/` directory, **When** developers review the script code, **Then** they can understand how to calculate momentum using weighted linear regression
2. **Given** stock data with sufficient historical data (e.g., 60+ days), **When** the momentum script executes via the API, **Then** it returns a numeric momentum score for each stock
3. **Given** stocks without sufficient historical data, **When** the momentum script executes, **Then** it returns appropriate error/null values without crashing
4. **Given** the script uses platform-compatible API calls, **When** it executes in the sandbox, **Then** it runs successfully without security violations

### Edge Cases

- What happens when stock has less than required trading days (e.g., new IPO)?
- How does system handle stocks with missing/irregular data points?
- What if all historical prices are identical (no variation)?
- How does script handle division by zero in calculations?
- What if market data contains NaN or None values?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Script MUST calculate momentum score using weighted linear regression on logarithmic price data
- **FR-002**: Platform MUST provide historical price data access API (e.g., `context.get_history(symbol, days)`) for scripts to retrieve historical data
- **FR-003**: Script MUST compute annualized returns using: `(exp(slope) ^ 250) - 1` where slope is from weighted regression
- **FR-004**: Script MUST calculate R² coefficient using weighted residuals for regression quality assessment
- **FR-005**: Script MUST return final momentum score as: `annualized_returns * r_squared`
- **FR-006**: Script MUST define error handler function (e.g., `handle_error(data_available, data_requested, error_type)`) to customize behavior for insufficient data or other errors
- **FR-012**: Platform MUST provide default error handler implementation (returns None/null with generic error message) if script doesn't define custom handler
- **FR-007**: Script MUST use platform-compatible syntax that executes safely in RestrictedPython sandbox
- **FR-011**: Platform MUST expose historical price data API function to sandbox executor's safe globals (e.g., `get_history(symbol, days)`)
- **FR-008**: Script MUST be saved as example file in `script_example/` directory for reference
- **FR-009**: Script MUST include comments explaining calculation steps and key parameters
- **FR-010**: Script MUST be executable via existing custom calculation API (`/api/custom-calculation/execute`)

### Key Entities *(include if feature involves data)*

- **Stock Historical Data**: Daily closing prices, trade dates for momentum calculation
- **Momentum Score Input**: Stock symbol, historical price series, number of trading days
- **Momentum Score Output**: Numeric score value (float) representing momentum strength
- **Weight Array**: Linearly increasing weights applied to recent data points
- **Regression Metrics**: Slope, intercept, R² derived from weighted linear regression

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can successfully execute the momentum score script via API for at least 10 different stocks
- **SC-002**: Script execution completes successfully in under 2 seconds per stock
- **SC-003**: Script returns numeric values (not errors) for at least 90% of stocks with sufficient data
- **SC-004**: Momentum score calculation logic matches reference algorithm (weighted linear regression, annualized returns, R² integration)
- **SC-005**: Script demonstrates proper handling of platform variable access patterns (e.g., `row.close_price`, historical data access)
- **SC-006**: Script execution passes sandbox security checks without triggering RestrictedPython violations
- **SC-007**: Script serves as reusable reference for users creating similar custom calculations
- **SC-008**: Documentation/comment quality sufficient for users to understand and modify the example

## Assumptions

- Platform MUST provide historical price data access API (e.g., `context.get_history(symbol, days)` or equivalent function)
- Users have access to library functions equivalent to `np.polyfit`, `np.log`, `np.mean`, `np.sum`, `np.arange`, `math.exp`, `math.pow`
- Platform can provide sufficient historical data (e.g., 60-250 trading days) for meaningful momentum calculation
- Python standard library and math modules are available in sandbox environment
- Script will be executed in context where single-stock or multi-stock data is provided
- Weight vector generation (linear increase from 1 to 2) can be implemented using available array/length functions
- Annualization factor of 250 trading days is appropriate for stock market calculations
- Script parameters are hardcoded in script code (users edit script to modify)
- Scripts can define custom error handler callbacks (platform provides default)

## Clarifications

### Session 2025-01-27

- Q1: How should the script access historical price data for momentum calculation? → A: Platform will provide a history access API function (e.g., `context.get_history(symbol, days)`) for scripts to retrieve historical price data
- Q2: Should trading days parameter be configurable or fixed? → A: Parameters hardcoded in script code (e.g., `days = 250` in script), users modify script to adjust
- Q3: How to handle insufficient data errors? → A: Script defines custom error handler callback (e.g., `handle_error(data_available, data_requested)`), platform provides default implementation returning None/null with error message
