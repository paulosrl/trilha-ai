# Padrões técnicos

O ponto de partida da skill `sdd:tdd` quando a entrevista chega a estas decisões: ela os confirma com o usuário, nunca os impõe, e o desvio vira ADR com a justificativa. Os padrões são do projeto: ajuste-os aqui antes do TDD e apague o que não valer; sem ponto de partida nenhum, apague o arquivo, que a atualização do kit não o recria.

**Banco de dados (quando a topologia pedir servidor):** PostgreSQL com extensão **pgvector** habilitada. Desvio (NoSQL, embarcado) exige razão registrada no ADR.

**Projetos Python:**
- Python ≥ 3.12.3 (`requires-python = ">=3.12.3"` na seção `[project]` do `pyproject.toml`)
- Pacotes exclusivamente via `uv` (`uv add`, `uv venv`, `uv run`, `uv sync`); `pip`/`poetry`/`pipenv` proibidos; `pyproject.toml` como único manifesto; `uv.lock` versionado como fonte de verdade da resolução
- Dependências com faixa de compatibilidade (`>=2.5,<3.0` ou `~=2.5`), nunca travadas (`==`) nem livres
- Lint/formatação `ruff`; testes `pytest`; tipos `mypy` ou `pyright`; CI mínima com lint + testes por push/PR

**Projetos Node.js/TypeScript** (mutuamente exclusivo com o bloco Python):
- Node na Active LTS vigente (confirme antes de travar; declare em `"engines"`); nunca versão em End of Life
- `pnpm` como gerenciador padrão; `npm`/`yarn` só com justificativa em ADR
- Dependências em caret range (`^`); lockfile versionado
- Lint/formatação `Biome`; testes `Vitest`; `strict: true` no `tsconfig.json`; CI mínima

**Docker (quando houver app + serviços):** `docker-compose.yml` em sintaxe v2 (sem chave `version:`), variáveis via `.env`, `Dockerfile` instalando com `uv` ou `pnpm` conforme a linguagem. Imagens de infraestrutura fixadas em major + variante (`postgres:16-alpine`, `node:26-alpine`) — nunca `latest`, nunca patch hiper-específico.

**Quando a topologia for programa local simples** (ADR-001 = local, usuário único): Docker e CI podem ser dispensados por ADR explícito ("complexidade não justificada pelo produto") — simplicidade também é decisão registrada.
