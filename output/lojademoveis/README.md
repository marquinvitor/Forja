# Herança na Loja de Móveis – Desafio Avançado

## História  

Ana é a fundadora da **Móveis Sonho**, uma loja que começou em um pequeno galpão de São Paulo e hoje sonha em abrir filiais em todo o país. Seu melhor amigo, **Bruno**, acabou de ser contratado como gerente de estoque e percebeu que o controle manual dos produtos está gerando erros de precificação e de registro de atributos específicos (material da cadeira, forma da mesa, capacidade do sofá).  

Para evitar que a loja perca vendas e para garantir que cada cliente receba exatamente o que pediu, Ana decidiu que é hora de criar um **sistema de gerenciamento de produtos** totalmente orientado a objetos, usando **herança em Java**. O objetivo é que o sistema:

* registre diferentes tipos de móveis com seus atributos exclusivos;  
* calcule o preço final de cada item (aplicando, por exemplo, descontos ou acréscimos);  
* permita consultas rápidas ao estoque via um shell de comandos simples.

## Intro  

O núcleo do sistema é formado por quatro classes:

| Classe | Tipo | Atributos | Construtor | Métodos Principais |
|--------|------|-----------|------------|--------------------|
| **`Produto`** | abstrata | `String nome`<br>`double precoBase` | `Produto(String nome, double precoBase)` | `double calcularPrecoFinal()` (abstrato)<br>`String getNome()`<br>`double getPrecoBase()` |
| **`Cadeira`** | concreta (extends `Produto`) | `String material` | `Cadeira(String nome, double precoBase, String material)` | implementação de `calcularPrecoFinal()` (ex.: +10% se material = “madeira”) |
| **`Mesa`** | concreta (extends `Produto`) | `String forma` | `Mesa(String nome, double precoBase, String forma)` | implementação de `calcularPrecoFinal()` (ex.: +5% se forma = “redonda”) |
| **`Sofa`** | concreta (extends `Produto`) | `int capacidade` | `Sofa(String nome, double precoBase, int capacidade)` | implementação de `calcularPrecoFinal()` (ex.: +15% se capacidade > 3) |

### Comandos disponíveis no shell  

| Comando | Sintaxe | Descrição |
|---------|---------|-----------|
| `addItem` | `addItem <tipo> <nome> <preco> <atributo>` | Cria um novo produto do tipo indicado (`cadeira`, `mesa` ou `sofa`). |
| `show`   | `show` | Lista todos os itens cadastrados no formato `<tipo> <nome> <preco> <atributo>`. |
| `end`    | `end` | Finaliza a sessão. |

## Shell  

A seguir estão os **três primeiros casos de teste** que ilustram o uso do shell. Cada bloco reproduz exatamente o que deve ser digitado e o que o programa deve imprimir.

```bash
#TEST_CASE caso_01

$addItem cadeira cadeira1 100.0 madeira
$show
cadeira cadeira1 100.0 madeira
$end
```

```bash
#TEST_CASE caso_02

$addItem mesa mesa1 200.0 redonda
$addItem sofa sofa1 500.0 3
$show
mesa mesa1 200.0 redonda
sofa sofa1 500.0 3
$end
```

```bash
#TEST_CASE caso_03

$addItem cadeira cadeira2 150.0 plastico
$addItem cadeira cadeira3 120.0 metal
$show
cadeira cadeira2 150.0 plastico
cadeira cadeira3 120.0 metal
$end