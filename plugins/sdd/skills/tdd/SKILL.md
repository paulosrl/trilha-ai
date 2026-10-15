---
name: tdd
description: >
  Conduz a decisão técnica de um produto (Estágio 2 do pipeline PRD → TDD → OpenSpec), produzindo um Technical Design Document com ADRs leves, arquitetura, modelo físico de dados e ferramental — a partir de um PRD aprovado e agnóstico de tecnologia. Use esta skill SEMPRE que o usuário: tiver um PRD aprovado e perguntar "e agora?", pedir para "decidir a stack", "escolher tecnologia", "definir arquitetura", "escolher banco de dados", "fazer o design técnico", "criar ADRs", ou mencionar TDD/Technical Design Document. Também acione quando, durante a criação de um PRD, o usuário pedir decisões de tecnologia — essa conversa pertence aqui, não ao PRD. A skill foi desenhada para funcionar com usuários SEM profundidade técnica: entrevista por consequências (nunca por jargão) e recomendação única justificada por decisão. Também registra, no modo "como está", as decisões de um sistema que já existe sem TDD, lidas do código, dos specs e dos documentos. Não use para escrever requisitos de produto (skill prd) nem para gerar artefatos OpenSpec (etapa seguinte).
---

# Skill: Decisão Técnica — TDD (Estágio 2)

## Posição no pipeline

```
Estágio 1 — PRD (skill prd)    → O QUE e POR QUÊ. Já aprovado (gate 1).
        ↓
Estágio 2 — TDD (esta skill)   → COM O QUÊ. Stack, arquitetura, modelo físico.
        ↓ gate 2: usuário aprova a tecnologia
Estágio 3 — skill briefing     → EM QUE ORDEM. Decomposição e o briefing de cada change.
        ↓
            /opsx:propose        → COMO. Uma change por vez, a partir do briefing.
```

**Pré-condição:** um PRD aprovado (gate 1). Se não existir, ofereça a skill `prd` primeiro. Se o usuário insistir em decidir tecnologia sem PRD, aceite, mas registre no TDD: `⚠️ TDD emitido sem PRD aprovado — decisões sujeitas a revisão quando os requisitos forem formalizados`.

**Pós-condição (gate 2):** TDD aprovado pelo usuário. Só então o pipeline segue para a skill `briefing`, que decompõe o escopo em changes e escreve o briefing de cada uma para o `/opsx:propose`; o `design.md` de cada change, quando o OpenSpec o cria, referencia os ADRs deste documento em vez de redecidir tecnologia, e mudança de decisão técnica é versão nova do TDD, aprovada antes do código. Essas regras ficam aqui e não no documento: o kit Trilha AI as traz no `CLAUDE-comum.md` e no `openspec/config.yaml`.

## Princípios

1. **Toda decisão técnica é um ADR leve**: contexto → opções → decisão → consequências. Nada de escolha silenciosa.
2. **Entrevista por consequências, nunca por tecnologia.** O usuário leigo não escolhe entre PostgreSQL e SQLite; ele responde quantas pessoas usam, onde os dados podem morar, o que acontece se o computador quebrar. A skill traduz.
3. **Recomendação única justificada.** Para cada decisão, apresente no máximo 3 opções em uma linha cada e **uma recomendação** com razão em linguagem de consequência. O usuário aprova ou veta; nunca escolhe no vácuo.
4. **Defaults institucionais declarados, nunca impostos.** Os padrões da casa são ponto de partida; a entrevista confirma ou desvia, e o desvio vira ADR com justificativa.
5. **Reversibilidade classificada.** Cada ADR é marcado `🚪 porta de um sentido` (caro de reverter: linguagem, banco, arquitetura de distribuição) ou `🔁 porta de dois sentidos` (barato: biblioteca de UI, formato de exportação). O usuário sabe onde gastar atenção.
6. **O PRD é soberano.** O TDD não altera requisito, regra ou critério de aceite. Se uma decisão técnica revelar lacuna ou conflito no PRD, registre como `PEN-TDD-XXX` e devolva ao dono do PRD — não resolva por conta.

## Processo

### 0. Detectar o modo

Pergunte (ou infira da mensagem): o usuário quer declarar a stack diretamente?

