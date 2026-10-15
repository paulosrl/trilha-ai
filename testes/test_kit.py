"""O kit é coerente: a versão, o esqueleto, o verificador e o gerador da página (Python 3 puro)."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DO_KIT = (
    "CLAUDE-comum.md",
    "CLAUDE.md",
    "ANDAMENTO.md",
    "openspec/config.yaml",
    "scripts/check.sh",
    "scripts/confere_regras.py",
    "scripts/confere_metodo.py",
    "scripts/gerar_pagina_sdd.py",
    "scripts/pagina_sdd_modelo.html",
    ".gitignore",
    ".github/workflows/verificacao.yml",
)
# O que no repositório novo tem outro nome no kit.
ORIGEM = {"CLAUDE.md": "esqueleto-CLAUDE.md", ".github/workflows/verificacao.yml": "github-verificacao.yml"}
ESQUELETO_DO_CLAUDE = RAIZ / "CLAUDE.md"  # o deste repositório não é o esqueleto; o esqueleto é copiado abaixo


def _copia_do_kit(destino: Path) -> None:
    for nome in DO_KIT:
        alvo = destino / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RAIZ / ORIGEM.get(nome, nome), alvo)


class Kit(unittest.TestCase):
    def test_arquivos_existem(self) -> None:
        faltam = [n for n in DO_KIT if not (RAIZ / ORIGEM.get(n, n)).is_file()]
        self.assertEqual(faltam, [])

    def test_versao_no_comum(self) -> None:
        for arquivo in ("CLAUDE-comum.md",):
            texto = (RAIZ / arquivo).read_text(encoding="utf-8")
            self.assertIsNotNone(re.search(r"^Versão \d+\.\d+, de \d{4}-\d\d-\d\d\.", texto, re.M), arquivo)

    def test_comum_nao_cita_curso(self) -> None:
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("curso", comum.lower().replace("em curso", ""))

    def test_comum_fecha_a_porta_do_briefing_curto(self) -> None:
        """v1.8: sem decomposição, o passo do ciclo fica no ANDAMENTO.md; com PRD e TDD, a decomposição vem antes."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("o passo do ciclo de cada change fica no `ANDAMENTO.md`", comum)
        self.assertIn("Com o PRD e o TDD aprovados, a decomposição vem antes de qualquer change.", comum)

    def test_comum_preve_o_registro_de_processo_opcional(self) -> None:
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("registro de processo", comum)
        self.assertIn("é opcional; quem o mantém declara no `CLAUDE.md`", comum)

    def test_comum_cita_a_skill_briefing(self) -> None:
        """A skill do plugin chama-se sdd:briefing, para não colidir com a openspec-propose nativa do OpenSpec."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("`sdd:briefing`", comum)
        self.assertNotIn("openspec-propose", comum)

    def test_comum_poe_a_auditoria_na_revisao_do_openspec(self) -> None:
        """v1.9: a auditoria do gate 3 é a revisão que o OpenSpec pede ao fim do propose, não um passo à parte."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("a revisão dos artefatos, que o OpenSpec pede ao fim do propose, antes do apply, feita como a auditoria do gate 3", comum)
        self.assertNotIn("3. auditoria do gate 3, antes de qualquer código", comum)

    def test_metodo_nao_forca_o_apply(self) -> None:
        """v1.10: o apply segue o fluxo do OpenSpec; nem commit por tarefa nem parada forçada."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("4. `/opsx:apply`, no fluxo do OpenSpec;", comum)
        self.assertIn("Durante o apply, o ponto de retomada é o `tasks.md`", comum)
        self.assertNotIn("um por tarefa concluída", comum)
        self.assertNotIn("o apply para nela", comum)
        self.assertNotIn("commit por tarefa", config)
        self.assertNotIn("  apply:", config)

    def test_specs_com_o_nome_do_openspec(self) -> None:
        """v1.11: só as changes levam número e data; os specs seguem o nome que o OpenSpec dá."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Os specs seguem o nome que o OpenSpec dá", comum)
        self.assertNotIn("changes e specs seguem `AAAA-MM-DD-NN-nome`", comum)
        self.assertNotIn("spec novo recebe o próximo número e a data do dia", comum)

    def test_auditoria_nao_e_unidade_de_trabalho(self) -> None:
        """v1.12: até a escolha do usuário, a auditoria não muda o ANDAMENTO.md nem o registro de processo."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Até a escolha, a auditoria não é unidade de trabalho", comum)

    def test_correcao_de_texto_nao_sobe_versao(self) -> None:
        """v1.14: só a mudança de sentido sobe a versão do PRD, do TDD ou da decomposição."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("não sobe a versão dele nem a linha \"de origem\" de quem o cita", comum)
        self.assertIn("Só a mudança de sentido é versão nova, aprovada pelo usuário", comum)

    def test_prd_e_spec_em_desacordo(self) -> None:
        """v1.15: o PRD aprovado manda sobre o spec; se o certo for o spec, o PRD ganha versão nova."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("PRD e spec em desacordo: vale o PRD aprovado", comum)
        self.assertIn("se o certo for o spec, o PRD ganha versão nova", comum)

    def test_regras_gerais_vindas_dos_repositorios(self) -> None:
        """v1.16: o "sim" isolado, o que ler antes do propose e a mutação desfeita saem dos CLAUDE.md."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Um \"sim\" isolado responde só à pergunta principal da mensagem", comum)
        self.assertIn("rode `openspec list`", comum)
        self.assertIn("(`progress.total`)", comum)
        self.assertIn("desfaça-a por edição inversa, nunca com `git checkout`", comum)

    def test_remoto_privado_no_github(self) -> None:
        """v1.20: todo repositório do método tem um remoto privado no GitHub, criado na etapa 0."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertIn("desde a etapa 0, um remoto privado no GitHub (`origin`)", comum)
        self.assertIn("`gh repo create <nome> --private --source . --push`", comum)
        self.assertIn("`gh auth login`", readme)
        self.assertIn("`gh repo create <nome> --private --source . --push`", readme)

    def test_branch_e_pull_request_por_change(self) -> None:
        """v1.21: cada change numa branch; PR em rascunho ao fim do propose; um "sim" para os envios, outro para o merge."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Cada change vive numa branch `change/NN-nome`", comum)
        self.assertIn("pull request em rascunho (`gh pr create --draft`)", comum)
        self.assertIn("pedem um só \"sim\", dado no começo da change e válido até o merge", comum)
        self.assertIn("O merge na main (`gh pr merge --merge --delete-branch`: merge commit, nunca squash", comum)
        self.assertIn("pede o seu próprio \"sim\"", comum)

    def test_archive_dentro_do_pull_request(self) -> None:
        """v1.22: o archive e os passos seguintes na branch, antes do merge; depois, o PR sai do rascunho."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("O archive e os passos do `operations.archive` acontecem na branch, antes do merge", comum)
        self.assertIn("o PR sai do rascunho (`gh pr ready`)", comum)

    def test_ci_no_kit_e_merge_so_com_ele_verde(self) -> None:
        """v1.23: o GitHub roda o check.sh e o openspec validate; o merge só é pedido com tudo verde."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        ci = (RAIZ / "github-verificacao.yml").read_text(encoding="utf-8")
        self.assertIn("só é pedido com a verificação do GitHub verde no PR (`gh pr checks`)", comum)
        self.assertIn("run: bash scripts/check.sh", ci)
        self.assertIn("run: openspec validate --all --strict --no-interactive", ci)
        self.assertRegex(ci, r"@fission-ai/openspec@\d+\.\d+\.\d+")
        # Fora de .github/workflows/ no kit: aqui o check.sh reprovaria, porque o kit não segue o método.
        self.assertFalse((RAIZ / ".github/workflows/verificacao.yml").exists())

    def test_versao_nova_atualiza_a_origem_sem_versao(self) -> None:
        """v1.16: a versão nova de sentido muda a linha "de origem" de quem cita, sem versão nova dele."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("atualiza a linha \"de origem\" de quem o cita, sem versão nova dele", comum)

    def test_ciclo_guarda_os_marcos_e_o_andamento_o_passo(self) -> None:
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("O passo do ciclo em que cada change está: a tabela", comum)
        self.assertIn("Os marcos de cada change (briefing, auditoria, archive): a tabela \"Ciclo\"", comum)

    def test_auditoria_tem_criterio_de_fechamento(self) -> None:
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Uma auditoria fecha com a verificação do repositório verde e sem contradição", comum)

    def test_hora_do_andamento_lida_do_relogio(self) -> None:
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("a hora, lida do relógio (`date`) e nunca estimada", comum)

    def test_archive_gera_a_pagina(self) -> None:
        """v1.13: os passos depois do archive vivem só no config.yaml; o comum aponta para lá."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        esqueleto = (RAIZ / "esqueleto-CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("os passos que o `operations.archive` do `openspec/config.yaml` lista", comum)
        self.assertNotIn("página do método gerada de novo", comum)
        self.assertIn("gerar de novo sdd/documentacao.html", config)
        self.assertNotIn("gerar_pagina_sdd", esqueleto)

    def test_regras_do_metodo_num_lugar_so(self) -> None:
        """v1.13: o teste por cenário fica no config.yaml e os 8 itens da auditoria, na skill."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("Cada cenário de spec vira um teste", comum)
        self.assertNotIn("todo requisito virou spec", comum)
        self.assertIn("pelo checklist de 8 itens da skill `sdd:briefing`", comum)

    def test_andamento_sem_o_envio_e_com_trabalho_fora_de_change(self) -> None:
        """v1.13: o envio ao remoto não vai ao ANDAMENTO.md; a etapa admite trabalho fora de change."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("não guarda o estado do envio ao remoto", comum)
        self.assertIn("ou o trabalho fora de change)", comum)
        self.assertIn("quando a auditoria do gate 3 for aprovada", comum)

    def test_gates_aprovados_como_as_skills_pedem(self) -> None:
        """v1.17: PRD e TDD são aprovados bloco a bloco, como as skills pedem; a restrição imposta é exceção."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("seção por seção", comum)
        self.assertIn("aprovado bloco a bloco pelo usuário, como a skill pede (gate 1)", comum)
        self.assertIn("aprovado bloco a bloco pelo usuário, como a skill pede (gate 2)", comum)
        self.assertIn("salvo a restrição que o usuário declara imposta de fora", comum)

    def test_ciclo_sem_repetir_o_config_e_com_o_lugar_do_verify(self) -> None:
        """v1.17: a execução manual fica só no config.yaml; o verify responde no design.md; a sugestão
        de um comando do OpenSpec que pule passo não vale; a aprovação do gate 3 é unidade de trabalho."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("execução manual, em dado descartável, com o usuário olhando", comum)
        self.assertIn("recusada por escrito no `design.md` da change, com o motivo", comum)
        self.assertIn("a aprovação do gate 3 atualiza também o \"Ciclo\"", comum)

    def test_auditoria_fechada_no_registro_copia_sem_change_e_o_openspec_comanda(self) -> None:
        """v1.18: a escolha do usuário, com ou sem correção, leva o relatório ao registro; a cópia nova
        dos arquivos do método dispensa change; o OpenSpec comanda, e o método nunca se sobrepõe a ele:
        quando um comando oferece pular um passo, quem escolhe é o usuário."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("o relatório entra no registro junto com a primeira correção", comum)
        self.assertIn("A escolha, com ou sem correção, é unidade de trabalho", comum)
        self.assertIn("a cópia nova dos arquivos que o método manda copiar sem mudar", comum)
        self.assertIn("O OpenSpec comanda: o método nunca se sobrepõe ao fluxo dele", comum)
        self.assertIn("quem escolhe é o usuário, com a recomendação de não pular", comum)
        self.assertNotIn("vale este arquivo", comum)
        self.assertNotIn("não vale (arquivar sem o verify", comum)
        self.assertNotIn("sem pular etapa", comum)

    def test_config_nao_repete_o_comum_nem_o_claude(self) -> None:
        """v1.17: o contexto do config.yaml aponta para o comum e o CLAUDE.md, que o agente já carrega."""
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertNotIn("Não improvise", config)
        self.assertNotIn("Dados a proteger", config)
        self.assertNotIn("Documentos que mandam", config)
        self.assertIn("CLAUDE-comum.md e no CLAUDE.md, que o agente já carrega; este contexto não as repete", config)

    def test_metodo_sem_sobrepor_o_openspec(self) -> None:
        """v1.19: o design.md é do OpenSpec, que o cria só quando cabe (o notas.md o substitui); os specs
        mudam também pela edição que o OpenSpec pede; o gate 3 aceita o caminho que o update indicar;
        as regras do config.yaml sem o MAY e com os títulos do OpenSpec em inglês."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("o OpenSpec o cria só quando cabe", comum)
        self.assertIn("o `notas.md` da pasta da change faz as vezes dele", comum)
        self.assertNotIn("Não edite `openspec/specs/` à mão", comum)
        self.assertIn("a edição direta que as instruções dele pedem", comum)
        self.assertIn("ou pelo caminho que ele indicar", comum)
        self.assertNotIn("MAY (RFC 2119)", config)
        self.assertIn("o OpenSpec pede evitar SHOULD e MAY", config)
        self.assertEqual(config.count("mantendo em inglês os títulos do modelo do OpenSpec"), 2)

    def test_cenario_mantido_no_delta_fica_como_esta(self) -> None:
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("todo cenário novo ou alterado cita o CA de origem", config)
        self.assertIn("o que o delta repete sem mudança fica como está", config)

    def test_tarefas_nomeiam_o_requisito_sem_criterio(self) -> None:
        """A regra de tarefas do config.yaml (a única que há) cobre o cenário sem critério."""
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("ou o do requisito quando o cenário não tem critério", config)

    def test_regras_do_config_sao_texto(self) -> None:
        """Item sem aspas com ": " vira chave e valor no YAML, e o OpenSpec ignora em silêncio todas as
        regras daquele artefato ("must be an array of strings"); com " #", o resto vira comentário."""
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        depois_do_contexto = config.split("\nrules:\n", 1)[1]
        soltos = [
            linha.strip()
            for linha in depois_do_contexto.splitlines()
            if re.match(r"\s+- (?![\"'])", linha) and (": " in linha or " #" in linha)
        ]
        self.assertEqual(soltos, [])

    def test_regras_falam_do_usuario(self) -> None:
        for arquivo in ("CLAUDE-comum.md", "esqueleto-CLAUDE.md"):
            texto = (RAIZ / arquivo).read_text(encoding="utf-8")
            self.assertNotRegex(texto, r"\b[àa] pessoa\b", arquivo)

    def test_scripts_cabem_no_lint_de_quem_copia(self) -> None:
        # Os scripts são copiados sem mudança; um projeto Python com o ruff (limite de 100) os reprovaria.
        longas = [
            f"{nome}:{numero}"
            for nome in DO_KIT
            if nome.endswith(".py")
            for numero, linha in enumerate((RAIZ / nome).read_text(encoding="utf-8").splitlines(), 1)
            if len(linha) > 100
        ]
        self.assertEqual(longas, [])

    def test_verificador_aprova_um_repositorio_feito_do_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            saida = subprocess.run(
                [sys.executable, "-I", str(destino / "scripts/confere_regras.py"), tmp, "--fonte", str(RAIZ)],
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
                [sys.executable, "-I", str(destino / "scripts/confere_regras.py"), tmp],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(saida.returncode, 1, saida.stdout + saida.stderr)
            return saida.stderr

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

    def _confere_metodo(self, destino: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", str(destino / "scripts/confere_metodo.py"), *args],
            capture_output=True, text=True, check=False,
        )

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
                [sys.executable, "-I", str(destino / "scripts/gerar_pagina_sdd.py")],
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
                [sys.executable, "-I", str(destino / "scripts/gerar_pagina_sdd.py")],
                capture_output=True, text=True, check=True,
            )
            pagina = (destino / "sdd/documentacao.html").read_text(encoding="utf-8")
            self.assertIn('"estado": "retirada"', pagina)
            self.assertIn(".selo.retirada", pagina)


if __name__ == "__main__":
    unittest.main()
