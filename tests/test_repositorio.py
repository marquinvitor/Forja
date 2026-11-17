import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from repositorio import resolver_repositorio


class RepositorioTest(unittest.TestCase):
    def test_caminho_manual_e_preservado(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "labs"
            caminho.mkdir()
            self.assertEqual(resolver_repositorio({"caminho_repo": str(caminho)}), caminho.resolve())

    def test_caminho_manual_inexistente_falha(self):
        with self.assertRaisesRegex(ValueError, "não encontrado"):
            resolver_repositorio({"caminho_repo": "/tmp/nao-existe-forja"})

    def test_clone_automatico_usa_pasta_labs(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp) / "arcade"
            labs = raiz / "labs"

            def clone(*args, **kwargs):
                labs.mkdir(parents=True)

            with patch("repositorio.caminho_repositorio_automatico", return_value=labs), \
                 patch("repositorio.subprocess.run", side_effect=clone):
                self.assertEqual(resolver_repositorio({}), labs)


if __name__ == "__main__":
    unittest.main()
