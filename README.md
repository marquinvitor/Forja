# Forja

Gerador de questões de Programação Orientada a Objetos (POO) em Kotlin para o repositório arcade.

Você informa uma descrição em linguagem natural da questão desejada (contexto, classes, comportamentos e tópicos de POO) e define o nome da pasta de saída. O sistema analisa o pedido, busca padrões e exemplos em um repositório arcade de referência e gera a estrutura completa da questão: README.md (com enunciado, regras, diagrama Mermaid, guia de implementação e casos de teste embutidos), src/kt/shell.kt (questão totalmente resolvida e validada pelo auditor), starter/kt/shell.kt (esqueleto em Kotlin com TODOs para o estudante completar) e a pasta assets/ para a imagem de capa.

Todas as atividades são geradas no formato padrão [TRAIN], seguindo rigorosamente as convenções do repositório arcade (https://github.com/qxcodepoo/arcade.git) do professor David Sena Oliveira.

---

## Como funciona

O processo utiliza três agentes coordenados via CrewAI, com um ciclo integrado de auditoria técnica e autocorreção:

1. Designer Instrucional de TI: analisa a descrição do usuário e os tópicos de POO detectados, gerando um rascunho com a história, regras de negócio, comandos aceitos e casos de teste.
2. Especialista em POO Kotlin: transforma o rascunho no README.md padronizado e cria o esqueleto do arquivo shell.kt, com classes estruturadas (métodos com TODO) e a função main completa para interpretação dos comandos via terminal.
3. Auditor Técnico de Qualidade: implementa a solução funcional completa a partir do esqueleto e do enunciado. O sistema compila o código com kotlinc e executa a solução contra todos os casos de teste do README.md.

Se a auditoria detectar divergências de saída, erros de compilação ou falhas de execução, um diagnóstico detalhado é gerado e repassado ao Especialista para correção do README e do esqueleto. Esse ciclo se repete por até 3 tentativas.

Ao final:
- Se aprovada: a questão é salva na pasta de saída contendo o README.md, src/kt/shell.kt (solução completa resolvida), starter/kt/shell.kt (esqueleto para o estudante) e assets/.
- Se não for validada após o limite de tentativas: os arquivos são salvos acompanhados de um diagnostico_final.txt detalhando o problema para revisão manual.

Os agentes mantêm os mesmos papéis com Gemini ou OpenAI. A configuração fica em `settings.json`, fora do projeto, e cada papel recebe um modelo próprio. Por padrão, Gemini usa `gemini-3.5-flash-lite` no rascunho e na auditoria e `gemini-3.8-flash` na revisão; OpenAI usa `gpt-4.1-mini` no rascunho e na auditoria e `gpt-4.1` na revisão.

---

## Tópicos de POO suportados

O módulo `src/topicos_poo.py` identifica automaticamente os tópicos necessários com base na sua descrição, ou permite configurá-los manualmente:

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

O sistema consulta exemplos reais das questões presentes na pasta base do repositório arcade e utiliza um cache de padrões no diretório de cache do usuário para garantir conformidade técnica com o estilo do repositório (classes de domínio puras sem prints, mensagens em inglês na função main, comandos prefixados com cifrão nos testes, tipos explícitos).

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
pip install crewai litellm platformdirs
```

### Configuração

Na primeira execução, a Forja cria `settings.json` no diretório de configuração do usuário. No Linux, o caminho padrão é `~/.config/forja/settings.json`; em outros sistemas, ele é obtido pela biblioteca `platformdirs`.

O catálogo de modelos OpenAI pode ser atualizado usando a chave configurada em `settings.json` ou em `openai_api_key_file`:

```bash
forja models update
```

O comando consulta a API da OpenAI, mantém apenas modelos de texto compatíveis com o fluxo da Forja e grava o catálogo no cache do usuário. Ele não altera automaticamente os modelos já escolhidos nos papéis. O mesmo recurso está disponível pelo botão “Atualizar modelos OpenAI” no painel `forja open`.

O arquivo pode ser criado previamente a partir de [settings.example.json](settings.example.json). As chaves podem estar diretamente no JSON ou em arquivos separados; quando `*_api_key_file` existe, ele tem prioridade:

```json
{
  "llm_provider": "gemini",
  "gemini_api_key_file": "~/.gemini_key.txt",
  "openai_api_key_file": "~/.gpt_key.txt",
  "caminho_repo": null,
  "output_dir": null
}
```

Para usar uma pasta de configuração diferente, informe a pasta na inicialização:

```bash
uv run src/forja.py --settings /caminho/da/configuracao
```

O arquivo usado será `/caminho/da/configuracao/settings.json`. A chave OpenAI precisa ser uma chave da API; uma assinatura do ChatGPT não substitui essa credencial. A chave Gemini pode ser criada no Google AI Studio (https://aistudio.google.com) e a chave OpenAI na plataforma da API (https://platform.openai.com/api-keys).

Sem `output_dir`, os projetos são salvos em `~/forja/`.

Sem `caminho_repo`, a Forja clona automaticamente `https://github.com/qxcodepoo/arcade.git` no cache do usuário e usa a pasta `labs` como repositório de tarefas modelo. Para usar outra fonte, informe manualmente a pasta que contém as tarefas modelo no painel Ambiente.

---

## Uso

Execute o script principal:

Para abrir o painel local de configuração no navegador:

```bash
uv run src/forja.py open
```

Use `--no-browser` para iniciar sem abrir o navegador ou `--port 8765` para escolher uma porta. O painel escuta somente em `127.0.0.1` e encerra quando o processo termina.

O painel também permite criar projetos pela aba `Novo projeto`. A geração roda em um processo separado, com acompanhamento na aba `Projetos`. O histórico fica no banco SQLite de dados do usuário (`platformdirs.user_data_path("forja")/projects.sqlite3`); cada projeto também recebe `.forja/project.json` dentro da própria pasta, permitindo reconstruir o registro se necessário.

Na criação, o campo `Tentativas máximas de correção` define quantos ciclos de auditoria e correção o agente poderá executar; o padrão é 3 e o limite aceito é de 1 a 10.

Quando o provedor ativo é OpenAI, a aba `Novo projeto` oferece a opção de gerar uma capa visual em `assets/cover.webp` usando o modelo configurado em `openai_image_model` (por padrão, `gpt-image-2.5-flare`). A imagem final é paisagem, com exatamente `960 × 540` pixels. A opção fica desabilitada para Gemini.

Por privacidade, o Forja desativa por padrão a telemetria e o tracing do CrewAI. Para habilitar esses recursos conscientemente em uma execução, defina as variáveis `CREWAI_DISABLE_TELEMETRY=false` e `CREWAI_TRACING_ENABLED=true` no ambiente antes de iniciar a ferramenta.

Na aba Ambiente, é possível escolher um terminal Linux instalado e habilitar a abertura automática de um popup acompanhando o `generation.log` durante cada projeto. A lista sinaliza quais emuladores foram encontrados no `PATH`.

Com uv:

```bash
uv run src/forja.py
```

Com venv ativo:

```bash
python src/forja.py
```

O terminal solicitará:

1. Descrição da questão: texto livre descrevendo tema, regras e classes desejadas.
   Exemplo: 3 classes, com encapsulamento, mapas e exceções, no contexto de biblioteca
2. Nome da pasta de saída: nome da pasta que será criada dentro do diretório de dados configurado (exemplo: biblioteca_magica).

Todas as atividades são geradas automaticamente como [TRAIN]. O sistema identificará os tópicos de POO correspondentes e solicitará confirmação antes de disparar os agentes.

---

## Estrutura dos arquivos gerados

Cada questão gerada é salva em uma pasta própria dentro do diretório de dados da Forja com a seguinte organização:

```
forja/nome_da_questao/
├── README.md              # Enunciado, regras, diagrama Mermaid, guide e testes no formato #TEST_CASE
├── src/
│   └── kt/
│       └── shell.kt       # Questão totalmente resolvida (solução validada pelo auditor)
├── starter/
│   └── kt/
│       └── shell.kt       # Esqueleto para o estudante completar (classes com TODO e main implementada)
├── prompt.json             # Título, prompt original e tópicos usados na geração
├── assets/                # Diretório reservado para a imagem de capa (cover.webp)
└── diagnostico_final.txt  # Gerado apenas se a questão não passar em todas as validações
```

---

## Estrutura do projeto

- `src/forja.py`: ponto de entrada da aplicação, leitura do `--settings`, orquestração dos agentes CrewAI e tarefas, salvamento da solução em `src/kt/shell.kt` e do esqueleto em `starter/kt/shell.kt`, e ciclo de auditoria com compilação kotlinc e execução java.
- `src/llm_config.py`: seleção do provedor, modelos por papel e criação dos LLMs para os agentes.
- `src/persistencia.py`: diretórios de configuração, dados e cache, leitura e gravação atômica do `settings.json`.
- `src/painel_web.py` e `src/forja_panel.html`: painel local aberto por `forja open`, com a aba Ambiente e a API de gravação das configurações.
- `src/topicos_poo.py`: regras de detecção de tópicos de POO, extração de código e leitura de padrões do repositório arcade local.
- `settings.example.json`: exemplo de configuração inicial.
- `pyproject.toml` e `uv.lock`: definição e travamento determinístico de dependências do projeto.
