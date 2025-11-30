import textwrap
import pytest

from fglopt.utils.config_loader import ConfigLoader


def _write_yaml(tmp_path, content: str):
    'Helper to write a temporary YAML config.'
    path = tmp_path / 'config.yaml'
    path.write_text(textwrap.dedent(content))

    return path


def test_load_valid_config(tmp_path):
    path = _write_yaml(
        tmp_path,
        """
        input_stl: "example.stl"
        mesh_resolution: 40
        volume_fraction: 0.4
        material:
            E: 210e9
            nu: 0.3
        """
    )

    cfg = ConfigLoader(str(path))

    assert cfg.get("input_stl") == "example.stl"
    assert cfg.get("mesh_resolution") == 40
    assert cfg.get("volume_fraction") == 0.4
    assert cfg.get_nested("material", "E") == '210e9'
    assert cfg.get_nested("material", "nu") == 0.3


def test_missing_required_top_level_keys_raises(tmp_path):
    # no volume_fraction
    path = _write_yaml(
        tmp_path,
        """
        input_stl: "example.stl"
        mesh_resolution: 40
        material:
          E: 210e9
          nu: 0.3
        """
    )

    with pytest.raises(ValueError):
        ConfigLoader(str(path))


def test_missing_material_properties_raises(tmp_path):
    # missing E
    path = _write_yaml(
        tmp_path,
        """
        input_stl: "example.stl"
        mesh_resolution: 40
        volume_fraction: 0.4
        material:
          nu: 0.3
        """
    )

    with pytest.raises(ValueError):
        ConfigLoader(str(path))


def test_get_with_default_and_get_nested_default(tmp_path):
    path = _write_yaml(
        tmp_path,
        """
        input_stl: "example.stl"
        mesh_resolution: 40
        volume_fraction: 0.4
        material:
          E: 210e9
          nu: 0.3
        """
    )

    cfg = ConfigLoader(str(path))

    assert cfg.get("does_not_exist", default=123) == 123
    assert cfg.get_nested("material", "does_not_exist", default="foo") == "foo"


def test_bad_yaml_raises_value_error(tmp_path):
    path = _write_yaml(
        tmp_path,
        """
        input_stl: "example.stl"
        mesh_resolution: [this_is_not_closed
        """
    )

    with pytest.raises(ValueError):
        ConfigLoader(str(path))