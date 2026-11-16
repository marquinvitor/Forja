# Forja

Gerador de questões de Programação Orientada a Objetos (POO) em Kotlin para o repositório arcade.

Você informa uma descrição em linguagem natural da questão desejada (contexto, classes, comportamentos e tópicos de POO) e define o nome da pasta de saída. O sistema analisa o pedido, busca padrões e exemplos em um repositório arcade de referência e gera a estrutura completa da questão: README.md (com enunciado, regras, diagrama Mermaid, guia de implementação e casos de teste embutidos), src/kt/main.kt (questão totalmente resolvida e validada pelo auditor), src/kt/shell.kt (esqueleto em Kotlin com TODOs para o estudante completar) e a pasta assets/ para a imagem de capa.

Todas as atividades são geradas no formato padrão [TRAIN], seguindo rigorosamente as convenções do repositório arcade (https://github.com/qxcodepoo/arcade.git) do professor David Sena Oliveira.

---

## Como funciona

O processo utiliza três agentes coordenados via CrewAI, com um ciclo integrado de auditoria técnica e autocorreção:

1. Designer Instrucional de TI: analisa a descrição do usuário e os tópicos de POO detectados, gerando um rascunho com a história, regras de negócio, comandos aceitos e casos de teste.
2. Especialista em POO Kotlin: transforma o rascunho no README.md padronizado e cria o esqueleto do arquivo shell.kt, com classes estruturadas (métodos com TODO) e a função main completa para interpretação dos comandos via terminal.
3. Auditor Técnico de Qualidade: implementa a solução funcional completa a partir do esqueleto e do enunciado. O sistema compila o código com kotlinc e executa a solução contra todos os casos de teste do README.md.

Se a auditoria detectar divergências de saída, erros de compilação ou falhas de execução, um diagnóstico detalhado é gerado e repassado ao Especialista para correção do README e do esqueleto. Esse ciclo se repete por até 3 tentativas.

Ao final:
- Se aprovada: a questão é salva na pasta de saída contendo o README.md, src/kt/main.kt (solução completa resolvida), src/kt/shell.kt (esqueleto para o estudante) e assets/.
- Se não for validada após o limite de tentativas: os arquivos são salvos acompanhados de um diagnostico_final.txt detalhando o problema para revisão manual.

Os agentes utilizam modelos Gemini (gemini-3.5-flash-lite para rascunho e auditoria, e gemini-3.8-flash para geração e revisão) via LiteLLM.

---

## Tópicos de POO suportados

O módulo topicos_poo.py identifica automaticamente os tópicos necessários com base na sua descrição, ou permite configurá-los manualmente:

- Classes e Objetos
- Encapsulamento e Invariantes
- Agregação e Delegação
- Desafios de agregação e estados
- Coleções lineares
- Posições fixas e ausência
- Exceções
- Mapas
- Índices e Redundância
- Polimorfismo

O sistema consulta exemplos reais das questões presentes na pasta base do repositório arcade e utiliza os padrões catalogados em padroes.json para garantir conformidade técnica com o estilo do repositório (classes de domínio puras sem prints, mensagens em inglês na função main, comandos prefixados com cifrão nos testes, tipos explícitos).

---

## Requisitos

- Python 3.12+
- Gerenciador de pacotes uv (recomendado) ou pip
- Java JDK 17+ (comandos javac e java no PATH)
- Compilador Kotlin CLI (comando kotlinc no PATH, necessário para a validação do auditor)

No Arch Linux:

```bash
sudo pacman -S jdk-openjdk kotlin
```

No Ubuntu / Debian:

```bash
sudo apt update
sudo apt install default-jdk
```

Para instalar o kotlinc via SDKMAN:

```bash
sdk install kotlin
```

---

## Instalação

Clone o repositório e acesse a pasta:

```bash
git clone https://github.com/marquinvitor/Forja.git
cd Forja
```

### Opção 1: Usando uv (Recomendado)

Se tiver o uv instalado, sincronize as dependências diretamente:

```bash
uv sync
```

### Opção 2: Usando venv e pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install crewai litellm python-dotenv
```

### Configuração de variáveis de ambiente

Copie o arquivo de exemplo e crie o seu .env:

```bash
cp .env.example .env
```

Edite o arquivo .env com suas configurações:

```ini
GEMINI_API_KEY=sua_chave_gemini_aqui
CAMINHO_REPO=/home/seu-usuario/arcade/base
OUTPUT_DIR=/home/seu-usuario/Forja/output
```

A chave da API Gemini pode ser gerada gratuitamente no Google AI Studio (https://aistudio.google.com).
O CAMINHO_REPO deve apontar para o diretório base do repositório arcade clonado localmente.
O OUTPUT_DIR é a pasta onde as novas questões serão criadas.

---

## Uso

Execute o script principal:

Com uv:

```bash
uv run Forja.py
```

Com venv ativo:

```bash
python Forja.py
```

O terminal solicitará:

1. Descrição da questão: texto livre descrevendo tema, regras e classes desejadas.
   Exemplo: 3 classes, com encapsulamento, mapas e exceções, no contexto de biblioteca
2. Nome da pasta de saída: nome da pasta que será criada dentro de OUTPUT_DIR (exemplo: biblioteca_magica).

Todas as atividades são geradas automaticamente como [TRAIN]. O sistema identificará os tópicos de POO correspondentes e solicitará confirmação antes de disparar os agentes.

---

## Estrutura dos arquivos gerados

Cada questão gerada é salva em uma pasta própria dentro de output/ com a seguinte organização:

```
output/nome_da_questao/
├── README.md              # Enunciado, regras, diagrama Mermaid, guide e testes no formato #TEST_CASE
├── src/
│   └── kt/
│       ├── main.kt        # Questão totalmente resolvida (solução validada pelo auditor)
│       └── shell.kt       # Esqueleto para o estudante completar (classes com TODO e main implementada)
├── assets/                # Diretório reservado para a imagem de capa (cover.webp)
└── diagnostico_final.txt  # Gerado apenas se a questão não passar em todas as validações
```

---

## Estrutura do projeto

- Forja.py: ponto de entrada da aplicação, orquestração dos agentes CrewAI, tarefas, integração com LiteLLM, salvamento do esqueleto (shell.kt) e da solução (main.kt), e ciclo de auditoria com compilação kotlinc e execução java.
- topicos_poo.py: regras de detecção de tópicos de POO, extração de código e leitura de padrões do repositório arcade local.
- padroes.json: catálogo de boas práticas e convenções observadas em cada tópico de POO.
- pyproject.toml e uv.lock: definição e travamento determinístico de dependências do projeto.
