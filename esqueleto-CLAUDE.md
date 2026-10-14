# CLAUDE.md — <nome do produto>

Regras só deste repositório. As comuns a todo projeto (o método SDD, o ciclo OpenSpec, o registro de cada decisão, o trabalho interrompível, como trabalhar com o usuário, as armadilhas) estão em `CLAUDE-comum.md`, importado abaixo.

@CLAUDE-comum.md

## O que é

<uma ou duas frases: o que a ferramenta faz e para quem>.

## Documentos

- Em `sdd/`: PRD `prd-<nome>.md` · TDD `tdd-<nome>.md` · decomposição `decomposicao-<nome>.md` · briefings `briefing-openspec/briefing-change-NN-*.md` · a página `documentacao.html`.
- Contexto e regras por artefato do OpenSpec: `openspec/config.yaml`. Onde o trabalho parou: `ANDAMENTO.md`.
- Registro de processo (opcional; apague se não houver): `<caminho>`, atualizado `<quando>`.

## Comandos

```bash
<instalar as dependências>
scripts/check.sh    # as regras (confere_regras.py) e, depois da etapa 2, lint, tipos e testes
python3 scripts/gerar_pagina_sdd.py    # sdd/documentacao.html, ao fechar cada etapa
<rodar>
```

## Regras de código

- <gerenciador de pacotes e versão da linguagem, definidos no TDD; lint e tipos>.
- <onde ficam as respostas gravadas das fontes e como são simuladas nos testes>.

## Dados a proteger

- <o dado real que nunca entra em teste manual, e a variável ou o caminho da cópia descartável>.

## Armadilhas próprias

- <o que já deu errado neste repositório e não pode repetir; comece vazio>.

## Exceções ao comum

- Nenhuma.
