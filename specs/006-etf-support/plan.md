# Implementation Plan: ETF Support in Data Query API

**Branch**: `006-etf-support` | **Date**: 2025-10-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-etf-support/spec.md`

## Summary

Add ETF (Exchange Traded Fund) support to the stock list query API, allowing users to filter by instrument type (ETF vs. stock) and ensuring custom script calculations work identically for ETFs and stocks.

**Technical Approach**: Extend existing `/api/stock-price/list` endpoint to accept `is_etf` boolean parameter, add ETF filtering logic in service layer, include ETF marker in response, and ensure script execution context is identical for both instrument types.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Flask 3.x, SQLAlchemy 2.0+, psycopg2-binary 2.9+, RestrictedPython 6.0+  
**Storage**: PostgreSQL with TimescaleDB (TimescaleDB extension)  
**Testing**: pytest  
**Target Platform**: Linux server, Web application  
**Project Type**: Web application (single Flask app)  
**Performance Goals**: API response < 2 seconds for 200+ results, database query < 500ms  
**Constraints**: Existing LATERAL JOIN pattern for latest price data, backward compatibility with existing filters, script execution timeout 10 seconds  
**Scale/Scope**: Support filtering among 5000+ instruments (stocks + ETFs), maintain < 2s API response time

## Constitution Check

*Re-evaluated after Phase 1 design*

- **I. Direct Development on Main**: ✅ PASS - All development on main branch  
- **II. Complete Before Commit**: ✅ PASS - All requirements will be fully implemented before commit  
- **III. Incremental Commits**: ✅ PASS - Each requirement (ETF filtering, script support, metadata) will be independently committed  
- **IV. Test Before Push**: ⚠️ PENDING - Manual testing will be performed before push  
- **V. Documentation Integrity**: ✅ PASS - API contracts and data models will be updated  
- **VI. API Contract Compliance**: ✅ PASS - Response format will match contracts/api-contracts.json exactly

## Project Structure

### Documentation (this feature)

```text
specs/006-etf-support/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (already exists with api-contracts.json)
│   └── api-contracts.json
└── tasks.md             # Phase 2 output (will be created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── routes/
│   └── stock_price.py          # Modify: Add is_etf parameter parsing and filtering
├── services/
│   └── stock_data_service.py  # Modify: Add ETF filtering logic to list_stocks_with_latest_price()
└── models/
    └── stock_data.py           # Review: Ensure ETF support in data model

database/
└── connection.py               # No changes expected

tests/
└── (will add ETF-specific tests)
```

**Structure Decision**: Single Flask web application. ETF support will be added as a query parameter to the existing list endpoint, following the same pattern as existing market_code and is_active filters.

## Complexity Tracking

> **No violations - all features are incremental additions to existing API**

## Phase Status

- [x] Phase 0 (Research): COMPLETE ✅
- [x] Phase 1 (Design): COMPLETE ✅
- [x] Phase 2 (Tasks): COMPLETE ✅

## Next Steps

1. **Phase 0**: Research ETFs vs. stocks data model compatibility
2. **Phase 1**: Generate data model, API contracts (already exists), quickstart guide
3. **Phase 2**: Generate implementation tasks via `/speckit.tasks` command
4. **Implementation**: Add ETF filtering, test, commit, push

