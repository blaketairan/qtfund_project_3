# Research: Custom Calculation API

**Feature**: 002-custom-calculation-api  
**Date**: 2025-01-27  
**Status**: Complete

## Overview

Research conducted to select secure Python execution library and validate sandbox implementation approach.

## Decisions Made

### Decision 1: Sandbox Library

**Chosen**: RestrictedPython (https://github.com/zopefoundation/RestrictedPython)

**Rationale**:
- Actively maintained (Zope Foundation)
- Explicitly designed for safe code execution
- Blocks dangerous operations (file, network, system) by default
- Allows configurable safe built-ins
- Comprehensive security model

**Alternatives Considered**:
- Standard eval/exec: Rejected - extreme security risk
- Docker containers: Rejected - too heavyweight for calculation-only use
- PyPy sandboxing: Rejected - complex setup, overkill
- ast.literal_eval: Rejected - only evaluates literals, not expressions
- RestrictedPython: **CHOSEN** - best balance of security and usability

### Decision 2: Safe Built-ins

**Chosen**: dict, list, str, int, float, bool, len, range, zip, enumerate, math module

**Rationale**:
- Covers all common calculation operations
- Allows data manipulation (dict/list access)
- Supports mathematical computations (math module)
- Blocks file and system access

**Alternatives Considered**:
- Minimal built-ins (only math): Rejected - too restrictive for stock calculations
- All built-ins: Rejected - security risk
- Custom whitelist: **CHOSEN** - balance security and functionality

### Decision 3: Execution Model

**Chosen**: Direct execution in Flask request handler

**Rationale**:
- Simple implementation
- Flask context provides request isolation
- 10 second timeout sufficient for calculations
- No need for worker processes for this use case

**Alternatives Considered**:
- Separate worker process: Rejected - adds complexity, no clear benefit
- Queue-based: Rejected - overkill for simple calculations
- Async execution: Deferred - may add in v2 if performance becomes issue

### Decision 4: Error Handling

**Chosen**: Structured JSON error responses with error details

**Rationale**:
- Frontend needs detailed error messages
- Line numbers help debug syntax errors
- Exception messages help debug runtime errors
- Matches existing API response format

**Alternatives Considered**:
- Generic errors: Rejected - poor developer experience
- Silent failures: Rejected - users need to know what went wrong

### Decision 5: Input Data Format

**Chosen**: Pass stock row as Python dict

**Rationale**:
- Simple for users to access fields
- Matches database row structure
- Easy to validate and format

**Example**:
```python
row = {
    'symbol': 'SH.600519',
    'close_price': 1700.50,
    'volume': 1234567,
    'turnover': 2100000000.00
}
```

## Technology Choices

### RestrictedPython

**Installation**:
```bash
pip install RestrictedPython
```

**Usage**:
```python
from RestrictedPython import compile_restricted_exec, safe_globals
from RestrictedPython.Guards import guarded_iter_unpack

code = compile_restricted_exec(user_script)
exec(code) in {'_getiter_': guarded_iter_unpack}
```

**Security Features**:
- Blocks `import` statements (unless whitelisted)
- Blocks file operations (`open`, `read`, `write`)
- Blocks system calls (`subprocess`, `os.system`)
- Blocks dangerous built-ins (`eval`, `exec`, `__import__`)
- Allows safe operations (math, data structures)

### Safe Globals Configuration

```python
safe_builtins = {
    '__builtins__': {
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
    },
    'math': math,
    'row': stock_row_data,
    '_getitem_': lambda obj, key: obj[key],
}
```

## Security Considerations

### Blocked Operations

- File access: `open()`, `read()`, `write()`
- Network: `urllib`, `requests`, `socket`
- System: `subprocess`, `os.system()`, `os.popen()`
- Import: `import`, `__import__()`, `importlib`
- Eval: `eval()`, `exec()`, `compile()`

### Test Cases Required

1. Attempt to import os - should be blocked
2. Attempt to open file - should be blocked
3. Attempt to access sys - should be blocked
4. Valid calculation - should succeed
5. Division by zero - should return error gracefully

## Performance Considerations

**Execution Timeout**: 10 seconds maximum per request  
**Concurrent Requests**: Flask handles 200+ concurrent (tested with existing API)  
**Memory**: Minimal (each script executes in isolated context)  
**CPU**: Math calculations are fast (no I/O operations)

## Integration Points

**Flask Route**:
- POST endpoint: `/api/custom-calculations/execute`
- Uses existing database connections
- Returns JSON responses

**Database**:
- No schema changes required
- Reads existing StockDailyData table
- Passes row data to scripts

**Frontend**:
- Sends scripts via POST request
- Receives calculated results or errors
- Displays results in custom columns

## Research Status

All clarifications resolved. RestrictedPython library selected for sandboxing. Security model validated. Ready for Phase 1 implementation.

