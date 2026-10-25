# conferencias Specification

## Purpose

Define o que os verificadores que os projetos copiam do kit conferem e avisam antes do commit e no CI, para que um documento ou uma instalação fora do método seja apontado sem depender da máquina de quem o escreveu.

## Requirements

### Requirement: Plugin instalado lido pelo Claude Code
A conferência do método SHALL ler o plugin `sdd` instalado pela lista de plugins do próprio Claude Code (`claude plugin list --json`) e MUST NOT depender de outra pasta ao lado do projeto nem de arquivos internos do Claude Code.

#### Scenario: Pasta vizinha com outra versão
- **WHEN** existe, ao lado do projeto, uma pasta `pipeline-prd-tdd-openspec` com outra versão do plugin
- **THEN** o resultado da conferência é o mesmo que sem essa pasta

### Requirement: Aviso do plugin de fora do kit
Quando um plugin `sdd@…` instalado não for `sdd@trilha-ai` (o do marketplace antigo ou o de qualquer outro), a conferência do método SHALL avisar, nomeando-o, e mostrar como trocar para `sdd@trilha-ai`, com cada comando separado, sem falhar.

#### Scenario: Plugin do marketplace antigo
- **WHEN** a lista de plugins do Claude Code traz `sdd@pipeline-prd-tdd-openspec`
- **THEN** a conferência imprime um aviso com `claude plugin install sdd@trilha-ai`
- **AND** termina com o código de saída 0

#### Scenario: Plugin de outro marketplace
- **WHEN** a lista de plugins do Claude Code traz só `sdd@meu-fork`
- **THEN** a conferência imprime um aviso que cita `sdd@meu-fork` e `claude plugin install sdd@trilha-ai`
- **AND** termina com o código de saída 0

#### Scenario: Comandos separados
- **WHEN** a conferência avisa sobre o plugin de fora do kit ou ausente
- **THEN** `claude plugin marketplace add paulosrl/trilha-ai` e `claude plugin install sdd@trilha-ai` aparecem como comandos separados, nunca ligados por `&&`, para que o install rode mesmo se o marketplace já existir

### Requirement: Aviso do plugin desligado
Quando o `sdd@trilha-ai` estiver instalado e desligado na pasta do projeto, a conferência do método SHALL avisar uma vez só, com o comando `claude plugin enable sdd@trilha-ai --scope <escopo>` no escopo da configuração que o desliga, sem falhar. O escopo SHALL vir da configuração que vale na pasta: a local (`.claude/settings.local.json`), que prevalece, a do projeto (`.claude/settings.json`) e, sem declaração nelas, a do usuário, pelo "ligado" da lista.

#### Scenario: Plugin do kit desligado
- **WHEN** a lista de plugins do Claude Code traz `sdd@trilha-ai` na versão do comum, com `enabled` falso, e o projeto não declara o plugin
- **THEN** a conferência imprime um aviso com `claude plugin enable sdd@trilha-ai --scope user`
- **AND** termina com o código de saída 0

#### Scenario: Plugin desligado pelo projeto
- **WHEN** o `.claude/settings.json` do projeto tem `sdd@trilha-ai` falso e a lista traz a instalação do usuário e a do projeto, esta com `enabled` verdadeiro
- **THEN** a conferência imprime um só aviso de desligado, com `claude plugin enable sdd@trilha-ai --scope project`

#### Scenario: Plugin desligado pela configuração local
- **WHEN** o `.claude/settings.local.json` do projeto tem `sdd@trilha-ai` falso
- **THEN** a conferência imprime um aviso com `claude plugin enable sdd@trilha-ai --scope local`

#### Scenario: Configuração local liga o que o projeto desliga
- **WHEN** o `.claude/settings.json` do projeto tem `sdd@trilha-ai` falso e o `.claude/settings.local.json` o tem verdadeiro
- **THEN** a conferência não imprime aviso de desligado

