## ADDED Requirements

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
