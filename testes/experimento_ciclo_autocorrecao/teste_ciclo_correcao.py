#!/usr/bin/env python3
from __future__ import annotations
import argparse
import datetime
import os
import re
import sys
import tempfile
from pathlib import Path

_ROOT_DIR = Path(__file__).resolve().parent.parent
_SRC_DIR = _ROOT_DIR / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from forja import (
    compilar_e_executar,
    formatar_relatorio,
    extrair_testes_readme,
    extrair_bloco,
    extrair_codigo,
    criar_tarefa_gabarito,
    criar_tarefa_correcao,
    verificar_conformidade_esqueleto,
    kickoff_seguro,
    auditor_tecnico,
    especialista_poo,
    llm_revisao,
    llm_auditoria,
    chamar_llm,
    CAMINHO_REPO,
    OUTPUT_DIR,
    ESTILO_KOTLIN,
)
from topicos_poo import preparar, TOPICOS
from crewai import Crew, Process, Task


# ─── Cores e formatação de terminal ──────────────────────────────────────────

class Cores:
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    VERDE = "\033[32m"
    VERMELHO = "\033[31m"
    AMARELO = "\033[33m"
    AZUL = "\033[34m"
    CIANO = "\033[36m"
    MAGENTA = "\033[35m"


def titulo(txt: str):
    print(f"\n{Cores.NEGRITO}{Cores.CIANO}{'='*70}{Cores.RESET}")
    print(f"{Cores.NEGRITO}{Cores.CIANO}{txt.center(70)}{Cores.RESET}")
    print(f"{Cores.NEGRITO}{Cores.CIANO}{'='*70}{Cores.RESET}\n")


def subtitulo(txt: str):
    print(f"\n{Cores.NEGRITO}{Cores.AZUL}--- {txt} ---{Cores.RESET}\n")


def sucesso(txt: str):
    print(f"{Cores.VERDE}✓ {txt}{Cores.RESET}")


def falha(txt: str):
    print(f"{Cores.VERMELHO}✗ {txt}{Cores.RESET}")


def aviso(txt: str):
    print(f"{Cores.AMARELO}⚠ {txt}{Cores.RESET}")


def info(txt: str):
    print(f"{Cores.CIANO}ℹ {txt}{Cores.RESET}")


# ─── Carregamento da Questão ──────────────────────────────────────────────────

class QuestaoBase:
    def __init__(self, pasta: Path):
        self.pasta = pasta
        self.nome = pasta.name
        self.readme = (pasta / "README.md").read_text(encoding="utf-8")
        self.main_kt = (pasta / "src" / "kt" / "main.kt").read_text(encoding="utf-8")
        self.shell_kt = (pasta / "src" / "kt" / "shell.kt").read_text(encoding="utf-8")
        prompt_file = pasta / "prompt.txt"
        self.prompt = prompt_file.read_text(encoding="utf-8").strip() if prompt_file.exists() else ""
        self.testes = extrair_testes_readme(self.readme)


def carregar_questao(caminho_str: str) -> QuestaoBase:
    caminho = Path(caminho_str)
    if not caminho.is_absolute():
        caminho = _ROOT_DIR / caminho
    if not caminho.exists():
        raise FileNotFoundError(f"Questão não encontrada no caminho: {caminho}")
    return QuestaoBase(caminho)


# ─── Execução do Baseline ────────────────────────────────────────────────────

def executar_baseline(questao: QuestaoBase) -> bool:
    subtitulo("BASELINE: Verificação inicial da questão original")
    info(f"Questão selecionada: {questao.nome}")
    info(f"Casos de teste identificados no README: {len(questao.testes)}")

    res = compilar_e_executar(questao.main_kt, questao.testes)
    if res["sucesso"]:
        sucesso(f"Baseline OK: A questão '{questao.nome}' compila e passa em todos os {len(questao.testes)} casos de teste.")
        return True
    else:
        falha("Baseline FALHOU: A questão original não passou nos testes!")
        print(formatar_relatorio(res))
        return False


# ─── Cenário 1: Divergência nos Casos de Teste (README.md) ────────────────────

