# ferramenta-do-kit Specification

## Purpose

Define o que a ferramenta do kit (`ferramentas/kit.py`) faz num repositório: criar um projeto novo no método e atualizar um existente para a versão do kit, inclusive migrar o layout antigo para a pasta `trilha-ai/`, sem fazer commit nem envio.

## Requirements

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

### Requirement: Perfil do OpenSpec com o verify no projeto novo
O `kit.py novo` SHALL listar, nos próximos passos, o `openspec config profile` com o verify marcado, e MUST avisar, sem falhar, quando o perfil do OpenSpec da máquina não trouxer o verify ou quando o OpenSpec não estiver instalado. A ferramenta só lê o perfil, nunca o muda.

#### Scenario: Perfil sem o verify
- **WHEN** o `kit.py novo` roda numa máquina cujo perfil do OpenSpec é o padrão (`core`), ou um perfil próprio sem o verify
- **THEN** a ferramenta avisa que o verify falta no perfil, com o comando `openspec config profile`
- **AND** termina com o código de saída 0

#### Scenario: Perfil com o verify
- **WHEN** o `kit.py novo` roda numa máquina cujo perfil do OpenSpec é próprio (`custom`) e traz o verify
- **THEN** a ferramenta não avisa sobre o perfil
- **AND** os próximos passos citam o `openspec config profile`

#### Scenario: OpenSpec ausente
- **WHEN** o comando `openspec` não existe no PATH
- **THEN** a ferramenta avisa que o OpenSpec falta
- **AND** termina com o código de saída 0

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

### Requirement: Settings.json que a soma não entende
O `kit.py atualizar` SHALL recusar, antes de mudar qualquer arquivo, o `.claude/settings.json` que não é JSON válido ou que tem outro tipo onde o modelo tem objeto ou lista.

#### Scenario: Settings.json que a soma não entende
- **WHEN** o settings.json do projeto tem `enabledPlugins` nulo, `PreToolUse` que não é lista, uma raiz que não é objeto ou JSON inválido, e o `kit.py atualizar` roda
- **THEN** a ferramenta recusa, citando o `.claude/settings.json`, e termina com o código de saída 1
- **AND** o projeto fica sem mudança

### Requirement: Comando de instalação por máquina
O `kit.py novo` SHALL imprimir, nos próximos passos, o comando que cada máquina roda uma vez para instalar o plugin no projeto, `claude plugin install sdd@trilha-ai --scope project`, sem rodá-lo. O `kit.py atualizar` MUST NOT imprimi-lo por conta própria: a conferência do método, que ele roda, o cita só quando a instalação no projeto falta.

#### Scenario: Comando no projeto novo
- **WHEN** o `kit.py novo` cria um projeto
- **THEN** a saída cita `claude plugin install sdd@trilha-ai --scope project`

#### Scenario: Comando na atualização
- **WHEN** o `kit.py atualizar` roda numa máquina cuja lista de plugins traz o `sdd@trilha-ai` só de escopo `user`
- **THEN** a saída cita `claude plugin install sdd@trilha-ai --scope project`

#### Scenario: Atualização com o plugin já no projeto
- **WHEN** o `kit.py atualizar` roda numa máquina cuja lista de plugins traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto
- **THEN** a saída não cita `claude plugin install sdd@trilha-ai --scope project`

### Requirement: Padrões técnicos do projeto
O projeto SHALL receber do kit o arquivo `sdd/padroes-tecnicos.md`, que ele pode ajustar ou apagar: o `kit.py novo` o cria do modelo, e o `kit.py atualizar` só o cria quando falta num projeto de versão anterior à 2.2, avisando, sem mudar o que o projeto escreveu nele. Desde a 2.2, a falta do arquivo é escolha do projeto, e a atualização MUST NOT recriá-lo.

#### Scenario: Projeto novo com os padrões
- **WHEN** o `kit.py novo` cria um projeto
- **THEN** o `sdd/padroes-tecnicos.md` é igual ao `modelo/sdd/padroes-tecnicos.md` do kit
- **AND** o `scripts/check.sh` do projeto termina com o código de saída 0

