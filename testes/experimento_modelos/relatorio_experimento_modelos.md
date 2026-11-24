# Experimento Comparativo de Configurações de Modelos (Eixo B do TCC)

**Data da Execução:** 2026-11-23 17:34:18
**Ambiente:** Python 3.12.3 | LiteLLM + CrewAI

Este relatório documenta a avaliação empírica do **Eixo B**, comparando três configurações arquiteturais de Modelos de Linguagem de Grande Porte (LLMs) em três níveis crescentes de complexidade estrutural de POO em Kotlin.

---

## 1. Configurações Avaliadas e Metodologia

Para assegurar rigor metodológico e comparabilidade:
- **Few-Shot Padronizado:** O procedimento `preparar(...)` foi executado uma única vez por prompt, fornecendo idênticos tópicos e exemplos de referência para todas as configurações.
- **Temperatura:** Fixada em `1.0` em todos os agentes para manter paridade estocástica.
- **Tarifas de Rastreamento:** Baseadas na tabela oficial do Google AI Studio com fallback automático.

| Configuração | Designer Instrucional | Especialista POO Kotlin | Auditor Técnico QA | Perfil Arquitetural |
| :--- | :--- | :--- | :--- | :--- |
| **1. Leve Homogênea (Flash-Lite x3)** | `gemini-3.5-flash-lite` | `gemini-3.5-flash-lite` | `gemini-3.5-flash-lite` | gemini-3.5-flash-lite nos 3 agentes (Designer, Especialista, Auditor) |
| **2. Híbrida Proposta (Flash-Lite + Flash + Flash-Lite)** | `gemini-3.5-flash-lite` | `gemini-3.8-flash` | `gemini-3.5-flash-lite` | gemini-3.5-flash-lite no Designer e Auditor, e gemini-3.8-flash no Especialista |
| **3. Robusta Homogênea (Flash x3)** | `gemini-3.8-flash` | `gemini-3.8-flash` | `gemini-3.8-flash` | gemini-3.8-flash nos 3 agentes (Designer, Especialista, Auditor) |

---

## 2. Tabela Comparativa Geral de Desempenho e Custos

