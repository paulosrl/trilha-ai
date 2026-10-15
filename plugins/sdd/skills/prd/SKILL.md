---
name: prd
description: >
  Escreve o PRD (Estágio 1 do pipeline PRD → TDD → OpenSpec): o que o produto faz e por quê, sem tecnologia, em sdd/prd-<nome>.md. Use quando o usuário pedir um PRD ou requisitos de produto, ou quiser estruturar, documentar ou especificar um produto ou funcionalidade, mesmo sem dizer "PRD"; também no modo "como está", para um sistema que já existe sem PRD. Decisão de tecnologia é da skill tdd.
---

# Skill: Criar PRD (Estágio 1 — Produto)

## Posição no pipeline

```
Estágio 1 — PRD (esta skill)   → O QUE e POR QUÊ. Agnóstico de tecnologia.
        ↓ gate 1: usuário aprova o produto
Estágio 2 — TDD (skill tdd)    → COM O QUÊ. Stack, arquitetura, modelo físico.
        ↓ gate 2: usuário aprova a tecnologia
Estágio 3 — skill briefing     → EM QUE ORDEM. Decomposição e o briefing de cada change.
            /opsx:propose      → COMO. Uma change por vez: specs, design, tasks.
```

As regras comuns do repositório (o ciclo, as pastas, a versão dos documentos) vêm do kit Trilha AI (`CLAUDE-comum.md`), que prevalece; esta skill as cita e não as repete.

Esta skill produz exclusivamente o artefato do Estágio 1. O PRD gerado deve ser a fonte de verdade sobre o produto, legível e aprovável por quem **não** tem profundidade técnica, e estável diante de qualquer troca de tecnologia: o mesmo PRD deve servir intacto a um protótipo local ou a um sistema web multiusuário.

## Princípio de separação (regra inviolável)

**Nada de tecnologia dentro do PRD.** Isto significa:

| Proibido no PRD | Onde pertence |
|---|---|
| Linguagem de programação | TDD (Estágio 2) |
| Banco de dados, cache, filas | TDD |
| Frameworks, bibliotecas, gerenciadores de pacote | TDD |
| Docker, CI/CD, infraestrutura | TDD |
| Modelo físico de dados (tipos de coluna, PK, FK, índices) | TDD |
| Protocolos, provedores externos específicos | TDD |
| Diagrama de arquitetura de serviços | TDD |

A **única** exceção é a restrição técnica que o próprio usuário declarar espontaneamente como imposição externa ou institucional ("tem que rodar no servidor X", "a instituição exige a linguagem Y"). Nesse caso, registre como `RST-XXX` com origem e data declaradas — como fato imposto, nunca como decisão desta skill. Não pergunte sobre tecnologia; se o usuário mencionar, registre e avise que a decisão será validada no Estágio 2.

Se o usuário pedir que o PRD inclua stack ou modelo de dados, explique a separação em duas frases e ofereça acionar a skill `tdd` logo após a aprovação do PRD.

## O que um bom PRD de produto contém

| Incluir (sempre) | Excluir (sempre) |
|---|---|
| Problema e objetivos com IDs | Qualquer item da tabela de proibições acima |
| Atores e permissões | Seções de aprovação corporativa e glossário |
| Escopo da versão com IDs | Plano de implementação por semanas |
| Requisitos funcionais em EARS, com IDs | Equipe necessária |
| Regras de negócio com IDs | Design visual e UX detalhado |
| Entidades **conceituais** (atributos de negócio, sem tipos físicos) | Monitoramento pós-launch |
| Fluxos principais com exceções | Comparação com concorrentes |
| Requisitos não-funcionais **de produto** (ver §RNF) | Benefícios genéricos |
| Critérios de aceite em Gherkin | |
| Restrições confirmadas (RST) com origem | |
| Fora do escopo explícito | |
| Matriz de rastreabilidade | |

## Sistema de identificadores

Todo elemento normativo recebe ID estável, nunca renumerado:

- `PROB-XXX` problema · `OBJ-XXX` objetivo · `AT-XXX` ator · `PER-XXX` perfil
- `ESC-XXX` item de escopo · `RF-XXX` requisito funcional · `RN-XXX` regra de negócio
- `ENT-XXX` entidade conceitual · `FL-XXX` fluxo · `EX-XXX` exceção · `FA-XXX` fluxo alternativo
- `CA-RF-XXX-NN` critério de aceite · `RST-XXX` restrição confirmada
- `PRE-XXX` premissa · `RIS-XXX` risco · `FE-XXX` fora do escopo