#### Scenario: Padrões ajustados pelo projeto
- **WHEN** o `sdd/padroes-tecnicos.md` do projeto difere do modelo e o `kit.py atualizar` roda
- **THEN** o arquivo continua como o projeto o deixou

#### Scenario: Projeto sem os padrões
- **WHEN** o projeto, com o comum numa versão anterior à 2.2, não tem o `sdd/padroes-tecnicos.md` e o `kit.py atualizar` roda
- **THEN** o arquivo passa a existir, igual ao modelo
- **AND** a ferramenta avisa que ele foi criado do modelo do kit

#### Scenario: Padrões apagados pelo projeto
- **WHEN** o projeto, com o comum na 2.2, não tem o `sdd/padroes-tecnicos.md` e o `kit.py atualizar` roda
- **THEN** o arquivo continua sem existir, e a saída não o cita

### Requirement: Página regenerada só quando existe
O `kit.py atualizar` SHALL gerar de novo o `sdd/documentacao.html` só quando ele já existe, para que ganhe o modelo novo da página; MUST NOT criá-lo, porque ele nasce ao fechar uma etapa.

#### Scenario: Projeto sem a página
- **WHEN** o projeto tem a pasta `sdd/` sem o `documentacao.html` e o `kit.py atualizar` roda
- **THEN** o `sdd/documentacao.html` continua sem existir

#### Scenario: Projeto com a página
- **WHEN** o projeto tem o `sdd/documentacao.html` e o `kit.py atualizar` roda
- **THEN** o arquivo é gerado de novo pelo `trilha-ai/gerar_pagina_sdd.py`

### Requirement: CodeGraph opcional nos próximos passos
Os próximos passos do `kit.py novo` SHALL citar o `codegraph init` como opcional, condicionado ao uso do CodeGraph, e MUST NOT apresentá-lo como passo obrigatório junto do `openspec init`.

#### Scenario: Projeto novo com o CodeGraph opcional
- **WHEN** o `kit.py novo` cria um projeto
- **THEN** a linha dos próximos passos que cita o `codegraph init` diz que ele vale só para quem usa o CodeGraph
- **AND** a mesma linha diz que ele roda em cada clone
- **AND** o item do `openspec init` não cita o `codegraph init`

### Requirement: Recusa do kit atrás do projeto
O `kit.py atualizar` SHALL recusar, antes de mudar qualquer arquivo, o projeto cuja versão do comum é mais nova que a do kit, mandando atualizar o kit (`git pull`), e MUST NOT sugerir o commit nesse caso.

#### Scenario: Projeto mais novo que o kit
- **WHEN** o `kit.py atualizar` roda num projeto cujo comum está numa versão mais nova que a do kit (a 9.9, por exemplo); a proteção vale a partir do kit da 2.5, que a traz
- **THEN** a ferramenta recusa, citando as duas versões e o `git pull`, e termina com o código de saída 1
- **AND** o projeto fica sem mudança

### Requirement: Recusa do kit sem o histórico do git
O `kit.py atualizar` SHALL recusar, antes de mudar qualquer arquivo, o kit que não é um repositório git ou que é um clone raso, porque a atualização lê as versões antigas do kit pelo histórico.

#### Scenario: Kit sem o git
- **WHEN** o `kit.py atualizar` roda de uma cópia do kit sem o `.git` (baixada como ZIP)
- **THEN** a ferramenta recusa, dizendo que o kit precisa ser um clone do git, e termina com o código de saída 1
- **AND** o projeto fica sem mudança

#### Scenario: Kit extraído dentro de outro repositório
- **WHEN** o `kit.py atualizar` roda de uma cópia do kit sem o `.git`, extraída numa pasta que está dentro de outro repositório git
- **THEN** a ferramenta recusa, dizendo que o kit precisa ser um clone do git
- **AND** o projeto fica sem mudança

#### Scenario: Kit clonado raso
- **WHEN** o `kit.py atualizar` roda de um clone raso do kit
- **THEN** a ferramenta recusa, citando o `git fetch --unshallow --tags`
- **AND** o projeto fica sem mudança

