# Notas da change 15

## Verificação

**Execução manual (tarefa 2.2), em 2026-10-24,** com o OpenSpec 1.15.0, numa cópia do `openspec/` numa pasta à parte: o `openspec archive 15-requisitos-curtos --yes` de lá aplicou o delta ("+ 5, ~ 3, - 0, → 0"); o `openspec validate horas-de-trabalho --type spec --strict` passou, sem o aviso dos requisitos longos, e o `openspec show` listou 24 requisitos e 75 cenários (eram 19 e 70), com os 70 cenários de antes com o texto igual.

**Depois das respostas à revisão,** a mesma simulação com o delta corrigido deu "+ 5, ~ 3, - 0, → 0", o `validate --strict` do spec passou, com 24 requisitos e 75 cenários, e os 70 de antes continuaram com o texto igual. Os comandos das tarefas 1.1 a 1.4 rodam 7, 11, 10 e 5 testes, todos ok.

## Respostas à revisão

Do `/opsx:verify` (achados V1 a V8) e do `/code-review high 16` (achados C1 a C9), de 2026-10-24, rodados por um agente sem o contexto da sessão.

- **V1 e C1 (o `trilha.email` fora de "Commits do usuário"):** aplicados. O requisito cita os e-mails de autor do git e os do `trilha.email`, com o requisito "Outros e-mails do usuário".
- **C2 (a regra de juntar sem a exceção do resumo que não se lê):** aplicado. "Repositório que mudou de pasta" diz "salvo quando o resumo dele não se lê", citando "Resumo antigo ilegível".
- **V2, C4 e C5 (mover os cenários para o requisito novo de cada regra, sem a repetição):** recusados. O OpenSpec não aceita: o MODIFIED substitui o bloco inteiro, e o `openspec validate` reprova o MODIFIED que omite um cenário do spec principal (visto nesta sessão, na change 14); as instruções dele para dividir um requisito mandam manter o nome e todos os cenários no MODIFIED e dar a cada requisito ADDED cenários próprios. A repetição é o custo dessa regra; cada cenário novo aponta o mesmo teste do cenário de que repete a regra.
- **V3 (o aviso em cada execução):** aplicado no cenário "Raiz antiga sob uma pasta fechada".
- **V4 e C7 (as horas do resumo ilegível):** aplicados: "e as horas dele não entram".
- **V5 e C3 (o resumo antigo que nem é JSON some sem aviso):** o texto foi restrito ao que o código faz: o resumo que aponta uma raiz e não se lê, como o de uma versão desconhecida. O caso do arquivo que nem é JSON já era assim antes desta change, e avisar nele pede código: fica fora, para uma change própria, se o usuário quiser.
- **V6 (o que decide é a pasta `.git`):** aplicado nos dois requisitos: "já não tem a pasta `.git`" e "ainda tem a pasta `.git`, mesmo que o git a recuse".
- **V7 (o "ou" entre os e-mails de autor):** aplicado: "e".
- **V8 (os requisitos novos no fim do spec; o `isPlanningComplete` sem o design):** sem mudança. O archive do OpenSpec põe os ADDED no fim, e o `design.md` é condicional nas instruções dele.
- **C6 (o `-k test_tempo` das tarefas):** aplicado: cada tarefa dá o comando com um `-k` por teste nomeado.
- **C8 (as remotas):** aplicado: "as branches, as remotas e as tags", como o `_commits`.
- **C9 (o `trilha.email` sozinho):** aplicado no texto: sem nenhum e-mail de autor, contam os commits de qualquer autor, mesmo com o `trilha.email`, como o código faz. O cenário que comprova é "Sem e-mail configurado", que fica no MODIFIED pela regra acima.
