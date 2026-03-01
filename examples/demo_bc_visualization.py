#!/usr/bin/env python3
"""Demonstrate boundary-condition visualization with multiple load scenarios.

Run from the repo root:
    PYTHONPATH=src python examples/demo_bc_visualization.py

Generates a 2x2 panel image saved to artifacts/bc_demo.png showing four
classic structural loading scenarios on the same 20x10 mesh.
"""

from __future__ import annotations

import tempfile
import textwrap
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

from fglopt.fea.bc_manager import BCManager
from fglopt.fea.visualization import visualize_boundary_conditions
from fglopt.mesh.domain_mesh import DomainMesh
from fglopt.utils.config_loader import ConfigLoader


def _config_from_text(yaml_text: str) -> ConfigLoader:
    """Write YAML text to a temp file and return a ConfigLoader."""
    path = Path(tempfile.mktemp(suffix=".yaml"))
    path.write_text(textwrap.dedent(yaml_text))
    return ConfigLoader(str(path))


# ── Scenario 1: Cantilever beam ──────────────────────────────────────────
# Fixed left edge, distributed downward load on right edge.
cantilever_cfg = _config_from_text("""\
    input_stl: "example.stl"
    mesh_resolution: 20
    volume_fraction: 0.4
    material:
      E: 210e9
      nu: 0.3
    boundary_conditions:
      fixed:
        - selector: left_edge
          dofs: ["x", "y"]
      loads:
        - type: edge
          selector: right_edge
          direction: y
          magnitude: -5000.0
""")

# ── Scenario 2: Simply-supported beam with centre point load ─────────────
# Bottom-left corner pinned (x+y), bottom-right corner roller (y only),
# point load downward at top-centre node.
#
# On a 20x10 mesh (lx=2, ly=1), nodes per row = 21, rows = 11.
# Top-centre node: row 10 (top), column 10 (mid-x) → id = 10*21 + 10 = 220.
simply_supported_cfg = _config_from_text("""\
    input_stl: "example.stl"
    mesh_resolution: 20
    volume_fraction: 0.4
    material:
      E: 210e9
      nu: 0.3
    boundary_conditions:
      fixed:
        - nodes: [0]
          dofs: ["x", "y"]
        - nodes: [20]
          dofs: ["y"]
      loads:
        - type: point
          nodes: [220]
          direction: y
          magnitude: -8000.0
""")

# ── Scenario 3: Bridge-style loading ─────────────────────────────────────
# Both bottom corners pinned, uniform downward load across entire top edge.
bridge_cfg = _config_from_text("""\
    input_stl: "example.stl"
    mesh_resolution: 20
    volume_fraction: 0.4
    material:
      E: 210e9
      nu: 0.3
    boundary_conditions:
      fixed:
        - nodes: [0]
          dofs: ["x", "y"]
        - nodes: [20]
          dofs: ["x", "y"]
      loads:
        - type: edge
          selector: top_edge
          direction: y
          magnitude: -6000.0
""")

# ── Scenario 4: Mixed loading ────────────────────────────────────────────
# Bottom edge fully fixed, horizontal pull on right edge plus point load
# pushing down at the top-left corner.
#
# Top-left corner node: row 10, column 0 → id = 10*21 + 0 = 210.
mixed_cfg = _config_from_text("""\
    input_stl: "example.stl"
    mesh_resolution: 20
    volume_fraction: 0.4
    material:
      E: 210e9
      nu: 0.3
    boundary_conditions:
      fixed:
        - selector: bottom_edge
          dofs: ["x", "y"]
      loads:
        - type: edge
          selector: right_edge
          direction: x
          magnitude: 4000.0
        - type: point
          nodes: [210]
          direction: y
          magnitude: -7000.0
""")


def main() -> None:
    scenarios = [
        ("Cantilever Beam", cantilever_cfg),
        ("Simply-Supported + Point Load", simply_supported_cfg),
        ("Bridge Loading", bridge_cfg),
        ("Mixed: Pull + Point Load", mixed_cfg),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle("Boundary-Condition Visualization Demo", fontsize=14, fontweight="bold")

    for ax, (label, cfg) in zip(axes.flat, scenarios):
        mesh = DomainMesh(nx=20, ny=10, lx=2.0, ly=1.0)
        bc = BCManager(cfg)
        visualize_boundary_conditions(bc, mesh, title=label, ax=ax, show=False)

    fig.tight_layout(rect=[0, 0, 1, 0.95])

    output = Path("artifacts/bc_demo.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150)
    plt.close(fig)

    print(f"Saved demo image to {output.as_posix()}")

    # Also try showing interactively if a GUI backend is available.
    backend = matplotlib.get_backend().lower()
    interactive = {name.lower() for name in matplotlib.rcsetup.interactive_bk}
    if backend in interactive:
        # Re-render and show.
        fig2, axes2 = plt.subplots(2, 2, figsize=(14, 8))
        fig2.suptitle("Boundary-Condition Visualization Demo", fontsize=14, fontweight="bold")
        for ax, (label, cfg) in zip(axes2.flat, scenarios):
            mesh = DomainMesh(nx=20, ny=10, lx=2.0, ly=1.0)
            bc = BCManager(cfg)
            visualize_boundary_conditions(bc, mesh, title=label, ax=ax, show=False)
        fig2.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()


if __name__ == "__main__":
    main()
