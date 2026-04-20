# ADR-004: Verification Harness

## Status

Accepted

## Context

AI-assisted development is becoming a core part of the workflow. Coding agents generate code faster than humans can review line-by-line. The codebase already has linting (Ruff, ESLint), type checking (Pyright, TypeScript), and testing (pytest, Vitest) configured — but none of these run automatically. The CI pipeline deploys on push to `main` with zero verification. `make check` is documented but the Makefile target does not exist.

Without automated enforcement, the existing quality tools are voluntary. As AI-generated code increases in volume, voluntary checks are insufficient.

Harness engineering literature (Anthropic, Martin Fowler, LangChain) converges on a principle: **computational sensors first**. Deterministic checks — linters, type checkers, test suites, architecture constraints — are cheap, fast, and reliable. They form the backbone of a verification layer. Inferential checks (LLM-as-judge, AI code review) layer on top but cannot replace them.

## Decision

Introduce a layered verification harness with three enforcement points:

1. **Local hooks (Lefthook)** — pre-commit runs linters on staged files; pre-push runs type checkers and tests. Parallel execution, polyglot-native, no root `package.json` required.

2. **CI gate (GitHub Actions)** — lint + format + typecheck + test + audit must pass before deploy. PRs get the same checks. Deploy to Hetzner only triggers after all checks succeed on `main`.

3. **Architecture enforcement** — import-linter (backend) checks that the domain layer never imports infrastructure, including transitive dependencies. eslint-plugin-boundaries (frontend) enforces import rules between element types.

Supporting tools:
- `pnpm audit` / `uv audit` for dependency vulnerability scanning (built-in, zero config)
- Dependabot for automated upgrade PRs (pip, npm, Docker base images, Actions)
- `make check` as the single command to run all verification locally

### Tool choices

| Need | Tool | Why |
|------|------|-----|
| Git hooks | Lefthook | Polyglot monorepo, no root `package.json`, parallel execution |
| Backend arch guard | import-linter | Transitive dependency checking, config-driven, mature |
| Frontend arch guard | eslint-plugin-boundaries | ESLint v9 compatible, purpose-built for import rules |
| Dep scanning | `pnpm audit` + `uv audit` | Built-in, zero dependencies |
| Upgrade PRs | Dependabot | Free, covers pip/npm/Docker/Actions |

## Consequences

**Easier:**
- Every push to `main` is verified before deploy — no broken deploys from unchecked code
- AI-generated code goes through the same gates as human code
- Architecture rules are enforced by tooling, not just documentation
- `make check` gives a single confidence signal before committing
- Dependency vulnerabilities surface automatically

**More difficult:**
- Developers must install Lefthook locally (`brew install lefthook && make hooks`)
- CI pipeline adds ~2-3 minutes before deploy
- import-linter and eslint-plugin-boundaries add two new dev dependencies
- Hooks can be bypassed with `--no-verify` (but CI catches it)
