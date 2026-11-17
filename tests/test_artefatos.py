import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from forja import salvar_questao


class ArtefatosTest(unittest.TestCase):
    def test_prompt_e_salvo_em_json_com_topicos(self):
        with tempfile.TemporaryDirectory() as tmp:
            salvar_questao(tmp, "aeroporto", "# Aeroporto", "solucao", prompt="prompt original",
                           titulo="Sistema de Aeroporto", topicos=["mapas", "excecoes"],
                           topicos_input="mapas ; excecoes, mapas")
            pasta = Path(tmp) / "aeroporto"
            dados = json.loads((pasta / "prompt.json").read_text(encoding="utf-8"))
            self.assertEqual(dados, {
                "titulo": "Sistema de Aeroporto",
                "prompt": "prompt original",
                "topicos": "mapas ; excecoes, mapas",
                "topicos_detectados": ["mapas", "excecoes"],
            })
            self.assertEqual((pasta / "src" / "kt" / "shell.kt").read_text(encoding="utf-8"), "solucao")
            self.assertFalse((pasta / "starter" / "kt" / "shell.kt").exists())
            self.assertFalse((pasta / "prompt.txt").exists())


if __name__ == "__main__":
    unittest.main()
