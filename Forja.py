import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from crewai import Agent, Task, Crew, Process, LLM
import litellm
from dotenv import load_dotenv

from topicos_poo import preparar, TOPICOS

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CAMINHO_REPO   = os.getenv("CAMINHO_REPO", os.path.expanduser("~/arcade/base"))
OUTPUT_DIR     = os.getenv("OUTPUT_DIR", os.path.expanduser("~/QuestionCreate/output"))

TIPOS_VALIDOS  = ["GUIDE", "TRAIN", "ALONE", "CHECK"]
MAX_TENTATIVAS = 3

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada no .env")

# gambiarra pra nao usar cache
litellm.cache = None
_orig_completion = litellm.completion

def _safe_completion(**kwargs):
    if isinstance(kwargs.get("cache"), bool):
        kwargs.pop("cache")
    for msg in kwargs.get("messages", []):
        msg.pop("cache_breakpoint", None)
        if isinstance(msg.get("content"), list):
            for bloco in msg["content"]:
                if isinstance(bloco, dict):
                    bloco.pop("cache_control", None)
    return _orig_completion(**kwargs)

litellm.completion = _safe_completion
os.environ["CREWAI_DISABLE_PROMPT_CACHING"] = "true"


# ─── blocos de texto gerados pelos agentes ───────────────────────────────────

def _limpar_cercas_markdown(texto: str) -> str:
    """tira aqueles marcadores ```kotlin ... que ficavam saindo nos blocos"""
    texto = texto.strip()
    texto = re.sub(r"^```[a-zA-Z0-9_-]*[ \t]*\n?", "", texto)
    texto = re.sub(r"\n?```[ \t]*$", "", texto)
    return texto.strip()


def extrair_bloco(texto: str, marcador: str) -> str:
    inicio = texto.find(f"<<<{marcador}>>>")
    fim = texto.find("<<<END>>>", inicio)
    if inicio == -1 or fim == -1:
        return ""
    bruto = texto[inicio + len(f"<<<{marcador}>>>"):fim].strip()
    return _limpar_cercas_markdown(bruto)


def extrair_codigo(texto: str, marcador: str) -> str:
    """Como extrair_bloco, mas tolerante para CÓDIGO: aceita resposta cortada (sem <<<END>>>)
    e, como último recurso, pega o primeiro bloco ``` da resposta."""
    codigo = extrair_bloco(texto, marcador)
    if codigo:
        return codigo
    abre = f"<<<{marcador}>>>"
    ini = texto.find(abre)
    if ini != -1:
        resto = texto[ini + len(abre):]
        prox = re.search(r"<<<[A-Z]+>>>", resto)
        if prox:
            resto = resto[:prox.start()]
        return _limpar_cercas_markdown(resto.replace("<<<END>>>", "").strip())
    m = re.search(r"```(?:kotlin|kt)?[ \t]*\n(.*?)```", texto, re.DOTALL)
    return m.group(1).strip() if m else ""


# ─── testes: agora vivem dentro do README, em blocos ```bash ─────────────────
# Cada caso:
#   #TEST_CASE nome
#
#   $comando digitado        <- linhas com "$" são a ENTRADA (o programa as repete)
#   saída do programa        <- o caso inteiro é a SAÍDA esperada
#   $end

def parsear_casos(texto: str) -> list[dict]:
    casos, atual = [], None
    for linha in texto.splitlines():
        if linha.startswith("#TEST_CASE"):
            if atual:
                casos.append(atual)
            atual = {"nome": linha[len("#TEST_CASE"):].strip() or f"teste{len(casos) + 1}", "linhas": []}
        elif atual is not None:
            atual["linhas"].append(linha.rstrip())
    if atual:
        casos.append(atual)

    testes = []
    for c in casos:
        linhas = list(c["linhas"])
        while linhas and not linhas[0].strip():
            linhas.pop(0)
        while linhas and not linhas[-1].strip():
            linhas.pop()
        entradas = [l[1:] for l in linhas if l.startswith("$")]
        if entradas:
            testes.append({"nome": c["nome"], "input": "\n".join(entradas) + "\n", "output": "\n".join(linhas)})
    return testes


