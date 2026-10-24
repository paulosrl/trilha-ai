## RENAMED Requirements

- FROM: `### Requirement: Recusa da pasta trilha de outra coisa`
- TO: `### Requirement: Recusa da pasta trilha-ai de outra coisa`

## MODIFIED Requirements

### Requirement: Projeto novo com a pasta do método
O `kit.py novo` SHALL criar o projeto com a pasta `trilha-ai/` igual à `modelo/trilha-ai/` do kit, o `CLAUDE.md` importando `@trilha-ai/CLAUDE-comum.md`, a trava do commit ligada em `trilha-ai/hooks` e o hook do Claude Code apontando para `trilha-ai/guarda.py`.

#### Scenario: Projeto novo verificado
- **WHEN** o `kit.py novo` cria um projeto numa pasta vazia
- **THEN** a pasta `trilha-ai/` do projeto é igual à `modelo/trilha-ai/` do kit
- **AND** `git config core.hooksPath` responde `trilha-ai/hooks`
- **AND** o `.claude/settings.json` liga `trilha-ai/guarda.py`
- **AND** o `scripts/check.sh` do projeto termina com o código de saída 0

#### Scenario: Trava do commit no projeto novo
- **WHEN** o projeto novo recebe um commit com o `CLAUDE.md` sem a importação do comum
- **THEN** a trava do commit o barra

### Requirement: Atualização da pasta do método por inteiro
O `kit.py atualizar` SHALL deixar a pasta `trilha-ai/` do projeto igual à `modelo/trilha-ai/` do kit, inclusive apagando dela o arquivo que o kit não tem mais, sem tocar no que o projeto preencheu fora dela.

#### Scenario: Arquivo que o kit tirou
- **WHEN** a pasta `trilha-ai/` do projeto tem um arquivo que o kit não tem mais
- **THEN** depois do `kit.py atualizar` esse arquivo não existe
- **AND** a pasta é igual à do kit

### Requirement: Migração do layout antigo
Num projeto com as cópias do método na raiz, em `scripts/` e em `.githooks/pre-commit`, o `kit.py atualizar` SHALL levá-las para `trilha-ai/` e apagar as antigas, trocar a importação do `CLAUDE.md` para `@trilha-ai/CLAUDE-comum.md` (também quando as cópias já tiverem saído), o `core.hooksPath` para `trilha-ai/hooks` e o hook do Claude Code para `trilha-ai/guarda.py`, sem duplicá-lo e sem tocar em outros hooks do projeto.

#### Scenario: Projeto da versão 1.30 migrado
- **WHEN** o `kit.py atualizar` roda num projeto feito pelo kit na versão 1.30
- **THEN** não existem mais `CLAUDE-comum.md` na raiz, os `scripts/confere_*.py`, o `scripts/gerar_pagina_sdd.py`, o `scripts/pagina_sdd_modelo.html`, o `scripts/guarda.py` nem o `.githooks/pre-commit`
- **AND** o `CLAUDE.md` importa `@trilha-ai/CLAUDE-comum.md`, o `core.hooksPath` é `trilha-ai/hooks` e o `.claude/settings.json` liga só `trilha-ai/guarda.py`, uma vez
- **AND** a conferência das regras e a do método passam

#### Scenario: Hook de envio do projeto preservado
- **WHEN** o projeto tem, além do `.githooks/pre-commit`, um `.githooks/pre-push` próprio
- **THEN** depois da migração o `.githooks/pre-push` continua em `.githooks/`, sem mudança
- **AND** a ferramenta não avisa que ele deixou de rodar, porque o `trilha-ai/hooks/pre-push` o roda
- **AND** um `git push` do projeto migrado roda o `.githooks/pre-push`

#### Scenario: Hook de envio do projeto que não pode rodar
- **WHEN** o `.githooks/pre-push` do projeto está sem a permissão de execução ou é um link simbólico quebrado
- **THEN** a migração o mantém como está
- **AND** a ferramenta avisa que o envio será recusado até ele ser corrigido, citando o arquivo

#### Scenario: Outro hook do projeto preservado
- **WHEN** o projeto tem, além do `.githooks/pre-commit`, outro hook próprio em `.githooks/` (por exemplo, `commit-msg`)
- **THEN** depois da migração esse hook continua em `.githooks/`, sem mudança
- **AND** a ferramenta avisa que ele não roda mais, porque a trava do commit passou a `trilha-ai/hooks`, citando o arquivo