### Requirement: Conferência do plugin fora da trava do commit
A trava do commit SHALL rodar a conferência do método sem consultar o Claude Code, para continuar rápida; o aviso do plugin MUST continuar na verificação do repositório (`scripts/check.sh`), que o método manda rodar antes do commit.

#### Scenario: Commit sem consultar o Claude Code
- **WHEN** a trava do commit roda num projeto feito do kit, numa máquina com o Claude Code
- **THEN** a lista de plugins do Claude Code não é consultada

#### Scenario: Verificação do repositório com o aviso
- **WHEN** o `scripts/check.sh` roda numa máquina com o plugin de fora do kit
- **THEN** o aviso do plugin aparece

### Requirement: Aviso da versão do plugin diferente da do projeto
Quando a versão do `sdd@trilha-ai` instalado não for `X.Y.0` para a "Versão X.Y" do `CLAUDE-comum.md` do projeto, a conferência do método SHALL avisar, nomeando as duas versões, sem falhar.

#### Scenario: Versões diferentes
- **WHEN** o comum do projeto diz "Versão 1.35" e o plugin instalado é `sdd@trilha-ai` na versão `1.34.0`
- **THEN** a conferência imprime um aviso que cita `1.34.0` e `1.35`
- **AND** termina com o código de saída 0

#### Scenario: Versões iguais
- **WHEN** o comum do projeto diz "Versão 1.35" e o plugin instalado é `sdd@trilha-ai` na versão `1.35.0`
- **THEN** a conferência não imprime aviso sobre o plugin

### Requirement: Aviso do plugin ausente
Quando o Claude Code responder e nenhum plugin `sdd` valer no projeto, a conferência do método SHALL avisar, com o comando de instalação no projeto (`claude plugin install sdd@trilha-ai --scope project`), sem falhar.

#### Scenario: Claude Code sem o plugin
- **WHEN** a lista de plugins do Claude Code não traz nenhum `sdd@…`
- **THEN** a conferência imprime um aviso com `claude plugin install sdd@trilha-ai --scope project`
- **AND** termina com o código de saída 0

#### Scenario: Plugin instalado só para outro projeto
- **WHEN** a lista de plugins do Claude Code traz o `sdd@trilha-ai` só com o escopo `project`, na pasta de outro projeto
- **THEN** a conferência imprime um aviso com `claude plugin install sdd@trilha-ai --scope project`
- **AND** termina com o código de saída 0

### Requirement: Silêncio sem o Claude Code
Quando o Claude Code não estiver disponível, ou a lista de plugins falhar ou não responder no prazo (10 segundos), a conferência do método SHALL seguir sem aviso nem falha sobre o plugin, como no CI.

#### Scenario: Máquina sem o Claude Code
- **WHEN** o comando `claude` não existe no PATH
- **THEN** a conferência não imprime aviso sobre o plugin
- **AND** o código de saída não muda por causa do plugin

#### Scenario: Lista de plugins com erro
- **WHEN** `claude plugin list --json` termina com erro ou devolve um texto que não é JSON
- **THEN** a conferência não imprime aviso sobre o plugin
- **AND** o código de saída não muda por causa do plugin

#### Scenario: Lista de plugins sem resposta no prazo
- **WHEN** `claude plugin list --json` não termina dentro do prazo
- **THEN** a conferência segue sem esperar mais, sem imprimir aviso sobre o plugin
- **AND** o código de saída não muda por causa do plugin

### Requirement: Comum importado da pasta do método
A conferência das regras SHALL exigir que o `CLAUDE.md` do projeto importe o comum pela linha `@trilha-ai/CLAUDE-comum.md` e que o comum exista em `trilha-ai/CLAUDE-comum.md`, reprovando, com o motivo, o projeto que não cumprir.

#### Scenario: Projeto no layout da pasta do método
- **WHEN** a conferência das regras roda num projeto feito do kit, com `trilha-ai/CLAUDE-comum.md` e o `CLAUDE.md` importando `@trilha-ai/CLAUDE-comum.md`
- **THEN** ela termina com o código de saída 0

