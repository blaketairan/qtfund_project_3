# Script Debug API - Quickstart

**Feature**: 010-script-debug-api  
**Date**: 2025-11-03

## Overview

Debug endpoint for testing custom calculation scripts against single stocks with detailed execution logs.

## API Endpoint

**Endpoint**: `POST /api/custom-calculations/debug`

## Usage Examples

### 1. Debug Inline Script Code

```bash
curl -X POST http://localhost:8000/api/custom-calculations/debug \
  -H "Content-Type: application/json" \
  -d '{
    "script": "result = row[\"close_price\"] * 1.1",
    "symbol": "SH.600519"
  }'
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "脚本调试执行成功",
  "data": {
    "symbol": "SH.600519",
    "result": 1870.55,
    "logs": [
      "[INPUT] Symbol: SH.600519",
      "[INPUT] Script source: inline code",
      "[INPUT] Row data keys: ['symbol', 'stock_name', 'close_price', 'volume', ...]",
      "[VALIDATION] Syntax check passed",
      "[EXEC] Starting script execution",
      "[CALC] row['close_price'] = 1700.50",
      "[RESULT] result = 1870.55, type: float",
      "[TIMING] Total execution: 23ms"
    ],
    "duration_ms": 23,
    "row_data": {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "close_price": 1700.50
    }
  }
}
```

### 2. Debug Uploaded Script (Script ID)

```bash
curl -X POST http://localhost:8000/api/custom-calculations/debug \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": 2,
    "symbol": "SH.510300"
  }'
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "脚本调试执行成功",
  "data": {
    "symbol": "SH.510300",
    "result": 0.093,
    "logs": [
      "[INPUT] Symbol: SH.510300",
      "[INPUT] Script source: script_id=2 (动量加速度评分)",
      "[INPUT] Row data: {symbol: 'SH.510300', close_price: 4.852, ...}",
      "[EXEC] Calling get_history(SH.510300, 68)",
      "[EXEC] Retrieved 68 history records (2025-08-20 to 2025-10-27)",
      "[CALC] Calculating daily momentum scores...",
      "[CALC] window 1: score = 0.082",
      "[CALC] window 2: score = 0.089",
      "...",
      "[CALC] Second derivative: 0.0012",
      "[RESULT] result = 0.093",
      "[TIMING] Total execution: 156ms"
    ],
    "duration_ms": 156
  }
}
```

### 3. Debug with Mock Data

```bash
curl -X POST http://localhost:8000/api/custom-calculations/debug \
  -H "Content-Type: application/json" \
  -d '{
    "script": "result = row[\"close_price\"] / row[\"volume\"] * 1000000",
    "symbol": "TEST.000001",
    "mock_data": {
      "symbol": "TEST.000001",
      "stock_name": "测试股票",
      "close_price": 100.00,
      "volume": 1000000
    }
  }'
```

**Expected Response**:
```json
{
  "code": 200,
  "message": "脚本调试执行成功（使用Mock数据）",
  "data": {
    "symbol": "TEST.000001",
    "result": 100.00,
    "logs": [
      "[INPUT] Symbol: TEST.000001",
      "[INPUT] Using mock data (not queried from database)",
      "[INPUT] Mock row: {symbol: 'TEST.000001', close_price: 100.00, volume: 1000000}",
      "[EXEC] Starting script execution",
      "[CALC] row['close_price'] / row['volume'] * 1000000 = 100.00",
      "[RESULT] result = 100.00"
    ],
    "duration_ms": 12
  }
}
```

### 4. Debug Script with Syntax Error

```bash
curl -X POST http://localhost:8000/api/custom-calculations/debug \
  -H "Content-Type: application/json" \
  -d '{
    "script": "result = row[close_price]",
    "symbol": "SH.600519"
  }'
```

**Expected Response**:
```json
{
  "code": 400,
  "message": "语法错误",
  "error": "invalid syntax (<inline-script>, line 1)",
  "details": {
    "line_number": 1,
    "error_type": "syntax",
    "logs": [
      "[INPUT] Symbol: SH.600519",
      "[INPUT] Script source: inline code",
      "[VALIDATION] Syntax check failed",
      "[ERROR] Line 1: invalid syntax - missing quotes around 'close_price'"
    ]
  }
}
```

### 5. Debug Script with Runtime Error

```bash
curl -X POST http://localhost:8000/api/custom-calculations/debug \
  -H "Content-Type: application/json" \
  -d '{
    "script": "result = row[\"price\"] * 1.1",
    "symbol": "SH.600519"
  }'
```

**Expected Response**:
```json
{
  "code": 500,
  "message": "执行错误",
  "error": "'price'",
  "details": {
    "traceback": "Traceback (most recent call last):\\n  File \"<inline-script>\", line 1\\n    result = row[\"price\"] * 1.1\\nKeyError: 'price'",
    "error_type": "runtime",
    "logs": [
      "[INPUT] Symbol: SH.600519",
      "[INPUT] Row data keys: ['symbol', 'stock_name', 'close_price', 'volume', ...]",
      "[VALIDATION] Syntax check passed",
      "[EXEC] Starting script execution",
      "[ERROR] Runtime error: KeyError 'price' (available keys: symbol, stock_name, close_price, volume, ...)"
    ],
    "duration_ms": 8
  }
}
```

## Testing Checklist

### API Behavior

- [ ] Debug with inline script code works
- [ ] Debug with script ID works
- [ ] Debug with mock data works
- [ ] Syntax errors return 400 with line numbers
- [ ] Runtime errors return 500 with traceback
- [ ] Logs include all execution steps
- [ ] Duration measurement is accurate

### Log Quality

- [ ] Input logs show symbol and row data
- [ ] Execution logs show function calls (get_history)
- [ ] Calculation logs show intermediate values
- [ ] Result logs show final value and type
- [ ] Error logs show clear error messages
- [ ] Timing logs show execution duration

### Error Handling

- [ ] Missing symbol returns 400
- [ ] Invalid symbol format returns 400
- [ ] Both script and script_id provided returns 400
- [ ] Neither script nor script_id provided returns 400
- [ ] Non-existent script_id returns 404
- [ ] Symbol not found (without mock data) handles gracefully

## Implementation Notes

1. Reuse existing SandboxExecutor with verbose mode
2. Query stock data using existing StockDataService
3. Load scripts using existing CustomScript model
4. Add new route handler in custom_calculation.py
5. Enhance SandboxExecutor.execute() to accept verbose flag
6. Return logs in response alongside result

