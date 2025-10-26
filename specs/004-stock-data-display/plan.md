# Implementation Plan: Stock Data Display on Dashboard

**Branch**: `004-stock-data-display` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-stock-data-display/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement stock price data display on dashboard by enhancing `/stock-price/list` API to return latest price, change percentage, and volume for each stock. The current implementation only returns basic stock info without price data. Required: 1) Efficient SQL JOIN to fetch latest price from timescale data, 2) Calculate price change percentage, 3) Return volume data, 4) Optimize query performance for 200+ stocks.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Flask 3.x, SQLAlchemy 2.0+, psycopg2-binary 2.9+, TimescaleDB  
**Storage**: PostgreSQL with TimescaleDB extension (timeseries database)  
**Testing**: pytest (not initialized yet)  
**Target Platform**: Linux server (Rocky Linux 9)  
**Project Type**: Web application (Flask backend)  
**Performance Goals**: API response time < 2 seconds for 200+ stocks, DB query < 500ms  
**Constraints**: Must maintain backward compatibility with existing frontend, handle missing data gracefully  
**Scale/Scope**: 500+ stocks across multiple markets (SH/SZ/BJ), daily price data with historical records

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Direct Development on Main
✅ **PASS**: Currently on feature branch `004-stock-data-display`. Will switch to main after planning phase completes. This planning artifact creation can happen on feature branch.

### II. Complete Before Commit
✅ **PASS**: This is planning phase only - no code commits yet. Implementation will follow spec completion.

### III. Incremental Commits
✅ **PASS**: Implementation will follow incremental commit pattern - each feature complete before committing.

### IV. Test Before Push  
⚠️ **NEEDS ATTENTION**: Must ensure implementation includes:
- Test that API returns price data for stocks
- Test price change calculation accuracy
- Performance test for 200+ stocks
- Database query efficiency validation

### V. Documentation Integrity
✅ **PASS**: Will update API documentation with new response fields, data model changes documented.

### VI. API Contract Compliance
✅ **PASS**: Will ensure response format matches frontend expectations for Chinese column headers and data structure consistency.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

Flask Web Application (Single Project):

```text
app/
├── routes/
│   └── stock_price.py           # API endpoints (NEEDS MODIFICATION)
├── services/
│   └── stock_data_service.py    # Business logic (NEEDS MODIFICATION)
├── utils/
│   └── responses.py              # Response formatting
└── models/
    └── [model imports]

models/
├── stock_data.py                 # StockDailyData, StockInfo models
└── custom_script.py

database/
├── connection.py                 # DB manager
└── migrations/

tests/
├── test_sandbox_security.py
└── [test files to be added]

config/
├── settings.py                   # Database config
└── logging_config.py

constants/
└── stock_lists/
    ├── xshg_stocks.json         # Shanghai stocks
    ├── xshe_stocks.json         # Shenzhen stocks
    └── bjse_stocks.json         # Beijing stocks
```

**Structure Decision**: Single Flask application with clear separation between routes, services, and models. TimescaleDB for time-series stock data. No frontend code in this repository (frontend is separate application).

**Key Files to Modify**:
- `app/routes/stock_price.py` - Add price data to `/list` endpoint
- `app/services/stock_data_service.py` - New method `list_stocks_with_latest_price()` with SQL JOIN
- Response format to include: close_price, price_change_pct, volume

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. Implementation uses existing patterns and infrastructure.

## Phase Status

### Phase 0: Research ✅ COMPLETE
- ✅ Generated `research.md` with SQL query patterns
- ✅ Resolved all technical unknowns
- ✅ Decision: LATERAL JOIN for latest price per stock

### Phase 1: Design ✅ COMPLETE
- ✅ Generated `data-model.md` with entity details
- ✅ Generated `contracts/api-contracts.json` with API spec
- ✅ Generated `quickstart.md` with implementation guide
- ✅ Updated agent context files

### Phase 2: Tasks (TODO)
- Implementation tasks will be generated by `/speckit.tasks` command
- Not part of this planning phase

## Post-Design Constitution Check

**Re-evaluation after Phase 1 design completion:**

### I. Direct Development on Main
⚠️ **PENDING**: Currently on feature branch. Will switch to main branch before implementation per constitution requirement.

### II. Complete Before Commit
✅ **PASS**: Will ensure full implementation before committing.

### III. Incremental Commits
✅ **PASS**: Each component will be committed independently.

### IV. Test Before Push
✅ **PASS**: Test plan documented in quickstart.md:
- Manual API testing
- Performance validation
- Database query verification

### V. Documentation Integrity
✅ **PASS**: All documentation generated (spec, plan, research, data-model, contracts, quickstart).

### VI. API Contract Compliance
✅ **PASS**: Response format matches existing structure, only adds fields. Maintains backward compatibility.

## Next Steps

1. **Switch to main branch** per Constitution requirement
2. **Run `/speckit.tasks`** to generate implementation tasks
3. **Implement code changes** per quickstart.md
4. **Test thoroughly** per validation checklist
5. **Commit and push** after successful testing
