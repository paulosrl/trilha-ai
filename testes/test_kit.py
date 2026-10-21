"""O kit é coerente: a versão, o esqueleto, o verificador e o gerador da página (Python 3 puro)."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "modelo"  # o que vai aos projetos
PLUGIN = RAIZ / "plugins" / "sdd"  # o plugin que o kit publica
# A lista dos arquivos do kit vive num lugar só: a ferramenta que cria e atualiza os projetos.
_spec = importlib.util.spec_from_file_location("kit", RAIZ / "ferramentas" / "kit.py")
FERRAMENTA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FERRAMENTA)
# A conferência das regras, pelas tabelas dela (os campos e os marcadores da stack) e pelo teto.
_spec = importlib.util.spec_from_file_location("regras", MODELO / "trilha" / "confere_regras.py")
REGRAS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REGRAS)
DO_KIT = (*FERRAMENTA.SEM_MUDAR, *FERRAMENTA.A_PREENCHER)
ORIGEM = dict(FERRAMENTA.A_PREENCHER)  # destino no projeto → origem no kit
GIT_TESTE = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
             "GIT_COMMITTER_EMAIL": "t@t"}
ESQUELETO_DO_CLAUDE = RAIZ / "CLAUDE.md"  # o deste repositório não é o esqueleto; o esqueleto é copiado abaixo


def _claude_falso(pasta: Path, corpo: str) -> None:
    """Um `claude` de mentira em pasta/, que roda o corpo dado (um script de sh)."""
    falso = pasta / "claude"
    falso.write_text(f"#!/bin/sh\n{corpo}\n", encoding="utf-8")
    falso.chmod(0o755)


_SEM_CLAUDE = tempfile.TemporaryDirectory()
_PATH_ORIGINAL = os.environ["PATH"]
_XDG_ORIGINAL = os.environ.get("XDG_CONFIG_HOME")


def setUpModule() -> None:
    """Toda conferência dos testes vê um `claude` que falha, nunca o da máquina: o aviso do plugin
    depende do que está instalado nela. Os testes do aviso trocam este por outro."""
    _claude_falso(Path(_SEM_CLAUDE.name), "exit 1")
    os.environ["PATH"] = f"{_SEM_CLAUDE.name}:{os.environ['PATH']}"
    # O openspec falso acha a configuração pelo XDG_CONFIG_HOME, como o de verdade; o da máquina
    # (o runner do GitHub o define) não vale nos testes (change 09).
    os.environ.pop("XDG_CONFIG_HOME", None)


def tearDownModule() -> None:
    os.environ["PATH"] = _PATH_ORIGINAL
    if _XDG_ORIGINAL is not None:
        os.environ["XDG_CONFIG_HOME"] = _XDG_ORIGINAL
    _SEM_CLAUDE.cleanup()


def _copia_do_kit(destino: Path) -> None:
    for nome in DO_KIT:
        alvo = destino / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(MODELO / ORIGEM.get(nome, nome), alvo)


def _divergencia_de_versao(kit: str, manifesto: dict) -> str:
    """Vazio se o plugin está na versão do kit (X.Y.0 para "Versão X.Y"); senão, as duas."""
    plugin = manifesto.get("version", "?")
    return "" if plugin == f"{kit}.0" else f"o plugin está na {plugin} e o kit na {kit}"


def _mudou_desde_a_tag(raiz: Path) -> list[str]:
    """Os arquivos de modelo/ e plugins/ que mudaram desde a tag da versão atual do comum; vazio
    se a tag ainda não existe (a versão nova em preparo)."""
    tag = f"v{FERRAMENTA._versao(raiz / 'modelo' / 'trilha' / 'CLAUDE-comum.md')}"
    existe = subprocess.run(["git", "-C", str(raiz), "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
                            capture_output=True, text=True, check=False)
    if existe.returncode != 0:
        return []
    saida = subprocess.run(["git", "-C", str(raiz), "diff", "--name-only", tag, "--", "modelo", "plugins"],
                           capture_output=True, text=True, check=True)
    return saida.stdout.split()


class Kit(unittest.TestCase):
    def test_arquivos_existem(self) -> None:
        faltam = [n for n in DO_KIT if not (MODELO / ORIGEM.get(n, n)).is_file()]
        self.assertEqual(faltam, [])

    def test_modelo_separado_e_inerte_no_kit(self) -> None:
        """O que vai aos projetos fica em modelo/, com nomes que não valem dentro do kit."""
        for inerte in ("CLAUDE.md", ".gitignore", ".claude"):
            self.assertFalse((MODELO / inerte).exists(), inerte)
        # O atalho CLAUDE-comum.md da raiz saiu na 2.0: o --fonte compara a pasta modelo/trilha/.
        self.assertFalse((RAIZ / "CLAUDE-comum.md").exists() or (RAIZ / "CLAUDE-comum.md").is_symlink())

    def test_marketplace_lido_da_raiz_do_kit(self) -> None:
        marketplace = json.loads((RAIZ / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], "trilha-ai")
        self.assertEqual({p["name"]: p["source"] for p in marketplace["plugins"]}, {"sdd": "./plugins/sdd"})
        manifesto = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifesto["name"], "sdd")

    def test_as_tres_skills_no_plugin(self) -> None:
        self.assertEqual(sorted(p.name for p in (PLUGIN / "skills").iterdir()), ["briefing", "prd", "tdd"])
        for skill in ("prd", "tdd", "briefing"):
            cabecalho = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").split("\n---", 1)[0]
            self.assertRegex(cabecalho, rf"(?m)^name: {skill}$")

    def test_skill_tdd_le_os_padroes_do_projeto(self) -> None:
        """F21: os padrões técnicos são do projeto; a skill os lê, não os traz."""
        skill = (PLUGIN / "skills/tdd/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("sdd/padroes-tecnicos.md", skill)
        for padrao in ("pgvector", "`uv`", "pnpm", "Biome", "postgres:16-alpine"):
            self.assertNotIn(padrao, skill)

    def test_modelo_dos_padroes_com_requires_python(self) -> None:
        """F22: com o uv, o Python vai em requires-python, não na sintaxe do Poetry."""
        padroes = (MODELO / "sdd/padroes-tecnicos.md").read_text(encoding="utf-8")
        for padrao in ("pgvector", "`uv`", "pnpm", "Biome", "postgres:16-alpine"):
            self.assertIn(padrao, padroes)
        self.assertIn('requires-python = ">=3.12.3"', padroes)
        self.assertNotRegex(padroes, r'(?<![-\w])python = "')

    def test_plugin_sem_o_repositorio_antigo(self) -> None:
        arquivos = [a for pasta in (RAIZ / ".claude-plugin", RAIZ / "plugins") for a in pasta.rglob("*") if a.is_file()]
        self.assertTrue(arquivos)
        citam = [str(a.relative_to(RAIZ)) for a in arquivos
                 if "pipeline-prd-tdd-openspec" in a.read_text(encoding="utf-8")]
        self.assertEqual(citam, [])

    def test_versao_do_plugin_igual_a_do_kit(self) -> None:
        """Uma versão para o método: o plugin é X.Y.0 da "Versão X.Y" do comum."""
        kit = FERRAMENTA._versao(MODELO / "trilha/CLAUDE-comum.md")
        manifesto = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(_divergencia_de_versao(kit, manifesto), "")

    def test_versao_do_plugin_esquecida_reprova(self) -> None:
        erro = _divergencia_de_versao("1.36", {"version": "1.35.0"})
        self.assertIn("1.35.0", erro)
        self.assertIn("1.36", erro)

    @staticmethod
    def _esqueleto_da_decomposicao() -> str:
        skill = (PLUGIN / "skills/briefing/SKILL.md").read_text(encoding="utf-8")
        esqueleto = next(b for b in skill.split("```markdown\n")[1:] if "## 1. Mapa de changes" in b)
        return esqueleto.split("\n```", 1)[0]

    def _confere_decomposicao(self, texto: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            _copia_do_kit(Path(tmp))
            (Path(tmp) / "sdd").mkdir(exist_ok=True)
            (Path(tmp) / "sdd/decomposicao-x.md").write_text(texto, encoding="utf-8")
            return self._confere_metodo(Path(tmp))

    def test_esqueleto_da_decomposicao_passa_na_conferencia(self) -> None:
        """F02: o formato que a skill briefing ensina é o que a trava do commit lê, com ou sem retirada."""
        esqueleto = self._esqueleto_da_decomposicao()
        retirada = esqueleto.replace("<por que depende da 01> |", "<por que depende da 01>; retirada em 2026-10-16: motivo |")
        retirada = retirada.replace("| 02 | — | — | — |", "| 02 | — | — | retirada em 2026-10-16 |")
        self.assertNotEqual(retirada, esqueleto)
        for texto in (esqueleto, retirada):
            saida = self._confere_decomposicao(texto)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertNotIn("FALHA", saida.stderr)

    def test_decomposicao_com_titulo_so_dentro_do_texto_reprova(self) -> None:
        """F02: o título vale no começo da linha; `### 1.` não é o `## 1.` do esqueleto."""
        texto = self._esqueleto_da_decomposicao().replace("## 1. Mapa de changes", "### 1. Mapa de changes")
        saida = self._confere_decomposicao(texto)
        self.assertEqual(saida.returncode, 1, saida.stderr)
        falha = next(l for l in saida.stderr.splitlines() if l.startswith("FALHA: decomposição"))
        self.assertIn("`## 1.`", falha)
        self.assertNotIn("`## 2.`", falha)
        self.assertIn("sdd:briefing", falha)

    def test_decomposicao_sem_a_secao_2_reprova(self) -> None:
        texto = self._esqueleto_da_decomposicao().replace("## 2. Regras de convivência", "## Regras de convivência")
        saida = self._confere_decomposicao(texto)
        self.assertEqual(saida.returncode, 1, saida.stderr)
        falha = next(l for l in saida.stderr.splitlines() if l.startswith("FALHA: decomposição"))
        self.assertIn("`## 2.`", falha)
        self.assertNotIn("`## 1.`", falha)

    def test_decomposicao_com_subsecao_depois_do_ciclo_passa(self) -> None:
        """A seção termina no título seguinte, de qualquer nível: a tabela de uma subseção não é do Ciclo."""
        texto = self._esqueleto_da_decomposicao() + "\n\n### Notas\n\n| NN | nota |\n|---|---|\n| 03 | outra |\n"
        saida = self._confere_decomposicao(texto)
        self.assertEqual(saida.returncode, 0, saida.stderr)

    def test_decomposicao_com_titulo_citado_em_bloco_de_codigo(self) -> None:
        """O título e a tabela dentro de um bloco de código não contam."""
        citado = "\n\n## Pendências\n\n```markdown\n## 2. Regras\n\n## Ciclo\n\n| NN | b |\n|---|---|\n| 09 | — |\n```\n"
        esqueleto = self._esqueleto_da_decomposicao()
        saida = self._confere_decomposicao(esqueleto + citado)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        sem_a_2 = esqueleto.replace("## 2. Regras de convivência", "## Regras de convivência") + citado
        saida = self._confere_decomposicao(sem_a_2)
        self.assertEqual(saida.returncode, 1, saida.stderr)
        self.assertIn("`## 2.`", saida.stderr)

    def test_decomposicao_sem_dois_titulos_diz_os_titulos(self) -> None:
        texto = self._esqueleto_da_decomposicao().replace("## 1. Mapa", "## Mapa").replace("## 2. Regras", "## Regras")
        saida = self._confere_decomposicao(texto)
        self.assertEqual(saida.returncode, 1, saida.stderr)
        self.assertIn("sem os títulos `## 1.`, `## 2.`", saida.stderr)

    def test_briefing_seguinte_depois_do_merge(self) -> None:
        """F06: a change fecha no merge (comum, passo 7); o briefing da próxima espera por ele."""
        skill = (PLUGIN / "skills/briefing/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("quando a change anterior estiver com o merge feito", skill)
        self.assertIn("Depois do merge da change", skill)

    def test_gate_2_fecha_a_stack(self) -> None:
        """F04: ao fechar o gate 2, o comum nomeia os lugares da stack; a skill tdd remete a ele."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        regra = next(l for l in comum.splitlines() if l.startswith("- Ao fechar o gate 2"))
        for lugar in ("`scripts/check.sh`", "`.github/workflows/verificacao.yml`", "`.github/dependabot.yml`",
                      "`.gitignore`", "`openspec/config.yaml`"):
            self.assertIn(lugar, regra)
            self.assertTrue((MODELO / ORIGEM[lugar.strip("`")]).is_file(), lugar)
        tdd = (PLUGIN / "skills/tdd/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("como o `CLAUDE-comum.md` manda ao fechar o gate 2", tdd)

    def test_mudanca_sem_versao_nova_reprova(self) -> None:
        env = {**os.environ, **GIT_TESTE}
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "modelo/trilha").mkdir(parents=True)
            (raiz / "modelo/trilha/CLAUDE-comum.md").write_text("Versão 1.0, de 2026-10-15.\n", encoding="utf-8")
            (raiz / "plugins").mkdir()
            (raiz / "plugins/skill.md").write_text("antes\n", encoding="utf-8")
            for comando in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "kit"]):
                subprocess.run(["git", "-C", tmp, *comando], check=True, env=env)
            (raiz / "plugins/skill.md").write_text("depois\n", encoding="utf-8")
            self.assertEqual(_mudou_desde_a_tag(raiz), [])  # sem a tag: a versão nova em preparo
            subprocess.run(["git", "-C", tmp, "tag", "v1.0", "HEAD"], check=True, env=env)
            self.assertEqual(_mudou_desde_a_tag(raiz), ["plugins/skill.md"])

    def test_kit_sem_mudanca_depois_da_tag(self) -> None:
        """Mudou modelo/ ou plugins/ depois da tag da versão: suba a versão (CLAUDE.md do kit)."""
        self.assertEqual(_mudou_desde_a_tag(RAIZ), [])

    def test_versao_no_comum(self) -> None:
        for arquivo in ("trilha/CLAUDE-comum.md",):
            texto = (MODELO / arquivo).read_text(encoding="utf-8")
            self.assertIsNotNone(re.search(r"^Versão \d+\.\d+, de \d{4}-\d\d-\d\d\.", texto, re.M), arquivo)

    def test_comum_cabe_em_metade_do_teto(self) -> None:
        """F09: o comum fica em 16 KB, metade do teto que a conferência cobra; a outra é do projeto."""
        tamanho = len((MODELO / "trilha/CLAUDE-comum.md").read_bytes())
        self.assertLessEqual(tamanho, REGRAS.LIMITE_DE_BYTES // 2)

    def test_comum_nao_cita_curso(self) -> None:
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("curso", comum.lower().replace("em curso", ""))
        # O config.yaml vai a todo projeto: também não cita um.
        self.assertNotIn("Consulta Pública", (MODELO / "openspec/config.yaml").read_text(encoding="utf-8"))

    def test_clear_com_o_comando_da_proxima_sessao(self) -> None:
        """v1.34: quem sugere o /clear mostra o comando exato a dar ao voltar, pronto para copiar."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("e mostre, num bloco de código, o comando exato a dar na próxima sessão", comum)

    def test_comum_sem_repetir_o_openspec_nem_a_si_mesmo(self) -> None:
        """v1.32: a instrução do propose já manda ler o projeto e os specs; o pkill -f num lugar só."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Antes de propor, rode `openspec list`", comum)
        self.assertEqual(comum.count("`pkill -f`"), 1)
        # A trava confere o --merge e a verificação verde, não o passo em que se está.
        self.assertIn("o merge sem `--merge` ou sem a verificação verde", comum)
        self.assertIn("a cópia nova do kit (a pasta `trilha/` e o que o `kit.py atualizar` escreve) dispensam change", comum)

    def test_comum_fecha_a_porta_do_briefing_curto(self) -> None:
        """v1.8: sem decomposição, o passo do ciclo fica no ANDAMENTO.md; com PRD e TDD, a decomposição vem antes."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("o passo do ciclo de cada change fica no `ANDAMENTO.md`", comum)
        self.assertIn("Com o PRD e o TDD aprovados, a decomposição vem antes de qualquer change.", comum)

    def test_comum_preve_o_registro_de_processo_opcional(self) -> None:
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("registro de processo", comum)
        self.assertIn("é opcional; quem o mantém declara no `CLAUDE.md`", comum)

    def test_comum_cita_o_hook_de_envio_proprio(self) -> None:
        """Change 08: o hook de envio do projeto fica em .githooks/pre-push e roda pela trilha/hooks."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("`.githooks/pre-push`", comum)
        self.assertIn("`trilha/hooks/pre-push`", comum)

    def test_comum_cita_a_skill_briefing(self) -> None:
        """A skill do plugin chama-se sdd:briefing, para não colidir com a openspec-propose nativa do OpenSpec."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("`sdd:briefing`", comum)
        self.assertNotIn("openspec-propose", comum)

    def test_comum_poe_a_auditoria_na_revisao_do_openspec(self) -> None:
        """v1.9: a auditoria do gate 3 é a revisão que o OpenSpec pede ao fim do propose, não um passo à parte."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("a revisão dos artefatos, que o OpenSpec pede ao fim do propose, antes do apply, feita como a auditoria do gate 3", comum)

    def test_metodo_nao_forca_o_apply(self) -> None:
        """v1.10: o apply segue o fluxo do OpenSpec; nem commit por tarefa nem parada forçada."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("4. `/opsx:apply`, no fluxo do OpenSpec;", comum)
        self.assertIn("Durante o apply, o ponto de retomada é o `tasks.md`", comum)
        # O apply pode ter instrução, mas nunca a que força parada ou commit (a decisão da v1.10).
        apply = config.split("  apply:", 1)[1].split("  archive:", 1)[0] if "  apply:" in config else ""
        for proibido in ("commit", "pare", "parada"):
            self.assertNotIn(proibido, apply.lower())

    def test_specs_com_o_nome_do_openspec(self) -> None:
        """v1.11: só as changes levam número e data; os specs seguem o nome que o OpenSpec dá."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Os specs seguem o nome que o OpenSpec dá", comum)

    def test_auditoria_nao_e_unidade_de_trabalho(self) -> None:
        """v1.12: até a escolha do usuário, a auditoria não muda o ANDAMENTO.md nem o registro de processo."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Até a escolha, a auditoria não é unidade de trabalho", comum)

    def test_correcao_de_texto_nao_sobe_versao(self) -> None:
        """v1.14: só a mudança de sentido sobe a versão do PRD, do TDD ou da decomposição."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("não sobe a versão dele nem a linha \"de origem\" de quem o cita", comum)
        self.assertIn("Só a mudança de sentido é versão nova, aprovada pelo usuário", comum)

    def test_prd_e_spec_em_desacordo(self) -> None:
        """v1.15: o PRD aprovado manda sobre o spec; se o certo for o spec, o PRD ganha versão nova."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("PRD e spec em desacordo: vale o PRD aprovado", comum)
        self.assertIn("se o certo for o spec, o PRD ganha versão nova", comum)

    def test_regras_gerais_vindas_dos_repositorios(self) -> None:
        """v1.16: o "sim" isolado, o que ler antes do propose e a mutação desfeita saem dos CLAUDE.md."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Um \"sim\" isolado responde só à pergunta principal da mensagem", comum)
        self.assertIn("rode `openspec list`", comum)
        self.assertIn("(`progress.total`)", comum)
        self.assertIn("desfaça-a por edição inversa, nunca com `git checkout`", comum)

    def test_remoto_privado_no_github(self) -> None:
        """v1.20: todo repositório do método tem um remoto privado no GitHub, criado na etapa 0."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertIn("desde a etapa 0, um remoto privado no GitHub (`origin`)", comum)
        self.assertIn("`gh repo create <nome> --private --source . --push`", comum)
        self.assertIn("`gh auth login`", readme)
        self.assertIn("`gh repo create <nome> --private --source . --push`", readme)

    def test_branch_e_pull_request_por_change(self) -> None:
        """v1.21: cada change numa branch; PR em rascunho ao fim do propose; um "sim" para os envios, outro para o merge."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("numa branch `change/NN-nome` aberta a partir da main atualizada", comum)
        self.assertIn("pull request em rascunho (`gh pr create --draft`)", comum)
        self.assertIn("um só \"sim\" para todos os envios da branch até o merge", comum)
        self.assertIn("`gh pr merge --merge --delete-branch` (merge commit, nunca squash", comum)
        self.assertIn("com um \"sim\" só para ele", comum)

    def test_archive_dentro_do_pull_request(self) -> None:
        """v1.22: o archive e os passos seguintes na branch, antes do merge; depois, o PR sai do rascunho."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("o PR sai do rascunho (`gh pr ready`): código, specs e página chegam juntos à main", comum)
        self.assertIn("7. o merge", comum)

    def test_ci_no_kit_e_merge_so_com_ele_verde(self) -> None:
        """v1.23: o GitHub roda o check.sh e o openspec validate; o merge só é pedido com tudo verde."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        ci = (MODELO / ".github/workflows/verificacao.yml").read_text(encoding="utf-8")
        self.assertIn("o merge, só com a verificação do GitHub verde no PR (`gh pr checks`)", comum)
        self.assertIn("run: bash scripts/check.sh", ci)
        self.assertIn("bash scripts/check.sh", ci)  # que roda o trilha/verifica.sh, com o openspec validate
        self.assertIn("openspec validate --all --no-interactive", (MODELO / "trilha/verifica.sh").read_text())
        self.assertNotIn("--strict", ci)  # o estrito reprova os avisos que o check.sh aceita
        self.assertRegex(ci, r"@fission-ai/openspec@\d+\.\d+\.\d+")
        # Fora de .github/workflows/ no kit: aqui o check.sh reprovaria, porque o kit não segue o método.
        self.assertFalse((RAIZ / ".github/workflows/verificacao.yml").exists())
        # O CI do próprio kit roda estes testes.
        kit = (RAIZ / ".github/workflows/testes.yml").read_text(encoding="utf-8")
        self.assertIn("run: python3 -m unittest discover -s testes", kit)
        # E valida os specs do kit, com o OpenSpec na versão que os projetos usam (N06).
        openspec = re.search(r"@fission-ai/openspec@[\d.]+", ci).group(0)
        self.assertIn(f"npx --yes {openspec} validate --all --no-interactive", kit)

    def test_regras_de_verificacao_vindas_do_heimdall(self) -> None:
        """Cada cenário com teste nomeado e evidência; tarefa marcada só com o teste passando."""
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn('Terminar com a seção "Verificação"', config)
        self.assertIn("tem uma tarefa que nomeia o teste que o comprova", config)
        self.assertIn("nunca o valor literal que o código já usa", config)
        self.assertIn("Marcar a tarefa de um cenário só quando o teste que o comprova passar", config)

    def test_revisao_de_texto_da_auditoria(self) -> None:
        """Item 8 da auditoria: a precedência inteira no comum, o Purpose só do spec novo, a revisão
        de código numa sessão nova e o design dispensado no archive."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        ordem = ["as travas do kit", "a escolha do usuário", "o OpenSpec", '"Exceções ao comum"',
                 "este arquivo", "o `openspec/config.yaml`", "as skills `sdd:*`"]
        linha = next(l for l in comum.splitlines() if l.startswith("Regras comuns"))
        posicoes = [linha.find(trecho, linha.find("Em conflito")) for trecho in ordem]
        self.assertNotIn(-1, posicoes, linha)
        self.assertEqual(posicoes, sorted(posicoes))
        self.assertIn("(o Purpose de um spec novo)", comum)
        self.assertIn("numa sessão nova, depois do `/clear`", comum)
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("O design.md que o propose dispensou não é passo pulado", config)

    def test_skills_curtas_subordinadas_ao_kit_e_com_historico(self) -> None:
        """As descrições entram em toda sessão com o plugin ligado: curtas. Cada skill cede ao kit,
        e os modelos de PRD e de TDD têm onde registrar a versão nova."""
        for skill in ("prd", "tdd", "briefing"):
            texto = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            descricao = texto.split("\n---", 1)[0].split("description: >\n", 1)[1]
            self.assertLess(len(descricao), 500, skill)
            self.assertIn("kit Trilha AI (`CLAUDE-comum.md`", texto, skill)
        for skill in ("prd", "tdd"):
            modelo = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            modelo = modelo.split("## Estrutura obrigatória", 1)[1]
            self.assertRegex(modelo, r"(?m)^## \d+\. Histórico de versões$", skill)

    def test_tabela_do_readme_e_a_lista_do_kit(self) -> None:
        """F11: a tabela do README explica cada arquivo de modelo/; a lista vive no kit.py."""
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        tabela = {re.match(r"\s*\| `([^`]+)`", l).group(1) for l in readme.splitlines()
                  if re.match(r"\s*\| `[^`]+` \|", l) and "modelo/" not in l.split("|")[1]}
        self.assertEqual(tabela, {"trilha/", *FERRAMENTA.A_PREENCHER.values()})

    def test_readme_e_mapa_sem_curso_nem_projeto(self) -> None:
        """F03 e F14: o kit se instala sozinho, e o mapa explica o método sem histórico."""
        for nome in ("README.md", "mapa-da-trilha.html"):
            texto = (RAIZ / nome).read_text(encoding="utf-8")
            for proibido in ("consulta-publica", "heimdall", r"\bcurso\b", "guia do aluno",
                             "O que mudou desde a versão 1"):
                self.assertNotRegex(texto, proibido, nome)
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertIn("curl -fsSL https://claude.ai/install.sh | bash", readme)
        verificacao = (MODELO / ".github/workflows/verificacao.yml").read_text(encoding="utf-8")
        openspec = re.search(r"@fission-ai/openspec@[\d.]+", verificacao).group(0)
        self.assertIn(f"npm install -g {openspec}", readme)

    def test_regras_cabem_no_projeto_sem_prd(self) -> None:
        """O comum admite a correção vinda de um spec, sem PRD; as regras que pedem RF dizem o que vale."""
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        regras = config.split("\nrules:\n", 1)[1].split("\noperations:\n", 1)[0]
        for artefato in ("proposal", "specs", "tasks"):
            bloco = re.split(r"\n  (?=\w)", regras.split(f"  {artefato}:\n", 1)[1], maxsplit=1)[0]
            self.assertIn("no projeto ainda sem prd", bloco.lower(), artefato)

    def test_apply_registra_a_verificacao(self) -> None:
        """A regra do design só é lida no propose; quem preenche a Verificação é o apply, com ou sem design.md."""
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        apply = config.split("  apply:", 1)[1].split("  archive:", 1)[0]
        self.assertIn('na seção "Verificação" do design.md', apply)
        self.assertIn("no notas.md da pasta da change quando não houver design.md", apply)
        self.assertIn("nenhum cenário fica comprovado só pela execução manual", apply)

    def test_confere_metodo_se_declara_trava(self) -> None:
        """Desde a 1.27 ele roda na trava do commit e no CI; o texto dele diz isso."""
        texto = (MODELO / "trilha" / "confere_metodo.py").read_text(encoding="utf-8")
        self.assertIn("na trava do commit (trilha/hooks/pre-commit)", texto)

    def test_ci_com_acoes_fixadas_e_busca_de_segredos(self) -> None:
        """v1.29: ações pelo commit, gitleaks conferido pela soma, Dependabot e a regra dos segredos."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        for arquivo in (MODELO / ".github/workflows/verificacao.yml", RAIZ / ".github/workflows/testes.yml"):
            texto = arquivo.read_text(encoding="utf-8")
            # Também os exemplos comentados: quem os descomenta herda a fixação.
            usos = re.findall(r"^\s+(?:#\s+)?- uses: (\S+)", texto, re.M)
            self.assertTrue(usos, arquivo)
            for uso in usos:
                self.assertRegex(uso, r"@[0-9a-f]{40}$", f"{arquivo}: {uso} sem o commit fixado")
        ci = (MODELO / ".github/workflows/verificacao.yml").read_text(encoding="utf-8")
        self.assertIn("sha256sum -c -", ci)
        self.assertIn("gitleaks\" detect --source . --no-banner --redact", ci)
        self.assertIn("fetch-depth: 0", ci)
        self.assertIn("branches: [main, master]", ci)  # o hubia e o heimdall usam master
        for arquivo in (MODELO / ".github/dependabot.yml", RAIZ / ".github/dependabot.yml"):
            self.assertIn("package-ecosystem: github-actions", arquivo.read_text())
        self.assertIn("o CI os procura no histórico (gitleaks)", comum)

    def test_revisao_independente_no_verify(self) -> None:
        """v1.28: no passo 5, o /code-review, desde a 2.3 numa sessão nova, depois do /clear."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        # Com o alvo: sem ele, o /code-review revisa só o que não foi commitado, vazio depois do commit.
        self.assertIn("5. `/opsx:verify` e a revisão independente do código, o `/code-review <número do PR>`",
                      comum)
        self.assertIn("quem escreveu não é o único a revisar", comum)
        self.assertIn("/code-review <número do PR>", (RAIZ / "mapa-da-trilha.html").read_text())

    def test_a_change_fecha_no_merge(self) -> None:
        """v1.25: a change fecha no merge; a retomada olha o PR; um só lugar para a regra dos envios."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertIn("A change fecha aqui, não no archive", comum)
        self.assertIn("numa branch `change/…`, `gh pr view` e `gh pr checks`", comum)
        self.assertIn("change com o merge feito", comum)
        self.assertIn("fora de change (o PRD, o TDD, a decomposição e o trabalho que dispensa change), o commit vai direto à main", comum)
        self.assertEqual(comum.count("envie só com \"sim\""), 1)
        self.assertIn("o envio ao GitHub segue a regra dos envios", comum)
        self.assertIn("`openspec config profile` e marque também o `verify`", readme)

    def test_versao_nova_atualiza_a_origem_sem_versao(self) -> None:
        """v1.16: a versão nova de sentido muda a linha "de origem" de quem cita, sem versão nova dele."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("atualiza a linha \"de origem\" de quem o cita, sem versão nova dele", comum)

    def test_ciclo_guarda_os_marcos_e_o_andamento_o_passo(self) -> None:
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Os marcos de cada change (briefing, auditoria, archive): a tabela \"Ciclo\"", comum)

    def test_auditoria_tem_criterio_de_fechamento(self) -> None:
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Uma auditoria fecha com a verificação do repositório verde e sem contradição", comum)

    def test_hora_do_andamento_lida_do_relogio(self) -> None:
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("a hora, lida do relógio (`date`) e nunca estimada", comum)

    def test_archive_gera_a_pagina(self) -> None:
        """v1.13: os passos depois do archive vivem só no config.yaml; o comum aponta para lá."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        esqueleto = (MODELO / "esqueleto-CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("os passos que o `operations.archive` do `openspec/config.yaml` lista", comum)
        self.assertIn("gerar de novo sdd/documentacao.html", config)
        self.assertNotIn("gerar_pagina_sdd", esqueleto)

    def test_regras_do_metodo_num_lugar_so(self) -> None:
        """v1.13: o teste por cenário fica no config.yaml e os 8 itens da auditoria, na skill."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("pelo checklist da skill `sdd:briefing`", comum)

    def test_andamento_sem_o_envio_e_com_trabalho_fora_de_change(self) -> None:
        """v1.13: o envio ao remoto não vai ao ANDAMENTO.md; a etapa admite trabalho fora de change."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("não guarda o estado do envio ao remoto", comum)
        self.assertIn("ou o trabalho fora de change)", comum)
        self.assertIn("a revisão termina com a auditoria aprovada, em commit e envio", comum)

    def test_gates_aprovados_como_as_skills_pedem(self) -> None:
        """v1.17: PRD e TDD são aprovados bloco a bloco, como as skills pedem; a restrição imposta é exceção."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("aprovado bloco a bloco pelo usuário, como a skill pede (gate 1)", comum)
        self.assertIn("aprovado bloco a bloco pelo usuário, como a skill pede (gate 2)", comum)
        self.assertIn("salvo a restrição que o usuário declara imposta de fora", comum)

    def test_ciclo_sem_repetir_o_config_e_com_o_lugar_do_verify(self) -> None:
        """v1.17: a execução manual fica só no config.yaml; o verify responde no design.md; a sugestão
        de um comando do OpenSpec que pule passo não vale; a aprovação do gate 3 é unidade de trabalho."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("execução manual, em dado descartável, com o usuário olhando", comum)
        self.assertIn("recusada por escrito no `design.md` da change, com o motivo", comum)
        self.assertIn("a tabela \"Ciclo\" da decomposição, atualizada no commit do passo de cada marco", comum)

    def test_auditoria_fechada_no_registro_copia_sem_change_e_o_openspec_comanda(self) -> None:
        """v1.18: a escolha do usuário, com ou sem correção, leva o relatório ao registro; a cópia nova
        dos arquivos do método dispensa change; o OpenSpec comanda, e o método nunca se sobrepõe a ele:
        quando um comando oferece pular um passo, quem escolhe é o usuário."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("A escolha, com ou sem correção, é unidade de trabalho", comum)
        self.assertIn("a cópia nova do kit (a pasta `trilha/`", comum)
        self.assertIn("O OpenSpec comanda: o método nunca se sobrepõe ao fluxo dele", comum)
        self.assertIn("quem escolhe é o usuário, com a recomendação de não pular", comum)

    def test_config_nao_repete_o_comum_nem_o_claude(self) -> None:
        """v1.17: o contexto do config.yaml aponta para o comum e o CLAUDE.md, que o agente já carrega."""
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertNotIn("Não improvise", config)
        self.assertNotIn("Dados a proteger", config)
        self.assertNotIn("Documentos que mandam", config)
        self.assertIn("CLAUDE-comum.md e no CLAUDE.md, que o agente já carrega; este contexto não as repete", config)

    def test_metodo_sem_sobrepor_o_openspec(self) -> None:
        """v1.19: o design.md é do OpenSpec, que o cria só quando cabe (o notas.md o substitui); os specs
        mudam também pela edição que o OpenSpec pede; o gate 3 aceita o caminho que o update indicar;
        as regras do config.yaml sem o MAY e com os títulos do OpenSpec em inglês."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("o OpenSpec o cria só quando cabe", comum)
        self.assertIn("o `notas.md` da pasta da change faz as vezes dele", comum)
        self.assertIn("a edição direta que as instruções dele pedem", comum)
        self.assertIn("ou pelo caminho que ele indicar", comum)
        self.assertIn("um DEVE em português o reprova", config)
        # v1.30: o que o modelo do OpenSpec já pede fica nas instruções dele.
        for repetido in ("não o como", "alternativa rejeitada", "cenário com WHEN/THEN", '"- [ ] N.M'):
            self.assertNotIn(repetido, config)
        # v1.33: a língua fica no context, no bloco que o openspec init --language escreve.
        self.assertNotIn("PT-BR", config[config.find("\nrules:"):])

    def test_lingua_no_context_como_o_openspec_escreve(self) -> None:
        """O bloco de formatLanguageContext (core/init.js do OpenSpec): o init --language o reconhece."""
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        contexto = config[config.find("context: |\n"):config.find("\nrules:")]
        contexto = "\n".join(linha[2:] for linha in contexto.splitlines()[1:])
        self.assertIn(FERRAMENTA.LINGUA, contexto)
        self.assertTrue(FERRAMENTA.LINGUA.startswith(
            "Language: pt-BR\nAll artifacts must be written in pt-BR.\n"
            "Keep OpenSpec structural headings and SHALL/MUST keywords in English.\n"))
        self.assertIn("accents", FERRAMENTA.LINGUA)  # o hubia já perdeu acentos em textos de tela

    def test_cenario_mantido_no_delta_fica_como_esta(self) -> None:
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("todo cenário novo ou alterado cita o CA de origem", config)
        self.assertIn("o que o delta repete sem mudança fica como está", config)

    def test_tarefas_nomeiam_o_requisito_sem_criterio(self) -> None:
        """A regra de tarefas do config.yaml (a única que há) cobre o cenário sem critério."""
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("ou o do requisito quando o cenário não tem critério", config)

    def test_regras_do_config_sao_texto(self) -> None:
        """Item sem aspas com ": " vira chave e valor no YAML, e o OpenSpec ignora em silêncio todas as
        regras daquele artefato ("must be an array of strings"); com " #", o resto vira comentário."""
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        depois_do_contexto = config.split("\nrules:\n", 1)[1]
        soltos = [
            linha.strip()
            for linha in depois_do_contexto.splitlines()
            if re.match(r"\s+- (?![\"'])", linha) and (": " in linha or " #" in linha)
        ]
        self.assertEqual(soltos, [])

    def test_regras_falam_do_usuario(self) -> None:
        for arquivo in ("trilha/CLAUDE-comum.md", "esqueleto-CLAUDE.md"):
            texto = (MODELO / arquivo).read_text(encoding="utf-8")
            self.assertNotRegex(texto, r"\b[àa] pessoa\b", arquivo)

    def test_scripts_cabem_no_lint_de_quem_copia(self) -> None:
        # Os scripts são copiados sem mudança; um projeto Python com o ruff (limite de 100) os reprovaria.
        longas = [
            f"{nome}:{numero}"
            for nome in (*DO_KIT, "ferramentas/kit.py")
            if nome.endswith(".py")
            for numero, linha in enumerate(
                (RAIZ / nome if nome.startswith("ferramentas/") else MODELO / nome)
                .read_text(encoding="utf-8").splitlines(), 1)
            if len(linha) > 100
        ]
        self.assertEqual(longas, [])

    def test_verificador_aprova_um_repositorio_feito_do_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            saida = subprocess.run(
                # A raiz do kit, como o trilha/verifica.sh dos projetos a passa (../trilha-ai).
                [sys.executable, "-I", str(destino / "trilha/confere_regras.py"), tmp, "--fonte", str(RAIZ)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(saida.returncode, 0, saida.stderr)

    def _verifica_com_defeito(self, arquivo: str, de: str, para: str) -> str:
        """Copia o kit, troca um trecho de um arquivo e devolve o stderr do verificador, que deve reprovar."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            alvo = destino / arquivo
            texto = alvo.read_text(encoding="utf-8")
            self.assertIn(de, texto, f"{arquivo} do kit sem o trecho {de!r}")
            alvo.write_text(texto.replace(de, para), encoding="utf-8")
            saida = subprocess.run(
                [sys.executable, "-I", str(destino / "trilha/confere_regras.py"), tmp],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(saida.returncode, 1, saida.stdout + saida.stderr)
            return saida.stderr

    def test_regras_largas_demais_reprovam(self) -> None:
        """F09: abaixo das 200 linhas, mas acima dos 32 KB, a conferência reprova pelos bytes."""
        largas = "- " + "x" * REGRAS.LIMITE_DE_BYTES + "\n"  # sozinha, já passa do teto
        erro = self._verifica_com_defeito("CLAUDE.md", "- Nenhuma.\n", f"- Nenhuma.\n{largas}")
        self.assertIn("bytes", erro)
        self.assertIn("32768", erro)

    def test_regras_com_linhas_demais_reprovam(self) -> None:
        erro = self._verifica_com_defeito("CLAUDE.md", "- Nenhuma.\n", "- Nenhuma.\n" + "- x\n" * 120)
        self.assertIn("linhas", erro)
        self.assertIn("200", erro)

    def test_verificador_reprova_andamento_sem_hora(self) -> None:
        erro = self._verifica_com_defeito("ANDAMENTO.md", "<AAAA-MM-DD HH:MM>", "2026-10-14")
        self.assertIn("sem a hora", erro)

    def test_verificador_reprova_andamento_com_hora_no_futuro(self) -> None:
        erro = self._verifica_com_defeito("ANDAMENTO.md", "<AAAA-MM-DD HH:MM>", "2999-01-01 00:00")
        self.assertIn("no futuro", erro)

    def test_verificador_reprova_claude_sem_o_nome_do_produto(self) -> None:
        erro = self._verifica_com_defeito("CLAUDE.md", "# CLAUDE.md — <nome do produto>", "# CLAUDE.md")
        self.assertIn("título", erro)

    def test_verificador_reprova_documentos_sem_andamento_e_config(self) -> None:
        erro = self._verifica_com_defeito(
            "CLAUDE.md",
            "- Contexto e regras por artefato do OpenSpec: `openspec/config.yaml`. Onde o trabalho parou: `ANDAMENTO.md`.\n",
            "",
        )
        self.assertIn("ANDAMENTO.md", erro)
        self.assertIn("openspec/config.yaml", erro)

    def test_verificador_reprova_passo_numerado_do_comum_repetido(self) -> None:
        passo = next(linha for linha in (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8").splitlines()
                     if linha.startswith("2. "))
        erro = self._verifica_com_defeito("CLAUDE.md", "- Nenhuma.", f"- Nenhuma.\n\n{passo}")
        self.assertIn("repete regra do comum: 2. ", erro)

    def test_verificador_avisa_os_campos_do_modelo_por_preencher(self) -> None:
        """Cada campo < > dos modelos é cobrado como aviso, e só ele: o projeto pode usar < > no texto."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            regras = [sys.executable, "-I", str(destino / "trilha/confere_regras.py"), tmp]
            saida = subprocess.run(regras, capture_output=True, text=True, check=False)
            self.assertEqual(saida.returncode, 0, saida.stderr)  # aviso: a stack só vem na etapa 2
            for nome in ("CLAUDE.md", "ANDAMENTO.md", "openspec/config.yaml"):
                self.assertIn(f"aviso: {nome} ainda tem ", saida.stderr)
                alvo = destino / nome
                texto = alvo.read_text(encoding="utf-8").replace("<AAAA-MM-DD HH:MM>", "2026-10-15 10:00")
                texto = re.sub(r"<[^<>]+>", "x", texto)
                if nome != "ANDAMENTO.md":
                    texto += "\nO texto do projeto pode citar `<origem>`.\n"
                alvo.write_text(texto, encoding="utf-8")
            saida = subprocess.run(regras, capture_output=True, text=True, check=False)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertNotIn("ainda tem", saida.stderr)

    def test_campos_do_verificador_sao_os_dos_modelos(self) -> None:
        """A lista do confere_regras.py cobre cada campo < > dos modelos, e nenhum a mais."""
        for nome, campos in REGRAS.CAMPOS_DO_MODELO.items():
            texto = (MODELO / ORIGEM[nome]).read_text(encoding="utf-8").split("\nrules:")[0]
            if nome.endswith(".yaml"):  # sem os comentários ("o que está entre < e >")
                texto = "\n".join(l for l in texto.splitlines() if not l.lstrip().startswith("#"))
            trechos = [(m.start(), m.end()) for c in campos for m in re.finditer(re.escape(c), texto)]
            for campo in campos:
                self.assertIn(campo, texto, f"{nome}: {campo} não está no modelo")
            for achado in re.finditer(r"<[^<>]+>", texto):
                self.assertTrue(any(a < achado.end() and achado.start() < b for a, b in trechos),
                                f"{nome}: {achado.group()} fora de CAMPOS_DO_MODELO")

    def test_marcadores_da_stack_sao_os_dos_modelos(self) -> None:
        """F04: um marcador por lugar da stack que o comum nomeia no gate 2, e cada um está no modelo."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        gate_2 = next(l for l in comum.splitlines() if l.startswith("- Ao fechar o gate 2"))
        lugares = sorted(c for c in re.findall(r"`([^`]+)`", gate_2.split("Até lá")[0]) if "." in c)
        self.assertEqual(sorted(REGRAS.STACK_DO_MODELO), lugares)
        for nome, marcador in REGRAS.STACK_DO_MODELO.items():
            self.assertIn(marcador, (MODELO / ORIGEM[nome]).read_text(encoding="utf-8"), nome)

    def _avisos_da_stack(self, com_tdd: bool, preenchida: bool = False, com_spec: bool = False
                         ) -> list[str]:
        """As linhas de aviso da stack da conferência das regras num projeto feito do kit; com o
        spec, o projeto que já arquivou a change 01."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            (destino / "sdd").mkdir(exist_ok=True)
            if com_tdd:
                (destino / "sdd/tdd-x.md").write_text("# TDD\n", encoding="utf-8")
            if com_spec:
                (destino / "openspec/specs/x").mkdir(parents=True)
                (destino / "openspec/specs/x/spec.md").write_text("# x Specification\n", encoding="utf-8")
            if preenchida:
                for nome, marcador in REGRAS.STACK_DO_MODELO.items():
                    alvo = destino / nome
                    linhas = alvo.read_text(encoding="utf-8").splitlines(keepends=True)
                    alvo.write_text("".join(l for l in linhas if marcador not in l), encoding="utf-8")
            saida = subprocess.run([sys.executable, "-I", str(destino / "trilha/confere_regras.py"), tmp],
                                   capture_output=True, text=True, check=False)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        return [l for l in saida.stderr.splitlines() if l.startswith("aviso:") and "parte da stack" in l]

    def test_tdd_com_a_stack_do_modelo_avisa(self) -> None:
        """Change 07: no gate 2, só o Dependabot, o .gitignore e o contexto; o check.sh e o CI vêm
        com a change 01."""
        avisos = self._avisos_da_stack(com_tdd=True)
        self.assertEqual(len(avisos), 1, avisos)
        lugares = avisos[0].split(" em ", 1)[1].split(";", 1)[0]
        for lugar in (".github/dependabot.yml", ".gitignore", "openspec/config.yaml"):
            self.assertIn(lugar, lugares)
        for lugar in ("scripts/check.sh", ".github/workflows/verificacao.yml"):
            self.assertNotIn(lugar, lugares)

    def test_change_01_arquivada_avisa_os_cinco(self) -> None:
        avisos = self._avisos_da_stack(com_tdd=True, com_spec=True)
        self.assertEqual(len(avisos), 1, avisos)
        for lugar in ("scripts/check.sh", ".github/workflows/verificacao.yml", ".github/dependabot.yml",
                      ".gitignore", "openspec/config.yaml"):
            self.assertIn(lugar, avisos[0])

    def test_stack_preenchida_nao_avisa(self) -> None:
        self.assertEqual(self._avisos_da_stack(com_tdd=True, preenchida=True), [])

    def test_stack_preenchida_como_o_modelo_pede_nao_avisa(self) -> None:
        """Quem segue à risca o que o modelo pede ao preencher a stack não é mais avisado dela."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            (destino / "sdd").mkdir(exist_ok=True)
            (destino / "sdd/tdd-x.md").write_text("# TDD\n", encoding="utf-8")
            ignorar = destino / ".gitignore"  # fica o bloco do Python; sai o do Node e o pedido
            texto = re.sub(r"# Node\b[^\n]*\n(?:[^\n]+\n)*\n?", "", ignorar.read_text(encoding="utf-8"))
            ignorar.write_text("".join(l for l in texto.splitlines(True) if "este comentário" not in l))
            dependabot = destino / ".github/dependabot.yml"  # os exemplos viram o bloco real
            texto = dependabot.read_text(encoding="utf-8").replace("  #   ", "  ")
            dependabot.write_text("".join(l for l in texto.splitlines(True) if "este comentário" not in l))
            saida = subprocess.run([sys.executable, "-I", str(destino / "trilha/confere_regras.py"), tmp],
                                   capture_output=True, text=True, check=False)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = next(l for l in saida.stderr.splitlines() if "parte da stack" in l)
        self.assertIn("openspec/config.yaml", aviso)  # o contexto segue por preencher
        self.assertNotIn(".gitignore", aviso)
        self.assertNotIn("dependabot.yml", aviso)

    def test_projeto_sem_tdd_nao_avisa_a_stack(self) -> None:
        self.assertEqual(self._avisos_da_stack(com_tdd=False), [])

    def _confere_metodo(self, destino: Path, *args: str, claude: str | None = "exit 1"
                        ) -> subprocess.CompletedProcess[str]:
        """A conferência do método com um `claude` falso que roda o corpo dado; com None, a
        máquina sem o Claude Code (só a pasta do falso no PATH, vazia)."""
        with tempfile.TemporaryDirectory() as falsos:
            if claude is not None:
                _claude_falso(Path(falsos), claude)
            return subprocess.run(
                [sys.executable, "-I", str(destino / "trilha/confere_metodo.py"), *args],
                capture_output=True, text=True, check=False, env={**os.environ, "PATH": falsos},
            )

    def _aviso_do_plugin(self, lista: object, versao_do_comum: str = "1.35",
                         vizinho: bool = False, configuracoes: dict | None = None
                         ) -> subprocess.CompletedProcess[str]:
        """A conferência num projeto feito do kit, com o comum na versão dada e um `claude` falso
        que lista os plugins dados (o "<projeto>" da lista vira a pasta do projeto); com vizinho,
        uma pasta pipeline-prd-tdd-openspec ao lado. As configurações (caminho: conteúdo) trocam
        as do projeto; o conteúdo None apaga o arquivo."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "projeto"
            _copia_do_kit(destino)
            for nome, conteudo in (configuracoes or {}).items():
                if conteudo is None:
                    (destino / nome).unlink()
                else:
                    (destino / nome).write_text(json.dumps(conteudo), encoding="utf-8")
            comum = destino / "trilha/CLAUDE-comum.md"
            comum.write_text(re.sub(r"^Versão [\d.]+,", f"Versão {versao_do_comum},",
                                    comum.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
            if vizinho:
                manifesto = Path(tmp) / "pipeline-prd-tdd-openspec/plugins/sdd/.claude-plugin"
                manifesto.mkdir(parents=True)
                (manifesto / "plugin.json").write_text('{"name": "sdd", "version": "9.9.9"}')
            texto = lista if isinstance(lista, str) else json.dumps(lista)
            texto = texto.replace("<projeto>", str(destino.resolve()))
            return self._confere_metodo(destino, claude=f"printf '%s' '{texto}'")

    def test_plugin_conferido_sem_a_pasta_vizinha(self) -> None:
        lista = [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "project", "enabled": True,
                  "projectPath": "<projeto>"}]
        com, sem = self._aviso_do_plugin(lista, vizinho=True), self._aviso_do_plugin(lista)
        self.assertEqual((com.returncode, com.stderr), (sem.returncode, sem.stderr))
        self.assertNotIn("plugin sdd", com.stderr)

    def test_plugin_do_marketplace_antigo_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "sdd@pipeline-prd-tdd-openspec", "version": "0.3.9"}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("de fora do kit (sdd@pipeline-prd-tdd-openspec)", saida.stderr)
        self.assertIn("claude plugin install sdd@trilha-ai", saida.stderr)

    def test_plugin_com_versao_diferente_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "sdd@trilha-ai", "version": "1.34.0"}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = next(l for l in saida.stderr.splitlines() if "plugin sdd na" in l)
        self.assertIn("1.34.0", aviso)
        self.assertIn("1.35", aviso)

    def test_plugin_com_versao_igual_nao_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "project",
                                        "projectPath": "<projeto>"}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertNotIn("plugin sdd", saida.stderr)

    def test_plugin_ausente_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "outro@lugar", "version": "1.0.0"}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("plugin sdd não instalado", saida.stderr)
        self.assertIn("claude plugin install sdd@trilha-ai --scope project", saida.stderr)

    def test_plugin_de_outro_projeto_avisa_o_install(self) -> None:
        """A instalação de projeto aparece na lista de toda pasta, ligada, mas só vale na dela."""
        saida = self._aviso_do_plugin([{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "project",
                                        "enabled": True, "projectPath": "/outro/projeto"}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("plugin sdd não instalado", saida.stderr)
        self.assertIn("claude plugin install sdd@trilha-ai --scope project", saida.stderr)

    def test_instalacao_do_usuario_atras_da_do_projeto_avisa(self) -> None:
        """Com as duas, a sessão pode carregar a do usuário (a execução manual da change 04 o viu)."""
        saida = self._aviso_do_plugin(
            [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "user", "enabled": True},
             {"id": "sdd@trilha-ai", "version": "2.2.0", "scope": "project", "enabled": True,
              "projectPath": "<projeto>"}], versao_do_comum="2.2")
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = [l for l in saida.stderr.splitlines() if "plugin sdd" in l]
        self.assertEqual(len(aviso), 1, saida.stderr)
        for trecho in ("1.35.0", "2.2", "claude plugin update sdd@trilha-ai --scope user"):
            self.assertIn(trecho, aviso[0])

    def test_instalacao_do_projeto_atras_avisa(self) -> None:
        saida = self._aviso_do_plugin(
            [{"id": "sdd@trilha-ai", "version": "2.1.0", "scope": "project", "enabled": True,
              "projectPath": "<projeto>"},
             {"id": "sdd@trilha-ai", "version": "2.2.0", "scope": "user", "enabled": True}],
            versao_do_comum="2.2")
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = [l for l in saida.stderr.splitlines() if "plugin sdd" in l]
        self.assertEqual(len(aviso), 1, saida.stderr)
        for trecho in ("2.1.0", "2.2", "claude plugin update sdd@trilha-ai --scope project"):
            self.assertIn(trecho, aviso[0])

    def test_lista_de_plugins_roda_na_pasta_do_projeto(self) -> None:
        """O "ligado" da lista segue o settings.json da pasta em que ela roda: a do projeto."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "projeto"
            _copia_do_kit(destino)
            lista = json.dumps([{"id": "sdd@trilha-ai", "version": "9.9.0", "scope": "user"}])
            claude = f"[ \"$(pwd -P)\" = \"{destino.resolve()}\" ] && printf '%s' '{lista}'"
            saida = self._confere_metodo(destino, claude=claude)  # chamada da pasta dos testes
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("plugin sdd na 9.9.0", saida.stderr)

    def test_plugin_de_outro_marketplace_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "sdd@meu-fork", "version": "0.3.9", "enabled": True}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = next(l for l in saida.stderr.splitlines() if "plugin sdd" in l)
        self.assertIn("sdd@meu-fork", aviso)
        self.assertIn("claude plugin install sdd@trilha-ai", aviso)

    def test_plugin_de_fora_do_kit_desinstala_no_escopo(self) -> None:
        """O uninstall vai ao escopo do usuário sem --scope; o de projeto precisa dele."""
        saida = self._aviso_do_plugin([{"id": "sdd@meu-fork", "version": "0.3.9", "scope": "project",
                                        "enabled": True, "projectPath": "<projeto>"}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("`claude plugin uninstall sdd@meu-fork --scope project`", saida.stderr)

    def test_aviso_do_plugin_com_comandos_separados(self) -> None:
        for lista in ([{"id": "sdd@pipeline-prd-tdd-openspec", "version": "0.3.9"}], []):
            avisos = [l for l in self._aviso_do_plugin(lista).stderr.splitlines() if "plugin sdd" in l]
            self.assertEqual(len(avisos), 1, lista)
            self.assertIn("`claude plugin marketplace add paulosrl/trilha-ai`", avisos[0])
            self.assertIn("`claude plugin install sdd@trilha-ai --scope project`", avisos[0])
            self.assertNotIn("&&", avisos[0])

    def _desligado(self, lista: list, configuracoes: dict) -> list[str]:
        saida = self._aviso_do_plugin(lista, configuracoes=configuracoes)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        return [l for l in saida.stderr.splitlines() if "desligado" in l]

    def test_plugin_desligado_pelo_projeto_avisa_uma_vez_no_escopo(self) -> None:
        """A instalação de projeto vem ligada na lista mesmo desligada pelo settings.json da pasta;
        com a do usuário junto, o aviso sai uma vez, no escopo que desliga."""
        lista = [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "user", "enabled": False},
                 {"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "project", "enabled": True,
                  "projectPath": "<projeto>"}]
        avisos = self._desligado(lista, {".claude/settings.json": {"enabledPlugins": {"sdd@trilha-ai": False}}})
        self.assertEqual(len(avisos), 1, avisos)
        self.assertIn("`claude plugin enable sdd@trilha-ai --scope project`", avisos[0])

    def test_plugin_desligado_pela_configuracao_local(self) -> None:
        lista = [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "user", "enabled": False}]
        local = {"enabledPlugins": {"sdd@trilha-ai": False}}
        avisos = self._desligado(lista, {".claude/settings.local.json": local})
        self.assertEqual(len(avisos), 1, avisos)
        self.assertIn("`claude plugin enable sdd@trilha-ai --scope local`", avisos[0])

    def test_plugin_ligado_pela_configuracao_local_nao_avisa(self) -> None:
        """A configuração local prevalece sobre o settings.json do projeto."""
        lista = [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "project", "enabled": True,
                  "projectPath": "<projeto>"}]
        avisos = self._desligado(lista, {
            ".claude/settings.json": {"enabledPlugins": {"sdd@trilha-ai": False}},
            ".claude/settings.local.json": {"enabledPlugins": {"sdd@trilha-ai": True}}})
        self.assertEqual(avisos, [])

    def test_plugin_desligado_pelo_usuario(self) -> None:
        """Sem declaração no projeto, vale o "ligado" da lista, que segue o settings do usuário."""
        lista = [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "user", "enabled": False}]
        avisos = self._desligado(lista, {".claude/settings.json": None})
        self.assertEqual(len(avisos), 1, avisos)
        self.assertIn("`claude plugin enable sdd@trilha-ai --scope user`", avisos[0])

    def test_plugin_declarado_e_so_na_maquina_avisa_o_install_no_projeto(self) -> None:
        """A máquina que recebe o projeto pelo git não roda o kit.py: a conferência a avisa."""
        lista = [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "user", "enabled": True}]
        saida = self._aviso_do_plugin(lista)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        avisos = [l for l in saida.stderr.splitlines() if "plugin sdd" in l]
        self.assertEqual(len(avisos), 1, saida.stderr)
        self.assertIn("declarado no projeto", avisos[0])
        self.assertIn("`claude plugin install sdd@trilha-ai --scope project`", avisos[0])

    def test_so_a_instalacao_do_usuario_sem_declaracao_nao_avisa(self) -> None:
        """O projeto de antes da 2.2, que não declara o plugin, segue com a do usuário."""
        lista = [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "user", "enabled": True}]
        saida = self._aviso_do_plugin(lista, configuracoes={".claude/settings.json": None})
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertNotIn("plugin sdd", saida.stderr)

    def test_trava_do_commit_nao_consulta_o_claude(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta, marca = Path(tmp) / "proj", Path(tmp) / "consultou"
            self._ferramenta("novo", str(pasta))
            falsos = Path(tmp) / "falsos"
            falsos.mkdir()
            _claude_falso(falsos, f"touch {marca}; printf '[]'")
            env = {**os.environ, **GIT_TESTE, "PATH": f"{falsos}:{os.environ['PATH']}"}
            subprocess.run(["git", "add", "-A"], cwd=pasta, check=True)
            commit = subprocess.run(["git", "commit", "-qm", "kit"], cwd=pasta, env=env,
                                    capture_output=True, text=True)
            self.assertEqual(commit.returncode, 0, commit.stderr)
            self.assertFalse(marca.exists(), "a trava do commit consultou o Claude Code")

    def test_check_sh_avisa_o_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp) / "proj"
            self._ferramenta("novo", str(pasta))
            falsos = Path(tmp) / "falsos"
            falsos.mkdir()
            _claude_falso(falsos, "printf '%s' '[{\"id\": \"sdd@meu-fork\", \"version\": \"0.3.9\"}]'")
            # Fora do CI (no do kit, CI=true e sem o openspec, que a verificação então cobraria).
            env = {**{k: v for k, v in os.environ.items() if k != "CI"},
                   "PATH": f"{falsos}:{os.environ['PATH']}"}
            saida = subprocess.run(["bash", "scripts/check.sh"], cwd=pasta, env=env,
                                   capture_output=True, text=True)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertIn("sdd@meu-fork", saida.stderr)

    def test_sem_o_claude_code_nao_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _copia_do_kit(Path(tmp))
            saida = self._confere_metodo(Path(tmp), claude=None)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertNotIn("plugin sdd", saida.stderr)

    def test_lista_de_plugins_com_erro_nao_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _copia_do_kit(Path(tmp))
            erro = self._confere_metodo(Path(tmp), claude="echo falhou >&2; exit 2")
        self.assertEqual(erro.returncode, 0, erro.stderr)
        self.assertNotIn("plugin sdd", erro.stderr)
        nao_json = self._aviso_do_plugin("isto não é json")
        self.assertEqual(nao_json.returncode, 0, nao_json.stderr)
        self.assertNotIn("plugin sdd", nao_json.stderr)

    def test_lista_de_plugins_sem_resposta_no_prazo_nao_avisa(self) -> None:
        """Um `claude` que não responde no prazo: a conferência não espera mais, sem aviso nem falha."""
        spec = importlib.util.spec_from_file_location("metodo", MODELO / "trilha/confere_metodo.py")
        metodo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(metodo)
        metodo.PRAZO_DO_CLAUDE = 0.3  # o de verdade é de segundos; o teste não espera por ele
        erro = io.StringIO()
        with tempfile.TemporaryDirectory() as falsos:
            _claude_falso(Path(falsos), "exec sleep 5")
            antes = os.environ["PATH"]
            os.environ["PATH"] = f"{falsos}:{antes}"
            try:
                inicio = time.monotonic()
                with contextlib.redirect_stderr(erro), contextlib.redirect_stdout(io.StringIO()):
                    codigo = metodo.main([])
                duracao = time.monotonic() - inicio
            finally:
                os.environ["PATH"] = antes
        self.assertEqual(codigo, 0, erro.getvalue())
        self.assertNotIn("plugin sdd", erro.getvalue())
        self.assertLess(duracao, 3)

    # O OpenSpec da máquina na conferência do método (change 09).

    GERADOS = (".claude/skills/openspec-propose/SKILL.md", ".claude/commands/opsx/propose.md")

    def _projeto_com_gerados(self, tmp: str, gerados: tuple[str, ...] = GERADOS) -> Path:
        """Um projeto copiado do kit, com os arquivos gerados do OpenSpec no índice do git."""
        destino = Path(tmp) / "projeto"
        _copia_do_kit(destino)
        for nome in gerados:
            (destino / nome).parent.mkdir(parents=True, exist_ok=True)
            (destino / nome).write_text(f"gerado: {nome}\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=destino, check=True)
        subprocess.run(["git", "add", "-A"], cwd=destino, check=True)
        return destino

    def _openspec_falso(self, falsos: Path, versao: str = "1.14.1", config: bool = True,
                        update: str = "exit 0") -> Path:
        """Um `openspec` de mentira em falsos/, que grava cada chamada num registro e responde ao
        `config path` (um arquivo que existe, ou não), ao `--version` e ao `update <pasta>` (o corpo
        dado, com a pasta em $2). Devolve o registro."""
        registro = falsos / "registro"
        registro.touch()
        if config:  # a configuração global da máquina, em <falsos>/xdg, salvo outro XDG_CONFIG_HOME
            (falsos / "xdg/openspec").mkdir(parents=True)
            (falsos / "xdg/openspec/config.json").write_text('{"profile": "custom"}', encoding="utf-8")
        falso = falsos / "openspec"
        falso.write_text(
            "#!/bin/sh\n"
            f'echo "$*" >> "{registro}"\n'
            f'configuracao="${{XDG_CONFIG_HOME:-{falsos}/xdg}}/openspec/config.json"\n'
            'if [ "$1 $2" = "config path" ]; then echo "$configuracao"; exit 0; fi\n'
            f'if [ "$1" = "--version" ]; then echo "{versao}"; exit 0; fi\n'
            f'if [ "$1" = "update" ]; then {update}; fi\n',
            encoding="utf-8",
        )
        falso.chmod(0o755)
        _claude_falso(falsos, "exit 1")
        for ferramenta in ("git", "rm", "sleep", "cat", "cp", "mkdir"):
            (falsos / ferramenta).symlink_to(shutil.which(ferramenta))
        return registro

    def _metodo_com_openspec(self, destino: Path, *args: str, **falso: object
                             ) -> tuple[subprocess.CompletedProcess[str], str]:
        """A conferência do método com o `openspec` falso; devolve a saída e o registro."""
        with tempfile.TemporaryDirectory() as falsos:
            registro = self._openspec_falso(Path(falsos), **falso)
            saida = subprocess.run(
                [sys.executable, "-I", str(destino / "trilha/confere_metodo.py"), *args],
                capture_output=True, text=True, check=False, env={**os.environ, "PATH": falsos},
            )
            return saida, registro.read_text(encoding="utf-8")

    APAGA_A_SKILL = 'rm -r "$2/.claude/skills/openspec-propose"'

    def test_openspec_avisa_as_skills_que_o_update_apagaria(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida, _ = self._metodo_com_openspec(self._projeto_com_gerados(tmp), update=self.APAGA_A_SKILL)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = next((l for l in saida.stderr.splitlines() if "openspec update mudaria" in l), "")
        self.assertIn("apagaria: .claude/skills/openspec-propose/SKILL.md", aviso, saida.stderr)
        self.assertIn("openspec config list", aviso)

    def test_openspec_ensaio_sem_a_rede(self) -> None:
        """Verify da change 09: o ensaio roda com a consulta da versão nova e a telemetria desligadas."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = self._projeto_com_gerados(tmp)
            with tempfile.TemporaryDirectory() as falsos:
                grava = f'echo "$OPENSPEC_NO_UPDATE_CHECK $OPENSPEC_TELEMETRY $DO_NOT_TRACK" > "{falsos}/ambiente"'
                self._openspec_falso(Path(falsos), update=grava)
                subprocess.run([sys.executable, "-I", str(destino / "trilha/confere_metodo.py")],
                               capture_output=True, check=False, env={**os.environ, "PATH": falsos})
                ambiente = (Path(falsos) / "ambiente").read_text(encoding="utf-8").split()
        self.assertEqual(ambiente, ["1", "0", "1"])

    def test_openspec_aviso_corta_a_lista(self) -> None:
        """Verify da change 09: até cinco nomes por grupo, e o resto em contagem."""
        gerados = tuple(f".claude/skills/openspec-s{i}/SKILL.md" for i in range(7))
        with tempfile.TemporaryDirectory() as tmp:
            saida, _ = self._metodo_com_openspec(self._projeto_com_gerados(tmp, gerados=gerados),
                                                 update='rm -r "$2/.claude/skills"')
        aviso = next((l for l in saida.stderr.splitlines() if "openspec update mudaria" in l), "")
        self.assertIn("openspec-s4/SKILL.md e mais 2", aviso, saida.stderr)
        self.assertNotIn("openspec-s5", aviso)

    def test_openspec_ensaio_nao_muda_a_configuracao_da_maquina(self) -> None:
        """Revisão da change 09, achado 1: a migração do OpenSpec regrava a configuração global."""
        regrava = 'echo migrado > "$configuracao"; ' + self.APAGA_A_SKILL
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as falsos:
            destino = self._projeto_com_gerados(tmp)
            self._openspec_falso(Path(falsos), update=regrava)
            saida = subprocess.run([sys.executable, "-I", str(destino / "trilha/confere_metodo.py")],
                                   capture_output=True, text=True, check=False, env={**os.environ, "PATH": falsos})
            maquina = (Path(falsos) / "xdg/openspec/config.json").read_text(encoding="utf-8")
        self.assertEqual(maquina, '{"profile": "custom"}')
        self.assertIn("openspec update mudaria", saida.stderr)

    def test_openspec_avisa_o_que_criaria_e_trocaria(self) -> None:
        """Revisão da change 09, achado 5: os grupos "criaria" e "trocaria" do aviso."""
        muda = ('mkdir -p "$2/.claude/skills/openspec-nova" && echo nova > "$2/.claude/skills/openspec-nova/SKILL.md"; '
                'echo reescrito > "$2/.claude/commands/opsx/propose.md"')
        with tempfile.TemporaryDirectory() as tmp:
            saida, _ = self._metodo_com_openspec(self._projeto_com_gerados(tmp), update=muda)
        aviso = next((l for l in saida.stderr.splitlines() if "openspec update mudaria" in l), "")
        self.assertIn("criaria: .claude/skills/openspec-nova/SKILL.md", aviso, saida.stderr)
        self.assertIn("trocaria: .claude/commands/opsx/propose.md", aviso)
        self.assertNotIn("apagaria", aviso)

    def test_openspec_nome_fora_do_utf8_nao_derruba(self) -> None:
        """Revisão da change 09, achado 3: o aviso nunca vira falha, nem com um nome em Latin-1."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = self._projeto_com_gerados(tmp)
            (destino / os.fsdecode(b"caf\xe9.txt")).write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=destino, check=True)
            saida, _ = self._metodo_com_openspec(destino, update=self.APAGA_A_SKILL)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("openspec update mudaria", saida.stderr)

    def test_openspec_em_dia_nao_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida, registro = self._metodo_com_openspec(self._projeto_com_gerados(tmp))
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("update", registro)  # o ensaio rodou
        self.assertNotIn("openspec update mudaria", saida.stderr)

    def test_openspec_ensaio_nao_toca_o_projeto(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = self._projeto_com_gerados(tmp)
            antes = {str(a): a.read_bytes() for a in destino.rglob("*") if a.is_file() and ".git" not in a.parts}
            saida, _ = self._metodo_com_openspec(destino, update=self.APAGA_A_SKILL)
            depois = {str(a): a.read_bytes() for a in destino.rglob("*") if a.is_file() and ".git" not in a.parts}
        self.assertIn("openspec update mudaria", saida.stderr)
        self.assertEqual(antes, depois)

    def test_openspec_ausente_nao_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as falsos:
            destino = self._projeto_com_gerados(tmp)
            _claude_falso(Path(falsos), "exit 1")
            (Path(falsos) / "git").symlink_to(shutil.which("git"))
            saida = subprocess.run([sys.executable, "-I", str(destino / "trilha/confere_metodo.py")],
                                   capture_output=True, text=True, check=False, env={**os.environ, "PATH": falsos})
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertNotIn("openspec", saida.stderr.lower())

    def test_openspec_sem_configuracao_global_nao_ensaia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida, registro = self._metodo_com_openspec(self._projeto_com_gerados(tmp), config=False,
                                                        update=self.APAGA_A_SKILL)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("config path", registro)
        self.assertNotIn("update", registro)
        self.assertNotIn("openspec update mudaria", saida.stderr)

    def test_openspec_ensaio_com_erro_nao_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida, registro = self._metodo_com_openspec(self._projeto_com_gerados(tmp),
                                                        update=self.APAGA_A_SKILL + "; exit 1")
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("update", registro)
        self.assertNotIn("openspec update mudaria", saida.stderr)
        # Sem resposta no prazo: o prazo de verdade é de segundos; o teste não espera por ele.
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as falsos:
            destino = self._projeto_com_gerados(tmp)
            self._openspec_falso(Path(falsos), update="exec sleep 5")
            spec = importlib.util.spec_from_file_location("metodo_do_projeto", destino / "trilha/confere_metodo.py")
            metodo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(metodo)
            metodo.PRAZO_DO_OPENSPEC = 0.5
            antes = os.environ["PATH"]
            os.environ["PATH"] = falsos
            try:
                inicio = time.monotonic()
                avisos = metodo.avisar_openspec()
                duracao = time.monotonic() - inicio
            finally:
                os.environ["PATH"] = antes
        self.assertFalse([a for a in avisos if "openspec update mudaria" in a], avisos)
        self.assertLess(duracao, 4)

    def test_openspec_sem_arquivos_gerados_nao_ensaia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida, registro = self._metodo_com_openspec(self._projeto_com_gerados(tmp, gerados=()),
                                                        update=self.APAGA_A_SKILL)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertNotIn("update", registro)

    def test_openspec_versao_diferente_da_do_ci_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = self._projeto_com_gerados(tmp)
            ci = destino / ".github/workflows/verificacao.yml"
            self.assertIn("@fission-ai/openspec@1.14.1", ci.read_text(encoding="utf-8"))
            saida, _ = self._metodo_com_openspec(destino, versao="1.14.3")
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = next((l for l in saida.stderr.splitlines() if "1.14.3" in l), "")
        self.assertIn("1.14.1", aviso, saida.stderr)
        self.assertIn("npm install -g @fission-ai/openspec@1.14.1", aviso)

    def test_openspec_versao_igual_a_do_ci_nao_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida, registro = self._metodo_com_openspec(self._projeto_com_gerados(tmp), versao="1.14.1")
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("--version", registro)
        self.assertNotIn("npm install -g", saida.stderr)

    def test_openspec_sem_versao_no_ci_nao_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = self._projeto_com_gerados(tmp)
            ci = destino / ".github/workflows/verificacao.yml"
            ci.write_text(ci.read_text(encoding="utf-8").replace("@fission-ai/openspec@1.14.1", "@fission-ai/openspec"),
                          encoding="utf-8")
            sem_pin, _ = self._metodo_com_openspec(destino, versao="1.14.3")
            ci.write_text(ci.read_text(encoding="utf-8").replace("@fission-ai/openspec", "@fission-ai/openspec@latest"),
                          encoding="utf-8")
            com_latest, _ = self._metodo_com_openspec(destino, versao="1.14.3")
            ci.unlink()
            sem_ci, _ = self._metodo_com_openspec(destino, versao="1.14.3")
        for saida in (sem_pin, com_latest, sem_ci):
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertNotIn("npm install -g", saida.stderr)

    def test_trava_do_commit_nao_consulta_o_openspec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as falsos:
            pasta = self._projeto_novo(tmp)
            for nome in self.GERADOS:
                (pasta / nome).parent.mkdir(parents=True, exist_ok=True)
                (pasta / nome).write_text("gerado\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=pasta, check=True)
            registro = self._openspec_falso(Path(falsos), versao="1.14.3", update=self.APAGA_A_SKILL)
            for ferramenta in ("python3", "bash", "cat", "dirname", "readlink"):
                caminho = shutil.which(ferramenta)
                if caminho and not (Path(falsos) / ferramenta).exists():
                    (Path(falsos) / ferramenta).symlink_to(caminho)
            env = {**os.environ, "PATH": falsos}
            trava = subprocess.run(["bash", str(pasta / "trilha/hooks/pre-commit")], cwd=pasta, env=env,
                                   capture_output=True, text=True, check=False)
            sem_consulta = registro.read_text(encoding="utf-8")
            subprocess.run([sys.executable, "-I", str(pasta / "trilha/confere_metodo.py")], cwd=pasta, env=env,
                           capture_output=True, check=False)
            com_consulta = registro.read_text(encoding="utf-8")
        self.assertEqual(trava.returncode, 0, trava.stderr)
        self.assertEqual(sem_consulta, "")
        self.assertIn("--version", com_consulta)  # sem o --sem-plugin, o falso é consultado

    def test_metodo_aprova_um_repositorio_feito_do_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            shutil.rmtree(destino / "sdd")  # o projeto antigo, de antes do sdd/padroes-tecnicos.md
            saida = self._confere_metodo(destino, "--vizinho", "outro")
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertIn("sem a pasta sdd/: crie-a com `mkdir sdd`", saida.stderr)
            self.assertIn("modelo/sdd/padroes-tecnicos.md", saida.stderr)
            self.assertNotIn("sem sdd/decomposicao", saida.stderr)
            (destino / "sdd").mkdir()
            saida = self._confere_metodo(destino)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertNotIn("sem a pasta sdd/", saida.stderr)
            self.assertIn("sem sdd/decomposicao", saida.stderr)

    def test_metodo_reprova_ciclo_divergente_andamento_vizinho_e_linha_no_tdd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            (destino / "sdd").mkdir(exist_ok=True)
            (destino / "sdd/decomposicao-x.md").write_text(
                "## 1. Changes\n\n| NN | Change |\n|---|---|\n| 01 | a |\n| 02 | b |\n\n## 2. Regras\n\n"
                "## Ciclo\n\n| NN | briefing | auditoria | archive |\n|---|---|---|---|\n"
                "| 01 | — | — | — |\n",
                encoding="utf-8",
            )
            (destino / "sdd/tdd-x.md").write_text(
                "- **Evidência:** `app/nao_existe.py` (linhas 3 a 9)\n", encoding="utf-8"
            )
            andamento = destino / "ANDAMENTO.md"
            andamento.write_text(andamento.read_text(encoding="utf-8") + "outro\n", encoding="utf-8")
            saida = self._confere_metodo(destino, "--vizinho", "outro")
            self.assertEqual(saida.returncode, 1, saida.stdout)
            self.assertIn("tabela Ciclo diferem", saida.stderr)
            self.assertIn("número de linha", saida.stderr)
            self.assertIn("não existe: app/nao_existe.py", saida.stderr)
            self.assertIn("cita outro repositório: outro", saida.stderr)

    def test_metodo_recusa_argumento_errado(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            self.assertEqual(self._confere_metodo(destino, "--outro").returncode, 2)

    def test_gerador_da_pagina_nao_inventa_etapas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            saida = subprocess.run(
                [sys.executable, "-I", str(destino / "trilha/gerar_pagina_sdd.py")],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(saida.returncode, 0, saida.stderr)
            pagina = (destino / "sdd/documentacao.html").read_text(encoding="utf-8")
            self.assertIn('"prd": ""', pagina)
            self.assertIn("Trilha AI", pagina)

    def test_pagina_mostra_change_retirada(self) -> None:
        """Change retirada antes do archive tem linha no "Ciclo" e aparece como retirada, não em andamento."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            (destino / "sdd").mkdir(exist_ok=True)
            (destino / "sdd/decomposicao-x.md").write_text(
                "# Decomposição\n\n## Ciclo\n\n| NN | briefing | auditoria | archive |\n|---|---|---|---|\n"
                "| 01 | briefing-change-01-icone.md (aprovado 2026-10-13) | — | retirada em 2026-10-13 |\n",
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, "-I", str(destino / "trilha/gerar_pagina_sdd.py")],
                capture_output=True, text=True, check=True,
            )
            pagina = (destino / "sdd/documentacao.html").read_text(encoding="utf-8")
            self.assertIn('"estado": "retirada"', pagina)
            self.assertIn(".selo.retirada", pagina)

    def _gera_pagina(self, arquivos: dict[str, str], origin: str = "") -> tuple[dict, str]:
        """Copia o kit, escreve os documentos em sdd/, gera a página e devolve os dados e o stderr."""
        import json

        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            (destino / "sdd").mkdir(exist_ok=True)
            if origin:
                subprocess.run(["git", "init", "-q"], cwd=destino, check=True)
                subprocess.run(["git", "remote", "add", "origin", origin], cwd=destino, check=True)
            for nome, texto in arquivos.items():
                (destino / "sdd" / nome).write_text(texto, encoding="utf-8")
            saida = subprocess.run(
                [sys.executable, "-I", str(destino / "trilha/gerar_pagina_sdd.py")],
                capture_output=True, text=True, check=True,
            )
            pagina = (destino / "sdd/documentacao.html").read_text(encoding="utf-8")
        bruto = pagina.split('id="dados">', 1)[1].split("</script>", 1)[0]
        return json.loads(bruto.replace("<\\/", "</")), saida.stderr

    def test_pagina_le_o_ciclo_sem_perder_nem_inventar_change(self) -> None:
        """A leitura para na seção seguinte, avisa a linha fora do formato e acha o briefing na célula."""
        dados, stderr = self._gera_pagina({"decomposicao-x.md": (
            "# Decomposição\n\n## Ciclo\n\n| NN | briefing | auditoria | archive |\n|---|---|---|---|\n"
            "| 01 | [b](briefing-openspec/briefing-change-01-fundacao-cep.md) | aprovada | arquivada 2026 |\n"
            "| 02 | - | - | - |\n"
            "| 03 | briefing-change-03-x.md | — | — | PR #4 |\n"
            "\n## Depois\n\n| 05 | briefing-change-05-y.md | — | — |\n"
        )})
        changes = {c["numero"]: c for c in dados["changes"]}
        self.assertEqual(sorted(changes), ["01", "02"])
        self.assertEqual(changes["01"]["nome"], "fundacao-cep")  # como o OpenSpec escreve
        self.assertEqual(changes["01"]["estado"], "arquivada")
        self.assertEqual(changes["02"]["estado"], "futura")
        self.assertIn("linha do Ciclo fora do formato, ignorada: | 03 |", stderr)

    def test_resumo_do_produto_sem_marcacao_e_sem_cortar_palavra(self) -> None:
        palavras = " ".join(["palavra"] * 60)
        dados, _ = self._gera_pagina({"prd-x.md": (
            "# PRD: X\n\n> **Documento histórico.** Leia o `README.md`.\n\n"
            f"O **sistema** usa `código` e [um link](https://x) com {palavras}.\n"
        )})
        resumo = dados["resumo"]
        self.assertTrue(resumo.startswith("O sistema usa código e um link com palavra"), resumo)
        self.assertNotRegex(resumo, r"\*\*|`|\]\(|^>")
        self.assertTrue(resumo.endswith("palavra…"), resumo)
        self.assertLessEqual(len(resumo), 301)

    def test_pagina_liga_o_pr_de_cada_change_pelo_origin_local(self) -> None:
        """O "PR #N" do Ciclo vira link pelo origin do git; o endereço sai sem .git e sem credencial."""
        ciclo = (
            "## Ciclo\n\n| NN | briefing | auditoria | archive |\n|---|---|---|---|\n"
            "| 01 | briefing-change-01-a.md | aprovada | arquivada 2026-10-15 (PR #7) |\n"
            "| 02 | briefing-change-02-b.md | — | — |\n"
        )
        for origin in ("git@github.com:dono/repo.git", "https://usuario:segredo@github.com/dono/repo.git"):
            dados, _ = self._gera_pagina({"decomposicao-x.md": ciclo}, origin=origin)
            self.assertEqual(dados["repositorio"], "https://github.com/dono/repo", origin)
            self.assertEqual([c["pr"] for c in dados["changes"]], ["7", ""])
        dados, _ = self._gera_pagina({"decomposicao-x.md": ciclo})
        self.assertEqual(dados["repositorio"], "")
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn('célula do archive ("PR #N")', config)

    def test_pagina_funciona_sem_rede_e_se_chama_documentacao_do_projeto(self) -> None:
        modelo = (MODELO / "trilha/pagina_sdd_modelo.html").read_text(encoding="utf-8")
        gerador = (MODELO / "trilha/gerar_pagina_sdd.py").read_text(encoding="utf-8")
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("<script src=", modelo)
        self.assertIn("marked v12.0.2", modelo)
        self.assertNotIn("</script", modelo.split("marked v12.0.2", 1)[1].split("\n</script>", 1)[0])
        self.assertIn('f"{nome}: documentação"', gerador)
        self.assertIn("é a documentação do projeto, gerada", comum)

    def test_modelo_da_pagina_tem_teclado_celular_e_rodape_corretos(self) -> None:
        modelo = (MODELO / "trilha/pagina_sdd_modelo.html").read_text(encoding="utf-8")
        self.assertIn("ArrowRight", modelo)
        self.assertIn('document.getElementById("aba-" + chave).focus()', modelo)
        self.assertIn(".briefings > li {", modelo)
        self.assertNotIn(".briefings li {", modelo)  # a regra pegava as listas dentro dos briefings
        self.assertIn("grid-template-columns: minmax(0, 1fr); gap: 0.5rem; }", modelo)
        self.assertIn("article.doc { overflow-wrap: break-word; }", modelo)  # palavra longa no celular
        self.assertIn("article.doc a { overflow-wrap: anywhere; }", modelo)  # URL longa no celular
        self.assertIn("os documentos mudaram por último em", modelo)
        self.assertNotIn('", em " + dados.atualizado', modelo)


    def _guarda(self, comando: str, gh_sai_com: int = 0, gh_corpo: str | None = None,
                trava: Path | None = None) -> subprocess.CompletedProcess:
        """Roda a trava com um gh falso no PATH, que sai com o código pedido (ou roda o corpo)."""
        with tempfile.TemporaryDirectory() as tmp:
            gh = Path(tmp) / "gh"
            gh.write_text(f"#!/bin/sh\n{gh_corpo or f'exit {gh_sai_com}'}\n")
            gh.chmod(0o755)
            env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}"}
            return subprocess.run(
                [sys.executable, "-I", str(trava or MODELO / "trilha/guarda.py")],
                input=json.dumps({"tool_name": "Bash", "tool_input": {"command": comando}}),
                capture_output=True, text=True, check=False, env=env,
            )

    def test_trava_do_claude_barra_so_o_que_o_metodo_proibe(self) -> None:
        barrados = ("git push --force origin main", "git push -f", "git push origin +main",
                    "git commit --no-verify -m x", "pkill -f node", "pgrep -af x",
                    "gh pr merge 7 --squash", "gh pr merge 7", "gh pr merge 7 --merge --rebase")
        for comando in barrados:
            saida = self._guarda(comando)
            self.assertEqual(saida.returncode, 2, comando)
            self.assertIn("bloqueado pela trava do método", saida.stderr)
        for comando in ("git push -u origin change/01-x", "kill 1234", "git status",
                        "gh pr merge 7 --merge --delete-branch"):
            self.assertEqual(self._guarda(comando).returncode, 0, comando)
        vermelho = self._guarda("gh pr merge 7 --merge --delete-branch", gh_sai_com=1)
        self.assertEqual(vermelho.returncode, 2)
        self.assertIn("não está verde", vermelho.stderr)

    def test_trava_do_claude_le_as_opcoes_e_nao_o_texto(self) -> None:
        """As opções juntas e as longas não escapam; o texto de uma mensagem não é opção."""
        for comando in ("git push -uf origin main", "cd x && git push --force-with-lease=main",
                        "bash -c 'git push --force'", "pkill --full node", "git commit -n -m x",
                        "git commit -anm x", "git merge --no-verify main"):
            self.assertEqual(self._guarda(comando).returncode, 2, comando)
        mensagem = "git commit -m \"$(cat <<'EOF'\nfix: explica o --no-verify, o pkill -f e o gh pr merge 7\nEOF\n)\""
        for comando in (mensagem, "git commit -m 'sem --no-verify'", "git commit -mn",
                        "git push -u origin change/01-fix-f", "git push --follow-tags",
                        "git push && rm -f x", "pkill -F arquivo.pid", "echo git push -f"):
            saida = self._guarda(comando)
            self.assertEqual(saida.returncode, 0, f"{comando}: {saida.stderr}")

    # A trava contra os contornos da rodada 4 da auditoria (change 07).

    def _barrados(self, comandos: tuple[str, ...]) -> None:
        for comando in comandos:
            saida = self._guarda(comando)
            self.assertEqual(saida.returncode, 2, f"{comando!r}: {saida.stderr}")
            self.assertIn("bloqueado pela trava do método", saida.stderr)

    def _livres(self, comandos: tuple[str, ...]) -> None:
        for comando in comandos:
            saida = self._guarda(comando)
            self.assertEqual(saida.returncode, 0, f"{comando!r}: {saida.stderr}")

    def test_trava_barra_o_hookspath_desligado(self) -> None:
        self._barrados(("git -c core.hooksPath=/dev/null commit -m x", "git -ccore.hooksPath= commit -m x",
                        "git -c core.hookspath=.git/hooks commit -m x",
                        "git config core.hooksPath .git/hooks", "git config --unset core.hooksPath",
                        "git config --local core.hooksPath /dev/null"))

    def test_trava_deixa_ler_e_gravar_o_hookspath_do_metodo(self) -> None:
        self._livres(("git config core.hooksPath", "git config core.hooksPath trilha/hooks",
                      "git -c core.hooksPath=trilha/hooks commit -m x"))

    def test_trava_barra_o_no_verify_abreviado(self) -> None:
        self._barrados(("git commit --no-veri -m y", "git commit --no-verif -m y", "git push --no-veri"))
        self._livres(("git commit --no-edit", "git log --no-walk"))

    def test_trava_barra_o_push_forcado_atras_de_outro_comando(self) -> None:
        self._barrados(("timeout 10 git push -f", "echo main | xargs git push -f origin",
                        "eval git push -f", "nice -n 5 git push --force", "xargs -I {} git push -f origin {}"))

    def test_trava_barra_o_push_forcado_nas_palavras_do_shell(self) -> None:
        self._barrados(("if true; then git push -f; fi", "{ git push -f; }",
                        "for b in a; do git push -f origin $b; done", "while false; do :; done; ! git push -f"))

    def test_trava_barra_o_push_forcado_em_shell_aninhado(self) -> None:
        self._barrados(('bash -lc "git push -f"', "bash -xc 'git push --force'", 'bash <<< "git push -f"',
                        "`git push -f`", "echo $(git push -f)"))

    def test_trava_barra_o_push_forcado_com_cerquilha_ou_aspa_sem_par(self) -> None:
        self._barrados(("echo a#b; git push -f", "[ ${#x} -eq 0 ] && git push -f",
                        "cd repo  # entra\ngit push --force-with-lease",
                        "cat > n.txt <<EOF\nit's\nEOF\ngit push --force"))

    def test_trava_barra_a_forca_abreviada_e_o_espelho(self) -> None:
        self._barrados(("git push --force-w", "git push --forc", "git push --mirror", "git push --mirr origin"))

    def test_trava_deixa_o_git_como_argumento(self) -> None:
        self._livres(("echo git push -f", "git push && rm -f x", "git push --force-if-includes",
                      "git push -u origin change/07-x", "grep -rn 'git push -f' docs"))

    def test_trava_le_o_subcomando_depois_das_opcoes_globais(self) -> None:
        self._livres(("git log --grep commit -n 3", "git log -n 3 -- push -f", "git show HEAD -- commit"))
        self._barrados(("git -C ../x push -f", "git --git-dir=.git push --force", "git -c x.y=1 commit -n -m z"))

    def test_trava_aceita_o_merge_com_m(self) -> None:
        self._livres(("gh pr merge 7 -m -d", "gh pr merge 7 -md"))
        self._barrados(("gh pr merge 7 -s", "gh pr merge 7 -m -r"))

    def test_trava_confere_o_pr_no_repositorio_indicado(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            registro = Path(tmp) / "args.txt"
            saida = self._guarda("gh pr merge -R dono/repo 7 --merge -t 'titulo'",
                                 gh_corpo=f'echo "$@" >> {registro}; exit 0')
            self.assertEqual(saida.returncode, 0, saida.stderr)
            chamada = registro.read_text(encoding="utf-8").split()
        self.assertEqual(chamada[:3], ["pr", "checks", "7"])
        self.assertIn("dono/repo", chamada)
        self.assertNotIn("titulo", chamada)

    def test_trava_barra_a_verificacao_que_nao_responde(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            guarda = Path(tmp) / "guarda.py"
            texto = (MODELO / "trilha/guarda.py").read_text(encoding="utf-8")
            self.assertIn("PRAZO_DO_GH = 30", texto)
            guarda.write_text(texto.replace("PRAZO_DO_GH = 30", "PRAZO_DO_GH = 1"), encoding="utf-8")
            inicio = time.monotonic()
            saida = self._guarda("gh pr merge 7 --merge", gh_corpo="sleep 5; exit 0", trava=guarda)
            self.assertLess(time.monotonic() - inicio, 4)
        self.assertEqual(saida.returncode, 2)
        self.assertIn("não respondeu", saida.stderr)

    def test_trava_barra_a_linha_continuada_e_a_atribuicao_com_aspas(self) -> None:
        """Revisão de código, pontos 1 e 2."""
        self._barrados(("git push \\\n  --force origin main", "git push origin main \\\n  -f",
                        "git commit -m x \\\n  -n",
                        'GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push --force origin main',
                        'GIT_TRACE=1 GIT_SSH_COMMAND="ssh -v" git push -f'))

    def test_trava_le_o_c_so_do_shell(self) -> None:
        """Revisão de código, ponto 3: o -c do git não é shell, e o texto aninhado não engole o resto."""
        self._barrados(('git -c "user.name=Claude Bot" commit -n -m x',
                        'git -c "core.hooksPath=/tmp/sem hooks" commit -m x', 'sudo bash -c "git push -f"'))
        self._livres(('bash -lc "gh pr merge 7 --merge"', 'git -c "user.name=Claude Bot" commit -m x'))

    def test_trava_nao_le_o_corpo_do_heredoc(self) -> None:
        """Revisão de código, ponto 4: o texto de um heredoc não é comando, salvo para um shell."""
        self._livres(("cat > f.md <<'EOF'\nUse `git push -f` nunca, nem `pkill -f`.\nEOF",
                      "git commit -F- <<'EOF'\nfeat: a trava barra `git push -f`\nEOF",
                      "git commit -m \"$(cat <<'EOF'\nfix: `git push -f`, 12\" de tela\nEOF\n)\"",
                      "cat >> n.md <<-FIM\n\tgit push --force\n\tFIM"))
        self._barrados(("bash <<EOF\ngit push -f\nEOF", "cat > f <<'EOF'\nx\nEOF\ngit push -f",
                        "sh -s <<'EOF'\ngit commit -n -m x\nEOF"))

    def test_trava_confere_o_pr_do_gh_repo(self) -> None:
        """Revisão de código, ponto 6: o GH_REPO do comando vai ao gh pr checks."""
        with tempfile.TemporaryDirectory() as tmp:
            registro = Path(tmp) / "args.txt"
            saida = self._guarda("GH_REPO=dono/outro gh pr merge 7 --merge",
                                 gh_corpo=f'echo "$@" >> {registro}; exit 0')
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertIn("dono/outro", registro.read_text(encoding="utf-8").split())

    def test_trava_que_falha_barra(self) -> None:
        """Sugestão do verify: um erro inesperado da trava barra, nunca libera."""
        with tempfile.TemporaryDirectory() as tmp:
            guarda = Path(tmp) / "guarda.py"
            texto = (MODELO / "trilha/guarda.py").read_text(encoding="utf-8")
            marca = "def _motivo(texto: str) -> str:\n"
            self.assertIn(marca, texto)
            guarda.write_text(texto.replace(marca, marca + "    raise RuntimeError('quebrada')\n"),
                              encoding="utf-8")
            saida = self._guarda("git status", trava=guarda)
        self.assertEqual(saida.returncode, 2)
        self.assertIn("a trava falhou", saida.stderr)

    def test_trava_deixa_passar_a_entrada_sem_comando(self) -> None:
        for entrada in ("[]", '{"tool_input": "x"}', '{"tool_input": {"command": 3}}', "{}"):
            saida = subprocess.run([sys.executable, "-I", str(MODELO / "trilha/guarda.py")], input=entrada,
                                   capture_output=True, text=True, check=False)
            self.assertEqual(saida.returncode, 0, f"{entrada}: {saida.stderr}")
            self.assertEqual(saida.stderr, "", entrada)

    def test_travas_ligadas_no_projeto_novo_e_a_do_commit_funciona(self) -> None:
        env = {**os.environ, **GIT_TESTE}
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp) / "proj"
            self._ferramenta("novo", str(pasta))
            ligado = subprocess.run(["git", "config", "core.hooksPath"], cwd=pasta,
                                    capture_output=True, text=True).stdout.strip()
            self.assertEqual(ligado, "trilha/hooks")
            self.assertIn("trilha/guarda.py", (pasta / ".claude/settings.json").read_text())
            subprocess.run(["git", "add", "-A"], cwd=pasta, check=True)
            ok = subprocess.run(["git", "commit", "-qm", "kit"], cwd=pasta, env=env,
                                capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            claude = pasta / "CLAUDE.md"
            claude.write_text(claude.read_text(encoding="utf-8").replace("@trilha/CLAUDE-comum.md", ""))
            barrado = subprocess.run(["git", "commit", "-qam", "quebrado"], cwd=pasta, env=env,
                                     capture_output=True, text=True)
            self.assertNotEqual(barrado.returncode, 0)
            self.assertIn("não importa o comum", barrado.stderr)

    def test_atualizar_soma_a_trava_ao_settings_que_ja_existe(self) -> None:
        import json

        env = {**os.environ, **GIT_TESTE}
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_velho(tmp)
            settings = pasta / ".claude/settings.json"
            settings.write_text(json.dumps({"permissions": {"allow": ["Bash(ls:*)"]}}))
            subprocess.run(["git", "config", "--unset", "core.hooksPath"], cwd=pasta, check=True)
            subprocess.run(["git", "commit", "-qam", "settings do projeto"], cwd=pasta, env=env,
                           check=True)
            self.assertEqual(self._ferramenta("atualizar", str(pasta)).returncode, 0)
            dados = json.loads(settings.read_text())
            self.assertEqual(dados["permissions"], {"allow": ["Bash(ls:*)"]})
            self.assertIn("trilha/guarda.py", json.dumps(dados["hooks"]))
            self.assertEqual(self._ferramenta("atualizar", str(pasta)).returncode, 1)  # não commitado
            subprocess.run(["git", "commit", "-qam", "kit"], cwd=pasta, env=env, check=True)
            self._ferramenta("atualizar", str(pasta))
            self.assertEqual(json.dumps(json.loads(settings.read_text())["hooks"]).count("guarda"), 1)

    def test_novo_declara_o_plugin(self) -> None:
        """D4: o projeto declara o plugin e o marketplace; a trava continua ligada."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            dados = json.loads((pasta / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertIs(dados["enabledPlugins"]["sdd@trilha-ai"], True)
        self.assertEqual(dados["extraKnownMarketplaces"]["trilha-ai"],
                         {"source": {"source": "github", "repo": "paulosrl/trilha-ai"}})
        self.assertIn("trilha/guarda.py", json.dumps(dados["hooks"]))

    def _atualizar_com_settings(self, tmp: str, settings: dict) -> dict:
        """Um projeto com o settings.json dado, commitado, depois do kit.py atualizar."""
        pasta = self._projeto_novo(tmp)
        (pasta / ".claude/settings.json").write_text(json.dumps(settings), encoding="utf-8")
        self._commit_tudo(pasta, "settings do projeto")
        saida = self._ferramenta("atualizar", str(pasta))
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        return json.loads((pasta / ".claude/settings.json").read_text(encoding="utf-8"))

    def test_atualizar_soma_o_plugin_ao_settings_proprio(self) -> None:
        proprio = {"permissions": {"allow": ["Bash(ls:*)"]},
                   "enabledPlugins": {"outro@loja": True},
                   "extraKnownMarketplaces": {"loja": {"source": {"source": "github", "repo": "a/b"}}}}
        with tempfile.TemporaryDirectory() as tmp:
            dados = self._atualizar_com_settings(tmp, proprio)
        self.assertEqual(dados["permissions"], proprio["permissions"])
        self.assertEqual(dados["enabledPlugins"], {"outro@loja": True, "sdd@trilha-ai": True})
        self.assertEqual(dados["extraKnownMarketplaces"]["loja"], proprio["extraKnownMarketplaces"]["loja"])
        self.assertIn("trilha-ai", dados["extraKnownMarketplaces"])

    def test_atualizar_mantem_o_plugin_desligado(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dados = self._atualizar_com_settings(tmp, {"enabledPlugins": {"sdd@trilha-ai": False}})
        self.assertIs(dados["enabledPlugins"]["sdd@trilha-ai"], False)

    def test_atualizar_duas_vezes_nao_muda_o_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            (pasta / ".claude/settings.json").write_text('{"permissions": {}}', encoding="utf-8")
            self._commit_tudo(pasta, "settings do projeto")
            self.assertEqual(self._ferramenta("atualizar", str(pasta)).returncode, 0)
            self._commit_tudo(pasta, "kit")
            depois = (pasta / ".claude/settings.json").read_bytes()
            self.assertEqual(self._ferramenta("atualizar", str(pasta)).returncode, 0)
            self.assertEqual((pasta / ".claude/settings.json").read_bytes(), depois)

    def test_novo_traz_os_padroes_tecnicos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            self.assertEqual((pasta / "sdd/padroes-tecnicos.md").read_bytes(),
                             (MODELO / "sdd/padroes-tecnicos.md").read_bytes())
            self.assertEqual(self._verifica(pasta, check_sh=True).returncode, 0)

    def test_atualizar_preserva_os_padroes_do_projeto(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            padroes = pasta / "sdd/padroes-tecnicos.md"
            padroes.write_text("# Padrões técnicos\n\nGo com SQLite.\n", encoding="utf-8")
            self._commit_tudo(pasta, "padrões do projeto")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertEqual(padroes.read_text(encoding="utf-8"), "# Padrões técnicos\n\nGo com SQLite.\n")

    def test_atualizar_cria_os_padroes_que_faltam(self) -> None:
        """O projeto de antes da 2.2 recebe os padrões na passagem para ela."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_velho(tmp)
            shutil.rmtree(pasta / "sdd")
            self._commit_tudo(pasta, "sem os padrões")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertEqual((pasta / "sdd/padroes-tecnicos.md").read_bytes(),
                             (MODELO / "sdd/padroes-tecnicos.md").read_bytes())
            self.assertIn("aviso: sdd/padroes-tecnicos.md não existia e foi criado do modelo do kit",
                          saida.stdout)

    def test_novo_imprime_o_comando_de_instalacao(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._ferramenta("novo", f"{tmp}/proj")
        self.assertIn("claude plugin install sdd@trilha-ai --scope project",
                      saida.stdout.split("próximos passos", 1)[1])

    def test_atualizar_respeita_os_padroes_apagados(self) -> None:
        """Desde a 2.2, o projeto sem os padrões escolheu ficar sem eles."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            (pasta / "sdd/padroes-tecnicos.md").unlink()
            self._commit_tudo(pasta, "sem os padrões")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertFalse((pasta / "sdd/padroes-tecnicos.md").exists())
            self.assertNotIn("padroes-tecnicos.md", saida.stdout)

    def test_atualizar_so_regera_a_pagina_que_existe(self) -> None:
        """A página nasce ao fechar uma etapa; a atualização não a cria vazia."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            pagina = pasta / "sdd/documentacao.html"
            self.assertEqual(self._ferramenta("atualizar", str(pasta)).returncode, 0)
            self.assertFalse(pagina.exists())
            pagina.write_text("a página de antes\n", encoding="utf-8")
            self._commit_tudo(pasta, "a página")
            self.assertEqual(self._ferramenta("atualizar", str(pasta)).returncode, 0)
            self.assertNotEqual(pagina.read_text(encoding="utf-8"), "a página de antes\n")

    def _atualizar_com_claude(self, lista: list) -> subprocess.CompletedProcess:
        """O kit.py atualizar num projeto novo, com um `claude` falso que lista os plugins dados (o
        "<projeto>" da lista vira a pasta do projeto)."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            falsos = Path(tmp) / "falsos"
            falsos.mkdir()
            texto = json.dumps(lista).replace("<projeto>", str(pasta.resolve()))
            _claude_falso(falsos, f"printf '%s' '{texto}'")
            return self._ferramenta("atualizar", str(pasta),
                                    env={**os.environ, "PATH": f"{falsos}:{os.environ['PATH']}"})

    def test_atualizar_cita_o_install_so_quando_falta_no_projeto(self) -> None:
        """Quem diz a instalação que falta é a conferência, que roda também nas outras máquinas."""
        instalar = "claude plugin install sdd@trilha-ai --scope project"
        do_usuario = {"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "user", "enabled": True}
        saida = self._atualizar_com_claude([do_usuario])
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertIn(instalar, saida.stdout)
        do_projeto = {**do_usuario, "scope": "project", "projectPath": "<projeto>"}
        saida = self._atualizar_com_claude([do_usuario, do_projeto])
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertNotIn(instalar, saida.stdout)

    def test_atualizar_recusa_o_settings_que_nao_entende_sem_mudar_nada(self) -> None:
        for texto in ('{"enabledPlugins": null}', '{"hooks": {"PreToolUse": {}}}', "[]", "{"):
            with tempfile.TemporaryDirectory() as tmp:
                pasta = self._projeto_velho(tmp)
                (pasta / ".claude/settings.json").write_text(texto, encoding="utf-8")
                self._commit_tudo(pasta, "settings estranho")
                saida = self._ferramenta("atualizar", str(pasta))
                self.assertEqual(saida.returncode, 1, texto)
                self.assertIn("recusado: .claude/settings.json", saida.stderr, texto)
                status = subprocess.run(["git", "status", "--porcelain"], cwd=pasta,
                                        capture_output=True, text=True, check=True).stdout
                self.assertEqual(status, "", texto)

    def test_soma_traz_toda_chave_do_modelo_sem_trocar_as_do_projeto(self) -> None:
        """A soma lê o modelo inteiro: uma chave nova nele chega aos projetos na atualização."""
        atual = {"enabledPlugins": {"sdd@trilha-ai": False}, "lista": [{"a": 1, "b": 2}]}
        modelo = {"enabledPlugins": {"sdd@trilha-ai": True, "outro@x": True},
                  "permissions": {"allow": ["Bash(ls:*)"]}, "lista": [{"a": 1}, {"c": 3}]}
        FERRAMENTA._somar(atual, modelo)
        self.assertEqual(atual, {"enabledPlugins": {"sdd@trilha-ai": False, "outro@x": True},
                                 "permissions": {"allow": ["Bash(ls:*)"]},
                                 "lista": [{"a": 1, "b": 2}, {"c": 3}]})
        modelo["permissions"]["allow"].append("mudou")
        self.assertEqual(atual["permissions"], {"allow": ["Bash(ls:*)"]})  # cópia, não o do modelo

    def test_trava_de_outra_versao_troca_pela_do_modelo(self) -> None:
        """A trilha/guarda.py chamada de outro jeito sai; o gancho próprio do grupo fica."""
        modelo = FERRAMENTA._modelo_do_settings()
        proprio = {"type": "command", "command": "echo do projeto"}
        atual = {"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "python3 trilha/guarda.py"},
                                          proprio]},
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "python3 scripts/guarda.py"}]},
        ]}}
        FERRAMENTA._sem_guardas_antigas(atual, modelo)
        FERRAMENTA._somar(atual, modelo)
        grupos = atual["hooks"]["PreToolUse"]
        self.assertEqual(grupos, [{"matcher": "Bash", "hooks": [proprio]},
                                  *modelo["hooks"]["PreToolUse"]])

    def test_trava_do_modelo_num_grupo_do_projeto_nao_se_repete(self) -> None:
        modelo = FERRAMENTA._modelo_do_settings()
        grupo = json.loads(json.dumps(modelo["hooks"]["PreToolUse"][0]))
        grupo["hooks"].append({"type": "command", "command": "echo do projeto"})
        atual = {"hooks": {"PreToolUse": [grupo]}}
        FERRAMENTA._sem_guardas_antigas(atual, modelo)
        FERRAMENTA._somar(atual, modelo)
        self.assertEqual(atual["hooks"]["PreToolUse"], [grupo])

    def test_comando_de_instalacao_igual_no_kit_e_na_conferencia(self) -> None:
        """O confere_metodo.py roda no projeto, sem o kit.py: cada um tem a sua constante."""
        metodo = (MODELO / "trilha/confere_metodo.py").read_text(encoding="utf-8")
        self.assertEqual(FERRAMENTA.INSTALAR_NO_PROJETO, "claude plugin install sdd@trilha-ai --scope project")
        self.assertIn(f'f"`claude plugin install {{PLUGIN_SDD}} --scope project`"', metodo)

    def _ferramenta(self, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", str(RAIZ / "ferramentas/kit.py"), *args],
            capture_output=True, text=True, check=False, env=env,
        )

    def _projeto_velho(self, tmp: str) -> Path:
        """Um projeto feito pela ferramenta, com dois commits: o kit e o comum voltado à 1.19."""
        pasta = Path(tmp) / "proj"
        self.assertEqual(self._ferramenta("novo", str(pasta)).returncode, 0)
        env = {**os.environ, **GIT_TESTE}
        comum = pasta / "trilha/CLAUDE-comum.md"
        comum.write_text(re.sub(r"^Versão [\d.]+,", "Versão 1.19,", comum.read_text(encoding="utf-8"),
                                flags=re.M), encoding="utf-8")
        (pasta / ".github/workflows/verificacao.yml").write_text("# a parte da stack, preenchida\n")
        subprocess.run(["git", "add", "-A"], cwd=pasta, check=True)
        subprocess.run(["git", "commit", "-qm", "kit"], cwd=pasta, check=True, env=env)
        return pasta

    # A pasta trilha/ (change 02): as conferências, a verificação fixa e a ferramenta.

    def _projeto_novo(self, tmp: str) -> Path:
        """Um projeto feito pela ferramenta atual, com o primeiro commit."""
        pasta = Path(tmp) / "proj"
        self.assertEqual(self._ferramenta("novo", str(pasta)).returncode, 0)
        subprocess.run(["git", "add", "-A"], cwd=pasta, check=True)
        subprocess.run(["git", "commit", "-qm", "kit"], cwd=pasta, check=True, env={**os.environ, **GIT_TESTE})
        return pasta

    def _projeto_da_1_30(self, tmp: str) -> Path:
        """Um projeto feito pela ferramenta da 1.30 (a do layout antigo), lida da tag, com um commit."""
        kit = Path(tmp) / "kit-1.30"
        kit.mkdir()
        arquivo = subprocess.run(["git", "-C", str(RAIZ), "archive", "v1.30"], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", str(kit)], input=arquivo.stdout, check=True)
        pasta = Path(tmp) / "proj"
        subprocess.run([sys.executable, "-I", str(kit / "ferramentas/kit.py"), "novo", str(pasta)],
                       capture_output=True, check=True)
        self.assertTrue((pasta / "scripts/confere_regras.py").is_file())
        self._commit_tudo(pasta, "kit 1.30")
        return pasta

    def _commit_tudo(self, pasta: Path, mensagem: str) -> None:
        env = {**os.environ, **GIT_TESTE}
        subprocess.run(["git", "add", "-A"], cwd=pasta, check=True)
        subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "commit", "-qm", mensagem], cwd=pasta,
                       check=True, env=env)

    def _regras(self, pasta: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-I", str(pasta / "trilha/confere_regras.py"), str(pasta),
                               "--fonte", str(RAIZ)], capture_output=True, text=True, check=False)

    def test_regras_aprovam_o_projeto_com_a_pasta_trilha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._regras(self._projeto_novo(tmp))
        self.assertEqual(saida.returncode, 0, saida.stderr)

    def test_regras_reprovam_a_importacao_antiga(self) -> None:
        erro = self._verifica_com_defeito("CLAUDE.md", "@trilha/CLAUDE-comum.md", "@CLAUDE-comum.md")
        self.assertIn("falta a linha @trilha/CLAUDE-comum.md", erro)

    def test_copia_da_pasta_trilha_igual_passa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            (pasta / "trilha/__pycache__").mkdir()
            (pasta / "trilha/__pycache__/confere_regras.cpython-312.pyc").write_bytes(b"cache")
            saida = self._regras(pasta)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertNotIn("trilha/", saida.stderr.replace("trilha/hooks", ""))

    def test_copia_reprova_a_trava_editada(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            guarda = pasta / "trilha/guarda.py"
            guarda.write_text(guarda.read_text(encoding="utf-8") + "\n# afrouxada\n", encoding="utf-8")
            saida = self._regras(pasta)
        self.assertEqual(saida.returncode, 1)
        self.assertIn("trilha/guarda.py difere do kit", saida.stderr)
        self.assertIn("kit.py atualizar", saida.stderr)  # nunca editar a pasta (C02)

    def _kit_falso(self, tmp: str, com_tag: bool = True, versao: str = "9.9") -> Path:
        """Um kit com a modelo/trilha/ de agora, commitada e com a tag da versão dela (ou sem tag
        nenhuma), cuja cópia de trabalho já está noutra versão (a 9.9, à frente): o kit ao lado de
        um projeto atrasado (change 06). Sem os ganchos e a assinatura da configuração global."""
        kit = Path(tmp) / "kit"
        shutil.copytree(MODELO / "trilha", kit / "modelo/trilha",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (kit / "modelo/openspec").mkdir(parents=True)
        shutil.copy(MODELO / "openspec/config.yaml", kit / "modelo/openspec/config.yaml")
        env = {**os.environ, **GIT_TESTE}
        git = ["git", "-C", str(kit), "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
               "-c", "tag.gpgsign=false"]
        for comando in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "kit"]):
            subprocess.run([*git, *comando], check=True, env=env)
        if com_tag:
            atual = FERRAMENTA._versao(MODELO / "trilha/CLAUDE-comum.md")
            subprocess.run([*git, "tag", f"v{atual}"], check=True, env=env)
        comum = kit / "modelo/trilha/CLAUDE-comum.md"
        texto = re.sub(r"^Versão \d+\.\d+,", f"Versão {versao},", comum.read_text(encoding="utf-8"),
                       flags=re.M)
        comum.write_text(texto, encoding="utf-8")
        return kit

    def _regras_no_kit(self, pasta: Path, kit: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-I", str(pasta / "trilha/confere_regras.py"), str(pasta),
                               "--fonte", str(kit)], capture_output=True, text=True, check=False)

    def test_kit_mais_novo_compara_pela_tag_e_avisa(self) -> None:
        versao = FERRAMENTA._versao(MODELO / "trilha/CLAUDE-comum.md")
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._regras_no_kit(self._projeto_novo(tmp), self._kit_falso(tmp))
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = next((l for l in saida.stderr.splitlines() if "9.9" in l), "")
        self.assertIn(versao, aviso, saida.stderr)
        self.assertIn("kit.py atualizar", aviso)

    def test_kit_mais_novo_reprova_a_copia_divergente_da_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            guarda = pasta / "trilha/guarda.py"
            guarda.write_text(guarda.read_text(encoding="utf-8") + "\n# afrouxada\n", encoding="utf-8")
            saida = self._regras_no_kit(pasta, self._kit_falso(tmp))
        self.assertEqual(saida.returncode, 1)
        self.assertIn("trilha/guarda.py difere do kit", saida.stderr)
        # Comparado com a tag, o comum é igual; com a cópia de trabalho (na 9.9), diferiria.
        self.assertNotIn("trilha/CLAUDE-comum.md difere", saida.stderr)

    def test_kit_atras_do_projeto_avisa_sem_mandar_atualizar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._regras_no_kit(self._projeto_novo(tmp), self._kit_falso(tmp, versao="1.0"))
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = next((l for l in saida.stderr.splitlines() if "1.0" in l), "")
        self.assertIn("atualize o kit ao lado", aviso, saida.stderr)
        self.assertNotIn("kit.py atualizar", aviso)  # o atualizar rebaixaria o projeto

    def test_versao_que_o_kit_nao_tem_reprova(self) -> None:
        """Revisão de código, ponto 1: a linha Versão trocada à mão não desliga a comparação."""
        for inventada in ("1.99", "9.98"):
            with tempfile.TemporaryDirectory() as tmp:
                pasta = self._projeto_novo(tmp)
                comum = pasta / "trilha/CLAUDE-comum.md"
                comum.write_text(re.sub(r"^Versão \d+\.\d+,", f"Versão {inventada},",
                                        comum.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
                saida = self._regras_no_kit(pasta, self._kit_falso(tmp))
            self.assertEqual(saida.returncode, 1, inventada)
            self.assertIn(f"a versão {inventada} do projeto não existe no kit", saida.stderr)

    def test_comum_sem_versao_compara_com_a_copia_do_kit(self) -> None:
        """Revisão de código, ponto 4: sem a linha Versão, as outras diferenças não se escondem."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            comum = pasta / "trilha/CLAUDE-comum.md"
            comum.write_text(comum.read_text(encoding="utf-8").replace("Versão ", "Versao ", 1),
                             encoding="utf-8")
            guarda = pasta / "trilha/guarda.py"
            guarda.write_text(guarda.read_text(encoding="utf-8") + "\n# afrouxada\n", encoding="utf-8")
            saida = self._regras_no_kit(pasta, self._kit_falso(tmp))
        self.assertEqual(saida.returncode, 1)
        self.assertIn("trilha/guarda.py difere do kit", saida.stderr)

    # As regras por artefato do openspec/config.yaml iguais às do kit (change 09).

    def _regras_com_config(self, troca: tuple[str, str] | None) -> subprocess.CompletedProcess[str]:
        """A conferência das regras, com --fonte, de um projeto novo com o config.yaml trocado."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            config = pasta / "openspec/config.yaml"
            if troca is not None:
                texto = config.read_text(encoding="utf-8")
                self.assertIn(troca[0], texto)
                config.write_text(texto.replace(troca[0], troca[1], 1), encoding="utf-8")
            return self._regras(pasta)

    def test_config_com_as_regras_do_kit_passa(self) -> None:
        saida = self._regras_com_config(None)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertFalse([l for l in saida.stderr.splitlines() if l.startswith("FALHA") and "config.yaml" in l])

    def test_config_com_regra_propria_reprova(self) -> None:
        saida = self._regras_com_config(("  proposal:\n", "  proposal:\n    - Uma regra própria.\n"))
        self.assertEqual(saida.returncode, 1, saida.stderr)
        falha = next((l for l in saida.stderr.splitlines() if l.startswith("FALHA") and "rules:" in l), "")
        self.assertIn("openspec/config.yaml", falha, saida.stderr)

    def test_config_sem_linha_do_operations_reprova(self) -> None:
        modelo = (MODELO / "openspec/config.yaml").read_text(encoding="utf-8")
        linha = next(l for l in modelo.splitlines() if "O design.md que o propose dispensou" in l)
        saida = self._regras_com_config((linha + "\n", ""))
        self.assertEqual(saida.returncode, 1, saida.stderr)
        self.assertIn("- 'O design.md que o propose dispensou", saida.stderr)

    def test_config_com_acrescimos_proprios_passa(self) -> None:
        modelo = (MODELO / "openspec/config.yaml").read_text(encoding="utf-8")
        linha = next(l for l in modelo.splitlines() if "O design.md que o propose dispensou" in l)
        propria = "      - 'Um passo próprio do archive deste projeto.'"
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            config = pasta / "openspec/config.yaml"
            texto = config.read_text(encoding="utf-8").replace(linha, f"{linha}\n{propria}")
            config.write_text(texto + "githubCopilot:\n  cloudAgent: true\n", encoding="utf-8")
            saida = self._regras(pasta)
        self.assertEqual(saida.returncode, 0, saida.stderr)

    def test_config_da_versao_anterior_passa(self) -> None:
        """Com o kit à frente, as regras da tag da versão do projeto valem; as da cópia de trabalho, não."""
        nova = "  proposal:\n    - Uma regra nova do kit.\n"
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            kit = self._kit_falso(tmp)
            config_do_kit = kit / "modelo/openspec/config.yaml"
            config_do_kit.write_text(config_do_kit.read_text(encoding="utf-8").replace("  proposal:\n", nova, 1),
                                     encoding="utf-8")
            com_as_da_tag = self._regras_no_kit(pasta, kit)
            shutil.copy(config_do_kit, pasta / "openspec/config.yaml")
            com_as_novas = self._regras_no_kit(pasta, kit)
        self.assertEqual(com_as_da_tag.returncode, 0, com_as_da_tag.stderr)
        self.assertEqual(com_as_novas.returncode, 1, com_as_novas.stderr)
        self.assertIn("rules:", com_as_novas.stderr)

    def test_projeto_sem_config_nao_reprova_pelo_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            (pasta / "openspec/config.yaml").unlink()
            saida = self._regras(pasta)
        self.assertEqual(saida.returncode, 0, saida.stderr)

    def test_versao_sem_tag_no_kit_avisa_sem_comparar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._regras_no_kit(self._projeto_novo(tmp), self._kit_falso(tmp, com_tag=False))
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("não foi comparada", saida.stderr)

    def _regras_com_settings(self, tmp: str, **arquivos: dict) -> str:
        """O stderr da conferência num projeto novo com estes settings (projeto=, local=)."""
        pasta = self._projeto_novo(tmp)
        for qual, extra in arquivos.items():
            nome = {"projeto": "settings.json", "local": "settings.local.json"}[qual]
            settings = pasta / ".claude" / nome
            atual = json.loads(settings.read_text(encoding="utf-8")) if settings.is_file() else {}
            settings.write_text(json.dumps({**atual, **extra}), encoding="utf-8")
        saida = self._regras(pasta)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        return saida.stderr

    def test_disable_all_hooks_local_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            erro = self._regras_com_settings(tmp, local={"disableAllHooks": True})
        aviso = next((l for l in erro.splitlines() if "disableAllHooks" in l), "")
        self.assertIn(".claude/settings.local.json", aviso, erro)
        self.assertIn("trava do Claude Code desligada", aviso)

    def test_disable_all_hooks_do_projeto_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            erro = self._regras_com_settings(tmp, projeto={"disableAllHooks": True})
        aviso = next((l for l in erro.splitlines() if "disableAllHooks" in l), "")
        self.assertIn(".claude/settings.json", aviso, erro)

    def test_disable_all_hooks_religado_pelo_local_nao_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            erro = self._regras_com_settings(tmp, projeto={"disableAllHooks": True},
                                             local={"disableAllHooks": False})
        self.assertNotIn("disableAllHooks", erro)

    def test_projeto_novo_sem_aviso_de_trava(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            erro = self._regras_com_settings(tmp)
        self.assertNotIn("trava", erro)

    def test_copia_reprova_arquivo_faltando_ou_a_mais(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            (pasta / "trilha/verifica.sh").unlink()
            (pasta / "trilha/meu.py").write_text("print('do projeto')\n", encoding="utf-8")
            saida = self._regras(pasta)
        self.assertEqual(saida.returncode, 1)
        self.assertIn("trilha/verifica.sh falta", saida.stderr)
        self.assertIn("trilha/meu.py não é do kit", saida.stderr)

    def _verifica(self, pasta: Path, *args: str, path: str | None = None,
                  check_sh: bool = False, ci: bool = False) -> subprocess.CompletedProcess[str]:
        comando = ["bash", "scripts/check.sh"] if check_sh else ["bash", "trilha/verifica.sh", *args]
        env = {k: v for k, v in os.environ.items() if k != "CI"}  # o CI do kit define CI
        env = {**env, "TRILHA_AI": str(RAIZ), **({"PATH": path} if path else {}), **({"CI": "true"} if ci else {})}
        return subprocess.run(comando, cwd=pasta, env=env, capture_output=True, text=True, check=False)

    def test_verifica_aprova_o_projeto_novo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            saida = self._verifica(pasta, check_sh=True)
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertIn("ok: CLAUDE.md, trilha/ e ANDAMENTO.md conferidos", saida.stdout)
        self.assertIn("ok: decomposição, TDD e ANDAMENTO.md conferidos", saida.stdout)

    def test_verifica_repassa_o_vizinho(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            andamento = pasta / "ANDAMENTO.md"
            andamento.write_text(andamento.read_text(encoding="utf-8") + "outro\n", encoding="utf-8")
            saida = self._verifica(pasta, "--vizinho", "outro")
        self.assertNotEqual(saida.returncode, 0)
        self.assertIn("cita outro repositório: outro", saida.stderr)

    def test_verifica_reprova_quando_o_openspec_reprova(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            falsos = Path(tmp) / "falsos"
            falsos.mkdir()
            openspec = falsos / "openspec"
            openspec.write_text("#!/bin/sh\necho 'requisito sem SHALL' >&2\nexit 1\n", encoding="utf-8")
            openspec.chmod(0o755)
            saida = self._verifica(pasta, path=f"{falsos}:{os.environ['PATH']}")
        self.assertNotEqual(saida.returncode, 0)
        self.assertIn("requisito sem SHALL", saida.stderr)

    def test_verifica_sem_openspec_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            # Só as ferramentas que a verificação usa: o openspec existe em mais de uma pasta do PATH.
            sem_openspec = Path(tmp) / "sem-openspec"
            sem_openspec.mkdir()
            for programa in ("bash", "python3", "git", "dirname", "readlink"):
                (sem_openspec / programa).symlink_to(shutil.which(programa))
            saida = self._verifica(pasta, path=str(sem_openspec), ci=False)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("o openspec não está instalado", saida.stderr)

    def test_verifica_sem_openspec_no_ci_falha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            sem_openspec = Path(tmp) / "sem-openspec"
            sem_openspec.mkdir()
            for programa in ("bash", "python3", "git", "dirname", "readlink"):
                (sem_openspec / programa).symlink_to(shutil.which(programa))
            saida = self._verifica(pasta, path=str(sem_openspec), ci=True)
        self.assertNotEqual(saida.returncode, 0)
        self.assertIn("o openspec falta", saida.stderr)

    def _novo_com_openspec(self, perfil: dict | None) -> subprocess.CompletedProcess:
        """O kit.py novo com um `openspec` falso que responde o perfil dado ao `config list --json`;
        com None, sem o openspec no PATH."""
        with tempfile.TemporaryDirectory() as tmp:
            falsos = Path(tmp) / "falsos"
            falsos.mkdir()
            (falsos / "git").symlink_to(shutil.which("git"))  # o PATH tem só esta pasta
            if perfil is not None:
                falso = falsos / "openspec"
                falso.write_text(f"#!/bin/sh\nprintf '%s' '{json.dumps(perfil)}'\n", encoding="utf-8")
                falso.chmod(0o755)
            env = {**os.environ, "PATH": str(falsos)}
            return subprocess.run([sys.executable, "-I", str(RAIZ / "ferramentas/kit.py"), "novo", f"{tmp}/novo"],
                                  capture_output=True, text=True, check=False, env=env)

    def test_novo_avisa_o_perfil_sem_o_verify(self) -> None:
        """F32: no perfil core o OpenSpec ignora a lista e não traz o verify; no custom, só se a lista o tiver."""
        for perfil in ({"profile": "core", "workflows": ["propose", "verify"]},
                       {"profile": "custom", "workflows": ["propose", "apply", "archive"]}):
            saida = self._novo_com_openspec(perfil)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            aviso = [l for l in saida.stdout.splitlines() if l.startswith("aviso: o perfil do OpenSpec")]
            self.assertEqual(len(aviso), 1, (perfil, saida.stdout))
            self.assertIn("verify", aviso[0])
            self.assertIn("openspec config profile", aviso[0])

    def test_novo_com_o_verify_no_perfil_nao_avisa(self) -> None:
        saida = self._novo_com_openspec({"profile": "custom", "workflows": ["propose", "apply", "verify", "archive"]})
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertNotIn("aviso:", saida.stdout)
        passos = saida.stdout.split("próximos passos", 1)[1]
        self.assertIn("openspec config profile", passos)

    def test_novo_cita_o_codegraph_como_opcional(self) -> None:
        """F36: o CodeGraph é opcional no método; o item dele diz isso e fica fora do openspec."""
        saida = self._novo_com_openspec(None)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        passos = saida.stdout.split("próximos passos", 1)[1].split("\naviso:", 1)[0]
        # Os passos vêm com 2 espaços e os itens do passo 4 com 5; a continuação de uma linha, com 7.
        itens = re.split(r"\n(?:  \d+\.|     -) ", passos)
        openspec = [i for i in itens if "openspec init" in i]
        self.assertEqual(len(openspec), 1, itens)
        self.assertNotIn("codegraph", openspec[0])
        codegraph = [i for i in itens if "codegraph init" in i]
        self.assertEqual(len(codegraph), 1, itens)
        self.assertIn("se usar o CodeGraph", codegraph[0])
        self.assertIn("em cada clone", codegraph[0])

    def test_novo_sem_openspec_avisa(self) -> None:
        saida = self._novo_com_openspec(None)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("aviso: o openspec não está instalado", saida.stdout)

    def test_novo_cria_a_pasta_trilha_e_liga_as_travas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            kit = {str(a.relative_to(MODELO)) for a in (MODELO / "trilha").rglob("*")
                   if a.is_file() and "__pycache__" not in a.parts}
            nosso = {str(a.relative_to(pasta)) for a in (pasta / "trilha").rglob("*") if a.is_file()}
            self.assertEqual(nosso, kit)
            for nome in kit:
                self.assertEqual((pasta / nome).read_bytes(), (MODELO / nome).read_bytes(), nome)
            ligado = subprocess.run(["git", "config", "core.hooksPath"], cwd=pasta, capture_output=True,
                                    text=True).stdout.strip()
            self.assertEqual(ligado, "trilha/hooks")
            self.assertIn("trilha/guarda.py", (pasta / ".claude/settings.json").read_text(encoding="utf-8"))
            self.assertIn("@trilha/CLAUDE-comum.md", (pasta / "CLAUDE.md").read_text(encoding="utf-8").splitlines())
            self.assertEqual(self._verifica(pasta, check_sh=True).returncode, 0)

    def test_atualizar_apaga_da_trilha_o_que_o_kit_tirou(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            (pasta / "trilha/velho.py").write_text("# o kit tirou\n", encoding="utf-8")
            self._commit_tudo(pasta, "um arquivo que o kit tirou")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertFalse((pasta / "trilha/velho.py").exists())
            self.assertEqual(self._regras(pasta).returncode, 0)

    def test_migra_o_projeto_antigo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_da_1_30(tmp)
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            for antigo in FERRAMENTA.ANTES_DA_2_0.values():
                self.assertFalse((pasta / antigo).exists(), antigo)
            self.assertIn("@trilha/CLAUDE-comum.md", (pasta / "CLAUDE.md").read_text(encoding="utf-8").splitlines())
            ligado = subprocess.run(["git", "config", "core.hooksPath"], cwd=pasta, capture_output=True,
                                    text=True).stdout.strip()
            self.assertEqual(ligado, "trilha/hooks")
            ganchos = json.dumps(json.loads((pasta / ".claude/settings.json").read_text())["hooks"])
            self.assertEqual(ganchos.count("guarda.py"), 1)
            self.assertIn("trilha/guarda.py", ganchos)
            self.assertIn("bash trilha/verifica.sh", (pasta / "scripts/check.sh").read_text(encoding="utf-8"))
            self.assertEqual(self._regras(pasta).returncode, 0)
            self.assertEqual(self._confere_metodo(pasta).returncode, 0)

    def test_migracao_preserva_e_avisa_o_hook_proprio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_da_1_30(tmp)
            proprio = pasta / ".githooks/commit-msg"
            proprio.write_text("#!/bin/sh\necho o commit-msg do projeto\n", encoding="utf-8")
            self._commit_tudo(pasta, "um hook do projeto")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertEqual(proprio.read_text(encoding="utf-8"), "#!/bin/sh\necho o commit-msg do projeto\n")
            self.assertFalse((pasta / ".githooks/pre-commit").exists())
            self.assertIn(".githooks/commit-msg não roda mais", saida.stdout)

    def test_migracao_preserva_o_pre_push_sem_aviso(self) -> None:
        """O .githooks/pre-push roda pelo trilha/hooks/pre-push (change 08): nada a avisar."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_da_1_30(tmp)
            proprio = pasta / ".githooks/pre-push"
            proprio.write_text("#!/bin/sh\necho o pre-push do projeto\n", encoding="utf-8")
            proprio.chmod(0o755)
            self._commit_tudo(pasta, "um hook do projeto")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertEqual(proprio.read_text(encoding="utf-8"), "#!/bin/sh\necho o pre-push do projeto\n")
            remoto = Path(tmp) / "remoto.git"
            subprocess.run(["git", "init", "-q", "--bare", str(remoto)], check=True)
            subprocess.run(["git", "remote", "add", "origem", str(remoto)], cwd=pasta, check=True)
            envio = self._enviar(pasta)
            self.assertEqual(envio.returncode, 0, envio.stderr)
        self.assertNotIn(".githooks/pre-push não roda mais", saida.stdout)
        self.assertIn("o pre-push do projeto", envio.stdout + envio.stderr)

    def test_migracao_avisa_o_pre_push_que_nao_roda(self) -> None:
        """O pre-push próprio que não pode rodar recusaria todo envio: a migração avisa antes."""
        for caso in ("sem permissão", "link quebrado"):
            with self.subTest(caso), tempfile.TemporaryDirectory() as tmp:
                pasta = self._projeto_da_1_30(tmp)
                proprio = pasta / ".githooks/pre-push"
                if caso == "sem permissão":
                    proprio.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                    proprio.chmod(0o644)
                else:
                    proprio.symlink_to("nao-existe")
                self._commit_tudo(pasta, "um hook do projeto")
                saida = self._ferramenta("atualizar", str(pasta))
                self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
                self.assertTrue(proprio.is_symlink() or proprio.is_file())
                aviso = next((l for l in saida.stdout.splitlines() if ".githooks/pre-push" in l), "")
                self.assertIn("o envio será recusado", aviso, saida.stdout)

    def test_migracao_troca_a_parte_fixa_com_vizinhos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_da_1_30(tmp)
            check = pasta / "scripts/check.sh"
            texto = check.read_text(encoding="utf-8").replace(
                "python3 -I scripts/confere_metodo.py\n",
                "python3 -I scripts/confere_metodo.py --vizinho trilha-ai \\\n  --vizinho outro\n")
            check.write_text(texto + "echo a-stack-do-projeto\n", encoding="utf-8")
            self._commit_tudo(pasta, "vizinhos e a stack")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertNotIn("a parte fixa de scripts/check.sh difere", saida.stdout)
            migrado = check.read_text(encoding="utf-8")
        self.assertIn("bash trilha/verifica.sh --vizinho trilha-ai \\\n  --vizinho outro\n", migrado)
        self.assertNotIn("FONTE=", migrado)
        self.assertNotIn("scripts/confere_", migrado)
        self.assertTrue(migrado.endswith("echo a-stack-do-projeto\n"))

    def test_migracao_avisa_a_parte_fixa_alterada(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_da_1_30(tmp)
            check = pasta / "scripts/check.sh"
            texto = check.read_text(encoding="utf-8").replace("não foi comparada com o kit", "ficou sem comparar")
            check.write_text(texto, encoding="utf-8")
            self._commit_tudo(pasta, "parte fixa mexida")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(check.read_text(encoding="utf-8"), texto)
        self.assertIn("a parte fixa do scripts/check.sh não é a do kit", saida.stdout)
        self.assertEqual(saida.returncode, 1, saida.stdout)
        self.assertNotIn("commit sugerido", saida.stdout)

    def test_atualizar_recusa_a_pasta_trilha_de_outra_coisa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_da_1_30(tmp)
            (pasta / "trilha").mkdir()
            (pasta / "trilha/__init__.py").write_text("# um pacote do projeto\n", encoding="utf-8")
            self._commit_tudo(pasta, "um pacote chamado trilha")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 1)
            self.assertIn("trilha/ já existe e não é a do método", saida.stderr)
            self.assertTrue((pasta / "trilha/__init__.py").is_file())
            self.assertTrue((pasta / "scripts/confere_regras.py").is_file())  # nada foi mexido

    def test_aviso_da_parte_fixa_preciso(self) -> None:
        presente = FERRAMENTA._presente
        self.assertTrue(presente("bash trilha/verifica.sh", {"bash trilha/verifica.sh --vizinho trilha-ai \\"}))
        self.assertTrue(presente("fi", {"fi"}))
        self.assertFalse(presente("fi", {"find ."}))
        self.assertFalse(presente("run: |", {"run: |x"}))
        # Change 09: a chamada por uma função do projeto, depois de um espaço.
        self.assertTrue(presente("bash trilha/verifica.sh",
                                 {'etapa "regras" bash trilha/verifica.sh --vizinho trilha-ai'}))
        self.assertTrue(presente("bash trilha/verifica.sh", {'etapa "regras" bash trilha/verifica.sh'}))
        self.assertFalse(presente("bash trilha/verifica.sh", {"xbash trilha/verifica.sh"}))
        self.assertFalse(presente("bash trilha/verifica.sh", {"bash trilha/verifica.sh2"}))

    def test_migracao_parcial_troca_a_importacao(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_da_1_30(tmp)
            for antigo in FERRAMENTA.ANTES_DA_2_0.values():
                (pasta / antigo).unlink(missing_ok=True)
            claude = pasta / "CLAUDE.md"
            claude.write_text(claude.read_text(encoding="utf-8").replace("@CLAUDE-comum.md\n", "@CLAUDE-comum.md  \n"),
                              encoding="utf-8")
            self._commit_tudo(pasta, "cópias apagadas à mão")
            self._ferramenta("atualizar", str(pasta))
            linhas = claude.read_text(encoding="utf-8").splitlines()
        self.assertIn("@trilha/CLAUDE-comum.md", linhas)
        self.assertFalse(any(l.startswith("@CLAUDE-comum.md") for l in linhas))

    def test_copia_reprova_a_permissao_perdida(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            (pasta / "trilha/hooks/pre-commit").chmod(0o644)
            saida = self._regras(pasta)
        self.assertEqual(saida.returncode, 1)
        self.assertIn("trilha/hooks/pre-commit perdeu a permissão de execução", saida.stderr)

    # O envio pelo hook próprio do projeto (change 08).

    def _com_remoto(self, tmp: str) -> tuple[Path, Path]:
        """Um projeto novo e um remoto vazio, ligado a ele como `origem`."""
        pasta, remoto = self._projeto_novo(tmp), Path(tmp) / "remoto.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remoto)], check=True)
        subprocess.run(["git", "remote", "add", "origem", str(remoto)], cwd=pasta, check=True)
        return pasta, remoto

    def _hook_proprio(self, pasta: Path, corpo: str, executavel: bool = True) -> None:
        hook = pasta / ".githooks/pre-push"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text(f"#!/bin/sh\n{corpo}\n", encoding="utf-8")
        hook.chmod(0o755 if executavel else 0o644)

    def _enviar(self, pasta: Path) -> subprocess.CompletedProcess[str]:
        """O envio com o destino explícito, sem depender do push.default da máquina."""
        return subprocess.run(["git", "push", "-q", "origem", "HEAD:refs/heads/main"], cwd=pasta,
                              capture_output=True, text=True, check=False)

    def _main_do_remoto(self, remoto: Path) -> str:
        return subprocess.run(["git", "-C", str(remoto), "rev-parse", "-q", "--verify", "main"],
                              capture_output=True, text=True, check=False).stdout.strip()

    def _head(self, pasta: Path) -> str:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=pasta, capture_output=True, text=True,
                              check=True).stdout.strip()

    def test_pre_push_repassa_ao_hook_proprio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta, remoto = self._com_remoto(tmp)
            registro = Path(tmp) / "registro"
            self._hook_proprio(pasta, f"printf '%s\\n' \"$@\" > {shlex.quote(str(registro))}; cat >> {shlex.quote(str(registro))}; exit 0")
            saida = self._enviar(pasta)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            head = self._head(pasta)
            self.assertEqual(self._main_do_remoto(remoto), head)
            linhas = registro.read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[:2], ["origem", str(remoto)])
        # A linha da referência: <ref local> <commit> <ref remota> <commit remoto>.
        self.assertEqual(linhas[2].split()[:3], ["HEAD", head, "refs/heads/main"])

    def test_pre_push_recusa_quando_o_hook_proprio_reprova(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta, remoto = self._com_remoto(tmp)
            self._hook_proprio(pasta, "exit 1")
            saida = self._enviar(pasta)
            self.assertNotEqual(saida.returncode, 0)
            self.assertEqual(self._main_do_remoto(remoto), "")

    def test_pre_push_repassa_o_codigo_e_a_entrada(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            registro = Path(tmp) / "registro"
            self._hook_proprio(pasta, f"printf '%s\\n' \"$@\" > {shlex.quote(str(registro))}; cat >> {shlex.quote(str(registro))}; exit 3")
            saida = subprocess.run([str(pasta / "trilha/hooks/pre-push"), "um remoto", "dois"],
                                   cwd=pasta, input="a linha da entrada\n", capture_output=True,
                                   text=True, check=False)
            self.assertEqual(saida.returncode, 3, saida.stderr)
            self.assertEqual(registro.read_text(encoding="utf-8"), "um remoto\ndois\na linha da entrada\n")

    def test_pre_push_sem_hook_proprio_envia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta, remoto = self._com_remoto(tmp)
            saida = self._enviar(pasta)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertEqual(self._main_do_remoto(remoto), self._head(pasta))

    def test_pre_push_recusa_o_hook_proprio_nao_executavel(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta, remoto = self._com_remoto(tmp)
            self._hook_proprio(pasta, "exit 0", executavel=False)
            saida = self._enviar(pasta)
            self.assertNotEqual(saida.returncode, 0)
            self.assertEqual(self._main_do_remoto(remoto), "")
        self.assertIn(".githooks/pre-push", saida.stderr)
        self.assertIn("permissão de execução", saida.stderr)

    def test_pre_push_recusa_o_link_quebrado(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta, remoto = self._com_remoto(tmp)
            (pasta / ".githooks").mkdir()
            (pasta / ".githooks/pre-push").symlink_to("nao-existe")
            saida = self._enviar(pasta)
            self.assertNotEqual(saida.returncode, 0)
            self.assertEqual(self._main_do_remoto(remoto), "")
        self.assertIn(".githooks/pre-push", saida.stderr)

    def test_pre_push_recusa_o_repasse_a_si_mesmo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta, remoto = self._com_remoto(tmp)
            (pasta / ".githooks").mkdir()
            (pasta / ".githooks/pre-push").symlink_to("../trilha/hooks/pre-push")
            # Num grupo de processos próprio: se o repasse rodar sem fim, o prazo encerra o grupo
            # inteiro, e o hook não sobrevive ao teste.
            envio = subprocess.Popen(["git", "push", "-q", "origem", "HEAD:refs/heads/main"], cwd=pasta,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                     start_new_session=True)
            try:
                _, erro = envio.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(envio.pid, signal.SIGKILL)
                envio.communicate()
                self.fail("o repasse rodou sem fim")
            self.assertNotEqual(envio.returncode, 0)
            self.assertEqual(self._main_do_remoto(remoto), "")
        self.assertIn(".githooks/pre-push", erro)

    def test_lista_do_metodo_pelos_arquivos_versionados(self) -> None:
        solto = MODELO / "trilha/.rascunho.swp"
        try:
            solto.write_text("um arquivo do editor\n", encoding="utf-8")
            spec = importlib.util.spec_from_file_location("kit_de_novo", RAIZ / "ferramentas" / "kit.py")
            kit = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(kit)
        finally:
            solto.unlink()
        self.assertNotIn("trilha/.rascunho.swp", kit.SEM_MUDAR)
        self.assertIn("trilha/verifica.sh", kit.SEM_MUDAR)

    def test_dispensa_de_change_pela_pasta_trilha(self) -> None:
        """C13: a dispensa de change aponta para a pasta e para a ferramenta, sem lista repetida."""
        comum = (MODELO / "trilha/CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("a cópia nova do kit (a pasta `trilha/` e o que o `kit.py atualizar` escreve) "
                      "dispensam change", comum)
        self.assertIn("Não edite este arquivo nem a pasta `trilha/`", comum)

    def test_ferramenta_cria_projeto_novo_e_recusa_pasta_cheia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp) / "novo"
            saida = self._ferramenta("novo", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stderr)
            for destino, origem in ORIGEM.items():
                self.assertEqual((pasta / destino).read_bytes(), (MODELO / origem).read_bytes())
            for nome in FERRAMENTA.SEM_MUDAR:
                self.assertEqual((pasta / nome).read_bytes(), (MODELO / nome).read_bytes())
            self.assertTrue((pasta / "sdd").is_dir())
            self.assertIn("gh repo create", saida.stdout)
            self.assertIn("README do kit, passos 3 a 6", saida.stdout)
            self.assertEqual(self._ferramenta("novo", str(pasta)).returncode, 1)

    def test_ferramenta_atualiza_so_o_que_se_copia_sem_mudar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_velho(tmp)
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertEqual((pasta / "trilha/CLAUDE-comum.md").read_bytes(),
                             (MODELO / "trilha/CLAUDE-comum.md").read_bytes())
            # O que o projeto preencheu fica como está.
            self.assertEqual((pasta / ".github/workflows/verificacao.yml").read_text(),
                             "# a parte da stack, preenchida\n")
            versao = re.search(r"^Versão (\d+\.\d+)", (MODELO / "trilha/CLAUDE-comum.md").read_text(
                encoding="utf-8"), re.M).group(1)
            self.assertIn(f"comum 1.19 → {versao}", saida.stdout)
            # A ferramenta não faz commit.
            self.assertIn("CLAUDE-comum.md", subprocess.run(
                ["git", "status", "--short"], cwd=pasta, capture_output=True, text=True).stdout)

    def test_atualizar_sincroniza_so_as_regras_que_vieram_do_kit(self) -> None:
        env = {**os.environ, **GIT_TESTE}
        antigo = subprocess.run(["git", "show", "v1.25:openspec/config.yaml"], cwd=RAIZ,
                                capture_output=True, text=True, check=True).stdout
        atual = (MODELO / "openspec/config.yaml").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_velho(tmp)
            config = pasta / "openspec/config.yaml"
            contexto = "schema: spec-driven\ncontext: |\n  Projeto: o meu.\n"
            config.write_text(contexto + antigo[antigo.find("\nrules:"):], encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", "regras da 1.25"], cwd=pasta, env=env, check=True)
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertIn("eram as do kit em ", saida.stdout)
            texto = config.read_text(encoding="utf-8")
            # O context do projeto fica, e ganha a língua, que saiu das regras (v1.33).
            self.assertIn("  Projeto: o meu.\n", texto)
            self.assertIn("  All artifacts must be written in pt-BR.\n", texto)
            self.assertIn("a língua foi acrescentada ao context", saida.stdout)
            self.assertEqual(texto[texto.find("\nrules:"):], atual[atual.find("\nrules:"):])
            subprocess.run(["git", "commit", "-qam", "kit"], cwd=pasta, env=env, check=True)
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(config.read_text(encoding="utf-8"), texto)  # uma vez só
            self.assertNotIn("a língua foi acrescentada", saida.stdout)
            subprocess.run(["git", "checkout", "-q", "."], cwd=pasta, check=True)
            subprocess.run(["git", "clean", "-qfd"], cwd=pasta, check=True)
            config.write_text(contexto + "rules:\n  proposal:\n    - Uma regra própria.\n")
            subprocess.run(["git", "commit", "-qam", "regras próprias"], cwd=pasta, env=env, check=True)
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertIn("regras próprias", saida.stdout)
            self.assertIn("Uma regra própria.", config.read_text(encoding="utf-8"))

    def _atualizar_com_gitignore(self, tmp: str, troca: tuple[str, str]) -> str:
        """O atualizar de um projeto na versão atual, com o .gitignore do modelo trocado como pedido."""
        pasta = self._projeto_novo(tmp)
        gitignore = pasta / ".gitignore"
        texto = gitignore.read_text(encoding="utf-8")
        self.assertIn(troca[0], texto)
        gitignore.write_text(texto.replace(troca[0], troca[1]), encoding="utf-8")
        self._commit_tudo(pasta, ".gitignore preenchido")
        saida = self._ferramenta("atualizar", str(pasta))
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        return saida.stdout

    def test_parte_fixa_avisa_a_linha_que_o_projeto_nunca_copiou(self) -> None:
        """Change 09: a linha que já estava no modelo da versão do projeto e ele nunca copiou."""
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._atualizar_com_gitignore(tmp, ("*.log\n", ""))
        self.assertIn("a parte fixa de .gitignore difere do modelo do kit", saida)
        self.assertIn("  + *.log", saida)

    def _atualizar_com_check(self, tmp: str, troca: tuple[str, str]) -> str:
        """O atualizar de um projeto na versão atual, com o scripts/check.sh trocado como pedido."""
        pasta = self._projeto_novo(tmp)
        check = pasta / "scripts/check.sh"
        texto = check.read_text(encoding="utf-8")
        self.assertIn(troca[0], texto)
        check.write_text(texto.replace(troca[0], troca[1]), encoding="utf-8")
        self._commit_tudo(pasta, "check.sh preenchido")
        saida = self._ferramenta("atualizar", str(pasta))
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        return saida.stdout

    def test_parte_fixa_aceita_a_chamada_dentro_de_uma_funcao(self) -> None:
        """Change 09: o projeto que chama o verifica.sh por uma função própria (o etapa do Xavier)."""
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._atualizar_com_check(
                tmp, ("\nbash trilha/verifica.sh\n", '\netapa "regras" bash trilha/verifica.sh --vizinho trilha-ai\n'))
        self.assertNotIn("+ bash trilha/verifica.sh", saida)

    def test_parte_fixa_sem_o_bloco_da_parte_da_stack(self) -> None:
        """Change 09: o bloco "Parte da stack" trocado pelos comandos da stack não vira aviso."""
        modelo = (MODELO / "scripts/check.sh").read_text(encoding="utf-8")
        inicio = modelo.index("# Parte da stack")
        bloco = modelo[inicio:]
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._atualizar_com_check(tmp, (bloco, "# A stack do projeto.\nuv run pytest\n"))
        self.assertNotIn("a parte da stack ainda não foi preenchida", saida)
        self.assertNotIn("a parte fixa de scripts/check.sh", saida)

    def test_parte_fixa_aceita_a_acao_atualizada_pelo_dependabot(self) -> None:
        """Revisão da change 09, achado 2: a ação noutro commit não manda rebaixá-la."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            ci = pasta / ".github/workflows/verificacao.yml"
            texto = ci.read_text(encoding="utf-8")
            ci.write_text(re.sub(r"actions/checkout@[0-9a-f]+", "actions/checkout@" + "f" * 40, texto), encoding="utf-8")
            self._commit_tudo(pasta, "checkout atualizado pelo Dependabot")
            saida = self._ferramenta("atualizar", str(pasta))
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertNotIn("actions/checkout", saida.stdout)

    def test_parte_fixa_avisa_o_passo_do_ci_ao_lado_da_stack(self) -> None:
        """Change 09: no CI, o comentário da stack fica no mesmo bloco dos passos fixos; a falta de
        um deles continua sendo avisada (a segunda rodada da execução manual)."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            ci = pasta / ".github/workflows/verificacao.yml"
            linhas = ci.read_text(encoding="utf-8").splitlines(keepends=True)
            inicio = next(i for i, l in enumerate(linhas) if "actions/setup-node@" in l)
            ci.write_text("".join(linhas[:inicio] + linhas[inicio + 3 :]), encoding="utf-8")
            self.assertNotIn("setup-node", ci.read_text(encoding="utf-8"))
            self._commit_tudo(pasta, "CI sem o setup-node")
            saida = self._ferramenta("atualizar", str(pasta))
        self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
        self.assertIn("a parte fixa de .github/workflows/verificacao.yml difere do modelo do kit", saida.stdout)
        self.assertIn("+ - uses: actions/setup-node@", saida.stdout)

    def test_parte_fixa_sem_o_bloco_da_stack(self) -> None:
        """Change 09: o bloco da stack que o projeto apaga de propósito não vira aviso."""
        modelo = (MODELO / "gitignore").read_text(encoding="utf-8")
        self.assertIn("\n# Python\n", modelo)
        self.assertIn("\n# Node\n", modelo)
        # O bloco # Node, que não abre com "Parte da stack": só a regra dos títulos o tira.
        inicio = modelo.index("\n# Node\n") + 1
        bloco = modelo[inicio : modelo.index("\n\n", inicio) + 1]
        self.assertNotIn("Parte da stack", bloco)
        with tempfile.TemporaryDirectory() as tmp:
            saida = self._atualizar_com_gitignore(tmp, (bloco, ""))
        self.assertNotIn("node_modules/", saida)
        self.assertNotIn("a parte fixa de .gitignore", saida)
        # Sem a regra dos títulos, o mesmo bloco viraria aviso: o teste prova a regra.
        sem_titulos = FERRAMENTA.BLOCOS_DA_STACK
        try:
            FERRAMENTA.BLOCOS_DA_STACK = set()
            self.assertIn("node_modules/", FERRAMENTA._sem_blocos_da_stack(".gitignore", modelo))
        finally:
            FERRAMENTA.BLOCOS_DA_STACK = sem_titulos

    def test_atualizar_avisa_a_parte_fixa_que_mudou_no_kit(self) -> None:
        """O CI preenchido não é sobrescrito, mas o que o kit mudou nele desde a versão do projeto é dito."""
        env = {**os.environ, **GIT_TESTE}
        antigo = subprocess.run(["git", "show", "v1.29:github-verificacao.yml"], cwd=RAIZ,
                                capture_output=True, text=True, check=True).stdout
        stack = "      - run: uv sync  # a parte da stack, preenchida\n"
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_velho(tmp)
            comum = pasta / "trilha/CLAUDE-comum.md"
            comum.write_text(comum.read_text(encoding="utf-8").replace("Versão 1.19,", "Versão 1.29,"),
                             encoding="utf-8")
            ci = pasta / ".github/workflows/verificacao.yml"
            ci.write_text(antigo + stack, encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", "CI da 1.29"], cwd=pasta, env=env, check=True)
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertIn("a parte fixa de .github/workflows/verificacao.yml difere do modelo do kit",
                          saida.stdout)
            self.assertIn("+ branches: [main, master]", saida.stdout)
            self.assertIn("- run: openspec validate --all --strict --no-interactive", saida.stdout)
            self.assertNotIn("dependabot.yml difere", saida.stdout)
            self.assertEqual(ci.read_text(encoding="utf-8"), antigo + stack)  # só o aviso
            # Com as linhas novas trazidas à mão, o aviso some, mesmo com a stack do projeto.
            atual = (MODELO / ".github/workflows/verificacao.yml").read_text(encoding="utf-8")
            ci.write_text(atual + stack, encoding="utf-8")
            comum.write_text(re.sub(r"^Versão [\d.]+,", "Versão 1.29,", comum.read_text(encoding="utf-8"),
                                    flags=re.M), encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", "de volta à 1.29"], cwd=pasta, env=env, check=True)
            self.assertNotIn("a parte fixa", self._ferramenta("atualizar", str(pasta)).stdout)

    # O atualizar que confere o kit antes de mudar o projeto (change 07).

    def _atualizar_sem_mudar(self, kit: Path, pasta: Path) -> subprocess.CompletedProcess:
        """O atualizar de outro kit, conferindo que o projeto ficou como estava."""
        saida = subprocess.run([sys.executable, "-I", str(kit / "ferramentas/kit.py"), "atualizar", str(pasta)],
                               capture_output=True, text=True, check=False)
        self.assertEqual(saida.returncode, 1, saida.stdout + saida.stderr)
        mudou = subprocess.run(["git", "status", "--porcelain"], cwd=pasta, capture_output=True, text=True)
        self.assertEqual(mudou.stdout, "", "o projeto mudou antes da recusa")
        self.assertNotIn("commit sugerido", saida.stdout)
        return saida

    def test_atualizar_recusa_o_kit_atras_do_projeto(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            comum = pasta / "trilha/CLAUDE-comum.md"
            comum.write_text(re.sub(r"^Versão [\d.]+,", "Versão 9.9,", comum.read_text(encoding="utf-8"),
                                    flags=re.M), encoding="utf-8")
            self._commit_tudo(pasta, "comum na 9.9")
            saida = self._atualizar_sem_mudar(RAIZ, pasta)
        versao = FERRAMENTA._versao(MODELO / "trilha/CLAUDE-comum.md")
        for trecho in ("9.9", versao, "git pull"):
            self.assertIn(trecho, saida.stderr)

    def test_atualizar_recusa_o_kit_sem_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            kit = Path(tmp) / "kit-zip"
            shutil.copytree(RAIZ, kit, ignore=shutil.ignore_patterns(".git", "__pycache__", ".ruff_cache", ".codegraph"))
            saida = self._atualizar_sem_mudar(kit, pasta)
        self.assertIn("não é um repositório git", saida.stderr)

    def test_atualizar_recusa_o_kit_dentro_de_outro_repositorio(self) -> None:
        """Revisão de código, ponto 5: o ZIP extraído numa pasta versionada não é o kit no git."""
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            pai = Path(tmp) / "pai"
            pai.mkdir()
            for comando in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "pai"]):
                subprocess.run(["git", "-C", str(pai), "-c", "commit.gpgsign=false", *comando], check=True,
                               env={**os.environ, **GIT_TESTE})
            kit = pai / "kit"
            shutil.copytree(RAIZ, kit, ignore=shutil.ignore_patterns(".git", "__pycache__", ".ruff_cache", ".codegraph"))
            saida = self._atualizar_sem_mudar(kit, pasta)
        self.assertIn("não é um repositório git", saida.stderr)

    def test_atualizar_recusa_o_kit_raso(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_novo(tmp)
            kit = Path(tmp) / "kit-raso"
            subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{RAIZ}", str(kit)], check=True)
            shutil.copy(RAIZ / "ferramentas/kit.py", kit / "ferramentas/kit.py")  # o kit.py de agora
            saida = self._atualizar_sem_mudar(kit, pasta)
        self.assertIn("git fetch --unshallow --tags", saida.stderr)

    def test_ferramenta_recusa_trabalho_pendente_change_em_curso_e_outra_branch(self) -> None:
        env = {**os.environ, **GIT_TESTE}
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_velho(tmp)
            (pasta / "solto.txt").write_text("x")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 1)
            self.assertIn("trabalho não commitado", saida.stderr)
            (pasta / "solto.txt").unlink()
            andamento = pasta / "ANDAMENTO.md"
            andamento.write_text(andamento.read_text(encoding="utf-8").replace(
                "nada em andamento", "em andamento"), encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", "andamento"], cwd=pasta, check=True, env=env)
            self.assertIn("em andamento", self._ferramenta("atualizar", str(pasta)).stderr)
            subprocess.run(["git", "switch", "-qc", "change/01-x"], cwd=pasta, check=True)
            self.assertIn("vai à main", self._ferramenta("atualizar", str(pasta)).stderr)
            self.assertEqual(self._ferramenta("atualizar", str(RAIZ)).returncode, 1)


TEMPO = MODELO / "trilha" / "tempo.py"


class HorasDeTrabalho(unittest.TestCase):
    """O trilha/tempo.py (change 10): as horas de cada dia, das conversas do Claude Code e dos
    commits, com o resumo e a página fora do repositório. Tudo em pastas temporárias, em UTC."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.raiz = base / "proj"
        self.config = base / "config"
        self.dados = base / "dados"
        self.casa = base / "casa"
        for pasta in (self.raiz, self.config / "projects", self.casa):
            pasta.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.raiz)], check=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # Montagem

    def _commit(self, quando: str, nome: str = "a") -> None:
        """Um commit com a data de autor dada (ISO 8601, em UTC)."""
        env = {**os.environ, **GIT_TESTE, "GIT_AUTHOR_DATE": quando, "GIT_COMMITTER_DATE": quando}
        (self.raiz / nome).write_text(quando, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.raiz), "add", "-A"], check=True, env=env)
        subprocess.run(["git", "-C", str(self.raiz), "commit", "-qm", quando], check=True, env=env)

    @staticmethod
    def _pedido(hora: str, cwd: Path, sessao: str = "s1", texto: str = "faça") -> dict:
        return {"type": "user", "timestamp": hora, "sessionId": sessao, "cwd": str(cwd),
                "isSidechain": False, "message": {"role": "user", "content": texto}}

    @staticmethod
    def _ia(hora: str, cwd: Path, sessao: str = "s1") -> dict:
        return {"type": "assistant", "timestamp": hora, "sessionId": sessao, "cwd": str(cwd),
                "isSidechain": False,
                "message": {"role": "assistant", "content": [{"type": "text", "text": "feito"}]}}

    @staticmethod
    def _resultado(hora: str, cwd: Path, sessao: str = "s1") -> dict:
        return {"type": "user", "timestamp": hora, "sessionId": sessao, "cwd": str(cwd),
                "isSidechain": False, "message": {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": "x", "content": "ok"}]}}

    def _conversa(self, linhas: list[dict], sessao: str = "s1", pasta: str = "-proj",
                  config: Path | None = None, subagente: bool = False) -> Path:
        destino = (config or self.config) / "projects" / pasta
        arquivo = destino / sessao / "subagents" / "agent-1.jsonl" if subagente else destino / f"{sessao}.jsonl"
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        with arquivo.open("a", encoding="utf-8") as saida:
            saida.write('{"type": "ai-title", "sessionId": "%s"}\n' % sessao)
            saida.write("isto não é json\n")
            for linha in linhas:
                saida.write(json.dumps(linha) + "\n")
        return arquivo

    def _rodar(self, cwd: Path | None = None, **env_extra: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "TZ": "UTC", "HOME": str(self.casa), **self.SEM_GIT_DA_MAQUINA,
               "CLAUDE_CONFIG_DIR": str(self.config), "XDG_DATA_HOME": str(self.dados), **env_extra}
        return subprocess.run([sys.executable, "-I", str(TEMPO)], cwd=cwd or self.raiz, env=env,
                              capture_output=True, text=True, check=False)

    # Leitura do que ele gravou

    def _pasta_tempo(self, dados: Path | None = None) -> Path:
        return (dados or self.dados) / "trilha-ai" / "tempo"

    def _pagina(self, dados: Path | None = None) -> str:
        paginas = list(self._pasta_tempo(dados).glob("*.html"))
        self.assertEqual(len(paginas), 1, paginas)
        return paginas[0].read_text(encoding="utf-8")

    def _resumo(self) -> dict:
        resumos = list(self._pasta_tempo().glob("*.json"))
        self.assertEqual(len(resumos), 1, resumos)
        return json.loads(resumos[0].read_text(encoding="utf-8"))

    def _dias(self) -> dict:
        """Os dias dos dados embutidos na página, pela data."""
        bloco = re.search(r'<script id="dados" type="application/json">(.*?)</script>',
                          self._pagina(), re.S)
        self.assertIsNotNone(bloco)
        return {dia["d"]: dia for dia in json.loads(bloco.group(1))["dias"]}

    def _ok(self, **env_extra: str) -> subprocess.CompletedProcess:
        saida = self._rodar(**env_extra)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        return saida

    # Só sob demanda

    def test_tempo_sem_gancho_no_modelo(self) -> None:
        settings = json.loads((MODELO / "claude-settings.json").read_text(encoding="utf-8"))
        comandos = [gancho.get("command", "") for eventos in settings.get("hooks", {}).values()
                    for grupo in eventos for gancho in grupo.get("hooks", [])]
        self.assertTrue(comandos)
        self.assertFalse([c for c in comandos if "tempo.py" in c])

    def test_tempo_fora_de_repositorio(self) -> None:
        solta = Path(self._tmp.name) / "solta"
        solta.mkdir()
        saida = self._rodar(cwd=solta, GIT_CEILING_DIRECTORIES=self._tmp.name)
        self.assertNotEqual(saida.returncode, 0)
        self.assertIn("não é um repositório git", saida.stderr)
        self.assertFalse(self.dados.exists())

    # Conversas do repositório

    def test_tempo_ignora_repositorio_vizinho(self) -> None:
        vizinho = Path(f"{self.raiz}-antigo")
        self._conversa([self._pedido("2026-10-01T09:00:00Z", vizinho),
                        self._ia("2026-10-01T09:20:00Z", vizinho)], pasta="-proj-antigo")
        self._ok()
        self.assertNotIn("2026-10-01", self._dias())

    def test_tempo_conta_conversa_em_subpasta(self) -> None:
        sub = self.raiz / "src"
        self._conversa([self._pedido("2026-10-01T09:00:00Z", sub)], pasta="-proj-src")
        sub_ia = self._ia("2026-10-01T09:10:00Z", sub)
        sub_ia["isSidechain"] = True
        self._conversa([sub_ia], pasta="-proj-src", subagente=True)
        self._ok()
        self.assertEqual(self._dias()["2026-10-01"]["total"], 10)

    def test_tempo_usa_claude_config_dir(self) -> None:
        outra = Path(self._tmp.name) / "outra-config"
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:15:00Z", self.raiz)], config=outra)
        self._ok(CLAUDE_CONFIG_DIR=str(outra))
        self.assertEqual(self._dias()["2026-10-01"]["total"], 15)

    # Pedido do usuário

    def test_tempo_resultado_de_ferramenta_e_da_ia(self) -> None:
        self._conversa([self._ia("2026-10-01T09:00:00Z", self.raiz),
                        self._resultado("2026-10-01T09:10:00Z", self.raiz)])
        self._ok()
        dia = self._dias()["2026-10-01"]
        self.assertEqual((dia["total"], dia["usuario"], dia["ia"]), (10, 0, 10))

    def test_tempo_metadados_nao_sao_pedido(self) -> None:
        meta = self._pedido("2026-10-01T09:10:00Z", self.raiz)
        meta["isMeta"] = True
        self._conversa([self._ia("2026-10-01T09:00:00Z", self.raiz), meta])
        self._ok()
        self.assertEqual(self._dias()["2026-10-01"]["usuario"], 0)

    # O resumo

    def test_tempo_resumo_sem_texto(self) -> None:
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz, texto="frase-que-nao-pode-vazar"),
                        self._ia("2026-10-01T09:05:00Z", self.raiz),
                        self._pedido("2026-10-01T09:06:00Z", self.raiz, texto="frase-que-nao-pode-vazar")])
        self._ok()
        texto = next(self._pasta_tempo().glob("*.json")).read_text(encoding="utf-8")
        self.assertIn("s1", texto)
        self.assertNotIn("frase-que-nao-pode-vazar", texto)
        self.assertNotIn("frase-que-nao-pode-vazar", self._pagina())

    def test_tempo_nao_toca_o_repositorio(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        (self.raiz / "solto.txt").write_text("x", encoding="utf-8")
        antes = subprocess.run(["git", "-C", str(self.raiz), "status", "--porcelain"],
                               capture_output=True, text=True, check=True).stdout
        self._ok()
        depois = subprocess.run(["git", "-C", str(self.raiz), "status", "--porcelain"],
                                capture_output=True, text=True, check=True).stdout
        self.assertEqual(antes, depois)

    def test_tempo_usa_xdg_data_home(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        outra = Path(self._tmp.name) / "outros-dados"
        self._ok(XDG_DATA_HOME=str(outra))
        self.assertEqual(len(list(self._pasta_tempo(outra).glob("*.json"))), 1)
        self.assertEqual(len(list(self._pasta_tempo(outra).glob("*.html"))), 1)
        self.assertFalse(self.dados.exists())

    def test_tempo_conversa_apagada_continua(self) -> None:
        arquivo = self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                                  self._ia("2026-10-01T09:20:00Z", self.raiz)])
        self._ok()
        primeira, resumo = self._dias(), self._resumo()
        arquivo.unlink()
        self._ok()
        self.assertEqual(self._dias(), primeira)
        self.assertEqual(self._resumo()["conversas"], resumo["conversas"])

    def test_tempo_conversa_que_cresceu(self) -> None:
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:05:00Z", self.raiz)])
        self._ok()
        self._conversa([self._pedido("2026-10-01T09:10:00Z", self.raiz),
                        self._ia("2026-10-01T09:30:00Z", self.raiz)])
        self._ok()
        intervalos = self._resumo()["conversas"]["s1"]
        self.assertEqual(len(intervalos), len({tuple(i) for i in intervalos}))
        self.assertEqual(len(intervalos), 3)
        self.assertEqual(self._dias()["2026-10-01"]["total"], 30)

    # A apuração por dia

    def test_tempo_dois_pedidos_e_duas_respostas(self) -> None:
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:05:00Z", self.raiz),
                        self._pedido("2026-10-01T09:12:00Z", self.raiz),
                        self._ia("2026-10-01T09:31:00Z", self.raiz)])
        self._ok()
        dia = self._dias()["2026-10-01"]
        self.assertEqual((dia["fonte"], dia["total"], dia["usuario"], dia["ia"]), ("conversas", 31, 7, 24))

    def test_tempo_pausa_longa_nao_conta(self) -> None:
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:05:00Z", self.raiz),
                        self._pedido("2026-10-01T10:00:00Z", self.raiz)])
        self._ok()
        self.assertEqual(self._dias()["2026-10-01"]["total"], 5)

    def test_tempo_conversas_em_paralelo(self) -> None:
        for sessao in ("s1", "s2"):
            self._conversa([self._ia(f"2026-10-01T10:{m:02d}:00Z", self.raiz, sessao) for m in (0, 20, 40)]
                           + [self._ia("2026-10-01T11:00:00Z", self.raiz, sessao)], sessao=sessao)
        self._ok()
        dia = self._dias()["2026-10-01"]
        self.assertEqual((dia["total"], dia["usuario"], dia["ia"]), (60, 0, 60))

    def test_tempo_usuario_numa_ia_noutra(self) -> None:
        self._conversa([self._ia("2026-10-01T10:00:00Z", self.raiz),
                        self._ia("2026-10-01T10:30:00Z", self.raiz)])
        self._conversa([self._ia("2026-10-01T10:20:00Z", self.raiz, "s2"),
                        self._pedido("2026-10-01T10:30:00Z", self.raiz, "s2")], sessao="s2")
        self._ok()
        dia = self._dias()["2026-10-01"]
        self.assertEqual((dia["total"], dia["usuario"], dia["ia"]), (30, 10, 20))

    def test_tempo_virada_do_dia(self) -> None:
        self._conversa([self._ia("2026-10-01T23:50:00Z", self.raiz),
                        self._ia("2026-10-02T00:10:00Z", self.raiz)])
        self._ok()
        dias = self._dias()
        self.assertEqual((dias["2026-10-01"]["total"], dias["2026-10-02"]["total"]), (10, 10))

    def test_tempo_sessoes_de_commits(self) -> None:
        for hora in ("10", "11", "14"):
            self._commit(f"2026-10-01T{hora}:00:00Z", nome=hora)
        self._ok()
        dia = self._dias()["2026-10-01"]
        self.assertEqual((dia["fonte"], dia["total"]), ("commits", 120))

    def test_tempo_dia_com_conversa_usa_conversa(self) -> None:
        self._commit("2026-10-01T14:00:00Z")
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:05:00Z", self.raiz)])
        self._ok()
        dia = self._dias()["2026-10-01"]
        self.assertEqual((dia["fonte"], dia["total"]), ("conversas", 5))

    def test_tempo_commit_em_duas_branches(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        subprocess.run(["git", "-C", str(self.raiz), "branch", "outra"], check=True)
        subprocess.run(["git", "-C", str(self.raiz), "tag", "v1"], check=True)
        self._ok()
        self.assertEqual(self._dias()["2026-10-01"]["commits"], 1)

    def test_tempo_dia_de_commits_sem_divisao(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        self._ok()
        dia = self._dias()["2026-10-01"]
        self.assertEqual((dia["fonte"], dia["total"], dia["usuario"], dia["ia"]), ("commits", 30, None, None))

    # A página e a saída

    def test_tempo_imprime_o_caminho_da_pagina(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        saida = self._ok()
        pagina = next(self._pasta_tempo().glob("*.html"))
        self.assertIn(str(pagina), saida.stdout)
        self.assertTrue(pagina.name.startswith("proj-"))

    def test_tempo_pagina_sem_rede(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        self._ok()
        pagina = self._pagina()
        self.assertNotRegex(pagina, r"""(?i)\b(src|href)\s*=\s*["']?https?:""")
        self.assertNotRegex(pagina, r"(?i)@import|url\(\s*[\"']?https?:")

    def test_tempo_avisa_guarda_padrao(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        saida = self._ok()
        self.assertIn('"cleanupPeriodDays": 3650', saida.stderr)

    def test_tempo_guarda_longa_sem_aviso(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        (self.config / "settings.json").write_text('{"cleanupPeriodDays": 3650}', encoding="utf-8")
        saida = self._ok()
        self.assertNotIn("cleanupPeriodDays", saida.stderr)

    # As respostas à revisão (verify e code review da change 10)

    def test_tempo_caminho_com_acento(self) -> None:
        acento = Path(self._tmp.name) / "projeto-ação"
        subprocess.run(["git", "init", "-q", "-b", "main", str(acento)], check=True)
        arquivo = self.config / "projects" / "-projeto-acao" / "s1.jsonl"
        arquivo.parent.mkdir(parents=True)
        linhas = [self._pedido("2026-10-01T09:00:00Z", acento), self._ia("2026-10-01T09:20:00Z", acento)]
        # O Claude Code grava os acentos como são, sem o escape \\u do json.dumps padrão.
        arquivo.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas),
                           encoding="utf-8")
        saida = self._rodar(cwd=acento)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertEqual(self._dias()["2026-10-01"]["total"], 20)

    def test_tempo_atividade_de_segundos(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:00:02Z", self.raiz)])
        self._ok()
        dia = self._dias()["2026-10-01"]
        self.assertEqual((dia["fonte"], dia["total"]), ("commits", 30))

    def test_tempo_dia_da_mudanca_de_horario(self) -> None:
        # 01/11/2026 é o fim do horário de verão nesse fuso: 23:00 local é 04:00 UTC do dia 2.
        self._conversa([self._ia("2026-11-02T04:00:00Z", self.raiz),
                        self._ia("2026-11-02T04:20:00Z", self.raiz)])
        self._ok(TZ="EST5EDT,M3.2.0,M11.1.0")
        self.assertEqual(self._dias()["2026-11-01"]["faixas"], [[1380, 1400]])

    def test_tempo_commit_depois_da_meia_noite(self) -> None:
        self._commit("2026-10-02T00:10:00Z")
        self._ok()
        dias = self._dias()
        self.assertNotIn("2026-10-01", dias)
        self.assertEqual(dias["2026-10-02"]["total"], 10)

    def test_tempo_subagente_apagado_continua(self) -> None:
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:55:00Z", self.raiz)])
        passos = []
        for minuto in (10, 20, 30, 40, 50):
            passo = self._ia(f"2026-10-01T09:{minuto}:00Z", self.raiz)
            passo["isSidechain"] = True
            passos.append(passo)
        subagente = self._conversa(passos, subagente=True)
        self._ok()
        primeira = self._dias()["2026-10-01"]["total"]
        subagente.unlink()
        self._ok()
        self.assertEqual(primeira, 55)
        self.assertEqual(self._dias()["2026-10-01"]["total"], primeira)

    def _resumo_trocado(self, texto: str) -> tuple[Path, subprocess.CompletedProcess]:
        """O resumo de uma primeira execução trocado pelo texto dado, e a execução seguinte."""
        self._commit("2026-10-01T10:00:00Z")
        self._ok()
        resumo = next(self._pasta_tempo().glob("*.json"))
        resumo.write_text(texto, encoding="utf-8")
        return resumo, self._rodar()

    def test_tempo_resumo_corrompido_preservado(self) -> None:
        resumo, saida = self._resumo_trocado("isto não é json")
        self.assertNotEqual(saida.returncode, 0)
        self.assertIn(resumo.name, saida.stderr)
        self.assertEqual(resumo.read_text(encoding="utf-8"), "isto não é json")

    def test_tempo_entrada_fora_do_formato(self) -> None:
        texto = json.dumps({"versao": 1, "raiz": str(self.raiz),
                            "conversas": {"s1": [["2026-10-01T09:00:00+00:00", "ia"]]}})
        resumo, saida = self._resumo_trocado(texto)
        self.assertNotEqual(saida.returncode, 0)
        self.assertNotIn("Traceback", saida.stderr)
        self.assertEqual(resumo.read_text(encoding="utf-8"), texto)

    def _arquivo_de_outro_repositorio(self) -> tuple[Path, os.stat_result]:
        """Uma conversa de um vizinho com o caminho do mesmo tamanho, lida numa primeira execução e
        depois trocada pela deste repositório, com o mesmo tamanho e a mesma data."""
        vizinho = Path(str(self.raiz)[:-1] + "X")
        arquivo = self._conversa([self._pedido("2026-10-01T09:00:00Z", vizinho),
                                  self._ia("2026-10-01T09:20:00Z", vizinho)], pasta="-viz")
        self._ok()
        antes = arquivo.stat()
        arquivo.write_text(arquivo.read_text(encoding="utf-8").replace(str(vizinho), str(self.raiz)),
                           encoding="utf-8")
        os.utime(arquivo, ns=(antes.st_atime_ns, antes.st_mtime_ns))
        self.assertEqual(arquivo.stat().st_size, antes.st_size)
        return arquivo, antes

    def test_tempo_arquivo_sem_mudanca_nao_e_relido(self) -> None:
        self._arquivo_de_outro_repositorio()
        self._ok()
        self.assertNotIn("2026-10-01", self._dias())

    def test_tempo_arquivo_que_mudou_e_relido(self) -> None:
        arquivo, antes = self._arquivo_de_outro_repositorio()
        os.utime(arquivo, ns=(antes.st_atime_ns, antes.st_mtime_ns + 10**10))
        self._ok()
        self.assertEqual(self._dias()["2026-10-01"]["total"], 20)

    def test_tempo_guarda_curta_definida(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        (self.config / "settings.json").write_text('{"cleanupPeriodDays": 90}', encoding="utf-8")
        saida = self._ok()
        self.assertIn("90 dias", saida.stderr)
        self.assertNotIn("padrão", saida.stderr)

    def test_tempo_temporario_antigo_nao_atrapalha(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        self._ok()
        resumo = next(self._pasta_tempo().glob("*.json"))
        resumo.with_name(resumo.name + ".tmp").mkdir()  # o que uma execução interrompida deixaria
        self._ok()

    def test_tempo_um_dia_no_singular(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        saida = self._ok()
        self.assertIn(": 1 dia,", saida.stdout)

    # A revisão do tempo.py (change 11)

    SEM_GIT_DA_MAQUINA = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}

    def _repositorio(self, caminho: Path, quando: str = "2026-10-01T10:00:00Z") -> Path:
        """Outro repositório git, com um commit."""
        caminho.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q", "-b", "main", str(caminho)], check=True)
        env = {**os.environ, **GIT_TESTE, "GIT_AUTHOR_DATE": quando, "GIT_COMMITTER_DATE": quando}
        subprocess.run(["git", "-C", str(caminho), "commit", "-q", "--allow-empty", "-m", "a"],
                       check=True, env=env)
        return caminho

    def test_tempo_clone_dentro_da_raiz(self) -> None:
        aninhado = self.raiz / "vendor" / "lib"
        subprocess.run(["git", "init", "-q", str(aninhado)], check=True)
        self._conversa([self._pedido("2026-10-01T09:00:00Z", aninhado),
                        self._ia("2026-10-01T09:20:00Z", aninhado)])
        self._ok()
        self.assertNotIn("2026-10-01", self._dias())

    def test_tempo_worktree_da_raiz(self) -> None:
        self._commit("2026-09-01T10:00:00Z")
        worktree = self.raiz / ".claude" / "worktrees" / "w1"
        subprocess.run(["git", "-C", str(self.raiz), "worktree", "add", "-q", "-b", "w1", str(worktree)],
                       check=True, capture_output=True)
        self._conversa([self._pedido("2026-10-01T09:00:00Z", worktree),
                        self._ia("2026-10-01T09:20:00Z", worktree)])
        self._ok()
        self.assertEqual(self._dias()["2026-10-01"]["total"], 20)

    def test_tempo_saida_e_volta_no_meio_da_conversa(self) -> None:
        fora = Path(self._tmp.name) / "outra"
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:05:00Z", fora),
                        self._ia("2026-10-01T09:20:00Z", fora),
                        self._ia("2026-10-01T09:28:00Z", self.raiz)])
        self._ok()
        self.assertNotIn("2026-10-01", self._dias())

    def test_tempo_subagente_noutra_pasta(self) -> None:
        fora = Path(self._tmp.name) / "outra"
        self._conversa([self._pedido("2026-10-01T09:00:00Z", self.raiz),
                        self._ia("2026-10-01T09:10:00Z", self.raiz),
                        self._ia("2026-10-01T09:20:00Z", self.raiz)])
        # Uma linha que cita o repositório, sem ser evento: o arquivo do subagente passa no primeiro
        # filtro, e os eventos de fora dele são lidos.
        passos = [{"type": "system", "timestamp": "2026-10-01T09:01:00Z", "sessionId": "s1",
                   "cwd": str(self.raiz)}]
        for minuto in ("05", "15"):
            passo = self._ia(f"2026-10-01T09:{minuto}:00Z", fora)
            passo["isSidechain"] = True
            passos.append(passo)
        self._conversa(passos, subagente=True)
        self._ok()
        self.assertEqual(self._dias()["2026-10-01"]["total"], 20)

    def test_tempo_commit_de_outro_autor(self) -> None:
        subprocess.run(["git", "-C", str(self.raiz), "config", "user.email", "eu@exemplo.br"], check=True)
        self._commit("2026-10-01T10:00:00Z")  # o autor dos commits de teste é t@t, como um robô
        self._ok(**self.SEM_GIT_DA_MAQUINA)
        self.assertNotIn("2026-10-01", self._dias())

    def test_tempo_email_a_mais(self) -> None:
        for nome, valor in (("user.email", "eu@exemplo.br"), ("trilha.email", "t@t")):
            subprocess.run(["git", "-C", str(self.raiz), "config", nome, valor], check=True)
        self._commit("2026-10-01T10:00:00Z")
        self._ok(**self.SEM_GIT_DA_MAQUINA)
        self.assertEqual(self._dias()["2026-10-01"]["total"], 30)

    def test_tempo_avisa_emails_de_fora(self) -> None:
        subprocess.run(["git", "-C", str(self.raiz), "config", "user.email", "eu@exemplo.br"], check=True)
        self._commit("2026-10-01T10:00:00Z")
        saida = self._ok(**self.SEM_GIT_DA_MAQUINA)
        self.assertIn("t@t", saida.stderr)
        self.assertIn("git config --add trilha.email", saida.stderr)

    def test_tempo_sem_email_configurado(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        self._ok(**self.SEM_GIT_DA_MAQUINA)
        self.assertEqual(self._dias()["2026-10-01"]["total"], 30)

    def test_tempo_commit_a_meia_noite(self) -> None:
        self._commit("2026-10-01T23:30:00Z", nome="a")
        self._commit("2026-10-02T00:00:00Z", nome="b")
        self._ok()
        self.assertEqual(self._dias()["2026-10-02"]["total"], 1)

    def test_tempo_commit_assinado(self) -> None:
        chave = Path(self._tmp.name) / "chave"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(chave)], check=True)
        for nome, valor in (("gpg.format", "ssh"), ("user.signingkey", f"{chave}.pub"),
                            ("log.showSignature", "true")):
            subprocess.run(["git", "-C", str(self.raiz), "config", nome, valor], check=True)
        quando = "2026-10-01T10:00:00Z"
        env = {**os.environ, **GIT_TESTE, "GIT_AUTHOR_DATE": quando, "GIT_COMMITTER_DATE": quando}
        subprocess.run(["git", "-C", str(self.raiz), "commit", "-q", "-S", "--allow-empty", "-m", "a"],
                       check=True, env=env)
        self._ok()
        self.assertIn("2026-10-01", self._dias())

    def test_tempo_data_em_utc_com_z(self) -> None:
        spec = importlib.util.spec_from_file_location("tempo", TEMPO)
        tempo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tempo)
        instantes = tempo._ler_commits("abc123\x00t@t\x002026-10-01T10:00:00Z\nlixo\n", None)
        self.assertEqual(instantes, [datetime.fromisoformat("2026-10-01T10:00:00+00:00").timestamp()])

    def test_tempo_dados_uma_vez(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        self._ok()
        self.assertEqual(self._pagina().count('"dias": ['), 1)

    def test_tempo_nome_com_caracteres_especiais(self) -> None:
        estranho = self._repositorio(Path(self._tmp.name) / "a<b__DADOS__")
        saida = self._rodar(cwd=estranho)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        pagina = self._pagina()
        self.assertIn("<title>Horas de a&lt;b__DADOS__</title>", pagina)
        self.assertEqual(pagina.count('"dias": ['), 1)

    def test_tempo_pasta_trocada(self) -> None:
        self._commit("2026-10-01T10:00:00Z")
        self._ok()
        antigo = next(self._pasta_tempo().glob("*.json"))
        nova = self._repositorio(Path(self._tmp.name) / "b" / "proj")
        saida = self._rodar(cwd=nova)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn(antigo.name, saida.stderr)

    def test_tempo_vizinho_de_nome_parecido(self) -> None:
        vizinho = self._repositorio(Path(self._tmp.name) / "proj-antigo")
        self.assertEqual(self._rodar(cwd=vizinho).returncode, 0)
        self._commit("2026-10-01T10:00:00Z")
        saida = self._ok()
        self.assertNotIn("proj-antigo", saida.stderr)

    # As respostas ao verify e ao code review da change 11

    def _saida_e_volta(self, sessao: str = "s1") -> list[dict]:
        fora = Path(self._tmp.name) / "outra"
        return [self._pedido("2026-10-01T09:00:00Z", self.raiz, sessao),
                self._ia("2026-10-01T09:10:00Z", fora, sessao),
                self._ia("2026-10-01T09:25:00Z", self.raiz, sessao)]

    def test_tempo_conversa_retomada_noutro_arquivo(self) -> None:
        self._conversa(self._saida_e_volta())
        self._conversa(self._saida_e_volta(), pasta="-proj-copia")
        self._ok()
        self.assertNotIn("2026-10-01", self._dias())

    def _resumo_da_2_8(self, conversas: dict) -> Path:
        """Um resumo da versão 1, a da 2.8, no lugar do resumo deste repositório."""
        nome = f"proj-{hashlib.sha1(str(self.raiz).encode('utf-8')).hexdigest()[:8]}.json"
        resumo = self._pasta_tempo() / nome
        resumo.parent.mkdir(parents=True)
        resumo.write_text(json.dumps({"versao": 1, "raiz": str(self.raiz), "conversas": conversas}),
                          encoding="utf-8")
        return resumo

    def test_tempo_horas_a_mais_da_2_8(self) -> None:
        self._conversa(self._saida_e_volta())
        resumo = self._resumo_da_2_8(
            {"s1": [["2026-10-01T09:00:00+00:00", "2026-10-01T09:25:00+00:00", "ia"]]})
        self._ok()
        self.assertNotIn("2026-10-01", self._dias())
        self.assertEqual(json.loads(resumo.read_text(encoding="utf-8"))["versao"], 2)

    def test_tempo_conversa_apagada_no_resumo_antigo(self) -> None:
        self._resumo_da_2_8({"s2": [["2026-10-02T10:00:00+00:00", "2026-10-02T10:20:00+00:00", "ia"]]})
        self._ok()
        self.assertEqual(self._dias()["2026-10-02"]["total"], 20)

    def _commit_de(self, email: str, quando: str) -> None:
        env = {**os.environ, **GIT_TESTE, "GIT_AUTHOR_EMAIL": email, "GIT_AUTHOR_DATE": quando,
               "GIT_COMMITTER_DATE": quando}
        subprocess.run(["git", "-C", str(self.raiz), "commit", "-q", "--allow-empty", "-m", email],
                       check=True, env=env)

    def test_tempo_robo_fora_do_aviso(self) -> None:
        subprocess.run(["git", "-C", str(self.raiz), "config", "user.email", "eu@exemplo.br"], check=True)
        self._commit_de("49699333+dependabot[bot]@users.noreply.github.com", "2026-10-01T10:00:00Z")
        saida = self._ok()
        self.assertNotIn("trilha.email", saida.stderr)

    def test_tempo_aviso_com_tres_emails(self) -> None:
        subprocess.run(["git", "-C", str(self.raiz), "config", "user.email", "eu@exemplo.br"], check=True)
        for numero, email in enumerate(("a@x", "b@x", "c@x", "d@x")):
            self._commit_de(email, f"2026-10-0{numero + 1}T10:00:00Z")
        aviso = next(l for l in self._ok().stderr.splitlines() if "trilha.email" in l)
        self.assertEqual(sum(email in aviso for email in ("a@x", "b@x", "c@x", "d@x")), 3)
        self.assertIn("mais 1", aviso)

    def test_tempo_nome_que_abre_comentario(self) -> None:
        estranho = self._repositorio(Path(self._tmp.name) / "x<!--<script")
        self.assertEqual(self._rodar(cwd=estranho).returncode, 0)
        bloco = re.search(r'<script id="dados" type="application/json">(.*?)</script>',
                          self._pagina(), re.S)
        self.assertIsNotNone(bloco)
        self.assertNotIn("<!--", bloco.group(1))

    def test_tempo_email_com_espaco_e_vazio(self) -> None:
        spec = importlib.util.spec_from_file_location("tempo", TEMPO)
        tempo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tempo)
        saida = ("h1\x00joao silva@x\x002026-10-01T10:00:00+00:00\n"
                 "h2\x00\x002026-10-01T11:00:00+00:00\n")
        fora: dict = {}
        self.assertEqual(tempo._ler_commits(saida, {"eu@x"}, fora), [])
        self.assertEqual(fora, {"joao silva@x": 1})
        self.assertEqual(len(tempo._ler_commits(saida, None)), 2)

    # A segunda revisão do tempo.py (change 12)

    def test_tempo_aninhado_no_resumo_antigo(self) -> None:
        aninhado = self.raiz / "vendor" / "lib"
        subprocess.run(["git", "init", "-q", str(aninhado)], check=True)
        self._conversa([self._pedido("2026-10-01T09:00:00Z", aninhado),
                        self._ia("2026-10-01T09:20:00Z", aninhado)])
        resumo = self._resumo_da_2_8(
            {"s1": [["2026-10-01T09:00:00+00:00", "2026-10-01T09:20:00+00:00", "ia"]]})
        self._ok()
        self.assertNotIn("2026-10-01", self._dias())
        self.assertNotIn("s1", json.loads(resumo.read_text(encoding="utf-8"))["conversas"])

    @staticmethod
    def _modulo_tempo():
        spec = importlib.util.spec_from_file_location("tempo", TEMPO)
        tempo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tempo)
        return tempo

    def test_tempo_arquivo_que_so_cita_a_raiz(self) -> None:
        fora = Path(self._tmp.name) / "outra"
        linhas = [self._pedido("2026-10-01T09:00:00Z", fora, texto=f"veja {self.raiz}")]
        linhas += [self._ia(f"2026-10-01T09:{minuto:02d}:00Z", fora) for minuto in range(1, 40)]
        self._conversa(linhas, pasta="-outra")
        tempo = self._modulo_tempo()
        original, chamadas = tempo._evento, []
        tempo._evento = lambda *args: chamadas.append(1) or original(*args)
        conversas, ignorados = tempo._eventos(self.config, self.raiz, {})
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(len(ignorados), 1)
        self.assertEqual(tempo._intervalos(conversas.get("s1", {})), [])


if __name__ == "__main__":
    unittest.main()
