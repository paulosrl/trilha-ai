# Design

## Context

Ver `proposal.md` (Why). Na 2.19, o `atualizar` migra a `trilha/` do método (o `_migrar_a_trilha`): apaga a pasta, troca as citações no `CLAUDE.md` e no `scripts/check.sh` pelo `NA_TRILHA` e, depois das travas e da página, avisa os outros arquivos versionados que citam `trilha/` (o `_avisar_as_citacoes`, um `git grep -l -E` com o `NA_TRILHA_DO_GREP`). Antes de mudar o projeto, o `_conferir_a_trilha` recusa a `trilha/` do método que é link simbólico. Na conferência das regras, o `avisos_das_travas` avisa a trava do commit desligada quando o `core.hooksPath` não é `trilha-ai/hooks`. O kit já usa um link de transição para ele mesmo (`modelo/trilha`, change 20, D8).

No Heimdall, o código próprio cita a pasta antiga de formas que a busca de hoje não acha: `"$ROOT_DIR/trilha/hooks/pre-push"` (a busca só aceita `trilha/` depois de espaço, aspa, `(`, `@`, `=` ou `:`, para não confundir com `src/trilha/`). Esses arquivos só entraram no aviso por outra linha deles.

## Goals / Non-Goals

**Goals:**
- Depois da migração, o que o projeto chama pelo caminho antigo continua funcionando, até ele deixar de chamá-lo.
- O link nunca sai enquanto um arquivo versionado do projeto ainda cita a pasta antiga numa forma que a busca reconhece.

**Non-Goals:**
- Achar toda citação possível (um caminho montado em tempo de execução, peça por peça, escapa a qualquer busca de texto).
- Trocar as citações do projeto.

## Decisions

### D1. Quando o link nasce
Na migração, depois das travas e da página (onde o aviso das citações já roda), se a busca acha algum arquivo, a ferramenta cria `trilha` como link simbólico relativo para `trilha-ai` (`os.symlink("trilha-ai", ...)`) e diz que o criou, por quê e o que o tira, com a lista. O git versiona o link, que entra no commit da cópia.

*Alternativas:* (a) criar o link sempre na migração: recusada, porque a descrição aprovada pede o link só onde há citação, e os projetos que não citam a pasta antiga não precisam dele; (b) recusar a migração enquanto o projeto citar a pasta antiga: recusada, porque o projeto não consegue trocar antes, já que o caminho novo ainda não existe; (c) copiar a pasta nas duas: recusada, porque seriam duas cópias a manter iguais, e a conferência só compara uma.

### D2. A busca das citações, mais larga
A busca, que alimenta o aviso e o link, acha `trilha/` em qualquer caminho, desde que não seja parte de outro nome (`(^|[^[:alnum:]_.-])trilha/`: fora `minhatrilha/` e `trilha-ai/`; dentro `src/trilha/`, `../trilha/`, `$X/trilha/`, `${R:-.}/trilha/`, `` `pwd`/trilha/ ``), e o nome `trilha` sozinho entre aspas (`Path("trilha")`, `join(raiz, 'trilha')`). Ela lê os arquivos versionados, fora da `trilha/` e da `trilha-ai/`, das changes arquivadas do OpenSpec (histórico, que não se edita nem roda) e do `sdd/documentacao.html` (gerado a partir do `sdd/`, que a busca já lê), e também o `.claude/settings.local.json`, que o git ignora e pode ligar a trava antiga. O `git grep` que sai com erro não conta como "nada achado": a busca devolve que falhou. O `NA_TRILHA`, que reescreve o `CLAUDE.md` e o `check.sh`, não muda. Uma busca que acha a mais só mantém o link e o aviso por mais tempo, e esse é o lado seguro; achar a menos é que quebraria.

*Alternativa:* uma busca só para o link, deixando o aviso como estava: recusada, porque seriam duas listas diferentes para o mesmo fato.

### D3. Como se reconhece o link de transição
`trilha` é o link de transição quando é link simbólico e resolve para a `trilha-ai/` do mesmo projeto. Na ferramenta, o `_trilha_do_metodo` não o conta como a pasta do método (assim ele não migra), e o `_conferir_a_trilha` não o recusa. O link para outro lugar continua recusado como na 2.19. Na conferência das regras, a mesma regra.