def extrair_testes_readme(readme: str) -> list[dict]:
    blocos = re.findall(r"```bash[ \t]*\n(.*?)```", readme, re.DOTALL)
    return parsear_casos("\n".join(blocos))


def inserir_guia(readme: str, esqueleto: str) -> str:
    """Coloca o esqueleto numa seção '## Guide' logo antes de '## Shell' (formato do repositório)."""
    if "## Guide" in readme:
        return readme
    guia = f"## Guide\n\n```kotlin\n{esqueleto.strip()}\n```\n\n"
    if "## Shell" in readme:
        return readme.replace("## Shell", guia + "## Shell", 1)
    return readme.rstrip() + "\n\n" + guia


def salvar_questao(output_dir: str, nome: str, readme: str, solucao: str):
    pasta = Path(output_dir) / nome
    (pasta / "assets").mkdir(parents=True, exist_ok=True)
    (pasta / "src" / "kt").mkdir(parents=True, exist_ok=True)
    (pasta / "README.md").write_text(readme, encoding="utf-8")
    if solucao:
        (pasta / "src" / "kt" / "main.kt").write_text(solucao, encoding="utf-8")
    print(f"\nQuestão salva em: {pasta}")
    print("✓ README.md (enunciado, esqueleto e testes)")
    print("✓ src/kt/main.kt (solução do auditor)" if solucao else "⚠ Sem solução para salvar em src/kt/")
    print("⚠ Falta adicionar a capa: assets/cover.webp")


# ─── compilação e execução do Kotlin ─────────────────────────────────────────

def _normalizar(saida: str) -> str:
    return "\n".join(linha.rstrip() for linha in saida.strip("\n").splitlines())


def comparar_saida(esperado: str, obtido: str) -> bool:
    return _normalizar(esperado) == _normalizar(obtido)


def compilar_e_executar(codigo_kt: str, testes: list[dict], timeout_execucao: int = 15) -> dict:
    """compila a solução com kotlinc e executa cada caso de teste (extraídos do README)."""

    if shutil.which("kotlinc") is None or shutil.which("java") is None:
        return {"sucesso": False, "etapa": "ambiente", "resultados": [],
                "detalhe": "kotlinc/java não encontrados no PATH. Instale com SDKMAN: 'sdk install kotlin' (e um JDK)."}

    if not testes:
        return {"sucesso": False, "etapa": "testes", "resultados": [],
                "detalhe": "Nenhum caso de teste válido no README (use blocos ```bash com '#TEST_CASE nome' e linhas '$comando')."}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "main.kt").write_text(codigo_kt, encoding="utf-8")

        try:
            compilacao = subprocess.run(
                ["kotlinc", "main.kt", "-include-runtime", "-d", "main.jar"],
                cwd=tmp_path, capture_output=True, text=True, timeout=240,  # kotlinc é lento na 1ª vez
            )
        except subprocess.TimeoutExpired:
            return {"sucesso": False, "etapa": "compilacao", "detalhe": "Timeout ao compilar (> 240s).", "resultados": []}

        if compilacao.returncode != 0:
            return {"sucesso": False, "etapa": "compilacao", "resultados": [],
                    "detalhe": (compilacao.stderr or compilacao.stdout).strip()[:2000]}

        resultados, todos_ok = [], True
        for i, teste in enumerate(testes, start=1):
            nome = teste["nome"]
            try:
                ex = subprocess.run(["java", "-jar", "main.jar"], cwd=tmp_path, input=teste["input"],
                                    capture_output=True, text=True, timeout=timeout_execucao)
            except subprocess.TimeoutExpired:
                todos_ok = False
                resultados.append({"teste": i, "nome": nome, "ok": False,
                                   "detalhe": f"Timeout (> {timeout_execucao}s) — possível loop infinito ou leitura além do esperado."})
                continue

            if ex.returncode != 0 and ex.stderr.strip():
                todos_ok = False
                resultados.append({"teste": i, "nome": nome, "ok": False,
                                   "detalhe": f"Exceção em tempo de execução:\n{ex.stderr.strip()[:800]}"})
            elif comparar_saida(teste["output"], ex.stdout):
                resultados.append({"teste": i, "nome": nome, "ok": True})
            else:
                todos_ok = False
                resultados.append({"teste": i, "nome": nome, "ok": False,
                                   "detalhe": f"Saída divergente.\n--- Esperado ---\n{teste['output'].strip()}\n--- Obtido ---\n{ex.stdout.strip()}"})

        return {"sucesso": todos_ok, "etapa": "execucao" if todos_ok else "testes",
                "detalhe": "" if todos_ok else "Um ou mais casos de teste falharam.", "resultados": resultados}


