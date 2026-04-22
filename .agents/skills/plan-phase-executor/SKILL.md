---
name: plan-phase-executor
description: Execute a specific implementation phase from a plan in docs/plans, run corresponding validations, and update that phase verification checkboxes as tasks complete.
compatibility: Requires repository read/write access plus ability to run make, uv, and pnpm commands.
---

# Phase Executor from Plan

Use this skill when the user asks to implement a specific phase from an existing plan in `docs/plans/`.

## Required inputs

- Plan path (must be inside `docs/plans/`).
- Target phase by explicit identifier (`Phase N`).

If either input is missing, request it and do not start implementation.

## Workflow

### 1) Validate scope and locate phase

1. Verify the plan file exists and is inside `docs/plans/`.
2. Locate the exact requested phase (`### Phase N:` or `## Phase N:`).
3. If not found or ambiguous, stop and ask for confirmation.

### 2) Extract executable work

From the target phase, extract:

- `Changes` list.
- `Verification` checkboxes.

Do not modify or execute tasks from other phases.

### 3) Execute implementation task-by-task

Implement incrementally, prioritizing small and verifiable changes.

Rules:

- Reuse existing repository patterns.
- Do not introduce unnecessary abstractions.
- If design/scope is blocked, stop and ask the user for a decision.

### 4) Run validations by touched surface

Apply minimum validations based on phase change type:

- Backend domain/service/repo/router:
  - `make check`
  - `cd backend && uv run lint-imports`
- Frontend UI/routes/data fetch:
  - `make check`
- Dependency updates:
  - `make check`
  - `cd backend && uv run ruff format --check app tests && uv run lint-imports && uv audit`
  - `cd frontend && pnpm audit`
- Database migrations/schema:
  - `make db-init` on a running stack
  - smoke test affected flows
- Infra/deploy:
  - `make check`
  - validate impacted compose/deploy commands

If the phase touches multiple surfaces, run the union of validations.

### 5) Update plan progress

As tasks in the phase are completed:

1. Mark only existing `Verification` checkboxes in the target phase (`[ ]` -> `[x]`) when evidence is real.
2. Do not create new checkboxes.
3. Do not edit checkboxes from other phases.

If a verification item cannot be completed, leave it unchecked and report the blocker.

## Done criteria

A phase is considered complete when:

- Phase changes are implemented.
- Corresponding validations were executed.
- Verifiable `Verification` checkboxes are updated.

Deliver a final summary including:

- Modified files.
- Executed validations.
- Checked and pending checkboxes in the target phase.