#### Scenario: Importação antiga
- **WHEN** o `CLAUDE.md` importa `@CLAUDE-comum.md` em vez de `@trilha-ai/CLAUDE-comum.md`
- **THEN** a conferência das regras reprova, citando a linha que falta

### Requirement: Cópia idêntica da pasta do método
Com a pasta do kit indicada, a conferência das regras SHALL comparar a pasta `trilha-ai/` do projeto com a `modelo/trilha-ai/` (a `modelo/trilha/` nas tags de antes da 2.19) da versão do projeto (a linha "Versão X.Y" do `trilha-ai/CLAUDE-comum.md`): a cópia de trabalho do kit, na mesma versão ou sem a linha no projeto; a tag `vX.Y` do kit, noutra. Ela MUST reprovar, nomeando o arquivo e mandando rodar o `kit.py atualizar`, o arquivo diferente, faltando, a mais ou sem a permissão de execução, e a versão que um kit com as tags não tem.

#### Scenario: Pasta igual à do kit
- **WHEN** a pasta `trilha-ai/` do projeto tem os mesmos arquivos, com o mesmo conteúdo, que a `modelo/trilha-ai/` do kit
- **THEN** a conferência das regras não reprova pela cópia

#### Scenario: Trava editada no projeto
- **WHEN** o `trilha-ai/guarda.py` do projeto difere do kit
- **THEN** a conferência das regras reprova, citando `trilha-ai/guarda.py`
- **AND** a mensagem manda rodar o `kit.py atualizar`, e não editar a pasta

#### Scenario: Arquivo faltando ou a mais
- **WHEN** falta no projeto um arquivo que a pasta do kit tem, ou o projeto tem em `trilha-ai/` um arquivo que o kit não tem
- **THEN** a conferência das regras reprova, citando o arquivo

#### Scenario: Permissão de execução perdida
- **WHEN** o `trilha-ai/hooks/pre-commit` do projeto tem o mesmo conteúdo do kit, mas sem a permissão de execução
- **THEN** a conferência das regras reprova, citando `trilha-ai/hooks/pre-commit`

#### Scenario: Kit numa versão mais nova
- **WHEN** a cópia de trabalho do kit está numa versão mais nova que a do projeto, o kit tem a tag da versão do projeto, e a pasta `trilha-ai/` do projeto é igual à `modelo/trilha-ai/` dessa tag
- **THEN** a conferência das regras não reprova pela cópia
- **AND** avisa, citando as duas versões e o `kit.py atualizar`

#### Scenario: Cópia divergente com o kit mais novo
- **WHEN** a cópia de trabalho do kit está numa versão mais nova, o kit tem a tag da versão do projeto, e o `trilha-ai/guarda.py` do projeto difere do dessa tag
- **THEN** a conferência das regras reprova, citando `trilha-ai/guarda.py`

#### Scenario: Kit sem as tags
- **WHEN** o kit está noutra versão e não tem tag nenhuma (um clone raso, por exemplo)
- **THEN** a conferência das regras avisa que a pasta `trilha-ai/` não foi comparada
- **AND** não reprova pela cópia

#### Scenario: Versão que o kit não tem
- **WHEN** o kit tem as tags `vX.Y` e nenhuma é a da versão do projeto, como a de uma linha "Versão" trocada à mão, abaixo ou acima da do kit
- **THEN** a conferência das regras reprova, citando a versão do projeto

#### Scenario: Kit atrás do projeto
- **WHEN** a cópia de trabalho do kit está numa versão mais antiga que a do projeto e o kit tem a tag da versão do projeto
- **THEN** a conferência das regras não reprova pela cópia
- **AND** avisa para atualizar o kit ao lado, sem mandar rodar o `kit.py atualizar`

#### Scenario: Kit atrás na pasta antiga
- **WHEN** o projeto já está na `trilha-ai/`, e a cópia de trabalho do kit ao lado ainda é de antes da 2.19, com a `modelo/trilha/` e a tag da versão do projeto
- **THEN** a conferência das regras não reprova pela cópia
- **AND** avisa para atualizar o kit ao lado

