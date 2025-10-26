# 股票数据查询服务 Constitution

<!--
Sync Impact Report (v1.1.0):
  Version change: 1.0.0 → 1.1.0 (MINOR: Added API contract validation principle)
  Modified principles: None
  Added sections: API Contract Compliance (Principle VI)
  Removed sections: None
  Templates requiring updates: 
    ✅ plan-template.md - updated check
    ✅ spec-template.md - aligned scope
    ✅ tasks-template.md - task types aligned
    ⚠ commands/*.md - needs review for git workflow references
  Follow-up TODOs: None
-->

## Core Principles

### I. Direct Development on Main

所有功能开发直接在 `main` 分支上进行。开发者应直接提交到 `main` 分支，无需创建feature分支。

**规则**:
- 所有代码变更直接在 `main` 分支开发
- 每个需求完成必须独立commit
- 每个commit后必须立即push到远程
- Commit消息应清晰描述修改内容

**原因**: 简化开发流程，减少分支管理开销，适合快速迭代开发。多人协作时通过频繁push避免冲突。

### II. Complete Before Commit

每个需求必须完整实现后才能提交。

**规则**:
- 需求规格、设计、实现必须全部完成
- 所有必需的任务已完成
- 代码通过基本验证（lint、格式检查）
- 关键功能手动测试通过

**原因**: 确保每次提交都是完整、可用的功能，避免断头提交或半成品代码。

### III. Incremental Commits

每完成一个功能需求，立即独立commit并push。

**规则**:
- 每个需求作为独立的commit提交
- Commit包含完整的变更：代码、文档、配置
- 使用清晰的commit消息描述修改内容
- 提交后立即push，不要积累多次commit

**原因**: 保持提交历史清晰，便于回溯和问题定位。及时push避免本地改动丢失。

### IV. Test Before Push

Push之前必须验证代码可以正常工作。

**规则**:
- 应用可以正常启动
- 修复的功能正常工作
- 相关端点可以访问
- 不存在明显的语法或逻辑错误

**原因**: 确保远程仓库main分支始终保持可工作状态。

### V. Documentation Integrity

所有功能变更必须伴随相应的文档更新。

**规则**:
- 新增API端点需要更新API文档
- 数据结构变更需要更新数据模型文档
- 重要功能变更需要更新README或使用说明
- 保留feature规格文档作为历史记录

**原因**: 保持文档与代码同步，便于后续维护和新成员理解。

### VI. API Contract Compliance

API响应格式必须与文档契约完全一致，确保前端能够正确解析。

**规则**:
- API返回结构必须与spec文档定义的响应结构完全匹配
- 文档中定义的数组位置（如 `data` vs `data.items`）必须严格执行
- 必须提供完整的响应示例，包括真实的JSON结构
- 如果响应格式与前端期望不匹配，必须立即修正后端实现或更新契约文档
- 不得返回与契约不一致的结构（例如文档说返回 `data.items`，实际返回 `data`）

**原因**: 响应格式不一致会导致前端解析失败，产生生产环境bug。严格遵循契约可以确保前后端协作顺畅。

**示例错误**:
```python
# ❌ 错误：文档约定返回 data.items，实际返回 data
return {"code": 200, "data": items}  # 与契约不匹配

# ✅ 正确：与契约一致
return {"code": 200, "data": {"items": items, "total": len(items)}}
```

## Development Workflow

### Git Workflow

**直接在main分支开发**:
1. 从main分支开始工作
2. 完成需求实现
3. 验证功能正常工作
4. Commit所有变更
5. Push到远程main分支

**提交频率**: 每个完整需求完成后立即提交并push，不要等待多个需求。

### Commit Message Format

推荐格式：
```
<type>: <简短描述>

<详细说明，可选>

相关issue: #issue-number
```

示例：
```
fix: 修复stock-price路由中缺失的create_success_response导入

- 在app/routes/stock_price.py中添加缺失的导入
- 修复/api/stock-price/list端点返回500的问题
```

## Quality Gates

### Code Quality

- **Lint检查**: 代码必须通过基本的lint检查
- **格式统一**: 遵守项目代码风格规范
- **无语法错误**: 确保代码可以正常解析和执行

### Functional Validation

- **应用启动**: 修改后应用可以正常启动
- **功能验证**: 新增或修改的功能可以正常工作
- **回归测试**: 确认没有破坏现有功能

### Documentation

- **代码注释**: 复杂逻辑需要注释说明
- **文档更新**: API、配置等变更需要更新相应文档
- **变更记录**: 重要变更应记录在文档中

## Governance

### Amendment Process

宪法修正案需要：
1. 明确说明修正原因和目标
2. 评估对现有开发流程的影响
3. 更新相关模板和文档
4. 提交commit记录变更历史

### Compliance

- 所有开发者必须遵守本宪法
- 代码审查时验证是否符合宪法要求
- 违反宪法的代码将被要求修正

### Version Policy

**版本号**: MAJOR.MINOR.PATCH

- **MAJOR**: 核心原则的重大变更，影响所有开发者
- **MINOR**: 新增原则或工作流改进
- **PATCH**: 澄清说明或非实质性调整

**Version**: 1.1.0 | **Ratified**: 2025-10-26 | **Last Amended**: 2025-01-27