### D4. O atualizar seguinte
Quando a pasta não migrou, mas o link existe, a busca roda no mesmo ponto. Se ela acha algo, ou falha, o link fica, e a saída diz isso, com a lista ou a falha. Se não acha nada, o link sai (`unlink`), e a saída diz por quê e pede o que a migração pedia sem o link: reabrir a sessão do Claude Code, conferir os arquivos locais que o git não versiona e trocar o `core.hooksPath` dos outros clones. Com o link criado na migração, esse pedido não sai, porque a sessão e os clones seguem funcionando por ele. A remoção entra no commit sugerido como parte da cópia.

O link só nasce na migração da `trilha/` (o `atualizar` que a tira). Nenhum projeto foi migrado pela 2.19 (os três estão na 2.15 e na 2.12), e um projeto que nunca teve a pasta antiga não deve ganhar o link por uma citação a `src/trilha/`.

### D5. A conferência das regras
O `avisos_das_travas` ganha dois avisos: o do link de transição, sempre que ele existe (lembra que ele sai pelo `atualizar` quando nada citar `trilha/`), e, com o link e o `core.hooksPath` em `trilha/hooks`, o da trava ligada pelo link, com o comando para trocar, no lugar de "desligada". Sem o link, `trilha/hooks` continua "desligada". Os dois são avisos, porque o `core.hooksPath` é de cada clone e o link é uma transição.

### D6. A versão
O método vai à 2.20: o comum, o `plugin.json` na 2.20.0 e a tag `v2.20`. O roteiro de validação (`ferramentas/validar-projeto.md`) passa a tratar `trilha` como link para a `trilha-ai/`, que não é migração pela metade.

## Risks / Trade-offs

- [O projeto com uma pasta `src/trilha/` própria, ou com a palavra entre aspas num documento, segura o link e o aviso indefinidamente] → É o lado seguro: o aviso diz o que o segura, e tirar o link à mão (`git rm trilha`) é escolha do usuário.
- [Um caminho montado peça por peça (`"tri" + "lha"`, ou uma variável com o nome) escapa à busca, e o link pode sair com o projeto ainda o usando] → A busca cobre as formas que o ensaio achou e as comuns de shell e Python. Depois que o link sai, a verificação do projeto e o `pre-push` dele rodam no envio seguinte, e a saída do `atualizar` diz que o link saiu.
- [O link esconde que o projeto ainda depende da pasta antiga] → A conferência das regras o avisa em cada `check.sh`, e cada `atualizar` repete a lista.
- [Num clone sem suporte a link simbólico (`core.symlinks=false`), o link vira um arquivo de texto] → Nessa máquina, o caminho antigo volta a não existir, como sem esta change. O kit é usado no Linux, no macOS e no WSL.
- [Os outros clones ficam com o `core.hooksPath` em `trilha/hooks` depois que o link sai] → A saída da remoção dá o comando, e a conferência das regras avisa a trava desligada.

## Migration Plan

Nada a migrar no kit. Nos projetos, o `kit.py atualizar` que os leva da `trilha/` à `trilha-ai/` cria o link onde houver citação. Para voltar atrás antes do commit, `git reset --hard` e `git clean` no projeto, como em toda atualização.

## Verificação

**Execução manual (tarefa 3.2), em 2026-10-24,** no scratchpad, num clone descartável do Heimdall (comum 2.15, na `master` do `1fd4cc5`), com o `core.hooksPath` em `trilha/hooks`, como nos clones dele.
- O `kit.py atualizar --openspec` do kit desta change terminou com 0. A saída listou as citações a `trilha/` (o `.githooks/pre-push`, os scripts, os testes, o TDD, a decomposição, as changes arquivadas), disse "criado o link de transição trilha → trilha-ai" e sugeriu "chore(metodo): cópia do kit Trilha AI, comum 2.15 → 2.20, e os arquivos gerados pelo OpenSpec 1.15.0". As duas conferências passaram, e a das regras avisou o link. No ensaio com o kit 2.19, sem o link, a conferência tinha reprovado a evidência do TDD (`trilha/hooks/pre-push`).
- O commit da cópia, pela trava em `trilha-ai/hooks`, passou, e o git guardou `trilha` como link (modo `120000`). O `bash scripts/check.sh` do Heimdall terminou com 0.
- Com o `core.hooksPath` em `trilha/hooks`: um commit passou pela trava, que avisou "trava do commit ligada pelo link de transição"; o envio a um remoto local descartável passou pelo `trilha/hooks/pre-push`, que rodou o `.githooks/pre-push` do Heimdall (o encoding, o `openspec validate --specs --strict` e os 49 testes pareados, `ok` todos) e terminou com 0, e o remoto recebeu o commit.