#### Scenario: Migração parcial
- **WHEN** as cópias soltas já saíram, mas o `CLAUDE.md` ainda importa `@CLAUDE-comum.md` (com ou sem espaço no fim da linha)
- **THEN** depois do `kit.py atualizar` o `CLAUDE.md` importa `@trilha-ai/CLAUDE-comum.md`

### Requirement: Recusa da pasta trilha-ai de outra coisa
O `kit.py atualizar` SHALL recusar, sem apagar nem copiar nada, o projeto que já tem uma pasta `trilha-ai/` sem `trilha-ai/CLAUDE-comum.md`, porque ela não é a do método.

#### Scenario: Pasta trilha do projeto
- **WHEN** o projeto tem `trilha-ai/` com arquivos próprios e sem `trilha-ai/CLAUDE-comum.md`
- **THEN** o `kit.py atualizar` recusa, com o motivo
- **AND** os arquivos da pasta continuam lá

### Requirement: Lista do método pelos arquivos versionados
O que o kit copia sem mudar SHALL ser a lista dos arquivos versionados no git em `modelo/trilha-ai/`, e não o que estiver na pasta: arquivo não versionado ali não vai ao projeto.

#### Scenario: Arquivo solto na pasta do kit
- **WHEN** a pasta `modelo/trilha-ai/` do kit tem um arquivo que o git não versiona
- **THEN** ele não está na lista do que se copia

### Requirement: Parte fixa do check.sh migrada
Na migração, quando o `scripts/check.sh` do projeto tiver a parte fixa do kit, o `kit.py atualizar` SHALL trocá-la pela chamada `bash trilha-ai/verifica.sh`, preservando os argumentos e a continuação de linha da chamada antiga e o resto do arquivo; quando não tiver, SHALL deixar o arquivo como está e avisar o que trocar.

#### Scenario: Parte fixa do kit com vizinhos
- **WHEN** o `scripts/check.sh` tem o bloco `FONTE=…` até o `fi` e `python3 -I scripts/confere_metodo.py --vizinho trilha-ai \` seguido de outra linha
- **THEN** depois da migração o bloco não existe mais e a chamada é `bash trilha-ai/verifica.sh --vizinho trilha-ai \`, com a linha seguinte e a parte da stack intactas

#### Scenario: Parte fixa alterada pelo projeto
- **WHEN** o `scripts/check.sh` não tem a parte fixa do kit e ainda chama `scripts/confere_*`, que a migração tirou
- **THEN** o arquivo fica como está
- **AND** a ferramenta diz que a chamada a `bash trilha-ai/verifica.sh` deve ser posta à mão
- **AND** a atualização termina com o código de saída 1, sem sugerir o commit

### Requirement: Aviso da parte fixa que falta no projeto
O `kit.py atualizar` SHALL avisar cada linha da parte fixa do modelo atual que falta no projeto, em qualquer versão dele; vale como presente a linha igual, com argumentos ou chamada dentro de uma linha dele, após um espaço, e a ação (`uses:`) noutra versão. MUST NOT avisar os blocos da parte da stack (os que abrem com "# Parte da stack" e, no `.gitignore`, `# Python` e `# Node`). O que o kit tirou SHALL seguir pela diferença entre as versões.

#### Scenario: Chamada com os vizinhos
- **WHEN** o `scripts/check.sh` migrado tem `bash trilha-ai/verifica.sh --vizinho trilha-ai \`
- **THEN** a ferramenta não avisa que falta `bash trilha-ai/verifica.sh`

#### Scenario: Linha curta que falta
- **WHEN** o kit acrescentou à parte fixa a linha `fi` e o projeto só tem uma linha que começa com `fi` sem ser ela (por exemplo, `find .`)
- **THEN** a ferramenta avisa que falta `fi`

#### Scenario: Linha que o projeto nunca copiou
- **WHEN** o modelo do `.gitignore` já trazia `*.log` na versão do projeto e o `.gitignore` do projeto não o tem
- **THEN** a ferramenta avisa que falta `*.log`

#### Scenario: Bloco da stack apagado
- **WHEN** o `.gitignore` do projeto não tem o bloco `# Python` do modelo
- **THEN** a ferramenta não avisa que falta `.venv/`

#### Scenario: Chamada dentro de uma função do projeto
- **WHEN** o `scripts/check.sh` do projeto chama `etapa "regras" bash trilha-ai/verifica.sh --vizinho trilha-ai`
- **THEN** a ferramenta não avisa que falta `bash trilha-ai/verifica.sh`

