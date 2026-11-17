import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from painel_web import _environment, _merge_payload, _key_status


class PainelWebTest(unittest.TestCase):
    def test_environment_nao_expoe_chaves(self):
        settings = {
            "llm_provider": "openai",
            "openai_api_key": "segredo",
            "openai_api_key_file": None,
            "gemini_api_key": None,
            "gemini_api_key_file": None,
            "output_dir": "~/forja",
            "caminho_repo": "~/arcade/base",
        }
        with tempfile.TemporaryDirectory() as tmp:
            state = _environment(settings, Path(tmp) / "settings.json")
        self.assertNotIn("segredo", str(state))
        self.assertTrue(state["providers"]["openai"]["key"]["configured"])
        self.assertEqual(state["settings_path"], str(Path(tmp) / "settings.json"))
        self.assertIn("cache_path", state)

    def test_payload_vazio_preserva_chaves(self):
        settings = {
            "llm_provider": "gemini",
            "gemini_api_key": "segredo",
            "gemini_api_key_file": None,
        }
        merged = _merge_payload(settings, {"llm_provider": "openai"})
        self.assertEqual(merged["gemini_api_key"], "segredo")
        self.assertEqual(merged["llm_provider"], "openai")

    def test_status_de_arquivo_so_fica_configurado_com_arquivo_valido(self):
        with tempfile.TemporaryDirectory() as tmp:
            key_file = Path(tmp) / "key.txt"
            key_file.write_text("chave\n", encoding="utf-8")
            status = _key_status({"openai_api_key_file": str(key_file)}, "openai")
        self.assertEqual(status["source"], "file")
        self.assertTrue(status["configured"])


if __name__ == "__main__":
    unittest.main()
