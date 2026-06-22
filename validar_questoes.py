import argparse
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


CHAVES_CASOS = ("tests", "cases", "casos")

CHAVES_ENTRADA = ("input", "entrada", "stdin")
CHAVES_SAIDA = ("output", "saida", "expected", "stdout")


@dataclass
class CasoTeste:
    nome: str
    entrada: str
    saida_esperada: str | None
    possui_entrada: bool
    possui_saida: bool


@dataclass
class ExecucaoCaso:
    caso: str
    ok: bool
    timeout: bool = False
    returncode: int | None = None
    stderr: str = ""


@dataclass
class ResultadoQuestao:
    questao: str
    caminho: str

    possui_shell_java: bool = False
    possui_tests_toml: bool = False

    toml_parseado: bool = False
    toml_estrutura_valida: bool = False
    total_casos: int = 0
    erros_toml: list[str] = field(default_factory=list)
    avisos_toml: list[str] = field(default_factory=list)

    compilou: bool = False
    erro_compilacao: str = ""

    comandos_detectados: list[str] = field(default_factory=list)
    comandos_nao_encontrados_no_shell: list[str] = field(default_factory=list)
    cobertura_comandos_ok: bool = True

    execucoes: list[ExecucaoCaso] = field(default_factory=list)
    execucoes_sem_crash: bool = False

    status_geral: str = "NAO_VALIDADO"


def remover_cercas_markdown(texto: str) -> str:
    """
    Remove apenas linhas de cerca Markdown, como:
    ```java
    ```
    
    Não altera o arquivo original. A limpeza é feita em uma cópia temporária.
    """
    linhas = texto.splitlines(keepends=True)

    linhas_limpas = [
        linha for linha in linhas
        if not linha.strip().startswith("```")
    ]

    return "".join(linhas_limpas)


def valor_para_texto(valor: Any) -> str:
    """
    Converte valores do TOML para string.
    Isso evita erro caso a entrada venha como número, lista etc.
    """
    if valor is None:
        return ""

    if isinstance(valor, str):
        return valor

    if isinstance(valor, list):
        return "\n".join(str(item) for item in valor)

    return str(valor)


def obter_primeira_chave_existente(dicionario: dict[str, Any], chaves: tuple[str, ...]) -> tuple[str | None, Any]:
    """
    Procura a primeira chave existente em um dicionário.
    Retorna o nome da chave e o valor encontrado.
    """
    for chave in chaves:
        if chave in dicionario:
            return chave, dicionario[chave]

    return None, None


def normalizar_lista_de_casos(casos_brutos: Any) -> list[dict[str, Any]]:
    """
    Aceita tanto:
    
    [[tests]]
    input = "..."
    output = "..."
    
    quanto:
    
    [tests.caso1]
    input = "..."
    output = "..."
    """
    if isinstance(casos_brutos, list):
        return casos_brutos

    if isinstance(casos_brutos, dict):
        return list(casos_brutos.values())

    return []


