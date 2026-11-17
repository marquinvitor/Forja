import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from persistencia import (
    DEFAULT_SETTINGS,
    carregar_settings,
    resolver_output_dir,
    resolver_settings_path,
)


class PersistenciaTest(unittest.TestCase):
    def test_settings_customizado_aponta_para_settings_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(resolver_settings_path(tmp), Path(tmp) / "settings.json")

    def test_settings_e_criado_com_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "settings.json"
            dados = carregar_settings(caminho)
            self.assertEqual(dados, DEFAULT_SETTINGS)
            self.assertEqual(json.loads(caminho.read_text()), DEFAULT_SETTINGS)

    def test_output_padrao_vem_do_diretorio_de_dados(self):
        with patch("persistencia.diretorio_dados", return_value=Path("/tmp/forja-data")):
            self.assertEqual(resolver_output_dir({}), "/tmp/forja-data")

    def test_output_padrao_real_e_pasta_forja_do_usuario(self):
        with patch("persistencia.Path.home", return_value=Path("/home/teste")):
            from persistencia import diretorio_dados
            self.assertEqual(diretorio_dados(), Path("/home/teste/forja"))

    def test_json_invalido_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "settings.json"
            caminho.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON inválido"):
                carregar_settings(caminho)

    def test_campo_com_tipo_invalido_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "settings.json"
            caminho.write_text(json.dumps({"output_dir": 42}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "output_dir"):
                carregar_settings(caminho)
