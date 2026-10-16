# Design

## Context

O `--fonte` está no `modelo/trilha/confere_regras.py`: a função `conferir` lê a `modelo/trilha/` da pasta do kit e a compara, arquivo a arquivo (conteúdo e permissão de execução), com a pasta `trilha/` do projeto. O `trilha/verifica.sh` passa o `--fonte` quando o kit está ao lado (ou em `TRILHA_AI`). Os avisos das travas saem da `avisos_das_travas`, que hoje olha o `core.hooksPath` e se o `.claude/settings.json` cita o `trilha/guarda.py`. O script roda com `python3 -I`, só com a biblioteca padrão, e o kit é um clone git com as tags `vX.Y`.

## Goals / Non-Goals

**Goals:**
- A versão de referência da comparação é a do projeto, nunca a da cópia de trabalho do kit, quando as duas diferem.
- Nenhuma falha nova sem o git do kit, sem as tags ou com um clone raso: nesses casos, aviso.

**Non-Goals:**
- Conferir o projeto contra uma versão diferente da dele (isso é o `kit.py atualizar`).
- Avisar o que o usuário escolhe por sessão (`--bare`, `--settings`).

## Decisions

**1. A versão de cada lado pela linha "Versão X.Y" do comum.** O projeto lê a do `trilha/CLAUDE-comum.md`; o kit, a da `modelo/trilha/CLAUDE-comum.md` da cópia de trabalho. Iguais: a comparação é a de hoje, com a cópia de trabalho, o que cobre o caso comum e a versão em preparo no kit (sem tag ainda). Alternativa descartada: comparar sempre com a tag; reprovaria o projeto feito da cópia de trabalho durante o preparo de uma versão, quando a tag ainda não existe.

**2. A pasta da tag lida pelo git, sem extrair arquivos.** `git -C <kit> ls-tree -r -z vX.Y -- modelo/trilha` dá, por arquivo, o modo (`100755` é executável) e o objeto; `git -C <kit> cat-file --batch` dá o conteúdo de todos de uma vez. Os dois lados viram o mesmo formato (nome → conteúdo e se é executável), e uma só função compara, com as mensagens de hoje. Alternativa descartada: `git archive` extraído numa pasta temporária, que pede o `tarfile` com filtro de extração (diferente entre versões do Python) e escreve no disco.

**3. Sem a tag, aviso.** O `ls-tree` que falha (tag ausente, clone raso, pasta sem git) ou que não traz a `modelo/trilha/` (tag de antes da 2.0) vira o aviso "a pasta trilha/ não foi comparada", sem falha.

**4. As mensagens.** A falha mantém o começo de hoje ("trilha/<arquivo> difere do kit", "falta", "não é do kit", "perdeu a permissão de execução") e termina com "rode o kit.py atualizar do kit, com a escolha do usuário; não edite a pasta". O aviso da versão diferente cita as duas versões: "o kit está na A.B e o projeto na X.Y: a pasta trilha/ foi comparada com a vX.Y; rode o kit.py atualizar do kit, com a escolha do usuário".

**5. O `disableAllHooks` pela precedência.** Lê o `.claude/settings.local.json` e depois o `.claude/settings.json`; o primeiro que tem a chave decide. JSON inválido não conta, como no `confere_metodo.py`. Verdadeiro: aviso que cita a chave e o arquivo.

## Risks / Trade-offs

- [Kit sem as tags (clone raso, cópia baixada sem o git)] → aviso, sem comparar; a cópia continua conferida no `kit.py atualizar`.
- [Dois processos git a mais por verificação, só quando as versões diferem] → custo de milissegundos; a trava do commit não usa o `--fonte`.
- [Tag apontando para o commit errado] → fora do alcance da conferência; a regra de versão do `CLAUDE.md` do kit põe a tag no commit da versão.

## Migration Plan

Nenhuma: os projetos recebem a conferência nova com a cópia da 2.4, pelo `kit.py atualizar`, sob ordem do usuário.

## Verificação

A preencher no apply, com a evidência de cada cenário.

## Respostas à revisão

A preencher depois do `/opsx:verify` e da revisão de código.
