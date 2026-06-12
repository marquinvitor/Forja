# Encapsulamento em Java: Sistema de Escola
=====================================================

## Intro

Imagine que você é o diretor de uma escola e precisa criar um sistema para gerenciar as informações dos alunos. Você precisa armazenar o nome, matrícula, nota da primeira avaliação e nota da segunda avaliação de cada aluno. Além disso, você precisa calcular a média das notas e verificar se o aluno está aprovado ou não.

A classe `Aluno` deve ter os seguintes atributos:

* `nome`: o nome do aluno
* `matricula`: a matrícula do aluno
* `nota1`: a nota da primeira avaliação
* `nota2`: a nota da segunda avaliação

A classe deve ter um construtor que receba os parâmetros `nome`, `matricula`, `nota1` e `nota2`. Além disso, a classe deve ter os seguintes métodos:

* `getNome()`: retorna o nome do aluno
* `getMatricula()`: retorna a matrícula do aluno
* `getNota1()`: retorna a nota da primeira avaliação
* `getNota2()`: retorna a nota da segunda avaliação
* `calculaMedia()`: calcula e retorna a média das notas do aluno
* `isAprovado()`: verifica se o aluno está aprovado (média >= 7) e retorna um booleano

## Shell

Aqui estão os casos de teste para a classe `Aluno`:

```bash
#TEST_CASE iniciando
$addAluno Joao 12345 8 9
$show
Joao 12345 8 9
$end
```

```bash
#TEST_CASE adicionando outro aluno
$addAluno Maria 67890 5 6
$show
Joao 12345 8 9
Maria 67890 5 6
$end
```

```bash
#TEST_CASE calculando média
$addAluno Pedro 11111 10 10
$show
Joao 12345 8 9
Maria 67890 5 6
Pedro 11111 10 10
$media Pedro
10.0
$end
```