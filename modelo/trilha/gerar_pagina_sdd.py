"""Gera sdd/documentacao.html: a documentação do projeto, com três abas.

Aba 1, o produto: sdd/prd-*.md. Aba 2, as decisões: sdd/tdd-*.md. Aba 3, as entregas:
sdd/decomposicao-*.md, a faixa das changes lida da tabela "Ciclo" e os briefings de
sdd/briefing-openspec/; o "PR #N" anotado no Ciclo vira link, pelo origin do git (local, sem
rede). Etapa que ainda não existe aparece como tal; nada é inventado.
O visual e o comportamento ficam em trilha/pagina_sdd_modelo.html.

Uso (Python 3 puro, sem dependências):
    python3 trilha/gerar_pagina_sdd.py              # gera sdd/documentacao.html
    python3 trilha/gerar_pagina_sdd.py --fragmento X  # gera também X sem <head>/<body>
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SDD = RAIZ / "sdd"
BRIEFINGS = SDD / "briefing-openspec"
SAIDA = SDD / "documentacao.html"
MODELO = Path(__file__).resolve().parent / "pagina_sdd_modelo.html"


def _primeiro(padrao: str) -> Path | None:
    achados = sorted(SDD.glob(padrao))
    return achados[0] if achados else None


def _ler(arquivo: Path | None) -> str:
    return arquivo.read_text(encoding="utf-8") if arquivo else ""


def _titulo(texto: str, padrao: str) -> str:
    """O primeiro título de nível 1; sem ele, o primeiro de nível 2 (PRDs antigos começam assim)."""
    for nivel in ("# ", "## "):
        for linha in texto.splitlines():
            if linha.startswith(nivel):
                return linha[len(nivel) :].strip()
    return padrao


def _nome_do_produto(prd: str) -> str:
    """O nome vem do título do PRD ("PRD: Nome" ou "PRD — Nome"); sem PRD, o nome da pasta."""
    titulo = _titulo(prd, "")
    titulo = re.sub(r"^PRD\s*[:—–-]\s*", "", titulo).strip()
    return titulo or RAIZ.name


def _sem_marcacao(texto: str) -> str:
    """Tira a marcação de markdown que o resumo mostraria crua: negrito, código e links."""
    texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto)
    return re.sub(r"\*\*|__|`", "", texto)


def _resumo_do_produto(prd: str, limite: int = 300) -> str:
    """O primeiro parágrafo de texto corrido do PRD, depois do título, dos metadados e das notas."""
    paragrafo: list[str] = []
    for linha in prd.splitlines():
        if linha.startswith(("#", "**", "|", "-", ">")):
            if paragrafo:
                break
            continue
        if not linha.strip():
            if paragrafo:
                break
            continue
        paragrafo.append(linha.strip())
    resumo = _sem_marcacao(" ".join(paragrafo))
    if len(resumo) <= limite:
        return resumo
    return resumo[:limite].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"


def _nome_da_change(celula: str) -> str:
    """O nome da change como o OpenSpec o escreve, tirado do briefing citado na célula."""
    achado = re.search(r"briefing-change-\d+-([\w-]+)", celula)
    return achado.group(1) if achado else ""


VAZIO = {"", "—", "–", "-"}  # a célula de um passo que ainda não aconteceu


def _changes(decomposicao: str) -> list[dict[str, str]]:
    """A tabela da seção "## Ciclo" da decomposição: | NN | briefing | auditoria | archive |."""
    linhas = decomposicao.splitlines()
    titulos = (i for i, linha in enumerate(linhas) if linha.strip() == "## Ciclo")
    inicio = next(titulos, None)
    if inicio is None:
        return []
    changes = []
    for linha in linhas[inicio + 1 :]:
        if linha.startswith("## "):
            break
        celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
        if not re.fullmatch(r"\d{2,3}", celulas[0]):
            continue
        if len(celulas) != 4:
            print(f"aviso: linha do Ciclo fora do formato, ignorada: {linha}", file=sys.stderr)
            continue
        numero, briefing, _auditoria, archive = celulas
        pr = re.search(r"PR #(\d+)", linha)
        if archive.startswith("arquivada"):
            estado, rotulo = "arquivada", "arquivada"
        elif archive.startswith("retirada"):
            estado, rotulo = "retirada", "retirada"
        elif briefing not in VAZIO:
            estado, rotulo = "andamento", "em andamento"
        else:
            estado, rotulo = "futura", "a fazer"
        nome = _nome_da_change(briefing)
        changes.append(
            {
                "numero": numero,
                "nome": nome,
                "estado": estado,
                "rotulo": rotulo,
                "pr": pr.group(1) if pr else "",
            }
        )
    return changes


def _briefings() -> list[dict[str, str]]:
    itens = []
    for arquivo in sorted(BRIEFINGS.glob("briefing-change-*.md")) if BRIEFINGS.is_dir() else []:
        texto = arquivo.read_text(encoding="utf-8")
        itens.append(
            {"arquivo": arquivo.name, "titulo": _titulo(texto, arquivo.stem), "texto": texto}
        )
    return itens


def _atualizado_em() -> str:
    try:
        saida = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=format:%d/%m/%Y", "--", str(SDD)],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            check=True,
        )
        return saida.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _repositorio() -> str:
    """O endereço web do origin, lido do git local (sem rede e sem credenciais); sem ele, vazio."""
    try:
        saida = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    url = saida.stdout.strip()
    url = re.sub(r"^git@([^:]+):", r"https://\1/", url)  # git@github.com:dono/repo
    url = re.sub(r"^(https?://)[^@/]+@", r"\1", url)  # https://usuario:token@...
    url = re.sub(r"\.git$", "", url)
    return url if url.startswith(("https://", "http://")) else ""


def _json_seguro(valor: object) -> str:
    """JSON embutível em <script>: sem fechar a tag por engano."""
    return json.dumps(valor, ensure_ascii=False).replace("</", "<\\/")


def gerar_fragmento() -> str:
    prd = _ler(_primeiro("prd-*.md"))
    tdd = _ler(_primeiro("tdd-*.md"))
    decomposicao = _ler(_primeiro("decomposicao-*.md"))
    nome = _nome_do_produto(prd)
    dados = {
        "nome": nome,
        "resumo": _resumo_do_produto(prd),
        "prd": prd,
        "tdd": tdd,
        "decomposicao": decomposicao,
        "changes": _changes(decomposicao),
        "briefings": _briefings(),
        "atualizado": _atualizado_em(),
        "repositorio": _repositorio(),
    }
    modelo = MODELO.read_text(encoding="utf-8")
    return modelo.replace("__TITULO__", f"{nome}: documentação").replace(
        "__DADOS__", _json_seguro(dados)
    )


def gerar_documento(fragmento: str) -> str:
    """Documento completo para abrir direto no navegador: título e estilos no <head>."""
    cabeca, corpo = fragmento.split('<div class="casca">', 1)
    return (
        '<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + cabeca
        + '</head>\n<body>\n<div class="casca">'
        + corpo
        + "\n</body>\n</html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fragmento", type=Path, help="grava também a versão sem <head>/<body>")
    args = parser.parse_args()
    SDD.mkdir(exist_ok=True)
    fragmento = gerar_fragmento()
    SAIDA.write_text(gerar_documento(fragmento), encoding="utf-8")
    print(f"gerado: {SAIDA.relative_to(RAIZ)}")
    if args.fragmento:
        args.fragmento.write_text(fragmento, encoding="utf-8")
        print(f"gerado: {args.fragmento}")


if __name__ == "__main__":
    main()
