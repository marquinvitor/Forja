"""Painel local de configuração da Forja."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from catalogo_modelos import atualizar_catalogo_openai, carregar_catalogo, familias_openai, resolver_chave
from llm_config import MODELOS_PADRAO
from persistencia import (
    carregar_settings,
    diretorio_dados,
    arquivo_cache_padroes,
    arquivo_cache_modelos,
    carregar_ultimo_projeto,
    salvar_ultimo_projeto,
    limpar_ultimo_projeto,
    resolver_caminho_repo,
    resolver_output_dir,
    salvar_settings,
)
from projetos import atualizar_projeto, listar_projetos, registrar_projeto
from repositorio import caminho_repositorio_automatico
from terminais import abrir_acompanhamento, detectar_terminais
from topicos_poo import TOPICOS


HTML_PATH = Path(__file__).with_name("forja_panel.html")
_JOBS: dict[str, subprocess.Popen[str]] = {}


def _validar_nome_projeto(nome: str) -> str:
    nome = nome.strip().replace(" ", "_")
    if not nome or nome in {".", ".."} or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in nome):
        raise ValueError("O nome deve conter apenas letras, números, '_' ou '-'.")
    return nome


def _iniciar_projeto(settings_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    descricao = str(payload.get("description") or "").strip()
    if not descricao:
        raise ValueError("A descrição do projeto é obrigatória.")
    nome = _validar_nome_projeto(str(payload.get("name") or ""))
    settings = carregar_settings(settings_path)
    output_dir = Path(resolver_output_dir(settings))
    projeto_path = output_dir / nome
    if projeto_path.exists():
        raise ValueError(f"Já existe um projeto em {projeto_path}.")
    environment = _environment(settings, settings_path)
    topics_input = payload.get("topics_input")
    topics = payload.get("topics", [])
    if not isinstance(topics, list) or any(not isinstance(item, str) for item in topics):
        raise ValueError("topics deve ser uma lista de IDs de tópicos.")
    topics = [item for item in topics if item in TOPICOS]
    if topics_input is None:
        topics_input = ", ".join(topics)
    if not isinstance(topics_input, str):
        raise ValueError("topics_input deve ser texto.")
    max_attempts = payload.get("max_attempts", 3)
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or not 1 <= max_attempts <= 10:
        raise ValueError("max_attempts deve ser um número entre 1 e 10.")
    projeto = registrar_projeto(
        nome, projeto_path, descricao, provider=environment["provider"],
        models=environment["models"], topics=topics, topics_input=topics_input,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    comando = [sys.executable, "-u", str(Path(__file__).with_name("forja.py")),
               "--settings", str(settings_path.parent), "--description", descricao,
               "--name", nome, "--yes"]
    if topics:
        comando.extend(["--topics", ",".join(topics)])
    comando.extend(["--max-attempts", str(max_attempts)])
    if payload.get("generate_cover") and environment["provider"] == "openai":
        comando.append("--cover")
    log_path = projeto_path / "generation.log"
    projeto_path.mkdir(parents=True, exist_ok=True)
    log_path.touch()
    if settings.get("open_terminal_on_project"):
        abrir_acompanhamento(log_path, str(settings.get("terminal_name") or "auto"))

    def executar() -> None:
        atualizar_projeto(projeto["id"], status="generating")
        try:
            projeto_path.mkdir(parents=True, exist_ok=True)
            ambiente = os.environ.copy()
            ambiente["PYTHONUNBUFFERED"] = "1"
            processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, bufsize=1, cwd=str(Path(__file__).parent.parent),
                                        env=ambiente)
            _JOBS[projeto["id"]] = processo
            with log_path.open("w", encoding="utf-8") as log:
                assert processo.stdout is not None
                for linha in processo.stdout:
                    log.write(linha)
                    log.flush()
                    texto = linha.lower()
                    if "analisando tópicos" in texto:
                        atualizar_projeto(projeto["id"], status="analyzing")
                    elif "gerando questão" in texto:
                        atualizar_projeto(projeto["id"], status="generating")
                    elif "auditoria técnica" in texto or "compilando" in texto:
                        atualizar_projeto(projeto["id"], status="auditing")
                    elif "enviando relatório" in texto or "falhas detectadas" in texto:
                        atualizar_projeto(projeto["id"], status="correcting")
                processo.wait()
            aprovado = processo.returncode == 0 and not (projeto_path / "diagnostico_final.txt").exists()
            atualizar_projeto(projeto["id"], status="approved" if aprovado else "failed",
                              approved=aprovado, attempts=max_attempts,
                              diagnostic_path=str(projeto_path / "diagnostico_final.txt") if (projeto_path / "diagnostico_final.txt").exists() else (str(log_path) if not aprovado else None),
                              completed_at=datetime.now(timezone.utc).isoformat())
        except Exception as error:  # noqa: BLE001
            projeto_path.mkdir(parents=True, exist_ok=True)
            log_path.write_text(f"{type(error).__name__}: {error}\n", encoding="utf-8")
            atualizar_projeto(projeto["id"], status="failed", approved=False, attempts=max_attempts,
                              diagnostic_path=str(log_path), completed_at=datetime.now(timezone.utc).isoformat())
        finally:
            _JOBS.pop(projeto["id"], None)

    threading.Thread(target=executar, daemon=True).start()
    return projeto


def _key_status(settings: dict[str, Any], provider: str) -> dict[str, Any]:
    direct_name = f"{provider}_api_key"
    file_name = f"{provider}_api_key_file"
    direct = str(settings.get(direct_name) or "").strip()
    environment = str(os.environ.get(direct_name.upper()) or "").strip()
    file_value = str(settings.get(file_name) or "").strip()
    file_path = Path(file_value).expanduser() if file_value else None
    file_configured = False
    if file_path and file_path.is_file():
        try:
            file_configured = bool(file_path.read_text(encoding="utf-8").strip())
        except OSError:
            file_configured = False
    source = "direct" if direct else "environment" if environment else "file" if file_configured else "none"
    return {
        "configured": bool(direct or environment or file_configured),
        "source": source,
        "file_path": file_value,
    }


def _environment(settings: dict[str, Any], settings_path: Path) -> dict[str, Any]:
    provider = str(settings.get("llm_provider") or "gemini")
    catalogo = carregar_catalogo()
    models = {
        role: settings.get(f"llm_model_{role}") or MODELOS_PADRAO[provider][role]
        for role in ("rascunho", "revisao", "auditoria")
    }
    return {
        "settings_path": str(settings_path),
        "cache_path": str(arquivo_cache_padroes()),
        "models_cache_path": str(arquivo_cache_modelos()),
        "provider": provider,
        "providers": {
            name: {
                "key": _key_status(settings, name),
                "models": MODELOS_PADRAO[name],
                "available_models": catalogo.get(name, list(MODELOS_PADRAO[name].values())),
                "families": familias_openai(
                    catalogo.get(name, list(MODELOS_PADRAO[name].values()))
                ) if name == "openai" else {},
            }
            for name in MODELOS_PADRAO
        },
        "models": models,
        "repo_dir": resolver_caminho_repo(settings),
        "automatic_repo_dir": str(caminho_repositorio_automatico()),
        "terminal_name": settings.get("terminal_name") or "auto",
        "open_terminal_on_project": bool(settings.get("open_terminal_on_project")),
        "terminals": detectar_terminais(),
        "topics_options": [{"id": key, "title": value["titulo"]} for key, value in TOPICOS.items()],
        "output_dir": resolver_output_dir(settings),
        "default_output_dir": str(diretorio_dados()),
    }


def abrir_arquivo_local(caminho: Path) -> None:
    """Abre um arquivo no aplicativo padrão do sistema operacional."""
    if sys.platform == "win32":
        os.startfile(str(caminho))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(caminho)], start_new_session=True)
    else:
        subprocess.Popen(["xdg-open", str(caminho)], start_new_session=True)


def _merge_payload(settings: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(settings)
    simple_fields = {
        "llm_provider", "llm_model_rascunho", "llm_model_revisao",
        "llm_model_auditoria", "caminho_repo",
        "terminal_name",
    }
    for field in simple_fields:
        if field in payload:
            result[field] = payload[field]
    if "output_dir" in payload:
        result["output_dir"] = payload["output_dir"] or None
    if "open_terminal_on_project" in payload:
        result["open_terminal_on_project"] = bool(payload["open_terminal_on_project"])
    for provider in MODELOS_PADRAO:
        direct = f"{provider}_api_key"
        file_path = f"{provider}_api_key_file"
        # Campo de chave vazio preserva a chave existente, evitando apagar um
        # segredo por acidente ao apenas trocar o modelo.
        if str(payload.get(direct) or "").strip():
            result[direct] = str(payload[direct]).strip()
        if file_path in payload:
            result[file_path] = str(payload[file_path] or "").strip() or None
    return result


def serve(settings_path: Path, port: int = 8765, open_browser: bool = True) -> None:
    token = secrets.token_urlsafe(24)
    page = HTML_PATH.read_text(encoding="utf-8").replace("__FORJA_TOKEN__", token)

    class Handler(BaseHTTPRequestHandler):
        def _authorized(self) -> bool:
            return self.headers.get("X-Forja-Token") == token

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, value: Any) -> None:
            self._send(status, json.dumps(value, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def _projects(self) -> list[dict[str, Any]]:
            projetos = listar_projetos()
            for projeto in projetos:
                log_path = Path(projeto["path"]) / "generation.log"
                try:
                    projeto["log_tail"] = log_path.read_text(encoding="utf-8")[-4000:] if log_path.exists() else ""
                except OSError:
                    projeto["log_tail"] = ""
            return projetos

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/":
                self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
                return
            if not self._authorized():
                self._json(403, {"error": "Acesso local não autorizado"})
                return
            if urlsplit(self.path).path == "/api/environment":
                try:
                    self._json(200, _environment(carregar_settings(settings_path), settings_path))
                except (OSError, ValueError) as error:
                    self._json(400, {"error": str(error)})
                return
            if urlsplit(self.path).path == "/api/projects":
                self._json(200, {"projects": self._projects()})
                return
            if urlsplit(self.path).path == "/api/last-project":
                self._json(200, carregar_ultimo_projeto())
                return
            if urlsplit(self.path).path == "/api/projects/check-name":
                from urllib.parse import parse_qs
                nome = parse_qs(urlsplit(self.path).query).get("name", [""])[0]
                try:
                    nome = _validar_nome_projeto(nome)
                    settings = carregar_settings(settings_path)
                    caminho = Path(resolver_output_dir(settings)) / nome
                    disponivel = not caminho.exists()
                    self._json(200, {"available": disponivel, "path": str(caminho),
                                     "error": None if disponivel else "Já existe uma pasta com esse nome."})
                except ValueError as error:
                    self._json(200, {"available": False, "path": None, "error": str(error)})
                return
            self._json(404, {"error": "Rota não encontrada"})

        def do_POST(self) -> None:  # noqa: N802
            if not self._authorized():
                self._json(403, {"error": "Acesso local não autorizado"})
                return
            route = urlsplit(self.path).path
            if route == "/api/open-settings":
                try:
                    abrir_arquivo_local(settings_path)
                    self._json(200, {"opened": str(settings_path)})
                except OSError as error:
                    self._json(400, {"error": f"Não foi possível abrir {settings_path}: {error}"})
                return
            if route == "/api/models/update":
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    payload = json.loads(self.rfile.read(length) or b"{}")
                    provider = str(payload.get("provider") or "openai").lower()
                    if provider != "openai":
                        raise ValueError("A atualização automática está disponível para OpenAI.")
                    modelos = atualizar_catalogo_openai(resolver_chave(carregar_settings(settings_path), provider))
                    self._json(200, {"provider": provider, "models": modelos,
                                     "environment": _environment(carregar_settings(settings_path), settings_path)})
                except (OSError, ValueError, json.JSONDecodeError) as error:
                    self._json(400, {"error": str(error)})
                return
            if route == "/api/last-project":
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    payload = json.loads(self.rfile.read(length) or b"{}")
                    if payload.get("clear"):
                        limpar_ultimo_projeto()
                    else:
                        salvar_ultimo_projeto({
                            "name": str(payload.get("name") or ""),
                            "description": str(payload.get("description") or ""),
                            "topics_input": str(payload.get("topics_input") or ""),
                            "generate_cover": bool(payload.get("generate_cover")),
                            "max_attempts": int(payload.get("max_attempts") or 3),
                        })
                    self._json(200, carregar_ultimo_projeto())
                except (OSError, ValueError, json.JSONDecodeError) as error:
                    self._json(400, {"error": str(error)})
                return
            if route == "/api/projects":
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length > 128 * 1024:
                        raise ValueError("Payload de projeto muito grande")
                    payload = json.loads(self.rfile.read(length) or b"{}")
                    if not isinstance(payload, dict):
                        raise ValueError("O payload deve ser um objeto JSON")
                    self._json(202, _iniciar_projeto(settings_path, payload))
                except (OSError, ValueError, json.JSONDecodeError) as error:
                    self._json(400, {"error": str(error)})
                return
            if route.startswith("/api/projects/") and route.endswith("/open"):
                project_id = route.split("/")[3]
                projeto = next((item for item in listar_projetos() if item["id"] == project_id), None)
                if not projeto:
                    self._json(404, {"error": "Projeto não encontrado"})
                else:
                    try:
                        abrir_arquivo_local(Path(projeto["path"]))
                        self._json(200, {"opened": projeto["path"]})
                    except OSError as error:
                        self._json(400, {"error": str(error)})
                return
            if route != "/api/settings":
                self._json(404, {"error": "Rota não encontrada"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length > 256 * 1024:
                    raise ValueError("Payload de configuração muito grande")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("O payload deve ser um objeto JSON")
                updated = salvar_settings(settings_path, _merge_payload(carregar_settings(settings_path), payload))
                self._json(200, _environment(updated, settings_path))
            except (OSError, ValueError, json.JSONDecodeError) as error:
                self._json(400, {"error": str(error)})

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Painel da Forja: {url}")
    print("Pressione Ctrl+C para encerrar.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPainel encerrado.")
    finally:
        server.server_close()
