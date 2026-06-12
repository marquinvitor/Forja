# Forja

Gerador de questões de POO para o repositório arcade.

Você passa um contexto (cassino, aeroporto, biblioteca), um nível(fácil, médio ou difícil) e um tema de POO(herança, polimorfismo, encapsulamento ...), e ele gera os 3 arquivos da questão prontos: README.md, tests.toml e Shell.java, no mesmo formato das questões do repositório (https://github.com/qxcodepoo/arcade.git) do professor David Sena Oliveira.

---

## Como funciona

Três agentes rodam em sequência via CrewAI:

1. O Designer Instrucional cria o rascunho da questão com história, enunciado e casos de teste
2. O Especialista POO gera o README.md e o tests.toml no formato correto
3. O mesmo Especialista gera o Shell.java com o esqueleto para o aluno completar

Os agentes usam LLaMA 3.3 70B via Groq. Dá pra trocar pra Ollama e rodar local se quiser.
---

## Instalação

Clone o repositório e entre na pasta:

```bash
git clone https://github.com/seu-usuario/forja.git
cd forja
```
Instale as dependências:

```bash
pip install crewai litellm python-dotenv
```

Crie o .env:

```bash
cp .env.example .env
```

Preencha com seus valores: \
GROQ_API_KEY=sua_chave_aqui \
CAMINHO_REPO=/home/seu-usuario/arcade/base \
OUTPUT_DIR=/home/seu-usuario/QuestionCreate/output

A key do groq é gratuita em console.groq.com/keys

---

## Uso

```bash
python Main.py
```

O sistema pede 3 coisas:
Contexto da questão (ex: concessionaria, aeroporto, biblioteca) -  EX: maratona
Nível (Fácil / Médio / Difícil) -  EX: Difícil
Tema POO (ex: Herança e Interfaces, Polimorfismo, Encapsulamento) - EX: Herança

Os arquivos são salvos em output/maratona/.

---

## Rodando local com Ollama

Se não quiser depender do Groq, instale o Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

Troque os LLMs no código:

```python
llm_rascunho = LLM(
    model="ollama/llama3.1:8b",
    base_url="http://localhost:11434",
    temperature=0.5,
    max_tokens=1500
)
```

Rodando local não tem limite de requisição. O ollama8b é Recomendado se sua GPU tem 8GB+ de VRAM.
(Fique livre pra tentar com outros modelos :) )

---

## Dependências

- Python 3.10+
- crewai 0.80+
- litellm 1.0+
- python-dotenv 1.0+
