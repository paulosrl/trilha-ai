# Trilha AI: o kit de partida de um repositório no método

Trilha AI é um método de desenvolvimento assistido por IA: PRD → TDD → OpenSpec, com o usuário aprovando em gates e cada cenário virando um teste. Este repositório é a fonte do padrão que todo repositório do método copia.

O percurso inteiro, estação por estação, com o que acontece no git e no GitHub em cada uma, está desenhado em `mapa-da-trilha.html`: abra-o no navegador. Ele explica o método e não se copia para os projetos.

Este repositório é a **fonte** dos arquivos que todo repositório novo copia: eles ficam na pasta `modelo/`, e só ela vai aos projetos. O `modelo/trilha/CLAUDE-comum.md` é a versão vigente do padrão (a linha "Versão" no topo dele diz qual). Os outros arquivos são esqueletos, com o que preencher entre `<` e `>`.

A ordem:

1. **Instale as ferramentas,** uma vez por máquina, em Linux ou WSL:
   - o **Claude Code**: `curl -fsSL https://claude.ai/install.sh | bash` (a documentação oficial, com os requisitos, está em https://code.claude.com/docs/en/setup);
   - o **OpenSpec**, com o Node 20.19 ou mais novo: `npm install -g @fission-ai/openspec@1.15.0`, a versão que a verificação do GitHub usa;
   - o **Python 3**, porque os verificadores de `trilha/` são programas Python sem dependências; no Ubuntu e no WSL ele costuma vir instalado: confira com `python3 --version`;
   - uma **conta no GitHub** e o GitHub CLI (`gh`, instalação em https://cli.github.com), autenticado uma vez com `gh auth login`: todo repositório do método tem um remoto privado no GitHub;
   - o marketplace do plugin `sdd`, publicado por este repositório: `claude plugin marketplace add paulosrl/trilha-ai`. O plugin vale por projeto e se instala no passo 4; o que ele faz está em `plugins/sdd/README.md`;
   - opcional, o **CodeGraph** (`npm install -g @colbymchenry/codegraph`), que dá ao Claude um índice do código; sem ele, o método funciona igual.
   - a **guarda das conversas** do Claude Code: ponha `"cleanupPeriodDays": 3650` no `~/.claude/settings.json`. Sem isso, o Claude Code apaga as conversas depois de 30 dias, e o `python3 trilha/tempo.py` perde a hora exata dos dias apagados que ainda não estavam no resumo dele.
2. **Crie o repositório com o kit:** com este repositório em `../trilha-ai`, rode `python3 ../trilha-ai/ferramentas/kit.py novo <nome>`. Ele cria a pasta, o git (na branch `main`) e a pasta `sdd/`, copia os arquivos, como na tabela do passo 3, e imprime os próximos passos.
3. **Preencha o que é do projeto.** A tabela diz o que cada arquivo de `modelo/` é e o que fazer com ele; a cópia à mão, sem a ferramenta, segue a mesma tabela. O resto deste repositório é só do kit e não se copia:

   | Arquivo | O que fazer |
   |---|---|
   | `trilha/` | copiar a pasta inteira **sem mudar nada**: o comum, os verificadores, o `verifica.sh` (a parte fixa da verificação), o gerador da página, a trava do Claude Code (`guarda.py`), a do commit (`hooks/pre-commit`, ligada com `git config core.hooksPath trilha/hooks`, uma vez por clone), o `hooks/pre-push`, que roda a cada envio o `.githooks/pre-push` do projeto, quando ele existe, e o `tempo.py`, que o usuário roda quando quiser ver as horas de trabalho de cada dia (o resumo e a página dele ficam fora do repositório, em `~/.local/share/trilha-ai/tempo/`) |
   | `esqueleto-CLAUDE.md` | copiar como `CLAUDE.md`; preencher o que está entre `<` e `>`; apagar o que não se aplica |
   | `ANDAMENTO.md` | preencher a etapa e a hora; nasce "nada em andamento" |
   | `openspec/config.yaml` | preencher o contexto; as regras por artefato ficam como estão |
   | `scripts/check.sh` | a parte fixa (`bash trilha/verifica.sh`) já funciona; os repositórios ao lado entram nela, um `--vizinho` por nome; a parte da stack entra na change 01 |
   | `sdd/padroes-tecnicos.md` | copiar no mesmo caminho: os padrões técnicos de partida que a skill `sdd:tdd` lê; ajustá-los antes do TDD, ou apagar o arquivo, se o projeto não os quiser. Na pasta `sdd/` nascem também o PRD, o TDD, a decomposição e os briefings |
   | `.github/workflows/verificacao.yml` | copiar no mesmo caminho: a cada envio, o GitHub roda o `check.sh` (que inclui o `openspec validate`) e a busca de senhas e chaves no histórico (gitleaks); as ações vão fixadas pelo commit; a parte da stack entra na change 01 |
   | `.github/dependabot.yml` | copiar no mesmo caminho: o Dependabot (gratuito) abre um pull request a cada versão nova das ações e, depois da etapa 2, das dependências da stack |
   | `claude-settings.json` | copiar como `.claude/settings.json`, ou somar o que ele traz ao que já existir: liga o `trilha/guarda.py` e declara o plugin `sdd@trilha-ai` (`enabledPlugins`) e o marketplace dele (`extraKnownMarketplaces`) |
   | `gitignore` | copiar como `.gitignore`; apagar o bloco da stack que não for a sua, depois da etapa 2 |

4. **Inicialize as ferramentas no repositório.** Uma vez por máquina, antes: `openspec config profile` e marque também o `verify`, que o perfil padrão do OpenSpec não traz e o ciclo usa no passo 5, com a entrega em skills e comandos (`both`): só com comandos, o `openspec update` apaga as skills, e uma ferramenta que só as lê (o Codex) fica sem nada (num repositório já inicializado, rode depois `openspec update`; a conferência do método avisa o que ele mudaria). Então `openspec init` (ele mantém o `config.yaml` copiado; se perguntar, não o sobrescreva), `claude plugin install sdd@trilha-ai --scope project` e, se usar o CodeGraph, `codegraph init`, em cada clone, porque o índice fica fora do git. O `.claude/settings.json` declara o plugin, mas a instalação é de cada máquina, uma vez por projeto. Quem tem o plugin instalado para o usuário inteiro (como o kit ensinava até a 2.1) o tira com `claude plugin uninstall sdd@trilha-ai` depois que todos os projetos da máquina o declararem e o tiverem instalado assim; até lá, essa instalação continua valendo em todo repositório e pode ser a versão que a sessão carrega, mesmo num projeto com a sua (a conferência do método confere as duas).
5. **Confira:** `bash scripts/check.sh` deve terminar com `ok` na parte das regras e na do método. Com este kit em `../trilha-ai` (ou em `TRILHA_AI`), ele confere também que a pasta `trilha/` é igual à da versão do projeto aqui (a tag `vX.Y`, quando este kit já está noutra versão, que ele avisa); sem ele, avisa.
6. **Primeiro commit,** com a linha de coautoria da IA, **e o repositório no GitHub:** `gh repo create <nome> --private --source . --push` cria o repositório privado, liga-o como `origin` e envia o primeiro commit. Na conta gratuita, o merge só com a verificação verde é regra do método; com o GitHub Pro (ou num repositório público), ligue também a proteção da main, exigindo o check `verificar`, mas deixe o dono passar por ela: o trabalho fora de change (PRD, TDD, decomposição) e o fechamento de cada change vão direto à main.
7. **Comece pelo PRD:** peça ao Claude o PRD do produto; a skill `sdd:prd` conduz a conversa. O percurso inteiro, até a primeira change entregue, está no `mapa-da-trilha.html`.

## Os arquivos de regras

O Claude Code lê o `CLAUDE.md` da raiz de cada repositório. No método, as regras se dividem em dois arquivos, para que as comuns fiquem num lugar só e o `CLAUDE.md` de cada projeto fique curto:

| Arquivo | Vale para | Papel |
|---|---|---|
| `modelo/trilha/CLAUDE-comum.md` | todo projeto do método, na pasta `trilha/`, copiado sem mudar | as regras do método, iguais em todo projeto |
| `modelo/esqueleto-CLAUDE.md` | todo projeto novo, copiado como `CLAUDE.md` | o modelo do que é só daquele projeto (o que ele é, os documentos, os comandos, as armadilhas, as exceções ao comum); já traz a linha `@trilha/CLAUDE-comum.md`, que faz o Claude ler o comum |
| `CLAUDE.md` deste repositório | só este repositório | as regras de manutenção do kit; não importa o comum nem serve de modelo, porque este repositório não é um projeto do método |

As auditorias do kit, com o roteiro e o relatório de cada rodada, ficam em `docs/auditorias/` e não se copiam.

## Ao mudar o padrão

O `CLAUDE-comum.md` muda **aqui**, em `modelo/trilha/`, com a versão e a data novas (que o plugin `sdd` acompanha), o teste verde (`python3 -m unittest discover -s testes`) e a tag `vX.Y`, e só depois são copiados para cada repositório, cada um sob ordem do usuário. Um repositório nunca edita a própria cópia: o que é dele vai no `CLAUDE.md`, em "Exceções ao comum" se contrariar o comum. O `confere_regras.py --fonte` reprova a cópia que difere da versão do projeto e, desde a 2.4, só avisa quando o kit já está numa versão mais nova: o projeto atualiza quando o usuário mandar. Um projeto anterior à 2.4 traz a conferência antiga, que reprova com o kit à frente até a primeira atualização; para conferi-lo sem atualizar, ponha o kit na versão dele ao lado: `git -C ../trilha-ai worktree add /tmp/kit-vX.Y vX.Y` e `TRILHA_AI=/tmp/kit-vX.Y bash scripts/check.sh`.

Para atualizar um projeto: `python3 ferramentas/kit.py atualizar ../<projeto>`. Ela recusa o projeto com trabalho não commitado, fora da branch principal ou com o `ANDAMENTO.md` "em andamento"; deixa a pasta `trilha/` igual à do kit (num projeto de antes da 2.0, migra para ela as cópias soltas, a importação do comum, as travas e a parte fixa do `check.sh`), cria do modelo só o que faltar (os padrões técnicos, só num projeto de antes da 2.2), avisa o que o kit mudou desde a versão do projeto na parte fixa do CI, do Dependabot, do `.gitignore` e do `check.sh` (a cópia dessas linhas fica com você), gera de novo a página que já existir, roda a conferência e sugere a mensagem do commit. Não faz commit nem envia. Com `--openspec`, ela também põe o OpenSpec da máquina na versão do kit (`npm install -g`, só quando a da máquina é outra) e roda o dry-run do `openspec update` no projeto antes de mudar qualquer arquivo dele; o update roda depois da cópia. O que falha antes da cópia recusa com o projeto como estava; a recusa diz o que falhou, e basta corrigir e rodar de novo. Se o update fosse apagar algum arquivo do projeto (o perfil da máquina sem o que o projeto versiona), confira o perfil com `openspec config list` e rode de novo, ou acrescente `--aceitar-apagados` para deixar o update apagá-los. A máquina pode ficar na versão do kit mesmo com o projeto recusado. Num projeto sem a pasta `openspec/`, rode antes sem `--openspec` e faça o commit. Sem a opção, só avisa quando a versão da máquina difere da do kit. O que mudou desde a versão do projeto: `git diff v<versão do projeto> v<versão nova>`.