def formatar_relatorio(resultado: dict) -> str:
    if resultado["sucesso"]:
        return "Todos os testes passaram. Compilação e execução consistentes."
    linhas = [f"Etapa com falha: {resultado['etapa']}"]
    if resultado.get("detalhe"):
        linhas.append(resultado["detalhe"])
    for r in resultado.get("resultados", []):
        if not r["ok"]:
            linhas.append(f"\n--- Teste {r['teste']} ({r.get('nome', '')}) ---\n{r.get('detalhe', '')}")
    return "\n".join(linhas)


def kickoff_seguro(crew: Crew, contexto: str) -> bool:
    """Executa crew.kickoff() capturando erros de API (rate limit, resposta vazia, timeout etc.)
    para não derrubar o processo inteiro com um stack trace e perder os artefatos já gerados."""
    try:
        crew.kickoff()
        return True
    except Exception as e:
        print(f"\n⚠ Erro ao executar '{contexto}': {type(e).__name__}: {e}")
        print("Interrompendo o ciclo de auditoria aqui e mantendo a última versão válida disponível.")
        return False


# config  (troque pelos modelos que você escolheu; o pensamento conta no max_tokens, então deixe folga)

llm_rascunho = LLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=GEMINI_API_KEY,
    temperature=1.0,
    max_retries=3,
    timeout=600,
    max_tokens=8000
)

llm_revisao = LLM(
    model="gemini/gemini-3.8-flash",
    api_key=GEMINI_API_KEY,
    temperature=1.0,
    max_retries=3,
    timeout=600,
    max_tokens=16000
)

llm_auditoria = LLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=GEMINI_API_KEY,
    temperature=1.0,
    max_retries=3,
    timeout=600,
    max_tokens=16000
)


# ─── agentes ─────────────────────────────────────────────────────────────────

designer_criativo = Agent(
    role='Designer Instrucional de TI',
    goal='Criar enunciados claros aplicando os tópicos pedidos exatamente como o repositório os aplica.',
    backstory='Professor que transforma conceitos de programação em desafios práticos.',
    verbose=False,
    allow_delegation=False,
    max_iter=2,
    llm=llm_rascunho
)

especialista_poo = Agent(
    role='Especialista em POO Kotlin',
    goal='Garantir rigor técnico, sintaxe correta e gerar os arquivos finais em Kotlin.',
    backstory='Desenvolvedor sênior de Kotlin com foco em design patterns e ensino de POO.',
    verbose=False,
    allow_delegation=False,
    max_iter=2,
    llm=llm_revisao
)

auditor_tecnico = Agent(
    role='Auditor Técnico de Qualidade',
    goal='Produzir uma solução de referência completa e correta em Kotlin a partir do enunciado, para validar a consistência técnica da questão.',
    backstory=(
        'Engenheiro de QA especialista em Kotlin, focado em garantir que toda questão publicada '
        'seja tecnicamente irretocável antes de chegar aos alunos. Não confia em enunciados: '
        'implementa a solução do zero e deixa a compilação/execução real falarem por si.'
    ),
    verbose=False,
    allow_delegation=False,
    max_iter=2,
    llm=llm_auditoria
)