- **Modo expert:** o usuário declara as escolhas. A skill: valida coerência com o PRD (RSTs, RNFs, entidades), aponta conflitos, registra cada escolha como ADR com a justificativa do usuário, e preenche o que ele não declarou via entrevista reduzida. Não questione escolha coerente; questione apenas o que colidir com o PRD ou com restrição declarada.
- **Modo assistido (padrão):** entrevista completa abaixo.
- **Modo "como está":** o sistema já existe e não tem TDD; as decisões são lidas, não entrevistadas. Siga a seção "Modo 'como está'", adiante.

### 1. Ler o PRD e extrair o que já decide por si

Antes de qualquer pergunta, extraia do PRD:

- `RST-XXX` — restrições impostas (podem pré-decidir ADRs inteiros; registre como "decidido por RST-XXX")
- `ENT-XXX` e relacionamentos — insumo do modelo físico
- RNFs de produto — privacidade, compliance, desempenho percebido
- `AT/PER` — quantos tipos de usuário, se há login implícito
- Escopo e fora do escopo — o que a arquitetura NÃO precisa suportar

**Não pergunte o que o PRD já responde.**

### 2. Entrevista por consequências (modo assistido)

Uma única rodada de perguntas, só as que o PRD não respondeu. Banco de perguntas por dimensão — selecione as aplicáveis, em linguagem leiga:

| Dimensão | Perguntas (exemplos) | Decide |
|---|---|---|
| Concorrência | "Quantas pessoas usam ao mesmo tempo? Uma, algumas, muitas?" | Local vs. cliente-servidor; banco embarcado vs. servidor |
| Localização dos dados | "Os dados podem morar só neste computador, ou precisam estar acessíveis de outros lugares?" | Arquivo local vs. banco servido vs. nuvem |
| Acesso | "Alguém vai usar pelo celular? Pelo navegador? Só neste computador?" | Interface: CLI, desktop, web |
| Conectividade | "Precisa funcionar sem internet?" | Offline-first, sincronização |
| Perda de dados | "Se o computador quebrar hoje, perder os dados é aceitável, ruim ou catastrófico?" | Backup, replicação, durabilidade |
| Sigilo | "Há dado de terceiros, dado sensível, ou exigência legal sobre esses dados?" | Criptografia, LGPD, residência de dados |
| Operação | "Quem mantém isso funcionando depois de pronto? Você, um time, ninguém?" | Complexidade operacional tolerável |
| Custo | "Existe orçamento para servidor/serviços pagos, ou precisa ser custo zero?" | Self-hosted vs. gerenciado |
| Crescimento | "Daqui a um ano, isso atende 10x mais gente ou continua do mesmo tamanho?" | Margem de escalabilidade |
| Integração | "Isso conversa com algum sistema que já existe?" | Protocolos, formatos |

Aceite "não sei" como resposta válida: converta no default mais simples que satisfaça o PRD e registre `⚠️ Assumido`.

### 3. Derivar decisões como ADRs

Cobertura mínima de decisões (adapte ao produto; omita o que não se aplica, declarando por quê):

1. **ADR-001 Topologia** — local / cliente-servidor / serverless
2. **ADR-002 Linguagem e runtime** — com versão mínima
3. **ADR-003 Persistência** — banco/arquivo, com justificativa
4. **ADR-004 Interface** — CLI / desktop / web / API
5. **ADR-005 Autenticação e autorização** — ou "não aplicável por PER-XXX"
6. **ADR-006 Ferramental** — pacotes, lint, testes, CI (bloco institucional da linguagem)
7. **ADR-007 Implantação** — como roda em produção (ou "máquina do usuário")
8. **ADR-00N** — integrações, filas, cache, IA/RAG, conforme o PRD exigir

Formato de apresentação de cada decisão no chat:

```
### ADR-003 — Persistência  🚪 porta de um sentido

**Contexto:** você disse que os dados moram só neste computador (resposta Q2)
e que perder os dados seria ruim mas não catastrófico (Q5). ENT-001 tem um
único tipo de registro, sem relacionamentos (PRD §8).

**Opções:**
- A. Arquivo JSON local — simples, legível, zero instalação
- B. SQLite — arquivo único com consultas estruturadas
- C. PostgreSQL — servidor completo

**Recomendação: A**, porque o volume é pequeno, há um só usuário e a
exportação (RF-009) já cobre o backup. B só valeria se as consultas
crescessem; C exigiria operar um servidor que ninguém vai manter (Q7).

**Consequências:** sem consultas complexas; migração futura para B é simples.

Aprova, veta ou pergunta?
```

