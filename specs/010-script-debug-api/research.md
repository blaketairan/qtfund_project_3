# Research: Script Debug API

**Feature**: 010-script-debug-api  
**Date**: 2025-11-03  
**Status**: Complete

## Overview

Research conducted to determine how to implement verbose logging for script execution debugging without impacting production performance.

## Decisions Made

### Decision 1: Debug Endpoint Design

**Chosen**: New dedicated debug endpoint `POST /api/custom-calculations/debug`

**Rationale**:
- Separates debug concerns from production execution endpoint
- Allows different logging verbosity without affecting production
- Clear API semantics (debug vs execute)
- Can have different rate limits and timeout settings

**Request Format**:
```json
{
  "script": "result = row['close_price'] * 1.1",  // OR
  "script_id": 5,  // Reference uploaded script
  "symbol": "SH.600519",
  "mock_data": {...}  // Optional
}
```

**Alternatives Considered**:
- Add debug flag to existing execute endpoint: Rejected - mixes concerns, complicates production code
- Separate debug service: Rejected - overkill for single endpoint

### Decision 2: Verbose Logging Implementation

**Chosen**: Add `verbose=True` mode to SandboxExecutor

**Rationale**:
- Minimal changes to existing executor
- Logging can be toggled per request
- Production performance unaffected (verbose=False by default)
- Captures logs in list for response inclusion

**Implementation**:
```python
class SandboxExecutor:
    def execute(self, script_code, context, verbose=False):
        logs = []
        if verbose:
            logs.append(f"Context keys: {list(context.keys())}")
            logs.append(f"Row data: {context.get('row')}")
        # ... execution ...
        return result, error, logs if verbose else []
```

**Alternatives Considered**:
- Monkey-patch print(): Rejected - unreliable, doesn't capture all info
- AST instrumentation: Rejected - complex, may break RestrictedPython
- Separate debug executor: Rejected - code duplication

### Decision 3: Script Source (Code vs ID)

**Chosen**: Support both inline script code and script ID reference

**Rationale**:
- Inline code: Quick testing without uploading
- Script ID: Test uploaded/versioned scripts
- Flexibility for different workflows

**Logic**:
```python
if request_data.get('script_id'):
    script = load_script_by_id(script_id)
elif request_data.get('script'):
    script = request_data['script']
else:
    return error("Must provide script or script_id")
```

**Alternatives Considered**:
- Script code only: Rejected - forces re-pasting for uploaded scripts
- Script ID only: Rejected - inconvenient for quick tests

### Decision 4: Mock Data Support

**Chosen**: Optional `mock_data` parameter replaces database query

**Rationale**:
- Enables unit testing without database dependency
- Allows edge case testing (null values, extreme numbers)
- Simple to implement (pass mock_data as row context)

**Implementation**:
```python
if mock_data:
    row = mock_data
else:
    row = query_stock_data(symbol)

context = {'row': row}
```

**Alternatives Considered**:
- Always query database: Rejected - limits testing scenarios
- Separate mock endpoint: Rejected - unnecessary duplication

### Decision 5: Log Capture Strategy

**Chosen**: Collect logs in list during execution, return in response

**Rationale**:
- Simple to implement
- Preserves log order
- Easy to format in JSON response
- No file I/O overhead

**Log Categories**:
1. **Input logs**: Context data, row values
2. **Function call logs**: get_history() calls and results
3. **Execution logs**: Intermediate values, variable assignments
4. **Error logs**: Syntax errors, runtime errors, tracebacks
5. **Timing logs**: Execution duration per phase

**Alternatives Considered**:
- Write to log file: Rejected - requires file management, slower
- Stream logs via WebSocket: Rejected - overkill, requires connection management

## Technology Choices

### Logging Enhancement

**Current Logging**:
```python
logger.info(f"Script execution context keys: {list(context.keys())}")
```

**Enhanced for Debug**:
```python
debug_logs = []
debug_logs.append(f"[INPUT] Symbol: {symbol}")
debug_logs.append(f"[INPUT] Row data: {row}")
debug_logs.append(f"[EXEC] Calling get_history({symbol}, {days})")
debug_logs.append(f"[EXEC] Retrieved {len(history)} records")
debug_logs.append(f"[RESULT] Final value: {result}, type: {type(result)}")
```

### Performance Impact

**Debug Mode**: Verbose logging enabled
- Additional overhead: ~10-50ms per execution
- Memory: ~1-10KB per debug session
- **Acceptable**: Debug is development-only

**Production Mode**: Verbose logging disabled (default)
- No performance impact
- Existing minimal logging preserved

## Security Considerations

### Same Sandbox as Production

- Debug endpoint uses same RestrictedPython sandbox
- No additional security risks
- Script code validated identically
- Execution timeout applies (10 seconds)

### Log Content

- Logs may contain stock prices (not sensitive)
- No user PII in logs
- Logs returned in response (not persisted)
- No log file security concerns

## References

- Existing sandbox executor: `app/services/sandbox_executor.py`
- Script model: `app/models/custom_script.py`
- Production execute endpoint: `app/routes/custom_calculation.py` lines 19-115

