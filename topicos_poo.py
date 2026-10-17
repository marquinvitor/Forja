"""
topicos_poo.py  (versão simples)

Ideia: o sistema aprende "como o professor aplica cada tópico" olhando as questões reais.

  1. TOPICOS: índice tópico -> questões-exemplo do repositório (edite à vontade).
  2. detectar_topicos(): descrição natural -> ids de tópicos (palavras-chave + LLM opcional).
  3. obter_padrao(): o LLM lê o exemplo real e resume como o tópico foi aplicado.
     O resultado é salvo em padroes.json -> revise/corrija esse arquivo à mão.
  4. preparar(): devolve o texto de contexto pronto para injetar nos prompts.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Callable, Optional

# ─────────────────────────────────────────────────────────────────────────────
# 1. ÍNDICE: tópico -> questões do repositório (slug = trecho do nome da pasta)
#    O PRIMEIRO exemplo de cada lista é o preferido.
# ─────────────────────────────────────────────────────────────────────────────

TOPICOS: dict[str, dict] = {
    "classes_objetos": {
        "titulo": "Classes e Objetos", "requer": [],
        "palavras": ["early return", "retorno antecipado", "enum", "enumeracao", "ciclo de vida", "classes e objetos"],
        "exemplos": ["toalha", "animal", "carro", "calculadora"],
    },
    "encapsulamento_invariantes": {
        "titulo": "Encapsulamento e Invariantes", "requer": [],
        "palavras": ["encapsulamento", "encapsular", "encapsulado", "invariante", "privado", "getter", "setter", "validar", "validacao", "estado valido"],
        "exemplos": ["chinela", "camisa", "roupa", "relogio"],
    },
    "agregacao_delegacao": {
        "titulo": "Agregação e Delegação", "requer": ["encapsulamento_invariantes"],
        "palavras": ["agregacao", "agregar", "delegacao", "delegar", "referencia opcional", "nullable", "coordenador"],
        "exemplos": ["motoca", "grafite", "motouber"],
    },
    "desafios_agregacao_estados": {
        "titulo": "Desafios de agregação e estados", "requer": ["agregacao_delegacao"],
        "palavras": ["estado terminal", "morte", "bateria", "carregador", "coordenacao de estados", "componente"],
        "exemplos": ["tamagotchi", "charger"],
    },
    "colecoes_lineares": {
        "titulo": "Coleções lineares", "requer": ["encapsulamento_invariantes"],
        "palavras": ["lista", "array", "colecao", "fila", "composicao", "filtro"],
        "exemplos": ["contato", "pula-pula", "lapiseira"],
    },
    "posicoes_fixas_ausencia": {
        "titulo": "Posições fixas e ausência", "requer": ["colecoes_lineares"],
        "palavras": ["posicao fixa", "posicoes fixas", "capacidade fixa", "ausencia", "objeto vazio", "vetor fixo", "cadeira"],
        "exemplos": ["cinema", "budega"],
    },
    "excecoes": {
        "titulo": "Exceções", "requer": ["encapsulamento_invariantes"],
        "palavras": ["excecao", "excecoes", "exception", "throw", "try", "catch", "illegalargument"],
        "exemplos": ["bermuda", "birita", "junkfood", "cofrinho"],
    },
    "mapas": {
        "titulo": "Mapas", "requer": ["colecoes_lineares"],
        "palavras": ["mapa", "map", "dicionario", "chave", "identidade", "codenome", "identificador unico"],
        "exemplos": ["agenda", "agiota"],
    },
    "indices_redundancia": {
        "titulo": "Índices e Redundância", "requer": ["mapas"],
        "palavras": ["indice secundario", "indices secundarios", "redundancia", "favoritos"],
        "exemplos": ["favoritos", "ligacao"],
    },
    "polimorfismo": {
        "titulo": "Polimorfismo", "requer": ["colecoes_lineares"],
        "palavras": ["polimorfismo", "interface", "classe abstrata", "heranca", "substituicao", "contrato comum"],
        "exemplos": ["zoo", "pagamento", "shapes", "estacionamento", "cofre", "cadastro"],
    },
}

REGRA_BASE = (
    "REGRA GERAL DO REPOSITÓRIO: as classes de domínio nunca imprimem nada; devolvem o resultado "
    "(boolean, enum, null ou exceção, conforme o tópico). O Shell lê os comandos, ecoa '$comando', "
    "chama o domínio e escreve as mensagens 'fail: ...'. Os testes verificam só o comportamento "
    "observável pelo Shell, incluindo falhas e estado preservado."
)

# Nomes de arquivo considerados "solução" dentro da pasta de uma questão.
# Ajuste conforme a estrutura real do seu repositório.
ORDEM_LINGUAGENS = [".kt", ".java", ".ts", ".py"]   # preferência ao escolher a solução
SUFIXOS_CODIGO = set(ORDEM_LINGUAGENS)
DICAS_SOLUCAO = ("solution", "solucao", "gabarito", "shell", "main")

PADROES_JSON = Path(__file__).with_name("padroes.json")


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


# ─────────────────────────────────────────────────────────────────────────────
# 2. DETECTAR TÓPICOS
# ─────────────────────────────────────────────────────────────────────────────

def detectar_topicos(descricao: str, chamar_llm: Optional[Callable[[str], str]] = None) -> list[str]:
    texto = _norm(descricao)
    ids = [tid for tid, t in TOPICOS.items()
           if any(re.search(r"\b" + re.escape(_norm(p)) + r"(?:s|es)?\b", texto) for p in t["palavras"])]

    if chamar_llm is not None and not ids:  # palavras-chave bastam; LLM só como plano B
        print("  → nenhuma palavra-chave reconhecida; pedindo ajuda ao LLM para detectar os tópicos...")
        catalogo = "\n".join(f"- {tid}: {t['titulo']}" for tid, t in TOPICOS.items())
        prompt = (f"Quais tópicos do catálogo o pedido abaixo exige? Responda SOMENTE com uma lista JSON de ids.\n"
                  f"{catalogo}\n\nPEDIDO: {descricao}")
        try:
            m = re.search(r"\[.*?\]", chamar_llm(prompt), re.DOTALL)
            for tid in json.loads(m.group(0)) if m else []:
                if tid in TOPICOS and tid not in ids:
                    ids.append(tid)
        except Exception as e:  # noqa: BLE001
            print(f"⚠ LLM não ajudou na detecção ({type(e).__name__}); usando só palavras-chave.")
    return ids


# ─────────────────────────────────────────────────────────────────────────────
# 3. LER EXEMPLO REAL + EXTRAIR PADRÃO (com cache revisável)
# ─────────────────────────────────────────────────────────────────────────────

def localizar_questao(caminho_repo: str, slug: str) -> Optional[Path]:
    for d in sorted(Path(caminho_repo).iterdir()):
        if d.is_dir() and not d.name.startswith("+") and _norm(slug) in _norm(d.name) and (d / "README.md").exists():
            return d
    return None


def _limpar_readme(texto: str) -> str:
    """Tira o que não ensina nada ao modelo (diagrama mermaid, imagem, comentários HTML)
    e transforma o front matter (Descrição/Domínio/Objetivos) em um resumo legível."""
    resumo = ""
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.DOTALL)
    if m:
        linhas = [l.strip() for l in m.group(1).splitlines() if l.strip().startswith("-")]
        resumo = "\n".join(linhas) + "\n\n"
        texto = texto[m.end():]
    texto = re.sub(r"```mermaid.*?```", "", texto, flags=re.DOTALL)
    texto = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", texto)
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.DOTALL)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return (resumo + texto).strip()


def ler_exemplo(pasta: Path, limite_readme: int = 2200, limite_codigo: int = 1200) -> str:
    """Formato atual da questão:
         <questao>/README.md          (front matter, Intro, Regras, Guide com esqueleto, testes)
         <questao>/assets/            (capa; ignorada)
         <questao>/src/<lang>/...     (solução de referência)
       Compatível também com o formato antigo (tests.toml solto na pasta)."""
    readme = _limpar_readme((pasta / "README.md").read_text(encoding="utf-8"))
    partes = [f"--- README (resumo, enunciado, regras e testes) ---\n{readme[:limite_readme]}"]

    toml = pasta / "tests.toml"
    if toml.exists():  # formato antigo
        partes.append(f"--- TESTES ---\n{toml.read_text(encoding='utf-8')[:600]}")

    raiz_src = pasta / "src" if (pasta / "src").is_dir() else pasta
    codigos = [f for f in raiz_src.rglob("*") if f.is_file() and f.suffix in SUFIXOS_CODIGO]
    codigos.sort(key=lambda f: (ORDEM_LINGUAGENS.index(f.suffix),
                                not any(d in f.name.lower() for d in DICAS_SOLUCAO)))
    if codigos:
        c = codigos[0]
        partes.append(f"--- SOLUÇÃO DE REFERÊNCIA ({c.parent.name}/{c.name}) ---\n"
                      f"{c.read_text(encoding='utf-8')[:limite_codigo]}")
    return "\n\n".join(partes)


def _ler_cache() -> dict:
    return json.loads(PADROES_JSON.read_text(encoding="utf-8")) if PADROES_JSON.exists() else {}


def obter_padrao(topico: str, slug: str, exemplo: str, chamar_llm: Optional[Callable[[str], str]]) -> str:
    """Resumo de 'como este tópico foi aplicado nesta questão'. Gerado uma vez, depois vem do cache."""
    chave = f"{topico}/{slug}"
    cache = _ler_cache()
    if cache.get(chave):
        return cache[chave]
    if chamar_llm is None:
        return ""
    print(f"  → resumindo o exemplo '{slug}' ({TOPICOS[topico]['titulo']}); "
          f"só na 1ª vez, depois fica salvo em padroes.json...")

    prompt = f"""Você analisa uma questão de POO de um repositório didático.
