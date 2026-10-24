# Plano: Heimdall, Xavier e HubIA na versão atual do kit

De 2026-10-16, com a ordem pedida então: Heimdall, depois Xavier, depois HubIA. Até a etapa 6, é o histórico; a etapa 7 (os dados pessoais) segue aberta, e a ordem que vale agora é a da [fila de 2026-10-24](#a-fila-de-2026-10-24-a-que-vale-agora). Cada repositório só muda sob ordem do usuário nomeando-o; cada envio ao GitHub, só com "sim".

## Onde cada um estava em 2026-10-16

| Repositório | Comum | Formato | Situação |
|---|---|---|---|
| Heimdall | 1.30 | antigo (comum na raiz, `scripts/`, `.githooks/`) | envio barrado hoje: o teste que compara o comum com os vizinhos reprova o HubIA, que já migrou |
| Xavier | 1.30 | antigo | não está de acordo (`docs/validacao-trilha-ai.md`, commit `c46b6ec`, não enviado) |
| HubIA | 2.5 | atual | de acordo, com pendências; uma delas grave: dados pessoais no git (`docs/validacao-trilha-ai.md`, sem commit) |

## O que os ensaios mostraram

Rodei o `kit.py atualizar` em clones descartáveis do Heimdall e do Xavier. A ferramenta funciona nos dois (código 0, `check.sh` com código 0). Dois pontos do Heimdall, porém, quebram e decidem a ordem:

1. **O `pre-push` do Heimdall deixa de rodar.** A migração põe o `core.hooksPath` em `trilha/hooks`, que só tem o `pre-commit`. Hoje o `.githooks/pre-push` é a única verificação a cada envio do Heimdall: o encoding, o `openspec validate --specs` e os testes pareados (o GitHub Actions dele está desligado por custo). Ele é exigido pelo spec `dev-scripts` ("Push verificado na máquina do desenvolvedor") e pelo ADR-011. A ferramenta só avisa: `.githooks/pre-push não roda mais`. Migrar o Heimdall na 2.5 desligaria essa proteção em silêncio. Por isso o kit muda antes (etapa 1).
2. **O Heimdall reprova citação de arquivo que não existe** (`teste-referencias.sh`, no `pre-push`), inclusive no registro de processo. Depois da cópia, oito citações aos arquivos antigos ficam quebradas: sete em `docs/2026-10-12-processo-desenvolvimento-assistido.md` e uma em `docs/README.md`. O próprio verificador prevê a saída: a marca `<!-- ref-externa -->` na linha que cita algo removido.

O Xavier e o HubIA não têm hook próprio nem conferem citações; neles, a cópia não quebra nada.

## A ordem

| Etapa | Onde | O quê | Change? |
|---|---|---|---|
| 0 | Heimdall | destravar o envio de hoje (feita em 2026-10-18, `b2d28f9`) | não: ajuste de teste e documentação |
| 1 | kit | o `pre-push` próprio do projeto pela `trilha/hooks` (versão 2.6; feita em 2026-10-18, PR #8, tag `v2.6`) | sim, a change 08 do kit |
| 2 | Heimdall | a cópia do kit 2.6 e os ajustes (feita em 2026-10-18, `298378f` e `08632cb`) | não: a cópia do kit dispensa change |
| 3 | Heimdall | o spec `dev-scripts` e os scripts com a trava em `trilha/hooks` (feita: change 09 do Heimdall, PR #7) | sim, uma change do Heimdall |
| 4 | Xavier | a cópia do kit 2.6 e os ajustes (feita em 2026-10-19, `37f7852` e `9435ee4`) | não |
| 5 | modelo-interface-heimdall | a cópia do kit 2.6, a evidência do TDD e o guia do derivado (feita em 2026-10-19, `5aa02ff`, `af572da` e `d88461b`, o CI por chave de implantação) | não (acrescentada em 2026-10-19, a pedido do usuário) |
| 6 | HubIA | a cópia do kit 2.6 e as pendências do relatório (feita em 2026-10-19, `468576c`, `bbd71a7` e `b24802a`) | não |
| 7 | os quatro | os dados pessoais: decidir o que fazer | a decidir |

**Os dados pessoais ficam para o fim (decisão do usuário, 2026-10-16).** Só se tratam depois das etapas 0 a 6. Até lá, só se anota quem os tem, na etapa 7.

## Em todas as etapas

- **Antes:**
  - o repositório na branch principal atualizada, sem nada por commitar e com o `ANDAMENTO.md` em "nada em andamento";
  - o kit atualizado (`git -C /home/pl/projetos/trilha-ai pull --tags`);
  - o ensaio num clone descartável, quando a etapa muda arquivos do método;
  - a linha de base dos testes do código, anotada (o que passou, falhou e foi pulado), para comparar no fim.
- **Prova de que o código não quebrou:**
  - `git diff --stat <antes>..HEAD` sem nenhum arquivo de código da aplicação;
  - os mesmos testes, com o mesmo resumo da linha de base;
  - `bash scripts/check.sh`, rodado sozinho, com código 0.
- **Commits:** a cópia da ferramenta num commit e os ajustes à mão em outro, para cada um se desfazer sozinho.
- **Como voltar:**
  - antes do envio: `git reset --hard <antes>` e o `core.hooksPath` de volta ao valor anterior (ele fica na configuração do clone, fora do commit);
  - depois do envio: `git revert` dos commits, em ordem inversa. Nunca envio forçado.

## Etapa 0. Heimdall: destravar o envio

**Objetivo:** o `pre-push` do Heimdall volta a passar. Hoje ele reprova porque o `teste-claude-comum.sh` compara o comum do Heimdall com o dos vizinhos ao lado, e o HubIA já não tem o comum na raiz. Isso independe da migração e pode ser feito já.

**Por que apagar, e não adaptar:**
- Nada fora do teste usa o `scripts/lib/claude-comum.sh`.
- O que ele confere no próprio repositório (a importação, a regra repetida, as 200 linhas) o `confere_regras.py` do kit já confere.
- Desde a 2.4, cada vizinho é comparado com o kit pela própria versão, no `check.sh` dele.
- A comparação direta entre vizinhos é justamente o que quebra quando eles estão em versões diferentes.

**Passos (na `master`):**
1. `git rm scripts/lib/claude-comum.sh scripts/tests/teste-claude-comum.sh`.
2. `CLAUDE.md`, linha 3: sai a frase sobre o `claude-comum.sh`.
3. `CLAUDE.md`, linha 101: sai a exceção "Verificação das regras"; fica só o `confere_regras.py` do kit.
4. `docs/2026-10-12-processo-desenvolvimento-assistido.md`, linhas 54, 74 e 75: a marca `<!-- ref-externa -->` no fim de cada linha, que cita algo removido.
5. Uma seção nova no mesmo registro de processo, com o prompt literal.

**Conferir (ensaiado num clone):**
- `bash scripts/local-011-test-scripts.sh`: sem o passo 4, o `teste-referencias.sh` reprova as cinco citações ao arquivo apagado; com ele, passa. No clone, o `teste-modo-borda.sh` reprovou só pela falta do `.env`, que fica fora do git e existe no repositório real.
- `bash scripts/check.sh`: código 0.

**Commit:** `test(scripts): sai a conferência do comum nos vizinhos, que o kit já faz em cada um`. Pela regra do comum, ajuste de teste e documentação dispensam change; é a minha leitura, e a decisão é do usuário. Envio com "sim": o próprio `pre-push` passa a ser a prova.

## Etapa 1. Kit: a change 08, o `pre-push` próprio do projeto

Segue o ciclo do kit (`CLAUDE.md` do kit), da descrição aprovada ao merge e à tag `v2.6`.

**Descrição curta para aprovar:**
- **Origem:** o Heimdall tem um `.githooks/pre-push` próprio, exigido pelo spec `dev-scripts` e pelo ADR-011, que é a única verificação a cada envio dele. A migração ao formato 2.0 põe o `core.hooksPath` em `trilha/hooks`, que só tem o `pre-commit`; o hook próprio deixa de rodar, e o `kit.py atualizar` só avisa.
- **Comportamento esperado:**
  - um `trilha/hooks/pre-push` roda o `.githooks/pre-push` do projeto quando ele existe, com os mesmos argumentos e a mesma entrada, e devolve o código de saída dele; sem ele, sai com 0;
  - a migração mantém o `.githooks/pre-push` e deixa de avisar que ele não roda;
  - o comum ganha meia frase: o hook de envio próprio do projeto fica em `.githooks/pre-push` e roda pela `trilha/hooks`.
- **Fica fora:**
  - outros hooks próprios (`pre-commit` e `commit-msg` do projeto), sem caso real hoje;
  - qualquer mudança no `guarda.py`, que já barra trocar o `core.hooksPath`.

**Resultado:** a versão 2.6, com a tag `v2.6` enviada. Só depois disso a etapa 2.

## Etapa 2. Heimdall: a cópia do kit 2.6

**Passos (na `master`):**
1. Do kit: `python3 ferramentas/kit.py atualizar /home/pl/projetos/heimdall`. Com a 2.6, o aviso sobre o `.githooks/pre-push` some.
2. O `sdd/padroes-tecnicos.md` que a ferramenta cria: recomendo apagá-lo. O Heimdall já tem o TDD aprovado, e os padrões de partida só serviriam a um TDD novo.
3. No Heimdall: `claude plugin install sdd@trilha-ai --scope project`.
4. Commit 1, com a mensagem que a ferramenta sugere: `chore(metodo): cópia do kit Trilha AI, comum 1.30 → 2.6`.
5. **Ajustes à mão (commit 2):**
   - `docs/2026-10-12-processo-desenvolvimento-assistido.md`, linhas 175, 177, 583 e 617: a marca `<!-- ref-externa -->`; são as sete citações aos arquivos que saíram;
   - `docs/README.md`, linha 11: o link passa a `../trilha/CLAUDE-comum.md`;
   - `scripts/README.md`, linha 31: os arquivos do kit ficam em `trilha/`;
   - `scripts/local-012-confere-metodo.sh`, linha 13: `scripts/confere_metodo.py` passa a `trilha/confere_metodo.py`; sem isso, o script quebra (ensaiado);
   - `.github/workflows/verificacao.yml`: sai o passo "Os specs e as changes do OpenSpec", porque o `trilha/verifica.sh` já valida os specs e as changes; é o aviso da ferramenta;
   - `openspec/config.yaml`: a ferramenta avisa que as regras são próprias. Comparar com o `modelo/openspec/config.yaml` e trazer só a língua no `context` e o `operations.apply`, se faltarem;
   - o aviso novo da conferência das regras, visto no ensaio da 2.6: "há TDD, e a parte da stack ainda é a do modelo em `.github/workflows/verificacao.yml`". Decidir com o usuário se a stack do Heimdall entra no CI ou se a exceção do CI leve, no `CLAUDE.md`, cobre o caso;
   - o registro de processo, com o prompt literal.
   
   Os ajustes de documentação dispensam change. O do `local-012` e o do CI devolvem o mesmo efeito de antes, então valem como refatoração sem efeito. Também aqui a leitura é minha, e a decisão é do usuário.
6. **Conferir:**
   - `bash scripts/check.sh`;
   - `bash scripts/local-011-test-scripts.sh` (com o `teste-referencias.sh` verde);
   - `git config core.hooksPath` dá `trilha/hooks`;
   - `bash scripts/local-012-confere-metodo.sh`;
   - o gate do `scripts/azure-004-publish.sh` não muda, mas o pytest, o mypy e o ruff do núcleo entram na linha de base e na prova final.
7. Envio com "sim": o `pre-push`, agora chamado pela `trilha/hooks/pre-push`, roda o encoding, os specs e os testes pareados. **Ver isso acontecer no envio é a prova da etapa 1.**

**Ensaiado na 2.6 (change 08, 2026-10-18):** com a cópia num commit e as oito citações marcadas noutro, o envio a um remoto local passou pelo `trilha/hooks/pre-push`, com os 22 testes pareados verdes. Com a cópia sem commit, o `teste-modos.sh` e o `teste-referencias.sh` reprovam, porque leem o índice do git: o commit da cópia vem antes de qualquer envio.

**Ensaiado na 2.5:**
- `check.sh` com código 0 e 36 specs válidos;
- o `teste-common.sh` e o `teste-pre-push.sh` verdes;
- o `teste-referencias.sh` com as oito citações acima;
- o `local-012` quebrado.

## Etapa 3. Heimdall: a change da trava em `trilha/hooks`

**Andamento (2026-10-18):** a decomposição 1.9 do Heimdall (`47600ec`) pôs esta change como a 09, `hooks-ativados-pela-trilha`, antes da divisão dos requisitos, com o briefing aprovado. O propose em diante vai numa sessão aberta no Heimdall, onde valem a trava `trilha/guarda.py` e o plugin 2.6; o `ANDAMENTO.md` dele traz o próximo passo.

Uma change do Heimdall, no ciclo do comum, porque muda requisito: o spec `dev-scripts`, requisito "Push verificado na máquina do desenvolvedor".

**Descrição curta para aprovar:**
- **Origem:** o ADR-011 e a migração ao kit 2.6. O hook de envio continua versionado em `.githooks/pre-push`, mas é ativado pelo `core.hooksPath` em `trilha/hooks`, cujo `pre-push` o chama.
- **Comportamento esperado:**
  - o `local-005` e o `local-006` (`ensure_git_hooks`, em `scripts/lib/common.sh`) apontam o `core.hooksPath` para `trilha/hooks` quando não há valor configurado;
  - um valor `.githooks` antigo também passa a `trilha/hooks`, com aviso; outro valor é mantido, com aviso;
  - o `teste-common.sh` acompanha;
  - o `README.md`, linha 50, passa a dizer `git config core.hooksPath trilha/hooks`.
- **Fica fora:** o conteúdo do `pre-push`, que não muda.

Até essa change, o `local-005` e o `local-006` avisam, sem razão, que o hook "não está ativo". O valor é mantido, então nada quebra; é só ruído.

## Etapa 4. Xavier: a cópia do kit 2.6

**Ensaiado na 2.5:** código 0, e o `check.sh` do clone migrado deu código 0, com 45 specs e changes válidas. Nada em `src/`, `apps/`, `tests/`, `Makefile`, `pyproject.toml` ou `uv.lock` muda.

**Passos (na `main`):**
1. Linha de base: `make test-fast` (com o Tesseract) e a suíte pytest de `apps/plataforma-web/tests/` (confira no resumo se a integração virou `skip` por falta do Postgres).
2. Do kit: `python3 ferramentas/kit.py atualizar /home/pl/projetos/xavier`. A ferramenta:
   - tira o comum da raiz, os cinco `scripts/` antigos e o `.githooks/`;
   - cria a `trilha/`;
   - troca a importação no `CLAUDE.md`;
   - troca a parte fixa do `check.sh` por `bash trilha/verifica.sh`, com os `--vizinho`;
   - aponta o hook do `.claude/settings.json` para `trilha/guarda.py` e declara o plugin;
   - põe o `core.hooksPath` em `trilha/hooks`.
3. Apagar o `sdd/padroes-tecnicos.md`, pelo mesmo motivo do Heimdall. Depois, `claude plugin install sdd@trilha-ai --scope project`.
4. Commit 1: `chore(metodo): cópia do kit Trilha AI, comum 1.30 → 2.6`.
5. **Ajustes à mão (commit 2):**
   - `scripts/check.sh`: sai a última linha, `uv run openspec validate --specs`, que repete o que o `trilha/verifica.sh` já faz;
   - CI: sai o passo "Os specs e as changes do OpenSpec" e o `setup-uv`, que só servia àquela linha;
   - `openspec/config.yaml`: entram a língua no topo do `context`, o `operations.apply` e as duas frases novas do `archive`, do modelo do kit. As regras por artefato ficam as do Xavier: as do kit pedem o código do RF e do CA do PRD, e o PRD do Xavier é histórico. Adotá-las é decisão para quando houver PRD novo;
   - caminhos: `AGENTS.md` (linhas 515 e 627), `README.md` (661 e 718) e `docs/001-guia-de-leitura.md` (14) passam a citar `trilha/CLAUDE-comum.md`;
   - `CLAUDE.md`: a linha 3 e a linha "Regras, método e specs" de **Testar** descrevem o `trilha/verifica.sh`;
   - o registro em `docs/018-processo-desenvolvimento-assistido.md`, com o prompt literal.
6. Prova:
   - o mesmo resumo da linha de base;
   - `TRILHA_AI=/nao-existe bash scripts/check.sh` com código 0, que é o caminho do CI;
   - numa sessão nova do Claude Code no Xavier, o `/sdd:` lista as skills e `git commit --no-verify` é barrado.
7. Envio com "sim" e `gh run watch` até o CI ficar verde. Vão juntos o commit do relatório (`c46b6ec`) e os dois da migração.

## Etapa 5. modelo-interface-heimdall: a cópia do kit 2.6

Acrescentada em 2026-10-19, a pedido do usuário. Ensaiada num clone: a cópia sai com código 1, porque a evidência do ADR-010 no TDD (linha 95) cita `scripts/confere_metodo.py`; com a referência corrigida, as conferências passam. A ferramenta atualiza sozinha as regras do `openspec/config.yaml` (eram as do kit) e acrescenta a língua.

- **Ajustes à mão (commit 2):** o TDD (linhas 94 e 95; a 215 é histórico), o `CLAUDE.md` (34) e o `README.md` (85, 89, 269 e 275, a seção do derivado) citam a pasta `trilha/`; sai a linha `openspec validate --specs` do `check.sh`; no CI, sai só o passo do OpenSpec (a stack fica); o registro `docs/002` e o `ANDAMENTO.md`.
- **Andamento (2026-10-19):** cópia e ajustes enviados (`5aa02ff`, `af572da`), com os testes iguais aos de antes. O CI falha porque o repositório não tem o segredo `HEIMDALL_LEITURA` (falhava assim desde 2026-10-15): resolvido com uma chave de implantação só de leitura no `paulosrl/heimdall` e o segredo `HEIMDALL_LEITURA_SSH` (`d88461b`); verificação verde.
- **Cuidado:** o compose tem o nome fixo `layout-padrao`; a bateria (`testa-layout.sh --sem-e2e`, no `check.sh`) roda só no repositório real, nunca num clone.

## Etapa 6. HubIA: a cópia do kit 2.6 e as pendências

O HubIA já está no formato atual. A cópia da 2.6 só troca a `trilha/`, e ele não tem `.githooks/pre-push`. Os dados pessoais dele ficam para a etapa 7.

1. A cópia: `python3 ferramentas/kit.py atualizar /home/pl/projetos/hubia` e o commit sugerido.
2. **Pequenos ajustes de texto:**
   - o PRD ganha a linha `**Status:**`;
   - saem do `openspec/config.yaml` as duas regras que repetem as convenções do `context` (a do `proposal` e a do `tasks`).
3. **Ficam para depois, e não são migração:**
   - a decomposição, pela skill `sdd:briefing`, antes da próxima change nova;
   - os requisitos com mais de 500 caracteres, enxugados quando cada spec mudar.
   
   Os dois já estão no `ANDAMENTO.md` do HubIA.
4. O relatório `docs/validacao-trilha-ai.md` do HubIA, ainda sem commit, entra no primeiro commit desta etapa.

## Etapa 7. Os dados pessoais (no fim de tudo)

Só depois das etapas 0 a 6, já feitas. Aqui, o que já se sabe; a decisão do que fazer é do usuário, nesta etapa.

| Repositório | Situação | Achado |
|---|---|---|
| HubIA | **tem dados pessoais no git** | `prompts-importados/064-PRM-20260520-68369-autorelatormp.md`: dados reais de um inquérito policial (nomes, CPF, nascimento e endereços de vítima, investigado e testemunha), no git desde o `e027e0c` e já no GitHub (repositório privado); conferido: está no git e tem dois CPFs. `autores.csv` e `autresoriginais.csv`: nomes e e-mails de servidores; `afazer.txt` na raiz (os três já anotados no `ANDAMENTO.md` do HubIA). |
| Xavier | nada achado | busca de 2026-10-16: nenhum `.env`, chave, PDF, CSV nem `entrada/`, `saida*/` e `logs/` no git, e nenhuma chave, token ou CPF pelo `git grep`. Só os `.env.example`, com senhas de exemplo, e a senha do usuário de teste do e2e. |
| Heimdall | **tem dados pessoais no git** | levantamento de 2026-10-21: nome completo e e-mail de dois colegas no `infra/azure/staging.admins.txt` (apagado, mas no histórico) e do usuário no `infra/azure/producao.admins.txt`; o e-mail pessoal do usuário no CHANGELOG e num doc. Os outros e-mails @mppa são de teste. |
| modelo-interface-heimdall | nada achado | levantamento de 2026-10-21: nada, nem no histórico. |

As opções para levar à decisão do usuário:
- trocar os dados por marcadores (`[NOME]`, `[CPF]`), como nos outros prompts do HubIA;
- ou tirar os arquivos do git (`git rm --cached`) e mandá-los para uma pasta ignorada;
- e acrescentar uma regra ao "Dados a proteger" do `CLAUDE.md` de cada repositório afetado.

Apagar os dados do histórico pede reescrever a história e enviar com força. O método nunca faz isso, e o `guarda.py` barra; se o usuário escolher esse caminho, ele faz isso por fora (`git filter-repo`), sabendo que os clones guardam a cópia antiga.

## A fila de 2026-10-24 (a que vale agora)

O kit foi à 2.18 (o OpenSpec 1.15.0, o `kit.py atualizar --openspec`, os requisitos curtos e o aviso do resumo sem a raiz). O Xavier e o Heimdall estão na 2.15 (`760574a` e `1fd4cc5`, de 2026-10-23), o HubIA na 2.12, e os três fixam o OpenSpec 1.14.1 no CI. A atualização é um a um, e cada um só começa quando o usuário o nomear:

1. Xavier;
2. Heimdall;
3. HubIA.

O comando de cada um, rodado da raiz do kit, com o nome da pasta em minúsculas: `python3 ferramentas/kit.py atualizar ../xavier --openspec` (e `../heimdall`, `../hubia`).

- **Antes:** o projeto na branch principal, sem nada por commitar (o `docs/validacao-trilha-ai.md` da validação, com commit ou descartado) e com o "Estado" do `ANDAMENTO.md` em "nada em andamento"; fora disso (com trabalho por commitar, noutra branch ou "em andamento"), o comando recusa sem mudar nada. Confira na hora (`git status -sb` e o `ANDAMENTO.md`): os projetos seguem com as changes deles, e o estado muda de um dia para o outro.
- **O que ele faz:** copia o kit; põe o OpenSpec da máquina na versão do kit, pelo `npm install -g`, quando ela é outra (vale para todos os projetos, e não só para este; hoje a máquina já está na 1.15.0); e roda o `openspec update` no projeto, se o dry-run não listar arquivo dele a apagar.
- **Se o dry-run listar arquivos a apagar** (por exemplo, os de um workflow instalado que o perfil não tem; no HubIA, em 2026-10-24, os seis do `onboard`): o update não roda, o comando sai com 1 e a cópia fica sem commit; rodá-lo de novo é recusado, porque há trabalho não commitado. O perfil é da máquina (`openspec config path`), não do projeto, e a saída é escolha do usuário: deixar os arquivos saírem, ou pôr o workflow no perfil (`openspec config profile`, que pede o terminal do usuário; responda não a "Apply changes to this project now?", para o update esperar o passo 1), sabendo que o próximo `openspec update` dos outros projetos também o cria neles. Depois da escolha:
  1. ver o que o update faria, com `openspec update --dry-run --force --json` no projeto, que só lê e mostra também a limpeza do legado, que o dry-run do kit não lista;
  2. rodar `OPENSPEC_NO_UPDATE_CHECK=1 openspec update --force` no projeto: ele não pergunta nada, nem pede terminal, e faz o que o passo 1 mostrou, a limpeza do legado inclusive;
  3. rodar o `bash scripts/check.sh`, com código 0: as conferências do comando rodaram antes deste update, e o comando não valida os specs nem roda a parte da stack;
  4. fazer o commit, com a mensagem `chore(metodo): cópia do kit Trilha AI, comum <antes> → 2.18`.
- **O CI do projeto não muda:** a versão do OpenSpec no `.github/workflows/verificacao.yml` se troca à mão, num commit à parte, como os outros ajustes à mão; o comando avisa. Até lá, a conferência do método, que o próprio comando roda, avisa que a máquina e o CI divergem e sugere `npm install -g @fission-ai/openspec@1.14.1`: não rode, troque a versão no CI.
- **Nos que esperam a vez:** a máquina já está na 1.15.0, então o `check.sh` deles avisa que a máquina e o CI divergem e que o `openspec update` mudaria arquivos gerados. O aviso sugere voltar a máquina à 1.14.1: não volte, porque os já atualizados passariam a divergir e um `openspec update` neles geraria de novo os arquivos da 1.14.1. E não rode o `openspec update` neles antes da vez: ele geraria os arquivos da 1.15.0 com o CI ainda na 1.14.1. Os avisos somem quando cada um for atualizado, com o CI trocado, salvo se o perfil mudar depois: aí os já atualizados pedem um `openspec update` de novo.

O modelo-interface-heimdall fica fora, na 2.6, e a etapa 7 (os dados pessoais) continua como acima.
