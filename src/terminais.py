"""Detecção e abertura de terminais Linux para acompanhar uma geração."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path


TERMINAIS = (
    ("kgx", "GNOME Console (kgx)"),
    ("gnome-terminal", "GNOME Terminal"),
    ("konsole", "Konsole"),
    ("xfce4-terminal", "XFCE Terminal"),
    ("mate-terminal", "MATE Terminal"),
    ("terminator", "Terminator"),
    ("tilix", "Tilix"),
    ("lxterminal", "LXTerminal"),
    ("xterm", "xterm"),
    ("alacritty", "Alacritty"),
    ("kitty", "Kitty"),
    ("foot", "Foot"),
    ("wezterm", "WezTerm"),
)


def detectar_terminais() -> list[dict[str, str | bool]]:
    return [{"id": comando, "label": label, "found": bool(shutil.which(comando))}
            for comando, label in TERMINAIS]


def abrir_acompanhamento(caminho_log: Path, terminal: str = "auto") -> str:
    encontrados = {item["id"] for item in detectar_terminais() if item["found"]}
    escolhido = next(iter(encontrados), None) if terminal in {"", "auto"} else terminal
    if escolhido not in encontrados:
        raise ValueError("Nenhum terminal selecionado foi encontrado no PATH.")
    comando = f"tail -n +1 -f {shlex.quote(str(caminho_log))}"
    # As formas abaixo são compatíveis com os emuladores mais usados; todos
    # recebem o mesmo comando shell para manter o log em acompanhamento.
    argv = {
        "kgx": ["kgx", "--", "bash", "-lc", comando],
        "gnome-terminal": ["gnome-terminal", "--", "bash", "-lc", comando],
        "konsole": ["konsole", "-e", "bash", "-lc", comando],
        "xfce4-terminal": ["xfce4-terminal", "--command", f"bash -lc {shlex.quote(comando)}"],
        "mate-terminal": ["mate-terminal", "--", "bash", "-lc", comando],
        "terminator": ["terminator", "-e", f"bash -lc {shlex.quote(comando)}"],
        "tilix": ["tilix", "-e", "bash", "-lc", comando],
        "lxterminal": ["lxterminal", "-e", f"bash -lc {shlex.quote(comando)}"],
        "xterm": ["xterm", "-e", "bash", "-lc", comando],
        "alacritty": ["alacritty", "-e", "bash", "-lc", comando],
        "kitty": ["kitty", "bash", "-lc", comando],
        "foot": ["foot", "bash", "-lc", comando],
        "wezterm": ["wezterm", "start", "--", "bash", "-lc", comando],
    }[escolhido]
    subprocess.Popen(argv, start_new_session=True, env=os.environ.copy())
    return str(escolhido)
