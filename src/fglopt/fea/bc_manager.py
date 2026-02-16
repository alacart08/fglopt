from __future__ import annotations

import numpy as np

from fglopt.mesh.domain_mesh import DomainMesh
from fglopt.utils.config_loader import ConfigLoader


class BCManager:
    """
    Boundary-condition manager for 2D, 2-DOF-per-node FE models.

    DOF mapping rule used throughout this class:
    - ux(node i) -> dof 2*i
    - uy(node i) -> dof 2*i + 1

    Expected YAML structure under `boundary_conditions`:

    ```yaml
    boundary_conditions:
      constraints:
        - selector: left_edge
          dofs: [ux, uy]
        - nodes: [0, 3]
          dofs: [ux]
      loads:
        point:
          - node: 5
            fx: 0.0
            fy: -100.0
        edge:
          - selector: top_edge
            dof: uy
            magnitude: -300.0
    ```

    Edge loads are treated as *total* force over the selected node set and are
    distributed uniformly: each selected node receives
    `magnitude / n_selected_nodes` in the requested DOF/component.
    """

    def __init__(self, config: ConfigLoader):
        self.config = config

    def get_constrained_dofs(self, mesh: DomainMesh) -> np.ndarray:
        """Return sorted unique constrained DOF indices as an integer array."""
        constraints = self.config.get_nested("boundary_conditions", "constraints", default=[])
        constrained: set[int] = set()

        for item in constraints:
            selected_nodes = self._resolve_selector(mesh, item)
            dofs = item.get("dofs", [])

            for node in selected_nodes:
                for dof_name in dofs:
                    constrained.add(self._node_dof_to_global(node, dof_name))

        return np.array(sorted(constrained), dtype=int)

    def build_force_vector(self, mesh: DomainMesh) -> np.ndarray:
        """Build and return the global force vector with shape (2 * n_nodes,)."""
        f = np.zeros(mesh.n_nodes * 2, dtype=float)
        loads = self.config.get_nested("boundary_conditions", "loads", default={})

        for point in loads.get("point", []):
            node = int(point["node"])

            if "fx" in point:
                f[self._node_dof_to_global(node, "ux")] += float(point["fx"])
            if "fy" in point:
                f[self._node_dof_to_global(node, "uy")] += float(point["fy"])

        for edge in loads.get("edge", []):
            selected_nodes = self._resolve_selector(mesh, edge)
            if not selected_nodes:
                continue

            magnitude = float(edge["magnitude"])
            dof_name = edge.get("dof")
            if dof_name is None:
                component = edge.get("component")
                if component == "x":
                    dof_name = "ux"
                elif component == "y":
                    dof_name = "uy"
                else:
                    raise ValueError("Edge load must define `dof` or `component` (x/y).")

            nodal_value = magnitude / float(len(selected_nodes))
            # Uniform edge load distribution strategy:
            # total user-provided magnitude is split equally across every selected node.
            for node in selected_nodes:
                f[self._node_dof_to_global(node, dof_name)] += nodal_value

        return f

    def _resolve_selector(self, mesh: DomainMesh, item: dict) -> list[int]:
        """Resolve selector-based or explicit-node selection into global node ids."""
        if "nodes" in item:
            return [int(n) for n in item["nodes"]]

        selector = item.get("selector")
        if selector is None:
            raise ValueError("Boundary condition entry must define `selector` or `nodes`.")

        tol = 1e-12
        xs = mesh.node_coords[:, 0]
        ys = mesh.node_coords[:, 1]

        if selector == "left_edge":
            return np.where(np.isclose(xs, 0.0, atol=tol))[0].tolist()
        if selector == "right_edge":
            return np.where(np.isclose(xs, mesh.lx, atol=tol))[0].tolist()
        if selector == "bottom_edge":
            return np.where(np.isclose(ys, 0.0, atol=tol))[0].tolist()
        if selector == "top_edge":
            return np.where(np.isclose(ys, mesh.ly, atol=tol))[0].tolist()

        raise ValueError(f"Unsupported selector: {selector}")

    @staticmethod
    def _node_dof_to_global(node: int, dof_name: str) -> int:
        """Map node id and local DOF name to global DOF index."""
        if dof_name == "ux":
            return 2 * int(node)
        if dof_name == "uy":
            return (2 * int(node)) + 1
        raise ValueError(f"Unsupported DOF name: {dof_name}")
