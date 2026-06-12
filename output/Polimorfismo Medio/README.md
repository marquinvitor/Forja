# Sistema de Estacionamento com Polimorfismo em Java
## Intro
Imagine que você é o gerente de um estacionamento que precisa atender a diferentes tipos de veículos, desde carros e motos até caminhões. Cada tipo de veículo tem suas próprias características e necessidades, e o estacionamento precisa ser capaz de gerenciar essas diferenças de forma eficiente. Além disso, o estacionamento precisa calcular o valor da estadia de cada veículo com base em seu tipo e tempo de permanência. Para resolver esse problema, você precisa criar um sistema que utilize polimorfismo para gerenciar os diferentes tipos de veículos e calcular o valor da estadia de cada um.

A classe base `Veiculo` deve ter os atributos `placa`, `tipo` e `tempoPermanencia`, além dos métodos `getPlaca()`, `getTipo()`, `getTempoPermanencia()` e `calculaEstadia()`. As classes derivadas `Carro`, `Moto` e `Caminhao` devem herdar da classe `Veiculo` e implementar o método `calculaEstadia()` de acordo com as regras específicas de cada tipo de veículo.

## Shell
Aqui estão alguns casos de teste para você validar a implementação:
```bash
#TEST_CASE carro
$addCarro ABC123 2
$show
Carro ABC123 2 10.0
$end
```

```bash
#TEST_CASE moto
$addMoto DEF456 3
$show
Moto DEF456 3 9.0
$end
```

```bash
#TEST_CASE caminhao
$addCaminhao GHI789 1
$show
Caminhao GHI789 1 10.0
$end
```