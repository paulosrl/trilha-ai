"""A trava do Claude Code: barra, antes de rodar, o comando que o método proíbe.

Ligada no .claude/settings.json como hook PreToolUse do Bash. Lê o pedido (JSON) da entrada e
sai com 2, que bloqueia o comando e mostra o motivo ao Claude, ou com 0, que o deixa passar.
Lê as palavras de cada comando, como o shell: o texto entre aspas (a mensagem de um commit) não é
opção; o comando vale na posição de comando, depois das palavras do shell (if, then, do…) e dos
comandos que envolvem outro (timeout, xargs, eval…); o texto de um bash -c, de um <<< e de uma
crase é lido como comando também. Uma falha da própria trava barra, nunca libera.
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
SEM_TRAVA = "a trava do commit (core.hooksPath em trilha/hooks) não se desliga; se barrar, pergunte"
PKILL = "pkill -f e pgrep -f casam o próprio shell; use o PID"
MERGE = "o merge da change é com merge commit (gh pr merge --merge --delete-branch), passo 7"
SEPARADORES = ";&|()<>\n`"
PREFIXOS = ("sudo", "env", "command", "time", "nohup", "exec", "builtin", "setsid", "chronic")
PREFIXOS += ("unbuffer", "eval", "watch", "nice", "ionice", "stdbuf", "timeout", "xargs")
PALAVRAS_DO_SHELL = ("if", "then", "else", "elif", "do", "while", "until", "!", "{", "}")
# As opções que levam valor separado, nos comandos que envolvem outro.
COM_VALOR = {"nice": ("-n",), "ionice": ("-c", "-n"), "xargs": ("-I", "-n", "-P", "-L", "-d", "-s")}
COM_VALOR |= {"timeout": ("-s", "-k"), "watch": ("-n",), "env": ("-u",), "sudo": ("-u", "-g")}
# As opções globais do git que levam valor, e as do gh pr merge.
DO_GIT = ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env")
DO_MERGE = ("-R", "--repo", "-b", "--body", "-t", "--subject", "-F", "--body-file", "-A")
DO_MERGE += ("--author-email", "--match-head-commit")
SHELLS = ("sh", "bash", "zsh", "dash", "ksh")
PRAZO_DO_GH = 30  # segundos; o prazo do hook no Claude Code é maior
HEREDOC = re.compile(r"(?<!<)<<(-?)(?!<)\s*(['\"]?)([\w.-]+)\2")


def _sem_corpo_de_heredoc(texto: str) -> str:
    """O texto sem o corpo de cada heredoc, que é dado e não comando (um Markdown que cita um
    comando proibido), salvo o que um shell recebe para rodar (bash <<EOF)."""
    linhas, saida, i = texto.split("\n"), [], 0
    while i < len(linhas):
        linha = linhas[i]
        saida.append(linha)
        i += 1
        for achado in HEREDOC.finditer(linha):
            antes = linha[: achado.start()].split()
            if any(p.rsplit("/", 1)[-1] in SHELLS for p in antes):
                continue
            delimitador, com_tab = achado.group(3), achado.group(1)
            while (
                i < len(linhas)
                and (linhas[i].lstrip("\t") if com_tab else linhas[i]) != delimitador
            ):
                i += 1
            i += 1  # a linha do delimitador
    return "\n".join(saida)


def _palavras(texto: str) -> list[str]:
    """As palavras e os separadores, como o shell os lê: a linha continuada (\\ no fim) se junta
    à seguinte, o corpo do heredoc sai, e o # não é comentário (no bash, só no começo de uma
    palavra, e o fim da linha é outro comando). Aspa sem par: lidas sem as aspas."""
    texto = _sem_corpo_de_heredoc(texto.replace("\\\n", ""))
    for tentativa in (texto, texto.replace("'", " ").replace('"', " ")):
        lexer = shlex.shlex(tentativa, posix=True, punctuation_chars=SEPARADORES)
        lexer.whitespace_split = True
        lexer.whitespace = " \t\r"
        lexer.commenters = ""
        try:
            return list(lexer)
        except ValueError:
            continue
    return texto.split()


def _aninhado(anterior: str, comando: list[str], palavra: str) -> bool:
    """O texto com espaço de um bash -c (ou -lc, -xc…) ou de um <<<, que o shell roda; o -c de
    outro comando (git -c chave=valor) não é shell."""
    if " " not in palavra and "\n" not in palavra:
        return False
    if anterior == "<<<":
        return True
    shell = any(p.rsplit("/", 1)[-1] in SHELLS for p in comando)
    return shell and bool(re.fullmatch(r"-[a-zA-Z]*c[a-zA-Z]*", anterior))


def _comandos(texto: str) -> list[list[str]]:
    """Os comandos simples de uma linha de shell, cada um com as suas palavras."""
    palavras = _palavras(texto)
    comandos: list[list[str]] = [[]]
    aninhados: list[list[str]] = []  # à parte: as palavras seguintes são do comando de fora
    for anterior, palavra in zip(["", *palavras], palavras):
        if palavra and set(palavra) <= set(SEPARADORES):
            comandos.append([])
            continue
        if _aninhado(anterior, comandos[-1], palavra):
            aninhados.extend(_comandos(palavra))
        comandos[-1].append(palavra)
    return [comando for comando in comandos + aninhados if comando]


def _no_lugar_de_comando(palavras: list[str]) -> list[str]:
    """As palavras a partir do comando de verdade: sem as palavras do shell, as atribuições
    (X=y) e os comandos que envolvem outro, com as opções deles."""
    i = 0
    while i < len(palavras):
        palavra = palavras[i]
        nome = palavra.rsplit("/", 1)[-1]
        if palavra in PALAVRAS_DO_SHELL or re.fullmatch(r"[A-Za-z_]\w*=.*", palavra, re.DOTALL):
            i += 1
        elif nome in PREFIXOS:
            i += 1
            while i < len(palavras) and palavras[i].startswith("-"):
                i += 2 if palavras[i] in COM_VALOR.get(nome, ()) else 1
            if (
                nome == "timeout"
                and i < len(palavras)
                and re.fullmatch(r"[\d.]+[smhd]?", palavras[i])
            ):
                i += 1
        else:
            break
    return palavras[i:]


def _curtas(palavra: str) -> str:
    """As letras de um grupo de opções curtas (-uf → uf); vazio se a palavra não é um."""
    return palavra[1:] if re.fullmatch(r"-[a-zA-Z]+", palavra) else ""


def _do_git(palavras: list[str]) -> tuple[list[str], str, list[str]] | None:
    """As opções globais, o subcomando e o resto de um comando git; None se não é o git."""
    if not palavras or palavras[0].rsplit("/", 1)[-1] != "git":
        return None
    i = 1
    while i < len(palavras) and palavras[i].startswith("-"):
        i += 2 if palavras[i] in DO_GIT else 1
    if i >= len(palavras):
        return palavras[1:], "", []
    return palavras[1:i], palavras[i], palavras[i + 1 :]


def _desliga_a_trava(globais: list[str], subcomando: str, resto: list[str]) -> bool:
    """O core.hooksPath com outro valor num -c (ou --config-env), ou gravado ou apagado pelo
    git config; a leitura e o valor trilha/hooks passam."""
    for anterior, palavra in zip(["", *globais], globais):
        if anterior in ("-c", "--config-env"):
            par = palavra
        elif palavra.startswith("-c") and palavra != "-c":  # -ccore.hooksPath=…
            par = palavra[2:]
        elif palavra.startswith("--config-env="):
            par = palavra.removeprefix("--config-env=")
        else:
            continue
        chave, _, valor = par.partition("=")
        # No --config-env, o valor é o nome de uma variável: qualquer um desliga.
        do_ambiente = "--config-env" in (anterior, palavra.split("=", 1)[0])
        if chave.lower() == "core.hookspath" and (do_ambiente or valor != "trilha/hooks"):
            return True
    if subcomando != "config":
        return False
    chaves = [i for i, p in enumerate(resto) if p.lower() == "core.hookspath"]
    if not chaves:
        return False
    if {"--unset", "--unset-all", "unset"} & set(resto):
        return True
    valor = [p for p in resto[chaves[0] + 1 :] if not p.startswith("-")]
    return bool(valor) and valor[0] != "trilha/hooks"


def _forcado(resto: list[str]) -> bool:
    for palavra in resto:
        longa = palavra.split("=", 1)[0]
        if "f" in _curtas(palavra) or palavra.startswith("+"):
            return True
        if longa.startswith("--force") and longa != "--force-if-includes":
            return True
        if len(longa) >= 5 and "--force".startswith(longa):  # --for, --forc: abreviações
            return True
        if len(longa) >= 4 and "--mirror".startswith(longa):
            return True
    return False


def _sem_verificar(palavras: list[str]) -> bool:
    return any(
        len(p) >= 9 and p.startswith("--no-veri") and "--no-verify".startswith(p) for p in palavras
    )


def _motivo_simples(palavras: list[str]) -> str:
    if _sem_verificar(palavras):
        return SEM_VERIFICAR
    git = _do_git(palavras)
    if git is not None:
        globais, subcomando, resto = git
        if _desliga_a_trava(globais, subcomando, resto):
            return SEM_TRAVA
        if subcomando == "push" and _forcado(resto):
            return FORCADO
        # -n é o --no-verify do commit; num grupo, só antes da letra que leva valor
        # (-mn é mensagem).
        if subcomando == "commit" and any("n" in re.split("[mFcCt]", _curtas(p))[0] for p in resto):
            return SEM_VERIFICAR
    nome = palavras[0].rsplit("/", 1)[-1] if palavras else ""
    if nome in ("pkill", "pgrep") and any(p == "--full" or "f" in _curtas(p) for p in palavras[1:]):
        return PKILL
    return ""


def _motivo_do_merge(palavras: list[str], gh_repo: str = "") -> str:
    if (
        len(palavras) < 3
        or palavras[0].rsplit("/", 1)[-1] != "gh"
        or palavras[1:3] != ["pr", "merge"]
    ):
        return ""
    alvo, repo, i, curtas = [], [], 3, ""
    merge = palavras[3:]
    while i < len(palavras):
        palavra = palavras[i]
        if palavra in DO_MERGE:
            if palavra in ("-R", "--repo") and i + 1 < len(palavras):
                repo = ["--repo", palavras[i + 1]]
            i += 2
            continue
        if palavra.startswith("--repo="):
            repo = ["--repo", palavra.split("=", 1)[1]]
        elif palavra.startswith("-"):
            curtas += _curtas(palavra)
        else:
            alvo.append(palavra)
        i += 1
    repo = repo or (["--repo", gh_repo] if gh_repo else [])
    com_merge = "--merge" in merge or "m" in curtas
    if not com_merge or {"--squash", "--rebase"} & set(merge) or set(curtas) & {"s", "r"}:
        return MERGE
    try:
        checks = subprocess.run(
            ["gh", "pr", "checks", *alvo[:1], *repo],
            capture_output=True,
            text=True,
            check=False,
            timeout=PRAZO_DO_GH,
        )
    except OSError:
        return "o gh não está instalado; sem ele, a verificação do PR não foi conferida"
    except subprocess.TimeoutExpired:
        return f"a verificação do PR (gh pr checks) não respondeu em {PRAZO_DO_GH} s; tente de novo"
    if checks.returncode != 0:
        return "a verificação do PR não está verde (gh pr checks); o merge só com ela verde"
    return ""


def _motivo(texto: str) -> str:
    for palavras in _comandos(texto):
        comando = _no_lugar_de_comando(palavras)
        antes = palavras[: len(palavras) - len(comando)]
        gh_repo = next((p.split("=", 1)[1] for p in antes if p.startswith("GH_REPO=")), "")
        motivo = _motivo_simples(comando) or _motivo_do_merge(comando, gh_repo)
        if motivo:
            return motivo
    return ""


def main() -> int:
    try:
        pedido = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    entrada = pedido.get("tool_input") if isinstance(pedido, dict) else None
    comando = entrada.get("command") if isinstance(entrada, dict) else None
    if not isinstance(comando, str) or not comando:
        return 0
    try:
        motivo = _motivo(comando)
    except Exception as erro:  # noqa: BLE001 - a trava que falha barra, nunca libera
        motivo = f"a trava falhou ao ler o comando ({erro!r}); confira-o e pergunte"
    if motivo:
        print(f"bloqueado pela trava do método: {motivo}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