IDs criam a matriz de rastreabilidade e são o vocabulário que o TDD e o OpenSpec referenciam depois. Numere sequencialmente dentro de cada tipo, começando em 001.

## Sintaxe EARS para requisitos funcionais

Cada RF declara seu tipo e segue o gabarito correspondente:

| Tipo | Gabarito | Uso |
|---|---|---|
| `EARS-EVT` (event-driven) | "Quando [gatilho], o sistema deve [resposta]" | Ação disparada por evento |
| `EARS-IND` (unwanted behavior) | "Se [condição indesejada], o sistema [não] deve [resposta]" | Validações e rejeições |
| `EARS-EST` (state-driven) | "Enquanto [estado], o sistema deve [comportamento]" | Comportamento contínuo |
| `EARS-OPC` (optional feature) | "Onde [feature presente], o sistema deve [comportamento]" | Variação por configuração |
| `EARS-UBI` (ubiquitous) | "O sistema deve [comportamento]" | Invariantes sem gatilho |

Regras de qualidade: um RF por comportamento (atomicidade); verbo verificável (nunca "funcionar bem", "ser amigável"); todo RF aponta ao menos um `CA`, um `ESC` e os `RN`/`ENT`/`FL` relacionados.

## Processo

### 1. Capturar contexto

Se a mensagem inicial não permitir escrever requisitos concretos, pergunte em **uma única rodada**:

- **O que é?** — nome ou descrição curta
- **Qual dor resolve?** — problema específico, com dado quantitativo se houver
- **Para quem?** — atores e o que cada um pode fazer
- **O que entra nesta versão?** — e o que explicitamente fica de fora
- **Existe alguma imposição externa?** — prazo, norma, sistema legado, exigência institucional (vira `RST`, não decisão)

**Não pergunte linguagem, banco, plataforma ou qualquer item técnico.** Se o usuário já respondeu algo na mensagem, não repita a pergunta.

### 2. Inferir o que for razoável

Faça inferências de **produto** (nunca de tecnologia) e sinalize cada uma com `⚠️ Assumido: [premissa]` ou registre como `PRE-XXX`. O usuário corrige nos gates. Lacuna que o usuário não souber responder agora vira `PRE` ou `PEN` declarada — nunca silêncio.

### 3. Escrever por blocos com aprovação (gates internos)

**NÃO gere o PRD completo de uma vez.** Apresente cada bloco no chat e aguarde aprovação explícita ("ok", "pode seguir", "próximo") antes de avançar:

1. **Bloco 1 — Fundamentos:** Seções 1 a 4 (Resumo, Problema, Objetivos e Métricas, Atores) → aguarde aprovação
2. **Bloco 2 — Escopo:** Seção 5 (Escopo da versão) e Seção 11 (Fora do escopo) → aguarde aprovação
3. **Bloco 3 — Comportamento:** Seções 6 e 7 (RFs em EARS, Regras de negócio) → aguarde aprovação
4. **Bloco 4 — Estrutura:** Seções 8 e 9 (Entidades conceituais, Fluxos) → aguarde aprovação
5. **Bloco 5 — Verificação:** Seções 10, 12, 13, 14 (RNFs, Critérios de aceite, RST/PRE/RIS, Matriz) → aprovação final

Correção pedida em qualquer bloco: corrija **apenas aquele bloco** e reapresente antes de avançar. Após a aprovação final, compile, salve o `.md` e declare o **gate 1 cumprido**, oferecendo o próximo passo: skill `tdd`.

**Camada de apresentação dos gates (obrigatória).** O aparato técnico — identificadores, siglas EARS, referências cruzadas — existe para o documento final e para as etapas seguintes do pipeline, **não para a conversa de aprovação**. Nos gates, apresente cada bloco em linguagem simples:

1. Frases curtas, sem siglas e sem códigos; um requisito aparece como "o que o sistema faz em qual situação", nunca como "RF-007 (EARS-UBI)". No máximo, um código discreto entre parênteses ao fim da frase, quando o usuário precisar citá-lo de volta.
2. Toda decisão trazida ao usuário segue o padrão: diagnóstico em uma frase → no máximo 3 opções com a consequência de cada → **uma recomendação justificada**. O usuário aprova ou veta; nunca escolhe no vácuo.
3. Inferências e lacunas são apresentadas como perguntas de confirmação em português comum ("assumi que X; confirma?"), não como listas de premissas codificadas.
4. O conteúdo integral com IDs, tipos EARS e rastreabilidade entra **apenas** no arquivo `.md` compilado ao final. O usuário aprova significado; o documento carrega a estrutura.

