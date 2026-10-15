"""A trava do Claude Code: barra, antes de rodar, o comando que o método proíbe.

Ligada no .claude/settings.json como hook PreToolUse do Bash. Lê o pedido (JSON) da entrada e
sai com 2, que bloqueia o comando e mostra o motivo ao Claude, ou com 0, que o deixa passar.
Copiada sem mudar; uma trava que bloquear algo legítimo volta ao usuário, nunca é contornada.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys

REGRAS = (
    (
        r"\bgit\s+push\b.*(\s--force\b|\s--force-with-lease\b|\s-f\b|\s\+\S)",
        "envio forçado reescreve a história no GitHub; o método nunca o usa",
    ),
    (r"--no-verify\b", "a verificação não se pula; se ela barrar algo legítimo, pergunte"),
    (r"\b(pkill|pgrep)\s+(-\w*\s+)*-\w*f", "pkill -f e pgrep -f casam o próprio shell; use o PID"),
    (
        r"\bgh\s+pr\s+merge\b(?!.*\s--merge\b)|\bgh\s+pr\s+merge\b.*\s(--squash|--rebase|-s|-r)\b",
        "o merge da change é com merge commit (gh pr merge --merge --delete-branch), passo 7",
    ),
)


def _motivo(comando: str) -> str:
    for padrao, motivo in REGRAS:
        if re.search(padrao, comando):
            return motivo
    merge = re.search(r"\bgh\s+pr\s+merge\b(.*)", comando)
    if merge:
        try:
            tokens = shlex.split(merge.group(1).split("&&")[0])
        except ValueError:
            tokens = []
        alvo = [t for t in tokens if not t.startswith("-")]
        try:
            checks = subprocess.run(
                ["gh", "pr", "checks", *alvo[:1]], capture_output=True, text=True, check=False
            )
        except OSError:
            return "o gh não está instalado; sem ele, a verificação do PR não foi conferida"
        if checks.returncode != 0:
            return "a verificação do PR não está verde (gh pr checks); o merge só com ela verde"
    return ""


def main() -> int:
    try:
        pedido = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    comando = (pedido.get("tool_input") or {}).get("command") or ""
    motivo = _motivo(comando)
    if motivo:
        print(f"bloqueado pela trava do método: {motivo}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