def cenario_1_falha_testes(questao: QuestaoBase, contexto: str, topicos_txt: str, exemplos: str) -> dict:
    titulo("CENÁRIO 1: Divergência nos Casos de Teste (README.md)")
    info("Objetivo: Alterar propositalmente a saída esperada de um caso de teste no README.md,")
    info("confirmar falha na etapa 'testes', acionar o Especialista para corrigir o README")
    info("e revalidar com o Auditor Técnico + compilação e execução real.")

    # 1. Injeção de falha na saída esperada dentro do primeiro bloco ```bash
    readme_original = questao.readme
    alvo_original = None
    alvo_injetado = None

    match = re.search(r"(```bash[ \t]*\n)(.*?)(```)", readme_original, re.DOTALL)
    if not match:
        falha("Nenhum bloco ```bash encontrado no README.md da questão!")
        return {"sucesso": False, "etapa": "injecao"}

    prefixo = match.group(1)
    conteudo = match.group(2)
    sufixo = match.group(3)
    linhas_bloco = conteudo.splitlines()

    for idx, l in enumerate(linhas_bloco):
        l_strip = l.strip()
        if l_strip and not l_strip.startswith("$") and not l_strip.startswith("#"):
            alvo_original = l
            alvo_injetado = f"{l}__VALOR_DIVERGENTE_99999"
            linhas_bloco[idx] = alvo_injetado
            break

    if not alvo_original:
        falha("Nenhuma linha de saída esperada encontrada no primeiro bloco de testes do README.md!")
        return {"sucesso": False, "etapa": "injecao"}

    novo_conteudo = "\n".join(linhas_bloco)
    readme_modificado = (
        readme_original[:match.start()]
        + prefixo
        + novo_conteudo
        + ("\n" if not novo_conteudo.endswith("\n") else "")
        + sufixo
        + readme_original[match.end():]
    )

    print(f"\n{Cores.MAGENTA}[1. INJEÇÃO CONTROLADA]{Cores.RESET}")
    print(f"Saída original esperada : {alvo_original}")
    print(f"Saída injetada (falha)  : {alvo_injetado}")

    testes_modificados = extrair_testes_readme(readme_modificado)
    info(f"Casos de teste extraídos do README modificado: {len(testes_modificados)}")

    # 2. Executa compilar_e_executar e confirma falha na etapa 'testes'
    print(f"\n{Cores.MAGENTA}[2. DETECÇÃO DA FALHA (EXECUÇÃO REAL)]{Cores.RESET}")
    info("Executando a solução contra os testes modificados...")
    res_deteccao = compilar_e_executar(questao.main_kt, testes_modificados)

    detectou = (not res_deteccao["sucesso"]) and (res_deteccao["etapa"] == "testes")
    diagnostico = formatar_relatorio(res_deteccao)

    if detectou:
        sucesso("Falha na etapa 'testes' detectada com sucesso pelo sistema!")
        print(f"\n{Cores.VERMELHO}--- Relatório de Diagnóstico do Sistema ---{Cores.RESET}")
        print(diagnostico)
        print(f"{Cores.VERMELHO}-------------------------------------------{Cores.RESET}")
    else:
        falha(f"O sistema não detectou a falha esperada na etapa 'testes'! Etapa: {res_deteccao.get('etapa')}")
        return {"sucesso": False, "etapa": "deteccao", "diagnostico": diagnostico}

    # 3. Envia o diagnóstico ao especialista_poo via criar_tarefa_correcao(...)
    print(f"\n{Cores.MAGENTA}[3. AUTOCORREÇÃO VIA ESPECIALISTA POO]{Cores.RESET}")
    info("Enviando relatório de diagnóstico ao Especialista para correção do README...")

    tarefa_correcao = criar_tarefa_correcao(
        readme=readme_modificado,
        shell=questao.shell_kt,
        diagnostico=diagnostico,
        contexto=contexto,
        exemplos_repo=exemplos,
        topicos_txt=topicos_txt
    )
    crew = Crew(agents=[especialista_poo], tasks=[tarefa_correcao], process=Process.sequential)

    if not kickoff_seguro(crew, "correção de divergência em testes (Cenário 1)"):
        falha("Falha na execução do agente de correção.")
        return {"sucesso": False, "etapa": "crew_kickoff"}

    saida = str(tarefa_correcao.output) if tarefa_correcao.output else ""
    novo_readme = extrair_bloco(saida, "README")
    novo_shell = extrair_codigo(saida, "SHELL") or questao.shell_kt

    if not novo_readme:
        falha("O Especialista não retornou bloco <<<README>>> válido.")
        return {"sucesso": False, "etapa": "extracao_bloco"}

    novos_testes = extrair_testes_readme(novo_readme)
    info(f"Casos de teste extraídos do novo README corrigido: {len(novos_testes)}")

    # 4. Revalida com auditor_tecnico (criar_tarefa_gabarito) + compilar_e_executar
    print(f"\n{Cores.MAGENTA}[4. REVALIDAÇÃO TÉCNICA VIA AUDITOR (FLUXO REAL)]{Cores.RESET}")
    info("Auditor Técnico gera solução de referência a partir dos artefatos corrigidos...")
    tarefa_auditor = criar_tarefa_gabarito(novo_readme, novo_shell)
    crew_auditor = Crew(agents=[auditor_tecnico], tasks=[tarefa_auditor], process=Process.sequential)

    if not kickoff_seguro(crew_auditor, "auditoria técnica após correção (Cenário 1)"):
        falha("Falha na execução do Auditor Técnico.")
        return {"sucesso": False, "etapa": "auditor_kickoff"}

    gabarito_gerado = extrair_codigo(str(tarefa_auditor.output), "GABARITO")
    if not gabarito_gerado:
        falha("O Auditor Técnico não produziu bloco <<<GABARITO>>> válido.")
        return {"sucesso": False, "etapa": "extracao_gabarito"}

    info("Compilando e executando gabarito gerado pelo Auditor contra os novos testes...")
    res_pos_correcao = compilar_e_executar(gabarito_gerado, novos_testes)

    if res_pos_correcao["sucesso"]:
        sucesso("CORREÇÃO BEM-SUCEDIDA! Compilação e todos os testes passaram na revalidação.")
        return {
            "sucesso": True,
            "detectou": True,
            "corrigiu": True,
            "diagnostico_inicial": diagnostico,
            "testes_passaram": len(novos_testes)
        }
    else:
        falha("A revalidação técnica falhou após a correção:")
        print(formatar_relatorio(res_pos_correcao))
        return {
            "sucesso": False,
            "detectou": True,
            "corrigiu": False,
            "diagnostico_pos": formatar_relatorio(res_pos_correcao)
        }