**Verificação por bloco — teste da promessa.** Antes de apresentar cada bloco (e de novo no teste de prontidão final), confira: toda consequência prometida na dor (Seção 2) tem item de escopo que a entrega ou exclusão declarada com motivo (Seção 11)? Promessa órfã é inconsistência — apresente-a ao usuário no gate como decisão, com proposta de resolução, nunca resolva em silêncio.

Extensão alvo: **120–250 linhas** de Markdown.

---

## Modo "como está": sistema que já existe sem PRD

Use quando o sistema já está construído e não tem PRD: o comum manda escrever o que falta antes da próxima change que toque requisito. O PRD descreve o que o sistema **já faz**, lido dos specs em `openspec/specs/`, do README e do código; não cria requisito novo. Requisito novo entra numa versão seguinte do PRD, aprovada como qualquer outra.

O que muda em relação ao modo normal:

1. **Contexto:** leia em vez de perguntar. Pergunte só o que não estiver escrito em lugar nenhum (em geral, a dor e para quem), numa rodada única.
2. **Cabeçalho:** além de Status, Versão e Data, a linha `**Modo:** "como está"`, dizendo de onde o PRD foi lido e que a estrutura é a reduzida deste modo.
3. **Estrutura reduzida**, nesta ordem: 1. O que é e por quê (o que é, a dor, para quem); 2. Escopo (o que está dentro e o que está fora, com o motivo); 3. Requisitos funcionais, numa tabela `Código | Requisito | Origem`, com o spec de origem pelo nome; 4. Regras (`RN-XXX`); 5. Requisitos não funcionais de produto; 6. Critérios de aceite; 7. Histórico de versões. Métricas, entidades, fluxos e matriz só entram se o sistema os justificar; a coluna "Origem" faz as vezes da matriz.
4. **Requisitos:** um por comportamento, verificável, sem tecnologia; o tipo EARS é opcional. Os specs anteriores ao método não citam o RF: a ligação é a coluna "Origem", declarada no PRD; todo requisito novo ou modificado depois cita o RF.
5. **Critérios de aceite:** os cenários dos specs, apontados na seção 6, sem copiá-los. Requisito sem spec que o descreva (lido do README ou do código) ganha critério em Gherkin na própria seção 6.
6. **Aprovação:** dois blocos, com a mesma camada de apresentação: bloco A, seções 1 e 2; bloco B, seções 3 a 6. Antes de cada bloco, o **teste da fidelidade**: toda afirmação tem origem num spec, no README ou no código, e nada descreve o que o sistema não faz. Comportamento que parece defeito não se corrige no PRD: apresente-o ao usuário como decisão (descrever como está ou abrir uma correção).
7. **Prontidão:** valem os testes da troca de stack, do leigo e da rastreabilidade (todo RF com origem; todo spec com ao menos um RF). Extensão alvo: **60–150 linhas**.

---

## Estrutura obrigatória do PRD (modo normal)