Tópico a observar: {TOPICOS[topico]['titulo']}.

Descreva em NO MÁXIMO 6 linhas curtas COMO esse tópico foi aplicado NESTA questão:
1) atributos/estruturas usados e se são privados;
2) qual método guarda a regra e o que ele retorna;
3) como as falhas são comunicadas;
4) o que a interface (Shell ou laço do main) faz;
5) o que os testes verificam.
Seja específico a esta questão, sem teoria genérica. Responda só com as linhas.

{exemplo}"""
    padrao = chamar_llm(prompt).strip()[:900]
    print("    ✓ resumo pronto" if padrao else "    ⚠ resposta vazia do modelo (verifique servidor/modelo no LM Studio)")
    if padrao:
        cache[chave] = padrao
        PADROES_JSON.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return padrao


# ─────────────────────────────────────────────────────────────────────────────
# 4. PREPARAR O CONTEXTO PARA OS PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

def preparar(descricao: str, caminho_repo: str,
             chamar_llm: Optional[Callable[[str], str]] = None,
             topicos: Optional[list[str]] = None,
             max_chars: int = 6000) -> tuple[list[str], str]:
    """Devolve (topicos_usados, texto_de_contexto).

    Passe `topicos=[...]` para escolher à mão (sem detecção automática).
    Tópicos pedidos: padrão + exemplo completo. Pré-requisitos: só o padrão.
    """
    pedidos = [t for t in (topicos or detectar_topicos(descricao, chamar_llm)) if t in TOPICOS]
    if not pedidos:
        raise ValueError("Nenhum tópico reconhecido. Passe topicos=[...] ou use palavras do vocabulário.")
    prereqs = [r for t in pedidos for r in TOPICOS[t]["requer"] if r not in pedidos]
    prereqs = list(dict.fromkeys(prereqs))

    print("Tópicos:", ", ".join(TOPICOS[t]["titulo"] for t in pedidos))
    if prereqs:
        print("Pré-requisitos (só o padrão):", ", ".join(TOPICOS[t]["titulo"] for t in prereqs))

    def achar(topico: str) -> tuple[Optional[str], Optional[Path]]:
        for slug in TOPICOS[topico]["exemplos"]:
            pasta = localizar_questao(caminho_repo, slug)
            if pasta:
                return slug, pasta
        print(f"⚠ Nenhuma questão do tópico '{topico}' encontrada no repositório.")
        return None, None

    blocos_padrao, blocos_exemplo = [], []
    for topico in pedidos + prereqs:
        slug, pasta = achar(topico)
        if not pasta:
            continue
        exemplo = ler_exemplo(pasta)
        padrao = obter_padrao(topico, slug, exemplo, chamar_llm)
        cab = f"### {TOPICOS[topico]['titulo']} — exemplo do repositório: {slug}"
        blocos_padrao.append(f"{cab}\nComo foi aplicado:\n{padrao or '(sem resumo; veja o exemplo)'}")
        if topico in pedidos:
            blocos_exemplo.append(f"{cab}\n{exemplo}")

    distribuicao = (
        "DISTRIBUIÇÃO: antes de escrever, decida qual classe da nova questão recebe qual tópico "
        f"({', '.join(TOPICOS[t]['titulo'] for t in pedidos)}). Todo tópico pedido precisa aparecer "
        "em pelo menos uma classe, aplicado do mesmo modo que nos exemplos. Não copie o domínio dos "
        "exemplos; copie a FORMA de aplicar o conceito."
    )

    contexto = REGRA_BASE + "\n\n=== COMO O PROFESSOR APLICOU CADA TÓPICO ===\n" + "\n\n".join(blocos_padrao)
    contexto += "\n\n" + distribuicao
    # exemplos completos entram enquanto couberem
    extras = []
    for b in blocos_exemplo:
        if len(contexto) + sum(len(x) for x in extras) + len(b) <= max_chars:
            extras.append(b)
    if extras:
        contexto += "\n\n=== EXEMPLOS COMPLETOS ===\n" + "\n\n".join(extras)
    return pedidos, contexto