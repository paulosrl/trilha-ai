# Trilha AI: o kit de partida de um repositório no método

Trilha AI é um método de desenvolvimento assistido por IA: PRD → TDD → OpenSpec, com o usuário aprovando em gates e cada cenário virando um teste. Este repositório é a fonte do padrão que todo repositório do método copia.

O percurso inteiro, estação por estação, com o que acontece no git e no GitHub em cada uma, está desenhado em `mapa-da-trilha.html`: abra-o no navegador. Ele explica o método e não se copia para os projetos.

Este repositório é a **fonte** dos arquivos que todo repositório novo copia: eles ficam na pasta `modelo/`, e só ela vai aos projetos. O `modelo/trilha/CLAUDE-comum.md` é a versão vigente do padrão (a linha "Versão" no topo dele diz qual). Os outros arquivos são esqueletos, com o que preencher entre `<` e `>`.

Para o passo a passo com a explicação de cada coisa, siga a etapa 0 do guia do aluno, no repositório do curso (https://github.com/paulosrl/consulta-publica, pasta `docs/curso/`). A ordem, resumida:

1. **Instale as ferramentas** (Claude Code, OpenSpec, CodeGraph e o plugin `sdd`), pela subseção "Instalar as ferramentas" da etapa 0, que copia os comandos das documentações oficiais. O plugin `sdd` é publicado por este repositório: `claude plugin marketplace add paulosrl/trilha-ai`, uma vez por máquina. Ele vale por projeto, e não para o usuário inteiro, e se instala no passo 4 (o que ele faz está em `plugins/sdd/README.md`). O kit precisa também do **Python 3** instalado, porque os verificadores de `trilha/` são programas Python sem dependências; no Ubuntu e no WSL ele costuma vir instalado: confira com `python3 --version`. Precisa ainda de uma **conta no GitHub** e do GitHub CLI (`gh`, instalação em https://cli.github.com), autenticado uma vez com `gh auth login`: todo repositório do método tem um remoto privado no GitHub.
2. **Crie o repositório com o kit:** com este repositório em `../trilha-ai`, rode `python3 ../trilha-ai/ferramentas/kit.py novo <nome>`. Ele cria a pasta, o git (na branch `main`) e a pasta `sdd/`, copia os arquivos, como na tabela do passo 3, e imprime os próximos passos.
3. **Preencha o que é do projeto.** A tabela diz o que cada arquivo de `modelo/` é e o que fazer com ele; a cópia à mão, sem a ferramenta, segue a mesma tabela. O resto deste repositório é só do kit e não se copia:

   | Arquivo | O que fazer |
   |---|---|
   | `trilha/` | copiar a pasta inteira **sem mudar nada**: o comum, os verificadores, o `verifica.sh` (a parte fixa da verificação), o gerador da página, a trava do Claude Code (`guarda.py`) e a do commit (`hooks/pre-commit`, ligada com `git config core.hooksPath trilha/hooks`, uma vez por clone) |
   | `esqueleto-CLAUDE.md` | copiar como `CLAUDE.md`; preencher o que está entre `<` e `>`; apagar o que não se aplica |
   | `ANDAMENTO.md` | preencher a etapa e a hora; nasce "nada em andamento" |
   | `openspec/config.yaml` | preencher o contexto; as regras por artefato ficam como estão |
   | `scripts/check.sh` | a parte fixa (`bash trilha/verifica.sh`) já funciona; os repositórios ao lado entram nela, um `--vizinho` por nome; a parte da stack entra na etapa 2 |
   | `sdd/padroes-tecnicos.md` | copiar no mesmo caminho: os padrões técnicos de partida que a skill `sdd:tdd` lê; ajustá-los antes do TDD. Na pasta `sdd/` nascem também o PRD, o TDD, a decomposição e os briefings |
   | `.github/workflows/verificacao.yml` | copiar no mesmo caminho: a cada envio, o GitHub roda o `check.sh` (que inclui o `openspec validate`) e a busca de senhas e chaves no histórico (gitleaks); as ações vão fixadas pelo commit; a parte da stack entra na etapa 2 |
   | `.github/dependabot.yml` | copiar no mesmo caminho: o Dependabot (gratuito) abre um pull request a cada versão nova das ações e, depois da etapa 2, das dependências da stack |
   | `claude-settings.json` | copiar como `.claude/settings.json`, ou somar o que ele traz ao que já existir: liga o `trilha/guarda.py` e declara o plugin `sdd@trilha-ai` (`enabledPlugins`) e o marketplace dele (`extraKnownMarketplaces`) |
   | `gitignore` | copiar como `.gitignore`; apagar o bloco da stack que não for a sua, depois da etapa 2 |

4. **Inicialize as ferramentas no repositório.** Uma vez por máquina, antes: `openspec config profile` e marque também o `verify`, que o perfil padrão do OpenSpec não traz e o ciclo usa no passo 5 (num repositório já inicializado, rode depois `openspec update`). Então `openspec init` (ele mantém o `config.yaml` copiado; se perguntar, não o sobrescreva), `codegraph init` e `claude plugin install sdd@trilha-ai --scope project`: o `.claude/settings.json` declara o plugin, mas a instalação é de cada máquina, uma vez por projeto. Quem tem o plugin instalado para o usuário inteiro (como o kit ensinava até a 2.1) o tira com `claude plugin uninstall sdd@trilha-ai` depois que todos os projetos da máquina o declararem e o tiverem instalado assim; até lá, essa instalação continua valendo em todo repositório.
5. **Confira:** `bash scripts/check.sh` deve terminar com `ok` na parte das regras e na do método. Com este kit em `../trilha-ai` (ou em `TRILHA_AI`), ele confere também que a pasta `trilha/` é cópia idêntica da daqui; sem ele, avisa.
6. **Primeiro commit,** com a linha de coautoria da IA, **e o repositório no GitHub:** `gh repo create <nome> --private --source . --push` cria o repositório privado, liga-o como `origin` e envia o primeiro commit. Na conta gratuita, o merge só com a verificação verde é regra do método; com o GitHub Pro (ou num repositório público), ligue também a proteção da main, exigindo o check `verificar`, mas deixe o dono passar por ela: o trabalho fora de change (PRD, TDD, decomposição) e o fechamento de cada change vão direto à main.
7. **Siga para a etapa 1 do guia:** o PRD.

## Os arquivos de regras

O Claude Code lê o `CLAUDE.md` da raiz de cada repositório. No método, as regras se dividem em dois arquivos, para que as comuns fiquem num lugar só e o `CLAUDE.md` de cada projeto fique curto:

| Arquivo | Vale para | Papel |
|---|---|---|
| `modelo/trilha/CLAUDE-comum.md` | todo projeto do método, na pasta `trilha/`, copiado sem mudar | as regras do método, iguais em todo projeto |
| `modelo/esqueleto-CLAUDE.md` | todo projeto novo, copiado como `CLAUDE.md` | o modelo do que é só daquele projeto (o que ele é, os documentos, os comandos, as armadilhas, as exceções ao comum); já traz a linha `@trilha/CLAUDE-comum.md`, que faz o Claude ler o comum |
| `CLAUDE.md` deste repositório | só este repositório | as regras de manutenção do kit; não importa o comum nem serve de modelo, porque este repositório não é um projeto do método |

## Ao mudar o padrão

O `CLAUDE-comum.md` muda **aqui**, em `modelo/trilha/`, com a versão e a data novas (que o plugin `sdd` acompanha), o teste verde (`python3 -m unittest discover -s testes`) e a tag `vX.Y`, e só depois são copiados para cada repositório, cada um sob ordem do usuário. Um repositório nunca edita a própria cópia: o que é dele vai no `CLAUDE.md`, em "Exceções ao comum" se contrariar o comum. O `confere_regras.py --fonte` acusa a cópia divergente.

Para atualizar um projeto: `python3 ferramentas/kit.py atualizar ../<projeto>`. Ela recusa o projeto com trabalho não commitado, fora da branch principal ou com o `ANDAMENTO.md` "em andamento"; deixa a pasta `trilha/` igual à do kit (num projeto de antes da 2.0, migra para ela as cópias soltas, a importação do comum, as travas e a parte fixa do `check.sh`), cria do modelo só o que faltar, avisa o que o kit mudou desde a versão do projeto na parte fixa do CI, do Dependabot, do `.gitignore` e do `check.sh` (a cópia dessas linhas fica com você), gera de novo a página, roda a conferência e sugere a mensagem do commit. Não faz commit nem envia. O que mudou desde a versão do projeto: `git diff v<versão do projeto> v<versão nova>`.
