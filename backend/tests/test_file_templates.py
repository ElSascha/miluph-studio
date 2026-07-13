import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from backend.miluph_studio.file_templates import (
    DEFAULT_MILUPHCUDA_CONFIG,
    DEFAULT_PARAMETER_H,
    load_miluphcuda_config,
    read_text_file,
    write_miluphcuda_config,
    write_parameter_header,
    write_text_file,
)
import backend.miluph_studio.server as server_module
from backend.miluph_studio.server import resolve_parameter_header_target


class FileTemplateTests(unittest.TestCase):
    def test_read_text_file_returns_default_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "parameter.h"
            content = read_text_file(path, DEFAULT_PARAMETER_H)
            self.assertEqual(content, DEFAULT_PARAMETER_H)

    def test_write_and_reload_miluphcuda_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "miluphcuda.yaml"
            payload = {"simulation_name": "demo", "dt": 0.01, "t_end": 1.0}
            write_miluphcuda_config(path, payload)
            loaded = load_miluphcuda_config(path, DEFAULT_MILUPHCUDA_CONFIG)
            self.assertEqual(loaded["simulation_name"], "demo")
            self.assertEqual(loaded["dt"], 0.01)
            self.assertEqual(loaded["t_end"], 1.0)

    def test_write_parameter_header_includes_extended_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "parameter.h"
            content = write_parameter_header(path, {"GRAVITATING_POINT_MASSES": 1, "ARTIFICIAL_VISCOSITY": 1})
            self.assertIn("#define GRAVITATING_POINT_MASSES 1", content)
            self.assertIn("#define ARTIFICIAL_VISCOSITY 1", content)

    def test_write_parameter_header_preserves_header_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "parameter.h"
            content = write_parameter_header(path, {"DIM": 2, "SOLID": 0})
            self.assertIn("// Dimension of the problem", content)
            self.assertIn("#define DIM 2", content)
            self.assertIn("#define SOLID 0", content)
            self.assertIn("#endif", content)

    def test_resolve_parameter_header_target_uses_selected_installation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            install_dir = Path(tmpdir) / "miluphcuda"
            install_dir.mkdir()
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(
                f"miluphcuda_instances:\n  - name: demo\n    mode: local\n    path: {install_dir}\n",
                encoding="utf-8",
            )
            target = resolve_parameter_header_target("demo", config_path, Path(tmpdir) / "fallback")
            self.assertEqual(target, install_dir / "parameter.h")

    def test_update_parameter_header_uses_supplied_macro_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parameter_path = root / "parameter.h"
            parameter_path.write_text(DEFAULT_PARAMETER_H, encoding="utf-8")
            with patch.object(server_module, "ROOT_DIR", root), patch.object(server_module, "CONFIG_PATH", root / "config.yaml"):
                server_module.update_parameter_header({"DIM": 2, "SOLID": 0, "instance_name": None})
            content = parameter_path.read_text(encoding="utf-8")
            self.assertIn("#define DIM 2", content)
            self.assertIn("#define SOLID 0", content)

    def test_write_text_file_persists_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "parameter.h"
            write_text_file(path, "#define N 128")
            self.assertEqual(path.read_text(encoding="utf-8"), "#define N 128")


if __name__ == "__main__":
    unittest.main()
