#!/usr/bin/env bash
# Verificação local do repositório, chamada antes de todo commit (regra do CLAUDE-comum.md).
# Rode-a sozinha e confira o código de saída; nunca a encadeie com um filtro.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

# Parte fixa: as regras, o método e os specs, pelo script do método. Acrescente um
# --vizinho <nome> por repositório ao lado que o ANDAMENTO.md não pode citar.
bash trilha/verifica.sh

# Parte da stack, decidida no TDD (etapa 2). Troque as linhas abaixo pelos comandos reais e
# apague este comentário. Exemplo para Python com uv:
#   uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest
echo "aviso: a parte da stack ainda não foi preenchida em scripts/check.sh (etapa 2)" >&2