def chamar_llm(prompt: str) -> str:
    """Chamada simples ao LLM (detectar tópicos / resumir exemplos). Se falhar, devolve '' em vez de derrubar o programa."""
    try:
        return str(llm_auditoria.call([{"role": "user", "content": prompt}]))
    except Exception as e:
        print(f"⚠ chamar_llm falhou: {type(e).__name__}: {e}")
        return ""


# Input do usuario

print("=== Gerador de Questões POO (Kotlin) ===\n")
print("Tópicos disponíveis:", ", ".join(TOPICOS.keys()), "\n")
descricao = input(
    "Descreva a questão (ex: '3 classes, com encapsulamento, mapas e exceções, no contexto de biblioteca'):\n> "
).strip()
tipo = input(f"Tipo da atividade {TIPOS_VALIDOS} (padrão TRAIN): ").strip().upper()
if tipo not in TIPOS_VALIDOS:
    tipo = "TRAIN"
nome_questao = input("Nome da pasta de saída: ").strip().lower().replace(" ", "_") or "questao"

print("\nAnalisando tópicos e carregando exemplos do repositório...")
topicos, exemplos = preparar(descricao, CAMINHO_REPO, chamar_llm)
# Para fixar os tópicos manualmente (sem detecção automática), use:
# topicos, exemplos = preparar(descricao, CAMINHO_REPO, chamar_llm,
#                              topicos=["encapsulamento_invariantes", "mapas", "excecoes"])

topicos_txt = ", ".join(TOPICOS[t]["titulo"] for t in topicos)
contexto_usuario = descricao
entrada_usuario = descricao

confirma = input("\nContinuar com esses tópicos? [S/n] ").strip().lower()
if confirma == "n":
    raise SystemExit(0)


# ─── formatos e regras (constantes raw: têm {}, $ e \\ que quebrariam f-strings) ──────

FORMATO_README = r"""---
index_content: |2
    - Descrição: (uma frase)
    - Domínio: (uma frase)
    - Objetivos: (uma frase)
---
# [TIPO] Título da questão

<!-- toc-table -->

![_](assets/cover.webp)

## Intro

(história criativa + descrição dos atributos, construtor e métodos)

## Regras

- (uma regra por linha)

## Diagrama

```mermaid
%%{init: { "fontFamily": "monospace" } }%%
classDiagram
    direction TB

    class Slipper {
        +MIN_SIZE : Int$
        -size : Int
        +getSize() Int
        +setSize(size : Int) Boolean
    }

    class Main {
        +main() Unit
    }

    Main ..> Slipper : creates and uses
```

## Shell

```bash
#TEST_CASE iniciando

$init lion roar
$show
lion:0:roar
$grow 1
$noise
roar
$end
```

```bash
#TEST_CASE morrendo

$init cat meow
$grow 4
warning: animal is dead
$noise
RIP
$end
```

<!-- MERMAID -->"""

REGRAS_TESTES = r"""REGRAS DOS CASOS DE TESTE (blocos ```bash dentro de "## Shell"):
- Cada caso começa com "#TEST_CASE nome_curto" (sem espaços no nome) seguido de uma linha em branco.
- TODA linha de comando começa com "$" (sem exceção) e usa só argumentos de UMA palavra, sem aspas.
- As linhas sem "$" são o que o programa imprime como resultado do comando logo acima.
- O programa repete cada comando com "$" na frente, então a saída esperada inclui as linhas "$comando".
- Todo caso termina com "$end".
- No mínimo 5 casos, incluindo falhas, valores de fronteira, estado preservado e uma sequência de operações."""

