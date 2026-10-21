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

import bisect
import contextlib
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from itertools import pairwise
from pathlib import Path

PAUSA = 30 * 60  # o maior intervalo entre dois eventos de uma conversa que ainda conta
SESSAO_DE_COMMITS = 2 * 3600  # o maior intervalo entre dois commits da mesma sessão
ANTES_DO_COMMIT = 30 * 60  # o trabalho que antecede o primeiro commit de uma sessão
GUARDA_MINIMA = 365  # dias de guarda das conversas abaixo dos quais o comando avisa
GUARDA_SUGERIDA = '"cleanupPeriodDays": 3650'
MODELO = Path(__file__).resolve().parent / "pagina_tempo_modelo.html"
VERSAO_DO_RESUMO = 2  # a 1, da 2.8, ainda se lê (ver _ler_resumo)
UTC = timezone(timedelta(0))  # o datetime.UTC e o "Z" no fromisoformat pedem o Python 3.11
TIPOS = ("usuario", "ia")
MAXIMO_NO_AVISO = 3  # os e-mails de fora que o aviso cita
FORA = "fora"  # o evento da conversa com cwd fora da raiz, ou noutro repositório dentro dela


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


def _diretorio_comum(raiz: Path) -> Path | None:
    """A pasta .git que a raiz e os worktrees dela dividem; o caminho relativo vale a partir da
    raiz (o --path-format=absolute pede o git 2.31)."""
    caminho = (_git_texto(raiz, "rev-parse", "--git-common-dir") or "").strip()
    return (raiz / caminho).resolve() if caminho else None


def _tem_git(pasta: Path) -> bool | None:
    """A pasta tem um .git; None quando não se confere (sem permissão, um caminho inválido). O
    stat direto, e não o exists(), porque o exists() muda com o Python: até o 3.13 levanta o erro
    de permissão, e no 3.14 devolve False."""
    try:
        (pasta / ".git").stat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    except (OSError, ValueError):
        return None
    return True


def _de_outro_repositorio(git: Path, comum: Path | None) -> bool:
    """A pasta com este .git é outro repositório: um .git em pasta, ou um em arquivo que não
    aponta para um worktree da raiz (o de um submódulo aponta para .git/modules/)."""
    if git.is_dir():
        return True
    try:
        primeira = git.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return True
    if not primeira.startswith("gitdir:") or comum is None:
        return True
    destino = (git.parent / primeira.removeprefix("gitdir:").strip()).resolve()
    return not destino.is_relative_to(comum / "worktrees")


def _eh_da_raiz(cwd: str, raiz: Path, comum: Path | None, vistos: dict[str, bool]) -> bool:
    """O cwd é a raiz, ou uma pasta dentro dela que não é de outro repositório git aninhado; um
    worktree da própria raiz conta como dela. A pasta que já não existe, ou cujo .git não se
    confere, conta para a raiz."""
    texto_da_raiz = str(raiz)
    if cwd == texto_da_raiz:
        return True
    if not cwd.startswith(texto_da_raiz + "/"):
        return False
    if cwd not in vistos:
        pasta, da_raiz = Path(cwd), True
        while pasta != raiz and pasta != pasta.parent:
            if _tem_git(pasta) and _de_outro_repositorio(pasta / ".git", comum):
                da_raiz = False
                break
            pasta = pasta.parent
        vistos[cwd] = da_raiz
    return vistos[cwd]


Eventos = dict[tuple[float, str], set[int]]


