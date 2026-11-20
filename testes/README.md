# Suíte de Testes de Injeção de Falhas e Ciclo de Autocorreção

Este diretório contém a suíte de testes automatizados para validar e comprovar o funcionamento do **ciclo de auditoria técnica e autocorreção** do sistema **Forja**.

## Objetivo

Comprovar empiricamente que o sistema é capaz de:
1. **Detectar falhas reais** em diferentes camadas da questão (testes no README, sintaxe do código Kotlin e regras pedagógicas do esqueleto de código).
2. **Gerar diagnósticos técnicos precisos** (erros reais de compilador `kotlinc`, divergências de saída esperada vs. obtida, violações de integridade).
3. **Disparar o ciclo de autocorreção** com os agentes CrewAI (`Especialista em POO Kotlin` e `Auditor Técnico de Qualidade`).
4. **Revalidar os artefatos corrigidos**, garantindo que a versão final alcance 100% de conformidade técnica e pedagógica.

---

## Cenários Testados

| Cenário | Injeção de Falha Controlada | Como o Sistema Detecta | Como o Sistema Corrige |
| :--- | :--- | :--- | :--- |
| **1. Divergência nos Casos de Teste (`README.md`)** | Altera propositalmente uma linha de saída esperada no primeiro bloco bash do `README.md`. | A execução real gera divergência de saída nos testes (`Etapa com falha: testes`). | O Especialista POO corrige o `README.md` e o ciclo é revalidado com o Auditor Técnico (`criar_tarefa_gabarito`) + `compilar_e_executar`. |
| **2. Erro de Sintaxe/Assinatura no Esqueleto (`shell.kt`)** | Injeta erro de sintaxe ou quebra uma chamada de método na `main` do `shell.kt`. | Auditor Técnico tenta gerar gabarito sobre o esqueleto quebrado e o compilador real `kotlinc` falha na compilação (`Etapa com falha: compilacao`). | O Especialista POO recebe o relatório do `kotlinc`, corrige o `shell.kt`, e uma nova tentativa completa com o Auditor valida compilação e testes. |
| **3. Falha Simulada no Gabarito (`main.kt`) do Auditor** | Simula a Tentativa 1 em que o Auditor Técnico entrega um `main.kt` com erro de sintaxe ou lógica injetado. | `compilar_e_executar` captura a falha e o relatório formatado (`formatar_relatorio`) é enviado ao Especialista POO. | Na Tentativa 2 do ciclo real, o Auditor Técnico gera um novo `main.kt` do zero a partir do `README.md` e `shell.kt` atualizados, comprovando a recuperação. |
| **4. Violação de Esqueleto (Método Concreto em `shell.kt`)** | Substitui a primeira marcação `TODO(...)` de um método de domínio por implementação concreta. | A validação estática granular `verificar_conformidade_esqueleto` detecta violação no método específico. | O Especialista POO restaura `TODO(...)`, o esqueleto corrigido é revalidado e o ciclo é fechado com o Auditor Técnico e testes 100% aprovados. |

---

## Como Executar

A partir da raiz do repositório:

### 1. Executar todos os cenários em sequência:
```bash
python3 testes/teste_ciclo_correcao.py --cenario todos
```
ou com `uv`:
```bash
uv run python testes/teste_ciclo_correcao.py --cenario todos
```

### 2. Executar um cenário individual:
- **Cenário 1 (Testes do README.md):**
  ```bash
  python3 testes/teste_ciclo_correcao.py --cenario 1
  ```
- **Cenário 2 (Esqueleto quebrado shell.kt):**
  ```bash
  python3 testes/teste_ciclo_correcao.py --cenario 2
  ```
- **Cenário 3 (Gabarito defeituoso main.kt do Auditor):**
  ```bash
  python3 testes/teste_ciclo_correcao.py --cenario 3
  ```
- **Cenário 4 (Violação de esqueleto shell.kt):**
  ```bash
  python3 testes/teste_ciclo_correcao.py --cenario 4
  ```

### 3. Usar qualquer questão de referência:
```bash
python3 testes/teste_ciclo_correcao.py --questao output/Questão-01 --cenario todos
```

---

## Arquivos

- `teste_ciclo_correcao.py`: Script principal de injeção controlada de falhas e orquestração do ciclo de autocorreção.
- `relatorio_validacao_ciclo.md`: Relatório gerado automaticamente com os resultados da última execução dos testes.
