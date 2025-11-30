import numpy as np

from fglopt.mesh.domain_mesh import DomainMesh


def test_basic_sizes():
    mesh = DomainMesh(nx=3, ny=2, lx=3.0, ly=2.0)

    assert mesh.nx == 3
    assert mesh.ny == 2

    # (nx + 1) * (ny + 1) nodes = 4 * 3 = 12
    assert mesh.n_nodes == 12
    # nx * ny elements = 3 * 2 = 6
    assert mesh.n_elements == 6

    assert mesh.node_coords.shape == (mesh.n_nodes, 2)
    assert mesh.element_nodes.shape == (mesh.n_elements, 4)


def test_node_coordinates():
    mesh = DomainMesh(nx=3, ny=2, lx=3.0, ly=2.0)

    # xs = [0, 1, 2, 3], ys = [0, 1, 2]
    # Node ordering: row-major over y, then x

    # Node 0: (0, 0)
    assert np.allclose(mesh.get_node_position(0), (0.0, 0.0))

    # Node 3: (3, 0)
    assert np.allclose(mesh.get_node_position(3), (3.0, 0.0))

    # Node 4: (0, 1)
    assert np.allclose(mesh.get_node_position(4), (0.0, 1.0))

    # Last node: (3, 2)
    last_id = mesh.n_nodes - 1
    assert np.allclose(mesh.get_node_position(last_id), (3.0, 2.0))


def test_element_connectivity():
    mesh = DomainMesh(nx=3, ny=2, lx=3.0, ly=2.0)

    # npx = nx + 1 = 4
    # Element 0 (ey=0, ex=0):
    # n0 = 0, n1 = 1, n2 = 5, n3 = 4
    assert mesh.get_element_nodes(0) == (0, 1, 5, 4)

    # Element 1 (ey=0, ex=1):
    # n0 = 1, n1 = 2, n2 = 6, n3 = 5
    assert mesh.get_element_nodes(1) == (1, 2, 6, 5)

    # Last element (ey=1, ex=2) for nx=3, ny=2:
    # ey = ny - 1 = 1, ex = nx - 1 = 2
    # n0 = 1*4 + 2 = 6
    # n1 = 1*4 + 3 = 7
    # n2 = 2*4 + 3 = 11
    # n3 = 2*4 + 2 = 10
    last_elem_id = mesh.n_elements - 1
    assert mesh.get_element_nodes(last_elem_id) == (6, 7, 11, 10)