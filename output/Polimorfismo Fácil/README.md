# Polimorfismo em Java: Sistema de Loja de Ferramentas
## Intro
Uma loja de ferramentas deseja criar um sistema para gerenciar seus produtos. Eles têm diferentes tipos de ferramentas, como martelos, serrotes e chaves de fenda. Cada ferramenta tem um nome, preço e descrição. Além disso, cada tipo de ferramenta tem uma característica única: martelos têm um peso, serrotes têm um comprimento de lâmina e chaves de fenda têm um tamanho. A loja deseja criar um sistema que possa calcular o imposto sobre cada ferramenta com base no seu tipo. O imposto é calculado da seguinte forma:
- Martelos: 10% do preço
- Serrotes: 15% do preço
- Chaves de fenda: 5% do preço

Os atributos esperados para as classes são:
- Nome
- Preço
- Descrição (opcional)
- Peso (para martelos)
- Comprimento da lâmina (para serrotes)
- Tamanho (para chaves de fenda)

Os métodos esperados são:
- `addItem`: adiciona uma ferramenta ao sistema
- `show`: exibe as informações de todas as ferramentas adicionadas
- `end`: finaliza o programa

## Shell
Abaixo estão os casos de teste para o sistema:

```bash
#TEST_CASE 1
$addItem Martelo de Bola 50.0 2.0
$show
Martelo de Bola 50.0 2.0
$end
```

```bash
#TEST_CASE 2
$addItem Serrote de Madeira 30.0 20.0
$show
Serrote de Madeira 30.0 20.0
$end
```

```bash
#TEST_CASE 3
$addItem Chave de Fenda Ajustável 20.0 10
$show
Chave de Fenda Ajustável 20.0 10
$end
```