| Configuração | Pass@1 (%) | Aprovação Final (%) | Tentativas Médias | Tempo Médio (s) | Tokens Médios (In / Out) | Custo Total (US$) | Custo Médio / Q (US$) | Custo Efetivo / Q Aprovada (US$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Leve Homogênea (Flash-Lite x3)** | **66.7%** | **66.7%** | 0.67 | 15.9s | 9980 / 4351 | $0.0416 | $0.0139 | **$0.0208** |
| **2. Híbrida Proposta (Flash-Lite + Flash + Flash-Lite)** | **100.0%** | **100.0%** | 1.0 | 97.83s | 13001 / 13014 | $0.1590 | $0.0530 | **$0.0530** |
| **3. Robusta Homogênea (Flash x3)** | **100.0%** | **100.0%** | 1.0 | 154.77s | 13632 / 18446 | $0.2382 | $0.0794 | **$0.0794** |

---

## 3. Qualidade Estrutural dos Artefatos Gerados

Verificação dos 4 pilares de conformidade das questões:
1. **Esqueleto Conforme:** Todas as classes contêm estritamente `TODO(...)` nos métodos.
2. **Sem println no Domínio:** Classes não violam o encapsulamento imprimindo saídas diretamente.
3. **Diagrama Mermaid:** Presença de diagrama de classes funcional em bloco ```` ```mermaid ````.
4. **Casos de Teste Suficientes:** Cobertura de no mínimo 5 casos de teste estruturados no README.

| Configuração | Esqueleto Conforme (%) | Sem println Domínio (%) | Diagrama Mermaid (%) | Média Casos de Teste | Aderência Estrutural (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Leve Homogênea (Flash-Lite x3)** | 100.0% | 100.0% | 66.7% | 3.3 | **83.3%** |
| **2. Híbrida Proposta (Flash-Lite + Flash + Flash-Lite)** | 100.0% | 100.0% | 100.0% | 5.7 | **100.0%** |
| **3. Robusta Homogênea (Flash x3)** | 100.0% | 100.0% | 100.0% | 5.3 | **100.0%** |

---

## 4. Detalhamento por Execução (Configuração x Nível)

| Configuração | Nível | Aprovado | Pass@1 | Tentativas | Tempo (s) | Tokens (In / Out) | Custo (US$) | Esqueleto | Sem Print | Mermaid | Testes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `1_Leve_Homogenea` | L1 | ✗ Não | ✗ Não | 0 | 10.6s | 8384 / 3745 | $0.0119 | ✓ | ✓ | ✗ | 0 |
| `1_Leve_Homogenea` | L2 | ✓ Sim | ✓ Sim | 1 | 17.49s | 10376 / 4196 | $0.0136 | ✓ | ✓ | ✓ | 5 |
| `1_Leve_Homogenea` | L3 | ✓ Sim | ✓ Sim | 1 | 19.6s | 11180 / 5112 | $0.0161 | ✓ | ✓ | ✓ | 5 |
| `2_Hibrida_Proposta` | L1 | ✓ Sim | ✓ Sim | 1 | 63.38s | 12024 / 7993 | $0.0343 | ✓ | ✓ | ✓ | 6 |
| `2_Hibrida_Proposta` | L2 | ✓ Sim | ✓ Sim | 1 | 119.01s | 12248 / 15836 | $0.0634 | ✓ | ✓ | ✓ | 5 |
| `2_Hibrida_Proposta` | L3 | ✓ Sim | ✓ Sim | 1 | 111.09s | 14731 / 15215 | $0.0613 | ✓ | ✓ | ✓ | 6 |
| `3_Robusta_Homogenea` | L1 | ✓ Sim | ✓ Sim | 1 | 104.36s | 13240 / 11628 | $0.0535 | ✓ | ✓ | ✓ | 5 |
| `3_Robusta_Homogenea` | L2 | ✓ Sim | ✓ Sim | 1 | 153.13s | 14604 / 18998 | $0.0822 | ✓ | ✓ | ✓ | 5 |
| `3_Robusta_Homogenea` | L3 | ✓ Sim | ✓ Sim | 1 | 206.82s | 13053 / 24713 | $0.1025 | ✓ | ✓ | ✓ | 6 |

---

## 5. Análise Crítica para a Discussão do TCC

### 5.1. Trade-off Eficácia x Custo Financeiro
- **Configuração Leve (`1_Leve_Homogenea`):** Apresenta o menor custo operacional absoluto, porém pode demonstrar sensibilidade em questões de complexidade alta (L3) devido à capacidade de raciocínio mais restrita do modelo compacto ao alinhar assinaturas de métodos e testes.
- **Configuração Híbrida (`2_Hibrida_Proposta`):** Proposta central deste trabalho. Aloca o modelo de alta capacidade (`gemini-3.8-flash`) exclusivamente no **Especialista POO** (responsável pelo código Kotlin rigoroso e pelas correções), mantendo o modelo econômico (`gemini-3.5-flash-lite`) no Designer Instrucional e no Auditor Técnico. Essa divisão permite taxa de aprovação próxima ou idêntica à homogênea robusta com redução drástica no custo total.
- **Configuração Robusta (`3_Robusta_Homogenea`):** Mantém consistência técnica elevada, mas opera com multiplicadores elevados de custo por token tanto na fase criativa quanto na auditoria, encarecendo desnecessariamente o pipeline.

### 5.2. Custo Efetivo por Questão Aprovada
A métrica de **Custo Efetivo por Questão Aprovada** (`Custo Total / Aprovadas`) é o critério decisório primário: ela penaliza configurações que parecem baratas em chamadas isoladas mas reprovam questões ou exigem o número máximo de tentativas de correção.