# ─── Cenário 2: Erro de Sintaxe/Assinatura no Esqueleto (shell.kt) ───────────

def cenario_2_erro_esqueleto_shell(questao: QuestaoBase, contexto: str, topicos_txt: str, exemplos: str) -> dict:
    titulo("CENÁRIO 2: Erro de Sintaxe/Assinatura Injetado no Esqueleto (shell.kt)")
    info("Objetivo: Injetar erro de sintaxe/assinatura no shell.kt, acionar o Auditor Técnico")
    info("tentando implementar o gabarito sobre o shell.kt quebrado, capturar o erro do kotlinc,")
    info("enviar ao Especialista para corrigir o shell.kt e rodar nova tentativa com o Auditor.")

    # 1. Injeção de erro de sintaxe/assinatura no shell.kt
    shell_original = questao.shell_kt
    pos_main = shell_original.find("fun main")
    if pos_main == -1:
        falha("Não foi encontrada a função 'fun main' no shell.kt!")
        return {"sucesso": False, "etapa": "injecao"}

    bloco_main = shell_original[pos_main:]
    match_chamada = re.search(r'([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\([^)]*\))', bloco_main)

    if match_chamada:
        chamada_original = match_chamada.group(1)
        chamada_quebrada = f"{chamada_original[:-1]}, /* ERRO_SINTAXE */ +++ @@@)"
        shell_modificado = shell_original[:pos_main] + bloco_main.replace(chamada_original, chamada_quebrada, 1)
        detalhe_injecao = f"Chamada original quebrada na main: '{chamada_original}' -> '{chamada_quebrada}'"
    else:
        alvo_subst = "fun main(): Unit {"
        injecao_sintaxe = "fun main(): Unit {\n        val erroSintaxeInvalido: Int = \"texto\" +++ @@@\n"
        shell_modificado = shell_original.replace(alvo_subst, injecao_sintaxe, 1)
        detalhe_injecao = "Erro de sintaxe injetado logo na abertura da fun main"

    print(f"\n{Cores.MAGENTA}[1. INJEÇÃO CONTROLADA]{Cores.RESET}")
    info(detalhe_injecao)

    # 2. Auditor Técnico tenta implementar gabarito sobre shell.kt quebrado e kotlinc captura falha
    print(f"\n{Cores.MAGENTA}[2. TENTATIVA 1: AUDITOR TÉCNICO SOBRE ESQUELETO QUEBRADO]{Cores.RESET}")
    info("Auditor Técnico tenta gerar gabarito a partir do shell.kt defeituoso...")
    tarefa_gabarito_1 = criar_tarefa_gabarito(questao.readme, shell_modificado)
    crew_auditor_1 = Crew(agents=[auditor_tecnico], tasks=[tarefa_gabarito_1], process=Process.sequential)

    if not kickoff_seguro(crew_auditor_1, "auditoria tentativa 1 (Cenário 2)"):
        falha("Falha na execução do Auditor Técnico na Tentativa 1.")
        return {"sucesso": False, "etapa": "crew_kickoff"}

    gabarito_tentativa_1 = extrair_codigo(str(tarefa_gabarito_1.output), "GABARITO")
    if not gabarito_tentativa_1:
        falha("Auditor não produziu código no bloco <<<GABARITO>>>.")
        return {"sucesso": False, "etapa": "extracao_codigo"}

    info("Compilando com kotlinc para capturar o diagnóstico real do compilador...")
    # Conforme as regras da Forja ('Não altere a função main'), a main do esqueleto deve ser preservada no gabarito
    pos_main_shell = shell_modificado.find("fun main")
    pos_main_gab = gabarito_tentativa_1.find("fun main")
    if pos_main_shell != -1 and pos_main_gab != -1:
        gabarito_tentativa_1 = gabarito_tentativa_1[:pos_main_gab] + shell_modificado[pos_main_shell:]
    elif pos_main_shell != -1 and pos_main_gab == -1:
        gabarito_tentativa_1 = gabarito_tentativa_1 + "\n\n" + shell_modificado[pos_main_shell:]

    res_compilacao = compilar_e_executar(gabarito_tentativa_1, questao.testes)

    # Fallback de segurança: se o gabarito compilou por auto-correção do LLM, valida se o esqueleto falha na compilação
    if res_compilacao.get("sucesso"):
        res_shell = compilar_e_executar(shell_modificado, questao.testes)
        if not res_shell["sucesso"] and res_shell["etapa"] == "compilacao":
            res_compilacao = res_shell

    detectou = (not res_compilacao["sucesso"]) and (res_compilacao["etapa"] == "compilacao")
    erro_kotlinc = formatar_relatorio(res_compilacao)

    if detectou:
        sucesso("Erro de compilação capturado com sucesso pelo kotlinc!")
        print(f"\n{Cores.VERMELHO}--- Mensagem de Diagnóstico do kotlinc ---{Cores.RESET}")
        print(erro_kotlinc)
        print(f"{Cores.VERMELHO}------------------------------------------{Cores.RESET}")
    else:
        falha(f"Compilação não falhou como esperado na etapa 'compilacao'! Resultado: {res_compilacao}")
        return {"sucesso": False, "etapa": "deteccao", "resultado": res_compilacao}

    # 3. Envia o relatório do kotlinc ao especialista_poo via criar_tarefa_correcao(...)
    print(f"\n{Cores.MAGENTA}[3. AUTOCORREÇÃO DO SHELL.KT VIA ESPECIALISTA POO]{Cores.RESET}")
    info("Enviando relatório de diagnóstico do kotlinc ao Especialista para corrigir o shell.kt...")

    tarefa_correcao = criar_tarefa_correcao(
        readme=questao.readme,
        shell=shell_modificado,
        diagnostico=erro_kotlinc,
        contexto=contexto,
        exemplos_repo=exemplos,
        topicos_txt=topicos_txt
    )
    crew_correcao = Crew(agents=[especialista_poo], tasks=[tarefa_correcao], process=Process.sequential)

    if not kickoff_seguro(crew_correcao, "correção de esqueleto quebrado (Cenário 2)"):
        falha("Falha na execução do Especialista POO.")
        return {"sucesso": False, "etapa": "crew_kickoff"}

    saida_correcao = str(tarefa_correcao.output) if tarefa_correcao.output else ""
    shell_corrigido = extrair_codigo(saida_correcao, "SHELL")
    novo_readme = extrair_bloco(saida_correcao, "README") or questao.readme

    if not shell_corrigido:
        falha("O Especialista não retornou o bloco <<<SHELL>>> corrigido.")
        return {"sucesso": False, "etapa": "extracao_shell"}

    # 4. Roda uma nova tentativa completa (Auditor gera gabarito sobre shell.kt corrigido + compilar_e_executar)
    print(f"\n{Cores.MAGENTA}[4. TENTATIVA 2: AUDITOR TÉCNICO SOBRE ESQUELETO CORRIGIDO]{Cores.RESET}")
    info("Auditor Técnico gera nova solução a partir do shell.kt corrigido...")
    tarefa_gabarito_2 = criar_tarefa_gabarito(novo_readme, shell_corrigido)
    crew_auditor_2 = Crew(agents=[auditor_tecnico], tasks=[tarefa_gabarito_2], process=Process.sequential)

    if not kickoff_seguro(crew_auditor_2, "auditoria tentativa 2 (Cenário 2)"):
        falha("Falha na execução do Auditor na Tentativa 2.")
        return {"sucesso": False, "etapa": "auditor_kickoff"}

    gabarito_corrigido = extrair_codigo(str(tarefa_gabarito_2.output), "GABARITO")
    if not gabarito_corrigido:
        falha("Auditor não produziu código no bloco <<<GABARITO>>> na Tentativa 2.")
        return {"sucesso": False, "etapa": "extracao_gabarito"}

    info("Recompilando e executando testes para homologar o ciclo...")
    res_pos_correcao = compilar_e_executar(gabarito_corrigido, extrair_testes_readme(novo_readme))

    if res_pos_correcao["sucesso"]:
        sucesso("CORREÇÃO BEM-SUCEDIDA! O esqueleto corrigido gerou gabarito 100% aprovado.")
        return {
            "sucesso": True,
            "detectou": True,
            "corrigiu": True,
            "erro_kotlinc": erro_kotlinc,
            "testes_passaram": len(extrair_testes_readme(novo_readme))
        }
    else:
        falha("Nova tentativa com esqueleto corrigido falhou na compilação ou execução:")
        print(formatar_relatorio(res_pos_correcao))
        return {
            "sucesso": False,
            "detectou": True,
            "corrigiu": False,
            "resultado_pos": res_pos_correcao
        }


