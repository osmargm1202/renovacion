# Root AGENTS Renovacion Mode Contract Plan

> **For agentic workers:** Use TDD. Write contract test first, observe RED because root `AGENTS.md` is missing, then add minimal `AGENTS.md`, run targeted GREEN, run full skill suite, commit only scoped files if all checks pass.

**Goal:** Add root `AGENTS.md` manual mode contract for Renovacion so repo clearly distinguishes developer mode from operator-only mode while keeping `.pi/skills/renovacion/` as source of truth.

**Approved contract summary:**
- Root `AGENTS.md` must contain literal line `developer_mode = true`.
- `.pi/skills/renovacion/` is source of truth.
- Preserve `.pi/skills/renovacion/proyectos/[id]/` for project artifacts.
- `developer_mode = true` allows modifying skill implementation areas under source-of-truth tree, including assets/lib/catalog/docs/tests, and requires TDD with RED → GREEN → REFACTOR.
- `developer_mode = false` is operator-only: gather missing client info, ask one focused question at a time, use `.pi/skills/renovacion/docs/contracts/input-json.md`, update `.pi/skills/renovacion/proyectos/[id]/input.json`, run calc/spec/memory, report outputs.
- `developer_mode = false` must prohibit modifying skill/assets/lib/catalog/docs/tests.
- Missing-info workflow must mention top-level keys `project`, `validation`, `areas`, `equipment`, `defaults_applied`.

## Task order

### 1. Contract test first
- Create `.pi/skills/renovacion/tests/test_agents_contract.py`.
- Test for:
  - root `AGENTS.md` exists
  - literal line `developer_mode = true`
  - source-of-truth path
  - preserved `proyectos/[id]/`
  - developer-mode mutation allowance with TDD/red-green-refactor
  - operator-only false-mode workflow
  - false-mode mutation prohibition
  - missing-info interview contract with one focused question at a time and input-json reference
- Run:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_agents_contract.py
```
- Expected RED: failure because `AGENTS.md` does not exist yet.

### 2. Minimal implementation
- Create root `AGENTS.md` with:
  - manual flag `developer_mode = true`
  - source-of-truth statement
  - project artifact preservation rule
  - developer mode contract
  - operator-only false mode contract
  - client calculation workflow
  - missing-info interview instructions

### 3. Verification
- Run targeted GREEN:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_agents_contract.py
```
- Run full suite:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
```
- If both pass, commit only:
  - `AGENTS.md`
  - `.pi/skills/renovacion/tests/test_agents_contract.py`
  - `docs/superpowers/plans/2026-04-25-root-agents-renovacion-mode-contract.md`
  - optional `pdd/root-agents-renovacion-mode-contract/build-progress`

## Constraints
- Do not edit project outputs or engines.
- Keep change additive.
- Follow RED → GREEN → REFACTOR.
- Report RED/GREEN evidence and commit hash.
