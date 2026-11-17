"""Configuração dos modelos usados pelos agentes da Forja."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any, Callable, Mapping


MODELOS_PADRAO = {
    "gemini": {
        "rascunho": "gemini/gemini-3.5-flash-lite",
        "revisao": "gemini/gemini-3.8-flash",
        "auditoria": "gemini/gemini-3.5-flash-lite",
    },
    "openai": {
        "rascunho": "openai/gpt-4.1-mini",
        "revisao": "openai/gpt-4.1",
        "auditoria": "openai/gpt-4.1-mini",
    },
}

MAX_TOKENS = {"rascunho": 8000, "revisao": 16000, "auditoria": 16000}
VARIAVEIS_MODELO = {
    "rascunho": "LLM_MODEL_RASCUNHO",
    "revisao": "LLM_MODEL_REVISAO",
    "auditoria": "LLM_MODEL_AUDITORIA",
}


@dataclass(frozen=True)
class ConfiguracaoLLM:
    provedor: str
    modelos: dict[str, str]
    api_key: str = field(repr=False)


def carregar_configuracao(settings: Mapping[str, Any]) -> ConfiguracaoLLM:
    """Lê settings.json e valida o provedor, chave e modelos por papel."""
    provedor = str(settings.get("llm_provider") or "").strip().lower()
    if provedor not in MODELOS_PADRAO:
        raise ValueError("llm_provider deve ser 'gemini' ou 'openai'.")

    nome_chave = f"{provedor}_api_key"
    nome_arquivo = f"{provedor}_api_key_file"
    api_key = str(settings.get(nome_chave) or os.environ.get(nome_chave.upper()) or "").strip()
    arquivo_chave = str(settings.get(nome_arquivo) or "").strip()
    if arquivo_chave:
        caminho = Path(arquivo_chave).expanduser()
        try:
            api_key = caminho.read_text(encoding="utf-8").strip()
        except OSError as erro:
            raise ValueError(f"Não foi possível ler {nome_arquivo}: {caminho}.") from erro
    if not api_key:
        raise ValueError(
            f"Defina {nome_chave} ou {nome_arquivo} para llm_provider={provedor}."
        )

    modelos = {}
    for papel, modelo_padrao in MODELOS_PADRAO[provedor].items():
        variavel = VARIAVEIS_MODELO[papel]
        modelo = str(settings.get(variavel.lower()) or modelo_padrao).strip()
        if not modelo.startswith(f"{provedor}/") or not modelo.split("/", 1)[1]:
            raise ValueError(f"{variavel.lower()} deve conter um modelo com prefixo '{provedor}/'.")
        modelos[papel] = modelo

    return ConfiguracaoLLM(provedor=provedor, modelos=modelos, api_key=api_key)


_cache_gemini_configurado = False


def _configurar_cache_gemini() -> None:
    """Mantém a compatibilidade com o tratamento de cache já usado no Gemini."""
    global _cache_gemini_configurado
    if _cache_gemini_configurado:
        return

    import litellm

    litellm.cache = None
    completion_original = litellm.completion

    def completion_sem_cache(**kwargs):
        if isinstance(kwargs.get("cache"), bool):
            kwargs.pop("cache")
        for msg in kwargs.get("messages", []):
            msg.pop("cache_breakpoint", None)
            if isinstance(msg.get("content"), list):
                for bloco in msg["content"]:
                    if isinstance(bloco, dict):
                        bloco.pop("cache_control", None)
        return completion_original(**kwargs)

    import os

    litellm.completion = completion_sem_cache
    os.environ["CREWAI_DISABLE_PROMPT_CACHING"] = "true"
    _cache_gemini_configurado = True


def criar_llms(
    config: ConfiguracaoLLM,
    fabrica: Callable[..., object] | None = None,
) -> dict[str, object]:
    """Cria os modelos dos três papéis sem alterar a orquestração CrewAI."""
    if fabrica is None:
        from crewai import LLM

        fabrica = LLM
    if config.provedor == "gemini":
        _configurar_cache_gemini()

    return {
        papel: fabrica(
            model=modelo,
            api_key=config.api_key,
            temperature=1.0,
            max_retries=3,
            timeout=600,
            max_tokens=MAX_TOKENS[papel],
        )
        for papel, modelo in config.modelos.items()
    }