#### Scenario: Comum sem a linha de versão
- **WHEN** o `trilha-ai/CLAUDE-comum.md` do projeto não tem a linha "Versão X.Y" e o `trilha-ai/guarda.py` difere do kit
- **THEN** a conferência das regras compara com a cópia de trabalho do kit e reprova, citando `trilha-ai/guarda.py`

### Requirement: Verificação fixa do projeto
O `trilha-ai/verifica.sh` SHALL rodar, nesta ordem, a conferência das regras (com a pasta do kit quando ela está ao lado do projeto ou em `TRILHA_AI`, e com aviso quando não está), a conferência do método (repassando os argumentos que receber, como `--vizinho`) e o `openspec validate --all --no-interactive`, e MUST terminar com erro quando qualquer um deles falhar.

#### Scenario: Projeto novo
- **WHEN** o `scripts/check.sh` de um projeto recém-criado pelo kit roda, chamando o `trilha-ai/verifica.sh`
- **THEN** ele termina com o código de saída 0

#### Scenario: Vizinho repassado
- **WHEN** o `scripts/check.sh` chama `bash trilha-ai/verifica.sh --vizinho outro` e o `ANDAMENTO.md` cita `outro`
- **THEN** a verificação reprova, citando `outro`

#### Scenario: Spec inválido
- **WHEN** o projeto tem um spec do OpenSpec com um requisito sem SHALL nem MUST e o `openspec` está instalado
- **THEN** a verificação termina com erro

#### Scenario: OpenSpec ausente
- **WHEN** o comando `openspec` não existe no PATH, fora do CI
- **THEN** a verificação avisa que os specs não foram validados e não falha por isso

#### Scenario: OpenSpec ausente no CI
- **WHEN** o comando `openspec` não existe no PATH e a variável `CI` está definida, como no GitHub
- **THEN** a verificação termina com erro, dizendo que o OpenSpec falta

### Requirement: Decomposição no esqueleto da skill
A conferência do método SHALL exigir que a decomposição (`sdd/decomposicao-*.md`) tenha as linhas de título `## 1.`, `## 2.` e `## Ciclo`, cada uma no começo da linha e fora de bloco de código, lendo cada seção até o título seguinte, de qualquer nível, e MUST reprovar a que não tiver, nomeando cada título que falta e o esqueleto da skill `sdd:briefing`.

#### Scenario: Esqueleto da skill
- **WHEN** a decomposição é o esqueleto que a skill `sdd:briefing` traz, com ou sem uma change retirada
- **THEN** a conferência do método termina com o código de saída 0

#### Scenario: Título só dentro do texto
- **WHEN** a decomposição tem `## Ciclo` e `## 2.` como títulos, mas `## 1.` só aparece dentro de outra linha (por exemplo, em `### 1. Recepção`)
- **THEN** a conferência do método reprova, citando `## 1.` e a skill `sdd:briefing`

#### Scenario: Sem a seção 2
- **WHEN** a decomposição tem os títulos `## 1.` e `## Ciclo`, e não o `## 2.`
- **THEN** a conferência do método reprova, citando `## 2.`

#### Scenario: Subseção depois do Ciclo
- **WHEN** a decomposição traz, depois da tabela do `## Ciclo`, uma subseção `###` com outra tabela numerada
- **THEN** a conferência do método compara só a tabela do "Ciclo" com a da seção 1 e termina com o código de saída 0

#### Scenario: Título citado em bloco de código
- **WHEN** a decomposição cita, dentro de um bloco de código, um `## 2.` ou um `## Ciclo` com uma tabela
- **THEN** o título citado não conta: sem o `## 2.` de verdade, a conferência reprova, citando `## 2.`; com os três de verdade, a tabela citada não entra na comparação

