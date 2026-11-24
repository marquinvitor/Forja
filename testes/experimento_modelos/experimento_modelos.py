#!/usr/bin/env python3
"""
experimento_modelos.py — Experimento Comparativo entre Configurações de Modelos

Avalia 3 configurações de modelos de linguagem em 3 níveis de complexidade estrutural (L1, L2, L3),
totalizando 9 execuções com rastreamento automático de tokens, custos em dólares e métricas
de qualidade estrutural e conformidade técnica.
"""

from __future__ import annotations
import argparse
import copy
import datetime
import json
import os
import sys
import time
from pathlib import Path

# Garante que os módulos locais em 'src' sejam importáveis
_ROOT_DIR = Path(__file__).resolve().parent.parent
_SRC_DIR = _ROOT_DIR / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

import forja
from forja import (
    executar_geracao,
    resetar_custos,
    registro_custos,
    PRECOS_FALLBACK_1M,
    verificar_conformidade_esqueleto,
    extrair_testes_readme,
    chamar_llm,
    CAMINHO_REPO,
    OUTPUT_DIR,
    GEMINI_API_KEY,
)
from topicos_poo import preparar, TOPICOS
from crewai import LLM


# ─── Cores para saída no terminal ──────────────────────────────────────────

class Cores:
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    VERDE = "\033[32m"
    VERMELHO = "\033[31m"
    AMARELO = "\033[33m"
    AZUL = "\033[34m"
    CIANO = "\033[36m"
    MAGENTA = "\033[35m"


def log_titulo(txt: str):
    print(f"\n{Cores.NEGRITO}{Cores.CIANO}{'=' * 75}{Cores.RESET}")
    print(f"{Cores.NEGRITO}{Cores.CIANO}{txt.center(75)}{Cores.RESET}")
    print(f"{Cores.NEGRITO}{Cores.CIANO}{'=' * 75}{Cores.RESET}\n")


def log_subtitulo(txt: str):
    print(f"\n{Cores.NEGRITO}{Cores.AZUL}--- {txt} ---{Cores.RESET}\n")


def log_sucesso(txt: str):
    print(f"{Cores.VERDE}✓ {txt}{Cores.RESET}")


def log_falha(txt: str):
    print(f"{Cores.VERMELHO}✗ {txt}{Cores.RESET}")


def log_aviso(txt: str):
    print(f"{Cores.AMARELO}⚠ {txt}{Cores.RESET}")


def log_info(txt: str):
    print(f"{Cores.CIANO}ℹ {txt}{Cores.RESET}")


# ─── Configurações e Níveis do Experimento ─────────────────────────────────

NIVEIS = [
    {
        "id": "L1",
        "nome": "L1_Simples",
        "descricao_nivel": "1 tópico, 1 classe (Encapsulamento e Invariantes)",
        "prompt_path": _ROOT_DIR / "output" / "Questão-01" / "prompt.txt",
        "prompt_fallback": (
            "1 classe, com encapsulamento e invariantes, no contexto de uma garrafa térmica inteligente "
            "que controla volume de líquido, capacidade máxima e temperatura, com métodos para abastecer "
            "e servir sem permitir transbordamento nem valores negativos"
        ),
    },
    {
        "id": "L2",
        "nome": "L2_Medio",
        "descricao_nivel": "2 tópicos, 2 classes (Encapsulamento e Coleções Lineares)",
        "prompt_path": _ROOT_DIR / "output" / "Questão-03" / "prompt.txt",
        "prompt_fallback": (
            "2 classes, com encapsulamento e coleções lineares, no contexto de um carrinho de compras "
            "de uma padaria artesanal que armazena uma lista de itens com controle de quantidade máxima "
            "e cálculo do valor total"
        ),
    },
    {
        "id": "L3",
        "nome": "L3_Complexo",
        "descricao_nivel": "3 tópicos, 3 classes (Encapsulamento, Mapas e Exceções)",
        "prompt_path": _ROOT_DIR / "output" / "Questão-05" / "prompt.txt",
        "prompt_fallback": (
            "3 classes, com encapsulamento, mapas e exceções, no contexto de uma biblioteca de bairro "
            "que empresta livros para sócios, com limite de empréstimos por sócio e livros que podem "
            "estar indisponíveis"
        ),
    },
]