def ler_casos_toml(caminho_toml: Path) -> tuple[list[CasoTeste], list[str], list[str]]:
    """
    Lê o tests.toml e retorna:
    - lista de casos
    - lista de erros
    - lista de avisos
    """
    erros: list[str] = []
    avisos: list[str] = []
    casos: list[CasoTeste] = []

    try:
        with open(caminho_toml, "rb") as arquivo:
            dados_toml = tomllib.load(arquivo)
    except tomllib.TOMLDecodeError as erro:
        erros.append(f"Erro de sintaxe TOML: {erro}")
        return casos, erros, avisos
    except Exception as erro:
        erros.append(f"Erro ao abrir/ler TOML: {erro}")
        return casos, erros, avisos

    chave_casos, casos_brutos = obter_primeira_chave_existente(dados_toml, CHAVES_CASOS)

    if chave_casos is None:
        erros.append(
            "Nenhuma chave de casos encontrada. Esperado uma das chaves: "
            + ", ".join(CHAVES_CASOS)
        )
        return casos, erros, avisos

    lista_casos = normalizar_lista_de_casos(casos_brutos)

    if not lista_casos:
        erros.append(f"A chave '{chave_casos}' existe, mas não contém casos válidos.")
        return casos, erros, avisos

    for indice, caso_bruto in enumerate(lista_casos, start=1):
        nome_caso = f"caso_{indice}"

        if not isinstance(caso_bruto, dict):
            erros.append(f"{nome_caso}: deveria ser uma tabela/dicionário no TOML.")
            continue

        chave_entrada, entrada = obter_primeira_chave_existente(caso_bruto, CHAVES_ENTRADA)
        chave_saida, saida = obter_primeira_chave_existente(caso_bruto, CHAVES_SAIDA)

        possui_entrada = chave_entrada is not None
        possui_saida = chave_saida is not None

        if not possui_entrada:
            avisos.append(
                f"{nome_caso}: não possui campo de entrada. "
                f"Campos aceitos: {', '.join(CHAVES_ENTRADA)}. Será usada entrada vazia."
            )

        if not possui_saida:
            avisos.append(
                f"{nome_caso}: não possui campo de saída esperada. "
                f"Campos aceitos: {', '.join(CHAVES_SAIDA)}."
            )

        caso = CasoTeste(
            nome=nome_caso,
            entrada=valor_para_texto(entrada),
            saida_esperada=valor_para_texto(saida) if possui_saida else None,
            possui_entrada=possui_entrada,
            possui_saida=possui_saida,
        )

        casos.append(caso)

    return casos, erros, avisos


def preparar_entrada(entrada: str) -> str:
    """
    Garante que entradas não vazias terminem com quebra de linha.
    Isso reduz problemas com Scanner esperando finalização de linha.
    """
    if entrada == "":
        return entrada

    if entrada.endswith("\n"):
        return entrada

    return entrada + "\n"


def parece_comando(token: str) -> bool:
    """
    Heurística simples para detectar comandos nos testes.
    
    Exemplos aceitos:
    init
    addAluno
    $add
    show
    end
    
    Exemplos ignorados:
    1
    10.5
    -3
    """
    token = token.strip()

    if not token:
        return False

    token_sem_cifrao = token[1:] if token.startswith("$") else token

    if re.fullmatch(r"-?\d+(\.\d+)?", token_sem_cifrao):
        return False

    return bool(re.search(r"[A-Za-z_]", token_sem_cifrao))


def extrair_comandos_das_entradas(casos: list[CasoTeste]) -> list[str]:
    """
    Extrai o primeiro token de cada linha de entrada como possível comando.
    """
    comandos: set[str] = set()

    for caso in casos:
        for linha in caso.entrada.splitlines():
            linha = linha.strip()

            if not linha:
                continue

            primeiro_token = linha.split()[0]

            if parece_comando(primeiro_token):
                comando = primeiro_token.removeprefix("$")
                comandos.add(comando)

    return sorted(comandos)


def comando_aparece_no_shell(comando: str, codigo_shell: str) -> bool:
    """
    Verifica se um comando aparece no Shell.java.
    
    A busca cobre padrões comuns:
    - case "comando":
    - case "$comando":
    - .equals("comando")
    - .equals("$comando")
    - aparição direta da string "comando"
    
    Esta etapa é uma heurística. Ela ajuda a indicar compatibilidade entre
    os testes e o esqueleto, mas não prova correção lógica.
    """
    candidatos = [comando, f"${comando}"]

    for candidato in candidatos:
        candidato_regex = re.escape(candidato)

        padroes = [
            rf'case\s+"{candidato_regex}"\s*:',
            rf"case\s+'{candidato_regex}'\s*:",
            rf'\.equals\s*\(\s*"{candidato_regex}"\s*\)',
            rf'\.equalsIgnoreCase\s*\(\s*"{candidato_regex}"\s*\)',
            rf'"{candidato_regex}"',
        ]

        for padrao in padroes:
            if re.search(padrao, codigo_shell):
                return True

    return False