```markdown
# PRD: [Nome do Produto / Feature]

**Status:** Rascunho | Aprovado
**Versão:** 0.1
**Data:** [data atual]
**Próxima etapa:** Decisão técnica (TDD) — não iniciada

---

## 1. Resumo Executivo

[1-2 parágrafos: o que é, para quem, o que esta versão cobre. Sem tecnologia.]

## 2. Problema

### PROB-001
- **Descrição:** [situação atual e dor específica]
- **Atores afetados:** AT-XXX
- **Evidências:** [dado quantitativo, ou "⛔ Não informado"]

## 3. Objetivos e Métricas

### OBJ-001
- **Relacionado a:** PROB-001
- **Descrição:** [resultado desejado, verificável]

| Métrica | Baseline | Meta | Fonte |
|---------|----------|------|-------|
| [ou "NÃO APLICÁVEL — decisão do usuário"] | | | |

## 4. Atores e Permissões

### AT-001
[Quem é, o que caracteriza]

### PER-001
[O que esse ator pode fazer]

## 5. Escopo da Versão

| ID | Descrição | Relacionado a |
|----|-----------|---------------|
| ESC-001 | ... | OBJ-XXX, RF-XXX |

## 6. Requisitos Funcionais

### RF-001 — [Nome curto]
- **Tipo EARS:** EARS-EVT | EARS-IND | EARS-EST | EARS-OPC | EARS-UBI
- **Atores:** AT-XXX · **Escopo:** ESC-XXX
- **Descrição normativa:** [gabarito EARS]
- **Regras:** RN-XXX · **Entidades:** ENT-XXX · **Fluxos:** FL-XXX
- **Critérios de aceite:** CA-RF-001-01

## 7. Regras de Negócio

### RN-001 — [Nome curto]
- **Tipo:** validação | invariante | exceção | permissiva
- **Regra normativa:** [enunciado verificável]
- **RFs relacionados:** RF-XXX

## 8. Entidades Conceituais

### ENT-001 — [Nome]
- **Significado:** [o que representa no negócio]
- **Atributos de negócio:** [nome (obrigatório?), ...] — SEM tipos físicos
- **Relacionamentos:** [cardinalidade conceitual, ou "não aplicável"]
- **Ciclo de vida:** [criado → ... → removido]

## 9. Fluxos Principais

### FL-001 — [Nome]
- **Requisitos:** RF-XXX · **Regras:** RN-XXX
- **Pré-condição:** ... · **Gatilho:** ...
- **Sucesso:** ...
- **EX-001:** [condição de exceção] → [tratamento]

## 10. Requisitos Não-Funcionais de Produto

[APENAS os perceptíveis pelo usuário ou impostos por norma, em linguagem de
consequência: "resposta imperceptível para volume de até N registros",
"dados não saem do dispositivo", "conforme LGPD". Valores de latência/throughput
de engenharia, quando necessários, serão derivados no TDD.]

| Categoria | Estado | Conteúdo |
|-----------|--------|----------|
| Desempenho percebido | ✅/⚠️/N.A. | |
| Privacidade | | |
| Compliance | | |
| Acessibilidade | | |

## 11. Fora do Escopo

- **FE-001** — [item específico] — Motivo: ... — Destino: V2 | a confirmar

## 12. Critérios de Aceite

### CA-RF-001-01 — [Nome]
DADO [contexto]
QUANDO [ação]
ENTAO [resultado observável]

## 13. Restrições, Premissas e Riscos

### RST-001 (se houver)
- **Restrição:** [imposição externa declarada pelo usuário]
- **Origem:** [quem impôs] · **Data:** ... · **Validade:** ...
- **Nota:** será validada na etapa de decisão técnica (TDD)

### PRE-001 — ⚠️ [premissa assumida, reversível?, impacto]
### RIS-001 — [risco, impacto, mitigação]

## 14. Matriz de Rastreabilidade

| Origem | Destino |
|--------|---------|
| PROB-001 | OBJ-001 |
| OBJ-001 | ESC-001... |
| ESC-001 | RF-001... |
| RF-001 | CA-RF-001-01 |
| RN-001 | RF-XXX |

## 15. Histórico de versões

| Versão | Data | O que mudou de sentido |
|--------|------|------------------------|
| 0.1 | [data] | Primeira versão |
```

---

## Qualidade — teste de prontidão antes do gate 1

Antes de declarar o PRD pronto, verifique:

1. **Teste da troca de stack:** se a tecnologia mudar completamente, alguma linha do PRD precisa mudar? Se sim (exceto RSTs declaradas), há vazamento técnico — corrija.
2. **Teste do leigo:** o dono do produto, sem formação técnica, entende e consegue aprovar cada seção?
3. **Teste da IA:** todo comportamento tem RF atômico, verificável, com CA? O que não está escrito será inventado.
4. **Teste da rastreabilidade:** todo RF aponta para ESC e CA; toda RN aponta para RF; nenhum ID órfão na matriz.
5. **Fora do escopo específico:** "features de V2" não basta — nomeie cada exclusão.
6. **Teste da promessa:** toda consequência mencionada na dor tem item de escopo que a entrega ou exclusão declarada com motivo? Promessa órfã é inconsistência a resolver com o usuário, nunca em silêncio.

## Saída

Salve como `sdd/prd-<nome-kebab-case>.md` na raiz do repositório.

Após salvar:
1. Entregue o arquivo ao usuário
2. Resumo de 2 linhas: o que foi gerado, o que ficou como `PRE`/`⚠️`
3. Declare: "Gate 1 cumprido. Próxima etapa: decisão técnica — acione a skill `tdd` com este PRD."

**Não** exiba o PRD completo no chat — o arquivo é a entrega.
