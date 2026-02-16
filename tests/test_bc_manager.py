import textwrap

import numpy as np

from fglopt.fea.bc_manager import BCManager
from fglopt.mesh.domain_mesh import DomainMesh
from fglopt.utils.config_loader import ConfigLoader


def _write_config(tmp_path, content: str):
    path = tmp_path / "config.yaml"
    path.write_text(textwrap.dedent(content))
    return ConfigLoader(str(path))


def test_get_constrained_dofs_left_edge_xy(tmp_path):
    config = _write_config(
        tmp_path,
        """
        input_stl: "example.stl"
        mesh_resolution: 2
        volume_fraction: 0.4
        material:
          E: 210e9
          nu: 0.3
        boundary_conditions:
          fixed:
            - selector: left_edge
              dofs: ["x", "y"]
        """,
    )
    mesh = DomainMesh(nx=2, ny=1, lx=2.0, ly=1.0)

    constrained = BCManager(config).get_constrained_dofs(mesh)

    # Left edge nodes for this mesh are [0, 3].
    expected = np.array([0, 1, 6, 7], dtype=int)
    assert np.array_equal(constrained, expected)


def test_build_force_vector_point_load_to_x_dof(tmp_path):
    config = _write_config(
        tmp_path,
        """
        input_stl: "example.stl"
        mesh_resolution: 2
        volume_fraction: 0.4
        material:
          E: 210e9
          nu: 0.3
        boundary_conditions:
          loads:
            - type: point
              nodes: [2]
              direction: x
              magnitude: 5.0
        """,
    )
    mesh = DomainMesh(nx=2, ny=1, lx=2.0, ly=1.0)

    force = BCManager(config).build_force_vector(mesh)

    assert force.shape == (mesh.n_nodes * 2,)
    assert force[4] == 5.0  # node 2 x-DOF = 2 * 2
    assert np.count_nonzero(force) == 1


def test_build_force_vector_edge_load_distributes_total_magnitude(tmp_path):
    config = _write_config(
        tmp_path,
        """
        input_stl: "example.stl"
        mesh_resolution: 2
        volume_fraction: 0.4
        material:
          E: 210e9
          nu: 0.3
        boundary_conditions:
          loads:
            - type: edge
              selector: right_edge
              direction: y
              magnitude: -9.0
        """,
    )
    mesh = DomainMesh(nx=2, ny=2, lx=2.0, ly=2.0)

    force = BCManager(config).build_force_vector(mesh)

    # Right-edge nodes are [2, 5, 8], y-DOFs are [5, 11, 17].
    loaded_dofs = [5, 11, 17]
    expected_nodal_force = -3.0

    for dof in loaded_dofs:
        assert force[dof] == expected_nodal_force

    assert np.isclose(force[loaded_dofs].sum(), -9.0)
    assert np.count_nonzero(force) == len(loaded_dofs)
