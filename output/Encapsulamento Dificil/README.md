# Encapsulamento em Java: Sistema de Clínica Médica
=====================================================

## Intro

Imagine que você é o gerente de uma clínica médica e precisa desenvolver um sistema para gerenciar os dados dos pacientes. Esse sistema deve ser capaz de armazenar informações como nome, idade, sexo, altura, peso e histórico médico de cada paciente. Além disso, o sistema deve ser capaz de calcular o índice de massa corporal (IMC) de cada paciente.

A classe `Paciente` deve ter os seguintes atributos:

* `nome`: o nome do paciente
* `idade`: a idade do paciente
* `sexo`: o sexo do paciente (M para masculino, F para feminino)
* `altura`: a altura do paciente em centímetros
* `peso`: o peso do paciente em quilogramas
* `historicoMedico`: um array de strings que armazena o histórico médico do paciente

A classe deve ter os seguintes métodos:

* `construtor`: um construtor que inicializa os atributos do paciente
* `getNome()`: um método que retorna o nome do paciente
* `getIdade()`: um método que retorna a idade do paciente
* `getSexo()`: um método que retorna o sexo do paciente
* `getAltura()`: um método que retorna a altura do paciente
* `getPeso()`: um método que retorna o peso do paciente
* `getHistoricoMedico()`: um método que retorna o histórico médico do paciente
* `adicionarHistoricoMedico(String historico)`: um método que adiciona um novo histórico médico ao paciente
* `calcularIMC()`: um método que calcula o índice de massa corporal (IMC) do paciente

## Shell

Aqui estão os 3 primeiros casos de teste para a classe `Paciente`:

```bash
#TEST_CASE iniciando
$addPaciente Joao 25 M 180 70
$show
Nome: Joao, Idade: 25, Sexo: M, Altura: 180.0, Peso: 70.0, Historico Medico: []
$end
```

```bash
#TEST_CASE adicionando historico medico
$addPaciente Joao 25 M 180 70
$addHistoricoMedico Dor de cabeca
$show
Nome: Joao, Idade: 25, Sexo: M, Altura: 180.0, Peso: 70.0, Historico Medico: [Dor de cabeca]
$end
```

```bash
#TEST_CASE calculando IMC
$addPaciente Joao 25 M 180 70
$calcularIMC
IMC: 21.6
$end
```