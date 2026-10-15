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

### Requirement: Comando de instalação por máquina
O `kit.py novo` e o `kit.py atualizar` SHALL imprimir o comando que cada máquina roda uma vez para instalar o plugin no projeto, `claude plugin install sdd@trilha-ai --scope project`, sem rodá-lo.

#### Scenario: Comando no projeto novo
- **WHEN** o `kit.py novo` cria um projeto
- **THEN** a saída cita `claude plugin install sdd@trilha-ai --scope project`

#### Scenario: Comando na atualização
- **WHEN** o `kit.py atualizar` termina sem recusa
- **THEN** a saída cita `claude plugin install sdd@trilha-ai --scope project`

### Requirement: Padrões técnicos do projeto
O projeto SHALL receber do kit o arquivo `sdd/padroes-tecnicos.md`, que ele pode ajustar: o `kit.py novo` o cria do modelo, e o `kit.py atualizar` só o cria quando falta, avisando, sem mudar o que o projeto escreveu nele.

#### Scenario: Projeto novo com os padrões
- **WHEN** o `kit.py novo` cria um projeto
- **THEN** o `sdd/padroes-tecnicos.md` é igual ao `modelo/sdd/padroes-tecnicos.md` do kit
- **AND** o `scripts/check.sh` do projeto termina com o código de saída 0

#### Scenario: Padrões ajustados pelo projeto
- **WHEN** o `sdd/padroes-tecnicos.md` do projeto difere do modelo e o `kit.py atualizar` roda
- **THEN** o arquivo continua como o projeto o deixou

#### Scenario: Projeto sem os padrões
- **WHEN** o projeto não tem o `sdd/padroes-tecnicos.md` e o `kit.py atualizar` roda
- **THEN** o arquivo passa a existir, igual ao modelo
- **AND** a ferramenta avisa que ele foi criado do modelo do kit
