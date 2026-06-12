import os
import random
from pathlib import Path
from crewai import Agent, Task, Crew, Process, LLM
import litellm
from dotenv import load_dotenv

load_dotenv()

CHAVE_GROQ   = os.getenv("GROQ_API_KEY")
CAMINHO_REPO = os.getenv("CAMINHO_REPO", os.path.expanduser("~/arcade/base"))
OUTPUT_DIR   = os.getenv("OUTPUT_DIR", os.path.expanduser("~/QuestionCreate/output"))

if not CHAVE_GROQ:
    raise ValueError("GROQ_API_KEY não encontrada no .env")

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


def carregar_exemplos(caminho_base: str, max_exemplos: int = 2) -> str:
    base = Path(caminho_base)
    questoes = [
        d for d in base.iterdir()
        if d.is_dir()
        and not d.name.startswith("+")
        and (d / "README.md").exists()
        and (d / "tests.toml").exists()
    ]

    selecionadas = random.sample(questoes, min(max_exemplos, len(questoes)))

    contexto = ""
    for questao in selecionadas:
        readme = (questao / "README.md").read_text(encoding="utf-8")
        testes = (questao / "tests.toml").read_text(encoding="utf-8")

        secao_intro = ""
        secoes = readme.split("## ")
        for secao in secoes:
            if secao.startswith("Intro"):
                secao_intro = secao.strip()

        contexto += f"""
=== EXEMPLO: {questao.name} ===
--- ENUNCIADO ---
{secao_intro[:600]}

--- TESTES ---
{testes[:500]}

"""
    return contexto.strip()


def salvar_arquivos(output_dir: str, nome: str, readme: str, toml: str, shell: str):
    pasta = Path(output_dir) / nome
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "README.md").write_text(readme, encoding="utf-8")
    (pasta / "tests.toml").write_text(toml, encoding="utf-8")
    (pasta / "Shell.java").write_text(shell, encoding="utf-8")
    print(f"\nArquivos salvos em: {pasta}")


def extrair_bloco(texto: str, marcador: str) -> str:
    inicio = texto.find(f"<<<{marcador}>>>")
    fim = texto.find("<<<END>>>", inicio)
    if inicio == -1 or fim == -1:
        return ""
    return texto[inicio + len(f"<<<{marcador}>>>"):fim].strip()


# config

llm_rascunho = LLM(
    model="openai/llama-3.3-70b-versatile",
    api_key=CHAVE_GROQ,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.5,
    max_retries=3,
    max_tokens=1500
)

llm_revisao = LLM(
    model="openai/llama-3.3-70b-versatile",
    api_key=CHAVE_GROQ,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.3,
    max_retries=3,
    max_tokens=2000
)


# Input do usuario

print("=== Gerador de Questões POO ===\n")
contexto_usuario = input("Contexto da questão (ex: concessionaria, aeroporto, biblioteca): ").strip()
nivel            = input("Nível (Fácil / Médio / Difícil): ").strip()
tema_poo         = input("Tema POO (ex: Herança e Interfaces, Polimorfismo, Encapsulamento): ").strip()
nome_questao     = contexto_usuario.lower().replace(" ", "_")

entrada_usuario = f"Crie uma questão nível {nivel} sobre {tema_poo} em Java, contextualizada num sistema de {contexto_usuario}."


# contexto

print("\nCarregando exemplos do repositório...")
exemplos = carregar_exemplos(CAMINHO_REPO, max_exemplos=2)

# Exemplo de esqueleto para o shell.java, que mantém a responsabilidade para os alunos de implementar a lógica de classes e métodos.

