# Sistema de Aeroporto com Herança em Java
## Intro

Imagine que você é o gerente de recursos humanos de um grande aeroporto internacional. Seu aeroporto está crescendo rapidamente e precisa de um sistema para gerenciar os funcionários, pilotos e comissários de bordo. O sistema deve permitir que você crie, edite e exiba informações sobre cada tipo de funcionário. Além disso, o sistema deve ser capaz de lidar com as especificidades de cada tipo de funcionário, como as horas de voo para os pilotos e as línguas faladas para os comissários.

O sistema terá as seguintes classes:

- `Funcionario`: classe pai com atributos `nome`, `idade` e `matricula`. O construtor da classe `Funcionario` deve receber esses três atributos como parâmetros. A classe `Funcionario` deve ter um método `exibirInfo()` que imprima as informações do funcionário.
- `Piloto`: classe filha de `Funcionario` com atributo adicional `horasVoo`. O construtor da classe `Piloto` deve receber os atributos do `Funcionario` mais o `horasVoo`. A classe `Piloto` deve ter um método `exibirInfo()` que imprima as informações do piloto, incluindo o número de horas de voo.
- `Comissario`: classe filha de `Funcionario` com atributo adicional `linguas`. O construtor da classe `Comissario` deve receber os atributos do `Funcionario` mais a lista de `linguas`. A classe `Comissario` deve ter um método `exibirInfo()` que imprima as informações do comissário, incluindo as línguas que fala.

Os comandos disponíveis são:
- `criarFuncionario`: cria um novo funcionário
- `criarPiloto`: cria um novo piloto
- `criarComissario`: cria um novo comissário
- `exibirInfo`: exibe as informações de um funcionário, piloto ou comissário

## Shell

Aqui estão os casos de teste para o sistema:

```bash
#TEST_CASE 1
$criarFuncionario Joao 30 123
$exibirInfo 123
Nome: Joao, Idade: 30, Matricula: 123
$end
```

```bash
#TEST_CASE 2
$criarPiloto Maria 25 456 100
$exibirInfo 456
Nome: Maria, Idade: 25, Matricula: 456, Horas de Voo: 100
$end
```

```bash
#TEST_CASE 3
$criarComissario Jose 40 789 ingles frances
$exibirInfo 789
Nome: Jose, Idade: 40, Matricula: 789, Linguas: ingles, frances
$end
```