REGRAS_MAIN = r"""   - As mensagens do programa ficam em constantes no TOPO do arquivo, antes das classes, em inglês:
       const val INVALID_COMMAND_MSG: String = "fail: invalid command"
     (uma constante *_MSG para cada mensagem de falha ou aviso usada pela main).
   - A main é a ÚLTIMA coisa do arquivo: 'fun main(): Unit'.
   - O estado manipulado pelos comandos é declarado DENTRO da main, antes do loop, com valor neutro.
     Exemplo: var currentAnimal: Animal = Animal("", "")   (coleções: val itens: MutableList<Item> = mutableListOf())
   - Loop 'while (true)' com exatamente esta leitura:
       val line: String = readLine() ?: break
       println("$" + line)
       val parts: List<String> = line.trim().split(Regex("\\s+"))
   - 'when (parts[0])' com UM ramo por comando, em um destes formatos:
       "end" -> break
       "init" -> currentAnimal = Animal(parts[1], parts[2])                  (cria ou atribui)
       "show" -> println(currentAnimal)                                       (mostra o objeto via toString)
       "noise" -> println(currentAnimal.makeSound())                          (imprime o retorno do método)
       "grow" -> if (!currentAnimal.grow(parts[1].toInt())) { println(DEAD_ANIMAL_MSG) }   (traduz Boolean/enum/null em mensagem)
     Converta parâmetros direto em parts[i] com toInt()/toDouble().
   - Ramo final: else -> println(INVALID_COMMAND_MSG)
   - As classes NUNCA imprimem: só a main escreve na saída. Para exibir um objeto, a main faz println(obj)
     e a classe implementa toString(); o formato do toString faz parte da saída esperada dos testes.
   - Se houver exceções, a main usa try/catch por ramo e imprime a mensagem correspondente.
   - O main DEVE tratar todos os comandos que os testes usam."""

SHELL_ESQUELETO_EXEMPLO = r"""
const val DEAD_ANIMAL_MSG: String = "warning: animal is dead"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Animal(private val species: String, private val noise: String) {
    companion object {
        const val DEAD_STAGE: Int = 4
    }

    private var lifeStage: Int = 0

    fun makeSound(): String {
        TODO("retorne o som conforme o estágio de vida")
    }

    fun grow(stages: Int): Boolean {
        TODO("envelheça o animal; retorne false se já estiver morto ou se morrer agora")
    }

    override fun toString(): String {
        TODO("retorne a representação textual do animal")
    }
}

fun main(): Unit {
    var currentAnimal: Animal = Animal("", "")

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> currentAnimal = Animal(parts[1], parts[2])
            "show" -> println(currentAnimal)
            "noise" -> println(currentAnimal.makeSound())
            "grow" -> if (!currentAnimal.grow(parts[1].toInt())) {
                println(DEAD_ANIMAL_MSG)
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}
"""

REGRAS_MENSAGENS = (
    "As explicações do enunciado ficam em português, mas as MENSAGENS PRODUZIDAS PELO PROGRAMA "
    "(ex.: 'fail: invalid size', 'fail: invalid command') ficam em inglês, e são escritas só na main."
)

ESTILO_KOTLIN = (
    "ESTILO KOTLIN DO REPOSITÓRIO: tipos explícitos em tudo (val x: Int = 0), 'fun main(): Unit', "
    "atributos 'private var' ou 'private val', métodos getX()/setX() escritos à mão, constantes em "
    "'companion object' com 'const val', entrada com readLine() ?: break, conversões com toInt()/toDouble(). "
    "Use apenas a biblioteca padrão do Kotlin (kotlin.*); Kotlin NÃO tem printf: use println com templates de string."
)

ESCOPO = (
    "ESCOPO: implemente SOMENTE o que o pedido do professor e os tópicos pedem. Não invente recursos extras "
    "que não foram pedidos."
)


# ─── tasks ──────────────────────────────────────────────────────

tarefa_rascunho = Task(
    description=f"""Crie uma questão de programação em Kotlin para o seguinte pedido do professor:
"{entrada_usuario}"

Tópicos que a questão DEVE aplicar: {topicos_txt}.
{ESCOPO}

{exemplos}

Sua questão deve:
- Aplicar cada tópico pedido do MESMO modo que nos exemplos acima (copie a forma de aplicar o conceito,
  não o domínio dos exemplos);
- Ter Título;
- Ter Descrição, Domínio e Objetivos, uma frase cada (como no resumo do início dos exemplos);
- Ter uma Intro com a história e a descrição das classes, atributos, construtor e métodos;
- Ter uma lista de Regras;
- Listar os COMANDOS do programa (nome, argumentos de uma palavra, e o que imprimem);
- Ter 5 casos de teste (comandos e saída esperada).

{REGRAS_MENSAGENS}

Não inclua gabarito. Apenas enunciado e testes.""",
    expected_output='Enunciado completo com título, descrição, domínio, objetivos, intro, regras, comandos e casos de teste.',
    agent=designer_criativo
)