### Requirement: Aviso da stack por preencher depois do TDD
Quando a pasta `sdd/` tiver um `tdd-*.md`, a conferência das regras SHALL avisar, sem falhar, cada lugar da stack que ainda traz o texto do modelo do kit que pede o preenchimento: o `.github/dependabot.yml`, o `.gitignore` e a linha "Stack" do `openspec/config.yaml`, desde o TDD; o `scripts/check.sh` e o `.github/workflows/verificacao.yml`, só a partir do primeiro spec em `openspec/specs/`, que a change 01 cria. Sem TDD, ela MUST NOT dar esse aviso.

#### Scenario: TDD com a stack do modelo
- **WHEN** o projeto feito do kit tem um `sdd/tdd-x.md`, nenhum spec em `openspec/specs/` e os cinco lugares da stack como o modelo os deixou
- **THEN** a conferência das regras imprime um aviso que cita o `.github/dependabot.yml`, o `.gitignore` e o `openspec/config.yaml`
- **AND** o aviso não cita o `scripts/check.sh` nem o `.github/workflows/verificacao.yml`
- **AND** termina com o código de saída 0

#### Scenario: Change 01 arquivada com a stack do modelo
- **WHEN** o projeto tem um `sdd/tdd-x.md`, um spec em `openspec/specs/` e os cinco lugares da stack como o modelo os deixou
- **THEN** a conferência das regras imprime um aviso que cita os cinco

#### Scenario: Stack preenchida
- **WHEN** o projeto tem um `sdd/tdd-x.md` e nenhum dos cinco lugares traz mais o texto do modelo que pede o preenchimento
- **THEN** a conferência das regras não imprime o aviso da stack

#### Scenario: Stack preenchida como o modelo pede
- **WHEN** o projeto tem um `sdd/tdd-x.md`, apagou do `.gitignore` o bloco da stack que não é a sua e o comentário que pede isso, e trocou os exemplos do `.github/dependabot.yml` pelo bloco real, apagando o comentário que pede isso
- **THEN** o aviso da stack não cita o `.gitignore` nem o `.github/dependabot.yml`

#### Scenario: Projeto sem TDD
- **WHEN** o projeto feito do kit não tem `sdd/tdd-*.md`
- **THEN** a conferência das regras não imprime o aviso da stack

### Requirement: Teto de tamanho das regras carregadas
A conferência das regras SHALL reprovar o projeto cujo `CLAUDE.md` e `trilha-ai/CLAUDE-comum.md` somados passem de 200 linhas ou de 32.768 bytes (32 KB), citando a soma e o limite que ela passou.

#### Scenario: Regras largas demais
- **WHEN** o `CLAUDE.md` e o comum somam menos de 200 linhas e mais de 32.768 bytes
- **THEN** a conferência das regras reprova, citando os bytes e o limite de 32.768

#### Scenario: Linhas demais
- **WHEN** o `CLAUDE.md` e o comum somam mais de 200 linhas
- **THEN** a conferência das regras reprova, citando as linhas e o limite de 200

#### Scenario: Projeto novo dentro do teto
- **WHEN** a conferência das regras roda num projeto recém-criado pelo kit
- **THEN** ela não reprova pelo tamanho

### Requirement: Instalação no projeto que declara o plugin
Quando o `.claude/settings.json` do projeto declara o `sdd@trilha-ai` ligado e a lista do Claude Code o traz instalado só para a máquina inteira, a conferência do método SHALL avisar, com `claude plugin install sdd@trilha-ai --scope project`, sem falhar: a máquina que recebe o projeto pelo git não roda o `kit.py`.

#### Scenario: Projeto declarado e plugin só do usuário
- **WHEN** o projeto declara o plugin e a lista traz só o `sdd@trilha-ai` de escopo `user`, na versão do comum
- **THEN** a conferência imprime um só aviso sobre o plugin, com `claude plugin install sdd@trilha-ai --scope project`
- **AND** termina com o código de saída 0

#### Scenario: Plugin instalado no projeto
- **WHEN** o projeto declara o plugin e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão do comum
- **THEN** a conferência não imprime aviso sobre o plugin

