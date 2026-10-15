# ferramenta-do-kit Specification

## Purpose

Define o que a ferramenta do kit (`ferramentas/kit.py`) faz num repositório: criar um projeto novo no método e atualizar um existente para a versão do kit, inclusive migrar o layout antigo para a pasta `trilha/`, sem fazer commit nem envio.

## Requirements

### Requirement: Projeto novo com a pasta do método
O `kit.py novo` SHALL criar o projeto com a pasta `trilha/` igual à `modelo/trilha/` do kit, o `CLAUDE.md` importando `@trilha/CLAUDE-comum.md`, a trava do commit ligada em `trilha/hooks` e o hook do Claude Code apontando para `trilha/guarda.py`.

#### Scenario: Projeto novo verificado
- **WHEN** o `kit.py novo` cria um projeto numa pasta vazia
- **THEN** a pasta `trilha/` do projeto é igual à `modelo/trilha/` do kit
- **AND** `git config core.hooksPath` responde `trilha/hooks`
- **AND** o `.claude/settings.json` liga `trilha/guarda.py`
- **AND** o `scripts/check.sh` do projeto termina com o código de saída 0

#### Scenario: Trava do commit no projeto novo
- **WHEN** o projeto novo recebe um commit com o `CLAUDE.md` sem a importação do comum
- **THEN** a trava do commit o barra

### Requirement: Atualização da pasta do método por inteiro
O `kit.py atualizar` SHALL deixar a pasta `trilha/` do projeto igual à `modelo/trilha/` do kit, inclusive apagando dela o arquivo que o kit não tem mais, sem tocar no que o projeto preencheu fora dela.

#### Scenario: Arquivo que o kit tirou
- **WHEN** a pasta `trilha/` do projeto tem um arquivo que o kit não tem mais
- **THEN** depois do `kit.py atualizar` esse arquivo não existe
- **AND** a pasta é igual à do kit

### Requirement: Migração do layout antigo
Num projeto com as cópias do método na raiz, em `scripts/` e em `.githooks/pre-commit`, o `kit.py atualizar` SHALL levá-las para `trilha/` e apagar as antigas, trocar a importação do `CLAUDE.md` para `@trilha/CLAUDE-comum.md` (também quando as cópias já tiverem saído), o `core.hooksPath` para `trilha/hooks` e o hook do Claude Code para `trilha/guarda.py`, sem duplicá-lo e sem tocar em outros hooks do projeto.

#### Scenario: Projeto da versão 1.30 migrado
- **WHEN** o `kit.py atualizar` roda num projeto feito pelo kit na versão 1.30
- **THEN** não existem mais `CLAUDE-comum.md` na raiz, os `scripts/confere_*.py`, o `scripts/gerar_pagina_sdd.py`, o `scripts/pagina_sdd_modelo.html`, o `scripts/guarda.py` nem o `.githooks/pre-commit`
- **AND** o `CLAUDE.md` importa `@trilha/CLAUDE-comum.md`, o `core.hooksPath` é `trilha/hooks` e o `.claude/settings.json` liga só `trilha/guarda.py`, uma vez
- **AND** a conferência das regras e a do método passam

#### Scenario: Outro hook do projeto preservado
- **WHEN** o projeto tem, além do `.githooks/pre-commit`, um hook próprio em `.githooks/` (por exemplo, `pre-push`)
- **THEN** depois da migração esse hook continua em `.githooks/`, sem mudança
- **AND** a ferramenta avisa que ele não roda mais, porque a trava do commit passou a `trilha/hooks`, citando o arquivo

#### Scenario: Migração parcial
- **WHEN** as cópias soltas já saíram, mas o `CLAUDE.md` ainda importa `@CLAUDE-comum.md` (com ou sem espaço no fim da linha)
- **THEN** depois do `kit.py atualizar` o `CLAUDE.md` importa `@trilha/CLAUDE-comum.md`

### Requirement: Recusa da pasta trilha de outra coisa
O `kit.py atualizar` SHALL recusar, sem apagar nem copiar nada, o projeto que já tem uma pasta `trilha/` sem `trilha/CLAUDE-comum.md`, porque ela não é a do método.