def verificar_cobertura_de_comandos(casos: list[CasoTeste], codigo_shell: str) -> tuple[list[str], list[str]]:
    """
    Retorna:
    - comandos detectados nas entradas
    - comandos não encontrados no Shell.java
    """
    comandos = extrair_comandos_das_entradas(casos)

    nao_encontrados = [
        comando for comando in comandos
        if not comando_aparece_no_shell(comando, codigo_shell)
    ]

    return comandos, nao_encontrados


def copiar_fontes_java_para_temporario(diretorio_questao: Path, diretorio_temporario: Path, codigo_shell_limpo: str) -> Path:
    """
    Copia os arquivos .java da questão para uma pasta temporária.
    O Shell.java é copiado já sem cercas Markdown.
    """
    diretorio_fontes = diretorio_temporario / "src"
    diretorio_fontes.mkdir(parents=True, exist_ok=True)

    for arquivo_java in diretorio_questao.glob("*.java"):
        destino = diretorio_fontes / arquivo_java.name

        if arquivo_java.name == "Shell.java":
            destino.write_text(codigo_shell_limpo, encoding="utf-8")
        else:
            destino.write_text(arquivo_java.read_text(encoding="utf-8"), encoding="utf-8")

    return diretorio_fontes


def detectar_pacote_java(codigo_shell: str) -> str | None:
    """
    Detecta package no Shell.java, caso exista.
    """
    match = re.search(r"^\s*package\s+([\w.]+)\s*;", codigo_shell, flags=re.MULTILINE)

    if match:
        return match.group(1)

    return None


def compilar_shell(diretorio_questao: Path, codigo_shell_limpo: str) -> tuple[bool, str, tempfile.TemporaryDirectory | None, Path | None, str]:
    """
    Compila Shell.java em uma pasta temporária.
    
    Retorna:
    - compilou
    - stderr
    - objeto TemporaryDirectory
    - diretório das classes
    - nome da classe principal
    """
    javac = shutil.which("javac")

    if javac is None:
        return False, "Comando 'javac' não encontrado no sistema.", None, None, "Shell"

    temporario = tempfile.TemporaryDirectory(prefix=f"validacao_{diretorio_questao.name}_")
    caminho_temporario = Path(temporario.name)

    diretorio_fontes = copiar_fontes_java_para_temporario(
        diretorio_questao=diretorio_questao,
        diretorio_temporario=caminho_temporario,
        codigo_shell_limpo=codigo_shell_limpo,
    )

    diretorio_classes = caminho_temporario / "classes"
    diretorio_classes.mkdir(parents=True, exist_ok=True)

    arquivos_java = sorted(str(caminho) for caminho in diretorio_fontes.glob("*.java"))

    if not arquivos_java:
        temporario.cleanup()
        return False, "Nenhum arquivo .java encontrado para compilação.", None, None, "Shell"

    compilacao = subprocess.run(
        [javac, "-encoding", "UTF-8", "-d", str(diretorio_classes), *arquivos_java],
        capture_output=True,
        text=True,
    )

    pacote = detectar_pacote_java(codigo_shell_limpo)
    classe_principal = "Shell" if pacote is None else f"{pacote}.Shell"

    if compilacao.returncode != 0:
        erro = compilacao.stderr.strip()
        temporario.cleanup()
        return False, erro, None, None, classe_principal

    return True, "", temporario, diretorio_classes, classe_principal


