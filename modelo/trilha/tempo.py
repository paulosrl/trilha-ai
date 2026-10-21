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

import contextlib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import date, datetime, time, timedelta, timezone
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
TIPOS = ("usuario", "ia")


class ResumoIlegivel(Exception):
    """O resumo existe e não se lê; ele é a única cópia das horas das conversas já apagadas."""


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


def _eventos(
    configuracao: Path, raiz: Path, ignorados: dict[str, list]
) -> tuple[dict[str, set[tuple[float, bool]]], dict[str, list]]:
    """Os eventos de cada conversa feita dentro da raiz, (instante, é pedido do usuário), e os
    arquivos lidos sem nada dela, com a data e o tamanho: enquanto eles não mudam, não se leem de
    novo."""
    projetos = configuracao / "projects"
    if not projetos.is_dir():
        return {}, {}
    texto_da_raiz = str(raiz)
    # O caminho como ele aparece dentro do JSON: com os acentos como são, como o Claude Code grava,
    # e com o escape \u, por garantia.
    marcas = {json.dumps(texto_da_raiz, ensure_ascii=False)[1:-1], json.dumps(texto_da_raiz)[1:-1]}
    conversas: dict[str, set[tuple[float, bool]]] = {}
    sem_a_raiz: dict[str, list] = {}
    for arquivo in projetos.rglob("*.jsonl"):
        try:
            estado = arquivo.stat()
        except OSError:
            continue
        chave, assinatura = str(arquivo), [estado.st_mtime_ns, estado.st_size]
        if ignorados.get(chave) == assinatura:
            sem_a_raiz[chave] = assinatura
            continue
        try:
            entrada = arquivo.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        achou = False
        with entrada:
            for texto in entrada:
                if not any(marca in texto for marca in marcas):  # decodificar só o que pode servir
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
                achou = True
        if not achou:
            sem_a_raiz[chave] = assinatura
    return conversas, sem_a_raiz


def _intervalos(eventos: set[tuple[float, bool]]) -> list[list]:
    """Os intervalos ativos de uma conversa: [início, fim, "usuario" ou "ia"], em ISO UTC; os
    seguidos do mesmo tipo se juntam num só, o que encolhe o resumo sem mudar nenhuma soma."""
    juntos: list[list] = []
    for (a, _), (b, pedido) in pairwise(sorted(eventos)):
        if not 0 < b - a <= PAUSA:
            continue
        tipo = "usuario" if pedido else "ia"
        if juntos and juntos[-1][1] == a and juntos[-1][2] == tipo:
            juntos[-1][1] = b
        else:
            juntos.append([a, b, tipo])
    return [[_iso(a), _iso(b), tipo] for a, b, tipo in juntos]


def _juntar(*listas: list[list]) -> list[list]:
    """Os intervalos de uma conversa, os guardados e os recalculados, unidos por tipo: o que um
    arquivo já apagado (o de um subagente, por exemplo) cobria continua, e o repetido conta uma
    vez. O tempo da IA sai do total menos o do usuário, então um par de tipos sobreposto não soma
    duas vezes."""
    por_tipo: dict[str, list[tuple[float, float]]] = {}
    for lista in listas:
        for inicio, fim, tipo in lista:
            por_tipo.setdefault(tipo, []).append((_instante(inicio), _instante(fim)))
    juntos = sorted((a, b, tipo) for tipo, pares in por_tipo.items() for a, b in _uniao(pares))
    return [[_iso(a), _iso(b), tipo] for a, b, tipo in juntos]


# O resumo


def _intervalo_valido(item: object) -> bool:
    if not (isinstance(item, list) and len(item) == 3 and item[2] in TIPOS):
        return False
    try:
        return _instante(item[0]) <= _instante(item[1])
    except (AttributeError, TypeError, ValueError):
        return False


def _ler_resumo(arquivo: Path) -> tuple[dict[str, list], dict[str, list]]:
    """As conversas e os arquivos lidos sem nada do repositório; ({}, {}) quando não há resumo. O
    resumo que existe e não se lê é recusado: sobrescrevê-lo perderia as horas já apagadas."""
    if not arquivo.exists():
        return {}, {}
    try:
        resumo = json.loads(arquivo.read_text(encoding="utf-8"))
    except (OSError, ValueError) as erro:
        raise ResumoIlegivel(f"não é JSON: {erro}") from erro
    if not isinstance(resumo, dict) or resumo.get("versao") != VERSAO_DO_RESUMO:
        raise ResumoIlegivel(f"não é um resumo da versão {VERSAO_DO_RESUMO}")
    conversas, ignorados = resumo.get("conversas"), resumo.get("ignorados", {})
    if not isinstance(conversas, dict) or not all(
        isinstance(lista, list) and all(map(_intervalo_valido, lista))
        for lista in conversas.values()
    ):
        raise ResumoIlegivel("uma conversa tem um intervalo fora do formato")
    if not isinstance(ignorados, dict) or not all(
        isinstance(par, list) and len(par) == 2 and all(isinstance(n, int) for n in par)
        for par in ignorados.values()
    ):
        raise ResumoIlegivel("a lista dos arquivos já lidos está fora do formato")
    return conversas, ignorados


