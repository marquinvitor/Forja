# Encapsulamento em Java: Sistema de Banco
=====================================================

## Intro

Imagine que você é um gerente de um banco que precisa criar um sistema para gerenciar as contas bancárias dos clientes. O sistema deve ser capaz de criar contas, depositar e sacar valores, além de recuperar o saldo e o nome do titular da conta. Para isso, você irá criar uma classe `ContaBancaria` que represente uma conta bancária.

A classe `ContaBancaria` deve ter os seguintes atributos:

* `numeroConta`: um número inteiro que representa o número da conta bancária
* `saldo`: um valor double que representa o saldo atual da conta
* `nomeTitular`: uma string que representa o nome do titular da conta

A classe também deve ter um construtor que inicialize os atributos `numeroConta`, `saldo` e `nomeTitular`.

Além disso, a classe deve ter os seguintes métodos:

* `depositar(valor)`: um método que adiciona um valor ao saldo da conta
* `sacar(valor)`: um método que subtrai um valor do saldo da conta, desde que o valor seja menor ou igual ao saldo atual
* `getSaldo()`: um método que retorna o saldo atual da conta
* `getNomeTitular()`: um método que retorna o nome do titular da conta

## Shell

Aqui estão os 3 primeiros casos de teste para a classe `ContaBancaria`:

```bash
#TEST_CASE criando conta
$addConta 123 1000.0 João
$show
123 1000.0 João
$end
```

```bash
#TEST_CASE depositando valor
$addConta 123 1000.0 João
$depositar 123 500.0
$show
123 1500.0 João
$end
```

```bash
#TEST_CASE sacando valor
$addConta 123 1000.0 João
$sacar 123 200.0
$show
123 800.0 João
$end
```