tarefa_arquivos = Task(
    description=f"""Com base na questão criada, escreva o README.md COMPLETO, exatamente no formato do repositório.
Tipo da atividade (use no título): [{tipo}]
Contexto da história: "{contexto_usuario}"
Tópicos aplicados: {topicos_txt}.

FORMATO (siga a estrutura e os nomes das seções; troque o conteúdo entre parênteses):
{FORMATO_README}

{REGRAS_TESTES}

REGRAS DO README:
- A Intro deve ter uma HISTÓRIA criativa e envolvente relacionada ao contexto, como um cenário real de trabalho,
  com personagens, um problema concreto e o motivo de o sistema ser construído; depois descreva as classes,
  atributos, construtor, métodos, comandos e mensagens esperados.
- O diagrama deve refletir as classes da questão, com os tipos de retorno corretos.
- NÃO inclua a seção "## Guide": o esqueleto de código é inserido automaticamente.
- {REGRAS_MENSAGENS}

Use EXATAMENTE este marcador:

<<<README>>>
(README.md completo)
<<<END>>>""",
    expected_output='Um bloco <<<README>>> com o README.md completo, fechado com <<<END>>>.',
    agent=especialista_poo
)

tarefa_shell = Task(
    description=f"""Com base na questão e nos testes gerados, crie o main.kt (em Kotlin).
Tópicos aplicados na questão: {topicos_txt}.

{ESTILO_KOTLIN}

OBJETIVO: gerar um ESQUELETO para o aluno completar.

REGRA PRINCIPAL — dois tipos de conteúdo no arquivo:

1. CLASSES (para o aluno implementar):
   - Declare os atributos com tipo explícito e valor neutro ("" / 0 / 0.0 / false / lista vazia), para o arquivo compilar.
     Se o enunciado pede encapsulamento, use 'private'.
   - Cada método deve ter a assinatura correta e o tipo de retorno correto, e o corpo contém APENAS:
       TODO("descreva o que o método deve fazer")
   - Se precisar inicializar no construtor, use um bloco init contendo apenas: // TODO: inicialize os atributos
   - Use herança ('open class' / 'override'), enum class, MutableMap, exceções etc. SOMENTE se o enunciado exigir.
   - NÃO escreva nenhuma lógica real nas classes.

2. FUNÇÃO main (completamente implementada, SIGA ESTAS REGRAS EXATAMENTE):
{REGRAS_MAIN}

O exemplo abaixo serve APENAS para mostrar o FORMATO do arquivo (adapte classes e comandos ao contexto
"{contexto_usuario}"; NÃO copie o domínio da questão animal):
{SHELL_ESQUELETO_EXEMPLO}

Use EXATAMENTE este marcador:

<<<SHELL>>>
(conteúdo completo do main.kt)
<<<END>>>""",
    expected_output='Um bloco <<<SHELL>>> com o main.kt completo (esqueleto) fechado com <<<END>>>.',
    agent=especialista_poo
)


# ─── tasks do ciclo de auditoria ──────────────────────────────────────────

