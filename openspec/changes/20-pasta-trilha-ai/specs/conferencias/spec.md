## MODIFIED Requirements

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

### Requirement: Travas desligadas pela configuração
A conferência das regras SHALL avisar, sem falhar, cada trava desligada: a do commit, quando o `core.hooksPath` do clone não é `trilha-ai/hooks`; a do Claude Code, quando o `.claude/settings.json` não liga o `trilha-ai/guarda.py` ou quando o `disableAllHooks` que vale no projeto é verdadeiro, lido do `.claude/settings.local.json`, que prevalece, e do `.claude/settings.json`.

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


## ADDED Requirements

### Requirement: Link de transição da pasta antiga no kit
O kit SHALL manter `modelo/trilha` como link simbólico para `modelo/trilha-ai`, para a conferência das regras de um projeto de antes da 2.19, que procura a pasta pelo nome antigo, achar a do kit e comparar a do projeto com a tag da versão dele.

#### Scenario: Projeto da 2.18 com o kit novo ao lado
- **WHEN** a conferência das regras de um projeto feito pelo kit na versão 2.18, ainda na `trilha/`, roda com a pasta do kit 2.19 indicada
- **THEN** ela não reprova pela pasta do kit, e termina com o código de saída 0
