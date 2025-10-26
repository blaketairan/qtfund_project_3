# Data Model: Custom Calculation API

**Feature**: 002-custom-calculation-api  
**Date**: 2025-01-27

## Entities

### 1. CustomCalculationRequest

Input request body from frontend.

**Fields**:
- `script` (string, required): Python code to execute
- `column_name` (string, required): User-provided column name
- `stock_symbols` (array of strings, required): Array of stock symbols to calculate for
  - Format: "MARKET.CODE" (e.g., "SH.600519")

**Validation**:
- Script must be non-empty string
- column_name must be non-empty
- stock_symbols must be non-empty array
- Each symbol must match pattern `^[A-Z]{2}\.\d{6}$`

### 2. CustomCalculationResult

Response returned for successful execution.

**Fields**:
- `results` (array of objects, required): Calculated results per stock
  - `symbol` (string): Stock symbol
  - `value` (number | null): Calculated value, or null if error
  - `error` (string | null): Error message if execution failed

**Format**:
```json
{
  "code": 200,
  "data": {
    "results": [
      {"symbol": "SH.600519", "value": 1.234, "error": null},
      {"symbol": "SH.600036", "value": 2.456, "error": null}
    ]
  }
}
```

### 3. ScriptExecutionError

Error response for failed script execution.

**Fields**:
- `code` (number, required): HTTP status (400)
- `message` (string, required): Error message
- `detail` (object, optional): Error details
  - `line_number` (number, optional): Line number for syntax errors
  - `error_type` (string, optional): Error type (SyntaxError, NameError, etc.)
  - `error_message` (string, optional): Specific error message
- `error` (boolean, required): true

**Format**:
```json
{
  "code": 400,
  "message": "Script execution failed",
  "detail": {
    "line_number": 3,
    "error_type": "SyntaxError",
    "error_message": "invalid syntax"
  },
  "error": true
}
```

### 4. StockRowData

Data structure passed to Python script as `row` variable.

**Fields**:
- All fields from StockDailyData table
  - `symbol` (string): Stock symbol
  - `trade_date` (string): Trading date
  - `open_price` (number): Opening price
  - `high_price` (number): Highest price
  - `low_price` (number): Lowest price
  - `close_price` (number): Closing price
  - `volume` (number): Trading volume
  - `turnover` (number): Trading amount
  - `price_change` (number): Price change
  - `price_change_pct` (number): Price change percentage
  - `market_code` (string): Market code
  - Additional fields as needed

**Usage in Script**:
```python
result = row['close_price'] / row['volume']
return result
```

### 5. SandboxEnvironment

Execution environment for Python scripts.

**Fields**:
- `safe_builtins` (dict): Allowed built-in functions and modules
- `restrictions` (list): Blocked operations
- `timeout` (number): Maximum execution time (10 seconds)

**Configuration**:
```python
safe_builtins = {
    'dict': dict,
    'list': list,
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'len': len,
    'range': range,
    'zip': zip,
    'enumerate': enumerate,
    'abs': abs,
    'min': min,
    'max': max,
    'sum': sum,
    'round': round,
    'math': math,  # math module
    'row': stock_row_dict,
}
```

## Data Flow

1. **Frontend Request**:
   ```
   POST /api/custom-calculations/execute
   Body: {
     "script": "return row['close_price'] / row['volume']",
     "column_name": "Price per Volume",
     "stock_symbols": ["SH.600519", "SH.600036"]
   }
   ```

2. **Backend Processing**:
   - Validate request (script, column_name, stock_symbols)
   - Fetch stock data for each symbol from database
   - For each stock row:
     - Compile script with RestrictedPython
     - Execute in sandbox with safe globals
     - Pass row data as `row` variable
     - Capture return value or exception
   - Aggregate results

3. **Backend Response**:
   ```
   {
     "code": 200,
     "data": {
       "results": [
         {"symbol": "SH.600519", "value": 1.234, "error": null},
         {"symbol": "SH.600036", "value": 2.456, "error": null}
       ]
     }
   }
   ```

4. **Frontend Display**:
   - Receive results
   - Add custom column to table
   - Display calculated values or errors

## Security Model

### Allowed Operations

- Mathematical operations: `+`, `-`, `*`, `/`, `%`, `**`
- Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Data structures: `dict`, `list`, `str`, `int`, `float`
- Functions: `len()`, `range()`, `zip()`, `enumerate()`
- Math module: All functions from `math` module
- Dict/list access: `row['field']`, `list[0]`

### Blocked Operations

- Imports: `import os`, `import sys`, `__import__()`
- File access: `open()`, `read()`, `write()`
- System calls: `os.system()`, `subprocess.run()`
- Network: `socket`, `urllib`, `requests`
- Dangerous built-ins: `eval()`, `exec()`, `compile()`

## Validation Rules

**Request Validation**:
- Script must be non-empty
- column_name must be non-empty (max 100 chars)
- stock_symbols must be array with at least 1 item
- Each symbol must match pattern `/^[A-Z]{2}\.\d{6}$/`
- Maximum 200 symbols per request (performance limit)

**Script Execution Validation**:
- RestrictedPython compilation must succeed
- Execution must complete within 10 seconds
- Return value must be a number (int or float)
- All exceptions must be caught and returned

**Security Validation**:
- Block all import statements
- Block file operations
- Block system operations
- Log all executions for audit trail

