"""Registro persistente dos projetos gerados pela Forja."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from platformdirs import user_data_path


def arquivo_registro() -> Path:
    return Path(user_data_path("forja")) / "projects.sqlite3"


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _conexao(caminho: Path | None = None) -> sqlite3.Connection:
    caminho = caminho or arquivo_registro()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, slug TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE, description TEXT NOT NULL,
            activity_type TEXT NOT NULL, provider TEXT, models_json TEXT,
            topics_input TEXT, topics_json TEXT, status TEXT NOT NULL, approved INTEGER,
            attempts INTEGER NOT NULL DEFAULT 0, diagnostic_path TEXT,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL, completed_at TEXT
        )
    """)
    columns = {row[1] for row in conexao.execute("PRAGMA table_info(projects)").fetchall()}
    if "topics_input" not in columns:
        conexao.execute("ALTER TABLE projects ADD COLUMN topics_input TEXT")
    conexao.commit()
    return conexao


def registrar_projeto(
    name: str,
    path: str | Path,
    description: str,
    *,
    activity_type: str = "TRAIN",
    provider: str | None = None,
    models: Mapping[str, str] | None = None,
    topics: list[str] | None = None,
    topics_input: str | None = None,
    status: str = "queued",
    caminho_registro: Path | None = None,
) -> dict[str, Any]:
    caminho = Path(path).expanduser().resolve()
    now = _agora()
    projeto = {
        "id": str(uuid.uuid4()), "name": name, "slug": caminho.name, "path": str(caminho),
        "description": description, "activity_type": activity_type, "provider": provider,
        "models": dict(models or {}), "topics": list(topics or []), "topics_input": topics_input or "", "status": status,
        "approved": None, "attempts": 0, "diagnostic_path": None,
        "created_at": now, "updated_at": now, "completed_at": None,
    }
    with _conexao(caminho_registro) as db:
        existente = db.execute("SELECT * FROM projects WHERE path = ?", (str(caminho),)).fetchone()
        if existente is not None:
            return _row(existente)
        db.execute("""INSERT INTO projects
            (id, name, slug, path, description, activity_type, provider, models_json,
             topics_input, topics_json, status, approved, attempts, diagnostic_path,
             created_at, updated_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            projeto["id"], projeto["name"], projeto["slug"], projeto["path"], projeto["description"],
            projeto["activity_type"], projeto["provider"], json.dumps(projeto["models"]),
            projeto["topics_input"], json.dumps(projeto["topics"]), projeto["status"], None, 0, None,
            projeto["created_at"], projeto["updated_at"], None,
        ))
    escrever_manifesto(projeto)
    return projeto


def projeto_por_caminho(path: str | Path, caminho_registro: Path | None = None) -> dict[str, Any] | None:
    caminho = str(Path(path).expanduser().resolve())
    with _conexao(caminho_registro) as db:
        row = db.execute("SELECT * FROM projects WHERE path = ?", (caminho,)).fetchone()
    return _row(row) if row is not None else None


def atualizar_projeto(project_id: str, caminho_registro: Path | None = None, **campos: Any) -> dict[str, Any]:
    permitidos = {"status", "approved", "attempts", "diagnostic_path", "completed_at", "path", "description", "provider", "topics_input"}
    atualizacoes = {chave: valor for chave, valor in campos.items() if chave in permitidos}
    if "models" in campos:
        atualizacoes["models_json"] = json.dumps(campos["models"])
    if "topics" in campos:
        atualizacoes["topics_json"] = json.dumps(campos["topics"])
    atualizacoes["updated_at"] = _agora()
    partes = ", ".join(f"{chave} = ?" for chave in atualizacoes)
    with _conexao(caminho_registro) as db:
        db.execute(f"UPDATE projects SET {partes} WHERE id = ?", (*atualizacoes.values(), project_id))
        row = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if row is None:
        raise ValueError(f"Projeto não encontrado: {project_id}")
    projeto = _row(row)
    escrever_manifesto(projeto)
    return projeto


def listar_projetos(caminho_registro: Path | None = None) -> list[dict[str, Any]]:
    with _conexao(caminho_registro) as db:
        rows = db.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    return [_row(row) for row in rows]


def escrever_manifesto(projeto: Mapping[str, Any]) -> None:
    pasta = Path(str(projeto["path"]))
    if not pasta.exists():
        return
    manifesto = pasta / ".forja" / "project.json"
    manifesto.parent.mkdir(parents=True, exist_ok=True)
    dados = {chave: projeto.get(chave) for chave in (
        "id", "name", "description", "activity_type", "provider", "models", "topics_input", "topics",
        "status", "approved", "attempts", "diagnostic_path", "created_at", "updated_at", "completed_at",
    )}
    manifesto.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _row(row: sqlite3.Row) -> dict[str, Any]:
    projeto = dict(row)
    projeto["models"] = json.loads(projeto.pop("models_json") or "{}")
    projeto["topics"] = json.loads(projeto.pop("topics_json") or "[]")
    projeto["approved"] = None if projeto["approved"] is None else bool(projeto["approved"])
    return projeto
