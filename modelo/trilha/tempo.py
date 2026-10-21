"""Apura as horas de trabalho de cada dia neste repositório e gera a página delas.

Lê o que já está na máquina, sem nada rodar a cada interação: as conversas do Claude Code feitas
dentro do repositório (com a hora de cada pedido do usuário e de cada ação da IA) e os commits.
Nas conversas, o intervalo de até 30 minutos entre dois eventos seguidos conta: é do usuário se
termina num pedido dele, e da IA se termina numa ação dela; conversas em paralelo contam uma vez.
O dia sem conversa guardada é estimado pelos commits: commits com até 2 horas de intervalo formam
uma sessão, que começa 30 minutos antes do primeiro. Os dias seguem o relógio da máquina.

Guarda, fora do repositório, em <XDG_DATA_HOME ou ~/.local/share>/trilha-ai/tempo/, um resumo só
com datas e horas (nenhum texto das conversas), completado a cada execução: as horas apuradas
sobrevivem quando o Claude Code apaga as conversas. A página fica ao lado do resumo; o visual e o
comportamento dela ficam em trilha/pagina_tempo_modelo.html.

Uso (Python 3 puro, sem dependências), dentro do repositório:
    python3 trilha/tempo.py
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, time, timedelta, timezone
from itertools import pairwise
from pathlib import Path

PAUSA = 30 * 60  # o maior intervalo entre dois eventos de uma conversa que ainda conta
SESSAO_DE_COMMITS = 2 * 3600  # o maior intervalo entre dois commits da mesma sessão
ANTES_DO_COMMIT = 30 * 60  # o trabalho que antecede o primeiro commit de uma sessão
GUARDA_MINIMA = 365  # dias de guarda das conversas abaixo dos quais o comando avisa
GUARDA_SUGERIDA = '"cleanupPeriodDays": 3650'
MODELO = Path(__file__).resolve().parent / "pagina_tempo_modelo.html"
VERSAO_DO_RESUMO = 1
UTC = timezone(timedelta(0))  # o datetime.UTC e o "Z" no fromisoformat pedem o Python 3.11


def _pasta(variavel: str, padrao: Path) -> Path:
    """A pasta da variável de ambiente; vazia vale como ausente."""
    valor = os.environ.get(variavel, "").strip()
    return Path(valor) if valor else padrao


def _configuracao() -> Path:
    return _pasta("CLAUDE_CONFIG_DIR", Path.home() / ".claude")


def _pasta_dos_dados() -> Path:
    return _pasta("XDG_DATA_HOME", Path.home() / ".local" / "share") / "trilha-ai" / "tempo"


def _raiz() -> Path | None:
    saida = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    )
    caminho = saida.stdout.strip()
    return Path(caminho) if saida.returncode == 0 and caminho else None


def _instante(texto: str) -> float:
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    return datetime.fromisoformat(texto).timestamp()


def _iso(instante: float) -> str:
    return datetime.fromtimestamp(instante, UTC).isoformat()


# As conversas


def _pedido(linha: dict) -> bool:
    """A mensagem escrita pelo usuário: nem metadados, nem subagente, nem resumo da compactação,
    nem só o resultado de uma ferramenta."""
    if linha.get("type") != "user":
        return False
    if linha.get("isMeta") or linha.get("isSidechain") or linha.get("isCompactSummary"):
        return False
    conteudo = (linha.get("message") or {}).get("content")
    if isinstance(conteudo, list):
        return any(isinstance(p, dict) and p.get("type") != "tool_result" for p in conteudo)
    return isinstance(conteudo, str)


def _eventos(configuracao: Path, raiz: Path) -> dict[str, set[tuple[float, bool]]]:
    """Os eventos de cada conversa feita dentro da raiz: (instante, é pedido do usuário)."""
    projetos = configuracao / "projects"
    if not projetos.is_dir():
        return {}
    texto_da_raiz = str(raiz)
    marca = json.dumps(texto_da_raiz)[1:-1]  # o caminho como ele aparece dentro do JSON
    conversas: dict[str, set[tuple[float, bool]]] = {}
    for arquivo in sorted(projetos.rglob("*.jsonl")):
        try:
            entrada = arquivo.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with entrada:
            for texto in entrada:
                if marca not in texto:  # decodificar só a linha que pode ser deste repositório
                    continue
                try:
                    linha = json.loads(texto)
                except ValueError:
                    continue
                if not isinstance(linha, dict) or linha.get("type") not in ("user", "assistant"):
                    continue
                cwd, sessao, hora = linha.get("cwd"), linha.get("sessionId"), linha.get("timestamp")
                if not all(isinstance(v, str) for v in (cwd, sessao, hora)):
                    continue
                if cwd != texto_da_raiz and not cwd.startswith(texto_da_raiz + "/"):
                    continue
                try:
                    instante = _instante(hora)
                except ValueError:
                    continue
                conversas.setdefault(sessao, set()).add((instante, _pedido(linha)))
    return conversas


def _intervalos(eventos: set[tuple[float, bool]]) -> list[list]:
    """Os intervalos ativos de uma conversa: [início, fim, "usuario" ou "ia"], em ISO UTC."""
    ordem = sorted(eventos)
    return [
        [_iso(a), _iso(b), "usuario" if pedido else "ia"]
        for (a, _), (b, pedido) in pairwise(ordem)
        if 0 < b - a <= PAUSA
    ]


# O resumo


def _ler_resumo(arquivo: Path) -> dict[str, list]:
    try:
        resumo = json.loads(arquivo.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(resumo, dict) or resumo.get("versao") != VERSAO_DO_RESUMO:
        return {}
    conversas = resumo.get("conversas")
    return conversas if isinstance(conversas, dict) else {}


def _gravar(arquivo: Path, texto: str) -> None:
    """Grava num temporário da mesma pasta e troca: uma queda no meio não corrompe o arquivo."""
    temporario = arquivo.with_name(arquivo.name + ".tmp")
    temporario.write_text(texto, encoding="utf-8")
    os.replace(temporario, arquivo)


# Os commits


def _commits(raiz: Path) -> list[float]:
    """O instante de cada commit das branches, das remotas e das tags, uma vez, pelo autor."""
    saida = subprocess.run(
        ["git", "-C", str(raiz), "log", "--branches", "--remotes", "--tags", "--format=%H %aI"],
        capture_output=True,
        text=True,
        check=False,
    )
    if saida.returncode != 0:
        return []
    commits = {}
    for linha in saida.stdout.splitlines():
        hash_, _, quando = linha.partition(" ")
        if quando:
            commits[hash_] = datetime.fromisoformat(quando).timestamp()
    return sorted(commits.values())


def _sessoes_de_commits(instantes: list[float]) -> list[tuple[float, float]]:
    sessoes: list[list[float]] = []
    for instante in instantes:
        if sessoes and instante - sessoes[-1][1] <= SESSAO_DE_COMMITS:
            sessoes[-1][1] = instante
        else:
            sessoes.append([instante - ANTES_DO_COMMIT, instante])
    return [(a, b) for a, b in sessoes]


# Os dias


def _por_dia(pares: list[tuple[float, float]]) -> dict[str, list[tuple[float, float]]]:
    """Os intervalos cortados na meia-noite local, agrupados pela data local."""
    dias: dict[str, list[tuple[float, float]]] = {}
    for inicio, fim in pares:
        while inicio < fim:
            local = datetime.fromtimestamp(inicio)
            meia_noite = datetime.combine(local.date() + timedelta(days=1), time()).timestamp()
            corte = min(fim, meia_noite)
            dias.setdefault(local.date().isoformat(), []).append((inicio, corte))
            inicio = corte
    return dias


def _uniao(pares: list[tuple[float, float]]) -> list[tuple[float, float]]:
    juntos: list[list[float]] = []
    for inicio, fim in sorted(pares):
        if juntos and inicio <= juntos[-1][1]:
            juntos[-1][1] = max(juntos[-1][1], fim)
        else:
            juntos.append([inicio, fim])
    return [(a, b) for a, b in juntos]


def _minutos(pares: list[tuple[float, float]]) -> float:
    return round(sum(b - a for a, b in pares) / 60, 1)


def _faixas(pares: list[tuple[float, float]]) -> list[list[float]]:
    """Os intervalos de um dia em minutos desde a meia-noite local, para a página."""
    faixas = []
    for inicio, fim in pares:
        local = datetime.fromtimestamp(inicio)
        zero = datetime.combine(local.date(), time()).timestamp()
        faixas.append([round((inicio - zero) / 60, 1), round((fim - zero) / 60, 1)])
    return faixas


def _apurar(conversas: dict[str, list], commits: list[float]) -> list[dict]:
    todos: list[tuple[float, float]] = []
    do_usuario: list[tuple[float, float]] = []
    for intervalos in conversas.values():
        for inicio, fim, tipo in intervalos:
            par = (_instante(inicio), _instante(fim))
            todos.append(par)
            if tipo == "usuario":
                do_usuario.append(par)
    dias_todos, dias_usuario = _por_dia(todos), _por_dia(do_usuario)
    contagem: dict[str, int] = {}
    for instante in commits:
        dia = datetime.fromtimestamp(instante).date().isoformat()
        contagem[dia] = contagem.get(dia, 0) + 1
    dias_commits = _por_dia(_sessoes_de_commits(commits))
    saida = []
    for dia in sorted(set(dias_todos) | set(dias_commits)):
        if dia in dias_todos:
            total = _uniao(dias_todos[dia])
            usuario = _uniao(dias_usuario.get(dia, []))
            minutos, minutos_do_usuario = _minutos(total), _minutos(usuario)
            registro = {
                "fonte": "conversas",
                "total": minutos,
                "usuario": minutos_do_usuario,
                "ia": round(minutos - minutos_do_usuario, 1),
                "faixas": _faixas(total),
                "faixas_usuario": _faixas(usuario),
            }
        else:
            total = _uniao(dias_commits[dia])
            registro = {
                "fonte": "commits",
                "total": _minutos(total),
                "usuario": None,
                "ia": None,
                "faixas": _faixas(total),
                "faixas_usuario": [],
            }
        saida.append({"d": dia, "commits": contagem.get(dia, 0), **registro})
    return saida


# O aviso, a página e a saída


def _guarda_curta(configuracao: Path) -> bool:
    """O Claude Code apaga as conversas cedo: o cleanupPeriodDays falta ou é menor que o mínimo."""
    try:
        valor = json.loads((configuracao / "settings.json").read_text(encoding="utf-8"))
        valor = valor.get("cleanupPeriodDays")
    except (OSError, ValueError, AttributeError):
        return True
    numero = isinstance(valor, (int, float)) and not isinstance(valor, bool)
    return not (numero and valor >= GUARDA_MINIMA)


def _json_seguro(valor: object) -> str:
    return json.dumps(valor, ensure_ascii=False).replace("</", "<\\/")


def _pagina(nome: str, dias: list[dict]) -> str:
    dados = {
        "repositorio": nome,
        "gerada": datetime.now().astimezone().strftime("%d/%m/%Y %H:%M"),
        "pausa": PAUSA // 60,
        "sessao_de_commits": SESSAO_DE_COMMITS // 60,
        "antes_do_commit": ANTES_DO_COMMIT // 60,
        "dias": dias,
    }
    modelo = MODELO.read_text(encoding="utf-8")
    return modelo.replace("__TITULO__", f"Horas de {nome}").replace(
        "__DADOS__", _json_seguro(dados)
    )


def _data(dia: str) -> str:
    return datetime.fromisoformat(dia).strftime("%d/%m/%Y")


def main() -> int:
    raiz = _raiz()
    if raiz is None:
        print("tempo: a pasta atual não é um repositório git; rode dentro dele", file=sys.stderr)
        return 1
    configuracao = _configuracao()
    pasta = _pasta_dos_dados()
    caminho = hashlib.sha1(str(raiz).encode("utf-8")).hexdigest()[:8]
    resumo = pasta / f"{raiz.name}-{caminho}.json"
    pagina = resumo.with_suffix(".html")

    conversas = _ler_resumo(resumo)
    for sessao, eventos in _eventos(configuracao, raiz).items():
        conversas[sessao] = _intervalos(eventos)  # a conversa que ainda existe é recalculada
    dias = _apurar(conversas, _commits(raiz))

    pasta.mkdir(parents=True, exist_ok=True)
    conteudo = {"versao": VERSAO_DO_RESUMO, "raiz": str(raiz), "conversas": conversas}
    _gravar(resumo, json.dumps(conteudo, ensure_ascii=False, indent=1) + "\n")
    _gravar(pagina, _pagina(raiz.name, dias))

    if dias:
        horas = round(sum(d["total"] for d in dias) / 60)
        print(f"{_data(dias[0]['d'])} a {_data(dias[-1]['d'])}: {len(dias)} dias, {horas} h")
    else:
        print("nenhuma hora apurada: o repositório não tem conversas guardadas nem commits")
    print(f"página: {pagina}")
    if _guarda_curta(configuracao):
        print(
            "aviso: o Claude Code apaga as conversas com o prazo padrão de 30 dias; ponha "
            f"{GUARDA_SUGERIDA} em {configuracao / 'settings.json'} para guardá-las por mais tempo",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
