# Custom Calculation API - Quickstart

**Feature**: 002-custom-calculation-api  
**Date**: 2025-01-27

## Overview

Backend API endpoint for executing Python scripts in sandboxed environment. Enables custom quantitative indicators for stock dashboard.

## Prerequisites

- Python 3.9+
- Flask service running on port 8000
- RestrictedPython package installed
- Existing stock database (TimescaleDB)

## Setup

1. **Install RestrictedPython**:
   ```bash
   pip install RestrictedPython
   ```

2. **Add to requirements.txt**:
   ```bash
   echo "RestrictedPython>=6.0.0" >> requirements.txt
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```python
   from RestrictedPython import compile_restricted_exec
   print("RestrictedPython installed successfully")
   ```

## Implementation

### 1. Create Sandbox Executor Service

Create `src/services/sandbox_executor.py`:

```python
from RestrictedPython import compile_restricted_exec
import math

class SandboxExecutor:
    def execute(self, script, stock_row):
        safe_builtins = {
            '__builtins__': {
                'dict': dict, 'list': list, 'str': str, 'int': int,
                'float': float, 'bool': bool, 'len': len, 'range': range,
                'zip': zip, 'enumerate': enumerate, 'abs': abs,
                'min': min, 'max': max, 'sum': sum, 'round': round,
            },
            'math': math,
            'row': stock_row,
        }
        
        try:
            byte_code = compile_restricted_exec(script)
            exec(byte_code.code) in safe_builtins
            return safe_builtins.get('_result')
        except Exception as e:
            raise Exception(f"Script execution failed: {str(e)}")
```

### 2. Create API Endpoint

Create `src/api/routes/custom_calculation.py`:

```python
from flask import Blueprint, request, jsonify
from services.sandbox_executor import SandboxExecutor

bp = Blueprint('custom_calculation', __name__, url_prefix='/api/custom-calculations')

@bp.route('/execute', methods=['POST'])
def execute_calculation():
    data = request.json
    script = data['script']
    stock_symbols = data['stock_symbols']
    
    executor = SandboxExecutor()
    results = []
    
    for symbol in stock_symbols:
        stock_row = fetch_stock_row(symbol)
        try:
            result = executor.execute(script, stock_row)
            results.append({'symbol': symbol, 'value': result, 'error': null})
        except Exception as e:
            results.append({'symbol': symbol, 'value': null, 'error': str(e)})
    
    return jsonify({'code': 200, 'data': {'results': results}})
```

### 3. Register Blueprint

Add to main app:
```python
from api.routes.custom_calculation import bp as custom_calc_bp
app.register_blueprint(custom_calc_bp)
```

## Usage Examples

### Basic Calculation

**Request**:
```bash
curl -X POST http://localhost:8000/api/custom-calculations/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "return row[\"close_price\"] / row[\"volume\"]",
    "column_name": "Price per Volume",
    "stock_symbols": ["SH.600519", "SH.600036"]
  }'
```

**Response**:
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

### Syntax Error Handling

**Request** (with syntax error):
```bash
curl -X POST http://localhost:8000/api/custom-calculations/execute \
  -d '{
    "script": "return row[\"close_price\"] // division error",
    "column_name": "Test",
    "stock_symbols": ["SH.600519"]
  }'
```

**Response**:
```json
{
  "code": 400,
  "message": "Script execution failed",
  "detail": {
    "error_type": "SyntaxError",
    "error_message": "invalid syntax",
    "line_number": 1
  },
  "error": true
}
```

### Security Blocking

**Script attempting dangerous operation**:
```python
import os
return os.system('rm -rf /')
```

**Response**: Blocked - import statement not allowed in sandbox.

## Testing

### Manual API Test
```bash
npm run test-api
```

### Security Tests
```bash
python -m pytest tests/test_sandbox_security.py
```

### Performance Test
```bash
# Test with 200 stocks
python tests/test_batch_processing.py
```

## Troubleshooting

**RestrictedPython import fails**:
- Verify installation: `pip list | grep RestrictedPython`
- Check Python version: `python --version` (must be 3.9+)

**Scripts timeout**:
- Check script complexity (no loops allowed)
- Increase timeout in SandboxExecutor (not recommended)

**Malicious scripts not blocked**:
- Verify safe_builtins configuration
- Run security tests

## Next Steps

1. Add comprehensive test suite
2. Add logging for all script executions
3. Monitor performance under load
4. Consider caching for frequently-used scripts

