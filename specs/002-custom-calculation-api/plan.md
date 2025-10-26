# Implementation Plan: Custom Calculation API

**Branch**: `002-custom-calculation-api` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification for Python script execution API in backend Flask service

## Summary

Implement secure Python script execution endpoint for custom stock calculations. Users write Python scripts, backend executes them in sandboxed environment (restrictedpython) and returns calculated results. Supports batch processing for 200+ stocks. Prevents unauthorized operations (file access, imports, system calls). Robust error handling with structured responses.

## Technical Context

**Language/Version**: Python 3.9+, Flask 3.0+
**Primary Dependencies**: restrictedpython, Flask, existing TimescaleDB connection
**Storage**: No additional storage (uses existing stock data, results returned directly)
**Testing**: pytest with script execution tests, security validation tests
**Target Platform**: Linux/macOS backend (Flask service port 8000)
**Project Type**: Backend API extension (single Flask app)
**Performance Goals**: <10s execution per request, 200+ concurrent requests handled
**Constraints**: Must use restrictedpython (no eval/exec), must not allow file access, must block imports
**Scale/Scope**: 1 new endpoint, 1 service module, 10 test cases

## Constitution Check

Backend project (`qtfund_project_3`) does not have a constitution file yet. Following standard Python/Flask best practices.

**Principles Applied**:
- Restrictive security: Sandbox all user code execution
- Error transparency: Return detailed error messages to frontend
- Performance awareness: Batch processing, timeouts
- Logging: Audit trail for all script executions

## Project Structure

### Documentation (this feature)

```text
specs/002-custom-calculation-api/
├── spec.md              # Feature specification
├── plan.md            # This file
├── research.md        # Phase 0 output
├── data-model.md      # Phase 1 output
├── quickstart.md      # Phase 1 output
├── contracts/         # Phase 1 output
│   └── api-contracts.json
└── tasks.md           # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── routes/
│   └── custom_calculation.py        # NEW endpoint
└── services/
    └── sandbox_executor.py          # NEW sandbox service

tests/                                  # NEW directory
├── test_custom_calculation.py       # NEW API tests
└── test_sandbox_security.py         # NEW security tests
```

**Structure Decision**: Backend API extension. New endpoint added to existing `app/routes/`. Sandbox executor as separate service module in `app/services/` for testability. Security tests in new `tests/` directory at repo root.

## Implementation Approach

### Phase 1: Database Schema for Script Storage
- Create `custom_scripts` table with:
  - id (primary key)
  - name (string, required)
  - description (optional text)
  - code (Python script text)
  - created_at, updated_at (timestamps)
- Use existing PostgreSQL/TimescaleDB connection

### Phase 2: Sandbox Executor
- Install restrictedpython: `pip install RestrictedPython`
- Implement `SandboxExecutor` class with:
  - Safe globals (dict, list, str, int, float, math)
  - Block dangerous operations (file, network, system)
  - Script compilation and execution
  - Timeout handling (10s max)
  - Exception catching and formatting

### Phase 3: SavedScript Model
- Create `CustomScript` model in `app/models/custom_script.py`
- Implement CRUD operations (save, retrieve, update, delete)
- Add validation for script code syntax
- Handle script uniqueness (by name)

### Phase 4: Script Management Endpoints (CRUD)
- POST /api/custom-calculations/scripts - Create new script
- GET /api/custom-calculations/scripts - List all scripts
- GET /api/custom-calculations/scripts/{id} - Get specific script
- PUT /api/custom-calculations/scripts/{id} - Update script
- DELETE /api/custom-calculations/scripts/{id} - Delete script

### Phase 5: Execute Endpoint with Script Management
- Update `POST /api/custom-calculations/execute`
  - Accept either `script` (inline code) OR `script_id` (reference to saved script)
- If script_id provided: Load script from database
- Fetch stock data for symbols from database
- Pass stock row dict to sandbox executor
- Return JSON results or errors

### Phase 6: Error Handling & Security Validation
- Syntax errors: Return line number and message
- Runtime errors: Return exception type and message
- Timeout: Return timeout error
- Test restricted imports (os, sys, importlib, etc.)
- Test file operations (open, read, write)
- Test network operations
- Test system calls (subprocess, eval, exec)
- Verify all blocked operations fail gracefully

## Dependencies

### New Packages Required

```python
# requirements.txt additions
RestrictedPython>=6.0.0
```

### Existing Packages Used

- Flask: Web framework
- TimescaleDB: Stock data source
- json: Response formatting

## Integration Points

**Frontend API Contract**:
- `POST /api/custom-calculations/execute`
- Request format defined in `contracts/api-contracts.json`
- Response format for success and errors

**Database**:
- Uses existing stock data queries
- No schema changes required
- Reads from StockDailyData and StockInfo tables

## Complexity Tracking

No unnecessary complexity. Using proven restrictedpython library for security.

**Simpler Alternative Rejected**: Using eval/exec directly - REJECTED due to security risk.