def _eventos(
    configuracao: Path, raiz: Path, ignorados: dict[str, list]
) -> tuple[dict[str, Eventos], dict[str, list]]:
    """Os eventos de cada conversa que citou a raiz, (instante, tipo), com o tipo "pedido", "ia"
    ou "fora" (a conversa só com eventos "fora" vem também, para o resumo da 2.8), e os arquivos
    de onde cada um veio: a linha repetida em dois arquivos (a conversa retomada) é um evento só,
    dos dois. E os arquivos lidos sem nada da raiz, com a data e o tamanho: enquanto eles não
    mudam, não se leem de novo."""
    projetos = configuracao / "projects"
    if not projetos.is_dir():
        return {}, {}
    texto_da_raiz = str(raiz)
    # O caminho como ele aparece dentro do JSON: com os acentos como são, como o Claude Code grava,
    # e com o escape \u, por garantia.
    marcas = {json.dumps(texto_da_raiz, ensure_ascii=False)[1:-1], json.dumps(texto_da_raiz)[1:-1]}
    comum, vistos = _diretorio_comum(raiz), {}
    conversas: dict[str, Eventos] = {}
    sem_a_raiz: dict[str, list] = {}
    for numero, arquivo in enumerate(projetos.rglob("*.jsonl")):
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
            # Primeiro, só as linhas que citam a raiz, até uma delas ser um evento da raiz: a
            # conversa de outro repositório que só cita o caminho não passa disso. Achado o
            # evento, cada linha com cwd, do começo, de dentro ou de fora da raiz, porque a saída
            # para outra pasta corta o tempo da conversa.
            achados = []
            for texto in entrada:
                citada = any(marca in texto for marca in marcas)
                evento = _evento(texto, raiz, comum, vistos) if citada else None
                if evento is not None and evento[2] != FORA:
                    achou = True
                    break
                if evento is not None:
                    achados.append(evento)
            if achou:
                entrada.seek(0)
                com_cwd = (texto for texto in entrada if '"cwd"' in texto)
                achados = filter(None, (_evento(t, raiz, comum, vistos) for t in com_cwd))
            for sessao, instante, tipo in achados:
                conversas.setdefault(sessao, {}).setdefault((instante, tipo), set()).add(numero)
        if not achou:
            sem_a_raiz[chave] = assinatura
    return conversas, sem_a_raiz


def _evento(
    texto: str, raiz: Path, comum: Path | None, vistos: dict[str, bool]
) -> tuple[str, float, str] | None:
    """A conversa, o instante e o tipo do evento da linha; None quando ela não é um evento."""
    try:
        linha = json.loads(texto)
    except ValueError:
        return None
    if not isinstance(linha, dict) or linha.get("type") not in ("user", "assistant"):
        return None
    cwd, sessao, hora = linha.get("cwd"), linha.get("sessionId"), linha.get("timestamp")
    if not all(isinstance(v, str) for v in (cwd, sessao, hora)):
        return None
    try:
        instante = _instante(hora)
    except ValueError:
        return None
    if not _eh_da_raiz(cwd, raiz, comum, vistos):
        return sessao, instante, FORA
    return sessao, instante, "pedido" if _pedido(linha) else "ia"


def _intervalos(eventos: Eventos) -> list[list]:
    """Os intervalos ativos de uma conversa: [início, fim, "usuario" ou "ia"], em ISO UTC. Conta
    o par seguido de eventos da raiz, de qualquer arquivo dela, com até 30 minutos, salvo quando
    os dois vêm de um mesmo arquivo e ele saiu da raiz entre eles: um subagente noutra pasta não
    corta a conversa principal. Os seguidos do mesmo tipo se juntam num só."""
    saidas: dict[int, list[float]] = {}
    for (instante, tipo), arquivos in eventos.items():
        if tipo == FORA:
            for arquivo in arquivos:
                saidas.setdefault(arquivo, []).append(instante)
    for lista in saidas.values():
        lista.sort()
    da_raiz = sorted((i, t, frozenset(a)) for (i, t), a in eventos.items() if t != FORA)
    juntos: list[list] = []
    for (a, _, arquivos_a), (b, tipo_b, arquivos_b) in pairwise(da_raiz):
        if not 0 < b - a <= PAUSA:
            continue
        if any(_saiu(saidas.get(arquivo, []), a, b) for arquivo in arquivos_a & arquivos_b):
            continue
        tipo = "usuario" if tipo_b == "pedido" else "ia"
        if juntos and juntos[-1][1] == a and juntos[-1][2] == tipo:
            juntos[-1][1] = b
        else:
            juntos.append([a, b, tipo])
    return [[_iso(a), _iso(b), tipo] for a, b, tipo in juntos]


def _saiu(saidas: list[float], a: float, b: float) -> bool:
    """Há uma saída da raiz entre os instantes a e b, sem eles."""
    i = bisect.bisect_right(saidas, a)
    return i < len(saidas) and saidas[i] < b


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


