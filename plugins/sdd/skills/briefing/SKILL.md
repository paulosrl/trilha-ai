---
name: briefing
description: >
  Estágio 3 do pipeline PRD → TDD → OpenSpec, antes do /opsx:propose: confere o PRD e o TDD aprovados, decompõe o escopo em changes ordenadas (sdd/decomposicao-<nome>.md), escreve o briefing de cada change para o propose e audita os artefatos que ele gerou. Use quando o usuário, com PRD e TDD aprovados, pedir para decompor em changes, preparar o OpenSpec, gerar ou auditar o briefing. Nunca escreve proposal, spec, design nem tasks.
---

# Skill: Ponte para o OpenSpec (Estágio 3 — adaptador)

Chama-se `briefing` para não se confundir com o propose do OpenSpec (`/opsx:propose`), que é quem gera os artefatos. As regras comuns do repositório (o ciclo, os nomes das pastas, o que dispensa change, a verificação) vêm do kit Trilha AI (`CLAUDE-comum.md`); esta skill as cita e não as repete.

## Posição no pipeline e divisão de trabalho

```
Estágio 1 — PRD (skill prd)           → aprovado (gate 1)
Estágio 2 — TDD (skill tdd)           → aprovado (gate 2)
Estágio 3 — ESTA SKILL (antes do propose) → recepção + decomposição + briefings + auditoria
            /opsx:propose (no repo)   → gera proposal/spec/design/tasks vendo o código
        ↓ gate 3: a revisão que o OpenSpec pede ao fim do propose, feita como auditoria
Implementação: /opsx:apply → verificação → archive → próxima change
```

**Fronteira inviolável:** esta skill nunca escreve `proposal.md`, `spec.md`, `design.md` ou `tasks.md`. Quem os gera é o OpenSpec nativo, dentro do repositório, com acesso ao código — única posição de onde changes sobre código existente (brownfield) podem ser especificadas corretamente. Se o usuário pedir que esta skill gere os artefatos diretamente, explique a fronteira em duas frases e gere o briefing. Ela também não acrescenta passo nem ordem ao fluxo do OpenSpec: age antes do propose, na revisão que ele pede e depois do archive.

**Pré-condições:** PRD aprovado (gate 1) e TDD aprovado (gate 2), com o TDD declarando o PRD de origem. Faltando um, direcione à skill correspondente, salvo o briefing curto num projeto que nasceu sem PRD ou TDD: até ele escrever o que falta, uma correção de comportamento que um spec já descreve nasce de um briefing curto, escrito a partir desse spec (o requisito e o cenário corrigidos, o defeito, o esperado, o que já existe), sem requisito novo nem decisão técnica, aprovado pelo usuário; o resto do ciclo é o mesmo. Nesse caso, o passo do ciclo de cada change fica no `ANDAMENTO.md`, e a change arquivada entra na tabela "Ciclo" quando a decomposição nascer.

## Princípios

1. **O OpenSpec executa; esta skill prepara e confere.** Entrada de qualidade (briefing) e saída auditada (checklist) — o meio pertence à ferramenta nativa.
2. **Nada se redecide no caminho.** O briefing entrega os ADRs que tocam a change, sob "NÃO redecidir", para o propose referenciá-los, nunca reabri-los. Tecnologia redecidida no `design.md` é defeito de auditoria.
3. **Lacuna se devolve, não se resolve.** Falta de requisito → `PEN-PRD-XXX` (volta ao Estágio 1). Falta de decisão técnica → `PEN-TDD-XXX` (volta ao Estágio 2). O briefing lista as pendências que tocam a change; nenhuma se resolve por improviso dentro do OpenSpec.
4. **Decomposição completa, especificação progressiva.** Todas as changes são nomeadas e ordenadas de uma vez; o briefing é emitido um por vez, quando a change anterior estiver com o merge feito (é no merge que ela fecha, pelo `CLAUDE-comum.md`) — a partir da change 02, o propose nativo precisa ver, na main, o código que já existe.
5. **Rastreabilidade é auditável nos dois sentidos.** PRD → artefatos (todo RF virou spec? todo CA virou cenário?) e artefatos → PRD (há spec sem RF? cenário inventado?).

## Processo

### 1. Recepção — validar o par PRD + TDD

Leia os dois documentos e verifique:

1. O TDD referencia este PRD na versão vigente?
2. Todo `RST-XXX` do PRD foi tratado no TDD (ADR ou dispensa justificada)?
3. Há `PEN-TDD-XXX` aberta que bloqueie a primeira change?
4. Todo `ESC-XXX` tem RF; todo RF tem CA? Num PRD "como está", escrito de um sistema que já tem specs, os cenários dos specs fazem as vezes dos CAs: aceite; o nome do teste de cada cenário segue a regra de tarefas do `openspec/config.yaml`.
5. Os ADRs cobrem o mínimo para implementar (topologia, linguagem, persistência, interface, ferramental)?

