# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. A change não mexe em código nem em teste: cada cenário é comprovado por um teste que já existe, e o comportamento fica igual.

## 1. Os cenários e os testes que os comprovam

- [ ] 1.1 "Conversas do repositório": "Conversa de outro repositório" (`test_tempo_ignora_repositorio_vizinho`), "Conversa numa subpasta" (`test_tempo_conta_conversa_em_subpasta`), "Caminho com acento" (`test_tempo_caminho_com_acento`), "Pasta de configuração trocada" (`test_tempo_usa_claude_config_dir`), "Clone dentro da raiz" (`test_tempo_clone_dentro_da_raiz`), "Worktree do próprio repositório dentro da raiz" (`test_tempo_worktree_da_raiz`) e "Subpasta sem permissão" (`test_tempo_subpasta_sem_permissao`); os sete passam (`-k test_tempo`)
- [ ] 1.2 "Estimativa pelos commits nos dias sem conversa": "Sessões de commits" (`test_tempo_sessoes_de_commits`), "Commit logo depois da meia-noite" (`test_tempo_commit_depois_da_meia_noite`), "Dia com conversa e commits" (`test_tempo_dia_com_conversa_usa_conversa`), "Commit em duas branches" (`test_tempo_commit_em_duas_branches`), "Commit de outro autor" (`test_tempo_commit_de_outro_autor`), "Sem e-mail configurado" (`test_tempo_sem_email_configurado`), "Commit à meia-noite em ponto" (`test_tempo_commit_a_meia_noite`), "E-mail de autor do git" (`test_tempo_email_de_autor_do_git`), "E-mail de autor no ambiente" (`test_tempo_email_de_autor_no_ambiente`), "E-mail da configuração global" (`test_tempo_email_da_configuracao_global`) e "Variável EMAIL" (`test_tempo_email_da_variavel_email`); os onze passam (`-k test_tempo`)
- [ ] 1.3 "Repositório que mudou de pasta": "Pasta trocada" (`test_tempo_pasta_trocada`), "Pasta antiga que já não existe" (`test_tempo_pasta_antiga_que_ja_nao_existe`), "Pasta antiga que sobrou sem o repositório" (`test_tempo_pasta_antiga_que_sobrou_sem_repositorio`), "Segundo resumo juntado com o mesmo nome" (`test_tempo_segundo_juntado_com_o_mesmo_nome`), "Pasta antiga juntada depois da primeira execução" (`test_tempo_pasta_antiga_juntada_depois`), "Resumo antigo que não se lê" (`test_tempo_resumo_antigo_que_nao_se_le`), "Pasta antiga com um .git que o git recusa" (`test_tempo_pasta_antiga_com_git_que_falha`), "Pasta antiga sem permissão" (`test_tempo_pasta_antiga_sem_permissao`), "Raiz antiga com caminho inválido" (`test_tempo_raiz_antiga_com_caminho_invalido`) e "Vizinho de nome parecido" (`test_tempo_vizinho_de_nome_parecido`); os dez passam (`-k test_tempo`)
- [ ] 1.4 Os requisitos novos: "Conversa sob uma pasta fechada" (`test_tempo_subpasta_sem_permissao`), "Só os commits dos e-mails do usuário" (`test_tempo_commit_de_outro_autor`), "Resumo antigo de versão desconhecida" (`test_tempo_resumo_antigo_que_nao_se_le`), "Raiz antiga sob uma pasta fechada" (`test_tempo_pasta_antiga_sem_permissao`) e "Repositório copiado para outra pasta" (`test_tempo_pasta_trocada`); os cinco passam (`-k test_tempo`)

## 2. Integração

- [ ] 2.1 O conjunto dos testes, o `openspec validate --all --no-interactive` e o `openspec validate 15-requisitos-curtos --strict --no-interactive` passam
- [ ] 2.2 A execução manual, por último: numa cópia do `openspec/` numa pasta à parte, com o delta aplicado pelo `openspec archive 15-requisitos-curtos --yes` de lá, o `openspec validate horas-de-trabalho --type spec --strict` passa sem o aviso dos requisitos longos, e o `openspec show horas-de-trabalho --type spec --json` lista os 24 requisitos (19 de antes e 5 novos), com os cenários de antes inteiros; o resultado vai ao `notas.md` da pasta da change

## Workflow follow-up

- O `/opsx:verify` e o `/code-review` do pull request, por um agente sem o contexto da sessão; as respostas vão ao `notas.md` da pasta da change, porque esta change não tem `design.md`.
- O `/opsx:archive`, os passos do `operations.archive` e o merge.
