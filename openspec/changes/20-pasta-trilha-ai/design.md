# Design

## Context

Ver `proposal.md` (Why). A pasta entrou na 2.0, quando o `kit.py atualizar` passou a migrar as cópias soltas da raiz, de `scripts/` e de `.githooks/` para ela (o `_migrar`, o `ANTES_DA_2_0` e o `_migrar_check`). A ferramenta lê as versões antigas do kit pelo git (o `_caminhos` e o `_na_versao`), e a conferência das regras compara a pasta do projeto com a `modelo/trilha/` da tag da versão dele (o `_conteudos_da_tag`). O `.claude/settings.json` de cada projeto liga a trava por um caminho (`$CLAUDE_PROJECT_DIR/trilha/guarda.py`), e o `_sem_guardas_antigas` tira a trava de outra versão pelos nomes de `GUARDAS`.

## Goals / Non-Goals

**Goals:**
- Um `kit.py atualizar` leva o projeto da `trilha/` à `trilha-ai/` sem passo à mão no que é do método.

**Non-Goals:**
- Trocar as citações a `trilha/` nos arquivos do próprio projeto: o kit só as aponta.
- Manter as duas pastas por um tempo: a troca é de uma vez, numa versão.

## Decisions

### D1. A troca no kit
`git mv modelo/trilha modelo/trilha-ai`, e todo caminho `trilha/` que fala da pasta vira `trilha-ai/`, nos arquivos que vão aos projetos, na ferramenta, nos testes, nos specs e nos textos do kit. Ficam como estão os registros históricos (as auditorias, o plano de migração, as changes arquivadas) e os nomes que já são `trilha-ai` (o repositório, o marketplace, o `--vizinho trilha-ai`).

### D2. As versões antigas
Na ferramenta, o `ANTES_DA_2_0` passa a ter as chaves em `trilha-ai/`, e o `_caminhos` de um nome `trilha-ai/X` acrescenta o `modelo/trilha/X` das versões 2.0 a 2.18. Na conferência das regras, o `_conteudos_da_tag` lê a `modelo/trilha-ai/` da tag e, sem ela, a `modelo/trilha/`: um projeto já na `trilha-ai/` nunca está numa versão de antes da 2.19, mas a leitura das duas não custa nada e deixa a conferência ler qualquer tag.

### D3. A migração da pasta
No `_migrar`, antes da cópia: se existe o `trilha/CLAUDE-comum.md`, a pasta é a do método (o comum proíbe arquivo próprio nela, e a conferência das regras o reprova). A ferramenta avisa cada arquivo dela que o kit não tem (pelo nome relativo, diante da lista do método) e apaga a pasta inteira. Como o `atualizar` recusa trabalho não commitado, tudo o que sai volta pelo git. Sem o comum, a pasta é do projeto e fica.

*Alternativa:* apagar só os arquivos que o kit tinha na versão do projeto. Recusada: deixaria uma `trilha/` com sobras que a regra do método já proíbe, e o aviso já nomeia o que não era do kit.

### D4. A versão de antes
O `antes` sai do `trilha-ai/CLAUDE-comum.md`, depois do `trilha/CLAUDE-comum.md`, depois do `CLAUDE-comum.md` da raiz.

### D5. A importação, o check.sh, a trava e o hooksPath
- A importação: a linha `@CLAUDE-comum.md` ou `@trilha/CLAUDE-comum.md` (com espaço no fim ou não) vira `@trilha-ai/CLAUDE-comum.md`.
- O `check.sh`: o `_check_migrado` troca o `trilha/verifica.sh` (o caminho, onde estiver na linha, com os argumentos depois) por `trilha-ai/verifica.sh`, depois da troca da parte fixa de antes da 1.37, que já escreve o nome novo. A previsão da migração continua a mesma função.
- A trava do Claude Code: o `GUARDAS` ganha o `trilha-ai/guarda.py`; a de `trilha/guarda.py` sai pelo `_sem_guardas_antigas`, que a acha pelo nome (`trilha/guarda.py` não é parte de `trilha-ai/guarda.py`), e a soma põe a do modelo.
- O `core.hooksPath`: o `_ligar_travas` já o grava sempre; passa a `trilha-ai/hooks`.

### D6. As citações que sobram no projeto
Depois da migração da pasta, e só nela, a ferramenta procura nos arquivos versionados do projeto, fora da `trilha-ai/`, o `trilha/` que não seja parte de outro nome (`git grep -l` com a palavra inteira) e avisa a lista, para a troca à mão. O que já foi trocado (a importação, o `check.sh`) não aparece.

### D7. A recusa
A pasta `trilha-ai/` sem o `trilha-ai/CLAUDE-comum.md` recusa, como a `trilha/` recusava. A `trilha/` sem o comum deixa de ser obstáculo.

### D8. A versão
A linha "Versão 2.19, de 2026-10-24." no comum e o `plugin.json` na 2.19.0; a tag `v2.19` no merge. O comum e o esqueleto continuam nos limites (200 linhas somados, 16 KB o comum).

## Risks / Trade-offs

- [O projeto que tinha arquivo próprio na `trilha/` do método o perde na migração] → O aviso o nomeia, e ele volta pelo git; a regra do método já o proibia ali.
- [Um script, o CI ou um documento do projeto cita `trilha/` e quebra depois da migração] → O aviso do D6 os lista; o `check.sh` e a conferência rodam no fim do `atualizar`, e uma quebra na verificação aparece já ali.
- [Um projeto ainda na 2.18 que roda a conferência com o kit 2.19 ao lado] → A cópia dele (2.18) compara com a tag `v2.18`, que tem `modelo/trilha/`, e não muda; a migração só acontece pelo `kit.py atualizar`.