def executar_casos(
    casos: list[CasoTeste],
    diretorio_classes: Path,
    classe_principal: str,
    timeout_segundos: float,
) -> list[ExecucaoCaso]:
    """
    Executa java Shell para cada entrada do tests.toml.
    Não compara a saída, apenas verifica crash, exceção e timeout.
    """
    java = shutil.which("java")

    resultados: list[ExecucaoCaso] = []

    if java is None:
        for caso in casos:
            resultados.append(
                ExecucaoCaso(
                    caso=caso.nome,
                    ok=False,
                    stderr="Comando 'java' não encontrado no sistema.",
                )
            )
        return resultados

    for caso in casos:
        entrada = preparar_entrada(caso.entrada)

        try:
            execucao = subprocess.run(
                [java, "-cp", str(diretorio_classes), classe_principal],
                input=entrada,
                capture_output=True,
                text=True,
                timeout=timeout_segundos,
            )

            ok = execucao.returncode == 0

            resultados.append(
                ExecucaoCaso(
                    caso=caso.nome,
                    ok=ok,
                    timeout=False,
                    returncode=execucao.returncode,
                    stderr=execucao.stderr.strip(),
                )
            )

        except subprocess.TimeoutExpired:
            resultados.append(
                ExecucaoCaso(
                    caso=caso.nome,
                    ok=False,
                    timeout=True,
                    stderr="Timeout: possível loop infinito ou leitura aguardando entrada.",
                )
            )

    return resultados


def validar_uma_questao(
    caminho_toml: Path,
    timeout_segundos: float,
    strict_commands: bool,
) -> ResultadoQuestao:
    diretorio_questao = caminho_toml.parent
    caminho_shell = diretorio_questao / "Shell.java"

    resultado = ResultadoQuestao(
        questao=diretorio_questao.name,
        caminho=str(diretorio_questao),
        possui_tests_toml=True,
        possui_shell_java=caminho_shell.exists(),
    )

    if not caminho_shell.exists():
        resultado.status_geral = "FALHOU"
        resultado.erro_compilacao = "Shell.java não encontrado."
        return resultado

    casos, erros_toml, avisos_toml = ler_casos_toml(caminho_toml)

    resultado.erros_toml = erros_toml
    resultado.avisos_toml = avisos_toml
    resultado.toml_parseado = len(erros_toml) == 0
    resultado.total_casos = len(casos)

    casos_com_entrada_e_saida = all(caso.possui_entrada and caso.possui_saida for caso in casos)

    resultado.toml_estrutura_valida = (
        resultado.toml_parseado
        and len(casos) > 0
        and casos_com_entrada_e_saida
    )

    codigo_original = caminho_shell.read_text(encoding="utf-8")
    codigo_shell_limpo = remover_cercas_markdown(codigo_original)

    comandos, comandos_nao_encontrados = verificar_cobertura_de_comandos(casos, codigo_shell_limpo)

    resultado.comandos_detectados = comandos
    resultado.comandos_nao_encontrados_no_shell = comandos_nao_encontrados

    if strict_commands:
        resultado.cobertura_comandos_ok = len(comandos_nao_encontrados) == 0
    else:
        resultado.cobertura_comandos_ok = True

    compilou, erro_compilacao, temporario, diretorio_classes, classe_principal = compilar_shell(
        diretorio_questao=diretorio_questao,
        codigo_shell_limpo=codigo_shell_limpo,
    )

    resultado.compilou = compilou
    resultado.erro_compilacao = erro_compilacao

    if not compilou:
        resultado.status_geral = "FALHOU"
        return resultado

    if diretorio_classes is None:
        resultado.status_geral = "FALHOU"
        resultado.erro_compilacao = "Diretório de classes não foi gerado."
        return resultado

    try:
        resultado.execucoes = executar_casos(
            casos=casos,
            diretorio_classes=diretorio_classes,
            classe_principal=classe_principal,
            timeout_segundos=timeout_segundos,
        )

        resultado.execucoes_sem_crash = (
            len(resultado.execucoes) > 0
            and all(execucao.ok for execucao in resultado.execucoes)
        )

    finally:
        if temporario is not None:
            temporario.cleanup()

    passou = (
        resultado.toml_estrutura_valida
        and resultado.compilou
        and resultado.execucoes_sem_crash
        and resultado.cobertura_comandos_ok
    )

    resultado.status_geral = "PASSOU" if passou else "FALHOU"

    return resultado