SHELL_ESQUELETO_EXEMPLO = """
import java.util.ArrayList;
import java.util.Scanner;

// ── EXEMPLO DE CONTEXTO: piscina / atletas ────────────────────────────────
// As classes abaixo mostram o PADRÃO esperado de esqueleto.
// O modelo deve criar classes equivalentes para o contexto da questão gerada.

class Atleta {
    String nome;
    int idade;
    int experiencia;

    public Atleta(String nome, int idade, int experiencia) {
        // TODO: inicialize os atributos
    }

    public String getInfo() {
        // TODO: retorne as informações do atleta formatadas
        return "";
    }
}

class Nadador extends Atleta {
    String estilo;
    double tempoMedio;

    public Nadador(String nome, int idade, int experiencia, String estilo, double tempoMedio) {
        super(nome, idade, experiencia);
        // TODO: inicialize os atributos específicos de Nadador
    }

    public String getDesempenho() {
        // TODO: retorne "ouro", "prata" ou "bronze" com base no tempoMedio
        return "";
    }

    @Override
    public String getInfo() {
        // TODO: retorne as informações completas do nadador
        return "";
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Atleta> atletas = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("addAtleta")) {
                var nome = par[1];
                var idade = Integer.parseInt(par[2]);
                var experiencia = Integer.parseInt(par[3]);
                atletas.add(new Atleta(nome, idade, experiencia));
            } else if (cmd.equals("addNadador")) {
                var nome = par[1];
                var idade = Integer.parseInt(par[2]);
                var experiencia = Integer.parseInt(par[3]);
                var estilo = par[4];
                var tempoMedio = Double.parseDouble(par[5]);
                atletas.add(new Nadador(nome, idade, experiencia, estilo, tempoMedio));
            } else if (cmd.equals("show")) {
                for (Atleta a : atletas) {
                    System.out.println(a.getInfo());
                }
            } else {
                System.out.println("fail: comando invalido\\n");
            }
        }
    }
}
"""

# ─── AGENTES ─────────────────────────────────────────────────────────────────

designer_criativo = Agent(
    role='Designer Instrucional de TI',
    goal='Criar enunciados claros no nível de dificuldade solicitado.',
    backstory='Professor que transforma conceitos de programação em desafios práticos.',
    verbose=False,
    allow_delegation=False,
    max_iter=2,
    llm=llm_rascunho
)

especialista_poo = Agent(
    role='Especialista em POO Java',
    goal='Garantir rigor técnico, sintaxe correta e gerar os arquivos finais.',
    backstory='Desenvolvedor sênior com foco em design patterns e ensino de POO.',
    verbose=False,
    allow_delegation=False,
    max_iter=2,
    llm=llm_revisao
)

# ─── TAREFAS ─────────────────────────────────────────────────────────────────

tarefa_rascunho = Task(
    description=f"""Crie uma questão de programação para: "{entrada_usuario}".

Exemplos do repositório para seguir o formato:
{exemplos}

Sua questão deve ter:
- Título
- Seção "Intro" com descrição detalhada dos atributos, construtor e métodos
- Seção "Shell" com 5 casos de teste no formato entrada/saída dos exemplos acima

Não inclua gabarito. Apenas enunciado e testes.""",
    expected_output='Enunciado completo com título, Intro e Shell com casos de teste.',
    agent=designer_criativo
)

tarefa_arquivos = Task(
    description=f"""Com base na questão criada, gere o README.md e o tests.toml.

REGRAS CRÍTICAS PARA O tests.toml:
- O input NUNCA contém código Java. São apenas comandos de texto simples como "addCli maria 500"
- Cada linha do input é um comando seguido de parâmetros separados por espaço
- O output espelha cada comando com $ na frente, seguido do resultado esperado
- Todo caso de teste termina com o comando "end"

O formato OBRIGATÓRIO é exatamente este, sem exceções:

[[tests]]
input = '''
addItem cadeira 100.0 40 30
addItem mesa 200.0 80 40
show
end
'''
output = '''
$addItem cadeira 100.0 40 30
$addItem mesa 200.0 80 40
$show
cadeira 100.0 40 30
mesa 200.0 80 40
$end
'''

PROIBIDO no input:
- Código Java (new, =, (, ), ;)
- Nomes de classes
- Declarações de variáveis

REGRAS PARA O README.md:
- O enunciado deve ter uma HISTÓRIA criativa e envolvente relacionada ao contexto "{contexto_usuario}"
  como se fosse um cenário real do mercado de trabalho, apresentando personagens, um problema
  concreto e por que o sistema precisa ser construído
- A seção Intro deve descrever os atributos, construtor e métodos esperados
- A seção Shell deve conter os 3 PRIMEIROS casos de teste do TOML, no mesmo formato
  (blocos ```bash com #TEST_CASE nome, os comandos e saídas esperadas)
- Exemplo de como apresentar um teste na seção Shell do README:

```bash
#TEST_CASE iniciando

$addItem cadeira 100.0
$show
cadeira 100.0
$end
```

Use EXATAMENTE estes marcadores:

<<<README>>>
(README.md com título, história criativa na Intro, comandos disponíveis e seção Shell com os 3 primeiros testes)
<<<END>>>

<<<TOML>>>
(tests.toml com TODOS os casos [[tests]] no formato correto)
<<<END>>>""",
    expected_output='Dois blocos <<<README>>> e <<<TOML>>>, cada um fechado com <<<END>>>.',
    agent=especialista_poo
)