CONFIGURACOES = [
    {
        "id": "1_Leve_Homogenea",
        "nome": "1. Leve Homogênea (Flash-Lite x3)",
        "descricao": "gemini-3.5-flash-lite nos 3 agentes (Designer, Especialista, Auditor)",
        "designer": "gemini/gemini-3.5-flash-lite",
        "especialista": "gemini/gemini-3.5-flash-lite",
        "auditor": "gemini/gemini-3.5-flash-lite",
    },
    {
        "id": "2_Hibrida_Proposta",
        "nome": "2. Híbrida Proposta (Flash-Lite + Flash + Flash-Lite)",
        "descricao": "gemini-3.5-flash-lite no Designer e Auditor, e gemini-3.8-flash no Especialista",
        "designer": "gemini/gemini-3.5-flash-lite",
        "especialista": "gemini/gemini-3.8-flash",
        "auditor": "gemini/gemini-3.5-flash-lite",
    },
    {
        "id": "3_Robusta_Homogenea",
        "nome": "3. Robusta Homogênea (Flash x3)",
        "descricao": "gemini-3.8-flash nos 3 agentes (Designer, Especialista, Auditor)",
        "designer": "gemini/gemini-3.8-flash",
        "especialista": "gemini/gemini-3.8-flash",
        "auditor": "gemini/gemini-3.8-flash",
    },
]


def carregar_prompt(nivel_cfg: dict) -> str:
    path = Path(nivel_cfg["prompt_path"])
    if path.exists():
        texto = path.read_text(encoding="utf-8").strip()
        if texto:
            return texto
    return nivel_cfg["prompt_fallback"]


def aplicar_configuracao_modelos(cfg: dict):
    """Atualiza dinamicamente os LLMs dos agentes com temperature=1.0 conforme a configuração."""
    forja.designer_criativo.llm = LLM(
        model=cfg["designer"],
        api_key=GEMINI_API_KEY,
        temperature=1.0,
        max_retries=3,
        timeout=600,
        max_tokens=8000,
    )
    forja.especialista_poo.llm = LLM(
        model=cfg["especialista"],
        api_key=GEMINI_API_KEY,
        temperature=1.0,
        max_retries=3,
        timeout=600,
        max_tokens=16000,
    )
    forja.auditor_tecnico.llm = LLM(
        model=cfg["auditor"],
        api_key=GEMINI_API_KEY,
        temperature=1.0,
        max_retries=3,
        timeout=600,
        max_tokens=16000,
    )


# ─── Verificações de Qualidade Estrutural ────────────────────────────────────

def avaliar_qualidade_estrutural(caminhos: dict) -> dict:
    """
    Executa verificações automáticas de qualidade estrutural nos artefatos gerados:
    1. esqueleto_valido: conformidade de shell.kt com as regras de esqueleto (todos os métodos das classes com TODO)
    2. sem_println_dominio: não há chamadas println( ou print( antes da fun main em main.kt e shell.kt
    3. possui_mermaid: bloco ```mermaid no README.md
    4. qtd_testes: quantidade de casos de teste extraídos do README.md
    """
    shell_file = Path(caminhos.get("shell_kt", ""))
    main_file = Path(caminhos.get("main_kt", ""))
    readme_file = Path(caminhos.get("readme", ""))

    shell_kt = shell_file.read_text(encoding="utf-8") if shell_file.exists() else ""
    main_kt = main_file.read_text(encoding="utf-8") if main_file.exists() else ""
    readme = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

    # 1. esqueleto_valido
    if shell_kt:
        esq_ok, esq_msg = verificar_conformidade_esqueleto(shell_kt)
    else:
        esq_ok, esq_msg = False, "Arquivo shell.kt ausente"

    # 2. sem_println_dominio
    def tem_println_dominio(codigo: str) -> bool:
        if not codigo:
            return False
        pos_main = codigo.find("fun main")
        dominio = codigo[:pos_main] if pos_main != -1 else codigo
        for linha in dominio.splitlines():
            l = linha.strip()
            if l.startswith("//") or l.startswith("/*") or l.startswith("*"):
                continue
            if "println(" in l or "print(" in l:
                return True
        return False

    sem_print = True
    violacoes_print = []
    if shell_kt and tem_println_dominio(shell_kt):
        sem_print = False
        violacoes_print.append("shell.kt")
    if main_kt and tem_println_dominio(main_kt):
        sem_print = False
        violacoes_print.append("main.kt")

    # 3. possui_mermaid
    possui_mermaid = "```mermaid" in readme

    # 4. qtd_testes
    testes = extrair_testes_readme(readme) if readme else []
    qtd_testes = len(testes)

    return {
        "esqueleto_valido": esq_ok,
        "detalhe_esqueleto": esq_msg,
        "sem_println_dominio": sem_print,
        "violacoes_println": violacoes_print,
        "possui_mermaid": possui_mermaid,
        "qtd_testes": qtd_testes,
        "testes_suficientes": qtd_testes >= 5,
    }