### Requirement: Lista de plugins lida da pasta do projeto
A conferência do método SHALL consultar a lista de plugins do Claude Code com a pasta do projeto como pasta de trabalho, de onde quer que seja chamada, porque o "ligado" que a lista devolve segue o `.claude/settings.json` da pasta em que ela roda.

#### Scenario: Conferência chamada de outra pasta
- **WHEN** a conferência do método de um projeto é chamada a partir de outra pasta
- **THEN** a lista de plugins do Claude Code roda na pasta do projeto

### Requirement: Instalações que podem valer no projeto
Das instalações do plugin `sdd` que a lista traz, a conferência do método SHALL julgar todas as que podem valer no projeto: as sem pasta (escopo `user` ou outro da máquina inteira) e as de escopo `local` ou `project` cuja pasta é a do projeto. A de escopo `local` ou `project` de outra pasta MUST NOT contar. O aviso de versão SHALL dizer o escopo da instalação e trazer o comando de atualização com esse escopo.

#### Scenario: Instalação do usuário atrás da do projeto
- **WHEN** o comum do projeto diz "Versão 2.2" e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão `2.2.0`, e o de escopo `user` na versão `1.35.0`
- **THEN** a conferência imprime um só aviso de versão, que cita `1.35.0`, `2.2` e `claude plugin update sdd@trilha-ai --scope user`

#### Scenario: Só a instalação do usuário
- **WHEN** o projeto não declara o plugin e a lista traz só o `sdd@trilha-ai` de escopo `user`, na versão do comum
- **THEN** a conferência não imprime aviso sobre o plugin

#### Scenario: Instalação do projeto atrás da versão
- **WHEN** o comum do projeto diz "Versão 2.2" e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão `2.1.0`, e o de escopo `user` na versão `2.2.0`
- **THEN** a conferência imprime um só aviso de versão, que cita `2.1.0`, `2.2` e `claude plugin update sdd@trilha-ai --scope project`

### Requirement: Travas desligadas pela configuração
A conferência das regras SHALL avisar, sem falhar, cada trava desligada: a do commit, quando o `core.hooksPath` do clone não é `trilha-ai/hooks`, salvo `trilha/hooks` com o link de transição `trilha` no projeto, que conta como ligada, com o aviso para trocar; a do Claude Code, quando o `.claude/settings.json` não liga o `trilha-ai/guarda.py` ou quando o `disableAllHooks` que vale no projeto é verdadeiro, lido do `.claude/settings.local.json`, que prevalece, e do `.claude/settings.json`.

#### Scenario: Hooks desligados pela configuração local
- **WHEN** o `.claude/settings.local.json` do projeto tem `"disableAllHooks": true`
- **THEN** a conferência das regras avisa que a trava do Claude Code está desligada, citando o `disableAllHooks` e o `.claude/settings.local.json`
- **AND** termina com o código de saída 0

#### Scenario: Hooks desligados pelo projeto
- **WHEN** o `.claude/settings.json` do projeto tem `"disableAllHooks": true` e não há `.claude/settings.local.json`
- **THEN** a conferência das regras avisa, citando o `disableAllHooks` e o `.claude/settings.json`

#### Scenario: Configuração local religa os hooks
- **WHEN** o `.claude/settings.json` tem `"disableAllHooks": true` e o `.claude/settings.local.json` o tem falso
- **THEN** a conferência das regras não avisa o `disableAllHooks`

#### Scenario: Travas ligadas no projeto novo
- **WHEN** a conferência das regras roda num projeto recém-criado pelo kit
- **THEN** ela não avisa trava desligada

#### Scenario: Trava do commit pelo link de transição
- **WHEN** o projeto tem o link de transição `trilha` para `trilha-ai` e o `core.hooksPath` do clone é `trilha/hooks`
- **THEN** a conferência das regras não avisa a trava do commit desligada
- **AND** avisa que ela está ligada pelo link de transição e dá o comando `git config core.hooksPath trilha-ai/hooks`

