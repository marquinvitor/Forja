# Herança em Java: Sistema de Aeroporto

## Intro
O Aeroporto Internacional de São Paulo está passando por uma grande reforma para melhorar a eficiência e a segurança de suas operações. Como parte desse processo, o gerente de operações, Sr. João, precisa de um sistema para gerenciar os veículos e aviões que utilizam o aeroporto. O sistema deve ser capaz de armazenar informações sobre os veículos, como marca, modelo e ano, e também informações específicas sobre os aviões, como capacidade de passageiros e altitude máxima.

O sistema terá duas classes: `Veiculo` e `Aviao`. A classe `Veiculo` terá os seguintes atributos: `marca`, `modelo` e `ano`. Além disso, terá um construtor que inicializa esses atributos e um método `imprimirInformacoes()` que imprime as informações do veículo.

A classe `Aviao` irá herdar da classe `Veiculo` e terá os seguintes atributos adicionais: `capacidadePassageiros` e `altitudeMaxima`. Além disso, terá um método `imprimirInformacoesAviao()` que imprime as informações do avião, incluindo as informações herdadadas da classe `Veiculo`.

Os comandos disponíveis para o sistema são:
- `addVeiculo marca modelo ano`
- `addAviao marca modelo ano capacidadePassageiros altitudeMaxima`
- `show`
- `end`

## Shell
Aqui estão os casos de teste para o seu sistema:
```bash
#TEST_CASE iniciando com veiculo
$addVeiculo Toyota Corolla 2015
$show
Toyota Corolla 2015
$end
```

```bash
#TEST_CASE iniciando com aviao
$addAviao Boeing 737 2010 200 12000
$show
Boeing 737 2010 200 12000
$end
```

```bash
#TEST_CASE adicionando veiculo e aviao
$addVeiculo Ford Fusion 2018
$addAviao Airbus A320 2012 250 10000
$show
Ford Fusion 2018
Airbus A320 2012 250 10000
$end
```