def _ler_resumo(arquivo: Path) -> tuple[dict[str, list], dict[str, list], int]:
    """As conversas, os arquivos lidos sem nada do repositório e a versão do resumo; ({}, {}, a
    versão atual) quando não há resumo. A versão 1, da 2.8, ainda se lê. O resumo que existe e não
    se lê é recusado: sobrescrevê-lo perderia as horas já apagadas."""
    if not arquivo.exists():
        return {}, {}, VERSAO_DO_RESUMO
    try:
        resumo = json.loads(arquivo.read_text(encoding="utf-8"))
    except (OSError, ValueError) as erro:
        raise ResumoIlegivel(f"não é JSON: {erro}") from erro
    versao = resumo.get("versao") if isinstance(resumo, dict) else None
    if versao not in (1, VERSAO_DO_RESUMO):
        raise ResumoIlegivel(f"não é um resumo da versão 1 nem da {VERSAO_DO_RESUMO}")
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
    return conversas, ignorados, versao


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


def _git_texto(raiz: Path, *args: str) -> str | None:
    saida = subprocess.run(
        ["git", "-C", str(raiz), *args], capture_output=True, text=True, check=False
    )
    return saida.stdout if saida.returncode == 0 else None


def _lista(raiz: Path, chave: str) -> list[str]:
    """Os valores de uma chave do git que pode se repetir, um por linha: o e-mail com espaço é
    um só."""
    texto = _git_texto(raiz, "config", "--get-all", chave) or ""
    return [linha.strip() for linha in texto.splitlines() if linha.strip()]


def _commits(raiz: Path) -> tuple[list[float], Counter[str]]:
    """O instante de cada commit do usuário nas branches, nas remotas e nas tags, uma vez, pela
    data de autor, e quantos commits de cada outro e-mail ficaram fora. Os e-mails do usuário são
    os de autor do git (o GIT_AUTHOR_EMAIL, o author.email e o user.email de todas as
    configurações, ou, sem eles, o EMAIL, como o git os escolhe no commit) e os do trilha.email;
    sem nenhum de autor, contam os de todos. A assinatura fica fora da saída."""
    saida = _git_texto(
        raiz,
        "log",
        "--branches",
        "--remotes",
        "--tags",
        "--no-show-signature",
        "--format=%H%x00%ae%x00%aI",
    )
    ambiente = os.environ.get("GIT_AUTHOR_EMAIL", "").strip()
    de_autor = [ambiente] if ambiente else []
    de_autor += _lista(raiz, "author.email") + _lista(raiz, "user.email")
    if not de_autor and os.environ.get("EMAIL", "").strip():
        de_autor = [os.environ["EMAIL"].strip()]
    emails = {*de_autor, *_lista(raiz, "trilha.email")} if de_autor else None
    return _ler_commits(saida or "", emails)


def _ler_commits(saida: str, emails: set[str] | None) -> tuple[list[float], Counter[str]]:
    """Os instantes da saída do git log (hash, e-mail e data, separados pelo caractere nulo, que
    não aparece num e-mail), só dos e-mails dados (todos, sem eles), e quantos commits de cada
    outro e-mail, não vazio, ficaram fora; a linha que não se entende é ignorada. O e-mail é o do
    autor sem o .mailmap (%ae), como o user.email. O git log já lista cada commit uma vez."""
    do_usuario = {e.lower() for e in emails} if emails else None
    instantes: list[float] = []
    fora: Counter[str] = Counter()
    for linha in saida.splitlines():
        partes = linha.split("\x00")
        if len(partes) != 3:
            continue
        _, autor, quando = partes
        if do_usuario is not None and autor.lower() not in do_usuario:
            if autor:
                fora[autor] += 1
            continue
        try:
            instantes.append(_instante(quando))
        except ValueError:
            continue
    return sorted(instantes), fora


