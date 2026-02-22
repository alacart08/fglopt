# AGENTS.md

This file defines how automated agents (e.g., Codex web) should operate within the `fglopt` repository.

---

# Project Overview

`fglopt` is a research-stage Python project for topology optimization and functionally graded lattice generation.

Current implemented components:

* `ConfigLoader` (YAML parsing + validation)
* `DomainMesh` (2D structured quad mesh + visualization)
* REPL interface (`./fglopt`)
* Unit tests using `pytest`

Not yet implemented:

* Full TopologyOptimizer
* FEA solver
* Density update loop (SIMP)
* Lattice generation
* STL export

Agents should assume this is an actively evolving architecture.

---

# Development Environment

Python version: 3.10+

Virtual environment is required:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Tests must pass using:

```bash
PYTHONPATH=src pytest
```

The CLI can be run using:

```bash
export PYTHONPATH=src
./fglopt
```

---

# Project Structure

```
src/
  fglopt/
    mesh/
    utils/
    optimization/
    main.py

tests/
requirements.txt
pyproject.toml
```

All Python source code lives under `src/fglopt/`.

Agents must respect the `src` layout and not move modules outside of it.

---

# Coding Rules

1. Do NOT modify `.venv/`, `__pycache__/`, `.pytest_cache/`, or generated artifacts.
2. Do NOT reformat unrelated files.
3. Keep changes minimal and scoped to the requested task.
4. Maintain clear, well-commented code.
5. Prefer explicit typing where reasonable.
6. Do not introduce new heavy dependencies without justification.

---

# Testing Requirements

Any functional code changes must:

* Pass all existing tests
* Add new tests if behavior changes
* Avoid breaking public interfaces unless explicitly requested

All tests must pass with:

```bash
PYTHONPATH=src pytest
```

---

# Visualization Policy

Mesh plotting must:

* Use matplotlib
* Gracefully handle non-interactive backends
* Save output to disk if no GUI backend is available

Do not hard-code system-specific backends unless necessary.

---

# Architectural Intent

Long-term architecture goal:

```
ConfigLoader → TopologyOptimizer → DomainMesh → FEASolver → Density Field → LatticeGenerator → STL Export
```

The `TopologyOptimizer` should own the mesh and density field.

Keep architecture modular and extensible for future 3D and lattice work.

---

# Preferred Development Pattern

When implementing new features:

1. Add minimal working structure
2. Write or update tests
3. Ensure CLI integration if relevant
4. Keep commits small and focused

---

# Agent Behavior Expectations

Agents should:

* Ask for clarification if requirements are ambiguous
* Avoid speculative refactors
* Prefer incremental changes over large rewrites
* Preserve current working behavior

This project is research-oriented and iterative.

Stability and clarity are preferred over cleverness.

## Living Plan Alignment

Agents must follow the living implementation phases in `docs/fea_plan.md`:

* Read `docs/fea_plan.md` before implementing any FEA phase work.
* Implement only the specifically requested phase scope.
* Update the corresponding phase status in `docs/fea_plan.md` when phase work is completed.
