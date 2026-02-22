from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt


def _has_gui_backend() -> bool:
    """Return True when matplotlib is using an interactive GUI backend."""
    backend = matplotlib.get_backend().lower()
    interactive_backends = {name.lower() for name in matplotlib.rcsetup.interactive_bk}
    return backend in interactive_backends


def visualize_boundary_conditions(
    bc_manager,
    mesh,
    title: str | None = None,
    ax=None,
    show: bool = True,
    output_path: str | Path = "artifacts/bc_overlay.png",
) -> str | Path | None:
    """Overlay fixed supports and loads on top of the mesh visualization.

    Returns the artifact path when saved in headless mode, otherwise None.
    """
    created_fig = False
    if ax is None:
        fig, ax = plt.subplots()
        created_fig = True
    else:
        fig = ax.figure

    mesh.plot(title=title or "Boundary Conditions", show=False, ax=ax)

    # Plot constrained support nodes.
    constrained_nodes: set[int] = set()
    for fixed in bc_manager._fixed:
        constrained_nodes.update(bc_manager._resolve_nodes(mesh, fixed))

    if constrained_nodes:
        node_ids = sorted(constrained_nodes)
        coords = mesh.node_coords[node_ids]
        ax.scatter(
            coords[:, 0],
            coords[:, 1],
            marker="s",
            c="tab:blue",
            s=36,
            label="supports",
            zorder=3,
        )

    # Plot loads as quiver arrows.
    load_xs: list[float] = []
    load_ys: list[float] = []
    load_us: list[float] = []
    load_vs: list[float] = []

    for load in bc_manager._loads:
        direction = bc_manager._normalize_dof(load.get("direction"))
        magnitude = float(load.get("magnitude", 0.0))
        nodes = bc_manager._resolve_nodes(mesh, load)
        if not nodes:
            continue

        nodal_magnitude = magnitude
        if load.get("type", "point") == "edge":
            nodal_magnitude = magnitude / len(nodes)

        for node in nodes:
            x, y = mesh.get_node_position(int(node))
            load_xs.append(x)
            load_ys.append(y)
            if direction == "x":
                load_us.append(nodal_magnitude)
                load_vs.append(0.0)
            else:
                load_us.append(0.0)
                load_vs.append(nodal_magnitude)

    if load_xs:
        ax.quiver(
            load_xs,
            load_ys,
            load_us,
            load_vs,
            angles="xy",
            scale_units="xy",
            scale=1,
            color="tab:red",
            label="loads",
            zorder=4,
        )

    if constrained_nodes or load_xs:
        ax.legend(loc="best")

    if show and _has_gui_backend() and created_fig:
        plt.show()
        return None

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    if created_fig:
        plt.close(fig)
    return output