def _aviso_dos_emails(fora: Counter[str], outros: list[str]) -> str | None:
    """Os e-mails cujos commits ficaram fora da estimativa, sem os de robôs e os do trilha.outro
    (os de outras pessoas), com o comando que inclui um deles e o que o tira do aviso."""
    de_outros = {e.lower() for e in outros}
    pessoas = [
        (autor, n)
        for autor, n in fora.most_common()
        if "[bot]" not in autor and autor.lower() not in de_outros
    ]
    if not pessoas:
        return None
    lista = ", ".join(f"{autor} ({n})" for autor, n in pessoas[:MAXIMO_NO_AVISO])
    if len(pessoas) > MAXIMO_NO_AVISO:
        lista += f" e mais {len(pessoas) - MAXIMO_NO_AVISO}"
    return (
        f"aviso: os commits destes e-mails ficaram fora da estimativa: {lista}; no repositório, "
        "rode git config --add trilha.email <e-mail> se ele é seu, ou git config --add "
        "trilha.outro <e-mail> se é de outra pessoa"
    )


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
    primeiro: dict[str, float] = {}
    for instante in commits:
        dia = datetime.fromtimestamp(instante).date().isoformat()
        contagem[dia] = contagem.get(dia, 0) + 1
        primeiro.setdefault(dia, instante)
    dias_commits = _por_dia(_sessoes_de_commits(commits))
    # O dia com commit tem pelo menos 1 minuto: o commit das 00:00:00 não some.
    for dia, instante in primeiro.items():
        if sum(b - a for a, b in _uniao(dias_commits.get(dia, []))) < 60:
            dias_commits.setdefault(dia, []).append((instante, instante + 60))
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
    # Todo < vira \u003c, que o JSON lê igual: nem </script> nem <!-- fecham ou abrem nada.
    return json.dumps(valor, ensure_ascii=False).replace("<", "\\u003c")


def _pagina(nome: str, dias: list[dict]) -> str:
    dados = {
        "repositorio": nome,
        "gerada": datetime.now().astimezone().strftime("%d/%m/%Y %H:%M"),
        "pausa": PAUSA // 60,
        "sessao_de_commits": SESSAO_DE_COMMITS // 60,
        "antes_do_commit": ANTES_DO_COMMIT // 60,
        "dias": dias,
    }
    # Só os dois marcadores inteiros, uma vez cada: o título protegido não forma o dos dados, e o
    # JSON seguro não forma o do título.
    titulo = f"<title>{html.escape(f'Horas de {nome}')}</title>"
    bloco = f'<script id="dados" type="application/json">{_json_seguro(dados)}</script>'
    modelo = MODELO.read_text(encoding="utf-8")
    modelo = modelo.replace("<title>__TITULO__</title>", titulo, 1)
    return modelo.replace('<script id="dados" type="application/json">__DADOS__</script>', bloco, 1)


def _outros_resumos(pasta: Path, raiz: Path) -> list[tuple[Path, str]]:
    """Os resumos de outro caminho com o mesmo nome de repositório, com a raiz gravada; o que
    nem a raiz deixa ler é ignorado."""
    if not pasta.is_dir():
        return []
    nome = re.compile(re.escape(raiz.name) + r"-[0-9a-f]{8}\.json")
    achados = []
    for outro in sorted(pasta.glob("*.json")):
        if not nome.fullmatch(outro.name):
            continue
        try:
            antiga = json.loads(outro.read_text(encoding="utf-8")).get("raiz")
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(antiga, str) and antiga != str(raiz) and Path(antiga).name == raiz.name:
            achados.append((outro, antiga))
    return achados


