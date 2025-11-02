# Implementation Plan: Backend Market Filter and Unlimited Results

**Branch**: `007-backend-filter-optimization` | **Date**: 2025-10-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-backend-filter-optimization/spec.md`

## Summary

Remove artificial pagination limits from stock list API, move market filtering to database layer, and extend request timeout to 10 minutes to support returning complete datasets with script calculations.

**Technical Approach**: Remove default `limit=100` constraint, ensure market_code filtering happens in SQL WHERE clause (already implemented), configure Flask request timeout to 600 seconds, optimize response handling for large datasets.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Flask 3.x, SQLAlchemy 2.0+, psycopg2-binary 2.9+, RestrictedPython 6.0+, Gunicorn/uWSGI (for timeout config)  
**Storage**: PostgreSQL with TimescaleDB  
**Testing**: pytest, manual curl testing  
**Target Platform**: Linux server, Web application  
**Project Type**: Web application (single Flask app)  
**Performance Goals**: Support 2000+ record queries, complete within 10 minutes with script calculations, database query < 2 seconds  
**Constraints**: Maintain backward compatibility with limit/offset parameters, ensure market filtering is database-level, prevent memory overflow for very large datasets  
**Scale/Scope**: 5000+ total instruments, support returning all without limit, handle 1000+ instruments with script calculations

## Constitution Check

*Re-evaluated after Phase 1 design*

- **I. Direct Development on Main**: ✅ PASS - All development on main branch  
- **II. Complete Before Commit**: ✅ PASS - All requirements will be fully implemented before commit  
- **III. Incremental Commits**: ✅ PASS - Each requirement (remove limit, timeout config) will be independently committed  
- **IV. Test Before Push**: ⚠️ PENDING - Manual testing with large datasets will be performed before push  
- **V. Documentation Integrity**: ✅ PASS - API contracts and configuration docs will be updated  
- **VI. API Contract Compliance**: ✅ PASS - Response format matches existing contract structure

## Project Structure

### Documentation (this feature)

```text
specs/007-backend-filter-optimization/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (already exists)
│   └── api-contracts.json
└── tasks.md             # Phase 2 output (will be created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── routes/
│   └── stock_price.py          # Modify: Remove default limit, make optional
├── services/
│   └── stock_data_service.py   # Review: Verify market_code filtering is database-level
└── main.py                      # Modify: Configure request timeout to 600 seconds

config/
└── settings.py                  # Modify: Add timeout configuration constants

start_flask_app.py               # Modify: Configure Gunicorn/uWSGI timeout if used
```

**Structure Decision**: Single Flask web application. Changes are configuration updates (remove default limit, increase timeout) and minor route handler modifications.

## Complexity Tracking

> **No violations - changes are configuration optimizations**

## Phase Status

- [x] Phase 0 (Research): COMPLETE ✅
- [x] Phase 1 (Design): COMPLETE ✅
- [x] Phase 2 (Tasks): COMPLETE ✅

## Next Steps

1. **Phase 0**: Research Flask timeout configuration, database connection pool limits, memory optimization for large result sets
2. **Phase 1**: Generate data model (minimal changes), quickstart guide for testing
3. **Phase 2**: Generate implementation tasks via `/speckit.tasks` command
4. **Implementation**: Remove limit default, configure timeout, test with large datasets