### Requirement: Atualização do OpenSpec sob pedido
Com a opção `--openspec`, o `kit.py atualizar` SHALL instalar o OpenSpec na versão fixada no CI do modelo do kit (`npm install -g @fission-ai/openspec@X`) quando a da máquina for outra ou faltar, e depois rodar o `openspec update` na pasta do projeto, sem consultar a rede por versão nova, antes da conferência. Sem a opção, o `kit.py atualizar` MUST NOT chamar o `npm` nem o `openspec update`.

#### Scenario: Versão da máquina diferente da do kit
- **WHEN** o `openspec --version` responde `1.14.1`, o CI do modelo do kit fixa `1.15.0`, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a ferramenta roda `npm install -g @fission-ai/openspec@1.15.0` e depois o `openspec update` na pasta do projeto
- **AND** termina com o código de saída 0

#### Scenario: Versão da máquina igual à do kit
- **WHEN** o `openspec --version` responde a versão que o CI do modelo do kit fixa, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a ferramenta não chama o `npm` e roda o `openspec update` na pasta do projeto

#### Scenario: Sem a opção
- **WHEN** o `kit.py atualizar` roda sem `--openspec`
- **THEN** a ferramenta não chama o `npm` nem o `openspec update`

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

### Requirement: Falha da atualização do OpenSpec
Quando o projeto não tem a pasta `openspec/`, o CI do modelo do kit não fixa a versão do OpenSpec, o `npm` falta ou falha, o `openspec` do PATH responde outra versão depois da instalação, ou o dry-run falha, o `kit.py atualizar --openspec` MUST terminar com o código 1, com uma recusa que diz o que falhou, sem mudar arquivo nenhum do projeto. Quando o `openspec update`, que roda depois da cópia, falha, a ferramenta MUST terminar com o código 1, com uma FALHA que o cita, sem sugerir o commit; o que o kit já copiou fica no projeto, sem commit. Quando a migração do `check.sh` falharia, a ferramenta MUST NOT chamar o `npm` nem o `openspec update`.

#### Scenario: Projeto sem a pasta openspec
- **WHEN** o projeto não tem a pasta `openspec/`, a versão da máquina é outra, e o `kit.py atualizar` roda com `--openspec`, com o `scripts/check.sh` do kit ou com um que a migração não sabe trocar
- **THEN** a saída traz uma recusa que manda rodar o `kit.py atualizar` sem `--openspec`, fazer o commit e rodar de novo com `--openspec`, e a ferramenta não chama o `npm` nem o `openspec update`
- **AND** termina com o código de saída 1, com o `git status` do projeto vazio

#### Scenario: Máquina sem o npm
- **WHEN** a versão da máquina é outra e o comando `npm` não existe no PATH
- **THEN** a saída traz uma recusa que cita o `npm install -g @fission-ai/openspec@X`, e o `openspec update` não roda
- **AND** termina com o código de saída 1, sem o "commit sugerido", com o `git status` do projeto vazio

#### Scenario: Instalação que não muda o openspec do PATH
- **WHEN** a versão da máquina é outra, o `npm install` termina com 0, e o `openspec --version` continua respondendo a versão anterior
- **THEN** a saída traz uma recusa que cita outro `openspec` antes no PATH, e o `openspec update` não roda
- **AND** termina com o código de saída 1, com o `git status` do projeto vazio

#### Scenario: Update com erro
- **WHEN** o `openspec update` termina com erro
- **THEN** a saída traz uma FALHA que cita o `openspec update`
- **AND** termina com o código de saída 1, sem o "commit sugerido"

#### Scenario: Dry-run com erro
- **WHEN** o dry-run termina com erro, com a mensagem `No OpenSpec directory found.`
- **THEN** a saída traz essa mensagem e, depois dela, mesmo com a saída de erro junta à do resto, uma recusa que cita o dry-run; o `openspec update` não roda
- **AND** termina com o código de saída 1, com o `git status` do projeto vazio

#### Scenario: Migração do check.sh que falha
- **WHEN** o `scripts/check.sh` do projeto ainda chama os `scripts/confere_*` fora da parte fixa do kit, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a ferramenta não chama o `npm` nem o `openspec update`, e a saída traz um aviso de que o `--openspec` não roda por causa do `scripts/check.sh`
- **AND** termina com o código de saída 1