def _renomear_juntado(arquivo: Path) -> Path:
    """Renomeia com o sufixo .juntado, sem sobrescrever um anterior (o repositório que foi e
    voltou): o novo ganha um número."""
    destino, numero = arquivo.with_name(f"{arquivo.name}.juntado"), 2
    while destino.exists():
        destino = arquivo.with_name(f"{arquivo.name}.juntado-{numero}")
        numero += 1
    arquivo.rename(destino)
    return destino


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

    existia = resumo.exists()
    try:
        conversas, ignorados, versao = _ler_resumo(resumo)
    except ResumoIlegivel as erro:
        print(
            f"tempo: o resumo {resumo} não se lê ({erro}). Ele guarda as horas das conversas já "
            "apagadas e não foi sobrescrito: corrija-o ou mova-o, e rode de novo",
            file=sys.stderr,
        )
        return 1
    eventos, ignorados = _eventos(configuracao, raiz, ignorados)
    for sessao, da_conversa in eventos.items():
        # O resumo da 2.8 guarda as horas que ela contava a mais (o tempo fora da raiz, o de um
        # repositório aninhado): a conversa que ainda existe é recalculada, sem juntar com elas.
        guardadas = conversas.get(sessao, []) if versao == VERSAO_DO_RESUMO else []
        juntos = _juntar(guardadas, _intervalos(da_conversa))
        # A conversa sem hora da raiz (só passou por fora dela) não fica no resumo.
        if juntos:
            conversas[sessao] = juntos
        else:
            conversas.pop(sessao, None)
    # O resumo de outro caminho de mesmo nome: se a raiz dele não tem mais o .git, o repositório
    # mudou de pasta, e as horas guardadas lá vêm para cá; se tem, é outra cópia, mesmo que o git
    # a recuse (de outro dono); se não se confere, nada vem, e o aviso sai em toda execução.
    juntados, avisos_de_pasta = [], []
    for outro, antiga in _outros_resumos(pasta, raiz):
        tem_git = _tem_git(Path(antiga))
        if tem_git is None:
            avisos_de_pasta.append(
                f"aviso: não deu para conferir se {antiga} ainda é um repositório (sem permissão, "
                f"por exemplo), e as horas guardadas no resumo de lá ({outro}) não vieram para este"
            )
            continue
        if tem_git:
            if not existia:
                avisos_de_pasta.append(
                    f"aviso: não há resumo deste caminho, mas há o de {antiga} ({outro}); se o "
                    "repositório mudou de pasta, as horas guardadas antes estão nele"
                )
            continue
        try:
            guardadas, _, _ = _ler_resumo(outro)
        except ResumoIlegivel as erro:
            avisos_de_pasta.append(
                f"aviso: {antiga} não é mais um repositório, mas o resumo de lá ({outro}) não se "
                f"lê ({erro}), e as horas guardadas nele não vieram para este: corrija-o ou "
                "mova-o, e rode de novo"
            )
            continue
        for sessao, intervalos in guardadas.items():
            conversas[sessao] = _juntar(conversas.get(sessao, []), intervalos)
        juntados.append((outro, antiga))
    commits, de_outros_emails = _commits(raiz)
    dias = _apurar(conversas, commits)

    pasta.mkdir(parents=True, exist_ok=True)
    conteudo = {
        "versao": VERSAO_DO_RESUMO,
        "raiz": str(raiz),
        "conversas": conversas,
        "ignorados": ignorados,
    }
    _gravar(resumo, json.dumps(conteudo, ensure_ascii=False, separators=(",", ":")) + "\n")
    _gravar(pagina, _pagina(raiz.name, dias))
    # Só depois de gravado o resumo com as horas dele: se a gravação falha, a próxima execução
    # junta de novo, e o repetido conta uma vez.
    for outro, antiga in juntados:
        with contextlib.suppress(OSError):
            _renomear_juntado(outro.with_suffix(".html"))
        try:
            destino = _renomear_juntado(outro)
        except OSError:
            destino = outro
        avisos_de_pasta.append(
            f"aviso: as horas guardadas de {antiga}, que não é mais um repositório, vieram para "
            f"este resumo; o resumo de lá ficou em {destino}"
        )

    if dias:
        horas = round(sum(d["total"] for d in dias) / 60)
        quantos = f"{len(dias)} dia" + ("s" if len(dias) != 1 else "")
        print(f"{_data(dias[0]['d'])} a {_data(dias[-1]['d'])}: {quantos}, {horas} h")
    else:
        print("nenhuma hora apurada: o repositório não tem conversas guardadas nem commits")
    print(f"página: {pagina}")
    avisos = (
        *avisos_de_pasta,
        _aviso_dos_emails(de_outros_emails, _lista(raiz, "trilha.outro")),
        _aviso_da_guarda(configuracao),
    )
    for aviso in avisos:
        if aviso:
            print(aviso, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
