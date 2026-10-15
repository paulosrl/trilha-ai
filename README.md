# Trilha AI: o kit de partida de um repositório no método

Trilha AI é um método de desenvolvimento assistido por IA: PRD → TDD → OpenSpec, com o usuário aprovando em gates e cada cenário virando um teste. Este repositório é a fonte do padrão que todo repositório do método copia.

O percurso inteiro, estação por estação, com o que acontece no git e no GitHub em cada uma, está desenhado em `mapa-da-trilha.html`: abra-o no navegador. Ele explica o método e não se copia para os projetos.

Este repositório é a **fonte** dos arquivos que todo repositório novo copia. O `CLAUDE-comum.md` daqui é a versão vigente do padrão (a linha "Versão" no topo dele diz qual). Os outros arquivos são esqueletos, com o que preencher entre `<` e `>`.

Para o passo a passo com a explicação de cada coisa, siga a etapa 0 do guia do aluno, no repositório do curso (https://github.com/paulosrl/consulta-publica, pasta `docs/curso/`). A ordem, resumida:

1. **Instale as ferramentas** (Claude Code, OpenSpec, CodeGraph e o plugin `sdd`), pela subseção "Instalar as ferramentas" da etapa 0, que copia os comandos das documentações oficiais. O kit precisa também do **Python 3** instalado, porque o verificador `scripts/confere_regras.py` é um programa Python sem dependências; no Ubuntu e no WSL ele costuma vir instalado: confira com `python3 --version`. Precisa ainda de uma **conta no GitHub** e do GitHub CLI (`gh`, instalação em https://cli.github.com), autenticado uma vez com `gh auth login`: todo repositório do método tem um remoto privado no GitHub.
2. **Crie a pasta e o git:** `mkdir <nome> && cd <nome> && git init`.
3. **Copie os arquivos deste repositório** (menos este README, o `CLAUDE.md`, o `mapa-da-trilha.html` e a pasta `testes/`) para a raiz do repositório novo, mantendo os caminhos:

   | Arquivo | O que fazer |
   |---|---|
   | `CLAUDE-comum.md` | copiar **sem mudar nada** |
   | `esqueleto-CLAUDE.md` | copiar como `CLAUDE.md`; preencher o que está entre `<` e `>`; apagar o que não se aplica |
   | `ANDAMENTO.md` | preencher a etapa e a hora; nasce "nada em andamento" |
   | `openspec/config.yaml` | preencher o contexto; as regras por artefato ficam como estão |
   | `scripts/check.sh` | a parte das regras já funciona; a parte da stack entra na etapa 2 |
   | `scripts/confere_regras.py` | copiar sem mudar nada |
   | `scripts/confere_metodo.py` | copiar sem mudar nada; confere a decomposição, o TDD e o `ANDAMENTO.md`; os repositórios ao lado entram no `check.sh`, um `--vizinho` por nome |
   | `scripts/gerar_pagina_sdd.py` e `scripts/pagina_sdd_modelo.html` | copiar sem mudar nada; geram `sdd/documentacao.html` |
   | `sdd/` | criar vazia (`mkdir sdd`): o PRD, o TDD, a decomposição e os briefings nascem nela |
   | `github-verificacao.yml` | copiar como `.github/workflows/verificacao.yml`: a cada envio, o GitHub roda o `check.sh` e o `openspec validate`; a parte da stack entra na etapa 2 |
   | `.gitignore` | apagar o bloco da stack que não for a sua, depois da etapa 2 |

4. **Inicialize as ferramentas no repositório.** Uma vez por máquina, antes: `openspec config profile` e marque também o `verify`, que o perfil padrão do OpenSpec não traz e o ciclo usa no passo 5 (num repositório já inicializado, rode depois `openspec update`). Então `openspec init` (ele mantém o `config.yaml` copiado; se perguntar, não o sobrescreva) e `codegraph init`.
5. **Confira:** `bash scripts/check.sh` deve terminar com `ok` na parte das regras e na do método. Com este kit em `../trilha-ai` (ou em `TRILHA_AI`), ele confere também que o comum é cópia idêntica do daqui; sem ele, avisa.
6. **Primeiro commit,** com a linha de coautoria da IA, **e o repositório no GitHub:** `gh repo create <nome> --private --source . --push` cria o repositório privado, liga-o como `origin` e envia o primeiro commit. Na conta gratuita, o merge só com a verificação verde é regra do método; com o GitHub Pro (ou num repositório público), ligue também a proteção da main, exigindo o check `verificar`, mas deixe o dono passar por ela: o trabalho fora de change (PRD, TDD, decomposição) e o fechamento de cada change vão direto à main.
7. **Siga para a etapa 1 do guia:** o PRD.

## Os arquivos de regras

O Claude Code lê o `CLAUDE.md` da raiz de cada repositório. No método, as regras se dividem em dois arquivos, para que as comuns fiquem num lugar só e o `CLAUDE.md` de cada projeto fique curto:

| Arquivo | Vale para | Papel |
|---|---|---|
| `CLAUDE-comum.md` | todo projeto do método, copiado sem mudar | as regras do método, iguais em todo projeto |
| `esqueleto-CLAUDE.md` | todo projeto novo, copiado como `CLAUDE.md` | o modelo do que é só daquele projeto (o que ele é, os documentos, os comandos, as armadilhas, as exceções ao comum); já traz a linha `@CLAUDE-comum.md`, que faz o Claude ler o comum |
| `CLAUDE.md` deste repositório | só este repositório | as regras de manutenção do kit; não importa o comum nem serve de modelo, porque este repositório não é um projeto do método |

## Ao mudar o padrão

O `CLAUDE-comum.md` muda **aqui**, com a versão e a data novas e o teste verde (`python3 -m unittest discover -s testes`), e só depois são copiados para cada repositório, cada um sob ordem do usuário. Um repositório nunca edita a própria cópia: o que é dele vai no `CLAUDE.md`, em "Exceções ao comum" se contrariar o comum. O `confere_regras.py --fonte` acusa a cópia divergente.