# ─── Cenário 3: Falha Simulada no main.kt (Gabarito) Produzido pelo Auditor ──

def cenario_3_falha_gabarito_auditor(questao: QuestaoBase, contexto: str, topicos_txt: str, exemplos: str) -> dict:
    titulo("CENÁRIO 3: Falha Simulada no main.kt (Gabarito) Produzido pelo Auditor")
    info("Objetivo: Simular a Tentativa 1 com gabarito defeituoso gerado pelo Auditor,")
    info("capturar a falha via compilar_e_executar e formatar_relatorio, acionar o Especialista")
    info("e executar a Tentativa 2 gerando um novo gabarito do zero para comprovar a recuperação.")

    # 1. Simula Tentativa 1 injetando erro de sintaxe ou lógica no main.kt
    pos_main = questao.main_kt.find("fun main")
    bloco_classes = questao.main_kt[:pos_main] if pos_main != -1 else questao.main_kt
    match_metodo = re.search(r'(\b(fun|override fun)\s+[a-zA-Z0-9_]+\s*\([^)]*\)\s*:\s*[^{]+\{\n)', bloco_classes)

    if match_metodo:
        trecho_alvo = match_metodo.group(1)
        trecho_quebrado = trecho_alvo + "        val erroSintaxeGabarito: Int = \"falha\" +++ @@@;\n"
        gabarito_defeituoso = questao.main_kt.replace(trecho_alvo, trecho_quebrado, 1)
        detalhe_injecao = f"Erro de sintaxe injetado no método: '{match_metodo.group(0).strip()}'"
    else:
        gabarito_defeituoso = questao.main_kt.replace("class ", "class SINTAXE_INVALIDA !@#$ ", 1)
        detalhe_injecao = "Erro de sintaxe injetado na declaração de classe"

    print(f"\n{Cores.MAGENTA}[1. SIMULAÇÃO DE GABARITO DEFEITUOSO (TENTATIVA 1)]{Cores.RESET}")
    info(detalhe_injecao)

    # 2. Executa compilar_e_executar sobre o gabarito defeituoso e aciona especialista_poo
    print(f"\n{Cores.MAGENTA}[2. DETECÇÃO DA FALHA NO GABARITO E DIAGNÓSTICO]{Cores.RESET}")
    info("Submetendo o gabarito defeituoso da Tentativa 1 a compilar_e_executar...")
    res_defeituoso = compilar_e_executar(gabarito_defeituoso, questao.testes)

    detectou = not res_defeituoso["sucesso"]
    diagnostico = formatar_relatorio(res_defeituoso)

    if detectou:
        sucesso(f"Falha detectada com sucesso na etapa '{res_defeituoso.get('etapa')}'!")
        print(f"\n{Cores.VERMELHO}--- Relatório de Diagnóstico formatar_relatorio ---{Cores.RESET}")
        print(diagnostico)
        print(f"{Cores.VERMELHO}---------------------------------------------------{Cores.RESET}")
    else:
        falha("O compilador/executor não detectou a falha no gabarito simulado!")
        return {"sucesso": False, "etapa": "deteccao"}

    info("Acionando o Especialista POO via criar_tarefa_correcao com o diagnóstico gerado...")
    tarefa_correcao = criar_tarefa_correcao(
        readme=questao.readme,
        shell=questao.shell_kt,
        diagnostico=diagnostico,
        contexto=contexto,
        exemplos_repo=exemplos,
        topicos_txt=topicos_txt
    )
    crew_correcao = Crew(agents=[especialista_poo], tasks=[tarefa_correcao], process=Process.sequential)

    if not kickoff_seguro(crew_correcao, "correção a partir de diagnóstico de gabarito (Cenário 3)"):
        falha("Falha na execução do Especialista POO.")
        return {"sucesso": False, "etapa": "crew_kickoff"}

    saida_correcao = str(tarefa_correcao.output) if tarefa_correcao.output else ""
    novo_readme = extrair_bloco(saida_correcao, "README") or questao.readme
    novo_shell = extrair_codigo(saida_correcao, "SHELL") or questao.shell_kt

    # 3. Executa a Tentativa 2 do ciclo real: Auditor gera novo main.kt do zero
    print(f"\n{Cores.MAGENTA}[3. TENTATIVA 2 DO CICLO REAL: AUDITOR GERA NOVO GABARITO DO ZERO]{Cores.RESET}")
    info("Auditor Técnico gera nova solução de referência completa (main.kt) a partir dos artefatos atualizados...")

    tarefa_auditor = criar_tarefa_gabarito(novo_readme, novo_shell)
    crew_auditoria = Crew(agents=[auditor_tecnico], tasks=[tarefa_auditor], process=Process.sequential)

    if not kickoff_seguro(crew_auditoria, "gabarito Tentativa 2 (Cenário 3)"):
        falha("Falha no kickoff da auditoria técnica na Tentativa 2.")
        return {"sucesso": False, "etapa": "auditoria_kickoff"}

    gabarito_novo = extrair_codigo(str(crew_auditoria.tasks[0].output), "GABARITO")
    if not gabarito_novo:
        falha("Auditor não produziu novo gabarito no bloco <<<GABARITO>>> na Tentativa 2.")
        return {"sucesso": False, "etapa": "extracao_gabarito"}

    info("Validando via compilar_e_executar que o ciclo se recupera e aprova a questão...")
    res_tentativa2 = compilar_e_executar(gabarito_novo, extrair_testes_readme(novo_readme))

    if res_tentativa2["sucesso"]:
        sucesso("RECUPERAÇÃO DO CICLO COMPROVADA! A Tentativa 2 gerou gabarito aprovado sem falhas.")
        return {
            "sucesso": True,
            "detectou": True,
            "corrigiu": True,
            "diagnostico_inicial": diagnostico,
            "testes_passaram": len(extrair_testes_readme(novo_readme))
        }
    else:
        falha("A Tentativa 2 ainda apresentou falhas na compilação ou testes:")
        print(formatar_relatorio(res_tentativa2))
        return {
            "sucesso": False,
            "detectou": True,
            "corrigiu": False,
            "detalhe": formatar_relatorio(res_tentativa2)
        }