#### Scenario: CI do modelo sem a versão do OpenSpec
- **WHEN** o CI do modelo do kit não fixa a versão do OpenSpec, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a saída traz uma recusa que diz que o CI do modelo não fixa a versão, e a ferramenta não roda comando nenhum
- **AND** nenhum arquivo do projeto muda

### Requirement: Aviso da versão do OpenSpec no atualizar
Sem a opção `--openspec`, quando a versão do `openspec` da máquina diferir da fixada no CI do modelo do kit, o `kit.py atualizar` SHALL avisar, sem falhar, com as duas versões e a opção `--openspec`; sem o `openspec`, ou com a mesma versão, MUST seguir sem esse aviso.

#### Scenario: Versão diferente sem a opção
- **WHEN** o `openspec --version` responde `1.14.1`, o CI do modelo do kit fixa `1.15.0`, e o `kit.py atualizar` roda sem `--openspec`
- **THEN** a saída traz um aviso que cita `1.14.1`, `1.15.0` e `--openspec`

#### Scenario: Versão igual sem a opção
- **WHEN** o `openspec --version` responde a versão que o CI do modelo do kit fixa
- **THEN** a saída não traz o aviso da opção `--openspec`

### Requirement: Aviso do CI do projeto atrás do kit
Quando o CI do projeto (`.github/workflows/verificacao.yml`) fixar uma versão do OpenSpec diferente da do CI do modelo do kit, o `kit.py atualizar` SHALL avisar, sem falhar, com as duas versões e o arquivo, dizendo que a conferência que roda depois cita a versão do projeto até ela ser trocada.

#### Scenario: CI do projeto na versão anterior
- **WHEN** o CI do projeto instala `@fission-ai/openspec@1.14.1`, o do modelo do kit fixa `1.15.0`, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a saída traz um aviso que cita `1.14.1`, `1.15.0` e `.github/workflows/verificacao.yml`

### Requirement: Aceite dos apagados no update do OpenSpec
Com `--openspec` e `--aceitar-apagados`, quando o dry-run listar arquivos do projeto para apagar, o `kit.py atualizar` SHALL avisar, sem falhar, com esses arquivos, e rodar o `openspec update`. Sem o `--openspec`, a opção `--aceitar-apagados` MUST ser recusada como erro de uso, antes de mudar qualquer arquivo.

#### Scenario: Apagados aceitos
- **WHEN** o dry-run lista `.claude/skills/openspec-propose/SKILL.md` para apagar, e o `kit.py atualizar` roda com `--openspec --aceitar-apagados`
- **THEN** a saída traz um aviso que cita esse arquivo, e a ferramenta roda o `openspec update`
- **AND** termina com o código de saída 0

#### Scenario: Opção sem o --openspec
- **WHEN** o `kit.py atualizar` roda com `--aceitar-apagados`, sem `--openspec`
- **THEN** a saída traz um erro de uso que diz que o `--aceitar-apagados` só vale no `atualizar`, com o `--openspec`, e a ferramenta não chama o `npm` nem o `openspec update`
- **AND** termina com o código de saída 2, com o `git status` do projeto vazio

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
- **AND** o aviso não cita um arquivo em que `trilha/` só aparece dentro de outro nome (`minhatrilha/`, `trilha-ai/`), nem o `.claude/settings.json`, cuja trava já foi trocada, nem uma change arquivada do OpenSpec
- **AND** o aviso traz inteiro o nome do arquivo com acento ou espaço (`docs/decisões técnicas.md`)
- **AND** o aviso também cita o arquivo que chama a pasta por outro caminho ou depois de uma variável do shell (`src/trilha/`, `../trilha/`, `"$RAIZ/trilha/hooks"`, `${R:-.}/trilha/`) ou pelo nome entre aspas (`Path("trilha")`)

#### Scenario: Importação com espaço no fim
- **WHEN** o `CLAUDE.md` do projeto da 2.18 importa `@trilha/CLAUDE-comum.md` com um espaço no fim da linha
- **THEN** depois do `kit.py atualizar` a linha é `@trilha-ai/CLAUDE-comum.md`, e a conferência das regras passa

