"""O kit é coerente: a versão, o esqueleto, o verificador e o gerador da página (Python 3 puro)."""

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# A lista dos arquivos do kit vive num lugar só: a ferramenta que cria e atualiza os projetos.
_spec = importlib.util.spec_from_file_location("kit", RAIZ / "ferramentas" / "kit.py")
FERRAMENTA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FERRAMENTA)
DO_KIT = (*FERRAMENTA.SEM_MUDAR, *FERRAMENTA.A_PREENCHER)
ORIGEM = dict(FERRAMENTA.A_PREENCHER)  # destino no projeto → origem no kit
GIT_TESTE = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
             "GIT_COMMITTER_EMAIL": "t@t"}
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
        # O config.yaml vai a todo projeto: também não cita um.
        self.assertNotIn("Consulta Pública", (RAIZ / "openspec/config.yaml").read_text(encoding="utf-8"))

    def test_clear_com_o_comando_da_proxima_sessao(self) -> None:
        """v1.34: quem sugere o /clear mostra o comando exato a dar ao voltar, pronto para copiar."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("e mostre, num bloco de código, o comando exato a dar na próxima sessão", comum)

    def test_comum_sem_repetir_o_openspec_nem_a_si_mesmo(self) -> None:
        """v1.32: a instrução do propose já manda ler o projeto e os specs; o pkill -f num lugar só."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("Antes de propor, rode `openspec list`", comum)
        self.assertNotIn("leia o spec da capability", comum)
        self.assertEqual(comum.count("`pkill -f`"), 1)
        # A trava confere o --merge e a verificação verde, não o passo em que se está.
        self.assertIn("o merge sem `--merge` ou sem a verificação verde", comum)
        self.assertNotIn("merge fora do passo 7", comum)
        self.assertIn("a trava `guarda.py` e o `.githooks/pre-commit`) dispensam change", comum)

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
        # O apply pode ter instrução, mas nunca a que força parada ou commit (a decisão da v1.10).
        apply = config.split("  apply:", 1)[1].split("  archive:", 1)[0] if "  apply:" in config else ""
        for proibido in ("commit", "pare", "parada"):
            self.assertNotIn(proibido, apply.lower())

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
        self.assertIn("numa branch `change/NN-nome` aberta a partir da main atualizada", comum)
        self.assertIn("pull request em rascunho (`gh pr create --draft`)", comum)
        self.assertIn("um só \"sim\" para todos os envios da branch até o merge", comum)
        self.assertIn("`gh pr merge --merge --delete-branch` (merge commit, nunca squash", comum)
        self.assertIn("com um \"sim\" só para ele", comum)

    def test_archive_dentro_do_pull_request(self) -> None:
        """v1.22: o archive e os passos seguintes na branch, antes do merge; depois, o PR sai do rascunho."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("o PR sai do rascunho (`gh pr ready`): código, specs e página chegam juntos à main", comum)
        self.assertIn("7. o merge", comum)

    def test_ci_no_kit_e_merge_so_com_ele_verde(self) -> None:
        """v1.23: o GitHub roda o check.sh e o openspec validate; o merge só é pedido com tudo verde."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        ci = (RAIZ / "github-verificacao.yml").read_text(encoding="utf-8")
        self.assertIn("o merge, só com a verificação do GitHub verde no PR (`gh pr checks`)", comum)
        self.assertIn("run: bash scripts/check.sh", ci)
        self.assertIn("run: openspec validate --all --no-interactive", ci)
        self.assertNotIn("--strict", ci)  # o estrito reprova os avisos que o check.sh aceita
        self.assertRegex(ci, r"@fission-ai/openspec@\d+\.\d+\.\d+")
        # Fora de .github/workflows/ no kit: aqui o check.sh reprovaria, porque o kit não segue o método.
        self.assertFalse((RAIZ / ".github/workflows/verificacao.yml").exists())
        # O CI do próprio kit roda estes testes.
        kit = (RAIZ / ".github/workflows/testes.yml").read_text(encoding="utf-8")
        self.assertIn("run: python3 -m unittest discover -s testes", kit)

    def test_regras_de_verificacao_vindas_do_heimdall(self) -> None:
        """Cada cenário com teste nomeado e evidência; tarefa marcada só com o teste passando."""
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn('Terminar com a seção "Verificação"', config)
        self.assertIn("dá o arquivo, o caso e o comando que o roda", config)
        self.assertIn("nunca o valor literal que o código já usa", config)
        self.assertIn("Marcar a tarefa de um cenário só quando o teste que o comprova passar", config)

    def test_regras_cabem_no_projeto_sem_prd(self) -> None:
        """O comum admite a correção vinda de um spec, sem PRD; as regras que pedem RF dizem o que vale."""
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        regras = config.split("\nrules:\n", 1)[1].split("\noperations:\n", 1)[0]
        for artefato in ("proposal", "specs", "tasks"):
            bloco = re.split(r"\n  (?=\w)", regras.split(f"  {artefato}:\n", 1)[1], maxsplit=1)[0]
            self.assertIn("no projeto ainda sem prd", bloco.lower(), artefato)

    def test_apply_registra_a_verificacao(self) -> None:
        """A regra do design só é lida no propose; quem preenche a Verificação é o apply, com ou sem design.md."""
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        apply = config.split("  apply:", 1)[1].split("  archive:", 1)[0]
        self.assertIn('na seção "Verificação" do design.md', apply)
        self.assertIn("no notas.md da pasta da change quando não houver design.md", apply)
        self.assertIn("nenhum cenário fica comprovado só pela execução manual", apply)

    def test_confere_metodo_se_declara_trava(self) -> None:
        """Desde a 1.27 ele roda na trava do commit e no CI; o texto dele diz isso."""
        texto = (RAIZ / "scripts" / "confere_metodo.py").read_text(encoding="utf-8")
        self.assertNotIn("portão de publicação", texto)
        self.assertIn("na trava do commit (.githooks/pre-commit)", texto)

    def test_ci_com_acoes_fixadas_e_busca_de_segredos(self) -> None:
        """v1.29: ações pelo commit, gitleaks conferido pela soma, Dependabot e a regra dos segredos."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        for arquivo in ("github-verificacao.yml", ".github/workflows/testes.yml"):
            texto = (RAIZ / arquivo).read_text(encoding="utf-8")
            # Também os exemplos comentados: quem os descomenta herda a fixação.
            usos = re.findall(r"^\s+(?:#\s+)?- uses: (\S+)", texto, re.M)
            self.assertTrue(usos, arquivo)
            for uso in usos:
                self.assertRegex(uso, r"@[0-9a-f]{40}$", f"{arquivo}: {uso} sem o commit fixado")
        ci = (RAIZ / "github-verificacao.yml").read_text(encoding="utf-8")
        self.assertIn("sha256sum -c -", ci)
        self.assertIn("gitleaks\" detect --source . --no-banner --redact", ci)
        self.assertIn("fetch-depth: 0", ci)
        self.assertIn("branches: [main, master]", ci)  # o hubia e o heimdall usam master
        for arquivo in ("github-dependabot.yml", ".github/dependabot.yml"):
            self.assertIn("package-ecosystem: github-actions", (RAIZ / arquivo).read_text())
        self.assertIn("o CI os procura no histórico (gitleaks)", comum)

    def test_revisao_independente_no_verify(self) -> None:
        """v1.28: no passo 5, o /code-review por um agente sem o contexto da sessão."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        # Com o alvo: sem ele, o /code-review revisa só o que não foi commitado, vazio depois do commit.
        self.assertIn("5. `/opsx:verify` e a revisão independente do código, o `/code-review <número do PR>`",
                      comum)
        self.assertIn("quem escreveu não é o único a revisar", comum)
        self.assertIn("/code-review <número do PR>", (RAIZ / "mapa-da-trilha.html").read_text())

    def test_a_change_fecha_no_merge(self) -> None:
        """v1.25: a change fecha no merge; a retomada olha o PR; um só lugar para a regra dos envios."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertIn("A change fecha aqui, não no archive", comum)
        self.assertIn("numa branch `change/…`, `gh pr view` e `gh pr checks`", comum)
        self.assertIn("change com o merge feito", comum)
        self.assertNotIn("change arquivada, conferência", comum)
        self.assertIn("fora de change (o PRD, o TDD, a decomposição e o trabalho que dispensa change), o commit vai direto à main", comum)
        self.assertEqual(comum.count("envie só com \"sim\""), 1)
        self.assertIn("o envio ao GitHub segue a regra dos envios", comum)
        self.assertIn("`openspec config profile` e marque também o `verify`", readme)

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
        self.assertIn("pelo checklist da skill `sdd:briefing`", comum)
        self.assertNotIn("checklist de 8 itens", comum)  # v1.30: a contagem é da skill

    def test_andamento_sem_o_envio_e_com_trabalho_fora_de_change(self) -> None:
        """v1.13: o envio ao remoto não vai ao ANDAMENTO.md; a etapa admite trabalho fora de change."""
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertIn("não guarda o estado do envio ao remoto", comum)
        self.assertIn("ou o trabalho fora de change)", comum)
        self.assertIn("a revisão termina com a auditoria aprovada, em commit e envio", comum)

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
        self.assertIn("a tabela \"Ciclo\" da decomposição, atualizada no commit do passo de cada marco", comum)

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
        self.assertIn("um DEVE em português o reprova", config)
        # v1.30: o que o modelo do OpenSpec já pede fica nas instruções dele.
        for repetido in ("não o como", "alternativa rejeitada", "cenário com WHEN/THEN", '"- [ ] N.M'):
            self.assertNotIn(repetido, config)
        # v1.33: a língua fica no context, no bloco que o openspec init --language escreve.
        self.assertNotIn("PT-BR", config[config.find("\nrules:"):])
        self.assertNotIn("títulos", config)

    def test_lingua_no_context_como_o_openspec_escreve(self) -> None:
        """O bloco de formatLanguageContext (core/init.js do OpenSpec): o init --language o reconhece."""
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        contexto = config[config.find("context: |\n"):config.find("\nrules:")]
        contexto = "\n".join(linha[2:] for linha in contexto.splitlines()[1:])
        self.assertIn(FERRAMENTA.LINGUA, contexto)
        self.assertTrue(FERRAMENTA.LINGUA.startswith(
            "Language: pt-BR\nAll artifacts must be written in pt-BR.\n"
            "Keep OpenSpec structural headings and SHALL/MUST keywords in English.\n"))
        self.assertIn("accents", FERRAMENTA.LINGUA)  # o hubia já perdeu acentos em textos de tela

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
            for nome in (*DO_KIT, "ferramentas/kit.py")
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

    def test_verificador_reprova_passo_numerado_do_comum_repetido(self) -> None:
        passo = next(linha for linha in (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8").splitlines()
                     if linha.startswith("2. "))
        erro = self._verifica_com_defeito("CLAUDE.md", "- Nenhuma.", f"- Nenhuma.\n\n{passo}")
        self.assertIn("repete regra do comum: 2. ", erro)

    def test_verificador_avisa_os_campos_do_modelo_por_preencher(self) -> None:
        """Cada campo < > dos modelos é cobrado como aviso, e só ele: o projeto pode usar < > no texto."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            regras = [sys.executable, "-I", str(destino / "scripts/confere_regras.py"), tmp]
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
        spec = importlib.util.spec_from_file_location("regras", RAIZ / "scripts/confere_regras.py")
        regras = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(regras)
        for nome, campos in regras.CAMPOS_DO_MODELO.items():
            texto = (RAIZ / ORIGEM[nome]).read_text(encoding="utf-8").split("\nrules:")[0]
            if nome.endswith(".yaml"):  # sem os comentários ("o que está entre < e >")
                texto = "\n".join(l for l in texto.splitlines() if not l.lstrip().startswith("#"))
            trechos = [(m.start(), m.end()) for c in campos for m in re.finditer(re.escape(c), texto)]
            for campo in campos:
                self.assertIn(campo, texto, f"{nome}: {campo} não está no modelo")
            for achado in re.finditer(r"<[^<>]+>", texto):
                self.assertTrue(any(a < achado.end() and achado.start() < b for a, b in trechos),
                                f"{nome}: {achado.group()} fora de CAMPOS_DO_MODELO")

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
                [sys.executable, "-I", str(destino / "scripts/gerar_pagina_sdd.py")],
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
        config = (RAIZ / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn('célula do archive ("PR #N")', config)

    def test_pagina_funciona_sem_rede_e_se_chama_documentacao_do_projeto(self) -> None:
        modelo = (RAIZ / "scripts/pagina_sdd_modelo.html").read_text(encoding="utf-8")
        gerador = (RAIZ / "scripts/gerar_pagina_sdd.py").read_text(encoding="utf-8")
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("<script src=", modelo)
        self.assertIn("marked v12.0.2", modelo)
        self.assertNotIn("</script", modelo.split("marked v12.0.2", 1)[1].split("\n</script>", 1)[0])
        self.assertIn('f"{nome}: documentação"', gerador)
        self.assertIn("é a documentação do projeto, gerada", comum)
        for texto in (modelo, gerador, comum):
            self.assertNotIn("página do método", texto)

    def test_modelo_da_pagina_tem_teclado_celular_e_rodape_corretos(self) -> None:
        modelo = (RAIZ / "scripts/pagina_sdd_modelo.html").read_text(encoding="utf-8")
        self.assertIn("ArrowRight", modelo)
        self.assertIn('document.getElementById("aba-" + chave).focus()', modelo)
        self.assertIn(".briefings > li {", modelo)
        self.assertNotIn(".briefings li {", modelo)
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
                [sys.executable, "-I", str(RAIZ / "scripts/guarda.py")],
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
            self.assertEqual(ligado, ".githooks")
            self.assertIn("scripts/guarda.py", (pasta / ".claude/settings.json").read_text())
            subprocess.run(["git", "add", "-A"], cwd=pasta, check=True)
            ok = subprocess.run(["git", "commit", "-qm", "kit"], cwd=pasta, env=env,
                                capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            claude = pasta / "CLAUDE.md"
            claude.write_text(claude.read_text(encoding="utf-8").replace("@CLAUDE-comum.md", ""))
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
            self.assertIn("scripts/guarda.py", json.dumps(dados["hooks"]))
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
        comum = pasta / "CLAUDE-comum.md"
        comum.write_text(re.sub(r"^Versão [\d.]+,", "Versão 1.19,", comum.read_text(encoding="utf-8"),
                                flags=re.M), encoding="utf-8")
        (pasta / ".github/workflows/verificacao.yml").write_text("# a parte da stack, preenchida\n")
        subprocess.run(["git", "add", "-A"], cwd=pasta, check=True)
        subprocess.run(["git", "commit", "-qm", "kit"], cwd=pasta, check=True, env=env)
        return pasta

    def test_ferramenta_cria_projeto_novo_e_recusa_pasta_cheia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp) / "novo"
            saida = self._ferramenta("novo", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stderr)
            for destino, origem in ORIGEM.items():
                self.assertEqual((pasta / destino).read_bytes(), (RAIZ / origem).read_bytes())
            for nome in FERRAMENTA.SEM_MUDAR:
                self.assertEqual((pasta / nome).read_bytes(), (RAIZ / nome).read_bytes())
            self.assertTrue((pasta / "sdd").is_dir())
            self.assertIn("gh repo create", saida.stdout)
            self.assertIn("README do kit, passos 3 a 6", saida.stdout)
            self.assertEqual(self._ferramenta("novo", str(pasta)).returncode, 1)

    def test_ferramenta_atualiza_so_o_que_se_copia_sem_mudar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = self._projeto_velho(tmp)
            saida = self._ferramenta("atualizar", str(pasta))
            self.assertEqual(saida.returncode, 0, saida.stdout + saida.stderr)
            self.assertEqual((pasta / "CLAUDE-comum.md").read_bytes(),
                             (RAIZ / "CLAUDE-comum.md").read_bytes())
            # O que o projeto preencheu fica como está.
            self.assertEqual((pasta / ".github/workflows/verificacao.yml").read_text(),
                             "# a parte da stack, preenchida\n")
            versao = re.search(r"^Versão (\d+\.\d+)", (RAIZ / "CLAUDE-comum.md").read_text(
                encoding="utf-8"), re.M).group(1)
            self.assertIn(f"comum 1.19 → {versao}", saida.stdout)
            # A ferramenta não faz commit.
            self.assertIn("CLAUDE-comum.md", subprocess.run(
                ["git", "status", "--short"], cwd=pasta, capture_output=True, text=True).stdout)

    def test_atualizar_sincroniza_so_as_regras_que_vieram_do_kit(self) -> None:
        env = {**os.environ, **GIT_TESTE}
        antigo = subprocess.run(["git", "show", "v1.25:openspec/config.yaml"], cwd=RAIZ,
                                capture_output=True, text=True, check=True).stdout
        atual = (RAIZ / "openspec/config.yaml").read_text(encoding="utf-8")
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
            comum = pasta / "CLAUDE-comum.md"
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
            atual = (RAIZ / "github-verificacao.yml").read_text(encoding="utf-8")
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
