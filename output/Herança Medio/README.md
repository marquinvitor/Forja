# Herança em Java: Sistema de Biblioteca

## Intro
Um sistema de biblioteca precisa ser desenvolvido para gerenciar diferentes tipos de itens, como livros, revistas e CDs. O sistema deve ser capaz de armazenar informações sobre cada item, como título, autor, ano de publicação e quantidade em estoque. Além disso, o sistema deve ser capaz de calcular o valor total de cada item com base em seu tipo e quantidade em estoque.

A classe base `Item` deve ter os seguintes atributos:
* `titulo`: uma string que representa o título do item
* `autor`: uma string que representa o autor do item
* `anoPublicacao`: um inteiro que representa o ano de publicação do item
* `quantidadeEstoque`: um inteiro que representa a quantidade do item em estoque

A classe base `Item` deve ter os seguintes métodos:
* `Item(String titulo, String autor, int anoPublicacao, int quantidadeEstoque)`: um construtor que inicializa os atributos do item
* `getValorTotal()`: um método que calcula o valor total do item com base em seu tipo e quantidade em estoque
* `toString()`: um método que retorna uma string que representa o item

As classes `Livro`, `Revista` e `CD` herdam da classe `Item` e têm os seguintes atributos e métodos adicionais:
* `Livro`: um atributo `preco` que representa o preço do livro e um método `getValorTotal()` que calcula o valor total do livro com base em seu preço e quantidade em estoque
* `Revista`: um atributo `preco` que representa o preço da revista e um método `getValorTotal()` que calcula o valor total da revista com base em seu preço e quantidade em estoque
* `CD`: um atributo `preco` que representa o preço do CD e um método `getValorTotal()` que calcula o valor total do CD com base em seu preço e quantidade em estoque

## Shell
Aqui estão os 3 primeiros casos de teste para o sistema de biblioteca:
```bash
#TEST_CASE 1
$addItem Livro Harry Potter J.K. Rowling 2000 10
$show
Título: Harry Potter, Autor: J.K. Rowling, Ano de Publicação: 2000, Quantidade em Estoque: 10, Valor Total: 100.0
$end
```

```bash
#TEST_CASE 2
$addItem Revista Veja Abril 2020 5
$show
Título: Veja, Autor: Abril, Ano de Publicação: 2020, Quantidade em Estoque: 5, Valor Total: 25.0
$end
```

```bash
#TEST_CASE 3
$addItem CD Thriller Michael Jackson 1982 8
$show
Título: Thriller, Autor: Michael Jackson, Ano de Publicação: 1982, Quantidade em Estoque: 8, Valor Total: 64.0
$end
```