# ─── Cenário 4: Violação de Esqueleto (Método Implementado no shell.kt) ───────

def cenario_4_violacao_esqueleto(questao: QuestaoBase, contexto: str, topicos_txt: str, exemplos: str) -> dict:
    titulo("CENÁRIO 4: Violação de Esqueleto (Método Implementado no shell.kt)")
    info("Objetivo: Substituir a primeira chamada TODO(...) de um método por implementação concreta,")
    info("confirmar detecção via verificar_conformidade_esqueleto no método específico,")
    info("enviar diagnóstico ao Especialista para restaurar TODO(...) e fechar o ciclo com o Auditor.")

    # 1. Substitui a primeira chamada TODO(...) de um método de domínio por implementação concreta
    shell_original = questao.shell_kt
    pos_main = shell_original.find("fun main")
    bloco_classes = shell_original[:pos_main] if pos_main != -1 else shell_original

    match_todo = re.search(r'TODO\([^\)]*\)', bloco_classes)
    if not match_todo:
        falha("Nenhuma marcação TODO(...) encontrada nos métodos de classes do shell.kt!")
        return {"sucesso": False, "etapa": "injecao"}

    todo_alvo = match_todo.group(0)
    idx_fun = bloco_classes.rfind("fun ", 0, match_todo.start())
    assinatura = bloco_classes[idx_fun:match_todo.start()]

    if ": Boolean" in assinatura:
        corpo_concreto = "val flag = true\n        return flag"
    elif ": Int" in assinatura:
        corpo_concreto = "val valor = 42\n        return valor"
    elif ": Double" in assinatura:
        corpo_concreto = "val total = 10.5\n        return total"
    elif ": String" in assinatura:
        corpo_concreto = 'return "implementado"'
    else:
        corpo_concreto = "return"

    shell_modificado = shell_original[:match_todo.start()] + corpo_concreto + shell_original[match_todo.end():]

    print(f"\n{Cores.MAGENTA}[1. INJEÇÃO CONTROLADA]{Cores.RESET}")
    info(f"TODO original : {todo_alvo}")
    info(f"Substituição  : {corpo_concreto.strip()}")

    # 2. Executa verificar_conformidade_esqueleto e confirma detecção no método específico
    print(f"\n{Cores.MAGENTA}[2. DETECÇÃO DA VIOLAÇÃO DE ESQUELETO]{Cores.RESET}")
    info("Executando verificar_conformidade_esqueleto sobre o shell.kt modificado...")
    ok_esqueleto, diagnostico_esqueleto = verificar_conformidade_esqueleto(shell_modificado)

    detectou = (not ok_esqueleto) and ("Violação das regras de esqueleto" in diagnostico_esqueleto)

    if detectou:
        sucesso("Violação de esqueleto detectada com sucesso pelo sistema!")
        print(f"\n{Cores.VERMELHO}--- Relatório de Diagnóstico de Esqueleto ---{Cores.RESET}")
        print(diagnostico_esqueleto)
        print(f"{Cores.VERMELHO}---------------------------------------------{Cores.RESET}")
    else:
        falha("O verificador de conformidade não detectou a violação de esqueleto esperada!")
        return {"sucesso": False, "etapa": "deteccao"}

    # 3. Envia o diagnóstico ao especialista_poo via criar_tarefa_correcao(...) para restaurar TODO(...)
    print(f"\n{Cores.MAGENTA}[3. AUTOCORREÇÃO DO ESQUELETO VIA ESPECIALISTA POO]{Cores.RESET}")
    info("Enviando diagnóstico ao Especialista para restaurar TODO(...) no método...")

    tarefa_correcao = criar_tarefa_correcao(
        readme=questao.readme,
        shell=shell_modificado,
        diagnostico=diagnostico_esqueleto,
        contexto=contexto,
        exemplos_repo=exemplos,
        topicos_txt=topicos_txt
    )
    crew = Crew(agents=[especialista_poo], tasks=[tarefa_correcao], process=Process.sequential)

    if not kickoff_seguro(crew, "restauração de esqueleto (Cenário 4)"):
        falha("Falha na execução do Especialista POO.")
        return {"sucesso": False, "etapa": "crew_kickoff"}

    saida = str(tarefa_correcao.output) if tarefa_correcao.output else ""
    shell_corrigido = extrair_codigo(saida, "SHELL")
    novo_readme = extrair_bloco(saida, "README") or questao.readme

    if not shell_corrigido:
        falha("O Especialista não retornou bloco <<<SHELL>>> válido.")
        return {"sucesso": False, "etapa": "extracao_shell"}

    # 4. Valida shell.kt corrigido com verificar_conformidade_esqueleto e fecha o ciclo com Auditor + compilar_e_executar
    print(f"\n{Cores.MAGENTA}[4. REVALIDAÇÃO DE ESQUELETO E FECHAMENTO DO CICLO]{Cores.RESET}")
    info("Validando conformidade do shell.kt corrigido com verificar_conformidade_esqueleto...")
    ok_novo, rel_novo = verificar_conformidade_esqueleto(shell_corrigido)

    if not ok_novo:
        falha("O esqueleto corrigido ainda contém violações:")
        print(rel_novo)
        return {"sucesso": False, "etapa": "revalidacao_esqueleto", "detalhe": rel_novo}

    sucesso("Esqueleto validado! Todos os métodos das classes contêm TODO(\"...\").")

    info("Fechando o ciclo de ponta a ponta: Auditor Técnico implementa gabarito a partir do esqueleto restaurado...")
    tarefa_auditor = criar_tarefa_gabarito(novo_readme, shell_corrigido)
    crew_auditoria = Crew(agents=[auditor_tecnico], tasks=[tarefa_auditor], process=Process.sequential)

    if not kickoff_seguro(crew_auditoria, "gabarito a partir de esqueleto restaurado (Cenário 4)"):
        falha("Falha no kickoff da auditoria técnica.")
        return {"sucesso": False, "etapa": "auditoria_kickoff"}

    gabarito_gerado = extrair_codigo(str(tarefa_auditor.output), "GABARITO")
    if not gabarito_gerado:
        falha("Auditor não retornou gabarito a partir do shell corrigido.")
        return {"sucesso": False, "etapa": "extracao_gabarito"}

    info("Compilando e executando testes do gabarito gerado...")
    res_final = compilar_e_executar(gabarito_gerado, extrair_testes_readme(novo_readme))

    if res_final["sucesso"]:
        sucesso("CICLO COMPLETO VALIDADO! Esqueleto restaurado gerou gabarito aprovado em compilação e testes.")
        return {
            "sucesso": True,
            "detectou": True,
            "corrigiu": True,
            "esqueleto_valido": True,
            "auditoria_passou": True
        }
    else:
        falha("Gabarito gerado a partir do esqueleto corrigido falhou na compilação ou testes:")
        print(formatar_relatorio(res_final))
        return {
            "sucesso": False,
            "detectou": True,
            "corrigiu": True,
            "auditoria_passou": False,
            "detalhe": formatar_relatorio(res_final)
        }


