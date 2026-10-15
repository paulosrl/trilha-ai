"""A trava do Claude Code: barra, antes de rodar, o comando que o método proíbe.

Ligada no .claude/settings.json como hook PreToolUse do Bash. Lê o pedido (JSON) da entrada e
sai com 2, que bloqueia o comando e mostra o motivo ao Claude, ou com 0, que o deixa passar.
Lê as palavras de cada comando, como o shell: o texto entre aspas (a mensagem de um commit) não é
opção, e o de um -c (bash -c "...") é lido como comando também.
Copiada sem mudar; uma trava que bloquear algo legítimo volta ao usuário, nunca é contornada.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys

FORCADO = "envio forçado reescreve a história no GitHub; o método nunca o usa"
SEM_VERIFICAR = "a verificação não se pula; se ela barrar algo legítimo, pergunte"
PKILL = "pkill -f e pgrep -f casam o próprio shell; use o PID"
MERGE = "o merge da change é com merge commit (gh pr merge --merge --delete-branch), passo 7"
SEPARADORES = ";&|()<>\n"
PREFIXOS = ("sudo", "env", "command", "time", "nohup", "exec")


def _comandos(texto: str) -> list[list[str]]:
    """Os comandos simples de uma linha de shell, cada um com as suas palavras."""
    lexer = shlex.shlex(texto, posix=True, punctuation_chars=SEPARADORES)
    lexer.whitespace_split = True
    lexer.whitespace = " \t\r"
    try:
        palavras = list(lexer)
    except ValueError:  # aspas sem par: as palavras cruas
        palavras = texto.split()
    comandos: list[list[str]] = [[]]
    for anterior, palavra in zip(["", *palavras], palavras):
        if palavra and set(palavra) <= set(SEPARADORES):
            comandos.append([])
            continue
        comandos[-1].append(palavra)
        if anterior == "-c" and " " in palavra:
            comandos.extend(_comandos(palavra))
    return [comando for comando in comandos if comando]


def _depois(palavras: list[str], programa: str, *sequencia: str) -> list[str] | None:
    """As palavras depois de `git … push` (o programa e a sequência), ou None se não é ele."""
    while palavras and (palavras[0] in PREFIXOS or re.fullmatch(r"\w+=\S*", palavras[0])):
        palavras = palavras[1:]
    if not palavras or palavras[0].rsplit("/", 1)[-1] != programa:
        return None
    posicao = 1
    for nome in sequencia:
        if nome not in palavras[posicao:]:
            return None
        posicao = palavras.index(nome, posicao) + 1
    return palavras[posicao:]


def _curtas(palavra: str) -> str:
    """As letras de um grupo de opções curtas (-uf → uf); vazio se a palavra não é um."""
    return palavra[1:] if re.fullmatch(r"-[a-zA-Z]+", palavra) else ""


def _motivo_simples(palavras: list[str]) -> str:
    if "--no-verify" in palavras:
        return SEM_VERIFICAR
    push = _depois(palavras, "git", "push")
    if push is not None and any(
        p == "--force" or p.startswith(("--force-with-lease", "+")) or "f" in _curtas(p)
        for p in push
    ):
        return FORCADO
    commit = _depois(palavras, "git", "commit")
    # -n é o --no-verify do commit; num grupo, só antes da letra que leva valor (-mn é mensagem).
    if commit is not None and any("n" in re.split("[mFcCt]", _curtas(p))[0] for p in commit):
        return SEM_VERIFICAR
    for programa in ("pkill", "pgrep"):
        opcoes = _depois(palavras, programa)
        if opcoes is not None and any(p == "--full" or "f" in _curtas(p) for p in opcoes):
            return PKILL
    return ""


def _motivo_do_merge(palavras: list[str]) -> str:
    merge = _depois(palavras, "gh", "pr", "merge")
    if merge is None:
        return ""
    if "--merge" not in merge or {"--squash", "--rebase", "-s", "-r"} & set(merge):
        return MERGE
    alvo = [p for p in merge if not p.startswith("-")]
    try:
        checks = subprocess.run(
            ["gh", "pr", "checks", *alvo[:1]], capture_output=True, text=True, check=False
        )
    except OSError:
        return "o gh não está instalado; sem ele, a verificação do PR não foi conferida"
    if checks.returncode != 0:
        return "a verificação do PR não está verde (gh pr checks); o merge só com ela verde"
    return ""


def _motivo(texto: str) -> str:
    for palavras in _comandos(texto):
        motivo = _motivo_simples(palavras) or _motivo_do_merge(palavras)
        if motivo:
            return motivo
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
