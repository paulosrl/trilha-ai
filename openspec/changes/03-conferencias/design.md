# Design

## Context

Desde a 2.0, as conferências que os projetos rodam estão em `modelo/trilha/`: o `confere_metodo.py` (decomposição, TDD, `ANDAMENTO.md`, plugin) e o `confere_regras.py` (o `CLAUDE.md`, o comum, o `ANDAMENTO.md`, a cópia da pasta `trilha/`, os avisos das travas e dos campos `< >`). Hoje a decomposição é lida com `"## 1." in texto` e cortada em `"## 2."`; o limite das regras é só de linhas (`LIMITE_DE_LINHAS = 200`); a lista de plugins espera 10 segundos, um número solto no `subprocess.run`. O comum tem 15.426 bytes; o maior `CLAUDE.md` de projeto real (heimdall) tem 13.773. A motivação está em proposal.md; os requisitos, nos specs.

## Goals / Non-Goals

**Goals:**
- Cada conferência nova se apoia num texto que o kit controla (o esqueleto da skill, os modelos), e um teste do kit prova que esse texto existe.
- Os avisos novos não barram o commit: a etapa entre o TDD aprovado e a stack preenchida é legítima.

**Non-Goals:**
- Conferir o conteúdo da stack preenchida (se o lint roda, se os testes existem): a stack é do projeto.
- Mudar o OpenSpec ou o perfil dele: o `kit.py` só lê o perfil.
- Reescrever o comum além do teto e da versão (item 8 do plano).

## Decisions

**1. Títulos da decomposição por linha.** A decomposição é lida por linhas de título: a seção 1 vai da linha que começa com `## 1.` até o título `## ` seguinte, e o "Ciclo" da linha que começa com `## Ciclo` até o título seguinte. Assim valem outras seções entre a 2 e o "Ciclo", como a skill permite, e `### 1. Recepção` não passa por `## 1.`. A falha lista cada título que falta e termina com "como no esqueleto da skill `sdd:briefing`". Alternativa: manter a busca por texto e só trocar a mensagem — descartada, porque o `## 2.` ausente faz a seção 1 engolir o "Ciclo", e a comparação das duas tabelas passa sem conferir nada.

**2. Stack por marcador do modelo.** Cada um dos cinco lugares tem, no modelo do kit, um texto que pede o preenchimento: a linha `echo "aviso: a parte da stack ainda não foi preenchida…"` do `check.sh`, "Troque o comentário pelos passos reais" do CI, "Parte da stack, decidida no TDD (etapa 2)" do Dependabot, "(apague se a stack decidida no TDD for outra)" do `.gitignore` e o campo `<linguagem e versão` do `config.yaml`. O lugar fica pendente enquanto traz esse texto; preencher é trocar ou apagar o texto, como os próprios modelos pedem. Os marcadores ficam numa tabela do `confere_regras.py`, e um teste do kit confere que cada um está no modelo correspondente, como o `test_campos_do_verificador_sao_os_dos_modelos` faz com os campos `< >`. O aviso é uma linha só, com os lugares pendentes, remetendo à regra do gate 2 do comum. Alternativa: comparar o arquivo inteiro com o modelo — descartada, porque o projeto muda a parte fixa por outros motivos (os `--vizinho`) e o aviso viraria ruído. Alternativa: falhar em vez de avisar — descartada pelo goal do commit entre o TDD e a stack.

**3. Teto em bytes, 32 KB, com o comum em metade.** O tamanho é medido em bytes do arquivo (UTF-8), o que o próprio arquivo diz sem depender de contagem de tokens; acento conta dois, o que só aperta um pouco. O teto dos projetos é 32.768 bytes para o comum e o `CLAUDE.md` somados: cabe o maior projeto real (29,2 KB) e corresponde a cerca de 160 bytes por linha nas 200 linhas. No kit, um teste segura o comum sozinho em 16.384 bytes, metade do teto, para que todo projeto tenha a outra metade; a regra do `CLAUDE.md` do kit passa a dizê-lo, ao lado das 200 linhas do comum com o esqueleto. Alternativa: largura máxima de linha — descartada, porque o comum usa um item por linha, e o teto de linha forçaria quebrar itens sem reduzir o tamanho. Alternativa: 16 KB para a soma, como a auditoria sugeriu de exemplo — descartada, porque o comum sozinho já tem 15,4 KB.

