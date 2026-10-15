# Proposal

## Why

O plugin `sdd` hoje se instala para o usuário inteiro, e as descrições das três skills entram em toda sessão de todo repositório da máquina, inclusive fora do método (decisão D4 da auditoria de 2026-10-15, achado F10). Além disso, os padrões técnicos do autor (PostgreSQL com pgvector, Python com `uv`, Node com `pnpm`, Docker) estão dentro da skill `tdd`, a camada reutilizável: quem adota o método com outros padrões precisa editar a própria skill (F21). E o padrão de Python ali usa a sintaxe do Poetry (`python = ">=3.12.3"`) numa seção que proíbe o Poetry (F22).

## What Changes

- O modelo do `.claude/settings.json` (`modelo/claude-settings.json`) passa a declarar o plugin: `enabledPlugins` com `sdd@trilha-ai` ligado e `extraKnownMarketplaces` com o marketplace `trilha-ai` (o GitHub `paulosrl/trilha-ai`).
- O `kit.py novo` e o `kit.py atualizar` somam essas duas declarações ao `.claude/settings.json` do projeto, sem mudar o que o projeto já declarou (nem o plugin que ele tiver desligado), e imprimem o comando que cada máquina roda uma vez: `claude plugin install sdd@trilha-ai --scope project`.
- A conferência do método passa a mandar instalar com `--scope project` e a consultar a lista de plugins do Claude Code de dentro da pasta do projeto, porque o "ligado" que a lista devolve depende do `.claude/settings.json` da pasta em que ela roda.
- Os padrões técnicos saem da skill `tdd` para um modelo novo, `modelo/sdd/padroes-tecnicos.md`, que o projeto recebe como `sdd/padroes-tecnicos.md` e pode ajustar. A skill lê esse arquivo quando ele existe; sem ele, recomenda só pela entrevista. No modelo, o Python vai pela sintaxe do `uv` (`requires-python`, na seção `[project]`).
- O README do kit e o do plugin passam a ensinar a instalação por projeto e como tirar a instalação do usuário depois que os projetos da máquina declararem o plugin.
- O kit vai à versão 2.2 (o comum "Versão 2.2", o plugin 2.2.0).

**Fora desta change:** encurtar as descrições das skills, a outra metade do F10 (item 8 do plano); tirar o plugin da instalação do usuário nesta máquina, que é da máquina e só cabe depois da migração dos projetos (item 10); a migração dos projetos reais (item 10); o resto do README e o mapa (item 9); a revisão de texto do comum (item 8).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `ferramenta-do-kit`: o projeto novo e o atualizado passam a declarar o plugin no `.claude/settings.json`, com o comando de instalação por máquina, e a receber o `sdd/padroes-tecnicos.md`.
- `conferencias`: o aviso do plugin ausente passa ao comando com `--scope project`, e a lista de plugins é lida da pasta do projeto.
- `plugin-sdd`: a skill `tdd` passa a ler os padrões técnicos do projeto, e não a trazê-los.

## Impact

- Kit: `modelo/claude-settings.json`, o modelo novo `modelo/sdd/padroes-tecnicos.md`, `ferramentas/kit.py`, `modelo/trilha/confere_metodo.py`, `plugins/sdd/skills/tdd/SKILL.md`, `modelo/esqueleto-CLAUDE.md` (a lista de `sdd/`), `README.md`, `plugins/sdd/README.md`, `testes/test_kit.py`, a versão no `modelo/trilha/CLAUDE-comum.md` e no `plugins/sdd/.claude-plugin/plugin.json`.
- Projetos: na próxima atualização, ganham a declaração do plugin e o `sdd/padroes-tecnicos.md` (com o aviso de arquivo criado do modelo). Em cada máquina, o plugin passa a valer por projeto depois do `claude plugin install sdd@trilha-ai --scope project`; enquanto a instalação do usuário existir, ela continua valendo em todos os repositórios.
- A skill `tdd` de um plugin 2.2 num projeto ainda na 2.1 não acha o `sdd/padroes-tecnicos.md` e recomenda sem os padrões; a conferência já avisa a versão do plugin diferente da do projeto.
