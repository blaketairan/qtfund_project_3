# Implementation Plan: Dynamic Script Columns in List Query

**Branch**: `005-dynamic-column-scripts` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-dynamic-column-scripts/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

增强 `/stock-price/list` API，支持通过 `script_ids` 参数动态计算脚本结果并返回。脚本仅对查询结果集中的股票执行计算（考虑 limit、offset、market_code 等过滤器），确保高效且符合用户期望。

**技术方案**：
- 在现有 API 中添加可选的 `script_ids` 查询参数（数组，最多5个）
- 查询股票列表后，对返回的股票执行指定脚本
- 脚本结果作为 `script_results` 字段添加到每个股票记录
- 支持批量脚本执行，优化性能

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Flask 3.x, SQLAlchemy 2.0+, RestrictedPython 6.0+, psycopg2-binary 2.9+  
**Storage**: PostgreSQL with TimescaleDB  
**Testing**: pytest, manual API testing  
**Target Platform**: Linux server  
**Project Type**: Web application (single Flask backend)  
**Performance Goals**: No specific performance targets  
**Constraints**: 单次查询最多 10000 只股票  
**Scale/Scope**: 支持股市数据查询场景

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Details |
|-----------|--------|---------|
| I. Direct Development on Main | ⚠️ **PENDING** | 当前在 feature 分支，完成后需切换回 main |
| II. Complete Before Commit | ✅ **PASS** | 规格完整，设计、实现将全部完成 |
| III. Incremental Commits | ✅ **PASS** | 功能完成后立即提交 |
| IV. Test Before Push | ✅ **PASS** | 实施后将进行 API 测试验证 |
| V. Documentation Integrity | ✅ **PASS** | 已有 API 契约文档 |
| VI. API Contract Compliance | ✅ **PASS** | 响应格式已定义，需严格遵循 |

**Note**: 当前在 feature 分支 `005-dynamic-column-scripts`。根据 Constitution I，需要在 main 分支开发，但为隔离规划阶段，使用 feature 分支进行规范和组织。

## Project Structure

### Documentation (this feature)

```text
specs/005-dynamic-column-scripts/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/
│   └── api-contracts.json  # Phase 1 output (already exists)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
app/
├── models/
│   └── custom_script.py  # Script model (already exists)
├── services/
│   ├── stock_data_service.py  # Stock list retrieval (exists)
│   └── sandbox_executor.py    # Script execution (exists)
├── routes/
│   └── stock_price.py         # List API endpoint (exists, to modify)
└── main.py                    # Flask app entry point

tests/
└── test_stock_price_api.py  # API integration tests (to create)
```

**Structure Decision**: 单 Flask 应用，现有结构保持不变。主要修改 `app/routes/stock_price.py` 添加 `script_ids` 参数支持，在查询结果上执行脚本并返回扩展记录。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - standard implementation of adding parameter support to existing API.

---

## Phase Status

### Phase 0: Research (✅ COMPLETE)

**Output**: `research.md`

**Key Decisions**:
1. Execute scripts after filtering stocks for efficiency
2. Sequential execution with error handling for simplicity
3. Return null for failed scripts, don't block response
4. Support up to 5 scripts per request

---

### Phase 1: Design (✅ COMPLETE)

**Outputs**: 
- `data-model.md` - Data structure and flow
- `quickstart.md` - Implementation guide
- `contracts/api-contracts.json` - Already exists

**Design Highlights**:
- No schema changes required
- Minimal code changes (modify one route file)
- Response structure: base fields + `script_results` object

---

### Phase 2: Tasks (⏳ PENDING)

**Next Step**: Run `/speckit.tasks` to generate implementation task list

---

## Summary

**Feature**: Add `script_ids` parameter support to `/api/stock-price/list` endpoint  
**Status**: Design complete, ready for implementation  
**Files to Modify**: `app/routes/stock_price.py`  
**Estimated Time**: 2-4 hours (implementation + testing)  
**Risk Level**: Low (additive change, no breaking changes)
