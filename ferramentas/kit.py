"""O kit Trilha AI aplicado a um repositório: criar um projeto novo ou atualizar um existente.

Uso (Python 3 puro, sem dependências), de qualquer pasta:
    python3 ferramentas/kit.py novo <pasta>        # a pasta, o git e os arquivos do kit
    python3 ferramentas/kit.py atualizar <pasta>   # a cópia nova do que se copia sem mudar

Nenhum dos dois faz commit nem envia: o commit segue o CLAUDE-comum.md (a mensagem, a coautoria)
e o envio pede o "sim" do usuário. Esta pasta, ferramentas/, é só do kit e não se copia.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent

# Copiados sem mudar: a atualização os sobrescreve.
SEM_MUDAR = (
    "CLAUDE-comum.md",
    "scripts/confere_regras.py",
    "scripts/confere_metodo.py",
    "scripts/gerar_pagina_sdd.py",
    "scripts/pagina_sdd_modelo.html",
    "scripts/guarda.py",
    ".githooks/pre-commit",
)
# Preenchidos em cada projeto (destino: origem no kit): o projeto novo os recebe; a atualização
# só cria o que falta, sem tocar no que o projeto já preencheu.
A_PREENCHER = {
    "CLAUDE.md": "esqueleto-CLAUDE.md",
    "ANDAMENTO.md": "ANDAMENTO.md",
    "openspec/config.yaml": "openspec/config.yaml",
    "scripts/check.sh": "scripts/check.sh",
    ".gitignore": ".gitignore",
    ".github/workflows/verificacao.yml": "github-verificacao.yml",
    ".claude/settings.json": "claude-settings.json",
    ".github/dependabot.yml": "github-dependabot.yml",
}


class Recusa(Exception):
    """O repositório não está em condição de receber o kit; a mensagem diz por quê."""


def _git(pasta: Path, *args: str) -> str:
    saida = subprocess.run(
        ["git", "-C", str(pasta), *args], capture_output=True, text=True, check=False
    )
    if saida.returncode != 0:
        raise Recusa(f"git {' '.join(args)} falhou em {pasta}: {saida.stderr.strip()}")
    return saida.stdout.strip()


def _principal(pasta: Path) -> str:
    """A branch principal: a do origin/HEAD, lido localmente; sem ele, main ou, na falta, master."""
    try:
        return _git(pasta, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").split("/", 1)[1]
    except Recusa:
        branches = _git(pasta, "branch", "--format=%(refname:short)").split()
        return "master" if "master" in branches and "main" not in branches else "main"


def _versao(comum: Path) -> str:
    if not comum.is_file():
        return "?"
    achado = re.search(r"^Versão (\d+\.\d+)", comum.read_text(encoding="utf-8"), re.MULTILINE)
    return achado.group(1) if achado else "?"


def _copiar(destino: Path, nome: str, origem: str) -> None:
    alvo = destino / nome
    alvo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(KIT / origem, alvo)


def novo(pasta: Path) -> None:
    if pasta.exists() and any(pasta.iterdir()):
        raise Recusa(f"{pasta} já existe e não está vazia; o projeto novo nasce numa pasta vazia")
    pasta.mkdir(parents=True, exist_ok=True)
    _git(pasta, "init", "-q")
    _git(pasta, "symbolic-ref", "HEAD", "refs/heads/main")
    for nome in SEM_MUDAR:
        _copiar(pasta, nome, nome)
    for nome, origem in A_PREENCHER.items():
        _copiar(pasta, nome, origem)
    (pasta / "sdd").mkdir()
    _ligar_travas(pasta)
    print(f"criado: {pasta}, com o kit (comum {_versao(KIT / 'CLAUDE-comum.md')})")
    print("próximos passos (README do kit, a partir do passo 4):")
    print("  1. preencha o que está entre < e > no CLAUDE.md, no ANDAMENTO.md e no config.yaml;")
    print("  2. openspec init (sem sobrescrever o config.yaml) e codegraph init;")
    print("  3. bash scripts/check.sh, que deve terminar com ok;")
    print("  4. o primeiro commit e: gh repo create <nome> --private --source . --push")


def atualizar(pasta: Path) -> int:
    if not (pasta / ".git").exists():
        raise Recusa(f"{pasta} não é a raiz de um repositório git")
    if pasta.resolve() == KIT:
        raise Recusa("esta é a pasta do próprio kit")
    if _git(pasta, "status", "--porcelain"):
        raise Recusa("há trabalho não commitado; só o usuário decide se continua ou descarta")
    principal = _principal(pasta)
    if _git(pasta, "branch", "--show-current") != principal:
        raise Recusa(f"a cópia do kit é trabalho fora de change: vai à {principal}; mude para ela")
    andamento = pasta / "ANDAMENTO.md"
    if andamento.is_file() and re.search(
        r"\*\*Estado:\*\*\s*em andamento", andamento.read_text(encoding="utf-8")
    ):
        raise Recusa('o ANDAMENTO.md diz "em andamento"; termine a unidade em curso antes')

    antes = _versao(pasta / "CLAUDE-comum.md")
    for nome in SEM_MUDAR:
        _copiar(pasta, nome, nome)
    for nome, origem in A_PREENCHER.items():
        if not (pasta / nome).exists():
            _copiar(pasta, nome, origem)
            print(f"aviso: {nome} não existia e foi criado do modelo do kit; confira-o")
    _ligar_travas(pasta)
    _sincronizar_regras(pasta)
    if (pasta / "sdd").is_dir():
        _rodar(pasta, [sys.executable, "-I", "scripts/gerar_pagina_sdd.py"])

    regras = ["scripts/confere_regras.py", ".", "--fonte", str(KIT)]
    ok = _rodar(pasta, [sys.executable, "-I", *regras])
    ok = _rodar(pasta, [sys.executable, "-I", "scripts/confere_metodo.py"]) and ok
    if not any((pasta / ".claude").glob("**/*verify*")):
        print("aviso: o /opsx:verify não está instalado; ligue-o no perfil e rode openspec update")
    depois = _versao(KIT / "CLAUDE-comum.md")
    mudou = _git(pasta, "status", "--short")
    print(mudou or "nada mudou: o projeto já está na versão do kit")
    if not ok:
        print("FALHA: a conferência reprovou; os arquivos ficaram copiados, sem commit")
        return 1
    if mudou:
        print(f"commit sugerido: chore(metodo): cópia do kit Trilha AI, comum {antes} → {depois}")
    return 0


def _ligar_travas(pasta: Path) -> None:
    """A trava do commit (core.hooksPath, do clone) e a do Claude Code, somada ao settings.json."""
    _git(pasta, "config", "core.hooksPath", ".githooks")
    modelo = json.loads((KIT / "claude-settings.json").read_text(encoding="utf-8"))
    entrada = modelo["hooks"]["PreToolUse"][0]
    settings = pasta / ".claude" / "settings.json"
    atual = json.loads(settings.read_text(encoding="utf-8")) if settings.is_file() else {}
    lista = atual.setdefault("hooks", {}).setdefault("PreToolUse", [])
    if "scripts/guarda.py" not in json.dumps(lista):
        lista.append(entrada)
        settings.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(atual, ensure_ascii=False, indent=2) + "\n"
        settings.write_text(texto, encoding="utf-8")


def _regras(texto: str) -> str:
    """A parte do config.yaml que vem do kit: das regras por artefato até o fim."""
    return texto[texto.find("\nrules:") + 1 :] if "\nrules:" in texto else ""


def _sincronizar_regras(pasta: Path) -> None:
    """Atualiza as regras do config.yaml só se forem as de uma versão do kit, sem mudança."""
    config = pasta / "openspec" / "config.yaml"
    if not config.is_file():
        return
    texto = config.read_text(encoding="utf-8")
    atuais = _regras((KIT / "openspec" / "config.yaml").read_text(encoding="utf-8"))
    if not _regras(texto) or _regras(texto) == atuais:
        return
    # Toda versão do config.yaml que o kit já teve, e não só as das tags, que seguem o comum.
    for versao in _git(KIT, "log", "--format=%h", "--", "openspec/config.yaml").split():
        antigas = subprocess.run(
            ["git", "-C", str(KIT), "show", f"{versao}:openspec/config.yaml"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        if _regras(antigas) and _regras(antigas) == _regras(texto):
            config.write_text(texto[: texto.find("\nrules:") + 1] + atuais, encoding="utf-8")
            print(f"regras do openspec/config.yaml atualizadas: eram as do kit em {versao}")
            return
    print("aviso: o openspec/config.yaml tem regras próprias; compare-as com as do kit à mão")


def _rodar(pasta: Path, comando: list[str]) -> bool:
    saida = subprocess.run(comando, cwd=pasta, capture_output=True, text=True, check=False)
    for linha in (saida.stdout + saida.stderr).splitlines():
        print(f"  {linha}")
    return saida.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("acao", choices=("novo", "atualizar"))
    parser.add_argument("pasta", type=Path)
    args = parser.parse_args()
    try:
        if args.acao == "novo":
            novo(args.pasta)
            return 0
        return atualizar(args.pasta)
    except Recusa as recusa:
        print(f"recusado: {recusa}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
