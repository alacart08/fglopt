from pathlib import Path

from fglopt.main import plot_mesh_from_config
from fglopt.utils.config_loader import ConfigLoader


def _write_config(path: Path) -> None:
    path.write_text(
        """
input_stl: examples/cant_beam.stl
mesh_resolution: 4
volume_fraction: 0.4
material:
  E: 1.0
  nu: 0.3
""".strip()
    )


def test_plot_mesh_saves_file_for_non_interactive_backend(tmp_path, monkeypatch, capsys):
    cfg_path = tmp_path / "config.yaml"
    _write_config(cfg_path)

    output_path = tmp_path / "artifacts" / "mesh.png"
    config = ConfigLoader(str(cfg_path))

    monkeypatch.setattr("fglopt.main._has_gui_backend", lambda: False)

    plot_mesh_from_config(config, output_path=str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0

    out = capsys.readouterr().out
    assert f"Saved mesh plot to {output_path.as_posix()}." in out


def test_help_lists_plot_mesh(monkeypatch, capsys):
    from fglopt.main import launch_console

    commands = iter(["help", "exit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(commands))

    launch_console()

    out = capsys.readouterr().out
    assert "plot mesh" in out