#### Scenario: Bloco da parte da stack trocado
- **WHEN** o `scripts/check.sh` do projeto trocou o bloco "Parte da stack" do modelo pelos comandos da stack dele
- **THEN** a ferramenta não avisa a linha `echo` daquele bloco

#### Scenario: Ação atualizada pelo Dependabot
- **WHEN** o CI do projeto tem `actions/checkout` fixada noutro commit que o do modelo
- **THEN** a ferramenta não avisa a linha do `actions/checkout`

#### Scenario: Passo fixo do CI ao lado do comentário da stack
- **WHEN** o CI do projeto não tem o passo `actions/setup-node` do modelo, que fica no mesmo bloco do comentário "Parte da stack"
- **THEN** a ferramenta avisa que falta a linha do `actions/setup-node`

### Requirement: Plugin declarado no projeto
O `kit.py novo` e o `kit.py atualizar` SHALL deixar o `.claude/settings.json` do projeto com o plugin `sdd@trilha-ai` em `enabledPlugins` e o marketplace `trilha-ai` (GitHub `paulosrl/trilha-ai`) em `extraKnownMarketplaces`, acrescentando só o que falta: o valor que o projeto já declarou para essas chaves e as outras chaves do arquivo MUST ficar como estavam.

#### Scenario: Projeto novo com o plugin declarado
- **WHEN** o `kit.py novo` cria um projeto numa pasta vazia
- **THEN** o `.claude/settings.json` tem `enabledPlugins` com `sdd@trilha-ai` verdadeiro
- **AND** tem `extraKnownMarketplaces` com `trilha-ai`, de origem `github` e repositório `paulosrl/trilha-ai`
- **AND** continua ligando `trilha-ai/guarda.py`

#### Scenario: Projeto atualizado com o settings.json próprio
- **WHEN** o `kit.py atualizar` roda num projeto cujo `.claude/settings.json` tem outras chaves, outro plugin em `enabledPlugins` e outro marketplace em `extraKnownMarketplaces`, sem o `sdd@trilha-ai`
- **THEN** o arquivo passa a ter o `sdd@trilha-ai` e o `trilha-ai`
- **AND** as outras chaves, o outro plugin e o outro marketplace continuam como estavam

#### Scenario: Plugin desligado pelo projeto
- **WHEN** o `.claude/settings.json` do projeto tem `sdd@trilha-ai` falso em `enabledPlugins`
- **THEN** depois do `kit.py atualizar` ele continua falso

#### Scenario: Atualização repetida
- **WHEN** o `kit.py atualizar` roda duas vezes seguidas no mesmo projeto
- **THEN** a segunda não muda o `.claude/settings.json`

### Requirement: Settings.json somado do modelo inteiro
A soma do `.claude/settings.json` SHALL ler o `modelo/claude-settings.json` inteiro: a chave que falta no projeto entra, o objeto presente nos dois é somado chave por chave, e o item de lista do modelo entra quando nenhum item do projeto o contém; o valor que o projeto já deu MUST ficar. A trava do Claude Code de outra versão do kit (`scripts/guarda.py`, `trilha/guarda.py` ou `trilha-ai/guarda.py` chamada de outro jeito) SHALL sair, com o grupo que só a tinha, e a do modelo entrar.

#### Scenario: Chave nova no modelo
- **WHEN** o modelo tem uma chave que o settings.json do projeto não tem
- **THEN** a soma a põe no projeto, sem trocar as que ele já tinha

#### Scenario: Trava de outra versão
- **WHEN** o grupo de `PreToolUse` do projeto tem a `trilha-ai/guarda.py` chamada de outro jeito e um gancho próprio, e outro grupo só com a `scripts/guarda.py`
- **THEN** depois da soma ficam o grupo com o gancho próprio e o grupo da trava do modelo

#### Scenario: Trava do modelo num grupo do projeto
- **WHEN** o grupo de `PreToolUse` do projeto tem a trava do modelo e um gancho próprio
- **THEN** a soma não acrescenta outro grupo com a trava

### Requirement: Página regenerada só quando existe
O `kit.py atualizar` SHALL gerar de novo o `sdd/documentacao.html` só quando ele já existe, para que ganhe o modelo novo da página; MUST NOT criá-lo, porque ele nasce ao fechar uma etapa.

#### Scenario: Projeto sem a página
- **WHEN** o projeto tem a pasta `sdd/` sem o `documentacao.html` e o `kit.py atualizar` roda
- **THEN** o `sdd/documentacao.html` continua sem existir

#### Scenario: Projeto com a página
- **WHEN** o projeto tem o `sdd/documentacao.html` e o `kit.py atualizar` roda
- **THEN** o arquivo é gerado de novo pelo `trilha-ai/gerar_pagina_sdd.py`