def imprimir_resultado_questao(resultado: ResultadoQuestao) -> None:
    print(f"\n--- Analisando Questão: {resultado.questao} ---")

    if not resultado.possui_shell_java:
        print("Shell.java não encontrado.")
        return

    if resultado.toml_parseado:
        print("tests.toml lido com sucesso.")
    else:
        print("Falha ao ler tests.toml.")

    if resultado.toml_estrutura_valida:
        print(f"Estrutura do TOML válida. {resultado.total_casos} caso(s) mapeado(s).")
    else:
        print(f"TOML lido, mas com problemas estruturais. {resultado.total_casos} caso(s) mapeado(s).")

    for aviso in resultado.avisos_toml:
        print(f"{aviso}")

    for erro in resultado.erros_toml:
        print(f"{erro}")

    if resultado.comandos_detectados:
        print(f"Comandos detectados nas entradas: {', '.join(resultado.comandos_detectados)}")

        if resultado.comandos_nao_encontrados_no_shell:
            print(
                "Comandos não encontrados explicitamente no Shell.java: "
                + ", ".join(resultado.comandos_nao_encontrados_no_shell)
            )
        else:
            print("Todos os comandos detectados aparecem no Shell.java.")
    else:
        print("Nenhum comando textual detectado nas entradas dos testes.")

    if resultado.compilou:
        print("Shell.java compilou com sucesso.")
    else:
        print(f"Erro de compilação:\n{resultado.erro_compilacao}")
        return

    if resultado.execucoes:
        falhas = [execucao for execucao in resultado.execucoes if not execucao.ok]

        if not falhas:
            print("Esqueleto processou todas as entradas sem crash.")
        else:
            for falha in falhas:
                if falha.timeout:
                    print(f"Timeout em {falha.caso}: {falha.stderr}")
                else:
                    print(f"Crash em {falha.caso}:")
                    print(falha.stderr if falha.stderr else f"Return code: {falha.returncode}")
    else:
        print("Nenhuma execução foi realizada.")

    if resultado.status_geral == "PASSOU":
        print("Status geral: PASSOU")
    else:
        print("Status geral: FALHOU")


def gerar_resumo(resultados: list[ResultadoQuestao]) -> dict[str, Any]:
    total = len(resultados)

    toml_parseados = sum(1 for r in resultados if r.toml_parseado)
    toml_validos = sum(1 for r in resultados if r.toml_estrutura_valida)
    compilados = sum(1 for r in resultados if r.compilou)
    execucoes_sem_crash = sum(1 for r in resultados if r.execucoes_sem_crash)
    cobertura_comandos_ok = sum(1 for r in resultados if r.cobertura_comandos_ok)
    passaram = sum(1 for r in resultados if r.status_geral == "PASSOU")

    total_casos = sum(r.total_casos for r in resultados)
    total_execucoes = sum(len(r.execucoes) for r in resultados)
    execucoes_ok = sum(
        1
        for r in resultados
        for execucao in r.execucoes
        if execucao.ok
    )

    return {
        "questoes_analisadas": total,
        "toml_parseados": toml_parseados,
        "toml_estrutura_valida": toml_validos,
        "shells_compilados": compilados,
        "questoes_com_execucoes_sem_crash": execucoes_sem_crash,
        "questoes_com_cobertura_de_comandos_ok": cobertura_comandos_ok,
        "questoes_aprovadas_no_status_geral": passaram,
        "total_casos_toml": total_casos,
        "total_execucoes": total_execucoes,
        "execucoes_ok": execucoes_ok,
    }


