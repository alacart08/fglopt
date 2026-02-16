# FGLopt Structural FEA Living Plan

## Objective

Implement a minimal, clean, and extensible linear elastic finite element solver (initially 2D) capable of computing structural compliance for topology optimization, with an architecture intended to extend to 3D.

This solver will support a structured quadrilateral (Q4) mesh—where "Q" denotes a quadrilateral finite element and "4" indicates four nodes per element using bilinear shape functions—and serve as the mechanics engine for future SIMP-based topology optimization. SIMP stands for Solid Isotropic Material with Penalization, a density-based topology optimization method in which each element is assigned a material density variable (between 0 and 1) that scales its stiffness using a penalized power law to encourage clear solid–void designs.

---

# Design Decisions (Locked In)

* Element type: Bilinear Q4 (4-node quad)
* Dimensionality: 2D
* Assumption: Plane stress
* Material: Linear isotropic elasticity
* Assembly: Sparse global stiffness matrix (scipy.sparse)
* Solver: Direct sparse solve (scipy.sparse.linalg.spsolve)

---

# Architecture Overview

Modules to be introduced:

src/fglopt/fea/
element.py        # Q4 stiffness matrix
assembler.py      # Global stiffness assembly
solver.py         # Ku = F solve + BC application
bc_manager.py     # Boundary condition handling

Existing modules used:

* mesh/domain_mesh.py
* utils/config_loader.py
* main.py (REPL integration)

---

# Phase 1 — Boundary Condition Definition

## Goals

* Extend YAML schema to support:

  * Fixed supports using simple selectors (e.g., `left_edge`, `bottom_edge`, or an explicit node list). These will ultimately map to *constrained DOFs* (e.g., fixing both x and y displacement on selected nodes).
  * Loads defined either as:

    * Point loads (apply a force to a specific node/s and direction), or
    * Edge loads (apply a distributed load along an edge, which the BC layer converts into equivalent nodal forces).
* Implement BCManager:

  * Map geometric selectors → node sets → DOF indices (e.g., node_id → (2*node_id, 2*node_id+1) for x/y DOFs in 2D).
  * Build the global force vector F with correct DOF placement and sign conventions.
  * Identify constrained DOFs for Dirichlet conditions, and provide them in a form the solver can apply (e.g., a list/array of fixed DOF indices, optionally with prescribed values such as 0).

## Example YAML Schema

Below is a minimal cantilever benchmark example for Phase 1:

```yaml
input_stl: examples/cant_beam.stl
mesh_resolution: 40
length_x: 2.0
length_y: 1.0

material:
  E: 210e9
  nu: 0.3

boundary_conditions:
  fixed:
    - selector: left_edge
      dofs: ["x", "y"]   # fix both ux and uy

  loads:
    - type: edge
      selector: right_edge
      direction: y
      magnitude: -1.0
```

### Interpretation Rules

* `selector` refers to geometric queries on the structured mesh (e.g., nodes where x = 0 → left_edge).
* `dofs` determines which displacement components are constrained.
* Edge loads are converted internally into equivalent nodal forces.
* Force sign convention: positive x = right, positive y = upward.

This schema keeps the BC definition geometric and mesh-independent, which makes it extensible to 3D later.

## Deliverables

* bc_manager.py

  * Class: `BCManager`
  * Construction:

    * `BCManager(config: ConfigLoader)` (stores BC/load definitions from the YAML)
  * Public API:

    * `build_force_vector(mesh) -> np.ndarray`  # uses stored config to create F
    * `get_constrained_dofs(mesh) -> np.ndarray`  # uses stored config to find fixed DOFs
    * (optional, later) `build_body_force_vector(mesh, density, g) -> np.ndarray`  # gravity/body forces
  * Responsibilities:

    * Parse boundary condition section of config
    * Convert geometric selectors (e.g., `left_edge`) into node index sets
    * Map node indices to global DOF indices using the rule:

      * dof_x = 2 * node_id
      * dof_y = 2 * node_id + 1
    * Construct the global force vector F of size (total_dofs,)
    * Return constrained DOF indices for Dirichlet conditions

* Unit tests validating:

  * Correct DOF selection:

    * Fixed left edge selects expected number of DOFs
    * DOF indices match 2*node_id mapping convention
  * Correct force placement:

    * Force applied to correct DOF index (x vs y)
    * Correct sign convention (positive x right, positive y up)
    * Resulting force vector has correct length and sparsity pattern

Status: NOT STARTED

---

# Phase 2 — Element Stiffness (Q4)

## Goals