### Requirement: Update do OpenSpec que apagaria arquivos
Antes de mudar qualquer arquivo do projeto, o `kit.py atualizar --openspec` SHALL rodar o `openspec update --dry-run --json` na pasta do projeto, já na versão do kit. Se ele listar algum arquivo do projeto para apagar, sem a opção `--aceitar-apagados`, a ferramenta MUST NOT rodar o update nem mudar arquivo nenhum do projeto, e MUST terminar com o código 1, com uma recusa que nomeia esses arquivos, o comando `openspec config list` e a opção `--aceitar-apagados`. O que ele apagaria fora do projeto (no HOME ou num caminho absoluto) MUST NOT recusar o update; a ferramenta MUST avisá-lo, sem falhar.

#### Scenario: Perfil da máquina sem o que o projeto versiona
- **WHEN** o dry-run lista `.claude/skills/openspec-propose/SKILL.md` para apagar, a `trilha-ai/` do projeto difere da do kit, e o `kit.py atualizar` roda com `--openspec`, sem `--aceitar-apagados`
- **THEN** a ferramenta não roda o `openspec update`, e a saída traz uma recusa que cita esse arquivo, o `openspec config list` e o `--aceitar-apagados`
- **AND** termina com o código de saída 1, sem o "commit sugerido", com o `git status` do projeto vazio e a `trilha-ai/` dele como estava

#### Scenario: De novo depois da recusa
- **WHEN** o `kit.py atualizar --openspec` foi recusado porque o update apagaria arquivos do projeto, e roda de novo com um dry-run sem nada a apagar
- **THEN** a ferramenta não recusa o projeto por trabalho não commitado e roda o `openspec update`
- **AND** termina com o código de saída 0

#### Scenario: Apagados fora do projeto
- **WHEN** o dry-run lista para apagar só `~/.codex/prompts/opsx-ff.md` e `/etc/openspec/x.md`
- **THEN** a ferramenta roda o `openspec update`, e a saída traz um aviso que cita os dois
- **AND** termina com o código de saída 0

### Requirement: Commit sugerido do atualizar
Quando o `kit.py atualizar` termina com o código 0 e o projeto mudou, ele SHALL sugerir o commit com as partes do que mudou: "cópia do kit Trilha AI, comum A → B" quando a versão do comum muda ou a cópia trocou algum arquivo, e "os arquivos gerados pelo OpenSpec X" (X, a versão do CI do modelo do kit) quando, com `--openspec`, o update mudou arquivos do projeto. Com as duas, a mensagem MUST trazê-las nessa ordem, unidas por ", e ". Nos cenários, V é a versão do comum do kit.

#### Scenario: Só o OpenSpec muda
- **WHEN** o projeto está na versão do comum do kit, a cópia não troca nenhum arquivo, e o `kit.py atualizar --openspec` roda com um dry-run que lista a troca de uma skill do projeto
- **THEN** a saída traz "commit sugerido: chore(metodo): os arquivos gerados pelo OpenSpec X"

#### Scenario: A cópia e o OpenSpec mudam
- **WHEN** o projeto está na versão do comum do kit, a `trilha-ai/` dele difere da do kit, e o `kit.py atualizar --openspec` roda com um dry-run que lista a troca de uma skill do projeto
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V, e os arquivos gerados pelo OpenSpec X"

#### Scenario: Só a cópia muda, com o --openspec
- **WHEN** o projeto está na versão do comum do kit, a `trilha-ai/` dele difere da do kit, e o `kit.py atualizar --openspec` roda com um dry-run sem mudança nenhuma
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V", sem citar o OpenSpec

#### Scenario: O dry-run previu, e o update não mudou
- **WHEN** a `trilha-ai/` do projeto difere da do kit, na mesma versão do comum, e o `kit.py atualizar --openspec` roda com um dry-run que lista a troca de uma skill que o update não faz
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V", sem citar o OpenSpec

#### Scenario: O update mudou sem o dry-run prever
- **WHEN** a cópia não troca nenhum arquivo, na mesma versão do comum, e o `kit.py atualizar --openspec` roda com um dry-run sem mudança nenhuma, mas o update troca uma skill do projeto
- **THEN** a saída traz "commit sugerido: chore(metodo): os arquivos gerados pelo OpenSpec X"

#### Scenario: Sem o --openspec
- **WHEN** o projeto está na versão do comum do kit, a `trilha-ai/` dele difere da do kit, e o `kit.py atualizar` roda sem `--openspec`
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V", sem citar o OpenSpec