Emita no chat o **relatório de recepção**: `ACEITO` | `ACEITO_COM_PENDENCIAS` (listadas, com estágio de destino) | `DEVOLVIDO` (o que falta, para qual skill). Prossiga apenas de ACEITO/ACEITO_COM_PENDENCIAS.

### 2. Decomposição — o mapa de changes

Derive as changes dos `ESC-XXX`, aplicando os critérios:

1. **Valor independente:** cada change entrega comportamento observável cujos CAs passam sem as changes seguintes.
2. **Fundação primeiro:** a change 01 estabelece entidade central + operação primária + esqueleto dos ADRs, com o manifesto e a parte da stack do `scripts/check.sh` e do CI, como o `CLAUDE-comum.md` manda ao fechar o gate 2; as demais incrementam.
3. **Tamanho de ciclo:** uma change cabe em uma sessão de implementação; grande demais divide, menor que um comportamento completo consolida.
4. **Dependência em prosa:** ordem declarada com razão ("02 depende de 01 porque exporta o que 01 cadastra").
5. **Fora de change, só o que o `CLAUDE-comum.md` dispensa:** a decomposição cita essa regra, sem repeti-la nem ampliá-la.

Apresente a tabela (change, ESC/RF cobertos, depende de, razão) e **aguarde aprovação**. Aprovada, salve `sdd/decomposicao-<nome>.md` — o arquivo de registro desta skill, ao lado dos briefings — neste esqueleto:

```markdown
# Decomposição: <nome do produto>

## 1. Mapa de changes

| NN | change | ESC e RF cobertos | depende de | razão |
|---|---|---|---|---|
| 01 | `<nome-da-change>` | ESC-001 · RF-001, RF-002 | — | <por que vem nesta ordem> |
| 02 | `<nome-da-change>` | ESC-002 · RF-003 | 01 | <por que depende da 01> |

## 2. Regras de convivência

<o que as changes compartilham; o que fica fora de change, citando o CLAUDE-comum.md sem repeti-lo>

## Ciclo

| NN | briefing | auditoria | archive |
|---|---|---|---|
| 01 | briefing-change-01-<nome>.md (aprovado AAAA-MM-DD) | gate 3 aprovado AAAA-MM-DD | arquivada em <pasta que o archive criou> (PR #N) |
| 02 | — | — | — |
```

Os títulos `## 1.`, `## 2.` e `## Ciclo`, e o número da change na primeira coluna das duas tabelas, são o formato que a conferência do método lê na trava do commit: as changes da seção 1 e as do "Ciclo" são as mesmas. Outras seções (a recepção, as pendências) podem vir entre a 2 e o "Ciclo". O "Ciclo" registra os marcos de cada change e é lido pela página do projeto (`sdd/documentacao.html`): uma linha por change, na ordem; `—` enquanto o passo não aconteceu. Change retirada antes do archive mantém as duas linhas: na seção 1, a razão termina com `retirada em AAAA-MM-DD` e o motivo; no "Ciclo", a coluna archive começa com `retirada em AAAA-MM-DD`. Num projeto que já tem changes arquivadas, as tabelas nascem com elas.

### 3. Briefing — a entrada do /opsx:propose

Antes de propor, rode `openspec list`: evita change duplicada ou em colisão com outra change ativa. Conte as tarefas de uma change por `openspec instructions apply --change <nome> --json` (`progress.total`) antes de escrever o número.

Nome das pastas: a change ativa nasce como `NN-nome`, e o archive do OpenSpec acrescenta a data (`AAAA-MM-DD-NN-nome`); o número tem dois dígitos até 99 e três a partir de 100, sem renomear os anteriores. Os specs seguem o nome que o OpenSpec dá: o comportamento que o spec descreve, em kebab-case, sem data nem número; o delta de um spec existente usa exatamente o nome da pasta principal. Confira com `ls` antes de criar e depois de arquivar.

Para a change da vez, emita o briefing como bloco de texto pronto para colar no comando nativo, dentro do repositório:

```markdown
# Briefing de propose — Change NN: [nome]

## Contexto
Produto: [nome] — PRD prd-<nome>.md v<X.Y> (gate 1) · TDD tdd-<nome>.md v<X.Y> (gate 2).
Esta é a change NN de [total]; changes anteriores arquivadas: [lista ou "nenhuma"].
Nome da change no OpenSpec: `NN-<nome>` (a pasta que o propose cria em `openspec/changes/`), salvo exceção no `CLAUDE.md` do repositório.

## Escopo DESTA change
[ESC-XXX cobertos. Para cada RF do recorte: ID, tipo EARS, descrição normativa
na íntegra. Regras de negócio (RN-XXX) na íntegra. Entidades (ENT-XXX) com
atributos de negócio. Fluxos (FL-XXX) com exceções. CAs (Gherkin) na íntegra, ou os
cenários dos specs que fazem as vezes deles.]

## Decisões técnicas herdadas (NÃO redecidir)
[Tabela: aspecto → decisão → ADR-XXX. Extraída do TDD, só o que toca esta change.]
Decisão local legítima = organização interna de código que o TDD não cobre.

## Fora desta change
[ESCs das changes seguintes + FE-XXX do PRD. Comportamento daqui não entra.]

## Pendências herdadas
[PEN-PRD/PEN-TDD que tocam esta change, com instrução de contorno, ou "nenhuma"]

## O que já existe
[Para a change 02 em diante: o que as changes arquivadas entregaram e esta change toca.]
```

O `context` (a língua) e as regras por artefato (a origem citada de cada requisito e cenário, um teste por cenário, a execução manual como última tarefa) estão no `openspec/config.yaml` do repositório, que o OpenSpec lê ao gerar cada artefato: o briefing não as repete.

Entregue com as instruções de uso:

1. No repositório (primeira vez): `openspec init`, com o `openspec/config.yaml` do kit preenchido
2. Salve o briefing em `sdd/briefing-openspec/briefing-change-NN-<nome>.md` e rode `/opsx:propose @sdd/briefing-openspec/briefing-change-NN-<nome>.md`
3. Traga os artefatos gerados de volta para a auditoria (passo 4)

### 4. Auditoria — conferir o que o OpenSpec gerou

A auditoria é a revisão que o próprio OpenSpec pede ao fim do propose, antes do apply. Receba os artefatos (colados ou como arquivos) e execute o checklist:

| # | Verificação | Defeito se |
|---|---|---|
| 1 | Cobertura PRD → spec | RF do recorte sem spec correspondente |
| 2 | Cobertura CA → cenário | CA do recorte sem cenário |
| 3 | Sentido inverso | Spec/cenário sem origem no PRD (invenção) |
| 4 | Herança técnica | design.md (quando o OpenSpec o criou) redecide ou omite ADR aplicável |
| 5 | Decisões locais | DT local que na verdade contraria/estende ADR |
| 6 | Escopo | Comportamento de change futura ou de FE-XXX vazou |
| 7 | Tasks | Task sem spec de origem; ausência de tasks de teste |
| 8 | Pendências | Pendência herdada resolvida por improviso em vez de contornada |

Emita o **laudo de auditoria**: `APROVADO` (nenhum defeito: peça ao usuário a aprovação do gate 3 e só com ela registre-o na tabela "Ciclo" e libere o apply) ou lista numerada de defeitos, cada um com a correção a pedir ao `/opsx:update`, que revisa os artefatos sem recriá-los. Reaudite após correção.

### 5. Ciclo

Depois do merge da change, que vem após o archive e os passos que o `openspec/config.yaml` manda fazer depois dele (entre eles, a linha da change na tabela "Ciclo"), retorne ao passo 3 para o briefing da próxima — agora com "changes arquivadas" atualizado, para o propose nativo tratar o código existente como brownfield.

## Qualidade — antes de emitir cada briefing

1. **Autossuficiência:** o briefing contém os textos na íntegra (RF, RN, CA, ADR)? O /opsx:propose lê o PRD e o TDD do repositório, mas eles trazem o escopo de todas as changes: o texto na íntegra fixa o recorte desta, sem que o propose o reconstrua ou parafraseie — referência por ID sem o texto é briefing quebrado.
2. **Recorte limpo:** nenhum RF aparece em duas changes; nenhum RF do escopo total ficou órfão de change.
3. **Herança mínima suficiente:** só os ADRs que tocam a change — herança total é ruído.
4. **Teste do assistente:** com o briefing, o propose consegue trabalhar sem perguntas de produto ou de tecnologia?

## Saída

Arquivos desta skill: apenas `sdd/decomposicao-<nome>.md` (tabela aprovada, o que dispensa change e a tabela "Ciclo") e, por ciclo, `sdd/briefing-openspec/briefing-change-NN-<nome>.md`. Artefatos OpenSpec vivem no repositório, gerados pela ferramenta nativa — nunca por esta skill.

Resumo por etapa no chat: recepção (veredicto), decomposição (nº de changes), briefing (change e recorte), auditoria (laudo).

Correção de texto na decomposição que não muda escopo nem ordem (redação, erro, referência) não sobe a versão dela: fica no registro de processo, se houver, ou na mensagem do commit. Só a mudança de sentido é versão nova, aprovada pelo usuário.