* Implement Q4 element stiffness matrix
* Use plane stress constitutive matrix
* Support arbitrary element dimensions (lx, ly)

## Deliverables

* element.py
* Unit test:

  * Symmetry of element stiffness matrix
  * Positive semi-definiteness (basic check)

Status: NOT STARTED

---

# Phase 3 — Global Assembly

## Goals

* Assemble sparse global stiffness matrix K
* Use mesh connectivity from DomainMesh
* Map local element DOFs → global DOFs

## Deliverables

* assembler.py
* Unit tests:

  * Correct global matrix size
  * Nonzero pattern reasonable

Status: NOT STARTED

---

# Phase 4 — Linear Solve (Ku = F)

## Goals

* Apply Dirichlet BCs
* Modify K and F accordingly
* Solve for displacement vector u

## Deliverables

* solver.py
* Unit tests:

  * Solution exists for cantilever case
  * No singular matrix errors

Status: NOT STARTED

---

# Phase 5 — Compliance Computation

## Goals

* Compute compliance: C = F^T u
* Return scalar objective value

## Deliverables

* Compliance function (likely in solver or optimizer layer)
* Unit test:

  * Compliance > 0

Status: NOT STARTED

---

# Phase 6 — REPL Integration

## Goals

* Add command: run fea
* Load config
* Build mesh
* Apply BCs
* Solve
* Print:

  * Compliance
  * Maximum displacement magnitude

## Deliverables

* main.py update
* Manual smoke test

Status: NOT STARTED

---

# Future Extensions (Not in Scope Yet)

* Density-dependent stiffness (SIMP)
* Sensitivity analysis
* Dynamic meshing
* 3D elements
* Modal analysis (vibration constraints)
* Lattice homogenization coupling

---

# Acceptance Criteria for FEA Milestone

* `pytest` passes
* `run fea` executes without error
* Cantilever benchmark produces reasonable displacement pattern
* Compliance printed to console

---

# Notes

This is a minimal mechanics foundation. Topology optimization will wrap around this solver.

The solver must remain modular so that density-based material scaling can later modify element stiffness without refactoring the entire system.

---

# Mathematical Appendix

## 1. Governing Equation (Linear Elasticity)

The finite element system solves the linear static equilibrium equation:

K u = F

Where:

* K = global stiffness matrix
* u = global displacement vector
* F = global force vector

After applying Dirichlet boundary conditions (fixed DOFs), the reduced system is solved for u.

---

## 2. Q4 Bilinear Element

A Q4 element is a 4-node quadrilateral element using bilinear shape functions.

Each node has 2 degrees of freedom in 2D (u_x, u_y).

In natural coordinates (ξ, η) ∈ [-1,1], the shape functions are:

N1 = 1/4 (1 - ξ)(1 - η)
N2 = 1/4 (1 + ξ)(1 - η)
N3 = 1/4 (1 + ξ)(1 + η)
N4 = 1/4 (1 - ξ)(1 + η)

The element stiffness matrix is computed as:

K_e = ∫_Ω (B^T D B) dΩ

Where:

* B = strain-displacement matrix
* D = constitutive (material) matrix
* Ω = element domain

For plane stress, the constitutive matrix is:

D = E/(1 - ν^2) * [[1, ν, 0],
[ν, 1, 0],
[0, 0, (1 - ν)/2]]

Numerical integration (e.g., 2×2 Gauss quadrature) is typically used.

---

## 3. Global Assembly

The global stiffness matrix is assembled by mapping each element stiffness matrix K_e
into the global matrix using the element-to-global DOF connectivity.

For a mesh with N nodes in 2D:

Total DOFs = 2N

K has size (2N × 2N).

---

## 4. Compliance

Compliance is defined as:

C = F^T u

Physically, compliance represents total strain energy and measures structural flexibility.
Minimizing compliance corresponds to maximizing stiffness.

---

## 5. SIMP Method (Topology Optimization Foundation)

In SIMP (Solid Isotropic Material with Penalization), each element is assigned a density variable ρ_e ∈ [0,1].

The element stiffness is interpolated as:

E(ρ_e) = ρ_e^p E_0

Where:

* ρ_e = element density
* p = penalization factor (typically 3)
* E_0 = base material stiffness

The penalization term (p > 1) discourages intermediate densities by making partial material inefficient in stiffness contribution.

The topology optimization problem becomes:

Minimize: C(ρ)
Subject to: ∑ ρ_e V_e ≤ V*
0 ≤ ρ_e ≤ 1

Where V* is the allowed material volume fraction.

---

This appendix defines the mathematical foundation that the implementation phases will realize incrementally.
