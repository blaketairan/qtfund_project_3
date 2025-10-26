# Data Model: Momentum Score Script

**Feature**: 005-momentum-score-script  
**Date**: 2025-01-27

## Overview

This feature creates an example momentum score calculation script and enhances the platform's sandbox executor to support historical data access. The script demonstrates weighted linear regression for stock momentum analysis.

## Data Entities

### Historical Stock Data (Existing)

**Table**: `stock_daily_data` (TimescaleDB hypertable)

**Fields Used**:
- `symbol` (String): Stock identifier with market prefix
- `trade_date` (DateTime): Trading date
- `close_price` (DECIMAL(10,4)): Closing price for the day
- `volume` (BIGINT): Trading volume
- `price_change_pct` (DECIMAL(8,4)): Percentage price change

**Query Pattern**: Retrieve last N trading days ordered by trade_date DESC

### Script Execution Context

**Context Object** (passed to script):
- `row` (Dict): Current stock data
  - `symbol`: Stock symbol
  - `close_price`: Latest close price
  - Other stock metadata
- `get_history(symbol, days)` (Function): New historical data access function
  - Returns: List of historical price records

### Example Script Data Flow

```
User Request (API)
  ↓
/api/custom-calculation/execute
  ↓
Sandbox Executor
  - Inject context: {row, get_history}
  ↓
Script Execution
  - Call get_history(row['symbol'], 250)
  - Calculate weighted linear regression
  - Compute momentum score
  ↓
Return: {symbol, value, error}
```

## Response Data Model

### Request Parameters

**Endpoint**: `POST /api/custom-calculation/execute`

**Request Body**:
```json
{
  "script": "<python code>",
  "stock_symbols": ["SH.600519", "SZ.000001"],
  "column_name": "momentum_score"
}
```

### Response Structure

**Status**: 200 OK

**Response Body**:
```json
{
  "code": 200,
  "message": "执行成功",
  "timestamp": "2025-01-27 10:30:45",
  "data": {
    "results": [
      {
        "symbol": "SH.600519",
        "value": 0.1523,
        "error": null
      },
      {
        "symbol": "SZ.000001",
        "value": null,
        "error": "Insufficient data: available 45, requested 250"
      }
    ]
  }
}
```

**Field Descriptions**:
- `symbol`: Stock identifier
- `value`: Momentum score (float or null)
- `error`: Error message if calculation failed (string or null)

## Calculation Data Model

### Input Data

**Historical Price Series**: Array of close prices
- Length: 60-250 trading days (configurable)
- Data points: Daily closing prices
- Source: TimescaleDB `stock_daily_data` table

**Parameters** (hardcoded in script):
- `DAYS` (int): Number of trading days to analyze
- `WEIGHT_START` (float): Starting weight for oldest data
- `WEIGHT_END` (float): Ending weight for newest data
- `ANNUALIZATION` (int): Trading days per year for annualization

### Processing Steps

1. **Data Retrieval**: Call `get_history(symbol, days)` to fetch historical prices
2. **Log Transform**: Apply natural logarithm to prices: `y = log(prices)`
3. **Weight Generation**: Create linear weight vector: `weights = linspace(start, end, n)`
4. **Regression Calculation**: Compute weighted linear regression on log prices
5. **Annualization**: Calculate annualized return: `(exp(slope) ^ 250) - 1`
6. **R² Calculation**: Compute weighted R² coefficient
7. **Score**: Multiply annualized return by R²: `score = return * r_squared`

### Output Data

**Momentum Score**: Float value representing momentum strength
- Range: Can be negative (downward momentum) or positive (upward momentum)
- Unit: Dimensionless ratio
- Interpretation: Higher positive value indicates stronger upward momentum

**Error Cases**:
- `null` when insufficient data (< 30 trading days)
- Custom error message if `handle_error()` returns specific response

## Script Error Handler Model

### Error Handler Function Signature

```python
def handle_error(data_available: int, data_requested: int, error_type: str) -> tuple:
    """
    Custom error handler for insufficient data or calculation errors
    
    Args:
        data_available: Number of data points actually available
        data_requested: Number of data points requested
        error_type: Type of error ('insufficient_data', 'zero_variance', etc.)
        
    Returns:
        Tuple of (result_value, error_message):
        - result_value: Optional value to return instead of null
        - error_message: Optional error description
    """
    # Platform default: return None with error message
    return None, f"Insufficient data: requested {data_requested}, available {data_available}"
```

### Error Types

1. **insufficient_data**: Requested days exceed available data
2. **zero_variance**: All prices identical (no momentum)
3. **missing_data**: Gaps in historical data
4. **invalid_symbol**: Symbol not found in database

## Data Validation Rules

### Input Validation
1. `symbol` format: Must be "MARKET.CODE" (e.g., "SH.600519")
2. `days` parameter: Must be positive integer, max 1000
3. Historical data availability: Minimum 30 days for meaningful calculation

### Output Validation
1. Momentum score: Must be float (can be negative)
2. Error message: Must be string or null
3. Result: Either `value` or `error` must be set, not both

## Integration with Existing Models

### CustomScript Model

Scripts can be saved to database using existing `CustomScript` model:
- `name`: "Momentum Score Example"
- `code`: Script code content
- `description`: "Calculates momentum using weighted linear regression"
- `created_at`, `updated_at`: Timestamps

### Sandbox Executor Integration

Historical data access integrated into sandbox execution:
- Function added to `_safe_globals`
- Available to all script executions
- Read-only access to TimescaleDB
- No schema changes required

## Performance Considerations

### Data Retrieval
- Query TimescaleDB efficiently using existing indexes
- Limit retrieval to requested days
- Cache recent queries if needed
- Expected query time: < 100ms for 250 days

### Calculation Performance
- Weighted regression: O(n) complexity for n data points
- Expected execution: < 100ms for 250 points
- Total script execution: < 2 seconds including DB query

### Error Handling
- No database queries for error cases
- Return null immediately if insufficient data
- Custom handlers add minimal overhead

## Migration Notes

### Platform Changes
- No database schema changes required
- Only enhancement to `SandboxExecutor` class
- Backward compatible with existing scripts

### Example Script
- New file: `script_example/momentum_score.py`
- No database migration needed
- Can be executed immediately after platform enhancement