### 4. Defaults institucionais

Ponto de partida quando a entrevista levar a essas regiões de decisão (confirme, nunca imponha; desvio vira ADR justificado):

**Banco de dados (quando a topologia pedir servidor):** PostgreSQL com extensão **pgvector** habilitada. Desvio (NoSQL, embarcado) exige razão registrada no ADR.

**Projetos Python:**
- Python ≥ 3.12.3 (`python = ">=3.12.3"` no `pyproject.toml`)
- Pacotes exclusivamente via `uv` (`uv add`, `uv venv`, `uv run`, `uv sync`); `pip`/`poetry`/`pipenv` proibidos; `pyproject.toml` como único manifesto; `uv.lock` versionado como fonte de verdade da resolução
- Dependências com faixa de compatibilidade (`>=2.5,<3.0` ou `~=2.5`), nunca travadas (`==`) nem livres
- Lint/formatação `ruff`; testes `pytest`; tipos `mypy` ou `pyright`; CI mínima com lint + testes por push/PR

**Projetos Node.js/TypeScript** (mutuamente exclusivo com o bloco Python):
- Node na Active LTS vigente (confirme antes de travar; declare em `"engines"`); nunca versão em End of Life
- `pnpm` como gerenciador padrão; `npm`/`yarn` só com justificativa em ADR
- Dependências em caret range (`^`); lockfile versionado
- Lint/formatação `Biome`; testes `Vitest`; `strict: true` no `tsconfig.json`; CI mínima

**Docker (quando houver app + serviços):** `docker-compose.yml` em sintaxe v2 (sem chave `version:`), variáveis via `.env`, `Dockerfile` instalando com `uv` ou `pnpm` conforme a linguagem. Imagens de infraestrutura fixadas em major + variante (`postgres:16-alpine`, `node:26-alpine`) — nunca `latest`, nunca patch hiper-específico.

**Quando a topologia for programa local simples** (ADR-001 = local, usuário único): Docker e CI podem ser dispensados por ADR explícito ("complexidade não justificada pelo produto") — simplicidade também é decisão registrada.

### 5. Modelo físico de dados

Derive das `ENT-XXX` do PRD, segundo o ADR de persistência:

- Relacional: tabela por entidade com campo, tipo, restrição, PK/FK/UNIQUE/índices; normalização justificada
- Documento/arquivo: estrutura do documento com exemplo
- Toda regra de negócio que vira constraint física referencia sua `RN-XXX`

### 6. Gates de aprovação

Apresente em blocos e aguarde aprovação explícita:

1. **Bloco 1:** ADRs de porta de um sentido (topologia, linguagem, persistência, interface) → aprovação
2. **Bloco 2:** ADRs restantes + ferramental → aprovação
3. **Bloco 3:** modelo físico de dados + arquitetura (diagrama) → aprovação final

Veto em qualquer ADR: reapresente só aquele ADR com nova recomendação. Após o Bloco 3, compile o TDD, salve e declare o **gate 2 cumprido**.

---

## Modo "como está": sistema que já existe sem TDD

Use quando o sistema já está construído e não tem TDD: o comum manda escrever o que falta antes da próxima change que toque tecnologia. O TDD registra as decisões que o sistema **já tomou**, lidas do código, dos specs e dos documentos; não decide nada novo. Decisão nova entra numa versão seguinte, aprovada como qualquer outra.

O que muda em relação ao modo assistido:

1. **Contexto:** leia em vez de entrevistar. Onde o código, os documentos e os modelos de origem divergem, ou onde algo parece defeito, pergunte ao usuário numa rodada única, com recomendação; as respostas vão para a seção 7, que neste modo se chama "Respostas do usuário (anexo)", no lugar de "Respostas da Entrevista", e cada correção vira uma dívida (abaixo), nunca uma mudança no código feita pelo TDD.
2. **Cabeçalho:** `**Modo de elaboração:** "como está"`, com a versão do produto analisada.
3. **ADR:** Estado, Decisão e **Evidência** (onde a decisão está no repositório, por arquivo e pelo nome do símbolo ou da seção, nunca por número de linha, que envelhece). Contexto, Opções, Justificativa e Consequências entram quando há o que dizer além do código; decisão sem alternativa considerada não as inventa.
4. **Teste da cadeia:** a origem "código" vale como causa, desde que a evidência a aponte; resposta do usuário e RNF do PRD continuam valendo.
5. **Seções a mais:** "Dívidas conhecidas" (cada uma resolvida por change, riscada com a change que a fechou) e "Histórico de versões", as duas depois do handoff, nesta ordem.
6. **Aprovação:** os mesmos três blocos do modo assistido, cada um com o **teste da fidelidade**: toda decisão tem evidência no repositório, e nada descreve o que o sistema não faz.