def _gravar(arquivo: Path, texto: str) -> None:
    """Grava num temporário de nome único da mesma pasta, leva ao disco e troca: nem uma queda no
    meio nem outra execução ao mesmo tempo corrompem o arquivo."""
    descritor, temporario = tempfile.mkstemp(
        dir=arquivo.parent, prefix=arquivo.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(descritor, "w", encoding="utf-8") as saida:
            saida.write(texto)
            saida.flush()
            os.fsync(saida.fileno())
        os.replace(temporario, arquivo)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temporario)
        raise


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


def _meia_noite(instante: float) -> float:
    """O instante da meia-noite local do dia do instante."""
    return datetime.combine(datetime.fromtimestamp(instante).date(), time()).timestamp()


def _sessoes_de_commits(instantes: list[float]) -> list[tuple[float, float]]:
    """O trabalho antes do primeiro commit de uma sessão não passa da meia-noite do dia dele: o
    commit das 00:10 não lança horas no dia anterior, em que ninguém trabalhou."""
    sessoes: list[list[float]] = []
    for instante in instantes:
        if sessoes and instante - sessoes[-1][1] <= SESSAO_DE_COMMITS:
            sessoes[-1][1] = instante
        else:
            sessoes.append([max(instante - ANTES_DO_COMMIT, _meia_noite(instante)), instante])
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


def _no_relogio(instante: float, dia: date) -> float:
    """Os minutos que o relógio local marca, de 0 a 1440 (o fim do dia). No dia da mudança de
    horário, a posição segue o relógio, e não o tempo corrido desde a meia-noite."""
    local = datetime.fromtimestamp(instante)
    if local.date() > dia:
        return 1440.0
    return round(local.hour * 60 + local.minute + local.second / 60 + local.microsecond / 6e7, 1)


def _faixas(pares: list[tuple[float, float]], dia: date) -> list[list[float]]:
    """Os intervalos de um dia nas posições do relógio local, para a fita da página."""
    return [[_no_relogio(inicio, dia), _no_relogio(fim, dia)] for inicio, fim in pares]


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
        data = date.fromisoformat(dia)
        total = _uniao(dias_todos.get(dia, []))
        # O dia cujas conversas somam menos de um décimo de minuto não tem tempo apurado delas.
        if _minutos(total) > 0:
            usuario = _uniao(dias_usuario.get(dia, []))
            minutos, minutos_do_usuario = _minutos(total), _minutos(usuario)
            registro = {
                "fonte": "conversas",
                "total": minutos,
                "usuario": minutos_do_usuario,
                "ia": round(minutos - minutos_do_usuario, 1),
                "faixas": _faixas(total, data),
                "faixas_usuario": _faixas(usuario, data),
            }
        else:
            total = _uniao(dias_commits.get(dia, []))
            if _minutos(total) == 0:
                continue
            registro = {
                "fonte": "commits",
                "total": _minutos(total),
                "usuario": None,
                "ia": None,
                "faixas": _faixas(total, data),
                "faixas_usuario": [],
            }
        saida.append({"d": dia, "commits": contagem.get(dia, 0), **registro})
    return saida


# O aviso, a página e a saída


def _aviso_da_guarda(configuracao: Path) -> str | None:
    """O aviso quando o Claude Code apaga as conversas cedo: o cleanupPeriodDays falta ou é menor
    que o mínimo. Ele cita o prazo de verdade, o definido ou o padrão."""
    settings = configuracao / "settings.json"
    try:
        valor = json.loads(settings.read_text(encoding="utf-8")).get("cleanupPeriodDays")
    except (OSError, ValueError, AttributeError):
        valor = None
    numero = isinstance(valor, (int, float)) and not isinstance(valor, bool)
    if numero and valor >= GUARDA_MINIMA:
        return None
    prazo = f"depois de {valor:g} dias" if numero else "depois de 30 dias, o prazo padrão"
    return (
        f"aviso: o Claude Code apaga as conversas {prazo}; ponha {GUARDA_SUGERIDA} em "
        f"{settings} para guardá-las por mais tempo"
    )


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

    try:
        conversas, ignorados = _ler_resumo(resumo)
    except ResumoIlegivel as erro:
        print(
            f"tempo: o resumo {resumo} não se lê ({erro}). Ele guarda as horas das conversas já "
            "apagadas e não foi sobrescrito: corrija-o ou mova-o, e rode de novo",
            file=sys.stderr,
        )
        return 1
    eventos, ignorados = _eventos(configuracao, raiz, ignorados)
    for sessao, da_conversa in eventos.items():
        conversas[sessao] = _juntar(conversas.get(sessao, []), _intervalos(da_conversa))
    dias = _apurar(conversas, _commits(raiz))

    pasta.mkdir(parents=True, exist_ok=True)
    conteudo = {
        "versao": VERSAO_DO_RESUMO,
        "raiz": str(raiz),
        "conversas": conversas,
        "ignorados": ignorados,
    }
    _gravar(resumo, json.dumps(conteudo, ensure_ascii=False, separators=(",", ":")) + "\n")
    _gravar(pagina, _pagina(raiz.name, dias))

    if dias:
        horas = round(sum(d["total"] for d in dias) / 60)
        quantos = f"{len(dias)} dia" + ("s" if len(dias) != 1 else "")
        print(f"{_data(dias[0]['d'])} a {_data(dias[-1]['d'])}: {quantos}, {horas} h")
    else:
        print("nenhuma hora apurada: o repositório não tem conversas guardadas nem commits")
    print(f"página: {pagina}")
    aviso = _aviso_da_guarda(configuracao)
    if aviso:
        print(aviso, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
