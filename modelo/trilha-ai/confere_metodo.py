"""Confere os documentos do método de um repositório que segue o kit (no trilha-ai/verifica.sh).

Uso: python3 -I trilha-ai/confere_metodo.py [--sem-plugin] [--vizinho <nome>]...

Confere, na raiz do repositório:
- a decomposição tem os títulos do esqueleto da skill (`## 1.`, `## 2.`, `## Ciclo`), toda change
  da seção 1 na tabela "Ciclo", e a retirada aparece como retirada;
- as evidências do TDD não têm número de linha e citam arquivos que existem;
- o ANDAMENTO.md não descreve trabalho de outro repositório ("../" e cada --vizinho, pelo nome
  inteiro: não o que é parte de outro nome nem o seguido de barra, como a pasta trilha-ai/);
- as instalações do plugin `sdd` que podem valer no projeto, pela lista do Claude Code lida na
  pasta dele: a do kit, ligada, na versão do trilha-ai/CLAUDE-comum.md e, se o .claude/settings.json
  a declara, instalada no projeto; só aviso, nunca falha, e
  nada sem o Claude Code (o CI), sem a resposta dele no prazo ou com --sem-plugin, que a trava do
  commit usa para não esperar a cada commit;
- o OpenSpec da máquina: o que o `openspec update` mudaria nos arquivos do projeto, pelo dry-run
  dele, sem a rede, e a versão instalada diante da fixada no CI do projeto; só aviso, e nada sem
  o openspec, sem a configuração global dele (o CI), sem resposta no prazo ou com --sem-plugin,
  que pula tudo o que depende da máquina.

Roda no check.sh (e, por ele, no CI) e na trava do commit (trilha-ai/hooks/pre-commit): documento do
método fora do formato barra o commit e o merge; o que depende da máquina (o plugin e o OpenSpec)
só avisa.
Sem a pasta `sdd/`, avisa que ela falta; sem a decomposição ou o TDD (o repositório que ainda não
os escreveu), a conferência deles é pulada com aviso. Só python3, sem dependências. Sai com 1 e
imprime "FALHA: ..." por problema; "ok" se nada falhar.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SDD = RAIZ / "sdd"
ANDAMENTO = RAIZ / "ANDAMENTO.md"
PLUGIN_SDD = "sdd@trilha-ai"
# Dois comandos, não ligados por &&: o install roda mesmo se o marketplace já estiver registrado.
# O plugin vale por projeto (o settings.json dele o declara); o kit.py cita o mesmo comando.
INSTALAR = (
    "`claude plugin marketplace add paulosrl/trilha-ai` (se ainda não estiver) e "
    f"`claude plugin install {PLUGIN_SDD} --scope project`"
)
# Os escopos de uma instalação que vale numa pasta só, a que a lista traz em projectPath.
ESCOPOS_DO_PROJETO = ("local", "project")
# Onde a pasta liga ou desliga o plugin, da configuração que prevalece à que cede; sem nenhuma
# delas, vale a do usuário.
CONFIGURACOES = (("local", ".claude/settings.local.json"), ("project", ".claude/settings.json"))
# Quanto esperar pela lista de plugins do Claude Code; sem resposta nele, segue sem aviso.
PRAZO_DO_CLAUDE = 10
# O OpenSpec: quanto esperar por ele (o dry-run do update leva menos de um segundo) e o ambiente
# sem a rede, com a consulta da versão nova e a telemetria desligadas.
PRAZO_DO_OPENSPEC = 60
SEM_REDE = {"OPENSPEC_NO_UPDATE_CHECK": "1", "OPENSPEC_TELEMETRY": "0", "DO_NOT_TRACK": "1"}
# Os arquivos que o OpenSpec gera para as ferramentas: as skills, os comandos e a marca do Codex.
GERADO = re.compile(r"(^|/)(openspec-[^/]+/SKILL\.md|opsx[^/]*(/.*)?|\.openspec-target)$")
# A versão fixada no CI, só quando é um número (o "latest" não se compara).
PIN_DO_OPENSPEC = re.compile(r"@fission-ai/openspec@(\d+\.\d+\.\d+[^\s\"']*)")
# Quantos nomes de cada grupo o aviso do dry-run mostra; o resto vira contagem.
MOSTRADOS = 5
# As ações do dry-run do update, no verbo do aviso.
VERBOS = {"delete": "apagaria", "add": "criaria", "update": "trocaria"}
NUMERO = re.compile(r"\d{2,3}")
# Os títulos da decomposição, como o esqueleto da skill sdd:briefing os traz.
TITULOS = ("## 1.", "## 2.", "## Ciclo")
TITULO = re.compile(r"#{1,6} ")


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


def _secoes(texto: str) -> dict[str, str]:
    """O texto de cada seção da decomposição, pelo começo do título, até o título seguinte, de
    qualquer nível; o que está em bloco de código (um exemplo citado) não conta."""
    secoes: dict[str, str] = {}
    atual, citando = None, False
    for linha in texto.splitlines():
        if linha.lstrip().startswith("```"):
            citando = not citando
        elif citando:
            continue
        elif TITULO.match(linha):
            atual = next((t for t in TITULOS if linha.startswith(t)), None)
            if atual is not None:
                secoes.setdefault(atual, "")
        elif atual is not None:
            secoes[atual] += f"{linha}\n"
    return secoes


def conferir_decomposicao(texto: str) -> list[str]:
    secoes = _secoes(texto)
    faltam = [f"`{titulo}`" for titulo in TITULOS if titulo not in secoes]
    if faltam:
        titulos = "os títulos" if len(faltam) > 1 else "o título"
        falha = (
            f"decomposição sem {titulos} {', '.join(faltam)} no começo da linha, como no "
            "esqueleto da skill `sdd:briefing`"
        )
        return [falha]
    linhas_1 = _linhas_de_tabela(secoes["## 1."])
    linhas_ciclo = _linhas_de_tabela(secoes["## Ciclo"])
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
    """O "../" em qualquer lugar e cada vizinho pelo nome inteiro e solto: não o que é parte de
    outro nome (hooks-pela-trilha-ai, outros) nem o seguido de barra, que é um caminho do próprio
    projeto (a pasta trilha-ai/ do método)."""
    citados = ["../"] if "../" in texto else []
    for nome in vizinhos:
        if re.search(rf"(?<![\w.-]){re.escape(nome)}(?![\w/-])", texto):
            citados.append(nome)
    return [f"ANDAMENTO.md cita outro repositório: {nome}" for nome in citados]


def _instalacoes_do_sdd() -> list[dict] | None:
    """As instalações do plugin sdd que podem valer no projeto, pela lista do Claude Code lida na
    pasta dele (o "ligado" segue o settings.json da pasta); None se ela não responder."""
    try:
        saida = subprocess.run(
            ["claude", "plugin", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=PRAZO_DO_CLAUDE,
            check=False,
            cwd=RAIZ,
        )
        lista = json.loads(saida.stdout) if saida.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None
    if not isinstance(lista, list):
        return None
    sdd = [p for p in lista if isinstance(p, dict) and str(p.get("id", "")).startswith("sdd@")]
    return [plugin for plugin in sdd if _pode_valer(plugin)]


def _pode_valer(plugin: dict) -> bool:
    """A instalação da máquina inteira (sem pasta) ou a deste projeto. A de outra pasta aparece na
    lista, até como ligada, mas não vale aqui. Com a do usuário e a do projeto, não se sabe qual a
    sessão carrega (a do usuário, quando instalada antes): as duas são conferidas."""
    pasta = plugin.get("projectPath")
    if not pasta:
        return True
    deste_projeto = Path(str(pasta)).resolve() == RAIZ.resolve()
    return deste_projeto and plugin.get("scope") in ESCOPOS_DO_PROJETO


def _versao_do_comum() -> str:
    comum = RAIZ / "trilha-ai" / "CLAUDE-comum.md"
    texto = comum.read_text(encoding="utf-8") if comum.is_file() else ""
    achado = re.search(r"^Versão (\d+\.\d+),", texto, re.MULTILINE)
    return achado.group(1) if achado else ""


def _declaracao() -> tuple[str, object] | None:
    """O escopo e o valor da declaração do plugin que vale nesta pasta, a da configuração que
    prevalece; None sem nenhuma. A lista não serve para isso: o "ligado" da instalação de projeto
    não segue a pasta, e o projectEnabled não lê o settings.local.json."""
    for escopo, nome in CONFIGURACOES:
        try:
            dados = json.loads((RAIZ / nome).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        plugins = dados.get("enabledPlugins") if isinstance(dados, dict) else None
        if isinstance(plugins, dict) and PLUGIN_SDD in plugins:
            return escopo, plugins[PLUGIN_SDD]
    return None


def _avisos_da_declaracao(instalacoes: list[dict]) -> list[str]:
    """O plugin desligado, com o escopo que o desliga; o declarado no projeto e instalado só para
    a máquina inteira, que cada máquina instala no projeto (o settings.json não instala)."""
    do_kit = [plugin for plugin in instalacoes if plugin.get("id") == PLUGIN_SDD]
    declaracao = _declaracao()
    if declaracao is None:
        desligado = any(plugin.get("enabled") is False for plugin in do_kit)
        escopo = "user"
    else:
        escopo, valor = declaracao
        desligado = valor is False
    if desligado:
        ligar = f"`claude plugin enable {PLUGIN_SDD} --scope {escopo}`"
        return [f"plugin {PLUGIN_SDD} desligado no escopo {escopo}: rode {ligar}"]
    no_projeto = any(plugin.get("scope") in ESCOPOS_DO_PROJETO for plugin in do_kit)
    if declaracao is not None and do_kit and not no_projeto:
        instalar = f"`claude plugin install {PLUGIN_SDD} --scope project`"
        return [f"plugin {PLUGIN_SDD} declarado no projeto e só na máquina: rode {instalar}"]
    return []


def avisar_plugin() -> list[str]:
    instalacoes = _instalacoes_do_sdd()
    if instalacoes is None:
        return []
    if not instalacoes:
        return [f"plugin sdd não instalado: rode {INSTALAR}"]
    avisos, versao = _avisos_da_declaracao(instalacoes), _versao_do_comum()
    for plugin in instalacoes:
        escopo = plugin.get("scope")
        opcao = f" --scope {escopo}" if escopo else ""
        if plugin.get("id") != PLUGIN_SDD:
            avisos.append(
                f"plugin sdd de fora do kit ({plugin.get('id')}): rode "
                f"`claude plugin uninstall {plugin.get('id')}{opcao}` e {INSTALAR}"
            )
            continue
        if versao and plugin.get("version") != f"{versao}.0":
            qual = f" (instalação {escopo})" if escopo else ""
            avisos.append(
                f"plugin sdd na {plugin.get('version')}{qual} e o CLAUDE-comum.md na {versao}: "
                f"atualize o que estiver atrás (`claude plugin update {PLUGIN_SDD}{opcao}` ou o "
                "kit.py atualizar)"
            )
    return avisos


def _saida(comando: list[str]) -> str | None:
    """A saída de um comando na raiz do projeto, sem a rede; None se ele faltar, falhar ou não
    responder no prazo. O nome de arquivo fora do UTF-8 chega como o sistema o guarda."""
    try:
        saida = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            errors="surrogateescape",
            timeout=PRAZO_DO_OPENSPEC,
            check=False,
            cwd=RAIZ,
            env={**os.environ, **SEM_REDE},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return saida.stdout if saida.returncode == 0 else None


def _aviso_da_versao() -> list[str]:
    """A versão do openspec da máquina diante da que o CI do projeto instala."""
    ci = RAIZ / ".github" / "workflows" / "verificacao.yml"
    texto = ci.read_text(encoding="utf-8", errors="replace") if ci.is_file() else ""
    pin = PIN_DO_OPENSPEC.search(texto)
    resposta = _saida(["openspec", "--version"]) if pin else None
    instalada = re.search(r"\d+\.\d+\.\d+\S*", resposta or "")
    if pin is None or instalada is None or instalada.group(0) == pin.group(1):
        return []
    aviso = (
        f"o OpenSpec da máquina está na {instalada.group(0)} e o CI do projeto instala a "
        f"{pin.group(1)}: rode `npm install -g @fission-ai/openspec@{pin.group(1)}`"
    )
    return [aviso]


def _nomes(nomes: list[str]) -> str:
    resto = len(nomes) - MOSTRADOS
    return ", ".join(nomes[:MOSTRADOS]) + (f" e mais {resto}" if resto > 0 else "")


def _do_projeto(nome: str) -> bool:
    """O caminho que o dry-run lista fica dentro da raiz: nem no HOME, que ele mostra como `~/...`
    (a configuração global, no lugar padrão), nem absoluto, nem fora dela por `..`."""
    return not nome.startswith("~") and Path(os.path.normpath(RAIZ / nome)).is_relative_to(RAIZ)


def _aviso_do_update() -> list[str]:
    """O que o `openspec update` mudaria nos arquivos do projeto, pelo `--dry-run --json` dele, que
    não escreve nada; só com a configuração global e com arquivos gerados no índice do git. O que
    ele lista fora do projeto (a configuração global) fica fora do aviso."""
    configuracao = _saida(["openspec", "config", "path"])
    if configuracao is None or not Path(configuracao.strip()).is_file():
        return []
    lista = _saida(["git", "ls-files", "-z"])
    if not any(GERADO.search(nome) for nome in (lista or "").split("\0")):
        return []
    try:
        plano = json.loads(_saida(["openspec", "update", "--dry-run", "--json"]) or "")
    except (ValueError, RecursionError):  # a saída aninhada fundo demais também não é a dele
        return []
    mudancas = plano.get("changes") if isinstance(plano, dict) else None
    if not isinstance(mudancas, list) or plano.get("failures"):
        return []
    grupos: dict[str, list[str]] = {verbo: [] for verbo in VERBOS.values()}
    for mudanca in (item for item in mudancas if isinstance(item, dict)):
        nome, acao = mudanca.get("path"), mudanca.get("action")
        if isinstance(nome, str) and isinstance(acao, str) and acao in VERBOS and _do_projeto(nome):
            grupos[VERBOS[acao]].append(nome)
    partes = [f"{verbo}: {_nomes(sorted(nomes))}" for verbo, nomes in grupos.items() if nomes]
    if not partes:
        return []
    aviso = (
        f"o openspec update mudaria arquivos gerados do OpenSpec ({'; '.join(partes)}): confira o "
        "perfil com `openspec config list` antes de rodá-lo"
    )
    return [aviso]


def avisar_openspec() -> list[str]:
    return _aviso_da_versao() + _aviso_do_update()


def main(argv: list[str]) -> int:
    sem_plugin = "--sem-plugin" in argv
    argv = [opcao for opcao in argv if opcao != "--sem-plugin"]
    if len(argv) % 2 or any(opcao != "--vizinho" for opcao in argv[::2]):
        print(__doc__, file=sys.stderr)
        return 2
    vizinhos = argv[1::2]
    falhas: list[str] = []
    avisos: list[str] = []
    decomposicao, tdd = _unico("decomposicao-*.md"), _unico("tdd-*.md")
    if not SDD.is_dir():
        avisos.append(
            "sem a pasta sdd/: crie-a com `mkdir sdd` e copie para ela o "
            "modelo/sdd/padroes-tecnicos.md do kit, os padrões de partida do TDD; o PRD, o TDD, "
            "a decomposição e os briefings nascem nela"
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
    if not sem_plugin:
        avisos += avisar_plugin() + avisar_openspec()

    for aviso in avisos:
        print(f"aviso: {aviso}", file=sys.stderr)
    for falha in falhas:
        print(f"FALHA: {falha}", file=sys.stderr)
    if not falhas:
        print("ok: decomposição, TDD e ANDAMENTO.md conferidos")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
