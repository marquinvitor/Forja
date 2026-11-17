import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from catalogo_modelos import listar_modelos_openai, atualizar_catalogo_openai, familias_openai


class CatalogoModelosTest(unittest.TestCase):
    def test_filtra_modelos_que_nao_sao_de_texto(self):
        payload = {"data": [
            {"id": "gpt-5.5"}, {"id": "gpt-5.5-2026-04-23"}, {"id": "gpt-4o-mini"},
            {"id": "text-embedding-3-small"}, {"id": "gpt-realtime"},
        ]}

        class Response(io.StringIO):
            def __enter__(self): return self
            def __exit__(self, *_): self.close()

        def opener(request, timeout):
            self.assertEqual(request.get_header("Authorization"), "Bearer segredo")
            return Response(json.dumps(payload))

        self.assertEqual(listar_modelos_openai("segredo", opener), ["openai/gpt-4o-mini", "openai/gpt-5.5"])

    def test_atualiza_cache_sem_gravar_chave(self):
        payload = {"data": [{"id": "gpt-5.5"}]}

        class Response(io.StringIO):
            def __enter__(self): return self
            def __exit__(self, *_): self.close()

        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "models.json"
            with patch("catalogo_modelos.listar_modelos_openai", return_value=["openai/gpt-5.5"]):
                self.assertEqual(atualizar_catalogo_openai("segredo", caminho), ["openai/gpt-5.5"])
            conteudo = caminho.read_text(encoding="utf-8")
            self.assertNotIn("segredo", conteudo)

    def test_familias_usam_papeis_explicitos(self):
        familias = familias_openai([
            "openai/gpt-6-astra", "openai/gpt-6.1-sol", "openai/gpt-6-luna",
            "openai/gpt-5.6-terra", "openai/gpt-5.6-sol",
        ])
        self.assertEqual(familias["gpt-6"]["suggestions"]["auditoria"], "openai/gpt-6-astra")
        self.assertEqual(familias["gpt-5.6"]["suggestions"]["rascunho"], "openai/gpt-5.6-terra")

    def test_modelos_sem_familia_real_nao_entram_no_seletor(self):
        familias = familias_openai(["openai/modelo-novo-sem-regra"])
        self.assertEqual(familias, {})


if __name__ == "__main__":
    unittest.main()
