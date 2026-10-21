# Spec Delta

## ADDED Requirements

### Requirement: Conversa que passa por outra pasta
O intervalo entre dois eventos seguidos de uma conversa SHALL contar só quando os dois são do repositório. O intervalo que começa ou termina num evento com `cwd` fora dele MUST NOT contar.

#### Scenario: Saída e volta no meio da conversa
- **WHEN** uma conversa tem um pedido às 09:00 no repositório, ações da IA às 09:05 e às 09:20 noutra pasta e uma ação da IA às 09:28 de novo no repositório
- **THEN** nenhum minuto dessa conversa entra no dia

### Requirement: Repositório dentro do repositório
A conversa com `cwd` dentro de outro repositório git, aninhado na raiz, MUST NOT contar para a raiz: ela é do repositório aninhado.

#### Scenario: Clone dentro da raiz
- **WHEN** a raiz tem uma pasta `vendor/lib` que é um repositório git próprio, e uma conversa tem `cwd` nela
- **THEN** as horas dessa conversa não entram na apuração da raiz

### Requirement: Commits do usuário
A estimativa pelos commits SHALL considerar só os commits cujo e-mail de autor é o `user.email` do git do repositório. Sem `user.email`, MUST considerar todos.

#### Scenario: Commit de outro autor
- **WHEN** o `user.email` é o do usuário, e um dia sem conversa só tem um commit com o e-mail do Dependabot
- **THEN** esse dia não aparece na apuração

#### Scenario: Sem e-mail configurado
- **WHEN** o repositório não tem `user.email`, e um dia sem conversa tem um commit de qualquer autor
- **THEN** o dia aparece, estimado pelos commits

### Requirement: Linha de commit que não se entende
A linha do `git log` que o comando não entende SHALL ser ignorada, sem falhar, e a assinatura dos commits MUST NOT entrar na leitura, mesmo com `log.showSignature` ligado.

#### Scenario: Assinatura na saída do git
- **WHEN** o repositório tem `log.showSignature` ligado
- **THEN** o comando termina com o código de saída 0, e os dias dos commits aparecem

#### Scenario: Data em UTC com Z
- **WHEN** o `git log` traz a data de um commit como `2026-10-01T10:00:00Z`
- **THEN** o commit conta no dia 01/10/2026

### Requirement: Sessão de commits mínima
A sessão de commits SHALL durar pelo menos 1 minuto: quando o corte na meia-noite a deixaria mais curta, ela MUST terminar 1 minuto depois do começo.

#### Scenario: Commit à meia-noite em ponto
- **WHEN** o único commit de um dia sem conversa é às 00:00:00
- **THEN** o dia aparece, com 1 minuto estimado

### Requirement: Página com os dados uma vez
A página SHALL ter os dados da apuração só no bloco de dados, e o nome do repositório MUST entrar no título com os caracteres especiais de HTML protegidos.

#### Scenario: Dados uma vez
- **WHEN** a página é gerada
- **THEN** a lista dos dias aparece uma vez só no arquivo

#### Scenario: Nome com caracteres especiais
- **WHEN** a raiz se chama `a<b__DADOS__`
- **THEN** o título da página traz `a&lt;b__DADOS__`, e a lista dos dias continua aparecendo uma vez só

### Requirement: Repositório que mudou de pasta
Quando não há resumo para o caminho da raiz, mas há outro resumo com o mesmo nome de repositório e outro caminho, o comando SHALL avisar, sem falhar, citando o resumo encontrado.

#### Scenario: Pasta trocada
- **WHEN** o comando já rodou com a raiz em `/a/proj`, e roda agora com ela em `/b/proj`
- **THEN** a saída traz um aviso que cita o resumo de `/a/proj`
- **AND** o comando termina com o código de saída 0