def imprimir_resumo(resumo: dict[str, Any]) -> None:
    total = resumo["questoes_analisadas"]

    print("\n" + "=" * 65)
    print("RESUMO DA VALIDAÇÃO AUTOMATIZADA - RQ2 E RQ3")
    print("=" * 65)

    print(f"Questões analisadas: {total}")
    print(f"RQ2: tests.toml lidos sem erro de parsing: {resumo['toml_parseados']}/{total}")
    print(f"RQ2: tests.toml com estrutura válida:       {resumo['toml_estrutura_valida']}/{total}")
    print(f"RQ3: Shell.java compilados com sucesso:    {resumo['shells_compilados']}/{total}")
    print(f"RQ3: Questões executadas sem crash:        {resumo['questoes_com_execucoes_sem_crash']}/{total}")
    print(f"RQ3: Cobertura heurística de comandos:     {resumo['questoes_com_cobertura_de_comandos_ok']}/{total}")

    print("-" * 65)
    print(f"Total de casos mapeados no TOML: {resumo['total_casos_toml']}")
    print(f"Execuções realizadas:            {resumo['total_execucoes']}")
    print(f"Execuções sem crash:             {resumo['execucoes_ok']}/{resumo['total_execucoes']}")
    print(f"Status geral PASSOU:             {resumo['questoes_aprovadas_no_status_geral']}/{total}")

    print("=" * 65)
    print("Observação:")
    print("Este script valida formato, compilação e execução sem crash.")
    print("Ele não valida a correção lógica da saída nem a cobertura semântica completa dos testes.")
    print("=" * 65)


def salvar_relatorio_json(
    caminho_relatorio: Path,
    resultados: list[ResultadoQuestao],
    resumo: dict[str, Any],
) -> None:
    dados = {
        "resumo": resumo,
        "questoes": [asdict(resultado) for resultado in resultados],
    }

    caminho_relatorio.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validar_questoes(
    diretorio_base: Path,
    timeout_segundos: float,
    strict_commands: bool,
) -> list[ResultadoQuestao]:
    caminhos_toml = sorted(diretorio_base.rglob("tests.toml"))

    resultados: list[ResultadoQuestao] = []

    if not caminhos_toml:
        print("Nenhum arquivo tests.toml encontrado.")
        return resultados

    for caminho_toml in caminhos_toml:
        resultado = validar_uma_questao(
            caminho_toml=caminho_toml,
            timeout_segundos=timeout_segundos,
            strict_commands=strict_commands,
        )

        imprimir_resultado_questao(resultado)
        resultados.append(resultado)

    return resultados


def criar_parser_argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validador automatizado de questões geradas: tests.toml + Shell.java."
    )

    parser.add_argument(
        "diretorio",
        nargs="?",
        default=".",
        help="Diretório base onde o script deve procurar por tests.toml. Padrão: diretório atual.",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Tempo máximo, em segundos, para cada execução do Shell.java. Padrão: 2.0.",
    )

    parser.add_argument(
        "--relatorio",
        type=str,
        default=None,
        help="Caminho para salvar um relatório JSON com os resultados.",
    )

    parser.add_argument(
        "--strict-commands",
        action="store_true",
        help=(
            "Faz a validação falhar caso algum comando detectado nas entradas "
            "não apareça explicitamente no Shell.java."
        ),
    )

    return parser


def main() -> None:
    parser = criar_parser_argumentos()
    args = parser.parse_args()

    diretorio_base = Path(args.diretorio).resolve()

    if not diretorio_base.exists():
        print(f"Diretório não encontrado: {diretorio_base}")
        return

    resultados = validar_questoes(
        diretorio_base=diretorio_base,
        timeout_segundos=args.timeout,
        strict_commands=args.strict_commands,
    )

    resumo = gerar_resumo(resultados)
    imprimir_resumo(resumo)

    if args.relatorio:
        caminho_relatorio = Path(args.relatorio).resolve()
        salvar_relatorio_json(
            caminho_relatorio=caminho_relatorio,
            resultados=resultados,
            resumo=resumo,
        )
        print(f"\nRelatório JSON salvo em: {caminho_relatorio}")


if __name__ == "__main__":
    main()