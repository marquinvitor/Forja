import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from llm_config import carregar_configuracao, criar_llms


class ConfiguracaoLLMTest(unittest.TestCase):
    def test_openai_usa_apenas_sua_chave_e_modelos_por_papel(self):
        padrao = carregar_configuracao({
            "llm_provider": "openai",
            "openai_api_key": "chave-openai",
        })
        self.assertEqual(padrao.modelos["revisao"], "openai/gpt-4.1")

        config = carregar_configuracao({
            "llm_provider": "openai",
            "gemini_api_key": "outra-chave",
            "openai_api_key": "chave-openai",
            "llm_model_revisao": "openai/gpt-4.1-mini",
        })
        chamadas = []

        def fabrica(**kwargs):
            chamadas.append(kwargs)
            return kwargs

        llms = criar_llms(config, fabrica=fabrica)

        self.assertEqual(set(llms), {"rascunho", "revisao", "auditoria"})
        self.assertEqual([c["model"] for c in chamadas], [
            "openai/gpt-4.1-mini",
            "openai/gpt-4.1-mini",
            "openai/gpt-4.1-mini",
        ])
        self.assertTrue(all(c["api_key"] == "chave-openai" for c in chamadas))
        self.assertEqual([c["max_tokens"] for c in chamadas], [8000, 16000, 16000])

    def test_gemini_preserva_modelos_e_configura_cache(self):
        config = carregar_configuracao({
            "llm_provider": "gemini",
            "gemini_api_key": "chave-gemini",
        })
        with patch("llm_config._configurar_cache_gemini") as configurar_cache:
            llms = criar_llms(config, fabrica=lambda **kwargs: kwargs)

        configurar_cache.assert_called_once_with()
        self.assertEqual(llms["rascunho"]["model"], "gemini/gemini-3.5-flash-lite")
        self.assertEqual(llms["revisao"]["model"], "gemini/gemini-3.8-flash")
        self.assertEqual(llms["auditoria"]["api_key"], "chave-gemini")

    def test_chave_em_arquivo_tem_prioridade_quando_configurada(self):
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = Path(tmp) / "api_key.txt"
            arquivo.write_text("chave-do-arquivo\n", encoding="utf-8")
            env = {"llm_provider": "openai", "openai_api_key_file": str(arquivo)}

            self.assertEqual(carregar_configuracao(env).api_key, "chave-do-arquivo")
            env["openai_api_key"] = "chave-direta"
            self.assertEqual(carregar_configuracao(env).api_key, "chave-do-arquivo")

    def test_arquivo_de_chave_invalido_falha_com_mensagem_clara(self):
        with self.assertRaisesRegex(ValueError, "openai_api_key_file"):
            carregar_configuracao({
                "llm_provider": "openai",
                "openai_api_key_file": "/arquivo/inexistente",
            })

    def test_configuracao_invalida_falha_antes_de_criar_modelos(self):
        casos = [
            ({}, "llm_provider"),
            ({"llm_provider": "local", "openai_api_key": "chave"}, "llm_provider"),
            ({"llm_provider": "openai", "gemini_api_key": "chave"}, "openai_api_key"),
            ({"llm_provider": "gemini", "openai_api_key": "chave"}, "gemini_api_key"),
            ({"llm_provider": "openai", "openai_api_key": "chave",
              "llm_model_auditoria": "gemini/gemini-3.8-flash"}, "llm_model_auditoria"),
        ]
        for env, mensagem in casos:
            with self.subTest(env=env), self.assertRaisesRegex(ValueError, mensagem):
                carregar_configuracao(env)


if __name__ == "__main__":
    unittest.main()
