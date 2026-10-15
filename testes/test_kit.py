"""O kit é coerente: a versão, o esqueleto, o verificador e o gerador da página (Python 3 puro)."""

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
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


def setUpModule() -> None:
    """Toda conferência dos testes vê um `claude` que falha, nunca o da máquina: o aviso do plugin
    depende do que está instalado nela. Os testes do aviso trocam este por outro."""
    _claude_falso(Path(_SEM_CLAUDE.name), "exit 1")
    os.environ["PATH"] = f"{_SEM_CLAUDE.name}:{os.environ['PATH']}"


def tearDownModule() -> None:
    os.environ["PATH"] = _PATH_ORIGINAL
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
            (Path(tmp) / "sdd").mkdir()
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

    def test_regras_de_verificacao_vindas_do_heimdall(self) -> None:
        """Cada cenário com teste nomeado e evidência; tarefa marcada só com o teste passando."""
        config = (MODELO / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn('Terminar com a seção "Verificação"', config)
        self.assertIn("dá o arquivo, o caso e o comando que o roda", config)
        self.assertIn("nunca o valor literal que o código já usa", config)
        self.assertIn("Marcar a tarefa de um cenário só quando o teste que o comprova passar", config)

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
        """v1.28: no passo 5, o /code-review por um agente sem o contexto da sessão."""
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

    def _avisos_da_stack(self, com_tdd: bool, preenchida: bool = False) -> list[str]:
        """As linhas de aviso da stack da conferência das regras num projeto feito do kit."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            (destino / "sdd").mkdir()
            if com_tdd:
                (destino / "sdd/tdd-x.md").write_text("# TDD\n", encoding="utf-8")
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
        avisos = self._avisos_da_stack(com_tdd=True)
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
            (destino / "sdd").mkdir()
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
        self.assertIn("scripts/check.sh", aviso)  # os outros três seguem por preencher
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
                         vizinho: bool = False) -> subprocess.CompletedProcess[str]:
        """A conferência num projeto feito do kit, com o comum na versão dada e um `claude` falso
        que lista os plugins dados; com vizinho, uma pasta pipeline-prd-tdd-openspec ao lado."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "projeto"
            _copia_do_kit(destino)
            comum = destino / "trilha/CLAUDE-comum.md"
            comum.write_text(re.sub(r"^Versão [\d.]+,", f"Versão {versao_do_comum},",
                                    comum.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
            if vizinho:
                manifesto = Path(tmp) / "pipeline-prd-tdd-openspec/plugins/sdd/.claude-plugin"
                manifesto.mkdir(parents=True)
                (manifesto / "plugin.json").write_text('{"name": "sdd", "version": "9.9.9"}')
            texto = lista if isinstance(lista, str) else json.dumps(lista)
            return self._confere_metodo(destino, claude=f"printf '%s' '{texto}'")

    def test_plugin_conferido_sem_a_pasta_vizinha(self) -> None:
        lista = [{"id": "sdd@trilha-ai", "version": "1.35.0", "scope": "user", "enabled": True}]
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
        aviso = next(l for l in saida.stderr.splitlines() if "plugin sdd" in l)
        self.assertIn("1.34.0", aviso)
        self.assertIn("1.35", aviso)

    def test_plugin_com_versao_igual_nao_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "sdd@trilha-ai", "version": "1.35.0"}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertNotIn("plugin sdd", saida.stderr)

    def test_plugin_ausente_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "outro@lugar", "version": "1.0.0"}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("plugin sdd não instalado", saida.stderr)
        self.assertIn("claude plugin install sdd@trilha-ai", saida.stderr)

    def test_plugin_de_outro_marketplace_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "sdd@meu-fork", "version": "0.3.9", "enabled": True}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        aviso = next(l for l in saida.stderr.splitlines() if "plugin sdd" in l)
        self.assertIn("sdd@meu-fork", aviso)
        self.assertIn("claude plugin install sdd@trilha-ai", aviso)

    def test_aviso_do_plugin_com_comandos_separados(self) -> None:
        for lista in ([{"id": "sdd@pipeline-prd-tdd-openspec", "version": "0.3.9"}], []):
            avisos = [l for l in self._aviso_do_plugin(lista).stderr.splitlines() if "plugin sdd" in l]
            self.assertEqual(len(avisos), 1, lista)
            self.assertIn("`claude plugin marketplace add paulosrl/trilha-ai`", avisos[0])
            self.assertIn("`claude plugin install sdd@trilha-ai`", avisos[0])
            self.assertNotIn("&&", avisos[0])

    def test_plugin_desligado_avisa(self) -> None:
        saida = self._aviso_do_plugin([{"id": "sdd@trilha-ai", "version": "1.35.0", "enabled": False}])
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("claude plugin enable sdd@trilha-ai", saida.stderr)

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

    def test_metodo_aprova_um_repositorio_feito_do_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            saida = self._confere_metodo(destino, "--vizinho", "outro")
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertIn("sem a pasta sdd/: crie-a com `mkdir sdd`", saida.stderr)
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
            (destino / "sdd").mkdir()
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
            (destino / "sdd").mkdir()
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
            (destino / "sdd").mkdir()
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


    def _guarda(self, comando: str, gh_sai_com: int = 0) -> subprocess.CompletedProcess:
        """Roda a trava com um gh falso no PATH, que sai com o código pedido."""
        import json

        with tempfile.TemporaryDirectory() as tmp:
            gh = Path(tmp) / "gh"
            gh.write_text(f"#!/bin/sh\nexit {gh_sai_com}\n")
            gh.chmod(0o755)
            env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}"}
            return subprocess.run(
                [sys.executable, "-I", str(MODELO / "trilha/guarda.py")],
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

    def _ferramenta(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", str(RAIZ / "ferramentas/kit.py"), *args],
            capture_output=True, text=True, check=False,
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
            proprio = pasta / ".githooks/pre-push"
            proprio.write_text("#!/bin/sh\necho o pre-push do projeto\n", encoding="utf-8")
            self._commit_tudo(pasta, "um hook do projeto")
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertEqual(proprio.read_text(encoding="utf-8"), "#!/bin/sh\necho o pre-push do projeto\n")
            self.assertFalse((pasta / ".githooks/pre-commit").exists())
            self.assertIn(".githooks/pre-push não roda mais", saida.stdout)

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
            self.assertNotIn("a parte fixa de scripts/check.sh mudou", saida.stdout)
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
            self.assertIn("a parte fixa de .github/workflows/verificacao.yml mudou no kit desde a 1.29",
                          saida.stdout)
            self.assertIn("+ branches: [main, master]", saida.stdout)
            self.assertIn("- run: openspec validate --all --strict --no-interactive", saida.stdout)
            self.assertNotIn("dependabot.yml mudou", saida.stdout)
            self.assertEqual(ci.read_text(encoding="utf-8"), antigo + stack)  # só o aviso
            # Com as linhas novas trazidas à mão, o aviso some, mesmo com a stack do projeto.
            atual = (MODELO / ".github/workflows/verificacao.yml").read_text(encoding="utf-8")
            ci.write_text(atual + stack, encoding="utf-8")
            comum.write_text(re.sub(r"^Versão [\d.]+,", "Versão 1.29,", comum.read_text(encoding="utf-8"),
                                    flags=re.M), encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", "de volta à 1.29"], cwd=pasta, env=env, check=True)
            self.assertNotIn("a parte fixa", self._ferramenta("atualizar", str(pasta)).stdout)

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


if __name__ == "__main__":
    unittest.main()
