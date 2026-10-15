"""Confere os documentos do método de um repositório que segue o kit (chamado pelo check.sh).

Uso: python3 -I scripts/confere_metodo.py [--vizinho <nome>]...

Confere, na raiz do repositório:
- a decomposição tem toda change da seção 1 na tabela "Ciclo", e a retirada aparece como retirada;
- as evidências do TDD não têm número de linha e citam arquivos que existem;
- o ANDAMENTO.md não descreve trabalho de outro repositório ("../" e cada --vizinho);
- o plugin `sdd` instalado é o da fonte (`../pipeline-prd-tdd-openspec`): só aviso, nunca falha.

Fica fora de qualquer bateria que seja portão de publicação: o estado dos documentos e das
ferramentas da máquina não pode impedir o sistema de ir ao ar. Sem a pasta `sdd/`, avisa que ela
falta; sem a decomposição ou o TDD (o repositório que ainda não os escreveu), a conferência deles é
pulada com aviso. Só python3, sem dependências. Sai com 1 e imprime "FALHA: ..." por problema;
"ok" se nada falhar.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SDD = RAIZ / "sdd"
ANDAMENTO = RAIZ / "ANDAMENTO.md"
FONTE_DO_PLUGIN = (
    RAIZ.parent / "pipeline-prd-tdd-openspec" / "plugins" / "sdd" / ".claude-plugin" / "plugin.json"
)
PLUGINS_INSTALADOS = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
PLUGIN_SDD = "sdd@pipeline-prd-tdd-openspec"
NUMERO = re.compile(r"\d{2,3}")


def _unico(padrao: str) -> Path | None:
    achados = sorted(SDD.glob(padrao))
    return achados[0] if achados else None


def _linhas_de_tabela(texto: str) -> list[list[str]]:
    return [
        [celula.strip() for celula in linha.strip().strip("|").split("|")]
        for linha in texto.splitlines()
        if linha.startswith("|")
    ]


def _numeros(linhas: list[list[str]]) -> set[str]:
    return {celulas[0] for celulas in linhas if NUMERO.fullmatch(celulas[0])}


def conferir_decomposicao(texto: str) -> list[str]:
    if "## 1." not in texto or "## Ciclo" not in texto:
        return ["decomposição sem a seção 1 ou sem a tabela Ciclo"]
    secao_1 = texto.split("## 1.", 1)[1].split("## 2.", 1)[0]
    ciclo = texto.split("## Ciclo", 1)[1].split("## ", 1)[0]
    linhas_1, linhas_ciclo = _linhas_de_tabela(secao_1), _linhas_de_tabela(ciclo)
    falhas = []
    # Uma linha por change; a retirada, com "retirada" no archive (o estado que a página mostra).
    if _numeros(linhas_ciclo) != _numeros(linhas_1):
        falhas.append("decomposição: as changes da seção 1 e as da tabela Ciclo diferem")
    retiradas = {c[0] for c in linhas_1 if NUMERO.fullmatch(c[0]) and "retirada" in c[-1]}
    no_ciclo = {
        c[0] for c in linhas_ciclo if NUMERO.fullmatch(c[0]) and c[-1].startswith("retirada")
    }
    if retiradas != no_ciclo:
        falhas.append("decomposição: a change retirada não aparece como retirada na tabela Ciclo")
    return falhas


def conferir_tdd(texto: str) -> list[str]:
    # O histórico de versões descreve o passado e pode citar o que já saiu.
    corpo = re.split(r"^## (?:\d+\. )?Histórico de versões", texto, maxsplit=1, flags=re.MULTILINE)[
        0
    ]
    falhas = [
        f"TDD: número de linha na evidência: {achado}"
        for achado in re.findall(r"\(linhas? \d[^)]*\)", corpo)
    ]
    for linha in corpo.splitlines():
        if not linha.startswith("- **Evidência:**"):
            continue
        for citado in re.findall(r"`([^`\s]+)`", linha):
            externo = citado.startswith("../") or "*" in citado or "<" in citado
            if externo or "/" not in citado.rstrip("/"):
                continue
            if not (RAIZ / citado).exists():
                falhas.append(f"TDD: a evidência cita um arquivo que não existe: {citado}")
    return falhas


def conferir_andamento(texto: str, vizinhos: list[str]) -> list[str]:
    return [
        f"ANDAMENTO.md cita outro repositório: {nome}"
        for nome in ["../", *vizinhos]
        if nome in texto
    ]


def avisar_plugin() -> str | None:
    if not (FONTE_DO_PLUGIN.is_file() and PLUGINS_INSTALADOS.is_file()):
        return None
    fonte = json.loads(FONTE_DO_PLUGIN.read_text(encoding="utf-8"))["version"]
    plugins = json.loads(PLUGINS_INSTALADOS.read_text(encoding="utf-8"))["plugins"]
    if [instalado["version"] for instalado in plugins.get(PLUGIN_SDD, [])] == [fonte]:
        return None
    return (
        f"plugin sdd instalado fora da versão da fonte ({fonte}): "
        f"rode `claude plugin update {PLUGIN_SDD}` e abra uma sessão nova"
    )


def main(argv: list[str]) -> int:
    if len(argv) % 2 or any(opcao != "--vizinho" for opcao in argv[::2]):
        print(__doc__, file=sys.stderr)
        return 2
    vizinhos = argv[1::2]
    falhas: list[str] = []
    avisos: list[str] = []
    decomposicao, tdd = _unico("decomposicao-*.md"), _unico("tdd-*.md")
    if not SDD.is_dir():
        avisos.append(
            "sem a pasta sdd/: crie-a com `mkdir sdd`; o PRD, o TDD, a decomposição e os "
            "briefings nascem nela"
        )
    if decomposicao:
        falhas += conferir_decomposicao(decomposicao.read_text(encoding="utf-8"))
    elif SDD.is_dir():
        avisos.append("sem sdd/decomposicao-*.md: a tabela Ciclo não foi conferida")
    if tdd:
        falhas += conferir_tdd(tdd.read_text(encoding="utf-8"))
    elif SDD.is_dir():
        avisos.append("sem sdd/tdd-*.md: as evidências não foram conferidas")
    if ANDAMENTO.is_file():
        falhas += conferir_andamento(ANDAMENTO.read_text(encoding="utf-8"), vizinhos)
    aviso_do_plugin = avisar_plugin()
    if aviso_do_plugin:
        avisos.append(aviso_do_plugin)

    for aviso in avisos:
        print(f"aviso: {aviso}", file=sys.stderr)
    for falha in falhas:
        print(f"FALHA: {falha}", file=sys.stderr)
    if not falhas:
        print("ok: decomposição, TDD e ANDAMENTO.md conferidos")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
