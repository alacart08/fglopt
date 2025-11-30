import numpy as np


class DomainMesh:
    """
    Simple 2D structured rectilinear mesh.

    nx, ny are the number of elements in x and y.
    This creates (nx+1) * (ny+1) nodes on a unit-spaced grid for now.
    """


    def __init__(self, nx: int, ny: int, lx: float = 1.0, ly: float = 1.0):
        """
        Args:
            nx: number of elements in x-direction
            ny: number of elements in y-direction
            lx: physical length in x (for now just scales coordinates)
            ly: physical length in y
        """
        self.nx = nx
        self.ny = ny
        self.lx = lx
        self.ly = ly

        self.node_coords: np.ndarray | None = None  # shape (n_nodes, 2)
        self.element_nodes: np.ndarray | None = None  # shape (n_elems, 4)

        self._generate_nodes()
        self._generate_elements()


    @property
    def n_nodes(self) -> int:
        return (self.nx + 1) * (self.ny + 1)


    @property
    def n_elements(self) -> int:
        return self.nx * self.ny


    def _generate_nodes(self) -> None:
        """
        Generate node coordinates on a regular grid.

        Node ordering: row-major over y, then x, e.g.
        node_id = iy * (nx + 1) + ix
        """
        xs = np.linspace(0.0, self.lx, self.nx + 1)
        ys = np.linspace(0.0, self.ly, self.ny + 1)

        coords = []
        for iy in range(self.ny + 1):
            for ix in range(self.nx + 1):
                coords.append((xs[ix], ys[iy]))
        self.node_coords = np.array(coords, dtype=float)


    def _generate_elements(self) -> None:
        """
        Generate 4-node quadrilateral elements.

        Element ordering: row-major over y, then x.
        Element local node order: [bottom-left, bottom-right, top-right, top-left]
        stored as global node indices.
        """
        elems = []
        npx = self.nx + 1  # nodes per row

        for ey in range(self.ny):
            for ex in range(self.nx):
                n0 = ey * npx + ex           # bottom-left
                n1 = ey * npx + (ex + 1)     # bottom-right
                n2 = (ey + 1) * npx + (ex + 1)  # top-right
                n3 = (ey + 1) * npx + ex        # top-left
                elems.append((n0, n1, n2, n3))

        self.element_nodes = np.array(elems, dtype=int)


    def get_node_position(self, node_id: int) -> tuple[float, float]:
        """Return (x, y) coordinates for a node index."""
        if self.node_coords is None:
            raise RuntimeError("Mesh nodes not generated.")
        return tuple(self.node_coords[node_id])


    def get_element_nodes(self, elem_id: int) -> tuple[int, int, int, int]:
        """Return the 4 node indices of an element."""
        if self.element_nodes is None:
            raise RuntimeError("Mesh elements not generated.")
        return tuple(self.element_nodes[elem_id])