#### Scenario: Pasta trilha do projeto
- **WHEN** o projeto tem `trilha/` com arquivos próprios e sem `trilha/CLAUDE-comum.md`
- **THEN** o `kit.py atualizar` recusa, com o motivo
- **AND** os arquivos da pasta continuam lá

### Requirement: Lista do método pelos arquivos versionados
O que o kit copia sem mudar SHALL ser a lista dos arquivos versionados no git em `modelo/trilha/`, e não o que estiver na pasta: arquivo não versionado ali não vai ao projeto.

#### Scenario: Arquivo solto na pasta do kit
- **WHEN** a pasta `modelo/trilha/` do kit tem um arquivo que o git não versiona
- **THEN** ele não está na lista do que se copia

### Requirement: Parte fixa do check.sh migrada
Na migração, quando o `scripts/check.sh` do projeto tiver a parte fixa do kit, o `kit.py atualizar` SHALL trocá-la pela chamada `bash trilha/verifica.sh`, preservando os argumentos e a continuação de linha da chamada antiga e o resto do arquivo; quando não tiver, SHALL deixar o arquivo como está e avisar o que trocar.

#### Scenario: Parte fixa do kit com vizinhos
- **WHEN** o `scripts/check.sh` tem o bloco `FONTE=…` até o `fi` e `python3 -I scripts/confere_metodo.py --vizinho trilha-ai \` seguido de outra linha
- **THEN** depois da migração o bloco não existe mais e a chamada é `bash trilha/verifica.sh --vizinho trilha-ai \`, com a linha seguinte e a parte da stack intactas

#### Scenario: Parte fixa alterada pelo projeto
- **WHEN** o `scripts/check.sh` não tem a parte fixa do kit e ainda chama `scripts/confere_*`, que a migração tirou
- **THEN** o arquivo fica como está
- **AND** a ferramenta diz que a chamada a `bash trilha/verifica.sh` deve ser posta à mão
- **AND** a atualização termina com o código de saída 1, sem sugerir o commit

### Requirement: Aviso da parte fixa que mudou no kit
O `kit.py atualizar` SHALL avisar cada linha que o kit acrescentou à parte fixa dos arquivos preenchidos desde a versão do projeto e que o projeto não tem, aceitando como presente só a linha igual ou a mesma linha seguida de espaço e argumentos.

#### Scenario: Chamada com os vizinhos
- **WHEN** o `scripts/check.sh` migrado tem `bash trilha/verifica.sh --vizinho trilha-ai \`
- **THEN** a ferramenta não avisa que falta `bash trilha/verifica.sh`

#### Scenario: Linha curta que falta
- **WHEN** o kit acrescentou à parte fixa a linha `fi` e o projeto só tem uma linha que começa com `fi` sem ser ela (por exemplo, `find .`)
- **THEN** a ferramenta avisa que falta `fi`

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
- **AND** continua ligando `trilha/guarda.py`

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
A soma do `.claude/settings.json` SHALL ler o `modelo/claude-settings.json` inteiro: a chave que falta no projeto entra, o objeto presente nos dois é somado chave por chave, e o item de lista do modelo entra quando nenhum item do projeto o contém; o valor que o projeto já deu MUST ficar. A trava do Claude Code de outra versão do kit (`scripts/guarda.py` ou `trilha/guarda.py` chamada de outro jeito) SHALL sair, com o grupo que só a tinha, e a do modelo entrar.

#### Scenario: Chave nova no modelo
- **WHEN** o modelo tem uma chave que o settings.json do projeto não tem
- **THEN** a soma a põe no projeto, sem trocar as que ele já tinha

#### Scenario: Trava de outra versão
- **WHEN** o grupo de `PreToolUse` do projeto tem a `trilha/guarda.py` chamada de outro jeito e um gancho próprio, e outro grupo só com a `scripts/guarda.py`
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
- **THEN** o arquivo é gerado de novo pelo `trilha/gerar_pagina_sdd.py`