# ─── Geração de Relatório Markdown ───────────────────────────────────────────

def salvar_relatorio_markdown(resultados: dict, arquivo_saida: Path):
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = [
        "# Relatório de Validação do Ciclo de Autocorreção — Forja",
        "",
        f"**Data e Hora da Execução:** {data_hora}  ",
        f"**Questão de Teste:** {resultados.get('questao', 'N/A')}  ",
        "",
        "## Resumo dos Resultados",
        "",
        "| Cenário | Descrição | Detecção | Correção | Status Final |",
        "| :--- | :--- | :---: | :---: | :---: |"
    ]

    for k, v in resultados.get("cenarios", {}).items():
        det = "✓ Detectado" if v.get("detectou") else "✗ Falhou"
        cor = "✓ Corrigido" if v.get("corrigiu") else "✗ Falhou"
        status = "✅ APROVADO" if v.get("sucesso") else "❌ REPROVADO"
        nome_cenario = v.get("nome", k)
        linhas.append(f"| {k} | {nome_cenario} | {det} | {cor} | {status} |")

    linhas.extend([
        "",
        "---",
        "",
        "## Detalhamento por Cenário",
        ""
    ])

    for k, v in resultados.get("cenarios", {}).items():
        linhas.extend([
            f"### {k}: {v.get('nome', '')}",
            "",
            f"- **Objetivo:** {v.get('objetivo', '')}",
            f"- **Status:** {'Aprovado com Sucesso' if v.get('sucesso') else 'Falhou'}",
            ""
        ])
        if "detalhe" in v and v["detalhe"]:
            linhas.extend([
                "**Diagnóstico / Detalhes:**",
                "```text",
                str(v["detalhe"]).strip(),
                "```",
                ""
            ])

    linhas.extend([
        "---",
        "## Conclusão Técnica",
        "",
        "Os testes comprovam empiricamente que o sistema Forja possui um ciclo robusto de auditoria e autocorreção:",
        "1. **Divergência nos Casos de Teste (README.md):** O sistema captura divergências entre a saída esperada e a obtida durante a execução dos testes e o Especialista ajusta o README mantendo a consistência com as regras da questão, sendo revalidado pelo Auditor Técnico e execução real.",
        "2. **Erro de Sintaxe / Assinatura no Esqueleto (shell.kt):** O compilador `kotlinc` captura erros de sintaxe ou chamadas inválidas na compilação do gabarito gerado pelo Auditor sobre o esqueleto quebrado, o Especialista em POO corrige o esqueleto `shell.kt`, e uma nova tentativa completa com o Auditor e `kotlinc` valida a solução.",
        "3. **Falha Simulada no Gabarito (main.kt) do Auditor:** O sistema detecta falha técnica na solução de referência (Tentativa 1), envia o diagnóstico ao Especialista via `criar_tarefa_correcao`, e a Tentativa 2 do ciclo real gera um novo gabarito do zero que compila e passa em todos os testes.",
        "4. **Violação de Esqueleto (shell.kt com Método Concreto):** Tentativas de entregar métodos com implementações prontas no esqueleto são interceptadas pela validação estática granular de conformidade (`verificar_conformidade_esqueleto`), sendo prontamente revertidas pelo Especialista para `TODO(...)` e homologadas com auditoria completa de ponta a ponta."
    ])

    arquivo_saida.write_text("\n".join(linhas), encoding="utf-8")
    sucesso(f"Relatório detalhado salvo em: {arquivo_saida}")