**4. Perfil lido por `openspec config list --json`.** O verify está ligado quando o `profile` é `custom` e `workflows` o inclui; no perfil `core`, o OpenSpec ignora a lista e usa a dele, sem o verify (`getProfileWorkflows`, em `core/profiles.js` da 1.14.1). Sem o comando, ou com uma saída que não seja JSON, a ferramenta avisa que o OpenSpec falta ou não respondeu. O aviso vem depois dos próximos passos, que ganham o `openspec config profile` antes do `openspec init`. O aviso do `atualizar`, que olha o projeto (`.claude/**verify*`), fica como está. Alternativa: `openspec config get workflows` — descartada, porque responde a lista mesmo com o perfil `core`, que não a usa.

**5. Prazo como constante.** `PRAZO_DO_CLAUDE = 10` no `confere_metodo.py`; o teste importa o módulo, baixa o prazo para uma fração de segundo e põe no PATH um `claude` que dorme (`exec sleep`), para não esperar 10 segundos nem deixar processo filho. A conferência chama a lista com esse prazo e trata o estouro como hoje, em silêncio.

**6. Critério da limpeza dos testes (F31).** Sai o `assertNotIn` que confere a ausência de uma frase que uma versão antiga tinha e que o `assertIn` da frase nova já cobre (por exemplo, "leia o spec da capability", "seção por seção", "merge fora do passo 7"). Fica o que guarda uma regra viva, independente da redação: o comum sem curso e o `config.yaml` sem nome de projeto, o `config.yaml` sem repetir o comum nem as instruções do OpenSpec, a língua só no `context`, o apply sem commit nem parada forçada, o CI sem `--strict`, a página sem script de fora, o esqueleto sem citar o gerador da página e todos os `assertNotIn` de comportamento (saídas das conferências e da ferramenta). Testes que ficam vazios saem; os que guardam outras frases ficam com elas.

**7. Versão 2.1.** Muda o que o projeto recebe (as conferências e o comum), sem quebrar caminho nem importação: sobe a versão menor. O comum vai a "Versão 2.1", o plugin a 2.1.0, e a tag `v2.1` vai no merge commit.

## Risks / Trade-offs

- [Projeto com TDD e a stack já preenchida, mas com o comentário do modelo mantido] → o aviso aparece até o comentário sair; ele nomeia o arquivo, e apagar o comentário é o que o modelo já pede.
- [Comum que cresça perto de 16 KB nas revisões de texto do item 8] → o teste do kit reprova antes do envio, e a revisão tem de compensar cortando; é a pressão que o achado F09 pede.
- [Decomposição de projeto com o título `## Ciclo` escrito de outro jeito] → as três decomposições reais têm os três títulos no começo da linha (conferido em consulta-publica, heimdall e modelo-interface-heimdall); outra reprova com a mensagem que aponta o esqueleto.
- [OpenSpec que mude o formato do `config list --json`] → o aviso aparece a mais, nunca a menos; a versão do OpenSpec está fixada no CI do modelo.

## Migration Plan

1. Na branch: as conferências, a ferramenta, o teto e a versão no comum, a regra do kit, os testes e a limpeza deles.
2. Execução manual: um projeto novo pelo `kit.py novo` com o perfil real da máquina, e um clone descartável do heimdall (com TDD) conferido pelas conferências novas.
3. Depois do merge: os projetos recebem as conferências na próxima atualização, cada um sob a ordem do usuário nomeando-o.
4. Volta atrás: reverter o merge devolve o kit à 2.0; os projetos não atualizados não mudam.

## Revisão dos artefatos

A revisão do fim do propose, pelo checklist da skill `sdd:briefing` adaptado ao kit (a descrição aprovada no lugar do PRD; o `CLAUDE.md` do kit e os specs atuais no lugar dos ADRs), deu o laudo APROVADO, aprovado pelo usuário em 2026-10-15. Duas observações, resolvidas no apply: o texto do topo do `confere_regras.py`, que lista o que ele confere, ganha o aviso da stack e o teto de 32 KB; e, com TDD e a linha "Stack" ainda por preencher, o aviso da stack e o dos campos `< >` saem juntos, de propósito, porque cada um diz uma coisa.
