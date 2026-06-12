# Implementação de Polimorfismo em Sistema de Petshop em Java
## Intro
Em uma petshop movimentada, a gerente, Maria, está tendo dificuldades em gerenciar os diferentes serviços oferecidos, como banhos, tosas e consultas veterinárias. Ela precisa de um sistema que permita adicionar, remover e realizar esses serviços de forma eficiente. Para resolver esse problema, decidimos criar um sistema de petshop utilizando conceitos de orientação a objetos, como o polimorfismo, para tornar o código mais flexível e escalável.

As classes do sistema terão os seguintes atributos e métodos:
- **Classe Servico** (classe pai):
  - Atributos: `nome`, `preco`
  - Métodos: `getNome()`, `getPreco()`, `setPreco(preco)`, `realizarServico()` (método abstrato que deve ser implementado pelas classes filhas)

- **Classe Banho** (classe filha de Servico):
  - Atributos adicionais: `tipoDeBanho` (pode ser "simples", "com shampoo", etc.)
  - Métodos: `getTipoDeBanho()`, `setTipoDeBanho(tipoDeBanho)`, implementação do método `realizarServico()`

- **Classe Tosa** (classe filha de Servico):
  - Atributos adicionais: `tipoDeTosa` (pode ser "padrão", "personalizada", etc.)
  - Métodos: `getTipoDeTosa()`, `setTipoDeTosa(tipoDeTosa)`, implementação do método `realizarServico()`

- **Classe Consulta** (classe filha de Servico):
  - Atributos adicionais: `especialidade` (pode ser "cardiologia", "dermatologia", etc.)
  - Métodos: `getEspecialidade()`, `setEspecialidade(especialidade)`, implementação do método `realizarServico()`

## Shell
Aqui estão os casos de teste para o seu sistema:

### Caso 1: Adicionar e realizar serviços de banho
```bash
#TEST_CASE banho
$addServico banho simples 20.0
$realizarServicos
Realizando banho simples para o pet.
$end
```

### Caso 2: Adicionar e realizar serviços de tosa
```bash
#TEST_CASE tosa
$addServico tosa padrao 30.0
$realizarServicos
Realizando tosa padrão para o pet.
$end
```

### Caso 3: Adicionar e realizar serviços de consulta
```bash
#TEST_CASE consulta
$addServico consulta cardiologia 50.0
$realizarServicos
Realizando consulta de cardiologia para o pet.
$end
```