#### Scenario: Trava do commit na pasta antiga sem o link
- **WHEN** o projeto não tem `trilha` e o `core.hooksPath` do clone é `trilha/hooks`
- **THEN** a conferência das regras avisa a trava do commit desligada

### Requirement: Regras por artefato iguais às do kit
Com a pasta do kit indicada, a conferência das regras SHALL comparar o bloco `rules:` do `openspec/config.yaml` do projeto com o do modelo do kit na versão do projeto, escolhida como na pasta `trilha-ai/`, e MUST reprovar o bloco diferente e cada linha do `operations` do kit que falte no projeto. Linhas próprias a mais no `operations`, chaves próprias no topo do arquivo e o projeto sem o `config.yaml` MUST NOT reprovar.

#### Scenario: Regras iguais às do kit
- **WHEN** o bloco `rules:` e o `operations` do `openspec/config.yaml` do projeto são os do modelo do kit
- **THEN** a conferência das regras não reprova pelo `config.yaml`

#### Scenario: Regras próprias
- **WHEN** o bloco `rules:` do projeto tem uma regra que o modelo do kit não tem
- **THEN** a conferência das regras reprova, citando o `openspec/config.yaml` e o bloco `rules:`

#### Scenario: Linha do operations que falta
- **WHEN** falta no `operations` do projeto uma linha do `operations` do modelo do kit
- **THEN** a conferência das regras reprova, citando o começo da linha que falta

#### Scenario: Acréscimos próprios aceitos
- **WHEN** o projeto tem as regras do kit, uma linha a mais no `operations.archive` e a chave `githubCopilot` no topo
- **THEN** a conferência das regras não reprova pelo `config.yaml`

#### Scenario: Projeto na versão anterior do kit
- **WHEN** o kit está numa versão nova, com regras mudadas, e o projeto, na anterior, tem as regras da tag dela
- **THEN** a conferência das regras não reprova pelo `config.yaml`

#### Scenario: Projeto sem o config.yaml
- **WHEN** o projeto não tem `openspec/config.yaml`
- **THEN** a conferência das regras não reprova pelo `config.yaml`

### Requirement: Link de transição da pasta antiga no kit
O kit SHALL manter `modelo/trilha` como link simbólico para `modelo/trilha-ai`, para a conferência das regras de um projeto de antes da 2.19, que procura a pasta pelo nome antigo, achar a do kit e comparar a do projeto com a tag da versão dele.

#### Scenario: Projeto da 2.18 com o kit novo ao lado
- **WHEN** a conferência das regras de um projeto feito pelo kit na versão 2.18, ainda na `trilha/`, roda com a pasta do kit 2.19 indicada
- **THEN** ela não reprova pela pasta do kit, e termina com o código de saída 0

### Requirement: Aviso do link de transição no projeto
Quando o projeto tem o link simbólico `trilha` que aponta para a `trilha-ai/` dele, a conferência das regras SHALL avisar, sem falhar, que esse é o link de transição da pasta antiga e que ele sai pelo `kit.py atualizar` quando nenhum arquivo do projeto citar mais `trilha/`. Um `trilha` que não é esse link MUST NOT gerar o aviso.

#### Scenario: Projeto com o link de transição
- **WHEN** a conferência das regras roda num projeto com o link `trilha` para `trilha-ai`
- **THEN** ela avisa o link de transição e o que o tira
- **AND** termina com o código de saída 0

#### Scenario: Pasta trilha própria do projeto
- **WHEN** o projeto tem uma pasta `trilha/` própria, que não é link
- **THEN** a conferência das regras não avisa o link de transição

#### Scenario: Link em laço
- **WHEN** o projeto tem um `trilha` que é um link simbólico para ele mesmo
- **THEN** a conferência das regras não avisa o link de transição e termina com o código de saída 0, sem traceback

