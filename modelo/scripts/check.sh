#!/usr/bin/env bash
# Verificação local do repositório, chamada antes de todo commit (regra do CLAUDE-comum.md).
# Rode-a sozinha e confira o código de saída; nunca a encadeie com um filtro.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

# Parte fixa: as regras do repositório (CLAUDE.md, CLAUDE-comum.md, ANDAMENTO.md), com o comum
# comparado ao do kit quando ele está ao lado (ou em TRILHA_AI).
FONTE="${TRILHA_AI:-../trilha-ai}"
if [ -d "$FONTE" ]; then
  python3 -I scripts/confere_regras.py . --fonte "$FONTE"
else
  echo "aviso: $FONTE não existe; a cópia do CLAUDE-comum.md não foi comparada com o kit" >&2
  python3 -I scripts/confere_regras.py .
fi
# Os documentos do método (decomposição, TDD, ANDAMENTO.md). Acrescente um --vizinho <nome> por
# repositório ao lado que o ANDAMENTO.md não pode citar.
python3 -I scripts/confere_metodo.py

# Parte da stack, decidida no TDD (etapa 2). Troque as linhas abaixo pelos comandos reais e
# apague este comentário. Exemplo para Python com uv:
#   uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest
echo "aviso: a parte da stack ainda não foi preenchida em scripts/check.sh (etapa 2)" >&2
