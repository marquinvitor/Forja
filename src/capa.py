"""Geração opcional da capa visual de uma atividade."""

from __future__ import annotations

import base64
from pathlib import Path
from urllib.request import urlopen


MODELO_CAPA_PADRAO = "gpt-image-2.5-flare"
TAMANHO_API_CAPA = "1536x1024"
TAMANHO_FINAL_CAPA = (960, 540)


def _ajustar_tamanho(caminho: Path) -> None:
    try:
        from PIL import Image, ImageOps
    except ImportError as error:
        raise ValueError("A dependência Pillow é necessária para ajustar a capa para 960x540.") from error
    with Image.open(caminho) as imagem:
        capa = ImageOps.fit(imagem.convert("RGB"), TAMANHO_FINAL_CAPA, method=Image.Resampling.LANCZOS)
        capa.save(caminho, format="WEBP", quality= WebP_QUALITY)


WebP_QUALITY = 90


def gerar_capa_openai(api_key: str, descricao: str, destino: Path, modelo: str = MODELO_CAPA_PADRAO) -> Path:
    if not api_key.strip():
        raise ValueError("A chave OpenAI não está configurada para gerar a capa.")
    try:
        from openai import OpenAI
    except ImportError as error:
        raise ValueError("O pacote openai não está instalado; execute 'uv sync'.") from error

    prompt = (
        "Crie uma ilustração de capa para uma atividade educacional de programação em Kotlin. "
        "A imagem deve ser limpa, profissional, sem texto, sem letras, sem logotipos e sem marcas d'água. "
        f"Tema da atividade: {descricao}"
    )
    resposta = OpenAI(api_key=api_key.strip()).images.generate(
        model=modelo, prompt=prompt, size=TAMANHO_API_CAPA, output_format="webp"
    )
    item = resposta.data[0]
    destino.parent.mkdir(parents=True, exist_ok=True)
    if getattr(item, "b64_json", None):
        destino.write_bytes(base64.b64decode(item.b64_json))
    elif getattr(item, "url", None):
        with urlopen(item.url, timeout=60) as arquivo:
            destino.write_bytes(arquivo.read())
    else:
        raise ValueError("A OpenAI não retornou dados de imagem para a capa.")
    _ajustar_tamanho(destino)
    return destino
