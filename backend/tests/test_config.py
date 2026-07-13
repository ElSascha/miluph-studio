import tempfile
import textwrap
import unittest
from pathlib import Path

from backend.miluph_studio.config import load_instances


class LoadInstancesTest(unittest.TestCase):
    def test_load_instances_reads_miluphcuda_instances_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(
                textwrap.dedent(
                    """
                    miluphcuda_instances:
                      - name: local
                        mode: local
                        path: /tmp/miluphcuda
                    """
                ).strip()
            )

            instances = load_instances(config_path)

            self.assertEqual(len(instances), 1)
            self.assertEqual(instances[0].name, "local")
            self.assertEqual(instances[0].mode, "local")
            self.assertEqual(instances[0].path, "/tmp/miluphcuda")


if __name__ == "__main__":
    unittest.main()