## Revisão dos artefatos

Feita antes do apply, em 2026-10-24, pela coerência entre a proposta, os deltas, o design e as tarefas, e diante do código do `atualizar`.

- **A1 (a busca de hoje não acha `"$ROOT_DIR/trilha/hooks"`, a forma do `teste-pre-push` do Heimdall):** achada ao escrever o design e aplicada antes do commit do propose: o D2 alarga a busca, e o cenário "Arquivo do projeto que ainda cita a pasta trilha" ganhou a linha que a comprova.
- **A2 (o link nasce e sai antes do `_mudados` que separa a cópia do update do OpenSpec):** sem mudança: o D1 e o D4 põem o link no ponto do aviso das citações, que já roda antes dele, e assim a criação e a remoção contam como parte da cópia no commit sugerido.
- **A3 (no `atualizar` que só tira o link, o commit sugerido diz "cópia do kit, comum 2.20 → 2.20"):** recusado: é o texto de hoje para toda cópia que muda arquivo sem mudar a versão, e o link é parte da cópia.

## Respostas à revisão

O `/opsx:verify` (V) e o `/code-review high 22` (R), em 2026-10-24, cada um por um agente sem o contexto da sessão. Nenhum achado crítico.

- **V1 e R1 (o histórico cita `trilha/` para sempre, e o link nunca sairia):** aplicado. A busca deixa de fora as changes arquivadas do OpenSpec e o `sdd/documentacao.html` (D2); o Heimdall, que reprova citação quebrada, também deixa as `openspec/changes/` de fora. O TDD e a decomposição ficam na busca: são documentos vivos, cuja citação de caminho se corrige sem versão nova. O nome entre aspas fica (R1 sugeriu tirá-lo): é a forma do Python (`Path("trilha")`), e o falso positivo só segura o link, com aviso; o risco entrou no design.
- **V3 e R2 (o `git grep` com erro devolvia lista vazia, e o link sairia):** aplicado. Só o código 1 é "nada achado"; com erro, o link nasce na migração e fica no `atualizar` seguinte, com o aviso da falha. Cenário "Busca que falha", `test_busca_que_falha_mantem_o_link`.
- **V4 e R3 (formas da pasta que a busca não achava: `${R:-.}/trilha/`, a crase, `[`, `,`):** aplicado pela inversão que R3 propôs: qualquer `trilha/` que não seja parte de outro nome (D2). O cenário das citações passou a pedir o `src/trilha/` e o `../trilha/` no aviso (antes, fora), e o `test_migracao_avisa_as_citacoes_da_trilha` cobre as formas novas. O nome sem barra nem aspas (`cd trilha`) fica fora: casaria a palavra no texto de qualquer documento em português e seguraria o link para sempre.
- **R4 (os arquivos que o git ignora, como o `.claude/settings.local.json`, ficam fora da busca):** aplicado em parte. A busca lê o `.claude/settings.local.json` (cenário "Configuração local que liga a trava antiga", `test_settings_local_que_cita_a_trilha_mantem_o_link`), e a saída da remoção pede para conferir os arquivos locais. Ler todo o ignorado (`--no-exclude-standard`) foi recusado: passaria por `node_modules/` e afins, devagar e com falso positivo de dependências.
- **R5 (um projeto já migrado pela 2.19 não ganha o link):** recusado no código, corrigido no design (D4 e Migration Plan): nenhum projeto foi migrado pela 2.19, e criar o link fora da migração o daria a projetos que nunca tiveram a pasta antiga.
- **R6 (um link em laço derrubava o `kit.py` e a conferência com traceback):** aplicado. O `resolve()` com erro devolve "não é o link". Cenário "Link em laço", `test_regras_com_o_link_em_laco`.
- **R7 (o aviso de reabrir a sessão contradizia o link):** aplicado. Com o link criado, o aviso não sai; ele vem quando o link sai (D4). Os testes do link criado e do link que sai o conferem.
- **R8 (a regra do link escrita duas vezes, no `kit.py` e no `confere_regras.py`):** aplicado com um teste, `test_link_de_transicao_igual_na_ferramenta_e_nas_regras`, que confere as duas nos mesmos casos. O `kit.py` não importa os verificadores do modelo; a cópia da regra segue o padrão do kit.
- **R9 (o README não fala do link):** aplicado.
- **V2 (o item 5 do roteiro de validação cobra `trilha-ai/hooks` sem a exceção do link):** aplicado.
