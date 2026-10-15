# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`; o ruff, com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check`. Cada teste novo é escrito antes do código e falha antes dele.

## 1. A decomposição pelo esqueleto da skill

- [x] 1.1 O `confere_metodo.py` lê a decomposição por linhas de título (`## 1.`, `## 2.`, `## Ciclo`, cada seção até o título `## ` seguinte) e a falha nomeia cada título que falta e o esqueleto da skill `sdd:briefing`; o `test_esqueleto_da_decomposicao_passa_na_conferencia` continua passando e comprova o cenário "Esqueleto da skill" (`-k test_esqueleto_da_decomposicao_passa_na_conferencia`)
- [x] 1.2 O teste `test_decomposicao_com_titulo_so_dentro_do_texto_reprova` comprova o cenário "Título só dentro do texto" (`-k test_decomposicao_com_titulo_so_dentro_do_texto_reprova`)
- [x] 1.3 O teste `test_decomposicao_sem_a_secao_2_reprova` comprova o cenário "Sem a seção 2" (`-k test_decomposicao_sem_a_secao_2_reprova`)

## 2. O aviso da stack por preencher

- [x] 2.1 O `confere_regras.py` ganha a tabela dos marcadores da stack (um por lugar, como no design, decisão 2) e o aviso, só com um `sdd/tdd-*.md`; o teste `test_marcadores_da_stack_sao_os_dos_modelos` confere que cada marcador está no modelo do lugar dele (`-k test_marcadores_da_stack_sao_os_dos_modelos`)
- [x] 2.2 O teste `test_tdd_com_a_stack_do_modelo_avisa` comprova o cenário "TDD com a stack do modelo" (`-k test_tdd_com_a_stack_do_modelo_avisa`)
- [x] 2.3 O teste `test_stack_preenchida_nao_avisa` comprova o cenário "Stack preenchida" (`-k test_stack_preenchida_nao_avisa`)
- [x] 2.4 O teste `test_projeto_sem_tdd_nao_avisa_a_stack` comprova o cenário "Projeto sem TDD" (`-k test_projeto_sem_tdd_nao_avisa_a_stack`)

## 3. O teto de tamanho das regras

- [x] 3.1 O `confere_regras.py` reprova acima de 32.768 bytes somados, citando os bytes e o limite; o teste `test_regras_largas_demais_reprovam` comprova o cenário "Regras largas demais" (`-k test_regras_largas_demais_reprovam`)
- [x] 3.2 O teste `test_regras_com_linhas_demais_reprovam` comprova o cenário "Linhas demais" (`-k test_regras_com_linhas_demais_reprovam`)
- [x] 3.3 O `test_verificador_aprova_um_repositorio_feito_do_kit` continua passando e comprova o cenário "Projeto novo dentro do teto" (`-k test_verificador_aprova_um_repositorio_feito_do_kit`)
- [x] 3.4 No kit: o teste `test_comum_cabe_em_metade_do_teto` segura o comum em 16.384 bytes; a última seção do comum diz o teto de 32 KB ao lado das 200 linhas, e o `CLAUDE.md` do kit diz a metade do comum (`-k test_comum_cabe_em_metade_do_teto`)

## 4. O prazo da lista de plugins

- [x] 4.1 O prazo vira a constante `PRAZO_DO_CLAUDE` do `confere_metodo.py`; o teste `test_lista_de_plugins_sem_resposta_no_prazo_nao_avisa` comprova o cenário "Lista de plugins sem resposta no prazo" (`-k test_lista_de_plugins_sem_resposta_no_prazo_nao_avisa`)
- [x] 4.2 Os testes `test_sem_o_claude_code_nao_avisa` e `test_lista_de_plugins_com_erro_nao_avisa` continuam passando e comprovam os cenários "Máquina sem o Claude Code" e "Lista de plugins com erro" (`-k test_sem_o_claude_code_nao_avisa`, `-k test_lista_de_plugins_com_erro_nao_avisa`)

## 5. O perfil do OpenSpec no projeto novo

- [x] 5.1 O `kit.py novo` lê o perfil por `openspec config list --json` (design, decisão 4), lista o `openspec config profile` nos próximos passos e avisa o verify que falta; o teste `test_novo_avisa_o_perfil_sem_o_verify` comprova o cenário "Perfil sem o verify", com um `openspec` falso no perfil `core` e noutro `custom` sem o verify (`-k test_novo_avisa_o_perfil_sem_o_verify`)
- [x] 5.2 O teste `test_novo_com_o_verify_no_perfil_nao_avisa` comprova o cenário "Perfil com o verify" (`-k test_novo_com_o_verify_no_perfil_nao_avisa`)
- [x] 5.3 O teste `test_novo_sem_openspec_avisa` comprova o cenário "OpenSpec ausente" (`-k test_novo_sem_openspec_avisa`)

## 6. A limpeza dos testes, a versão e os textos

- [x] 6.1 Saem do `testes/test_kit.py` os `assertNotIn` de frases aposentadas, pelo critério do design (decisão 6), e os testes que ficarem vazios; o conjunto de testes passa
- [x] 6.2 O comum vai a "Versão 2.1, de <data do commit>." e o plugin a `2.1.0`; o `context` do `openspec/config.yaml` do kit cita `modelo/trilha/` como a pasta do ruff; o `test_versao_do_plugin_igual_a_do_kit` passa e o `openspec validate --all --no-interactive` também
- [x] 6.3 O conjunto de testes e o ruff (check e format), cada um sozinho, sem erro

## 7. Execução manual

- [x] 7.1 Com o usuário olhando: um projeto novo pelo `kit.py novo`, numa pasta descartável, com o perfil real da máquina (sem o aviso do perfil) e com um `HOME` descartável (com o aviso); e um clone descartável do heimdall conferido pelo `confere_regras.py` e pelo `confere_metodo.py` desta branch, mostrando o aviso da stack (ou a ausência dele, se a stack já estiver preenchida) e o tamanho dentro do teto

## Workflow follow-up

- Depois do archive: `openspec validate --all --no-interactive`, os testes e o ruff do kit, e a regra de versão do `CLAUDE.md` (a tag `v2.1` no merge commit da main, enviada com ele).
- Depois do merge, com a confirmação do usuário: atualizar o plugin da máquina para a 2.1.0 (`claude plugin update sdd@trilha-ai`).
- Cada projeto real recebe a 2.1 com o `kit.py atualizar`, só com a ordem do usuário nomeando-o.
