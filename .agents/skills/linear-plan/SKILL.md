---
name: linear-plan
description: Create a detailed phased implementation plan from a Linear issue. Use when the user asks for planning from a specific issue ID.
compatibility: Requires Linear MCP access and repository read access.
---

# Implementation Plan from Linear Issue

You are entering **planning mode**. You MUST NOT make any code changes, create files (other than the plan), or run destructive commands. Your only output is a plan document.

## Step 1: Fetch the Linear issue

Extract the issue ID from the user's prompt (for example `LIN-123`).

If the user did not provide an issue ID, ask for it and stop until they answer.

Use the `mcp__linear-server__get_issue` tool to fetch that issue. Extract:
- Title
- Description (user story, acceptance criteria, out of scope)
- Priority, labels, project, milestone

If the issue ID is invalid or not found, stop and inform the user.

## Step 2: Understand the codebase

Explore the repository to understand the current state relevant to the issue:
- Read CLAUDE.md for project conventions and architecture
- Identify the files, models, endpoints, pages, and components related to the feature
- Trace the data flow end-to-end (DB schema -> backend models -> API endpoints -> frontend types -> pages/components)
- Look for existing patterns, utilities, and code that can be reused

Be thorough. Read actual files, don't assume.

## Step 3: Ask clarifying questions

Before designing the plan, ask the user questions to resolve ambiguity:
- Scope boundaries: what's in, what's out
- Technical decisions that have multiple valid approaches
- Dependencies or constraints not obvious from the issue
- Anything vague in the acceptance criteria

Do NOT proceed to the plan until the user has answered your questions. Iterate if needed.

## Step 4: Design the phased plan

Structure the plan in implementation phases. Each phase should be independently deliverable and verifiable.

For each phase include:
- **Goal**: what this phase achieves
- **Changes**: specific files to create/modify with a description of what changes
- **Verification**: how to verify the phase is complete and correct

### Testing strategy (include where applicable)

Each phase should define its testing needs:

- **Backend unit tests**: service logic with fake repositories (follow existing pattern in `tests/test_catalog.py`)
- **Backend endpoint tests**: HTTP tests with `httpx.AsyncClient`
- **Frontend tests**: component and page tests with vitest
- **Functional/E2E validation**: manual or automated verification of the full user flow
- **Performance**: identify endpoints that handle significant data and note where response time matters (e.g., queries with JOINs, pages with heavy fetches)

Not every phase needs all test types. Be pragmatic: test what matters, skip what doesn't add value.

## Step 5: Write and save the plan

1. Write the plan to the plan mode file (managed by the plan mode system).
2. After the user approves via `ExitPlanMode`, immediately save the same content to `docs/plans/<feature-slug>/plan.md` in the repo (create the directory if needed). This is the canonical plan file that lives in the codebase. Use a kebab-case `<feature-slug>` derived from the issue title.

### Plan document structure

The plan must be written **in Spanish**. Use the following structure:

```markdown
# <Issue ID>: <Issue Title>

## Contexto
Why this change is needed.

## Estado actual
Relevant parts of the codebase today (key files, models, endpoints, schemas).

## Fases de implementación

### Fase 1: <name>
**Objetivo:** ...
**Cambios:**
- `path/to/file.py` — description of change
**Verificación:**
- [ ] ...

### Fase N: <name>
...

## Estrategia de testing
Summary of test coverage across phases.

## Preguntas abiertas
Any remaining uncertainties or decisions deferred to implementation.
```

## Rules

- Write the plan **in Spanish**.
- Be concise. Sacrifice grammar for clarity.
- Reference specific file paths and existing functions/patterns to reuse.
- Do NOT propose new abstractions when existing patterns work.
- Do NOT include code snippets unless critical for understanding the approach.
- The plan must be actionable: another developer (or AI agent) should be able to execute it without re-reading the full codebase.