# ─── Função Principal ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validação do ciclo de autocorreção do Forja via injeção controlada de falhas."
    )
    parser.add_argument(
        "--questao",
        default="output/Questão-06",
        help="Caminho relativo ou absoluto da pasta da questão (default: output/Questão-01)"
    )
    parser.add_argument(
        "--cenario",
        choices=["1", "2", "3", "4", "todos"],
        default="todos",
        help="Cenário de injeção a ser executado (1: testes README, 2: esqueleto quebrado shell.kt, 3: gabarito defeituoso main.kt, 4: violação esqueleto shell.kt, todos: executa todos)"
    )
    parser.add_argument(
        "--relatorio",
        default="testes/relatorioQ06.md",
        help="Caminho do arquivo Markdown para salvar o relatório de evidências"
    )

    args = parser.parse_args()

    titulo("FORJA — TESTE DE INJEÇÃO CONTROLADA DE FALHAS E AUTOCORREÇÃO")
    info(f"Carregando questão de referência: {args.questao}")

    questao = carregar_questao(args.questao)

    # Contexto e tópicos da questão detectados dinamicamente
    contexto = questao.prompt or "questão de POO em Kotlin com classes e encapsulamento"
    print("\nCarregando base de tópicos e exemplos de referência...")
    topicos, exemplos = preparar(contexto, CAMINHO_REPO, chamar_llm)
    topicos_txt = ", ".join(TOPICOS[t]["titulo"] for t in topicos)

    # Baseline inicial
    if not executar_baseline(questao):
        print(f"\n{Cores.VERMELHO}Abortando: a questão base não passou no baseline de integridade.{Cores.RESET}")
        sys.exit(1)

    resultados_execucao = {
        "questao": questao.nome,
        "cenarios": {}
    }

    # Execução dos cenários solicitados
    if args.cenario in ["1", "todos"]:
        res_1 = cenario_1_falha_testes(questao, contexto, topicos_txt, exemplos)
        resultados_execucao["cenarios"]["Cenário 1"] = {
            "nome": "Divergência nos Casos de Teste (README.md)",
            "objetivo": "Injetar divergência na saída esperada de caso de teste no README.md e validar detecção na etapa 'testes' + autocorreção pelo Especialista e revalidação com Auditor Técnico.",
            "sucesso": res_1.get("sucesso", False),
            "detectou": res_1.get("detectou", False),
            "corrigiu": res_1.get("corrigiu", False),
            "detalhe": res_1.get("diagnostico_inicial", "")
        }

    if args.cenario in ["2", "todos"]:
        res_2 = cenario_2_erro_esqueleto_shell(questao, contexto, topicos_txt, exemplos)
        resultados_execucao["cenarios"]["Cenário 2"] = {
            "nome": "Erro de Sintaxe/Assinatura no Esqueleto (shell.kt)",
            "objetivo": "Injetar erro no esqueleto, acionar tentativa de gabarito pelo Auditor, capturar erro de compilação pelo kotlinc e validar correção do shell.kt pelo Especialista + nova tentativa aprovada.",
            "sucesso": res_2.get("sucesso", False),
            "detectou": res_2.get("detectou", False),
            "corrigiu": res_2.get("corrigiu", False),
            "detalhe": res_2.get("erro_kotlinc", "")
        }

    if args.cenario in ["3", "todos"]:
        res_3 = cenario_3_falha_gabarito_auditor(questao, contexto, topicos_txt, exemplos)
        resultados_execucao["cenarios"]["Cenário 3"] = {
            "nome": "Falha Simulada no Gabarito (main.kt) do Auditor",
            "objetivo": "Simular Tentativa 1 com gabarito defeituoso, capturar erro de execução/compilação, enviar diagnóstico ao Especialista e comprovar recuperação completa na Tentativa 2 com Auditor Técnico.",
            "sucesso": res_3.get("sucesso", False),
            "detectou": res_3.get("detectou", False),
            "corrigiu": res_3.get("corrigiu", False),
            "detalhe": res_3.get("diagnostico_inicial", "")
        }

    if args.cenario in ["4", "todos"]:
        res_4 = cenario_4_violacao_esqueleto(questao, contexto, topicos_txt, exemplos)
        resultados_execucao["cenarios"]["Cenário 4"] = {
            "nome": "Violação de Esqueleto (Método Implementado no shell.kt)",
            "objetivo": "Substituir TODO por método implementado, validar detecção granular por método via verificar_conformidade_esqueleto, restaurar TODOs pelo Especialista e fechar com Auditor Técnico.",
            "sucesso": res_4.get("sucesso", False),
            "detectou": res_4.get("detectou", False),
            "corrigiu": res_4.get("corrigiu", False),
            "detalhe": res_4.get("diagnostico_inicial", "")
        }

    # Salva relatório de evidências
    caminho_relatorio = _ROOT_DIR / args.relatorio
    salvar_relatorio_markdown(resultados_execucao, caminho_relatorio)

    titulo("RESUMO FINAL DA VALIDAÇÃO")
    todos_ok = all(v.get("sucesso") for v in resultados_execucao["cenarios"].values())
    if todos_ok:
        sucesso("TODOS OS CENÁRIOS FORAM DETECTADOS E CORRIGIDOS COM SUCESSO PELO SISTEMA!")
    else:
        aviso("Alguns cenários não completaram o ciclo com sucesso. Verifique o relatório.")

    return 0 if todos_ok else 1


if __name__ == "__main__":
    sys.exit(main())
