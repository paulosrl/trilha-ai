## ADDED Requirements

### Requirement: Commit sugerido do atualizar
Quando o `kit.py atualizar` termina com o código 0 e o projeto mudou, ele SHALL sugerir uma mensagem de commit que diga o que mudou: "cópia do kit Trilha AI, comum A → B" quando a versão do comum muda ou a cópia trocou algum arquivo, e "os arquivos gerados pelo OpenSpec X" quando, com `--openspec`, o dry-run previu mudanças dentro do projeto. Quando as duas acontecem, a mensagem MUST trazer as duas partes, nessa ordem, unidas por ", e ".

#### Scenario: Só o OpenSpec muda
- **WHEN** o projeto está na versão do comum do kit, a cópia não troca nenhum arquivo, e o `kit.py atualizar --openspec` roda com um dry-run que lista a troca de uma skill do projeto
- **THEN** a saída traz "commit sugerido: chore(metodo): os arquivos gerados pelo OpenSpec X", com a versão do kit

#### Scenario: A cópia e o OpenSpec mudam
- **WHEN** o projeto está na versão do comum do kit, a `trilha/` dele difere da do kit, e o `kit.py atualizar --openspec` roda com um dry-run que lista a troca de uma skill do projeto
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V, e os arquivos gerados pelo OpenSpec X"

#### Scenario: Só a cópia muda, com o --openspec
- **WHEN** o projeto está na versão do comum do kit, a `trilha/` dele difere da do kit, e o `kit.py atualizar --openspec` roda com um dry-run sem mudança nenhuma
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V", sem citar o OpenSpec
