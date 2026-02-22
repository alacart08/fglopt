import textwrap

from fglopt.fea.bc_manager import BCManager
from fglopt.fea.visualization import visualize_boundary_conditions
from fglopt.mesh.domain_mesh import DomainMesh
from fglopt.utils.config_loader import ConfigLoader


def _write_config(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        textwrap.dedent(
            """
            input_stl: "example.stl"
            mesh_resolution: 4
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
                  magnitude: -1.0
            """
        )
    )
    return ConfigLoader(str(path))


def test_visualize_boundary_conditions_saves_artifact_in_headless(tmp_path, monkeypatch):
    config = _write_config(tmp_path)
    mesh = DomainMesh(nx=4, ny=4, lx=1.0, ly=1.0)
    bc_manager = BCManager(config)

    output_path = tmp_path / "artifacts" / "bc_overlay.png"
    monkeypatch.setattr("fglopt.fea.visualization._has_gui_backend", lambda: False)

    artifact = visualize_boundary_conditions(
        bc_manager,
        mesh,
        show=True,
        output_path=output_path,
    )

    assert artifact == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0
