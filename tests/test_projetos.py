import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from projetos import atualizar_projeto, listar_projetos, projeto_por_caminho, registrar_projeto


class ProjetosTest(unittest.TestCase):
    def test_registro_e_manifesto(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            banco = raiz / "projects.sqlite3"
            pasta = raiz / "biblioteca"
            projeto = registrar_projeto("biblioteca", pasta, "descrição", provider="openai", caminho_registro=banco)
            self.assertEqual(projeto_por_caminho(pasta, banco)["id"], projeto["id"])
            pasta.mkdir()
            atualizado = atualizar_projeto(projeto["id"], banco, status="approved", approved=True)
            self.assertTrue((pasta / ".forja" / "project.json").exists())
            self.assertTrue(atualizado["approved"])
            self.assertEqual(len(listar_projetos(banco)), 1)


if __name__ == "__main__":
    unittest.main()
