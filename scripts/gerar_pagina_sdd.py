"""Gera sdd/documentacao.html: a página do método de um repositório, com três abas.

Aba 1, o produto: sdd/prd-*.md. Aba 2, as decisões: sdd/tdd-*.md. Aba 3, as entregas:
sdd/decomposicao-*.md, a faixa das changes lida da tabela "Ciclo" e os briefings de
sdd/briefing-openspec/. Etapa que ainda não existe aparece como tal; nada é inventado.
O visual e o comportamento ficam em scripts/pagina_sdd_modelo.html.

Uso (Python 3 puro, sem dependências):
    python3 scripts/gerar_pagina_sdd.py              # gera sdd/documentacao.html
    python3 scripts/gerar_pagina_sdd.py --fragmento X  # gera também X sem <head>/<body>
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
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


def _resumo_do_produto(prd: str) -> str:
    """O primeiro parágrafo de texto corrido do PRD, depois do título e dos metadados."""
    paragrafo: list[str] = []
    for linha in prd.splitlines():
        if (
            linha.startswith("#")
            or linha.startswith("**")
            or linha.startswith("|")
            or linha.startswith("-")
        ):
            if paragrafo:
                break
            continue
        if not linha.strip():
            if paragrafo:
                break
            continue
        paragrafo.append(linha.strip())
    return " ".join(paragrafo)[:300]


def _nome_da_change(briefing: str) -> str:
    """briefing-change-NN-nome-da-change.md → "Nome da change"."""
    nome = re.sub(r"^briefing-change-\d+-", "", Path(briefing).stem)
    return nome.replace("-", " ").capitalize()


def _changes(decomposicao: str) -> list[dict[str, str]]:
    """A tabela "Ciclo" da decomposição: | NN | briefing | auditoria | archive |."""
    if "## Ciclo" not in decomposicao:
        return []
    ciclo = decomposicao.split("## Ciclo", 1)[1]
    changes = []
    for linha in ciclo.splitlines():
        celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(celulas) != 4 or not re.fullmatch(r"\d{2,3}", celulas[0]):
            continue
        numero, briefing, _auditoria, archive = celulas
        if archive.startswith("arquivada"):
            estado, rotulo = "arquivada", "arquivada"
        elif briefing not in ("—", ""):
            estado, rotulo = "andamento", "em andamento"
        else:
            estado, rotulo = "futura", "a fazer"
        changes.append(
            {
                "numero": numero,
                "nome": _nome_da_change(briefing.split()[0])
                if briefing.startswith("briefing")
                else "",
                "estado": estado,
                "rotulo": rotulo,
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
    }
    modelo = MODELO.read_text(encoding="utf-8")
    return modelo.replace("__TITULO__", f"{nome}: o método").replace(
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