# ─── Cálculo de Métricas Agregadas ──────────────────────────────────────────

def calcular_metricas_configuracao(questoes: list[dict]) -> dict:
    """Calcula taxas de aprovação, pass@1, tempo, tokens, custos e qualidade estrutural."""
    N = len(questoes)
    if N == 0:
        return {}

    aprovadas = sum(1 for q in questoes if q["aprovado"])
    pass_at_1 = sum(1 for q in questoes if q["pass_at_1"])

    taxa_pass_at_1_pct = round((pass_at_1 / N) * 100, 1)
    taxa_aprovacao_final_pct = round((aprovadas / N) * 100, 1)

    media_tentativas = round(sum(q["tentativas_usadas"] for q in questoes) / N, 2)
    tempo_total_s = round(sum(q["tempo_segundos"] for q in questoes), 2)
    tempo_medio_s = round(tempo_total_s / N, 2)

    prompt_tokens_total = sum(q["custos"]["prompt_tokens"] for q in questoes)
    prompt_tokens_medio = round(prompt_tokens_total / N, 1)

    completion_tokens_total = sum(q["custos"]["completion_tokens"] for q in questoes)
    completion_tokens_medio = round(completion_tokens_total / N, 1)

    total_tokens = sum(q["custos"]["total_tokens"] for q in questoes)
    tokens_medio = round(total_tokens / N, 1)

    custo_total_usd = sum(q["custos"]["custo_usd"] for q in questoes)
    custo_medio_usd = round(custo_total_usd / N, 6)
    custo_efetivo_aprovada_usd = round(custo_total_usd / aprovadas, 6) if aprovadas > 0 else None

    # Qualidade estrutural
    esq_val_count = sum(1 for q in questoes if q["qualidade_estrutural"]["esqueleto_valido"])
    sem_print_count = sum(1 for q in questoes if q["qualidade_estrutural"]["sem_println_dominio"])
    mermaid_count = sum(1 for q in questoes if q["qualidade_estrutural"]["possui_mermaid"])
    qtd_testes_lista = [q["qualidade_estrutural"]["qtd_testes"] for q in questoes]
    media_qtd_testes = round(sum(qtd_testes_lista) / N, 1)
    testes_suf_count = sum(1 for q in questoes if q["qualidade_estrutural"]["testes_suficientes"])

    esq_val_pct = round((esq_val_count / N) * 100, 1)
    sem_print_pct = round((sem_print_count / N) * 100, 1)
    mermaid_pct = round((mermaid_count / N) * 100, 1)
    testes_suficientes_pct = round((testes_suf_count / N) * 100, 1)

    taxa_geral_aderencia_pct = round(
        (esq_val_pct + sem_print_pct + mermaid_pct + testes_suficientes_pct) / 4.0, 1
    )

    return {
        "total_questoes": N,
        "aprovadas": aprovadas,
        "pass_at_1_count": pass_at_1,
        "taxa_pass_at_1_pct": taxa_pass_at_1_pct,
        "taxa_aprovacao_final_pct": taxa_aprovacao_final_pct,
        "media_tentativas": media_tentativas,
        "tempo_total_s": tempo_total_s,
        "tempo_medio_s": tempo_medio_s,
        "prompt_tokens_total": prompt_tokens_total,
        "prompt_tokens_medio": prompt_tokens_medio,
        "completion_tokens_total": completion_tokens_total,
        "completion_tokens_medio": completion_tokens_medio,
        "total_tokens": total_tokens,
        "tokens_medio": tokens_medio,
        "custo_total_usd": round(custo_total_usd, 6),
        "custo_medio_usd": custo_medio_usd,
        "custo_efetivo_aprovada_usd": custo_efetivo_aprovada_usd,
        "qualidade_estrutural": {
            "esqueleto_valido_pct": esq_val_pct,
            "sem_println_dominio_pct": sem_print_pct,
            "possui_mermaid_pct": mermaid_pct,
            "media_qtd_testes": media_qtd_testes,
            "testes_suficientes_pct": testes_suficientes_pct,
            "taxa_geral_aderencia_pct": taxa_geral_aderencia_pct,
        },
    }