def criar_tarefa_gabarito(readme: str, shell: str) -> Task:
    return Task(
        description=f"""Você é o Auditor Técnico. Com base no enunciado (README) e no esqueleto (main.kt)
abaixo, implemente uma SOLUÇÃO DE REFERÊNCIA completa e funcional em Kotlin, substituindo todos os
TODO(...) e comentários TODO por lógica correta.

--- README ---
{readme}

--- MAIN.KT (ESQUELETO) ---
{shell}

{ESTILO_KOTLIN}

REGRAS:
- Mantenha a assinatura de todas as classes, atributos, construtores e métodos exatamente como estão no esqueleto.
- Implemente toda a lógica de acordo com o que o README descreve.
- Não altere a função main nem os comandos que ela reconhece.
- O código deve compilar sem erros com kotlinc.
- Responda DIRETAMENTE com o marcador, sem raciocínio e sem texto fora do bloco.

IMPORTANTE: não envolva o código em blocos markdown (```). Escreva o main.kt diretamente entre o marcador
de abertura e <<<END>>>: o conteúdo vai direto para o compilador. NÃO esqueça de fechar com <<<END>>>.

<<<GABARITO>>>
(main.kt completo, com todas as classes implementadas)
<<<END>>>""",
        expected_output='Um bloco <<<GABARITO>>> com o main.kt totalmente implementado, fechado com <<<END>>>.',
        agent=auditor_tecnico
    )


def criar_tarefa_correcao(readme: str, shell: str, diagnostico: str, contexto: str,
                          exemplos_repo: str, topicos_txt: str) -> Task:
    return Task(
        description=f"""A questão abaixo falhou na auditoria técnica automática. Corrija o README.md (incluindo os
casos de teste) e/ou o main.kt (esqueleto) para eliminar os problemas apontados no relatório.

Tópicos que a questão deve aplicar: {topicos_txt}.

{ESTILO_KOTLIN}

{exemplos_repo}

--- RELATÓRIO DE DIAGNÓSTICO (compilação/execução real) ---
{diagnostico}

--- README ATUAL ---
{readme}

--- MAIN.KT ATUAL (ESQUELETO) ---
{shell}

INSTRUÇÕES:
- Identifique a causa raiz: esqueleto mal especificado (assinatura, tipo de retorno, main fora do padrão),
  caso de teste com comando ou saída incorreta, ou inconsistência entre enunciado e comandos do main.
- Corrija apenas o necessário, sem descaracterizar a questão. Preserve o pedido original: "{contexto}"
- O README continua no formato do repositório (front matter, Intro, Regras, Diagrama, Shell) e SEM a seção "## Guide".
{REGRAS_TESTES}
- O main.kt entregue continua sendo um ESQUELETO: métodos só com TODO("..."), e a main completa:
{REGRAS_MAIN}

Use EXATAMENTE estes marcadores (sem cercas markdown em volta dos blocos):

<<<README>>>
(README.md completo corrigido)
<<<END>>>

<<<SHELL>>>
(main.kt corrigido, ainda como esqueleto com TODO)
<<<END>>>""",
        expected_output='Dois blocos <<<README>>> e <<<SHELL>>>, cada um fechado com <<<END>>>.',
        agent=especialista_poo
    )


# ─── execucao da geracao de questoes ────────────────────────────────────────────

equipe = Crew(
    agents=[designer_criativo, especialista_poo],
    tasks=[tarefa_rascunho, tarefa_arquivos, tarefa_shell],
    process=Process.sequential
)

print("\nGerando questão...\n")
if not kickoff_seguro(equipe, "geração do rascunho inicial"):
    raise SystemExit(1)

saida_arquivos = str(tarefa_arquivos.output) if tarefa_arquivos.output else ""
saida_shell    = str(tarefa_shell.output) if tarefa_shell.output else ""

readme_atual = extrair_bloco(saida_arquivos, "README")
shell_atual  = extrair_codigo(saida_shell, "SHELL")

if not (readme_atual and shell_atual and extrair_testes_readme(readme_atual)):
    print("\nFaltou algum bloco (README, SHELL) ou o README não tem casos de teste válidos.")
    print("\n--- Saída bruta (README) ---\n" + saida_arquivos)
    print("\n--- Saída bruta (SHELL) ---\n" + saida_shell)
    raise SystemExit(1)


# ─── ciclo de auditoria e correção ───────────────────────────────────────────
# a cada tentativa: gera a solução a partir do esqueleto, compila e executa contra os testes do README.
# se falhar, manda o diagnóstico pro especialista_poo corrigir, e tenta de novo.

