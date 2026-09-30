# FerragensPro - Sistema de Gerenciamento de Peças

## 🛠️ A História do Projeto

Você é o novo desenvolvedor contratado pela **FerragensPro**, uma loja familiar que há 30 anos abastece construtores e marceneiros em toda a região. O dono, Sr. Carlos, está cansado de anotações manuais no caderno para controlar o estoque de parafusos, kits de ferramentas e acessórios.

O problema é crítico: durante uma grande encomenda para um projeto de reforma urbana, o sistema falhou ao validar as dimensões dos parafusos vendidos (um erro que custou a loja uma multa por venda irregular) e não conseguiu processar a venda de um "Kit Premium" porque faltava apenas uma peça específica dentro do kit.

O Sr. Carlos precisa urgentemente de um software robusto, orientado a objetos, que garanta:
1.  **Validação Rigorosa**: Parafusos só são vendidos se tiverem diâmetro ≥ 3.0mm e comprimento ≥ 10.0mm.
2.  **Integridade dos Kits**: Um kit complexo só pode ser vendido se *todos* os seus componentes estiverem disponíveis no momento da transação.

Sua missão é implementar o núcleo do sistema usando herança (`Produto` -> `Parafuso`, `KitFerramental`) e polimorfismo para garantir que cada tipo de item seja tratado corretamente, evitando prejuízos financeiros e mantendo a reputação da loja.

---

## 📚 Introdução Técnica

O sistema é construído sobre uma hierarquia de classes em Java:

### 1. Classe Abstrata `Produto`
Representa qualquer item vendável na loja.
*   **Atributos**:
    *   `nome`: String (ex: "Parafuso M5", "Kit Básico").
    *   `precoUnitario`: float (Preço em Reais).
    *   `qtdEmEstoque`: int (Quantidade disponível).
*   **Métodos**:
    *   `__init__(nome, preco)`: Inicializa o objeto. Estoque começa em 0.
    *   `vender()`: Método abstrato. Retorna um dicionário com status da venda (`sucesso`, `qtd_vendida`, `valor_total`).
    *   `estoqueAtual()`: Retorna a quantidade atual de itens.

### 2. Classe Concreta `Parafuso` (Subclasse de Produto)
Representa parafusos simples com especificações técnicas.
*   **Atributos Adicionais**:
    *   `diâmetro`: float (mm).
    *   `comprimento`: float (mm).
*   **Lógica de Negócio (`vender`)**:
    *   Valida se `diâmetro >= 3.0` E `comprimento >= 10.0`.
    *   Se válido e estoque > 0: Reduz estoque, retorna sucesso.
    *   Se inválido ou sem estoque: Retorna falha sem alterar o estoque.

### 3. Classe Concreta `KitFerramental` (Subclasse de Produto)
Representa kits compostos por múltiplos itens.
*   **Atributos Adicionais**:
    *   `itens`: Lista de strings com os nomes dos componentes do kit.
*   **Lógica de Negócio (`vender`)**:
    *   Verifica se todos os nomes na lista `itens` possuem estoque > 0 (simulação de disponibilidade interna).
    *   Se todos disponíveis e estoque global > 0: Reduz estoque, retorna sucesso.
    *   Caso contrário: Retorna falha.

---

## 💻 Comandos do Shell

O sistema opera via linha de comando com os seguintes comandos:

| Comando | Descrição | Parâmetros | Exemplo |
| :--- | :--- | :--- | :--- |
| `init` | Cria um novo produto no sistema. | `<Tipo> <Nome> <Parametros> <Preco>` | `init Parafuso M5 2.0 30.00` |
| `vender` | Tenta realizar a venda do último item criado. | N/A | `vender` |
| `show` | Exibe o estado atual (nome, preço, estoque e detalhes) do último item. | N/A | `show` |
| `end` | Finaliza a sessão de teste. | N/A | `end` |

---

## 🧪 Casos de Teste Iniciais (Shell)

Abaixo estão os primeiros casos de teste para validação da lógica de negócio:

```bash
#TEST_CASE iniciando parafuso invalido

$init Parafuso M5 2.0 30.00
$show
nome=Parafuso | preco=30.00 | estoque=0 | tipo=parafuso (d=2.0, L=30.0)
$vender
fail: dimensões inválidas (d<3.0 ou L<10.0)
$end
```

```bash
#TEST_CASE vendendo parafuso valido

$init Parafuso M5 4.0 50.00
$show
nome=Parafuso | preco=50.00 | estoque=1 | tipo=parafuso (d=4.0, L=50.0)
$vender
nome=Parafuso | preco=50.00 | estoque=0 | tipo=parafuso (d=4.0, L=50.0)
$end
```

```bash
#TEST_CASE kit sem itens disponiveis

$init KitFerramental "Básico" 120.00 ["Parafuso M3", "Porca M3"]
$vender
fail: item indisponível no kit
$show
nome=KitFerramental | preco=120.00 | estoque=0 | tipo=kit (itens=["Parafuso M3", "Porca M3"])
$end