### Requirement: Vizinho citado pelo nome inteiro no ANDAMENTO
A conferência do método SHALL reprovar o `ANDAMENTO.md` que cita um vizinho (`--vizinho`): numa palavra, partida no que não cabe num nome, a parte que é o nome, sozinho ou com `.git`, `.wiki` ou um final que não é só de letras, ou o host de URL que começa por ele, sem a pontuação do fim da palavra nem o `_` das pontas. MUST NOT reprovar o nome dentro de outro, o arquivo com extensão só de letras nem a pasta do método seguida de `/` num caminho relativo. O `../` MUST reprovar onde estiver.

#### Scenario: Vizinho pelo nome
- **WHEN** o `ANDAMENTO.md` diz "o kit trilha-ai está na 2.21", termina a frase com "o kit trilha-ai.", diz "clonar trilha-ai.git ao lado" ou "versão trilha-ai.v2", e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela reprova, citando `trilha-ai`

#### Scenario: Caminho que chega ao vizinho de fora
- **WHEN** o `ANDAMENTO.md` cita `https://github.com/paulosrl/trilha-ai/pull/22`, `/home/pl/projetos/trilha-ai/x`, `git@github.com:paulosrl/trilha-ai.git`, `https://github.com/paulosrl/trilha-ai.wiki` ou termina a frase com `https://github.com/paulosrl/trilha-ai.git.`, e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela reprova, citando `trilha-ai`

#### Scenario: Pasta do método
- **WHEN** o `ANDAMENTO.md` cita `trilha-ai/verifica.sh`, `./trilha-ai/verifica.sh` ou `./trilha-ai`, sem a barra, e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela não reprova pelo vizinho

#### Scenario: Nome colado a um sinal
- **WHEN** o `ANDAMENTO.md` cita `trilha-ai@2.21`, `trilha-ai==2.21`, `trilha-ai#24` ou `trilha-ai:main` e a conferência roda com `--vizinho trilha-ai`, ou cita `pl@heimdall`, `@heimdall` ou `_heimdall_` e ela roda com `--vizinho heimdall`
- **THEN** ela reprova, citando o vizinho

#### Scenario: Host de uma URL
- **WHEN** o `ANDAMENTO.md` cita `https://heimdall.vercel.app/x` e a conferência roda com `--vizinho heimdall`
- **THEN** ela reprova, citando `heimdall`; o `https://exemplo.com/docs/heimdall.yaml` não reprova

#### Scenario: Caminho relativo que começa em outro vizinho
- **WHEN** o `ANDAMENTO.md` diz "ajustar heimdall/scripts/check.sh" e a conferência roda com `--vizinho heimdall`
- **THEN** ela reprova, citando `heimdall`

#### Scenario: Nome dentro de outro nome
- **WHEN** o `ANDAMENTO.md` cita a change `hooks-pela-trilha-ai`, a palavra `outros` e o arquivo `heimdall.yaml`, e a conferência roda com `--vizinho trilha-ai --vizinho outro --vizinho heimdall`
- **THEN** ela não reprova pelo vizinho

#### Scenario: Caminho para fora do projeto
- **WHEN** o `ANDAMENTO.md` cita `../qualquer/coisa`
- **THEN** ela reprova, citando `../`

#### Scenario: Vizinho vazio
- **WHEN** a conferência roda com `--vizinho ""`
- **THEN** ela não reprova pelo vizinho

### Requirement: Vizinho só com o nome de um repositório
A conferência do método SHALL aceitar no `--vizinho` só letras, números, `_`, `.` e `-`, os caracteres do nome de um repositório, e MUST recusar o vizinho com qualquer outro caractere (a barra, os dois-pontos, o espaço) como erro de uso, que ela nunca acharia no `ANDAMENTO.md`.

#### Scenario: Vizinho com barra
- **WHEN** a conferência do método roda com `--vizinho paulosrl/trilha-ai`, `--vizinho trilha-ai:main` ou `--vizinho "trilha ai"`
- **THEN** ela termina com o código de saída 2 e mostra o uso
