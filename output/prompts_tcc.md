# Lote de Questões para Avaliação do TCC

Este documento registra os prompts utilizados na geração do lote de 6 questões de Programação Orientada a Objetos (POO) em Kotlin para o TCC, organizadas pelas três categorias de complexidade (número de tópicos e de classes).

---

## Categoria 1: 1 tópico, 1 a 2 classes

### Questão-03
- **Prompt:**
  ```text
  1 classe, com encapsulamento e invariantes, no contexto de uma garrafa térmica inteligente que controla volume de líquido, capacidade máxima e temperatura, com métodos para abastecer e servir sem permitir transbordamento nem valores negativos
  ```
- **Tópico aplicado:** Encapsulamento e Invariantes (`encapsulamento_invariantes`)
- **Quantidade de classes:** 1 classe (`GarrafaTermica`)
- **Domínio:** Garrafa térmica inteligente
- **Status:** Gerada e validada com sucesso

### Questão-04
- **Prompt:**
  ```text
  2 classes, com agregação e delegação, no contexto de um sistema de patinetes elétricos onde um patinete agrega opcionalmente um usuário para realizar corridas por tempo determinado
  ```
- **Tópico aplicado:** Agregação e Delegação (`agregacao_delegacao`)
- **Quantidade de classes:** 2 classes (`Usuario`, `Patinete`)
- **Domínio:** Sistema de patinetes elétricos urbanos
- **Status:** Gerada e validada com sucesso

---

## Categoria 2: 2 tópicos, 2 a 3 classes

### Questão-05
- **Prompt:**
  ```text
  2 classes, com encapsulamento e coleções lineares, no contexto de um carrinho de compras de uma padaria artesanal que armazena uma lista de itens com controle de quantidade máxima e cálculo do valor total
  ```
- **Tópicos aplicados:** Encapsulamento e Invariantes (`encapsulamento_invariantes`), Coleções lineares (`colecoes_lineares`)
- **Quantidade de classes:** 2 classes (`Item`, `Carrinho`)
- **Domínio:** Carrinho de compras de padaria artesanal
- **Status:** Gerada e validada com sucesso

### Questão-06
- **Prompt:**
  ```text
  3 classes, com posições fixas e ausência e encapsulamento, no contexto de um estacionamento rotativo com capacidade fixa de vagas numeradas onde cada vaga pode estar vazia ou ocupada por um veículo
  ```
- **Tópicos aplicados:** Encapsulamento e Invariantes (`encapsulamento_invariantes`), Posições fixas e ausência (`posicoes_fixas_ausencia`)
- **Quantidade de classes:** 3 classes (`Veiculo`, `Vaga`, `Estacionamento`)
- **Domínio:** Estacionamento rotativo com vagas fixas
- **Status:** Gerada e validada com sucesso

---

## Categoria 3: 3+ tópicos, 3 a 4 classes (Questões Existentes)

### Questão-01
- **Prompt:**
  ```text
  4 classes, com herança, polimorfismo, encapsulamento e mapas, no contexto de uma oficina de bicicletas que atende bicicletas urbanas e elétricas, cada tipo com uma regra diferente de cobrança de revisão
  ```
- **Tópicos aplicados:** Herança, Polimorfismo (`polimorfismo`), Encapsulamento e Invariantes (`encapsulamento_invariantes`), Mapas (`mapas`)
- **Quantidade de classes:** 4 classes (`Bicicleta`, `BicicletaUrbana`, `BicicletaEletrica`, `Oficina`)
- **Domínio:** Oficina de bicicletas mecânicas e elétricas
- **Status:** Gerada e validada com sucesso

### Questão-02
- **Prompt:**
  ```text
  3 classes, com encapsulamento, mapas e exceções, no contexto de uma biblioteca de bairro que empresta livros para sócios, com limite de empréstimos por sócio e livros que podem estar indisponíveis
  ```
- **Tópicos aplicados:** Encapsulamento e Invariantes (`encapsulamento_invariantes`), Mapas (`mapas`), Exceções (`excecoes`)
- **Quantidade de classes:** 3 classes (`Livro`, `Socio`, `Biblioteca`)
- **Domínio:** Biblioteca comunitária de empréstimo de livros
- **Status:** Gerada e validada com sucesso
