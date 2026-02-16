import textwrap

import numpy as np

from fglopt.fea.bc_manager import BCManager
from fglopt.mesh.domain_mesh import DomainMesh
from fglopt.utils.config_loader import ConfigLoader


def _cfg(tmp_path, bc_block: str) -> ConfigLoader:
    content = f"""
    input_stl: "example.stl"
    mesh_resolution: 20
    volume_fraction: 0.4
    material:
      E: 210e9
      nu: 0.3
    boundary_conditions:
{textwrap.indent(textwrap.dedent(bc_block).strip(), '      ')}
    """
    path = tmp_path / "config.yaml"
    path.write_text(textwrap.dedent(content))
    return ConfigLoader(str(path))


def test_get_constrained_dofs_selector_and_explicit_nodes(tmp_path):
    cfg = _cfg(
        tmp_path,
        """
        constraints:
          - selector: left_edge
            dofs: [ux, uy]
          - selector: top_edge
            dofs: [uy]
          - nodes: [4]
            dofs: [ux]
        loads: {}
        """,
    )
    mesh = DomainMesh(nx=2, ny=2, lx=2.0, ly=2.0)
    bcm = BCManager(cfg)

    constrained = bcm.get_constrained_dofs(mesh)

    # left_edge nodes => [0, 3, 6] -> dofs {0,1,6,7,12,13}
    # top_edge nodes => [6,7,8] with uy -> {13,15,17}
    # explicit node 4 ux -> {8}
    expected = np.array(sorted({0, 1, 6, 7, 8, 12, 13, 15, 17}), dtype=int)
    assert np.array_equal(constrained, expected)


def test_build_force_vector_point_loads(tmp_path):
    cfg = _cfg(
        tmp_path,
        """
        constraints: []
        loads:
          point:
            - node: 4
              fx: 10.0
              fy: -5.0
            - node: 8
              fy: 2.5
        """,
    )
    mesh = DomainMesh(nx=2, ny=2, lx=2.0, ly=2.0)
    bcm = BCManager(cfg)

    f = bcm.build_force_vector(mesh)

    assert f.shape == (2 * mesh.n_nodes,)
    assert np.isclose(f[2 * 4], 10.0)
    assert np.isclose(f[2 * 4 + 1], -5.0)
    assert np.isclose(f[2 * 8 + 1], 2.5)


def test_build_force_vector_edge_load_is_uniform_and_conservative(tmp_path):
    cfg = _cfg(
        tmp_path,
        """
        constraints: []
        loads:
          edge:
            - selector: right_edge
              dof: uy
              magnitude: -90.0
            - nodes: [0, 1, 2]
              dof: ux
              magnitude: 30.0
        """,
    )
    mesh = DomainMesh(nx=2, ny=2, lx=2.0, ly=2.0)
    bcm = BCManager(cfg)

    f = bcm.build_force_vector(mesh)

    right_nodes = [2, 5, 8]
    right_node_forces = [f[2 * n + 1] for n in right_nodes]
    assert np.allclose(right_node_forces, [-30.0, -30.0, -30.0])
    assert np.isclose(sum(right_node_forces), -90.0)

    bottom_nodes = [0, 1, 2]
    bottom_node_forces = [f[2 * n] for n in bottom_nodes]
    assert np.allclose(bottom_node_forces, [10.0, 10.0, 10.0])
    assert np.isclose(sum(bottom_node_forces), 30.0)
