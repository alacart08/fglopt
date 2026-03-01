# CLAUDE.md

This file guides AI assistants working in the `fglopt` repository. Read it before making any changes.

---

## Project Overview

`fglopt` is a research-stage Python toolkit for **topology optimization** and **functionally graded lattice (FGL) generation** targeting FDM 3D printing. The long-term pipeline is:

```
ConfigLoader → TopologyOptimizer → DomainMesh → FEASolver → Density Field → LatticeGenerator → STL Export
```

### Implementation Status

| Component | Status |
|---|---|
| `ConfigLoader` – YAML parsing and validation | **Complete** |
| `DomainMesh` – 2D structured Q4 quad mesh | **Complete** |
| `BCManager` – boundary condition definition | **Complete** (Phase 1) |
| `visualization.py` – BC/load overlay plots | **Complete** (Phase 1b) |
| REPL interface (`./fglopt`) | **Complete** |
| `element.py` – Q4 element stiffness matrix | Not started (Phase 2) |
| `assembler.py` – global stiffness assembly | Not started (Phase 3) |
| `solver.py` – Ku=F solve with Dirichlet BCs | Not started (Phase 4) |
| Compliance computation | Not started (Phase 5) |
| `run fea` REPL command | Not started (Phase 6) |
| SIMP topology optimizer | Not started |
| Lattice generation | Not started |
| STL export | Not started |

---

## Repository Structure

```
fglopt/
├── fglopt                        # Executable entry point (launches REPL)
├── config.yaml                   # Default/example configuration
├── requirements.txt              # Runtime + dev dependencies
├── pyproject.toml                # Package metadata and build config
├── AGENTS.md                     # Agent/developer guidelines
├── src/
│   └── fglopt/
│       ├── __init__.py
│       ├── main.py               # REPL command loop
│       ├── utils/
│       │   └── config_loader.py  # YAML config parsing and validation
│       ├── mesh/
│       │   └── domain_mesh.py    # 2D structured quad mesh generation
│       └── fea/
│           ├── bc_manager.py     # Boundary condition and load handling
│           └── visualization.py  # Matplotlib BC overlay plots
├── tests/
│   ├── test_config_loader.py
│   ├── test_domain_mesh.py
│   ├── test_bc_manager.py
│   ├── test_bc_visualization.py
│   └── test_main.py
├── docs/
│   ├── fea_plan.md               # Living FEA implementation plan (read before FEA work)
│   ├── architecture.md           # Architecture overview
│   └── fea_big_picture.md        # Non-technical FEA primer
└── examples/
    └── cant_beam.stl             # Cantilever beam example geometry
```

All Python source lives under `src/fglopt/`. Do **not** move modules outside this layout.

---

## Development Environment

**Python:** 3.11+

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Run the REPL:**
```bash
export PYTHONPATH=src
./fglopt
```

**Run tests:**
```bash
PYTHONPATH=src pytest
```

---

## Tech Stack

| Layer | Library |
|---|---|
| Array operations | NumPy ≥ 1.26 |
| Sparse matrices / solver | SciPy ≥ 1.11 |
| Visualization | matplotlib ≥ 3.x |
| Config parsing | PyYAML ≥ 6.0 |
| STL loading (planned) | trimesh ≥ 4.4 |
| Testing | pytest |
| Build | setuptools ≥ 68 + wheel |

Do not introduce heavy new dependencies without clear justification.

---

## Key Conventions

### DOF Mapping (2D plane stress)
```
dof_x(node) = 2 * node_id
dof_y(node) = 2 * node_id + 1
```
Total DOFs = 2 × number of nodes.

### Coordinate System
- x: right (positive)
- y: upward (positive)

### Mesh Ordering
- Nodes: row-major over y first, then x
- Elements: row-major Q4 quads

### Force Sign Convention
- Positive x → rightward force
- Positive y → upward force

### Typing
- Use explicit type hints (Python 3.10+ union syntax: `np.ndarray | None`)
- Type all public function signatures