#### Scenario: Arquivo ignorado na pasta trilha do método
- **WHEN** a pasta `trilha/` do método tem um arquivo que o git ignora (por exemplo, `trilha/notas.log`)
- **THEN** o `kit.py atualizar` recusa, citando o arquivo, sem mudar nada no projeto

#### Scenario: Pasta trilha do método que é um link simbólico
- **WHEN** a `trilha/` do projeto é um link simbólico para uma pasta com o comum que não é a `trilha-ai/` do projeto
- **THEN** o `kit.py atualizar` recusa, com o motivo, sem mudar nada no projeto

#### Scenario: Caminho do projeto que cita trilha
- **WHEN** o `scripts/check.sh` do projeto da 2.18 também cita `src/trilha/` e `../trilha/x`
- **THEN** depois do `kit.py atualizar` essas citações continuam como estavam, e a chamada passa a `bash trilha-ai/verifica.sh`

#### Scenario: Versão de antes lida pelo nome novo
- **WHEN** o kit lê, na tag `v2.18`, o `trilha-ai/CLAUDE-comum.md`
- **THEN** ele acha o comum da 2.18, que naquela versão ficava em `modelo/trilha/`

### Requirement: Link de transição criado na migração
Quando a migração da `trilha/` do método termina e a busca das citações acha um arquivo que ainda cita `trilha/`, ou falha, o `kit.py atualizar` SHALL criar no projeto o link simbólico `trilha` para `trilha-ai`, relativo, e dizer na saída que o criou, por quê e que ele sai quando nenhum arquivo citar mais `trilha/`. Sem citação, o link MUST NOT ser criado.

#### Scenario: Projeto que ainda cita a pasta antiga
- **WHEN** o `kit.py atualizar` migra um projeto da 2.18 com um `docs/como.md` que cita `trilha/tempo.py`
- **THEN** o projeto tem o link simbólico `trilha` que aponta para `trilha-ai`, e o `trilha/tempo.py` existe por ele
- **AND** a saída diz que criou o link de transição e cita o `docs/como.md`, sem pedir para reabrir a sessão do Claude Code, que segue funcionando pelo link
- **AND** a conferência das regras e a do método passam, e o `git status` mostra o link entre o que mudou

#### Scenario: Projeto que não cita mais a pasta antiga
- **WHEN** o `kit.py atualizar` migra um projeto da 2.18 sem arquivo que cite `trilha/` fora do `CLAUDE.md` e do `scripts/check.sh`
- **THEN** o projeto não tem `trilha`, nem pasta nem link

### Requirement: Link de transição no atualizar seguinte
Num projeto que já está na `trilha-ai/` e tem o link simbólico `trilha` que aponta para a `trilha-ai/` dele, o `kit.py atualizar` SHALL tratá-lo como o link de transição: MUST NOT recusar nem migrar por ele; MUST tirá-lo, com aviso, quando a busca das citações não acha mais nenhuma, e mantê-lo, com aviso e a lista, quando ainda acha ou quando ela falha.

#### Scenario: Link que fica
- **WHEN** o `kit.py atualizar` roda de novo, depois do commit da migração, com o `docs/como.md` ainda citando `trilha/tempo.py`
- **THEN** ele termina com o código de saída 0, o link `trilha` continua apontando para `trilha-ai`
- **AND** a saída diz que o link de transição fica e cita o `docs/como.md`

#### Scenario: Link que sai
- **WHEN** o `kit.py atualizar` roda de novo depois que o projeto deixou de citar `trilha/`, com o commit, e só uma change arquivada do OpenSpec ainda a cita
- **THEN** ele termina com o código de saída 0, e o projeto não tem mais `trilha`
- **AND** a saída diz que o link de transição saiu porque nenhum arquivo cita mais `trilha/`, e pede para reabrir a sessão do Claude Code, conferir os arquivos locais que o git não versiona e trocar o `core.hooksPath` dos outros clones

#### Scenario: Busca que falha
- **WHEN** a busca das citações falha (o `git grep` sai com erro) num projeto com o link de transição
- **THEN** o link fica, e a saída diz que a busca falhou

#### Scenario: Configuração local que liga a trava antiga
- **WHEN** o `.claude/settings.local.json` do projeto, que o git ignora, cita `trilha/guarda.py`
- **THEN** a busca das citações o acha, e o link fica
