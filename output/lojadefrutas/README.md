# Herança em um Sistema de Loja de Frutas

## História

Ana é a gerente da **Frutaria Sol Nascente**, uma pequena loja que abastece cafés, restaurantes e famílias na cidade de Vila Verde. Nos últimos meses, a demanda por frutas exóticas (como kiwi, maracujá e mangostão) disparou, e Ana percebeu que o sistema de controle de estoque que a loja usa não consegue diferenciar o cálculo de impostos entre frutas comuns e exóticas.  

Para evitar prejuízos e garantir que o preço final cobrado ao cliente já inclua os impostos corretos, Ana decidiu que a loja precisa de um novo software de gerenciamento de estoque, construído em Java e que aproveite **herança** para reutilizar código e manter a lógica de cálculo de preço bem organizada.

## Intro

O sistema deve modelar os produtos da loja usando herança:

| Classe | Atributos | Construtor | Métodos |
|--------|-----------|------------|---------|
| **`Produto`** (abstrata) | `String nome` – nome da fruta<br>`double precoBase` – preço antes de impostos | `Produto(String nome, double precoBase)` | `abstract double precoFinal()` – devolve o preço já com impostos<br>`String getNome()` |
| **`Fruta`** (estende `Produto`) | `String origem` – país ou região de origem | `Fruta(String nome, double precoBase, String origem)` | `precoFinal()` – aplica **5 %** de imposto sobre o preço base |
| **`FrutaExotica`** (estende `Fruta`) | (herda `origem`) | `FrutaExotica(String nome, double precoBase, String origem)` | `precoFinal()` – aplica **15 %** de imposto (5 % da classe `Fruta` + 10 % extra) |

## Shell

O programa funciona como um *shell* que recebe comandos via **stdin** e ecoa cada comando precedido por `$`.  
Os comandos disponíveis são:

| Comando | Descrição |
|---------|-----------|
| `init N` | Cria um novo estoque com capacidade para **N** produtos. |
| `addFruit <nome> <precoBase> <origem>` | adiciona uma `Fruta` ao estoque. |
| `addExotic <nome> <precoBase> <origem>` | adiciona uma `FrutaExotica` ao estoque. |
| `show` | lista todos os produtos no estoque, um por linha, no formato `<nome> <precoFinal> <origem>`. |
| `end` | encerra a sessão. |

### Testes de exemplo

```bash
# TEST_CASE 01 - fruta simples
$init 10
$addFruit banana 1.00 Brazil
$show
banana 1.05 Brazil
$end
```

```bash
# TEST_CASE 02 - fruta exótica
$init 5
$addExotic kiwi 2.00 NewZealand
$show
kiwi 2.30 NewZealand
$end
```

```bash
# TEST_CASE 03 - mistura de frutas
$init 3
$addFruit apple 3.00 USA
$addExotic mangosteen 4.00 Thailand
$addFruit orange 2.50 Spain
$show
apple 3.15 USA
mangosteen 4.60 Thailand
orange 2.63 Spain
$end