### Error Handling
- Raise `ValueError` with descriptive messages for invalid configs
- Raise `FileNotFoundError` for missing files
- Validate at system boundaries (user input, YAML); trust internal guarantees

---

## YAML Config Schema

```yaml
input_stl: "examples/cant_beam.stl"
mesh_resolution: 40
length_x: 2.0
length_y: 1.0
volume_fraction: 0.4

material:
  E: 210e9    # Young's modulus (Pa)
  nu: 0.3     # Poisson's ratio

boundary_conditions:
  fixed:
    - selector: left_edge   # left_edge | right_edge | top_edge | bottom_edge
      dofs: ["x", "y"]      # which displacement components to fix
  loads:
    - type: edge            # "edge" or "point"
      selector: right_edge
      direction: y          # "x" or "y"
      magnitude: -1.0       # negative = downward
```

Edge selectors: `left_edge`, `right_edge`, `top_edge`, `bottom_edge` (geometric queries on the structured mesh).

---

## REPL Commands

| Command | Description |
|---|---|
| `load <file>` | Load a YAML config file |
| `plot mesh` | Display or save mesh visualization |
| `plot bc` | Display or save BC/load overlay |
| `run topo-opt` | Run topology optimization (stub) |
| `help` | Show available commands |
| `exit` | Quit |

---

## Visualization Policy

- Use **matplotlib** for all plots.
- Detect backend with `matplotlib.get_backend()`.
- If an interactive GUI backend is available → show window.
- If headless → save PNG to `artifacts/` directory (create it if absent).
- Never hard-code system-specific backends.
- Accept `ax` parameter in plot helpers to support subplot integration.

---

## Testing Conventions

- Framework: **pytest**
- Always run: `PYTHONPATH=src pytest`
- Use `tmp_path` fixture for temporary files.
- Use `monkeypatch` for mocking (e.g., matplotlib backend detection).
- Write helper functions in test files (`_write_yaml`, `_write_config`, etc.) to reduce duplication.
- Test names should describe behavior clearly.
- Any functional code change must:
  - Pass all existing tests
  - Add new tests if behavior changes
  - Not break public interfaces unless explicitly requested

---

## FEA Development Plan

**Before implementing any FEA phase work, read `docs/fea_plan.md`.**

Key locked-in design decisions:
- Element type: **bilinear Q4** (4-node quad, 2 DOFs per node)
- Dimensionality: **2D plane stress**
- Material: linear isotropic elasticity
- Stiffness assembly: **scipy.sparse** (CSR format)
- Solver: **scipy.sparse.linalg.spsolve** (direct sparse solve)

FEA module files to be introduced under `src/fglopt/fea/`:
- `element.py` — Q4 element stiffness matrix (`K_e = ∫ Bᵀ D B dΩ`, 2×2 Gauss quadrature)
- `assembler.py` — global stiffness assembly (local → global DOF mapping)
- `solver.py` — apply Dirichlet BCs, solve `Ku = F`, return `u`

When a phase is complete, **update the corresponding status in `docs/fea_plan.md`**.

---

## Coding Rules

1. **Do not** modify `.venv/`, `__pycache__/`, `.pytest_cache/`, or generated artifacts.
2. **Do not** reformat unrelated files.
3. Keep changes **minimal and scoped** to the requested task.
4. Prefer **incremental changes** over large rewrites.
5. Avoid speculative refactors.
6. Preserve current working behavior.
7. Stability and clarity are preferred over cleverness.

---

## Git Workflow

- All source is in the `src/` layout; keep it that way.
- Branch naming convention: `claude/<feature>` and `codex/<feature>`.
- Commits should be small and focused.
- Implement in this order: minimal working structure → tests → CLI integration → commit.

---

## Architectural Intent

The `TopologyOptimizer` will eventually own the mesh and density field. Keep all modules modular and extensible for future 3D support and lattice work. The SIMP density-stiffness interpolation (`E(ρ) = ρᵖ E₀`, p≈3) will wrap around the FEA solver without requiring solver refactoring.
