"""Resolve o repositório de tarefas modelo usado pela geração."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Mapping, Any

from platformdirs import user_cache_path


REPOSITORIO_URL = "https://github.com/qxcodepoo/arcade.git"


def caminho_repositorio_automatico() -> Path:
    return Path(user_cache_path("forja")) / "arcade" / "labs"


def resolver_repositorio(settings: Mapping[str, Any]) -> Path:
    """Usa a pasta configurada ou clona arcade e devolve sua pasta labs."""
    configurado = str(settings.get("caminho_repo") or "").strip()
    if configurado:
        caminho = Path(configurado).expanduser().resolve()
        if not caminho.is_dir():
            raise ValueError(f"Repositório de referência não encontrado: {caminho}")
        return caminho

    labs = caminho_repositorio_automatico()
    if labs.is_dir():
        return labs
    raiz = labs.parent
    if raiz.exists() and not (raiz / ".git").exists():
        raise ValueError(f"O cache automático já existe, mas não é um clone válido: {raiz}")
    raiz.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", REPOSITORIO_URL, str(raiz)],
            check=True, capture_output=True, text=True,
        )
    except FileNotFoundError as error:
        raise ValueError("Git não está instalado; configure manualmente uma pasta de tarefas modelo.") from error
    except subprocess.CalledProcessError as error:
        detalhe = (error.stderr or error.stdout or "").strip()
        raise ValueError(f"Não foi possível clonar {REPOSITORIO_URL}: {detalhe}") from error
    if not labs.is_dir():
        raise ValueError(f"O clone foi concluído, mas a pasta esperada não existe: {labs}")
    return labs
