# FEA Big-Picture Primer (Manager-Friendly)

This short primer explains how finite element analysis (FEA) fits into `fglopt` and why the current Phase 1 work (boundary conditions) matters.

## 1) What problem FEA solves

In plain language, FEA predicts how a part behaves when it is pushed, pulled, or fixed in place.

Instead of solving physics for one giant shape directly, FEA:

1. Breaks the geometry into many small elements (a mesh)
2. Writes a small stiffness equation for each element
3. Assembles all element equations into one global system
4. Applies boundary conditions (supports + loads)
5. Solves for unknown displacements
6. Derives strain/stress and other performance quantities

For linear static structural analysis, the core system is typically:

`K u = F`

- `K`: global stiffness matrix (how hard it is to deform)
- `u`: nodal displacement vector (unknown movement)
- `F`: global force vector (external loads)

## 2) Why boundary conditions are a dedicated phase

Boundary conditions are where we encode **how the part is held** and **where forces are applied**.

Without correct boundary conditions, even a perfect solver gives meaningless answers.

Phase 1 in this repository creates a dedicated boundary-condition manager so this logic is:

- Explicit (easy to inspect)
- Testable (easy to validate)
- Separate from solver internals (modular architecture)

## 3) How this maps to current repository architecture

Current pipeline intent:

`ConfigLoader -> BCManager -> FE assembly/solver (future phases)`

- `ConfigLoader` reads YAML input.
- `BCManager` translates YAML support/load definitions into arrays needed for FEA assembly/solve:
  - constrained DOF indices
  - global force vector

This clean handoff avoids mixing user-input parsing with core numerical routines.

## 4) DOF mapping in this project

For a 2D structural mesh, each node has two displacement degrees of freedom (DOFs):

- x-direction displacement
- y-direction displacement

Global indexing convention:

- `dof_x(node_id) = 2 * node_id`
- `dof_y(node_id) = 2 * node_id + 1`

This convention is critical because every module (BC parsing, assembly, solver, post-processing) must agree on it.

## 5) Supports vs loads (business interpretation)

- **Supports/fixed DOFs** represent manufacturing or test-fixture constraints (what cannot move).
- **Loads** represent operating conditions (forces from service environment).

Both together define the scenario being simulated. If either is wrong, optimization decisions downstream can be wrong.

## 6) Point load vs edge load semantics

Current behavior implemented for Phase 1:

- **Point load**: applied directly to each selected node DOF.
- **Edge load**: interpreted as a **total force** over selected edge nodes and distributed uniformly among those nodes.

Why this matters:

- It preserves force conservation.
- It keeps YAML input concise for common edge-loading cases.

## 7) Why this matters for topology optimization later

Topology optimization repeatedly solves FEA while updating material density.

That means boundary conditions are reused every iteration. A robust, well-tested BC layer:

- Reduces debugging time during optimization development
- Prevents invalid load/support states from propagating
- Makes future extension (e.g., richer selectors or load types) safer

## 8) Practical takeaway for planning

Phase 1 is foundational infrastructure, not cosmetic work.

It ensures that when solver and optimization phases are expanded, the project already has a reliable way to represent real-world constraints and loading scenarios.

## 9) Why BC visualization is its own step

Boundary-condition mistakes are one of the most common FEA failure modes (wrong edge fixed, wrong load direction, or load applied to the wrong nodes).

Because of that, this repository treats BC visualization as a pre-solve validation step, with an explicit Phase 1b before global assembly and solve.

The goal is to make support/load intent visually checkable early, so configuration issues are caught before numerical debugging begins.
