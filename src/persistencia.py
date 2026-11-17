"""Caminhos e persistência de configuração da Forja."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from platformdirs import user_cache_path, user_config_path


APP_NAME = "forja"
SETTINGS_FILENAME = "settings.json"
DEFAULT_SETTINGS: dict[str, Any] = {
    "llm_provider": "gemini",
    "gemini_api_key": None,
    "gemini_api_key_file": None,
    "openai_api_key": None,
    "openai_api_key_file": None,
    "openai_image_model": "gpt-image-2.5-flare",
    "llm_model_rascunho": None,
    "llm_model_revisao": None,
    "llm_model_auditoria": None,
    "caminho_repo": None,
    "output_dir": None,
    "terminal_name": "auto",
    "open_terminal_on_project": False,
}


def diretorio_configuracao() -> Path:
    return Path(user_config_path(APP_NAME))


def diretorio_dados() -> Path:
    # Os projetos são arquivos do usuário e ficam em um caminho curto e previsível.
    return Path.home() / APP_NAME


def arquivo_cache_padroes() -> Path:
    return Path(user_cache_path(APP_NAME)) / "padroes.json"


def arquivo_cache_modelos() -> Path:
    """Arquivo de catálogo de modelos descobertos nos provedores."""
    return Path(user_cache_path(APP_NAME)) / "models.json"


def arquivo_cache_ultimo_projeto() -> Path:
    return Path(user_cache_path(APP_NAME)) / "last_project.json"


def carregar_ultimo_projeto() -> dict[str, Any]:
    caminho = arquivo_cache_ultimo_projeto()
    if not caminho.exists():
        return {}
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dados if isinstance(dados, dict) else {}


def salvar_ultimo_projeto(dados: Mapping[str, Any]) -> None:
    _gravar_json_atomico(arquivo_cache_ultimo_projeto(), dados)


def limpar_ultimo_projeto() -> None:
    try:
        arquivo_cache_ultimo_projeto().unlink()
    except FileNotFoundError:
        pass


def resolver_settings_path(settings_dir: str | os.PathLike[str] | None = None) -> Path:
    """Resolve uma pasta de configuração para seu arquivo settings.json."""
    pasta = diretorio_configuracao() if settings_dir is None else Path(settings_dir).expanduser()
    if pasta.exists() and not pasta.is_dir():
        raise ValueError(f"O caminho de settings deve ser uma pasta: {pasta}")
    return pasta / SETTINGS_FILENAME


def _gravar_json_atomico(caminho: Path, dados: Mapping[str, Any]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(prefix=f".{caminho.name}.", dir=caminho.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        if os.path.exists(temporario):
            os.unlink(temporario)


def _validar_settings(dados: Mapping[str, Any], caminho: Path) -> dict[str, Any]:
    configuracao = dict(DEFAULT_SETTINGS)
    configuracao.update(dados)
    # GPT Image 1 foi encerrado; migra configurações antigas para o modelo
    # vigente de geração rápida de capas.
    if configuracao.get("openai_image_model") == "gpt-image-1":
        configuracao["openai_image_model"] = "gpt-image-2.5-flare"
    campos_texto = {
        "llm_provider", "gemini_api_key", "gemini_api_key_file",
        "openai_api_key", "openai_api_key_file", "llm_model_rascunho",
        "openai_image_model",
        "terminal_name", "open_terminal_on_project",
        "llm_model_revisao", "llm_model_auditoria", "caminho_repo", "output_dir",
    }
    for campo in campos_texto:
        valor = configuracao.get(campo)
        if campo == "open_terminal_on_project":
            if not isinstance(valor, bool):
                raise ValueError(f"O campo {campo} em {caminho} deve ser booleano.")
        elif valor is not None and not isinstance(valor, str):
            raise ValueError(f"O campo {campo} em {caminho} deve ser texto ou null.")
    return configuracao


def carregar_settings(caminho: Path) -> dict[str, Any]:
    """Carrega settings.json; cria um arquivo inicial se ele ainda não existir."""
    if not caminho.exists():
        dados = dict(DEFAULT_SETTINGS)
        _gravar_json_atomico(caminho, dados)
        return dados
    try:
        with caminho.open(encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ValueError(f"JSON inválido em {caminho}: {erro.msg}") from erro
    if not isinstance(dados, dict):
        raise ValueError(f"O conteúdo de {caminho} deve ser um objeto JSON.")
    return _validar_settings(dados, caminho)


def salvar_settings(caminho: Path, dados: Mapping[str, Any]) -> dict[str, Any]:
    configuracao = _validar_settings(dados, caminho)
    _gravar_json_atomico(caminho, configuracao)
    return configuracao


def expandir_caminho(valor: str | os.PathLike[str]) -> Path:
    return Path(valor).expanduser().resolve()


def resolver_caminho_repo(settings: Mapping[str, Any]) -> str:
    valor = settings.get("caminho_repo")
    return str(expandir_caminho(str(valor))) if valor else ""


def resolver_output_dir(settings: Mapping[str, Any]) -> str:
    valor = settings.get("output_dir")
    return str(expandir_caminho(valor)) if valor else str(diretorio_dados())
