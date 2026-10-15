# Spec Delta

## ADDED Requirements

### Requirement: Comum importado da pasta do método
A conferência das regras SHALL exigir que o `CLAUDE.md` do projeto importe o comum pela linha `@trilha/CLAUDE-comum.md` e que o comum exista em `trilha/CLAUDE-comum.md`, reprovando, com o motivo, o projeto que não cumprir.

#### Scenario: Projeto no layout da pasta do método
- **WHEN** a conferência das regras roda num projeto feito do kit, com `trilha/CLAUDE-comum.md` e o `CLAUDE.md` importando `@trilha/CLAUDE-comum.md`
- **THEN** ela termina com o código de saída 0

#### Scenario: Importação antiga
- **WHEN** o `CLAUDE.md` importa `@CLAUDE-comum.md` em vez de `@trilha/CLAUDE-comum.md`
- **THEN** a conferência das regras reprova, citando a linha que falta

### Requirement: Cópia idêntica da pasta do método
Com a pasta do kit indicada, a conferência das regras SHALL comparar a pasta `trilha/` do projeto com a `modelo/trilha/` do kit, arquivo a arquivo, e MUST reprovar, nomeando o arquivo, quando um deles estiver diferente, faltar no projeto ou existir só no projeto.

#### Scenario: Pasta igual à do kit
- **WHEN** a pasta `trilha/` do projeto tem os mesmos arquivos, com o mesmo conteúdo, que a `modelo/trilha/` do kit
- **THEN** a conferência das regras não reprova pela cópia

#### Scenario: Trava editada no projeto
- **WHEN** o `trilha/guarda.py` do projeto difere do kit
- **THEN** a conferência das regras reprova, citando `trilha/guarda.py`

#### Scenario: Arquivo faltando ou a mais
- **WHEN** falta no projeto um arquivo que a pasta do kit tem, ou o projeto tem em `trilha/` um arquivo que o kit não tem
- **THEN** a conferência das regras reprova, citando o arquivo

### Requirement: Verificação fixa do projeto
O `trilha/verifica.sh` SHALL rodar, nesta ordem, a conferência das regras (com a pasta do kit quando ela está ao lado do projeto ou em `TRILHA_AI`, e com aviso quando não está), a conferência do método (repassando os argumentos que receber, como `--vizinho`) e o `openspec validate --all --no-interactive`, e MUST terminar com erro quando qualquer um deles falhar.

#### Scenario: Projeto novo
- **WHEN** o `scripts/check.sh` de um projeto recém-criado pelo kit roda, chamando o `trilha/verifica.sh`
- **THEN** ele termina com o código de saída 0

#### Scenario: Vizinho repassado
- **WHEN** o `scripts/check.sh` chama `bash trilha/verifica.sh --vizinho outro` e o `ANDAMENTO.md` cita `outro`
- **THEN** a verificação reprova, citando `outro`

#### Scenario: Spec inválido
- **WHEN** o projeto tem um spec do OpenSpec com um requisito sem SHALL nem MUST e o `openspec` está instalado
- **THEN** a verificação termina com erro

#### Scenario: OpenSpec ausente
- **WHEN** o comando `openspec` não existe no PATH
- **THEN** a verificação avisa que os specs não foram validados e não falha por isso
