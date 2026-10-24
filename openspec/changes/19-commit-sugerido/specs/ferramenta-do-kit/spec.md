## ADDED Requirements

### Requirement: Commit sugerido do atualizar
Quando o `kit.py atualizar` termina com o código 0 e o projeto mudou, ele SHALL sugerir o commit com as partes do que mudou: "cópia do kit Trilha AI, comum A → B" quando a versão do comum muda ou a cópia trocou algum arquivo, e "os arquivos gerados pelo OpenSpec X" (X, a versão do CI do modelo do kit) quando, com `--openspec`, o update mudou arquivos do projeto. Com as duas, a mensagem MUST trazê-las nessa ordem, unidas por ", e ". Nos cenários, V é a versão do comum do kit.

#### Scenario: Só o OpenSpec muda
- **WHEN** o projeto está na versão do comum do kit, a cópia não troca nenhum arquivo, e o `kit.py atualizar --openspec` roda com um dry-run que lista a troca de uma skill do projeto
- **THEN** a saída traz "commit sugerido: chore(metodo): os arquivos gerados pelo OpenSpec X"

#### Scenario: A cópia e o OpenSpec mudam
- **WHEN** o projeto está na versão do comum do kit, a `trilha/` dele difere da do kit, e o `kit.py atualizar --openspec` roda com um dry-run que lista a troca de uma skill do projeto
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V, e os arquivos gerados pelo OpenSpec X"

#### Scenario: Só a cópia muda, com o --openspec
- **WHEN** o projeto está na versão do comum do kit, a `trilha/` dele difere da do kit, e o `kit.py atualizar --openspec` roda com um dry-run sem mudança nenhuma
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V", sem citar o OpenSpec

#### Scenario: O dry-run previu, e o update não mudou
- **WHEN** a `trilha/` do projeto difere da do kit, na mesma versão do comum, e o `kit.py atualizar --openspec` roda com um dry-run que lista a troca de uma skill que o update não faz
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V", sem citar o OpenSpec

#### Scenario: O update mudou sem o dry-run prever
- **WHEN** a cópia não troca nenhum arquivo, na mesma versão do comum, e o `kit.py atualizar --openspec` roda com um dry-run sem mudança nenhuma, mas o update troca uma skill do projeto
- **THEN** a saída traz "commit sugerido: chore(metodo): os arquivos gerados pelo OpenSpec X"

#### Scenario: Sem o --openspec
- **WHEN** o projeto está na versão do comum do kit, a `trilha/` dele difere da do kit, e o `kit.py atualizar` roda sem `--openspec`
- **THEN** a saída traz "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum V → V", sem citar o OpenSpec
