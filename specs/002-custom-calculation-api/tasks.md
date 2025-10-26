# Tasks: Custom Calculation API

**Input**: Design documents from `/specs/002-custom-calculation-api/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included (spec doesn't request them explicitly). Add tests later if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend API extension**: `app/routes/`, `app/services/`, `app/models/`
- **Tests**: `tests/` at repository root
- **Migrations**: `database/migrations/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Install RestrictedPython dependency in requirements.txt
- [X] T002 Create tests directory at repository root
- [X] T003 [P] Setup pytest configuration for tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create SandboxExecutor service class structure in app/services/sandbox_executor.py
- [X] T005 Install RestrictedPython package and configure safe globals in app/services/sandbox_executor.py
- [X] T006 Implement script compilation with RestrictedPython in app/services/sandbox_executor.py
- [X] T007 Implement execution timeout handling (10s max) in app/services/sandbox_executor.py
- [X] T008 Implement exception catching and formatting in app/services/sandbox_executor.py
- [X] T009 Configure safe built-ins (dict, list, str, int, float, math) in app/services/sandbox_executor.py
- [X] T010 Block dangerous operations (file access, imports, system calls) in app/services/sandbox_executor.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Execute Custom Python Scripts (Priority: P1) 🎯 MVP

**Goal**: Users submit Python scripts via frontend, backend executes them safely and returns calculated results.

**Independent Test**: Send POST request to /api/custom-calculations/execute with valid Python script and stock symbols, receive calculated values.

### Implementation for User Story 1

- [X] T011 [US1] Create custom_calculation blueprint in app/routes/custom_calculation.py
- [X] T012 [US1] Implement POST /api/custom-calculations/execute endpoint in app/routes/custom_calculation.py
- [X] T013 [US1] Add request validation for script, column_name, stock_symbols in app/routes/custom_calculation.py
- [X] T014 [US1] Implement stock data fetching from TimescaleDB in app/routes/custom_calculation.py
- [X] T015 [US1] Integrate with SandboxExecutor for script execution in app/routes/custom_calculation.py
- [X] T016 [US1] Implement result aggregation and JSON response formatting in app/routes/custom_calculation.py
- [X] T017 [US1] Add error handling for invalid requests in app/routes/custom_calculation.py
- [X] T018 [US1] Register custom_calculation blueprint in app/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Sandbox Security (Priority: P1)

**Goal**: All user Python scripts execute in restricted environment preventing unauthorized access.

**Independent Test**: Attempt to execute malicious Python code (file access, imports, system calls), verify blocked.

### Implementation for User Story 2

- [ ] T019 [P] [US2] Test restricted imports (os, sys, importlib) in app/services/sandbox_executor.py
- [ ] T020 [P] [US2] Test file operations (open, read, write) blocking in app/services/sandbox_executor.py
- [ ] T021 [P] [US2] Test network operations blocking in app/services/sandbox_executor.py
- [ ] T022 [P] [US2] Test system calls (subprocess, eval, exec) blocking in app/services/sandbox_executor.py
- [ ] T023 [US2] Verify all blocked operations fail gracefully with error messages in app/services/sandbox_executor.py
- [ ] T024 [US2] Add logging for all security violations in app/services/sandbox_executor.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Script Management (Priority: P1)

**Goal**: Users can save, retrieve, update, and delete Python scripts for reuse without re-typing.

**Independent Test**: Call CRUD endpoints to save script, retrieve it, update it, and delete it.

### Implementation for User Story 3

- [ ] T025 [US3] Create custom_scripts table migration in database/migrations/create_custom_scripts_table.sql
- [ ] T026 [US3] Create CustomScript model in app/models/custom_script.py
- [ ] T027 [US3] Implement CRUD service methods (save, retrieve, update, delete) in app/models/custom_script.py
- [ ] T028 [US3] Add validation for script code syntax in app/models/custom_script.py
- [ ] T029 [US3] Implement POST /api/custom-calculations/scripts endpoint in app/routes/custom_calculation.py
- [ ] T030 [US3] Implement GET /api/custom-calculations/scripts (list all) endpoint in app/routes/custom_calculation.py
- [ ] T031 [US3] Implement GET /api/custom-calculations/scripts/{id} endpoint in app/routes/custom_calculation.py
- [ ] T032 [US3] Implement PUT /api/custom-calculations/scripts/{id} endpoint in app/routes/custom_calculation.py
- [ ] T033 [US3] Implement DELETE /api/custom-calculations/scripts/{id} endpoint in app/routes/custom_calculation.py
- [ ] T034 [US3] Update POST /api/custom-calculations/execute to accept script_id parameter in app/routes/custom_calculation.py
- [ ] T035 [US3] Implement script loading from database when script_id provided in app/routes/custom_calculation.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Batch Processing (Priority: P2)

**Goal**: Support executing scripts against multiple stocks in single API call.

**Independent Test**: Submit script with array of 200 stock symbols, receive all calculated values.

### Implementation for User Story 4

- [ ] T036 [US4] Implement batch stock data fetching from database in app/routes/custom_calculation.py
- [ ] T037 [US4] Add validation for maximum 200 stocks per request in app/routes/custom_calculation.py
- [ ] T038 [US4] Implement result aggregation for multiple stocks in app/routes/custom_calculation.py
- [ ] T039 [US4] Add error handling for invalid stock symbols in app/routes/custom_calculation.py
- [ ] T040 [US4] Return null/error per symbol when some stocks fail in app/routes/custom_calculation.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T041 [P] Add comprehensive logging for all API requests in app/routes/custom_calculation.py
- [ ] T042 [P] Add performance monitoring for script execution time in app/services/sandbox_executor.py
- [ ] T043 [P] Update API documentation in README.md with new endpoints
- [ ] T044 Code cleanup and refactoring in app/routes/custom_calculation.py
- [ ] T045 Code cleanup and refactoring in app/services/sandbox_executor.py
- [ ] T046 [P] Review and optimize database queries in app/routes/custom_calculation.py
- [ ] T047 Add request/response logging for debugging in app/routes/custom_calculation.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Enhances security for US1
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Extends US1 batch processing capability

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks (T004-T010) can run in parallel within Phase 2
- Once Foundational phase completes, user stories can start in parallel (if team capacity allows)
- User Story 2 security tests (T019-T022) marked [P] can run in parallel
- Polish tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Core endpoint implementation
Task: T011-T014 [US1] - Create endpoint and basic functionality
Task: T015-T016 [US1] - Integrate execution and response formatting
Task: T017-T018 [US1] - Error handling and blueprint registration

# All US1 tasks must complete in order (endpoint depends on integration)
```

---

## Parallel Example: User Story 2

```bash
# Security tests can be done in parallel
Task: T019 [US2] Test imports blocking
Task: T020 [US2] Test file operations blocking
Task: T021 [US2] Test network operations blocking
Task: T022 [US2] Test system calls blocking

# Then implement verification
Task: T023-T024 [US2] - Verify and log security violations
```

---

## Parallel Example: User Story 3

```bash
# Database setup can proceed independently
Task: T025-T028 [US3] - Database schema and model
Task: T029-T033 [US3] - CRUD endpoints (can be parallelized)
Task: T034-T035 [US3] - Execute endpoint integration
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T010) ⚠️ CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T011-T018)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core functionality)
   - Developer B: User Story 2 (security) OR User Story 3 (script management)
   - Developer C: User Story 4 (batch processing)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

