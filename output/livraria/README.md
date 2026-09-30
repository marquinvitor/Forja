# Livraria OOP Challenge

## História

Em uma rua movimentada da cidade, a **Livraria Aurora** luta para se manter relevante num mercado dominado por gigantes digitais.  
A dona, **Clara**, percebe que o estoque está desorganizado: livros físicos encalhados, e os títulos digitais não aparecem nas listas de vendas.  
Para salvar o negócio, ela decide criar um sistema que registre **todos os livros**, independente do formato, e que só mostre ao cliente aqueles que realmente podem ser vendidos.  
O desafio é construir, em Java, um modelo orientado a objetos que reflita essa realidade, usando boas práticas de POO e design de interfaces.

## Intro

- **Interface `Livro`**
  - Métodos abstratos:
    - `String getNome()`
    - `String obterPreco()` – devolve o preço formatado como `"R$ 29,90"`.

- **Classe `LivroFisico`** (implementa `Livro`)
  - Atributos: `nome`, `autor`, `preco` (double), `qtdEstoque` (int).
  - Construtor que inicializa todos os atributos.
  - `obterPreco()` formata o `preco` usando a moeda brasileira.

- **Classe `LivroDigital`** (implementa `Livro`)
  - Atributos: `nome`, `autor`, `preco` (double), `formato` (String, ex.: PDF, EPUB), `qtdEstoque` (int) – o campo de estoque serve apenas para a regra de disponibilidade.
  - Construtor que inicializa todos os atributos.
  - `obterPreco()` segue a mesma formatação da classe física.

- **Classe `Livraria`**
  - Atributo privado: `List<Livro> estoque`.
  - `void adicionarLivro(Livro livro)` – adiciona o livro ao estoque **apenas se** `qtdEstoque > 0`.
  - `List<String> listarLivros()` – devolve uma lista contendo apenas os nomes dos livros presentes no estoque.

## Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `add <tipo> "<nome>" "<autor>" <preco> <qtd>` | Cadastra um livro. `<tipo>` pode ser `livroFisico` ou `livroDigital`. |
| `listarLivros` | Exibe a lista de nomes dos livros que foram efetivamente adicionados. |
| `end` | Finaliza a sessão. |

## Shell

```bash
#TEST_CASE caso_basico

$add livroFisico "Dom Casmurro" "Machado de Assis" 45.00 10
$add livroDigital "O Senhor dos Anéis" "J.R.R. Tolkien" 39.90 5
$listarLivros
[ Dom Casmurro O Senhor dos Anéis ]
$end
```

```bash
#TEST_CASE estoque_zero

$add livroFisico "1984" "George Orwell" 25.50 0
$add livroDigital "Duna" "Frank Herbert" 60.00 3
$listarLivros
[ Duna ]
$end
```

```bash
#TEST_CASE adicao_sequencial

$add livroFisico "Harry Potter" "J.K. Rowling" 55.90 15
$listarLivros
[ Harry Potter ]
$add livroDigital "Harry Potter Digital" "J.K. Rowling" 45.00 20
$listarLivros
[ Harry Potter Harry Potter Digital ]
$end