# Data Model: Script Debug API

**Feature**: 010-script-debug-api  
**Date**: 2025-11-03

## Overview

This feature adds a debug endpoint with enhanced logging. No new database entities required.

## Request/Response Data Model

### Debug Request

**HTTP Method**: POST  
**Endpoint**: `/api/custom-calculations/debug`

**Request Body**:
```typescript
interface DebugRequest {
  script?: string;      // Inline script code (mutually exclusive with script_id)
  script_id?: number;   // Reference to uploaded script (mutually exclusive with script)
  symbol: string;       // Stock symbol (e.g., "SH.600519")
  mock_data?: {         // Optional mock row data
    symbol: string;
    stock_name: string;
    close_price?: number;
    volume?: number;
    // ... other row fields
  };
}
```

**Validation Rules**:
- MUST provide exactly one of: `script` or `script_id`
- `symbol` is required
- `symbol` must match pattern: `^(SH|SZ|BJ)\.\d{6}$`
- `mock_data` is optional
- If `script_id` provided, script must exist in database

### Debug Response

**Success Response**:
```typescript
interface DebugResponse {
  code: 200;
  message: string;
  data: {
    symbol: string;
    result: number | null;     // Calculated result
    logs: string[];            // Execution logs array
    duration_ms: number;       // Execution time in milliseconds
    row_data: object;          // Input row data used
  };
}
```

**Error Response** (Syntax Error):
```typescript
interface DebugErrorResponse {
  code: 400;
  message: "语法错误";
  error: string;              // Error message
  details: {
    line_number?: number;
    error_type: "syntax" | "runtime";
    logs: string[];           // Logs up to point of failure
  };
}
```

**Error Response** (Runtime Error):
```typescript
interface DebugRuntimeErrorResponse {
  code: 500;
  message: "执行错误";
  error: string;
  details: {
    traceback: string;        // Full Python traceback
    error_type: "runtime";
    logs: string[];           // All execution logs
    duration_ms: number;
  };
}
```

## Execution Flow

### Flow 1: Debug with Script Code

```
User Request
    ↓
POST /api/custom-calculations/debug
{
  "script": "result = row['close_price'] * 1.1",
  "symbol": "SH.600519"
}
    ↓
Validate Parameters
    ↓
Query Stock Data (symbol="SH.600519")
    ↓
Create Context { row: stock_data }
    ↓
Execute Script (verbose=True)
    ↓
Collect Logs
    ↓
Return Response
{
  "code": 200,
  "data": {
    "result": 1870.55,
    "logs": [
      "[INPUT] Symbol: SH.600519",
      "[INPUT] Row: {symbol: 'SH.600519', close_price: 1700.50, ...}",
      "[EXEC] Script validation passed",
      "[EXEC] Executing script...",
      "[CALC] row['close_price'] = 1700.50",
      "[CALC] 1700.50 * 1.1 = 1870.55",
      "[RESULT] result = 1870.55",
      "[TIMING] Execution completed in 23ms"
    ],
    "duration_ms": 23
  }
}
```

### Flow 2: Debug with Script ID

```
User Request
    ↓
POST /api/custom-calculations/debug
{
  "script_id": 5,
  "symbol": "SH.600519"
}
    ↓
Load Script from Database (id=5)
    ↓
Query Stock Data
    ↓
Execute with Verbose Logging
    ↓
Return Response with Logs
```

### Flow 3: Debug with Mock Data

```
User Request
    ↓
POST /api/custom-calculations/debug
{
  "script": "...",
  "symbol": "SH.600519",
  "mock_data": {
    "symbol": "SH.600519",
    "close_price": 1000.00,  // Mock value
    "volume": 5000000
  }
}
    ↓
Skip Database Query
    ↓
Use Mock Data as Row Context
    ↓
Execute Script
    ↓
Return Response
{
  "data": {
    "logs": [
      "[INPUT] Using mock data",
      "[INPUT] Row: {close_price: 1000.00, ...}",
      "[RESULT] result = 1100.00"
    ]
  }
}
```

## Log Message Format

### Log Categories

**Input Logs** (`[INPUT]`):
```
[INPUT] Symbol: SH.600519
[INPUT] Script source: inline code (45 lines)
[INPUT] Row data: {symbol: 'SH.600519', close_price: 1700.50, volume: 12000000}
[INPUT] Using mock data
```

**Validation Logs** (`[VALIDATION]`):
```
[VALIDATION] Syntax check passed
[VALIDATION] Script code length: 1234 bytes
```

**Execution Logs** (`[EXEC]`):
```
[EXEC] Starting script execution
[EXEC] Calling get_history(SH.600519, 250)
[EXEC] Retrieved 250 history records (2024-01-01 to 2025-10-27)
```

**Calculation Logs** (`[CALC]`):
```
[CALC] Variable 'prices' = [1700.50, 1695.30, ...]
[CALC] Intermediate result: slope = 0.00123
[CALC] Intermediate result: r_squared = 0.856
```

**Result Logs** (`[RESULT]`):
```
[RESULT] Final value: 0.093
[RESULT] Type: <class 'float'>
```

**Error Logs** (`[ERROR]`):
```
[ERROR] Syntax error at line 15: invalid syntax
[ERROR] Runtime error: division by zero
[ERROR] Traceback: ...
```

**Timing Logs** (`[TIMING]`):
```
[TIMING] Validation: 2ms
[TIMING] Data retrieval: 45ms
[TIMING] Script execution: 18ms
[TIMING] Total: 65ms
```

## Validation Rules

### Input Validation

1. **Script Source**:
   - Exactly one of `script` or `script_id` must be provided
   - If `script_id`: Must exist in `custom_scripts` table
   - If `script`: Max length 100,000 characters

2. **Symbol**:
   - Required field
   - Format: `^(SH|SZ|BJ)\.\d{6}$`
   - Must exist in `stock_info` table (unless mock_data provided)

3. **Mock Data**:
   - Optional
   - If provided: Must include required fields (`symbol`, `stock_name`)
   - Other fields optional (will be null if not provided)

### Output Validation

- `result` must be number or null
- `logs` must be array of strings
- `duration_ms` must be non-negative integer
- Error responses must include `traceback` for runtime errors

## Performance Considerations

### Debug Mode Overhead

**Additional Operations**:
- Log string formatting: ~1-5ms
- Log array operations: ~1-2ms
- Context inspection: ~2-3ms
- **Total overhead**: ~5-10ms (acceptable for debug mode)

**Memory Usage**:
- Logs array: ~5-10KB per debug session
- Temporary variables: ~1-2KB
- **Total**: ~10KB (negligible)

### Comparison

| Mode | Response Time | Memory | Use Case |
|------|---------------|--------|----------|
| Production | 10-50ms | Minimal | Batch execution, performance critical |
| Debug | 20-100ms | +10KB | Single stock testing, detailed logs needed |