tarefa_shell = Task(
    description=f"""Com base na questão e nos testes gerados, crie o Shell.java.

OBJETIVO: gerar um ESQUELETO para o aluno completar.

REGRA PRINCIPAL — dois tipos de conteúdo no arquivo:

1. CLASSES (totalmente vazias para o aluno implementar):
   - Declare os atributos com o tipo correto, mas SEM inicializar valores.
   - O construtor deve ter os parâmetros corretos, mas o corpo contém apenas:
       // TODO: inicialize os atributos
   - Cada método deve ter a assinatura correta e o tipo de retorno correto, mas o corpo contém apenas:
       // TODO: implemente este método
       return ""; // (ou return 0; ou return null; conforme o tipo)
   - Herança (extends) e anotações (@Override) devem aparecer normalmente.
   - NÃO escreva nenhuma lógica real nas classes.

2. MÉTODO main (completamente implementado):
   - Loop while(true) com scanner.nextLine() e System.out.println("$" + line)
   - split(" ") e var cmd = par[0]
   - Um else-if por comando presente nos testes, com:
       • Extração de parâmetros do array par[] com os tipos corretos (parseInt, parseDouble etc.)
       • Instanciação correta da classe com new
       • Chamada ao método correto (add em lista, println no resultado etc.)
   - Bloco else com: System.out.println("fail: comando invalido\\n");
   - Listas (ArrayList) declaradas como atributos estáticos da classe Shell, fora da main.
   - NÃO deixe TODOs nem comentários na main — ela deve funcionar se o aluno implementar as classes.

Siga o padrão deste exemplo (adapte classes e comandos ao contexto "{contexto_usuario}"):
{SHELL_ESQUELETO_EXEMPLO}

Use EXATAMENTE este marcador:

<<<SHELL>>>
(conteúdo completo do Shell.java)
<<<END>>>""",
    expected_output='Um bloco <<<SHELL>>> com o Shell.java completo fechado com <<<END>>>.',
    agent=especialista_poo
)

# ─── EXECUÇÃO ────────────────────────────────────────────────────────────────

equipe = Crew(
    agents=[designer_criativo, especialista_poo],
    tasks=[tarefa_rascunho, tarefa_arquivos, tarefa_shell],
    process=Process.sequential
)

print("Gerando questão...\n")
resultado = equipe.kickoff()

# extração e salvamento

saidas = [str(t.output) for t in equipe.tasks if t.output]
tudo = "\n".join(saidas)

readme = extrair_bloco(tudo, "README")
toml   = extrair_bloco(tudo, "TOML")
shell  = extrair_bloco(tudo, "SHELL")

if readme and toml and shell:
    salvar_arquivos(OUTPUT_DIR, nome_questao, readme, toml, shell)
    print("✓ README.md")
    print("✓ tests.toml")
    print("✓ Shell.java")
else:
    faltando = [n for n, v in [("README", readme), ("TOML", toml), ("SHELL", shell)] if not v]
    print(f"\nBlocos não encontrados: {faltando}")
    print("\nSaída bruta:\n")
    print(tudo)