from __future__ import annotations

from typing import Iterable

import numpy as np

from fglopt.utils.config_loader import ConfigLoader


class BCManager:
    """Build constrained DOFs and force vectors from boundary-condition config.

    Phase 1 scope:
    - parse `boundary_conditions.fixed` into constrained displacement DOF indices
    - parse `boundary_conditions.loads` into a global nodal force vector

    Global DOF convention used throughout the project plan:
    - dof_x(node_id) = 2 * node_id
    - dof_y(node_id) = 2 * node_id + 1
    """

    _EDGE_SELECTORS = {"left_edge", "right_edge", "top_edge", "bottom_edge"}
    _DOF_INDEX = {"x": 0, "y": 1}

    def __init__(self, config: ConfigLoader):
        """Cache BC data from config for repeated mesh-based evaluation.

        Args:
            config: Parsed YAML configuration.
        """
        self._config = config
        bc_data = config.get("boundary_conditions", {}) or {}
        self._fixed = bc_data.get("fixed", []) or []
        self._loads = bc_data.get("loads", []) or []

    def get_constrained_dofs(self, mesh) -> np.ndarray:
        """Return sorted unique constrained global DOF indices for the mesh.

        Each fixed entry can target nodes via:
        - explicit `nodes: [...]`, or
        - geometric `selector: left_edge|right_edge|top_edge|bottom_edge`

        Then each requested dof (`x`, `y`) is converted to global DOF IDs using
        the 2-DOF-per-node mapping.
        """
        constrained: list[int] = []

        for entry in self._fixed:
            nodes = self._resolve_nodes(mesh, entry)
            dofs = entry.get("dofs", [])
            for dof in dofs:
                axis = self._normalize_dof(dof)
                base = self._DOF_INDEX[axis]
                constrained.extend([(2 * int(node)) + base for node in nodes])

        if not constrained:
            return np.array([], dtype=int)
        return np.array(sorted(set(constrained)), dtype=int)

    def build_force_vector(self, mesh) -> np.ndarray:
        """Build the global force vector F using configured nodal and edge loads.

        Load behavior:
        - point: apply full magnitude to every selected node in requested direction
        - edge: interpret magnitude as TOTAL load on selected edge and distribute
          it uniformly across selected nodes in requested direction

        Sign convention:
        - positive x: right
        - positive y: upward
        """
        force = np.zeros(mesh.n_nodes * 2, dtype=float)

        for load in self._loads:
            load_type = load.get("type", "point")
            direction = self._normalize_dof(load.get("direction"))
            dof_offset = self._DOF_INDEX[direction]
            magnitude = float(load.get("magnitude", 0.0))
            nodes = self._resolve_nodes(mesh, load)

            if not nodes:
                continue

            if load_type == "point":
                # If multiple nodes are selected for a point load definition,
                # each node receives the full specified magnitude.
                for node in nodes:
                    force[(2 * int(node)) + dof_offset] += magnitude
            elif load_type == "edge":
                # Edge load convention for Phase 1:
                # - `magnitude` is interpreted as the TOTAL force on the selected edge.
                # - That total is distributed uniformly to selected nodes so the nodal
                #   sum exactly equals the requested edge load magnitude.
                nodal_force = magnitude / len(nodes)
                for node in nodes:
                    force[(2 * int(node)) + dof_offset] += nodal_force
            else:
                raise ValueError(f"Unsupported load type: {load_type}")

        return force

    def _resolve_nodes(self, mesh, entry: dict) -> list[int]:
        """Resolve a BC/load entry into node IDs.

        Priority is explicit node list (`nodes`) when provided; otherwise,
        edge selector lookup is used.
        """
        if "nodes" in entry:
            return self._normalize_node_list(entry["nodes"], mesh.n_nodes)

        selector = entry.get("selector")
        if selector in self._EDGE_SELECTORS:
            return self._select_edge_nodes(mesh, selector)

        raise ValueError(f"Unsupported selector: {selector}")

    @staticmethod
    def _normalize_node_list(nodes: Iterable[int], n_nodes: int) -> list[int]:
        """Return sorted unique node IDs, validating bounds."""
        node_ids = sorted({int(node) for node in nodes})
        for node in node_ids:
            if node < 0 or node >= n_nodes:
                raise ValueError(f"Node index out of bounds: {node}")
        return node_ids

    def _select_edge_nodes(self, mesh, selector: str) -> list[int]:
        """Select nodes lying on the requested domain edge.

        The structured mesh coordinates are floating-point values; therefore,
        `np.isclose` is used instead of exact equality checks.
        """
        coords = mesh.node_coords
        if coords is None:
            raise RuntimeError("Mesh nodes not generated.")

        xs = coords[:, 0]
        ys = coords[:, 1]

        if selector == "left_edge":
            mask = np.isclose(xs, 0.0)
        elif selector == "right_edge":
            mask = np.isclose(xs, mesh.lx)
        elif selector == "bottom_edge":
            mask = np.isclose(ys, 0.0)
        elif selector == "top_edge":
            mask = np.isclose(ys, mesh.ly)
        else:
            raise ValueError(f"Unsupported selector: {selector}")

        return np.flatnonzero(mask).astype(int).tolist()

    def _normalize_dof(self, dof: str) -> str:
        """Validate and normalize direction/dof tokens to lowercase x/y."""
        if not isinstance(dof, str):
            raise ValueError(f"Invalid dof/direction value: {dof}")
        normalized = dof.lower()
        if normalized not in self._DOF_INDEX:
            raise ValueError(f"Unsupported dof/direction: {dof}")
        return normalized