---

## Estrutura obrigatória do TDD

```markdown
# TDD: [Nome do Produto]

**Status:** Rascunho | Aprovado
**Versão:** 0.1
**Data:** [data]
**PRD de origem:** prd-<nome>.md v<X.Y> (gate 1 cumprido em [data])
**Modo de elaboração:** assistido | expert | "como está"

---

## 1. Sumário das Decisões

| ADR | Decisão | Reversibilidade | Origem |
|-----|---------|-----------------|--------|
| ADR-001 | ... | 🚪 / 🔁 | entrevista Q1 | RST-XXX | default institucional | declaração expert |

## 2. Registros de Decisão (ADRs)

### ADR-001 — [Título]  [🚪|🔁]
- **Estado:** Aprovado
- **Contexto:** [respostas da entrevista e elementos do PRD que motivam]
- **Opções consideradas:** [A, B, C — uma linha cada]
- **Decisão:** [escolha]
- **Justificativa:** [em linguagem de consequência, citando Qn/RST/RNF]
- **Consequências:** [o que fica mais fácil, o que fica vedado]

[... demais ADRs ...]

## 3. Arquitetura

[Diagrama ASCII do fluxo de dados entre componentes, coerente com os ADRs]

## 4. Modelo Físico de Dados

### [tabela/documento] `nome` (deriva de ENT-XXX)

| Campo | Tipo | Restrição | Origem |
|-------|------|-----------|--------|
| id | ... | PK | — |
| ... | ... | NOT NULL | RN-XXX |

## 5. Ferramental e Qualidade

[Bloco institucional da linguagem escolhida: versões, gerenciador, lint,
testes, tipos, CI — ou ADR de dispensa]

## 6. Implantação

[docker-compose.yml quando aplicável + instruções mínimas, ou descrição
do empacotamento local]

## 7. Respostas da Entrevista (anexo)

| # | Pergunta | Resposta | ADRs que informa |
|---|----------|----------|------------------|

## 8. Pendências devolvidas ao PRD

- PEN-TDD-001 — [lacuna/conflito encontrado] → requer decisão do dono do PRD

## 9. Handoff ao Estágio 3

Este TDD, junto ao PRD de origem, é insumo da skill `briefing`, que decompõe o escopo em changes e escreve o briefing de cada uma para o `/opsx:propose`.
```

---

## Qualidade — teste antes do gate 2

1. **Teste da cadeia:** todo ADR cita ao menos uma resposta da entrevista, uma RST ou um RNF do PRD? Decisão sem causa rastreável é opinião, não ADR.
2. **Teste do leigo:** o usuário consegue explicar com as próprias palavras por que cada decisão de porta de um sentido foi tomada? Se não, a justificativa está em jargão — reescreva.
3. **Teste da suficiência:** com PRD + TDD, uma IA consegue iniciar o OpenSpec sem perguntar nada de tecnologia? O que faltar, ela inventará.
4. **Teste da soberania do PRD:** nenhum requisito, regra ou CA foi alterado por aqui? Conflitos estão em PEN-TDD, não resolvidos à revelia?
5. **Teste da simplicidade:** há componente sem RF que o justifique? Corte — arquitetura também tem fora do escopo.

## Saída

Salve como `sdd/tdd-<nome-kebab-case>.md`, ao lado do PRD de origem.

Após salvar:
1. Entregue o arquivo ao usuário
2. Resumo de 2 linhas: decisões de porta de um sentido tomadas e pendências devolvidas ao PRD
3. Declare: "Gate 2 cumprido. Próxima etapa: a decomposição e os briefings (skill `briefing`), que alimentam o `/opsx:propose`."

**Não** exiba o TDD completo no chat — o arquivo é a entrega.
