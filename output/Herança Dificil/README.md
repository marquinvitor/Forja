# Implementação de Herança em Sistema de Supermercado em Java
## Intro
Um sistema de supermercado precisa ser capaz de gerenciar diferentes tipos de produtos, incluindo alimentos, produtos de limpeza e eletrônicos. Cada produto tem um código, nome, preço e quantidade em estoque. Além disso, alimentos têm uma data de validade, produtos de limpeza têm um tipo de limpeza (por exemplo, "limpeza de superfícies", "limpeza de roupa", etc.) e eletrônicos têm um modelo e uma marca.

A classe base `Produto` deve ter os atributos `codigo`, `nome`, `preco` e `quantidadeEstoque`. Ela também deve ter métodos para calcular o valor total do estoque (`calcularValorTotalEstoque`) e para verificar se o produto está em estoque (`verificarEstoque`).

As classes filhas devem ser `Alimento`, `ProdutoLimpeza` e `Eletronico`, e devem herdar os atributos e métodos da classe `Produto`. Além disso, cada classe filha deve ter seus próprios atributos e métodos específicos.

## Shell
### Caso de Teste 1:
```bash
#TEST_CASE iniciando
$addItem arroz 5.0 10 2024-03-15
$show
arroz 5.0 10 2024-03-15
$end
```

### Caso de Teste 2:
```bash
#TEST_CASE adicionando produto de limpeza
$addItem detergente 3.0 20 limpeza de superfícies
$show
detergente 3.0 20 limpeza de superfícies
$end
```

### Caso de Teste 3:
```bash
#TEST_CASE adicionando eletrônico
$addItem tv 1000.0 5 Samsung 4K
$show
tv 1000.0 5 Samsung 4K
$end
```