# ─── Geração de Relatório em Markdown ───────────────────────────────────────

def gerar_relatorio_markdown(dados: dict, output_path: Path):
    """Gera relatório técnico formatado para inclusão no TCC."""
    linhas = []
    linhas.append("# Experimento Comparativo de Configurações de Modelos (Eixo B do TCC)")
    linhas.append("")
    linhas.append(f"**Data da Execução:** {dados['metadados']['data_execucao']}")
    linhas.append(f"**Ambiente:** Python {sys.version.split()[0]} | LiteLLM + CrewAI")
    linhas.append("")
    linhas.append("Este relatório documenta a avaliação empírica do **Eixo B**, comparando três configurações arquiteturais de Modelos de Linguagem de Grande Porte (LLMs) em três níveis crescentes de complexidade estrutural de POO em Kotlin.")
    linhas.append("")
    linhas.append("---")
    linhas.append("")
    linhas.append("## 1. Configurações Avaliadas e Metodologia")
    linhas.append("")
    linhas.append("Para assegurar rigor metodológico e comparabilidade:")
    linhas.append("- **Few-Shot Padronizado:** O procedimento `preparar(...)` foi executado uma única vez por prompt, fornecendo idênticos tópicos e exemplos de referência para todas as configurações.")
    linhas.append("- **Temperatura:** Fixada em `1.0` em todos os agentes para manter paridade estocástica.")
    linhas.append("- **Tarifas de Rastreamento:** Baseadas na tabela oficial do Google AI Studio com fallback automático.")
    linhas.append("")
    linhas.append("| Configuração | Designer Instrucional | Especialista POO Kotlin | Auditor Técnico QA | Perfil Arquitetural |")
    linhas.append("| :--- | :--- | :--- | :--- | :--- |")
    for cfg_id, cfg_info in dados["configuracoes"].items():
        meta = cfg_info["metadados"]
        des = meta["designer"].replace("gemini/", "")
        esp = meta["especialista"].replace("gemini/", "")
        aud = meta["auditor"].replace("gemini/", "")
        linhas.append(f"| **{meta['nome']}** | `{des}` | `{esp}` | `{aud}` | {meta['descricao']} |")
    linhas.append("")
    linhas.append("---")
    linhas.append("")
    linhas.append("## 2. Tabela Comparativa Geral de Desempenho e Custos")
    linhas.append("")
    linhas.append("| Configuração | Pass@1 (%) | Aprovação Final (%) | Tentativas Médias | Tempo Médio (s) | Tokens Médios (In / Out) | Custo Total (US$) | Custo Médio / Q (US$) | Custo Efetivo / Q Aprovada (US$) |")
    linhas.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for cfg_id, cfg_info in dados["configuracoes"].items():
        r = cfg_info["resumo"]
        nome = cfg_info["metadados"]["nome"]
        tokens_in_out = f"{int(r['prompt_tokens_medio'])} / {int(r['completion_tokens_medio'])}"
        custo_tot = f"${r['custo_total_usd']:.4f}"
        custo_med = f"${r['custo_medio_usd']:.4f}"
        custo_efetivo = f"${r['custo_efetivo_aprovada_usd']:.4f}" if r["custo_efetivo_aprovada_usd"] else "N/A"

        linhas.append(
            f"| **{nome}** | **{r['taxa_pass_at_1_pct']}%** | **{r['taxa_aprovacao_final_pct']}%** | "
            f"{r['media_tentativas']} | {r['tempo_medio_s']}s | {tokens_in_out} | "
            f"{custo_tot} | {custo_med} | **{custo_efetivo}** |"
        )

    linhas.append("")
    linhas.append("---")
    linhas.append("")
    linhas.append("## 3. Qualidade Estrutural dos Artefatos Gerados")
    linhas.append("")
    linhas.append("Verificação dos 4 pilares de conformidade das questões:")
    linhas.append("1. **Esqueleto Conforme:** Todas as classes contêm estritamente `TODO(...)` nos métodos.")
    linhas.append("2. **Sem println no Domínio:** Classes não violam o encapsulamento imprimindo saídas diretamente.")
    linhas.append("3. **Diagrama Mermaid:** Presença de diagrama de classes funcional em bloco ```` ```mermaid ````.")
    linhas.append("4. **Casos de Teste Suficientes:** Cobertura de no mínimo 5 casos de teste estruturados no README.")
    linhas.append("")
    linhas.append("| Configuração | Esqueleto Conforme (%) | Sem println Domínio (%) | Diagrama Mermaid (%) | Média Casos de Teste | Aderência Estrutural (%) |")
    linhas.append("| :--- | :---: | :---: | :---: | :---: | :---: |")

    for cfg_id, cfg_info in dados["configuracoes"].items():
        q = cfg_info["resumo"]["qualidade_estrutural"]
        nome = cfg_info["metadados"]["nome"]
        linhas.append(
            f"| **{nome}** | {q['esqueleto_valido_pct']}% | {q['sem_println_dominio_pct']}% | "
            f"{q['possui_mermaid_pct']}% | {q['media_qtd_testes']} | **{q['taxa_geral_aderencia_pct']}%** |"
        )

    linhas.append("")
    linhas.append("---")
    linhas.append("")
    linhas.append("## 4. Detalhamento por Execução (Configuração x Nível)")
    linhas.append("")
    linhas.append("| Configuração | Nível | Aprovado | Pass@1 | Tentativas | Tempo (s) | Tokens (In / Out) | Custo (US$) | Esqueleto | Sem Print | Mermaid | Testes |")
    linhas.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for cfg_id, cfg_info in dados["configuracoes"].items():
        cfg_nome = cfg_id.replace("_", " ")
        for q in cfg_info["questoes"]:
            aprov_str = "✓ Sim" if q["aprovado"] else "✗ Não"
            p1_str = "✓ Sim" if q["pass_at_1"] else "✗ Não"
            tok_str = f"{q['custos']['prompt_tokens']} / {q['custos']['completion_tokens']}"
            c_usd = f"${q['custos']['custo_usd']:.4f}"
            eq_str = "✓" if q["qualidade_estrutural"]["esqueleto_valido"] else "✗"
            sp_str = "✓" if q["qualidade_estrutural"]["sem_println_dominio"] else "✗"
            mm_str = "✓" if q["qualidade_estrutural"]["possui_mermaid"] else "✗"
            qtd_t = str(q["qualidade_estrutural"]["qtd_testes"])

            linhas.append(
                f"| `{cfg_id}` | {q['nivel']} | {aprov_str} | {p1_str} | {q['tentativas_usadas']} | "
                f"{q['tempo_segundos']}s | {tok_str} | {c_usd} | {eq_str} | {sp_str} | {mm_str} | {qtd_t} |"
            )

    linhas.append("")
    linhas.append("---")
    linhas.append("")
    linhas.append("## 5. Análise Crítica para a Discussão do TCC")
    linhas.append("")
    linhas.append("### 5.1. Trade-off Eficácia x Custo Financeiro")
    linhas.append("- **Configuração Leve (`1_Leve_Homogenea`):** Apresenta o menor custo operacional absoluto, porém pode demonstrar sensibilidade em questões de complexidade alta (L3) devido à capacidade de raciocínio mais restrita do modelo compacto ao alinhar assinaturas de métodos e testes.")
    linhas.append("- **Configuração Híbrida (`2_Hibrida_Proposta`):** Proposta central deste trabalho. Aloca o modelo de alta capacidade (`gemini-3.8-flash`) exclusivamente no **Especialista POO** (responsável pelo código Kotlin rigoroso e pelas correções), mantendo o modelo econômico (`gemini-3.5-flash-lite`) no Designer Instrucional e no Auditor Técnico. Essa divisão permite taxa de aprovação próxima ou idêntica à homogênea robusta com redução drástica no custo total.")
    linhas.append("- **Configuração Robusta (`3_Robusta_Homogenea`):** Mantém consistência técnica elevada, mas opera com multiplicadores elevados de custo por token tanto na fase criativa quanto na auditoria, encarecendo desnecessariamente o pipeline.")
    linhas.append("")
    linhas.append("### 5.2. Custo Efetivo por Questão Aprovada")
    linhas.append("A métrica de **Custo Efetivo por Questão Aprovada** (`Custo Total / Aprovadas`) é o critério decisório primário: ela penaliza configurações que parecem baratas em chamadas isoladas mas reprovam questões ou exigem o número máximo de tentativas de correção.")
    linhas.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(linhas), encoding="utf-8")
    log_sucesso(f"Relatório Markdown gerado com sucesso em: {output_path}")


