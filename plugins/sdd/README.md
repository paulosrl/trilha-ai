# Plugin `sdd`: as skills do método Trilha AI

Três skills do Claude Code que levam uma ideia de produto até o briefing de cada change do OpenSpec, separando **o que o produto faz** (decisão do dono do produto), **com que tecnologia** (decisão técnica assistida) e **em que ordem implementar** (OpenSpec).

O plugin é parte do kit Trilha AI, e a versão dele é a do kit. O ciclo de cada change, os nomes das pastas, a verificação e o versionamento dos documentos são regras do `modelo/CLAUDE-comum.md` do kit, que prevalece sobre o que estiver aqui. As skills produzem só os documentos de `sdd/`.

## Instalação

```bash
claude plugin marketplace add paulosrl/trilha-ai
claude plugin install sdd@trilha-ai
claude plugin list        # deve listar sdd@trilha-ai, na versão do kit
```

Para atualizar: `claude plugin marketplace update trilha-ai` e `claude plugin update sdd@trilha-ai`, depois uma sessão nova.

No método, só a instalação como plugin vale: o kit cita as skills como `sdd:prd`, `sdd:tdd` e `sdd:briefing`, e a conferência do método avisa quando o plugin instalado não está na versão do projeto. As skills também são acionadas pela descrição do pedido ("preciso de um PRD para…").

O estágio 3 precisa do OpenSpec no repositório do projeto: `npm install -g @fission-ai/openspec`, na versão que o CI do kit fixa (`modelo/.github/workflows/verificacao.yml`), e depois `openspec init` na raiz do projeto, como manda o `README.md` do kit.

## O encadeamento

```
Ideia
  → sdd:prd       PRD: o quê e o porquê, sem tecnologia          → gate 1
  → sdd:tdd       TDD: as decisões técnicas, como ADRs            → gate 2
  → sdd:briefing  recepção do par, decomposição em changes e o briefing de cada uma
  → /opsx:propose os artefatos da change, gerados pelo OpenSpec
  → a revisão que o OpenSpec pede ao fim do propose, pelo checklist da sdd:briefing → gate 3
  → o resto do ciclo da change, no CLAUDE-comum.md
```

## Por que três estágios

| Princípio | Consequência prática |
|---|---|
| **Autoridade separada** | Quem aprova "telefone exige 11 dígitos" é o dono do produto; quem aprova "PostgreSQL com pgvector" precisa de contexto técnico. Cada decisão tem o seu gate e o seu aprovador. |
| **Reversibilidade assimétrica** | Requisito errado se corrige com uma edição; stack errada se corrige com reescrita. Decisões de custo de reversão diferente não dividem o mesmo documento nem o mesmo gate. |
| **Reuso do PRD** | O mesmo PRD gera TDDs diferentes (protótipo local ou web multiusuário) sem reescrever um requisito. |
| **Fim da redecisão** | O `design.md` de cada change referencia os ADRs do TDD em vez de redecidir tecnologia. |

## As skills

Cada `SKILL.md` é a fonte do que a skill faz; o resumo abaixo só orienta.

- **`sdd:prd`** (`skills/prd/SKILL.md`): escreve `sdd/prd-<nome>.md` — problema, objetivos, atores, escopo, requisitos em EARS, regras, entidades conceituais, fluxos, critérios de aceite e o que fica fora — sem nenhuma tecnologia, salvo a restrição imposta de fora (`RST`). Aprovação em cinco blocos, em linguagem simples. O modo "como está" escreve o PRD de um sistema que já existe, lido dos specs, do README e do código.
- **`sdd:tdd`** (`skills/tdd/SKILL.md`): escreve `sdd/tdd-<nome>.md` — cada decisão técnica como ADR, a arquitetura, o modelo físico de dados e o ferramental. No modo assistido, entrevista por consequências ("quantas pessoas usam ao mesmo tempo?"), com uma recomendação justificada por decisão; no modo expert, valida a stack declarada; no modo "como está", registra as decisões que o código já tomou. Aprovação em três blocos.
- **`sdd:briefing`** (`skills/briefing/SKILL.md`): confere o par PRD e TDD, decompõe o escopo em changes ordenadas (`sdd/decomposicao-<nome>.md`, com a tabela "Ciclo"), escreve o briefing de cada change para o `/opsx:propose` e audita o que ele gerou. Nunca escreve os artefatos do OpenSpec.

## Erros comuns e como o método os evita

| Erro | Mecanismo de prevenção |
|---|---|
| PRD com stack embutida, que prende o produto a uma tecnologia | As proibições do estágio 1 e o teste da troca de stack |
| Leigo "aprovando" banco de dados que não entende | Entrevista por consequências, recomendação justificada e teste do leigo |
| Tecnologia decidida tarde, como remendo | O estágio 2 é o lugar nomeado da decisão, antes de qualquer spec |
| IA inventando o modelo de dados | Modelo físico derivado das entidades do PRD, no TDD, antes do código |
| `design.md` redecidindo a arquitetura | A regra do design no `openspec/config.yaml` do kit: referenciar o ADR, nunca redecidir |
| Decisão técnica mudando requisito por conta própria | Soberania do PRD; a pendência (`PEN-TDD`) volta ao dono do produto |

## Perguntas frequentes

**Posso pular o TDD num projeto trivial?** Não pule: reduza. O modo expert, com meia dúzia de ADRs de uma linha, custa minutos e deixa registrado por que o projeto é simples; é o ADR de dispensa (Docker, CI) que protege a simplicidade de virar acidente.

**E se eu já sei a stack?** Use o modo expert do estágio 2: a skill só valida a coerência com o PRD e registra.

**O PRD pode citar uma tecnologia que o cliente impôs?** Sim, como `RST-XXX`, com origem e data: é um fato imposto, não uma decisão. O TDD a valida e a converte em ADR "decidido por RST-XXX".

**Quem aprova cada gate?** O usuário, nos três: o gate 1 (o produto) e o gate 2 (a tecnologia, com a assistência da entrevista) bloco a bloco, e o gate 3 na revisão que o OpenSpec pede ao fim do propose, depois das correções que ele escolher.
