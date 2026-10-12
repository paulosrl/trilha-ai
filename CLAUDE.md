# CLAUDE.md — Trilha AI

Este repositório é a **fonte do padrão** Trilha AI: o `CLAUDE-comum.md`, o esqueleto do `CLAUDE.md`, o `ANDAMENTO.md`, o `openspec/config.yaml`, os scripts e a pasta `curso/`. Ele não segue o próprio kit: não importe o `CLAUDE-comum.md` aqui nem crie `sdd/` aqui. O que vale está no `README.md`.

## Regras

- Toda mudança no `CLAUDE-comum.md` ou no `curso/CLAUDE-curso.md` sobe a versão e a data na linha "Versão X.Y, de AAAA-MM-DD." e é registrada na mensagem do commit; os repositórios que seguem o padrão recebem a cópia depois, cada um sob ordem do usuário nomeando-o.
- Os arquivos de regras falam de "o usuário", nunca de "a pessoa"; o comum não menciona o curso e o curso não menciona o comum; nada aqui cita um projeto específico.
- O `CLAUDE-comum.md` e o esqueleto do `CLAUDE.md` somados cabem em 200 linhas.
- Antes do commit: `python3 -m unittest discover -s testes` (Python 3 puro, sem dependências) e confira o código de saída.
- Responda em PT-BR, em linguagem simples, uma coisa por vez; publique só com "sim" explícito.
