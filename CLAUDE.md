# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Scope

This is the **DataMonitor** PoC module — one of four independent modules for the SampleOrderSystem project. Its sole responsibility is the **모니터링 메뉴** (monitoring tool): a console-based administrator tool to inspect the current state of saved data in real time.

**In scope (this module only):**
- Order status counts by state: RESERVED / PRODUCING / CONFIRMED / RELEASE (REJECTED is excluded from monitoring)
- Per-sample inventory status with labels: 여유 (sufficient) / 부족 (insufficient) / 고갈 (depleted, qty=0)

**Out of scope for this module:** order creation, approval/rejection, production line management, release processing, sample CRUD — those belong to other PoC modules.

## Commands

```bash
# Run all tests
python -m pytest

# Run all tests with coverage report
python -m pytest --cov=. --cov-report=term-missing

# Run a single test file
python -m pytest tests/test_monitor.py -v

# Run a single test by name
python -m pytest tests/test_monitor.py::TestClassName::test_method_name -v
```

## Domain Model

**Order states** (from PRD):
- `RESERVED` — 주문 접수
- `REJECTED` — 주문 거절 (excluded from monitoring)
- `PRODUCING` — 재고 부족, 생산 중
- `CONFIRMED` — 출고 대기 중
- `RELEASE` — 출고 완료

**Sample attributes:** sample_id, name, avg_production_time, yield_rate (정상 수율 = 정상품/총생산)

**Inventory status labels** (monitoring display):
- `여유`: stock >= ordered quantity
- `부족`: stock < ordered quantity but > 0
- `고갈`: stock == 0

## TDD Workflow

All development follows strict **Red → Green → Refactor** with user approval gates between phases. Each phase must:
1. Update `PRD.md` with the phase plan before coding
2. Write failing tests first (RED) → get user approval
3. Implement minimum code to pass (GREEN) → get user approval
4. Refactor for quality (REFACTOR) → get user approval
5. Git push only after user approves the completed phase

Target test coverage: as close to 100% as possible.

## Available Agents

Use these agents at the appropriate moments in the workflow:

| Agent | When to invoke |
|-------|---------------|
| `planning-consistency-validator` | After updating PRD.md phases, to verify cross-document consistency |
| `tdd-ocp-implementer` | During RED→GREEN cycles to implement features test-first with OCP compliance |
| `code-quality-validator` | After each GREEN→REFACTOR cycle to validate test sufficiency, OCP, readability, SOLID |
| `prd-compliance-reviewer` | After completing a phase to verify implementation matches PRD requirements |

## Phase Gate Protocol

Before each Git push, confirm with the user. The push command is:
```bash
git add <specific files>
git commit -m "feat: <description>"
git push origin master
```

Never push without explicit user approval. PRD.md must be updated with phase status before pushing.