aprovado = False
gabarito_atual = ""
diagnostico = ""

for tentativa in range(1, MAX_TENTATIVAS + 1):
    print(f"\n=== Auditoria técnica — tentativa {tentativa}/{MAX_TENTATIVAS} ===")

    if "TODO" not in shell_atual:
        # o esqueleto veio com a lógica pronta: não há nada para o aluno implementar
        diagnostico = ("O main.kt entregue não é um esqueleto: não contém nenhum TODO. Os métodos das classes devem ter "
                       "apenas TODO(\"...\") no corpo; só a função main fica completa.")
        gabarito_atual = ""
    else:
        crew_auditoria = Crew(agents=[auditor_tecnico],
                              tasks=[criar_tarefa_gabarito(readme_atual, shell_atual)],
                              process=Process.sequential)
        tarefa_gabarito = crew_auditoria.tasks[0]
        if not kickoff_seguro(crew_auditoria, f"gabarito (tentativa {tentativa})"):
            diagnostico = diagnostico or "Ciclo interrompido por erro de API antes de concluir a auditoria."
            break

        saida_auditor = str(tarefa_gabarito.output) if tarefa_gabarito.output else ""
        gabarito_atual = extrair_codigo(saida_auditor, "GABARITO")

        if not gabarito_atual:
            print("Auditor não retornou um bloco <<<GABARITO>>> válido. Início da resposta recebida:")
            print(saida_auditor[:600] or "(resposta vazia — veja se o modelo esgotou os tokens 'pensando')")
            diagnostico = "O Auditor Técnico não produziu uma solução de referência no formato esperado."
        else:
            print("Compilando (kotlinc pode demorar) e executando a solução contra os casos de teste do README...")
            resultado = compilar_e_executar(gabarito_atual, extrair_testes_readme(readme_atual))
            diagnostico = formatar_relatorio(resultado)

            if resultado["etapa"] == "ambiente":
                print(f"⚠ {resultado['detalhe']}")
                print("Auditoria automática indisponível; salvando a questão sem validação.")
                break

            if resultado["sucesso"]:
                print("✓ Compilação e todos os testes passaram — questão validada tecnicamente.")
                aprovado = True
                break

    print(f"✗ Falhas detectadas:\n{diagnostico}")

    if tentativa == MAX_TENTATIVAS:
        print("\nLimite de tentativas atingido sem consistência técnica total.")
        break

    print("Enviando relatório de diagnóstico ao Especialista para correção...")
    tarefa_correcao = criar_tarefa_correcao(readme_atual, shell_atual, diagnostico,
                                            contexto_usuario, exemplos, topicos_txt)
    crew_correcao = Crew(agents=[especialista_poo], tasks=[tarefa_correcao], process=Process.sequential)
    if not kickoff_seguro(crew_correcao, f"correção (tentativa {tentativa})"):
        break

    saida_correcao = str(tarefa_correcao.output) if tarefa_correcao.output else ""
    novo_readme = extrair_bloco(saida_correcao, "README")
    novo_shell  = extrair_codigo(saida_correcao, "SHELL")

    if novo_readme and novo_shell and extrair_testes_readme(novo_readme):
        readme_atual, shell_atual = novo_readme, novo_shell
    else:
        print("Correção incompleta recebida do Especialista; mantendo versão anterior para a próxima tentativa.")


# ─── salvamento (só no final, depois do ciclo) ───────────────────────────────

status = (
    "APROVADA na auditoria técnica"
    if aprovado
    else f"NÃO validada após {MAX_TENTATIVAS} tentativas (recomenda-se revisão manual)"
)
print(f"\nStatus final da questão: {status}")

salvar_questao(OUTPUT_DIR, nome_questao, inserir_guia(readme_atual, shell_atual), gabarito_atual)

if not aprovado:
    log_path = Path(OUTPUT_DIR) / nome_questao / "diagnostico_final.txt"
    log_path.write_text(diagnostico, encoding="utf-8")
    print(f"✗ Diagnóstico final salvo em: {log_path}")