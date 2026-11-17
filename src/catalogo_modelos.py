"""Descoberta e cache dos modelos disponíveis nos provedores."""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from persistencia import arquivo_cache_modelos


OPENAI_API_URL = "https://api.openai.com/v1/models"
_SNAPSHOT_DATADO = re.compile(r"-\d{4}-\d{2}-\d{2}$")

# Preferências de uso do Forja. A API lista IDs, mas não fornece uma política
# de papéis (rascunho/revisão/auditoria), por isso essa camada é explícita.
FAMILIAS_OPENAI: dict[str, dict[str, Any]] = {
    "gpt-6": {
        "label": "GPT-6",
        "candidatos": {
            "rascunho": ["openai/gpt-6-luna", "openai/gpt-6.1-terra"],
            "revisao": ["openai/gpt-6.1-sol", "openai/gpt-6-sol"],
            "auditoria": ["openai/gpt-6-astra", "openai/gpt-6.1-sol"],
        },
    },
    "gpt-5.6": {
        "label": "GPT-5.6",
        "candidatos": {
            "rascunho": ["openai/gpt-5.6-luna", "openai/gpt-5.6-terra"],
            "revisao": ["openai/gpt-5.6-terra", "openai/gpt-5.6-sol"],
            "auditoria": ["openai/gpt-5.6-sol"],
        },
    },
    "gpt-5.2": {
        "label": "GPT-5.2",
        "candidatos": {
            "rascunho": ["openai/gpt-5-mini", "openai/gpt-5-nano", "openai/gpt-5.2"],
            "revisao": ["openai/gpt-5.2", "openai/gpt-5.2-pro"],
            "auditoria": ["openai/gpt-5.2-pro", "openai/gpt-5.2"],
        },
    },
}


def resolver_chave(settings: Mapping[str, Any], provider: str) -> str:
    direct = str(settings.get(f"{provider}_api_key") or "").strip()
    file_value = str(settings.get(f"{provider}_api_key_file") or "").strip()
    if file_value:
        try:
            return Path(file_value).expanduser().read_text(encoding="utf-8").strip()
        except OSError as error:
            raise ValueError(f"Não foi possível ler a chave em {file_value}: {error}") from error
    return direct


def _modelo_de_texto(model_id: str) -> bool:
    """Seleciona modelos que podem ser usados no fluxo de texto do CrewAI."""
    model_id = model_id.lower()
    if _SNAPSHOT_DATADO.search(model_id):
        return False
    if not model_id.startswith(("gpt-", "o1", "o3", "o4", "chatgpt-")):
        return False
    return not any(
        termo in model_id
        for termo in ("audio", "realtime", "transcribe", "tts", "image", "search", "moderation")
    )


def listar_modelos_openai(
    api_key: str,
    opener: Callable[..., Any] = urlopen,
) -> list[str]:
    if not api_key.strip():
        raise ValueError("A chave OpenAI não está configurada.")
    request = Request(
        OPENAI_API_URL,
        headers={"Authorization": f"Bearer {api_key.strip()}", "Accept": "application/json"},
    )
    try:
        with opener(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise ValueError(f"A OpenAI recusou a consulta de modelos (HTTP {error.code}).") from error
    except (URLError, TimeoutError, OSError) as error:
        raise ValueError(f"Não foi possível consultar os modelos da OpenAI: {error}") from error
    modelos = {
        f"openai/{item['id']}"
        for item in payload.get("data", [])
        if isinstance(item, Mapping)
        and isinstance(item.get("id"), str)
        and _modelo_de_texto(item["id"])
    }
    return sorted(modelos)


def carregar_catalogo(caminho: Path | None = None) -> dict[str, list[str]]:
    caminho = caminho or arquivo_cache_modelos()
    if not caminho.exists():
        return {}
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        provider: [str(model) for model in models if isinstance(model, str)]
        for provider, models in dados.get("providers", {}).items()
        if isinstance(provider, str) and isinstance(models, list)
    }


def salvar_catalogo(catalogo: Mapping[str, list[str]], caminho: Path | None = None) -> Path:
    caminho = caminho or arquivo_cache_modelos()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps({"providers": dict(catalogo)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return caminho


def familias_openai(modelos: list[str]) -> dict[str, dict[str, Any]]:
    """Monta linhas e sugestões somente com modelos presentes no catálogo."""
    disponiveis = set(modelos)
    resultado: dict[str, dict[str, Any]] = {}
    for nome, definicao in FAMILIAS_OPENAI.items():
        sugestoes = {
            papel: next((modelo for modelo in candidatos if modelo in disponiveis), None)
            for papel, candidatos in definicao["candidatos"].items()
        }
        sugestoes = {papel: modelo for papel, modelo in sugestoes.items() if modelo}
        if sugestoes:
            resultado[nome] = {"label": definicao["label"], "suggestions": sugestoes}

    return resultado


def atualizar_catalogo_openai(api_key: str, caminho: Path | None = None) -> list[str]:
    caminho = caminho or arquivo_cache_modelos()
    catalogo = carregar_catalogo(caminho)
    catalogo["openai"] = listar_modelos_openai(api_key)
    salvar_catalogo(catalogo, caminho)
    return catalogo["openai"]
