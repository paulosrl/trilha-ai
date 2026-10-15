#!/usr/bin/env bash
# A parte fixa da verificação de um projeto do método (em trilha/, copiada sem mudar). O
# scripts/check.sh do projeto a chama, com um --vizinho <nome> por repositório ao lado que o
# ANDAMENTO.md não pode citar, e depois roda a parte da stack.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

# As regras (CLAUDE.md, trilha/CLAUDE-comum.md, ANDAMENTO.md), com a pasta trilha/ comparada à do
# kit quando ele está ao lado (ou em TRILHA_AI).
FONTE="${TRILHA_AI:-../trilha-ai}"
if [ -d "$FONTE" ]; then
  python3 -I trilha/confere_regras.py . --fonte "$FONTE"
else
  echo "aviso: $FONTE não existe; a pasta trilha/ não foi comparada com a do kit" >&2
  python3 -I trilha/confere_regras.py .
fi
# Os documentos do método (decomposição, TDD, ANDAMENTO.md) e o plugin sdd instalado.
python3 -I trilha/confere_metodo.py "$@"
# Os specs e as changes do OpenSpec, sem o modo estrito, que reprova os avisos (requisito longo,
# por exemplo); num projeto ainda sem specs, ele passa.
if command -v openspec >/dev/null; then
  openspec validate --all --no-interactive
else
  echo "aviso: o openspec não está instalado; os specs e as changes não foram validados" >&2
fi
