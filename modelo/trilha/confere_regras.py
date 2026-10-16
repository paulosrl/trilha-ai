"""Confere as regras de um repositório que segue o CLAUDE-comum.md (no trilha/verifica.sh).

Uso: python3 -I trilha/confere_regras.py <raiz do repositório> [--fonte <pasta do kit>]

Confere, na raiz indicada:
- trilha/CLAUDE-comum.md existe e tem a linha de versão;
- CLAUDE.md importa o comum (linha "@trilha/CLAUDE-comum.md"), não repete regra dele, tem o nome do
  produto no título, cita ANDAMENTO.md e openspec/config.yaml em "Documentos" e segue o
  esqueleto das sete seções, na ordem;
- os dois somados têm no máximo 200 linhas e 32 KB (32.768 bytes);
- ANDAMENTO.md existe, tem as seis linhas pedidas, com a data e a hora (nunca no futuro), e cabe
  em dez linhas;
- com --fonte, a pasta trilha/ é igual à modelo/trilha/ da versão do projeto, arquivo a arquivo
  (o cache do Python, __pycache__/, não conta): a cópia de trabalho do kit, na mesma versão; a tag
  vX.Y do kit, noutra, com aviso; sem a tag, só o aviso;
- as travas desligadas (o core.hooksPath, o guarda.py no .claude/settings.json e o
  disableAllHooks), como aviso;
- os campos < > dos modelos do kit ainda por preencher, como aviso (a stack só vem na etapa 2);
- com o TDD escrito (sdd/tdd-*.md), os lugares da stack ainda como o modelo os deixou, como aviso.

Só python3, sem dependências. Sai com 1 e imprime "FALHA: ..." por problema; "ok" se nada falhar.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LIMITE_DE_LINHAS = 200
LIMITE_DE_BYTES = 32_768  # 32 KB: o comum e o CLAUDE.md vão a toda sessão
IMPORTACAO = "@trilha/CLAUDE-comum.md"
LIMITE_DO_ANDAMENTO = 10
ESQUELETO = (
    "## O que é",
    "## Documentos",
    "## Comandos",
    "## Regras de código",
    "## Dados a proteger",
    "## Armadilhas próprias",
    "## Exceções ao comum",
)
CHAVES_DO_ANDAMENTO = (
    "**Estado:**",
    "**Etapa:**",
    "**Unidade em curso:**",
    "**Feito nesta etapa:**",
    "**Próximo passo exato:**",
    "**Atualizado em:**",
)
# Os campos < > dos modelos do kit (esqueleto-CLAUDE.md, ANDAMENTO.md e o contexto do
# openspec/config.yaml), pelo começo de cada um; o teste do kit os confere com os modelos.
CAMPOS_DO_MODELO = {
    "CLAUDE.md": (
        "<nome do produto>",
        "<uma ou duas frases",
        "prd-<nome>.md",
        "tdd-<nome>.md",
        "decomposicao-<nome>.md",
        "`<caminho>`",
        "`<quando>`",
        "<instalar as dependências>",
        "<rodar>",
        "<gerenciador de pacotes",
        "<onde ficam as respostas",
        "<o dado real",
        "<o que já deu errado",
    ),
    "ANDAMENTO.md": (
        "<PRD, TDD, decomposição",
        "<o que já está pronto",
        "<o que fazer a seguir",
        "<AAAA-MM-DD HH:MM>",
    ),
    "openspec/config.yaml": ("Projeto: <nome>", "<uma frase sobre o que é", "<linguagem e versão"),
}

# Os lugares da stack que o comum manda preencher ao fechar o gate 2, cada um com o texto do
# modelo que pede o preenchimento; o teste do kit confere que cada texto está no modelo.
STACK_DO_MODELO = {
    "scripts/check.sh": "a parte da stack ainda não foi preenchida",
    ".github/workflows/verificacao.yml": "Troque o comentário pelos passos reais",
    ".github/dependabot.yml": "exemplos pelo bloco real e apague este comentário",
    ".gitignore": "apague o bloco que não for o seu e este comentário",
    "openspec/config.yaml": "<linguagem e versão",
}

# A hora real, ou o espaço reservado do kit recém-copiado.
DATA_E_HORA = re.compile(r"\*\*Atualizado em:\*\* (\d{4}-\d\d-\d\d \d\d:\d\d|<AAAA-MM-DD HH:MM>)")


def _linhas(arquivo: Path) -> list[str]:
    return arquivo.read_text(encoding="utf-8").splitlines()


def _secao(linhas: list[str], titulo: str) -> str:
    """O texto de uma seção de nível 2, até a próxima."""
    dentro, texto = False, []
    for linha in linhas:
        if linha.startswith("## "):
            dentro = linha == titulo
        elif dentro:
            texto.append(linha)
    return "\n".join(texto)


# Cada arquivo de uma pasta do método: o conteúdo e se é executável.
Conteudos = dict[str, tuple[bytes, bool]]
ATUALIZAR = "rode o kit.py atualizar do kit, com a escolha do usuário; não edite a pasta"


def _versao(comum: Path) -> str:
    """A versão X.Y da linha "Versão X.Y, de …" do comum; vazio sem ela."""
    texto = comum.read_text(encoding="utf-8") if comum.is_file() else ""
    achado = re.search(r"^Versão (\d+\.\d+),", texto, re.MULTILINE)
    return achado.group(1) if achado else ""


def _conteudos(pasta: Path) -> Conteudos:
    """Os arquivos de uma pasta do método, pelo caminho relativo, sem o cache do Python."""
    if not pasta.is_dir():
        return {}
    return {
        str(arquivo.relative_to(pasta)): (
            arquivo.read_bytes(),
            bool(arquivo.stat().st_mode & 0o111),
        )
        for arquivo in sorted(pasta.rglob("*"))
        if arquivo.is_file() and "__pycache__" not in arquivo.parts
    }


def _conteudos_da_tag(kit: Path, tag: str) -> Conteudos | None:
    """A modelo/trilha/ do kit numa tag, lida pelo git, sem extrair nada; None sem a tag (ou sem
    o git, num clone raso) ou sem a pasta nela (antes da 2.0)."""
    lista = subprocess.run(
        ["git", "-C", str(kit), "ls-tree", "-r", "-z", tag, "--", "modelo/trilha"],
        capture_output=True,
        check=False,
    )
    if lista.returncode != 0:
        return None
    itens = []
    for registro in filter(None, lista.stdout.split(b"\0")):
        info, caminho = registro.split(b"\t", 1)
        modo, tipo, objeto = info.split()
        if tipo == b"blob":
            itens.append((caminho.decode("utf-8"), modo == b"100755", objeto))
    if not itens:
        return None
    lote = subprocess.run(
        ["git", "-C", str(kit), "cat-file", "--batch"],
        input=b"".join(objeto + b"\n" for _, _, objeto in itens),
        capture_output=True,
        check=False,
    )
    if lote.returncode != 0:
        return None
    resto, conteudos = lote.stdout, {}
    for caminho, executavel, _ in itens:  # cada um: "<objeto> blob <tamanho>\n<conteúdo>\n"
        cabeca, resto = resto.split(b"\n", 1)
        tamanho = int(cabeca.split()[2])
        conteudos[caminho.removeprefix("modelo/trilha/")] = (resto[:tamanho], executavel)
        resto = resto[tamanho + 1 :]
    return conteudos


def _diferencas(deles: Conteudos, nossos: Conteudos) -> list[str]:
    """O que impede a pasta trilha/ do projeto de ser igual à do kit na versão que vale."""
    falhas = [f"trilha/{nome} falta; {ATUALIZAR}" for nome in deles if nome not in nossos]
    falhas += [
        f"trilha/{nome} não é do kit; a pasta é só do método: {ATUALIZAR}"
        for nome in nossos
        if nome not in deles
    ]
    falhas += [
        f"trilha/{nome} difere do kit; {ATUALIZAR}"
        for nome in deles
        if nome in nossos and deles[nome][0] != nossos[nome][0]
    ]
    # O git pula em silêncio o hook sem a permissão de execução: a cópia a mantém.
    falhas += [
        f"trilha/{nome} perdeu a permissão de execução; {ATUALIZAR}"
        for nome in deles
        if nome in nossos and deles[nome][1] and not nossos[nome][1]
    ]
    return falhas


def comparar_com_o_kit(raiz: Path, fonte: Path) -> tuple[list[str], list[str]]:
    """As falhas e os avisos da pasta trilha/ comparada com a da versão do projeto: a cópia de
    trabalho do kit, na mesma versão; a tag vX.Y do kit, noutra (o kit mais novo só avisa)."""
    original = fonte / "modelo" / "trilha"
    if not (original / "CLAUDE-comum.md").is_file():
        return [f"a fonte {original} não existe ou não é a pasta do kit"], []
    nossa = _versao(raiz / "trilha" / "CLAUDE-comum.md")
    do_kit = _versao(original / "CLAUDE-comum.md")
    if nossa == do_kit:
        return _diferencas(_conteudos(original), _conteudos(raiz / "trilha")), []
    da_tag = _conteudos_da_tag(fonte, f"v{nossa}") if nossa else None
    if da_tag is None:
        aviso = (
            f"o kit está na {do_kit} e não tem a tag v{nossa or '?'} da versão do projeto; a "
            "pasta trilha/ não foi comparada"
        )
        return [], [aviso]
    aviso = (
        f"o kit está na {do_kit} e o projeto na {nossa}: a pasta trilha/ foi comparada com a "
        f"v{nossa}; para a versão nova, rode o kit.py atualizar do kit, com a escolha do usuário"
    )
    return _diferencas(da_tag, _conteudos(raiz / "trilha")), [aviso]


def conferir(raiz: Path) -> list[str]:
    falhas: list[str] = []
    comum = raiz / "trilha" / "CLAUDE-comum.md"
    proprio, andamento = raiz / "CLAUDE.md", raiz / "ANDAMENTO.md"
    for arquivo in (comum, proprio, andamento):
        if not arquivo.is_file():
            falhas.append(f"{arquivo.relative_to(raiz)} não existe")
    if falhas:
        return falhas

    linhas_comum, linhas_proprio = _linhas(comum), _linhas(proprio)
    versao = re.compile(r"^Versão \d+\.\d+, de \d{4}-\d\d-\d\d\.")
    if not any(versao.match(linha) for linha in linhas_comum):
        falhas.append("CLAUDE-comum.md sem a linha 'Versão X.Y, de AAAA-MM-DD.'")
    if IMPORTACAO not in linhas_proprio:
        falhas.append(f"CLAUDE.md não importa o comum (falta a linha {IMPORTACAO})")
    item = re.compile(r"^(- |\d+\. )")
    regras_do_comum = {linha.strip() for linha in linhas_comum if item.match(linha)}
    for linha in linhas_proprio:
        if linha.strip() in regras_do_comum:
            falhas.append(f"CLAUDE.md repete regra do comum: {linha.strip()[:70]}")
    titulos = tuple(linha for linha in linhas_proprio if linha.startswith("## "))
    if titulos != ESQUELETO:
        falhas.append(f"CLAUDE.md fora do esqueleto: {' · '.join(titulos) or '(sem seções)'}")
    if not (linhas_proprio and re.match(r"^# CLAUDE\.md — \S", linhas_proprio[0])):
        falhas.append(
            "CLAUDE.md sem o nome do produto no título ('# CLAUDE.md — <nome do produto>')"
        )
    documentos = _secao(linhas_proprio, "## Documentos")
    for citado in ("ANDAMENTO.md", "openspec/config.yaml"):
        if citado not in documentos:
            falhas.append(f"CLAUDE.md não cita {citado} na seção Documentos")
    total = len(linhas_comum) + len(linhas_proprio)
    if total > LIMITE_DE_LINHAS:
        falhas.append(
            f"CLAUDE.md + CLAUDE-comum.md somam {total} linhas; o limite é {LIMITE_DE_LINHAS}"
        )
    tamanho = len(comum.read_bytes()) + len(proprio.read_bytes())
    if tamanho > LIMITE_DE_BYTES:
        falhas.append(
            f"CLAUDE.md + CLAUDE-comum.md somam {tamanho} bytes; o limite é {LIMITE_DE_BYTES}"
        )

    linhas_andamento = _linhas(andamento)
    if len(linhas_andamento) > LIMITE_DO_ANDAMENTO:
        n = len(linhas_andamento)
        falhas.append(f"ANDAMENTO.md tem {n} linhas; o limite é {LIMITE_DO_ANDAMENTO}")
    texto_andamento = "\n".join(linhas_andamento)
    for chave in CHAVES_DO_ANDAMENTO:
        if chave not in texto_andamento:
            falhas.append(f"ANDAMENTO.md sem a linha {chave}")
    hora = DATA_E_HORA.search(texto_andamento)
    if not hora:
        falhas.append("ANDAMENTO.md sem a hora em 'Atualizado em' (AAAA-MM-DD HH:MM)")
    elif not hora.group(1).startswith("<") and hora.group(1) > f"{datetime.now():%Y-%m-%d %H:%M}":
        falhas.append(f"ANDAMENTO.md com a hora no futuro ({hora.group(1)}); leia-a com `date`")
    return falhas


def avisos_das_travas(raiz: Path) -> list[str]:
    """As travas do kit desligadas: aviso, não falha, porque o core.hooksPath é de cada clone."""
    avisos = []
    if (raiz / ".git").exists():
        saida = subprocess.run(
            ["git", "-C", str(raiz), "config", "core.hooksPath"],
            capture_output=True,
            text=True,
            check=False,
        )
        if saida.stdout.strip() != "trilha/hooks":
            avisos.append("trava do commit desligada: rode git config core.hooksPath trilha/hooks")
    settings = raiz / ".claude" / "settings.json"
    ligada = settings.is_file() and "trilha/guarda.py" in settings.read_text(encoding="utf-8")
    if not ligada:
        avisos.append("trava do Claude Code desligada: .claude/settings.json sem o guarda.py")
    # O disableAllHooks segue a precedência do Claude Code: o local prevalece sobre o do projeto.
    for nome in (".claude/settings.local.json", ".claude/settings.json"):
        try:
            dados = json.loads((raiz / nome).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(dados, dict) and isinstance(dados.get("disableAllHooks"), bool):
            if dados["disableAllHooks"]:
                avisos.append(
                    f"trava do Claude Code desligada: disableAllHooks verdadeiro em {nome}"
                )
            break
    return avisos


def avisos_dos_campos(raiz: Path) -> list[str]:
    """Os campos do modelo ainda por preencher: aviso, porque alguns só se preenchem na etapa 2."""
    avisos = []
    for nome, campos in CAMPOS_DO_MODELO.items():
        arquivo = raiz / nome
        texto = arquivo.read_text(encoding="utf-8") if arquivo.is_file() else ""
        faltam = [campo for campo in campos if campo in texto]
        if faltam:
            avisos.append(f"{nome} ainda tem {len(faltam)} campo(s) do modelo: {faltam[0]}…")
    return avisos


def avisos_da_stack(raiz: Path) -> list[str]:
    """Com o TDD escrito, os lugares da stack ainda como o modelo os deixou: aviso, não falha."""
    if not any((raiz / "sdd").glob("tdd-*.md")):
        return []
    pendentes = [
        nome
        for nome, marcador in STACK_DO_MODELO.items()
        if (raiz / nome).is_file() and marcador in (raiz / nome).read_text(encoding="utf-8")
    ]
    if not pendentes:
        return []
    aviso = (
        f"há TDD, e a parte da stack ainda é a do modelo em {', '.join(pendentes)}; preencha-a "
        "como o CLAUDE-comum.md manda ao fechar o gate 2"
    )
    return [aviso]


def main(argv: list[str]) -> int:
    if not argv or len(argv) not in (1, 3) or (len(argv) == 3 and argv[1] != "--fonte"):
        print(__doc__, file=sys.stderr)
        return 2
    raiz = Path(argv[0]).resolve()
    fonte = Path(argv[2]).resolve() if len(argv) == 3 else None
    falhas, avisos = conferir(raiz), avisos_das_travas(raiz)
    if fonte is not None:
        da_fonte, avisos_da_fonte = comparar_com_o_kit(raiz, fonte)
        falhas, avisos = falhas + da_fonte, avisos + avisos_da_fonte
    for aviso in avisos + avisos_dos_campos(raiz) + avisos_da_stack(raiz):
        print(f"aviso: {aviso}", file=sys.stderr)
    for falha in falhas:
        print(f"FALHA: {falha}", file=sys.stderr)
    if not falhas:
        print("ok: CLAUDE.md, trilha/ e ANDAMENTO.md conferidos")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