## ADDED Requirements

### Requirement: Migração da pasta trilha para trilha-ai
Num projeto com a pasta `trilha/` do método (com o `trilha/CLAUDE-comum.md`), o `kit.py atualizar` SHALL tirá-la, criar a `trilha-ai/` do kit, trocar `trilha/` por `trilha-ai/` no `CLAUDE.md` (a importação e as citações) e no `scripts/check.sh` (a chamada do `verifica.sh`, com os argumentos), e ligar a trava do Claude Code e o `core.hooksPath` pela pasta nova. Uma pasta `trilha/` sem o comum MUST ficar como está.

#### Scenario: Projeto da versão 2.18 migrado
- **WHEN** o `kit.py atualizar` roda num projeto feito pelo kit na versão 2.18, com um `--vizinho` no `scripts/check.sh`
- **THEN** a pasta `trilha/` não existe mais, e a `trilha-ai/` é igual à `modelo/trilha-ai/` do kit
- **AND** o `CLAUDE.md` importa `@trilha-ai/CLAUDE-comum.md` e não cita mais `trilha/`, o `scripts/check.sh` chama `bash trilha-ai/verifica.sh` com o mesmo `--vizinho`, o `.claude/settings.json` liga só `trilha-ai/guarda.py`, uma vez, e o `core.hooksPath` é `trilha-ai/hooks`
- **AND** a conferência das regras e a do método passam, e a saída sugere o commit da cópia, com as duas versões
- **AND** a saída avisa para reabrir a sessão do Claude Code aberta no projeto, que ainda chama a trava antiga

#### Scenario: Arquivo a mais na pasta trilha do método
- **WHEN** a pasta `trilha/` do método tem um arquivo que o kit não tem
- **THEN** depois do `kit.py atualizar` a pasta `trilha/` não existe mais
- **AND** a saída traz um aviso que cita esse arquivo

#### Scenario: Pasta trilha que não é do método
- **WHEN** o projeto já está na `trilha-ai/` e tem uma pasta `trilha/` própria, sem o `trilha/CLAUDE-comum.md`
- **THEN** depois do `kit.py atualizar` a pasta `trilha/` continua lá, sem mudança

#### Scenario: Arquivo do projeto que ainda cita a pasta trilha
- **WHEN** um arquivo versionado do projeto fora da `trilha-ai/`, do `CLAUDE.md` e do `scripts/check.sh` (por exemplo, um `docs/` qualquer) cita `trilha/`
- **THEN** a saída do `kit.py atualizar` traz um aviso que cita esse arquivo, para a troca à mão
- **AND** o aviso não cita um arquivo em que `trilha/` só aparece dentro de outro nome ou caminho (`minhatrilha/`, `trilha-ai/`, `src/trilha/`, `../trilha/`), nem o `.claude/settings.json`, cuja trava já foi trocada
- **AND** o aviso traz inteiro o nome do arquivo com acento ou espaço (`docs/decisões técnicas.md`)

#### Scenario: Importação com espaço no fim
- **WHEN** o `CLAUDE.md` do projeto da 2.18 importa `@trilha/CLAUDE-comum.md` com um espaço no fim da linha
- **THEN** depois do `kit.py atualizar` a linha é `@trilha-ai/CLAUDE-comum.md`, e a conferência das regras passa

#### Scenario: Arquivo ignorado na pasta trilha do método
- **WHEN** a pasta `trilha/` do método tem um arquivo que o git ignora (por exemplo, `trilha/notas.log`)
- **THEN** o `kit.py atualizar` recusa, citando o arquivo, sem mudar nada no projeto

#### Scenario: Pasta trilha do método que é um link simbólico
- **WHEN** a `trilha/` do projeto é um link simbólico para uma pasta com o comum
- **THEN** o `kit.py atualizar` recusa, com o motivo, sem mudar nada no projeto

#### Scenario: Caminho do projeto que cita trilha
- **WHEN** o `scripts/check.sh` do projeto da 2.18 também cita `src/trilha/` e `../trilha/x`
- **THEN** depois do `kit.py atualizar` essas citações continuam como estavam, e a chamada passa a `bash trilha-ai/verifica.sh`

#### Scenario: Versão de antes lida pelo nome novo
- **WHEN** o kit lê, na tag `v2.18`, o `trilha-ai/CLAUDE-comum.md`
- **THEN** ele acha o comum da 2.18, que naquela versão ficava em `modelo/trilha/`
