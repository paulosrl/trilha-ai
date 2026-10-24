"""O kit Trilha AI aplicado a um repositório: criar um projeto novo ou atualizar um existente.

Uso (Python 3 puro, sem dependências), de qualquer pasta:
    python3 ferramentas/kit.py novo <pasta>        # a pasta, o git e os arquivos do kit
    python3 ferramentas/kit.py atualizar <pasta>   # a cópia nova do que se copia sem mudar
    python3 ferramentas/kit.py atualizar <pasta> --openspec   # e o OpenSpec na versão do kit

Nenhum dos dois faz commit nem envia: o commit segue o CLAUDE-comum.md (a mensagem, a coautoria)
e o envio pede o "sim" do usuário. O que vai aos projetos está em modelo/; esta pasta,
ferramentas/, é só do kit e não se copia.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
MODELO = KIT / "modelo"


# Copiados sem mudar: a pasta trilha/ inteira, que a atualização troca por inteiro. O cache do
# Python (__pycache__/), que os testes do kit criam ao importar os verificadores, não conta.
def _do_metodo() -> tuple[str, ...]:
    """Os arquivos versionados de modelo/trilha/ (um arquivo solto ali não vai aos projetos); sem
    o git, o que estiver na pasta."""
    saida = subprocess.run(
        ["git", "-C", str(KIT), "ls-files", "-z", "modelo/trilha"],
        capture_output=True,
        text=True,
        check=False,
    )
    nomes = [nome.removeprefix("modelo/") for nome in saida.stdout.split("\0") if nome]
    if saida.returncode != 0 or not nomes:
        nomes = [
            f"trilha/{arquivo.relative_to(MODELO / 'trilha')}"
            for arquivo in (MODELO / "trilha").rglob("*")
            if arquivo.is_file() and "__pycache__" not in arquivo.parts
        ]
    return tuple(sorted(nomes))


SEM_MUDAR = _do_metodo()
# Preenchidos em cada projeto (destino: origem em modelo/): o projeto novo os recebe; a
# atualização só cria o que falta, sem tocar no que o projeto já preencheu. Três origens têm
# outro nome, porque o nome real valeria dentro do próprio kit (o CLAUDE.md seria carregado
# pelo Claude Code, o .gitignore pelo git e o settings.json também pelo Claude Code).
A_PREENCHER = {
    "CLAUDE.md": "esqueleto-CLAUDE.md",
    "ANDAMENTO.md": "ANDAMENTO.md",
    "openspec/config.yaml": "openspec/config.yaml",
    "scripts/check.sh": "scripts/check.sh",
    ".gitignore": "gitignore",
    ".github/workflows/verificacao.yml": ".github/workflows/verificacao.yml",
    ".claude/settings.json": "claude-settings.json",
    ".github/dependabot.yml": ".github/dependabot.yml",
    "sdd/padroes-tecnicos.md": "sdd/padroes-tecnicos.md",
}
# Dos preenchidos, os que o projeto pode apagar (a falta deles é uma escolha), com a versão do kit
# que os trouxe: a atualização só os cria na passagem de uma versão anterior a ela.
APAGAVEIS = {"sdd/padroes-tecnicos.md": (2, 2)}
# Antes da 2.0, o que hoje está em trilha/ ficava solto; as versões antigas são lidas assim. É
# também o que a migração de um projeto antigo tira da raiz, de scripts/ e de .githooks/.
ANTES_DA_2_0 = {
    "trilha/CLAUDE-comum.md": "CLAUDE-comum.md",
    "trilha/hooks/pre-commit": ".githooks/pre-commit",
    **{
        f"trilha/{nome}": f"scripts/{nome}"
        for nome in (
            "confere_regras.py",
            "confere_metodo.py",
            "gerar_pagina_sdd.py",
            "pagina_sdd_modelo.html",
            "guarda.py",
        )
    },
}
# Até a 1.34, o modelo ficava na raiz do kit, com estes nomes; as versões antigas são lidas assim.
NA_RAIZ_ATE_1_34 = {
    "gitignore": ".gitignore",
    ".github/workflows/verificacao.yml": "github-verificacao.yml",
    ".github/dependabot.yml": "github-dependabot.yml",
}
# Dos preenchidos, os que só têm a parte da stack preenchida: o resto é fixo e muda com o kit.
COM_PARTE_FIXA = (
    ".gitignore",
    "scripts/check.sh",
    ".github/workflows/verificacao.yml",
    ".github/dependabot.yml",
)
# Os blocos da parte da stack nos modelos: o projeto troca ou apaga o que não é o seu, e a falta
# deles não vira aviso. Em todo arquivo, os que abrem com o comentário "Parte da stack" (no CI, ele
# fica no meio do bloco dos passos fixos, e o bloco fica); no .gitignore, também os de título
# Python e Node.
PARTE_DA_STACK = "# Parte da stack"
BLOCOS_DA_STACK = {"# Python", "# Node"}
# A língua dos artefatos, no context do openspec/config.yaml, como o `openspec init --language`
# a escreve (core/init.js do OpenSpec), mais os acentos: assim o init a reconhece.
LINGUA = (
    "Language: pt-BR\n"
    "All artifacts must be written in pt-BR.\n"
    "Keep OpenSpec structural headings and SHALL/MUST keywords in English.\n"
    "Write every Portuguese word with its accents."
)
# O plugin vale por projeto: o settings.json o declara, e cada máquina o instala uma vez nele. O
# trilha/confere_metodo.py, que roda no projeto sem este arquivo, cita o mesmo comando.
INSTALAR_NO_PROJETO = "claude plugin install sdd@trilha-ai --scope project"
# A trava do Claude Code em cada versão do kit: antes da 2.0, em scripts/; depois, em trilha/.
GUARDAS = ("scripts/guarda.py", "trilha/guarda.py")
# O OpenSpec que o kit espera, o do CI do modelo, e o ambiente dos comandos dele: sem a consulta da
# versão nova (que, no openspec update, pergunta se a instala) e sem a telemetria.
PIN_DO_OPENSPEC = re.compile(r"@fission-ai/openspec@(\d+\.\d+\.\d+[^\s\"']*)")
SEM_CONSULTA = {"OPENSPEC_NO_UPDATE_CHECK": "1", "OPENSPEC_TELEMETRY": "0", "DO_NOT_TRACK": "1"}
PRAZO_DO_OPENSPEC = 60
# O npm install e o openspec update baixam e escrevem: o prazo deles é maior.
PRAZO_DA_INSTALACAO = 600


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
    shutil.copy2(MODELO / origem, alvo)


def novo(pasta: Path) -> None:
    if pasta.exists() and any(pasta.iterdir()):
        raise Recusa(f"{pasta} já existe e não está vazia; o projeto novo nasce numa pasta vazia")
    pasta.mkdir(parents=True, exist_ok=True)
    _git(pasta, "init", "-q")
    _git(pasta, "symbolic-ref", "HEAD", "refs/heads/main")
    _copiar_trilha(pasta)
    for nome, origem in A_PREENCHER.items():
        _copiar(pasta, nome, origem)
    _ligar_travas(pasta)
    print(f"criado: {pasta}, com o kit (comum {_versao(MODELO / 'trilha' / 'CLAUDE-comum.md')})")
    print("próximos passos (README do kit, passos 3 a 6):")
    print("  3. preencha o que está entre < e > no CLAUDE.md, no ANDAMENTO.md e no config.yaml;")
    print("  4. inicialize as ferramentas:")
    print("     - uma vez por máquina, openspec config profile, com o verify marcado (o ciclo")
    print("       do método o usa); depois, openspec init (sem sobrescrever o config.yaml);")
    print(f"     - uma vez por máquina, nesta pasta, {INSTALAR_NO_PROJETO};")
    print("     - se usar o CodeGraph (opcional), codegraph init, em cada clone: o índice")
    print("       fica fora do git;")
    print("  5. bash scripts/check.sh, que deve terminar com ok;")
    print("  6. o primeiro commit e: gh repo create <nome> --private --source . --push")
    aviso = _aviso_do_perfil()
    if aviso:
        print(f"aviso: {aviso}")


def _aviso_do_perfil() -> str:
    """O verify que falta no perfil do OpenSpec desta máquina; vazio com ele. Só lê o perfil: no
    `core`, o OpenSpec ignora a lista de workflows e usa a dele, sem o verify (core/profiles.js)."""
    try:
        saida = subprocess.run(
            ["openspec", "config", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        perfil = json.loads(saida.stdout)
    except OSError:
        return "o openspec não está instalado; instale-o e ligue o verify no perfil (README do kit)"
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        perfil = None
    if not isinstance(perfil, dict):
        return "o openspec não respondeu ao openspec config list --json; confira o perfil nele"
    if perfil.get("profile") == "custom" and "verify" in (perfil.get("workflows") or []):
        return ""
    return (
        "o perfil do OpenSpec desta máquina não traz o verify, que o ciclo usa no passo 5: rode "
        "openspec config profile e marque-o"
    )


def atualizar(pasta: Path, openspec: bool = False) -> int:
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
    trilha = pasta / "trilha"
    if trilha.is_dir() and not (trilha / "CLAUDE-comum.md").is_file():
        raise Recusa(
            "a pasta trilha/ já existe e não é a do método (não tem o CLAUDE-comum.md); "
            "renomeie-a antes de atualizar"
        )
    _ler_settings(pasta)  # o settings.json que a soma não entende recusa antes de mudar algo

    comum = pasta / "trilha" / "CLAUDE-comum.md"
    antes = _versao(comum if comum.is_file() else pasta / "CLAUDE-comum.md")
    _conferir_o_kit(antes)  # antes de mudar qualquer arquivo do projeto
    migrou = _migrar(pasta)
    _copiar_trilha(pasta)
    for nome, origem in A_PREENCHER.items():
        if (pasta / nome).exists() or not _anterior(antes, APAGAVEIS.get(nome)):
            continue
        _copiar(pasta, nome, origem)
        print(f"aviso: {nome} não existia e foi criado do modelo do kit; confira-o")
    _ligar_travas(pasta)
    _sincronizar_regras(pasta)
    _avisar_parte_fixa(pasta, antes)
    # A página nasce ao fechar uma etapa (o comum); aqui, só a que já existe ganha o modelo novo.
    if (pasta / "sdd" / "documentacao.html").is_file():
        _rodar(pasta, [sys.executable, "-I", "trilha/gerar_pagina_sdd.py"])
    # Sem a migração do check.sh, a atualização falha: o OpenSpec não muda a máquina à toa.
    falha_do_openspec = _atualizar_o_openspec(pasta) if openspec and migrou else ""
    if not openspec:
        _avisar_o_openspec()
    _avisar_o_ci_do_projeto(pasta)

    regras = ["trilha/confere_regras.py", ".", "--fonte", str(KIT)]
    ok = _rodar(pasta, [sys.executable, "-I", *regras])
    ok = _rodar(pasta, [sys.executable, "-I", "trilha/confere_metodo.py"]) and ok
    if not any((pasta / ".claude").glob("**/*verify*")):
        print("aviso: o /opsx:verify não está instalado; ligue-o no perfil e rode openspec update")
    depois = _versao(MODELO / "trilha" / "CLAUDE-comum.md")
    mudou = _git(pasta, "status", "--short")
    print(mudou or "nada mudou: o projeto já está na versão do kit")
    if not migrou:
        print("FALHA: o scripts/check.sh ainda chama os scripts/confere_*, que saíram; troque-os")
        return 1
    if falha_do_openspec:
        print(f"FALHA: {falha_do_openspec}; os arquivos ficaram copiados, sem commit")
        return 1
    if not ok:
        print("FALHA: a conferência reprovou; os arquivos ficaram copiados, sem commit")
        return 1
    if mudou and openspec and antes == depois:
        alvo = _openspec_do_kit()
        print(f"commit sugerido: chore(metodo): os arquivos gerados pelo OpenSpec {alvo}")
    elif mudou:
        print(f"commit sugerido: chore(metodo): cópia do kit Trilha AI, comum {antes} → {depois}")
    return 0


def _openspec_do_kit() -> str:
    texto = (MODELO / ".github" / "workflows" / "verificacao.yml").read_text(encoding="utf-8")
    achado = PIN_DO_OPENSPEC.search(texto)
    return achado.group(1) if achado else ""


def _openspec(*args: str, pasta: Path | None = None) -> subprocess.CompletedProcess | None:
    """Um comando do openspec, sem a consulta da versão nova e sem a entrada do terminal; None se
    ele faltar ou não responder no prazo. O nome fora do UTF-8 chega como o sistema o guarda."""
    try:
        return subprocess.run(
            ["openspec", *args],
            cwd=pasta,
            capture_output=True,
            text=True,
            errors="surrogateescape",
            stdin=subprocess.DEVNULL,
            timeout=PRAZO_DO_OPENSPEC,
            check=False,
            env={**os.environ, **SEM_CONSULTA},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def _versao_do_openspec() -> str:
    """A versão do openspec da máquina; vazia sem ele ou sem resposta."""
    saida = _openspec("--version")
    achado = (
        re.search(r"\d+\.\d+\.\d+\S*", saida.stdout) if saida and not saida.returncode else None
    )
    return achado.group(0) if achado else ""


def _avisar_o_openspec() -> None:
    """Sem o --openspec, a versão da máquina diferente da do kit; sem o openspec, nada."""
    instalada, alvo = _versao_do_openspec(), _openspec_do_kit()
    if instalada and alvo and instalada != alvo:
        print(
            f"aviso: o OpenSpec da máquina está na {instalada} e o kit usa a {alvo}: rode de novo "
            "com --openspec para instalá-la e rodar o openspec update no projeto"
        )


def _avisar_o_ci_do_projeto(pasta: Path) -> None:
    """O CI do projeto com outra versão do OpenSpec que a do kit: a conferência do método cita a
    dele, e a troca da linha fica com o usuário, como o resto da parte fixa."""
    ci = pasta / ".github" / "workflows" / "verificacao.yml"
    achado = PIN_DO_OPENSPEC.search(ci.read_text(encoding="utf-8")) if ci.is_file() else None
    alvo = _openspec_do_kit()
    if achado and alvo and achado.group(1) != alvo:
        print(
            f"aviso: o .github/workflows/verificacao.yml do projeto instala o OpenSpec "
            f"{achado.group(1)}, e o kit usa a {alvo}: troque a versão nele; até lá, a conferência "
            f"do método abaixo cita a {achado.group(1)}"
        )


def _no_projeto(pasta: Path, nome: str) -> bool:
    """O caminho do dry-run fica dentro da pasta: nem no HOME (`~/...`), nem absoluto, nem fora
    dela por `..`."""
    raiz = pasta.resolve()
    return not nome.startswith("~") and Path(os.path.normpath(raiz / nome)).is_relative_to(raiz)


def _atualizar_o_openspec(pasta: Path) -> str:
    """O OpenSpec da máquina na versão do kit (o npm, só quando ela é outra ou falta) e o openspec
    update no projeto, depois do dry-run, que recusa o update que apagaria arquivos dele; devolve a
    falha, ou vazio."""
    alvo = _openspec_do_kit()
    if not alvo:
        return "o CI do modelo do kit não fixa a versão do OpenSpec"
    instalar = f"npm install -g @fission-ai/openspec@{alvo}"
    if _versao_do_openspec() != alvo:
        if not _rodar(pasta, instalar.split(), SEM_CONSULTA, PRAZO_DA_INSTALACAO):
            return f"o OpenSpec da máquina não ficou na {alvo}: rode {instalar}"
        agora = _versao_do_openspec()
        if agora != alvo:
            return (
                f"o {instalar} terminou, mas o openspec do PATH ({shutil.which('openspec')}) "
                f"responde {agora or 'nada'}: outro openspec vem antes no PATH"
            )
    saida = _openspec("update", "--dry-run", "--json", pasta=pasta)
    try:
        plano = json.loads(saida.stdout) if saida and not saida.returncode else None
    except (ValueError, RecursionError):
        plano = None
    mudancas = plano.get("changes") if isinstance(plano, dict) else None
    if not isinstance(mudancas, list) or plano.get("failures"):
        for linha in ((saida.stdout + saida.stderr) if saida else "").splitlines():
            print(f"  {linha}")
        return "o openspec update --dry-run --json falhou no projeto (a saída está acima)"
    apagados = sorted(
        mudanca["path"]
        for mudanca in mudancas
        if isinstance(mudanca, dict)
        and mudanca.get("action") == "delete"
        and isinstance(mudanca.get("path"), str)
    )
    fora = [nome for nome in apagados if not _no_projeto(pasta, nome)]
    if fora:
        print(f"aviso: o openspec update vai apagar, fora do projeto: {', '.join(fora)}")
    if dentro := [nome for nome in apagados if _no_projeto(pasta, nome)]:
        return (
            f"o openspec update apagaria {', '.join(dentro)}, e não rodou: confira o perfil com "
            "openspec config list e ajuste-o com openspec config profile"
        )
    if not _rodar(pasta, ["openspec", "update"], SEM_CONSULTA, PRAZO_DA_INSTALACAO):
        return "o openspec update falhou no projeto (a saída está acima)"
    return ""


def _conferir_o_kit(antes: str) -> None:
    """O kit é um clone do git com o histórico (a atualização lê as versões antigas dele) e não
    está atrás do projeto, que ele rebaixaria."""
    try:
        raso = _git(KIT, "rev-parse", "--is-shallow-repository")
        # O ZIP extraído numa pasta versionada responde pelo repositório de cima: não é o kit.
        if Path(_git(KIT, "rev-parse", "--show-toplevel")).resolve() != KIT.resolve():
            raise Recusa("outro repositório")
    except Recusa:
        raise Recusa(
            f"o kit em {KIT} não é um repositório git (baixado como ZIP?); a atualização lê o "
            "histórico dele: clone-o com o git"
        ) from None
    if raso == "true":
        raise Recusa(
            f"o kit em {KIT} é um clone raso, sem o histórico que a atualização lê: rode "
            f"git fetch --unshallow --tags, na pasta dele ({KIT})"
        )
    depois = _versao(MODELO / "trilha" / "CLAUDE-comum.md")
    if "?" not in (antes, depois) and _numeros(depois) < _numeros(antes):
        raise Recusa(
            f"o projeto está na {antes} e o kit na {depois}, atrás dele: a atualização o "
            f"rebaixaria; atualize o kit antes: git pull, na pasta dele ({KIT})"
        )


def _numeros(versao: str) -> tuple[int, int]:
    maior, menor = versao.split(".")
    return int(maior), int(menor)


def _copiar_trilha(pasta: Path) -> None:
    """A pasta trilha/ do projeto igual à do kit: copia tudo e apaga o que o kit não tem mais."""
    trilha = pasta / "trilha"
    for arquivo in sorted(trilha.rglob("*"), reverse=True) if trilha.is_dir() else []:
        nome = f"trilha/{arquivo.relative_to(trilha)}"
        if arquivo.is_file() and nome not in SEM_MUDAR:
            arquivo.unlink()
        elif arquivo.is_dir() and not any(arquivo.iterdir()):
            arquivo.rmdir()
    for nome in SEM_MUDAR:
        _copiar(pasta, nome, nome)


def _migrar(pasta: Path) -> bool:
    """O projeto de antes da 2.0 passa à pasta trilha/: sem as cópias soltas e com as citações."""
    antigas = [nome for nome in ANTES_DA_2_0.values() if (pasta / nome).is_file()]
    for nome in antigas:
        (pasta / nome).unlink()
    if antigas:
        print(f"migrado para trilha/: saíram {', '.join(antigas)}")
    ganchos = pasta / ".githooks"
    if antigas and ganchos.is_dir():
        proprios = sorted(arquivo.name for arquivo in ganchos.iterdir())
        # O pre-push próprio roda pelo trilha/hooks/pre-push; os outros ficam sem quem os chame.
        for nome in (nome for nome in proprios if nome != "pre-push"):
            print(
                f"aviso: .githooks/{nome} não roda mais, porque a trava do commit passou a "
                "trilha/hooks; ligue-o de outro jeito (por exemplo, chamado pelo scripts/check.sh)"
            )
        # O que o trilha/hooks/pre-push recusaria: o aviso vem já aqui, e não só no primeiro envio.
        envio = ganchos / "pre-push"
        if envio.is_symlink() and not envio.exists():
            print(
                "aviso: .githooks/pre-push é um link simbólico quebrado; o envio será recusado até "
                "ele ser corrigido"
            )
        elif envio.is_file() and not envio.stat().st_mode & 0o111:
            print(
                "aviso: .githooks/pre-push está sem a permissão de execução; o envio será recusado "
                "até ele ser corrigido (chmod +x .githooks/pre-push)"
            )
        if not proprios:
            ganchos.rmdir()
    claude = pasta / "CLAUDE.md"
    if claude.is_file():
        texto = claude.read_text(encoding="utf-8")
        importacao = re.compile(r"^@CLAUDE-comum\.md[ \t]*$", re.MULTILINE)
        migrado = importacao.sub("@trilha/CLAUDE-comum.md", texto)
        if migrado != texto:
            claude.write_text(migrado, encoding="utf-8")
            print("CLAUDE.md: a importação passou a @trilha/CLAUDE-comum.md")
    # As trocas rodam sempre: repeti-las não muda nada, e a migração parcial também se completa.
    return _migrar_check(pasta)


# A parte fixa do scripts/check.sh do kit até a 1.36, que a migração troca pelo trilha/verifica.sh.
CHECK_ANTIGO = (
    "# Parte fixa: as regras do repositório (CLAUDE.md, CLAUDE-comum.md, ANDAMENTO.md), "
    "com o comum\n"
    "# comparado ao do kit quando ele está ao lado (ou em TRILHA_AI).\n"
)
BLOCO_ANTIGO = (
    'FONTE="${TRILHA_AI:-../trilha-ai}"\n'
    'if [ -d "$FONTE" ]; then\n'
    '  python3 -I scripts/confere_regras.py . --fonte "$FONTE"\n'
    "else\n"
    '  echo "aviso: $FONTE não existe; a cópia do CLAUDE-comum.md não foi comparada '
    'com o kit" >&2\n'
    "  python3 -I scripts/confere_regras.py .\n"
    "fi\n"
)
CHAMADA_ANTIGA = "python3 -I scripts/confere_metodo.py"


def _migrar_check(pasta: Path) -> bool:
    """A parte fixa do check.sh, se for a do kit, vira o trilha/verifica.sh, com os --vizinho."""
    check = pasta / "scripts" / "check.sh"
    texto = check.read_text(encoding="utf-8") if check.is_file() else ""
    if "scripts/confere_" not in texto:
        return True
    if BLOCO_ANTIGO in texto and texto.count(CHAMADA_ANTIGA) == 1:
        texto = texto.replace(CHECK_ANTIGO, "# Parte fixa: as regras, o método e os specs.\n")
        texto = texto.replace(BLOCO_ANTIGO, "").replace(CHAMADA_ANTIGA, "bash trilha/verifica.sh")
        check.write_text(texto, encoding="utf-8")
        print("scripts/check.sh: a parte fixa passou a `bash trilha/verifica.sh`")
        return "scripts/confere_" not in texto
    print(
        "aviso: a parte fixa do scripts/check.sh não é a do kit; troque à mão a chamada aos "
        "scripts/confere_*.py por `bash trilha/verifica.sh` (com os --vizinho que houver)"
    )
    return False


def _anterior(antes: str, versao: tuple[int, int] | None) -> bool:
    """O projeto vem de antes da versão dada do kit, ou de versão desconhecida; sem versão, sim."""
    if versao is None or antes == "?":
        return True
    return tuple(int(parte) for parte in antes.split(".")) < versao


def _modelo_do_settings() -> dict:
    return json.loads((MODELO / "claude-settings.json").read_text(encoding="utf-8"))


def _ler_settings(pasta: Path) -> dict:
    """O .claude/settings.json do projeto ({} sem ele), recusado quando a soma do modelo não o
    entende: JSON inválido ou, onde o modelo tem um objeto ou uma lista, outro tipo (até null)."""
    settings = pasta / ".claude" / "settings.json"
    if not settings.is_file():
        return {}
    try:
        atual = json.loads(settings.read_text(encoding="utf-8"))
    except ValueError as erro:
        raise Recusa(f".claude/settings.json não é JSON válido ({erro}); corrija-o antes") from erro
    errado = _tipo_diferente(atual, _modelo_do_settings(), "")
    if errado:
        raise Recusa(
            f".claude/settings.json: {errado} não é do tipo que o modelo do kit tem ali (objeto "
            "ou lista); corrija-o antes"
        )
    return atual


def _tipo_diferente(atual: object, modelo: object, caminho: str) -> str:
    """O primeiro caminho em que o projeto tem outro tipo onde o modelo tem objeto ou lista."""
    if isinstance(modelo, list):
        return "" if isinstance(atual, list) else caminho
    if not isinstance(modelo, dict):
        return ""
    if not isinstance(atual, dict):
        return caminho or "a raiz"
    for chave in modelo.keys() & atual.keys():
        errado = _tipo_diferente(atual[chave], modelo[chave], f"{caminho}.{chave}".lstrip("."))
        if errado:
            return errado
    return ""


def _ligar_travas(pasta: Path) -> None:
    """A trava do commit (core.hooksPath, do clone) e o settings.json com o que o modelo tem: a
    trava do Claude Code e a declaração do plugin. O arquivo só é escrito quando algo muda."""
    _git(pasta, "config", "core.hooksPath", "trilha/hooks")
    settings = pasta / ".claude" / "settings.json"
    atual, modelo = _ler_settings(pasta), _modelo_do_settings()
    antes = json.dumps(atual, sort_keys=True)
    _sem_guardas_antigas(atual, modelo)
    _somar(atual, modelo)
    if json.dumps(atual, sort_keys=True) != antes or not settings.is_file():
        settings.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(atual, ensure_ascii=False, indent=2) + "\n"
        settings.write_text(texto, encoding="utf-8")


def _sem_guardas_antigas(atual: dict, modelo: dict) -> None:
    """Sai a trava do Claude Code de outra versão do kit (a de scripts/, de antes da 2.0, ou a de
    trilha/ chamada de outro jeito), e o grupo que só a tinha; a soma põe a do modelo."""
    do_modelo = [gancho for grupo in modelo["hooks"]["PreToolUse"] for gancho in grupo["hooks"]]

    def antiga(gancho: object) -> bool:
        comando = str(gancho.get("command", "")) if isinstance(gancho, dict) else ""
        return gancho not in do_modelo and any(guarda in comando for guarda in GUARDAS)

    lista = atual.get("hooks", {}).get("PreToolUse", [])
    esvaziados = []
    for grupo in lista:
        ganchos = grupo.get("hooks") if isinstance(grupo, dict) else None
        if isinstance(ganchos, list) and any(antiga(gancho) for gancho in ganchos):
            grupo["hooks"] = [gancho for gancho in ganchos if not antiga(gancho)]
            if not grupo["hooks"]:
                esvaziados.append(grupo)
    lista[:] = [grupo for grupo in lista if all(grupo is not vazio for vazio in esvaziados)]


def _somar(atual: dict, modelo: dict) -> None:
    """Põe no settings.json do projeto o que o modelo tem e ele não: a chave que falta e o item de
    lista que nenhum dos dele contém. O valor que o projeto deu fica, até o plugin desligado."""
    for chave, valor in modelo.items():
        if chave not in atual:
            atual[chave] = copy.deepcopy(valor)
        elif isinstance(valor, dict):
            _somar(atual[chave], valor)
        elif isinstance(valor, list):
            faltam = [item for item in valor if not any(_contido(item, n) for n in atual[chave])]
            atual[chave] += copy.deepcopy(faltam)


def _contido(parte: object, todo: object) -> bool:
    """A parte está no todo: as chaves dela com valores contidos, os itens dela cada um num item."""
    if isinstance(parte, dict):
        return isinstance(todo, dict) and all(
            chave in todo and _contido(valor, todo[chave]) for chave, valor in parte.items()
        )
    if isinstance(parte, list):
        return isinstance(todo, list) and all(any(_contido(p, t) for t in todo) for p in parte)
    return parte == todo


def _caminhos(origem: str) -> list[str]:
    """Onde a origem esteve no kit: em modelo/ (com trilha/ desde a 2.0) e, até a 1.34, na raiz."""
    antiga = ANTES_DA_2_0.get(origem, origem)
    return list(
        dict.fromkeys(
            [f"modelo/{origem}", f"modelo/{antiga}", NA_RAIZ_ATE_1_34.get(antiga, antiga)]
        )
    )


def _na_versao(versao: str, origem: str) -> str:
    """O texto da origem numa versão antiga do kit, onde quer que ela estivesse; vazio sem ela."""
    for caminho in _caminhos(origem):
        saida = subprocess.run(
            ["git", "-C", str(KIT), "show", f"{versao}:{caminho}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if saida.returncode == 0:
            return saida.stdout
    return ""


def _regras(texto: str) -> str:
    """A parte do config.yaml que vem do kit: das regras por artefato até o fim."""
    return texto[texto.find("\nrules:") + 1 :] if "\nrules:" in texto else ""


def _sincronizar_regras(pasta: Path) -> None:
    """Atualiza as regras do config.yaml só se forem as de uma versão do kit, sem mudança."""
    config = pasta / "openspec" / "config.yaml"
    if not config.is_file():
        return
    texto = config.read_text(encoding="utf-8")
    atuais = _regras((MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8"))
    if not _regras(texto) or _regras(texto) == atuais:
        return
    # Toda versão do config.yaml que o kit já teve, e não só as das tags, que seguem o comum.
    caminhos = _caminhos("openspec/config.yaml")
    for versao in _git(KIT, "log", "--format=%h", "--", *caminhos).split():
        antigas = _na_versao(versao, "openspec/config.yaml")
        if _regras(antigas) and _regras(antigas) == _regras(texto):
            cabeca = _com_lingua(texto[: texto.find("\nrules:") + 1])
            config.write_text(cabeca + atuais, encoding="utf-8")
            print(f"regras do openspec/config.yaml atualizadas: eram as do kit em {versao}")
            return
    print("aviso: o openspec/config.yaml tem regras próprias; compare-as com as do kit à mão")


def _linhas_fixas(texto: str) -> set[str]:
    """As linhas que valem, sem os comentários, que o projeto troca pelos passos da stack."""
    linhas = (re.sub(r"(^|\s+)#.*", "", linha).strip() for linha in texto.splitlines())
    return {linha for linha in linhas if linha}


def _sem_blocos_da_stack(nome: str, texto: str) -> str:
    """O modelo sem os blocos da parte da stack, que o projeto troca ou apaga de propósito."""
    titulos = BLOCOS_DA_STACK if nome == ".gitignore" else set()

    def da_stack(bloco: str) -> bool:
        linhas = [linha.strip() for linha in bloco.splitlines()]
        abre = bool(linhas) and linhas[0].startswith(PARTE_DA_STACK)
        return abre or bool(titulos & set(linhas))

    return "\n\n".join(bloco for bloco in re.split(r"\n\s*\n", texto) if not da_stack(bloco))


def _avisar_parte_fixa(pasta: Path, antes: str) -> None:
    """Diz o que falta da parte fixa do modelo atual no projeto e o que o kit tirou dela desde a
    versão do projeto; a cópia fica com o usuário."""
    # O commit que trouxe a versão do comum do projeto; só por ele se sabe o que o kit tirou.
    comum = _caminhos("trilha/CLAUDE-comum.md")
    desde = _git(KIT, "log", "--format=%h", "-S", f"Versão {antes},", "--", *comum)
    desde = "" if antes == "?" else desde
    for nome in COM_PARTE_FIXA:
        origem = A_PREENCHER[nome]
        if not (pasta / nome).is_file():
            continue
        velho = _na_versao(desde.split()[-1], origem) if desde else ""
        novo = (MODELO / origem).read_text(encoding="utf-8")
        projeto = _linhas_fixas((pasta / nome).read_text(encoding="utf-8"))
        acoes = {_sem_versao_da_acao(linha) for linha in projeto}
        faltam = sorted(
            linha
            for linha in _linhas_fixas(_sem_blocos_da_stack(nome, novo))
            if not _presente(_sem_versao_da_acao(linha), acoes)
        )
        do_kit = {_sem_versao_da_acao(linha) for linha in _linhas_fixas(novo)}
        sobram = sorted(
            linha
            for linha in (_linhas_fixas(velho) - _linhas_fixas(novo)) & projeto
            if _sem_versao_da_acao(linha) not in do_kit
        )
        if faltam or sobram:
            print(f"aviso: a parte fixa de {nome} difere do modelo do kit; traga à mão:")
            for linha in faltam:
                print(f"  + {linha}")
            for linha in sobram:
                print(f"  - {linha}")


def _sem_versao_da_acao(linha: str) -> str:
    """A linha com a ação do CI (`uses: dono/acao@versão`) sem a versão: o Dependabot a atualiza
    no projeto, e a ação noutra versão não é linha que falta nem que sobra."""
    return re.sub(r"(uses:\s*[^@\s]+)@\S+", r"\1@", linha)


def _presente(linha: str, projeto: set[str]) -> bool:
    """A linha do kit está no projeto: igual, seguida de espaço e argumentos (os --vizinho) ou
    chamada dentro de uma linha dele, depois de um espaço (por uma função do projeto)."""
    return any(f" {linha} " in f" {nossa} " for nossa in projeto)


def _com_lingua(cabeca: str) -> str:
    """O context do projeto com a língua, que até a 1.32 vinha repetida nas regras do kit."""
    if LINGUA.splitlines()[1] in cabeca:
        return cabeca
    if "\ncontext: |\n" not in cabeca:
        print("aviso: o openspec/config.yaml sem 'context: |'; acrescente a língua a ele à mão")
        return cabeca
    bloco = "".join(f"  {linha}\n" for linha in LINGUA.splitlines()) + "\n"
    print("a língua foi acrescentada ao context do openspec/config.yaml, como o OpenSpec pede")
    return cabeca.replace("\ncontext: |\n", "\ncontext: |\n" + bloco, 1)


def _rodar(
    pasta: Path,
    comando: list[str],
    ambiente: dict[str, str] | None = None,
    prazo: float | None = None,
) -> bool:
    """O comando na pasta, com a saída recuada; sem a entrada do terminal, para uma pergunta dele
    não travar a ferramenta calada."""
    try:
        saida = subprocess.run(
            comando,
            cwd=pasta,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=prazo,
            check=False,
            env={**os.environ, **(ambiente or {})},
        )
    except OSError as erro:  # o comando que falta na máquina (o npm, o openspec)
        print(f"  {comando[0]}: {erro.strerror}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  {comando[0]}: sem resposta em {prazo:.0f} segundos")
        return False
    for linha in (saida.stdout + saida.stderr).splitlines():
        print(f"  {linha}")
    return saida.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("acao", choices=("novo", "atualizar"))
    parser.add_argument("pasta", type=Path)
    parser.add_argument(
        "--openspec",
        action="store_true",
        help="no atualizar: instala o OpenSpec na versão do kit e roda o openspec update",
    )
    args = parser.parse_args()
    if args.openspec and args.acao != "atualizar":
        parser.error("o --openspec só vale no atualizar")
    try:
        if args.acao == "novo":
            novo(args.pasta)
            return 0
        return atualizar(args.pasta, openspec=args.openspec)
    except Recusa as recusa:
        print(f"recusado: {recusa}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