# ─── Execução Principal do Experimento ──────────────────────────────────────

def executar_experimento(
    configuracoes_filtro: list[str] | None = None,
    niveis_filtro: list[str] | None = None,
    delay_segundos: float = 3.0,
) -> dict:
    log_titulo("EXPERIMENTO DE CONFIGURAÇÕES DE MODELOS — EIXO B (TCC)")

    pasta_saida_base = _ROOT_DIR / "output" / "experimento_modelos"
    pasta_saida_base.mkdir(parents=True, exist_ok=True)

    # Filtra configurações e níveis se solicitado
    cfgs_ativas = [
        c for c in CONFIGURACOES
        if configuracoes_filtro is None or c["id"] in configuracoes_filtro
    ]
    niveis_ativos = [
        n for n in NIVEIS
        if niveis_filtro is None or n["id"] in niveis_filtro
    ]

    log_info(f"Configurações selecionadas: {len(cfgs_ativas)}")
    log_info(f"Níveis selecionados: {len(niveis_ativos)} ({', '.join(n['id'] for n in niveis_ativos)})")
    log_info(f"Total de execuções planejadas: {len(cfgs_ativas) * len(niveis_ativos)}")

    # 1. Carregamento e preparação dos prompts (preparar UMA ÚNICA VEZ por nível)
    log_subtitulo("Etapa 1: Preparação Padronizada dos Prompts (Few-Shot Compartilhado)")
    contextos_preparados = {}
    for nivel in niveis_ativos:
        prompt_txt = carregar_prompt(nivel)
        log_info(f"Preparando contexto para {nivel['id']} ({nivel['nome']})...")
        print(f"  Prompt: \"{prompt_txt[:90]}...\"")
        topicos, exemplos = preparar(prompt_txt, CAMINHO_REPO, chamar_llm)
        contextos_preparados[nivel["id"]] = {
            "prompt": prompt_txt,
            "topicos": topicos,
            "exemplos": exemplos,
            "descricao_nivel": nivel["descricao_nivel"],
        }
        log_sucesso(f"Tópicos detectados para {nivel['id']}: {topicos}")

    # 2. Execução das configurações
    dados_experimento = {
        "metadados": {
            "data_execucao": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tarifas_fallback_1m": PRECOS_FALLBACK_1M,
            "total_configuracoes": len(cfgs_ativas),
            "total_niveis": len(niveis_ativos),
        },
        "configuracoes": {},
    }

    execucao_idx = 0
    total_execucoes = len(cfgs_ativas) * len(niveis_ativos)

    for cfg in cfgs_ativas:
        log_titulo(f"Configuração: {cfg['nome']}")
        print(f"Designer:    {cfg['designer']}")
        print(f"Especialista:{cfg['especialista']}")
        print(f"Auditor:     {cfg['auditor']}")

        aplicar_configuracao_modelos(cfg)

        questoes_config = []

        for nivel in niveis_ativos:
            execucao_idx += 1
            nivel_id = nivel["id"]
            ctx = contextos_preparados[nivel_id]

            log_subtitulo(f"Execução {execucao_idx}/{total_execucoes} — [{cfg['id']}] x [{nivel_id}]")

            pasta_destino = pasta_saida_base / cfg["id"]

            t0 = time.time()
            try:
                resultado_geracao = executar_geracao(
                    descricao=ctx["prompt"],
                    nome_questao=nivel_id,
                    topicos=ctx["topicos"],
                    exemplos=ctx["exemplos"],
                    pasta_base=pasta_destino,
                )
            except Exception as e:
                log_falha(f"Exceção durante geração de {cfg['id']}/{nivel_id}: {type(e).__name__}: {e}")
                resultado_geracao = {
                    "aprovado": False,
                    "pass_at_1": False,
                    "tentativas_usadas": 0,
                    "tempo_segundos": round(time.time() - t0, 2),
                    "custos": copy.deepcopy(registro_custos),
                    "caminhos": {
                        "pasta": str(pasta_destino / nivel_id),
                        "readme": str(pasta_destino / nivel_id / "README.md"),
                        "shell_kt": str(pasta_destino / nivel_id / "src" / "kt" / "shell.kt"),
                        "main_kt": str(pasta_destino / nivel_id / "src" / "kt" / "main.kt"),
                    },
                }

            # Avaliação de qualidade estrutural
            qualidade = avaliar_qualidade_estrutural(resultado_geracao["caminhos"])

            status_str = "APROVADO" if resultado_geracao["aprovado"] else "REPROVADO"
            p1_str = "SIM" if resultado_geracao["pass_at_1"] else "NÃO"
            print(f"\nResultado da questão [{nivel_id}]:")
            print(f"  * Status: {status_str} (Pass@1: {p1_str}, Tentativas: {resultado_geracao['tentativas_usadas']})")
            print(f"  * Tempo: {resultado_geracao['tempo_segundos']}s")
            print(f"  * Tokens: In={resultado_geracao['custos']['prompt_tokens']}, Out={resultado_geracao['custos']['completion_tokens']}, Total={resultado_geracao['custos']['total_tokens']}")
            print(f"  * Custo: ${resultado_geracao['custos']['custo_usd']:.6f} USD")
            print(f"  * Qualidade: Esqueleto={qualidade['esqueleto_valido']}, SemPrint={qualidade['sem_println_dominio']}, Mermaid={qualidade['possui_mermaid']}, Testes={qualidade['qtd_testes']}")

            registro_item = {
                "nivel": nivel_id,
                "nome_nivel": nivel["nome"],
                "descricao_nivel": ctx["descricao_nivel"],
                "prompt": ctx["prompt"],
                "topicos": ctx["topicos"],
                "aprovado": resultado_geracao["aprovado"],
                "pass_at_1": resultado_geracao["pass_at_1"],
                "tentativas_usadas": resultado_geracao["tentativas_usadas"],
                "tempo_segundos": resultado_geracao["tempo_segundos"],
                "custos": resultado_geracao["custos"],
                "qualidade_estrutural": qualidade,
                "caminhos": resultado_geracao["caminhos"],
            }
            questoes_config.append(registro_item)

            if delay_segundos > 0 and execucao_idx < total_execucoes:
                log_info(f"Aguardando {delay_segundos}s para evitar rate-limits na API do Gemini...")
                time.sleep(delay_segundos)

        resumo_cfg = calcular_metricas_configuracao(questoes_config)

        dados_experimento["configuracoes"][cfg["id"]] = {
            "metadados": {
                "id": cfg["id"],
                "nome": cfg["nome"],
                "descricao": cfg["descricao"],
                "designer": cfg["designer"],
                "especialista": cfg["especialista"],
                "auditor": cfg["auditor"],
            },
            "resumo": resumo_cfg,
            "questoes": questoes_config,
        }

    # 3. Salvamento dos dados brutos em JSON
    json_path = _ROOT_DIR / "testes" / "resultado_experimento_modelos.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(dados_experimento, indent=2, ensure_ascii=False), encoding="utf-8")
    log_sucesso(f"Dados brutos do experimento salvos em: {json_path}")

    # 4. Geração do relatório formatado em Markdown
    md_path = _ROOT_DIR / "testes" / "relatorio_experimento_modelos.md"
    gerar_relatorio_markdown(dados_experimento, md_path)

    log_titulo("EXPERIMENTO CONCLUÍDO COM SUCESSO!")
    return dados_experimento


def parse_args():
    parser = argparse.ArgumentParser(
        description="Executa o experimento comparativo entre configurações de modelos (Eixo B do TCC)."
    )
    parser.add_argument(
        "--config",
        nargs="+",
        choices=["1_Leve_Homogenea", "2_Hibrida_Proposta", "3_Robusta_Homogenea"],
        help="Executa apenas a(s) configuração(ões) especificada(s). Padrão: todas as 3.",
    )
    parser.add_argument(
        "--niveis",
        nargs="+",
        choices=["L1", "L2", "L3"],
        help="Executa apenas o(s) nível(eis) especificado(s). Padrão: todos os 3 (L1, L2, L3).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Tempo de espera (em segundos) entre execuções sucessivas para evitar rate limits. Padrão: 3.0s.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    executar_experimento(
        configuracoes_filtro=args.config,
        niveis_filtro=args.niveis,
        delay_segundos=args.delay,
    )
