# Design

## Context

Ver `proposal.md` (Why). A pasta entrou na 2.0, quando o `kit.py atualizar` passou a migrar as cópias soltas da raiz, de `scripts/` e de `.githooks/` para ela (o `_migrar`, o `ANTES_DA_2_0` e o `_migrar_check`). A ferramenta lê as versões antigas do kit pelo git (o `_caminhos` e o `_na_versao`), e a conferência das regras compara a pasta do projeto com a `modelo/trilha/` da tag da versão dele (o `_conteudos_da_tag`). O `.claude/settings.json` de cada projeto liga a trava por um caminho (`$CLAUDE_PROJECT_DIR/trilha/guarda.py`), e o `_sem_guardas_antigas` tira a trava de outra versão pelos nomes de `GUARDAS`.

## Goals / Non-Goals

**Goals:**
- Um `kit.py atualizar` leva o projeto da `trilha/` à `trilha-ai/` sem passo à mão no que é do método.

**Non-Goals:**
- Trocar as citações a `trilha/` nos arquivos do próprio projeto: o kit só as aponta.
- Manter as duas pastas por um tempo: a troca é de uma vez, numa versão.

## Decisions

### D1. A troca no kit
`git mv modelo/trilha modelo/trilha-ai`, e todo caminho `trilha/` que fala da pasta vira `trilha-ai/`, nos arquivos que vão aos projetos, na ferramenta, nos testes, nos specs e nos textos do kit. Ficam como estão os registros históricos (as auditorias, o plano de migração, as changes arquivadas) e os nomes que já são `trilha-ai` (o repositório, o marketplace, o `--vizinho trilha-ai`).

### D2. As versões antigas
Na ferramenta, o `ANTES_DA_2_0` passa a ter as chaves em `trilha-ai/`, e o `_caminhos` de um nome `trilha-ai/X` acrescenta o `modelo/trilha/X` das versões 2.0 a 2.18. Na conferência das regras, o `_conteudos_da_tag` lê a `modelo/trilha-ai/` da tag e, sem ela, a `modelo/trilha/`: um projeto já na `trilha-ai/` nunca está numa versão de antes da 2.19, mas a leitura das duas não custa nada e deixa a conferência ler qualquer tag.

### D3. A migração da pasta
No `_migrar`, antes da cópia: se existe o `trilha/CLAUDE-comum.md`, a pasta é a do método (o comum proíbe arquivo próprio nela, e a conferência das regras o reprova). A ferramenta avisa cada arquivo dela que o kit não tem (pelo nome relativo, diante da lista do método) e apaga a pasta inteira. Como o `atualizar` recusa trabalho não commitado, tudo o que sai e o git versiona volta por ele; o cache do Python (`__pycache__/`, que o `.gitignore` do modelo ignora) sai sem aviso, como o `_do_metodo` o ignora. Sem o comum, a pasta é do projeto e fica.

*Alternativa:* apagar só os arquivos que o kit tinha na versão do projeto. Recusada: deixaria uma `trilha/` com sobras que a regra do método já proíbe, e o aviso já nomeia o que não era do kit.

### D4. A versão de antes
O `antes` sai do `trilha-ai/CLAUDE-comum.md`, depois do `trilha/CLAUDE-comum.md`, depois do `CLAUDE-comum.md` da raiz.

### D5. A importação, o check.sh, a trava e o hooksPath
- A importação: a linha `@CLAUDE-comum.md` ou `@trilha/CLAUDE-comum.md` (com espaço no fim ou não) vira `@trilha-ai/CLAUDE-comum.md`, em toda atualização, como hoje.
- O `CLAUDE.md` e o `scripts/check.sh`, na migração da pasta (D3) e só nela: todo `trilha/` citado do começo da linha ou depois de um espaço, de uma aspa, de um parêntese, de `@`, `=` ou `:`, com `./` ou sem, vira `trilha-ai/`; não muda o que é parte de outro nome (`minhatrilha/`) nem de outro caminho (`src/trilha/`, `../trilha/`). O esqueleto da 2.18 cita a pasta em duas linhas de texto do `CLAUDE.md`, e o `check.sh` a chama pelo `verifica.sh`, com os argumentos depois; como a pasta era a do método, toda citação nesses dois arquivos fala dela. Fora da migração, um `trilha/` do próprio projeto nesses arquivos não muda.
- A troca da parte fixa de antes da 1.37 (o `_check_migrado`) passa a escrever `bash trilha-ai/verifica.sh`; a previsão da migração continua a mesma função.
- A trava do Claude Code: o `GUARDAS` ganha o `trilha-ai/guarda.py`; a de `trilha/guarda.py` sai pelo `_sem_guardas_antigas`, que a acha pelo nome (`trilha/guarda.py` não é parte de `trilha-ai/guarda.py`), e a soma põe a do modelo.
- O `core.hooksPath`: o `_ligar_travas` já o grava sempre; passa a `trilha-ai/hooks`.

### D6. As citações que sobram no projeto
Quando o `atualizar` migrou a pasta, e só então, ele procura nos arquivos versionados do projeto, fora da `trilha/` e da `trilha-ai/`, o `trilha/` com o mesmo limite do D5 (`git grep -l -E`, sem o `-P`, que nem todo git tem) e avisa a lista, para a troca à mão. A busca roda depois das travas e da página, que também citavam a pasta: o `.claude/settings.json` e o `sdd/documentacao.html` já foram trocados, como o `CLAUDE.md` e o `check.sh`, e não aparecem. No mesmo momento, a ferramenta avisa para reabrir a sessão do Claude Code aberta no projeto e para trocar o `core.hooksPath` dos outros clones.

### D7. A recusa
A pasta `trilha-ai/` sem o `trilha-ai/CLAUDE-comum.md` recusa, como a `trilha/` recusava. A `trilha/` sem o comum deixa de ser obstáculo.

### D8. O link de transição
O verificador de um projeto de antes da 2.19 compara a pasta dele com a `modelo/trilha/` do kit ao lado e reprova quando ela não existe, antes de ler a tag da versão dele. O kit guarda `modelo/trilha` como link simbólico para `trilha-ai` (o git versiona o link): o verificador antigo acha a pasta e, com o kit noutra versão, compara pela tag da versão do projeto, que tem a `modelo/trilha/` de verdade. O link não entra na lista do método (o `_do_metodo` lê a `modelo/trilha-ai/`) e não vai aos projetos. Sai numa versão futura, quando os projetos estiverem na `trilha-ai/`.

*Alternativa:* aceitar a quebra da verificação local até cada atualização. Recusada pelo usuário.

### D9. A versão
A linha "Versão 2.19, de 2026-10-24." no comum e o `plugin.json` na 2.19.0; a tag `v2.19` no merge. O comum e o esqueleto continuam nos limites (200 linhas somados, 16 KB o comum).

## Risks / Trade-offs

- [O projeto que tinha arquivo próprio na `trilha/` do método o perde na migração] → O aviso o nomeia, e ele volta pelo git; a regra do método já o proibia ali.
- [Um script, o CI ou um documento do projeto cita `trilha/` e quebra depois da migração] → O aviso do D6 os lista; o `check.sh` e a conferência rodam no fim do `atualizar`, e uma quebra na verificação aparece já ali.
- [Um projeto de antes da 2.19 que roda a conferência com o kit 2.19 ao lado] → Sem o link, o verificador dele reprovaria por não achar a `modelo/trilha/`; o link de transição (D8) o resolve, e o `test_projeto_da_2_18_confere_com_o_kit_novo` o confere.
- [Num clone sem suporte a link simbólico (`core.symlinks=false`), o link vira um arquivo de texto] → O verificador antigo volta a reprovar nessa máquina; o kit é usado no Linux, no macOS e no WSL, onde o git cria o link.
- [A sessão do Claude Code aberta no projeto antes da migração continua chamando a trava em `trilha/guarda.py`, que não existe mais, e o Python sai com 2, que bloqueia todo comando Bash] → O aviso do D6 manda reabrir a sessão.
- [Os outros clones do projeto ficam com o `core.hooksPath` em `trilha/hooks`, e o git não roda hook nenhum] → O aviso do D6 dá o comando, e a conferência das regras já avisa a trava do commit desligada.

## Verificação

**Os testes antes do código (tarefas 1.1 e 1.2):** com os caminhos trocados nos testes e a pasta ainda em `modelo/trilha/`, o módulo dos testes nem carregou (ele importa o `modelo/trilha-ai/confere_regras.py`): todos falharam. Depois do código, o conjunto passou.

**Execução manual (tarefa 3.2), em 2026-10-24,** no scratchpad, com o `TRILHA_AI` no kit e o `HOME` e o `XDG_CONFIG_HOME` isolados: um projeto feito pelo `kit.py` da tag `v2.18` (extraída por `git archive`), com `--vizinho outro` no `check.sh` e um `docs/como.md` que cita `trilha/tempo.py`, commitado.
- Antes da atualização, o `bash scripts/check.sh` terminou com 0 com o kit 2.19 ao lado, pelo link de transição, com o aviso "o kit está na 2.19 e o projeto na 2.18: a pasta trilha/ foi comparada com a v2.18".
- O `kit.py atualizar` terminou com 0: saiu a `trilha/`, entrou a `trilha-ai/`; o `CLAUDE.md` (a importação e as duas linhas de texto) e o `check.sh` (`bash trilha-ai/verifica.sh --vizinho outro`) passaram a citar a `trilha-ai/`; o `core.hooksPath` é `trilha-ai/hooks` e o `settings.json` liga a `trilha-ai/guarda.py`; os avisos citaram o `docs/como.md` e a sessão a reabrir; a sugestão foi "chore(metodo): cópia do kit Trilha AI, comum 2.18 → 2.19".
- Depois, o `bash scripts/check.sh` terminou com 0; o commit da cópia passou pela trava em `trilha-ai/hooks`, e um commit com a importação antiga foi barrado por ela ("CLAUDE.md não importa o comum (falta a linha @trilha-ai/CLAUDE-comum.md)").

## Respostas à revisão

### Revisão dos artefatos

De 2026-10-24, por um agente sem o contexto da sessão. Os dois pontos de escolha foram ao usuário; o resto foi aplicado.

- **A1 (o verificador de um projeto de antes da 2.19 reprova com o kit 2.19 ao lado, porque procura a `modelo/trilha/`):** levado ao usuário, que escolheu o link de transição (D8); o requisito "Link de transição da pasta antiga no kit" e o `test_projeto_da_2_18_confere_com_o_kit_novo`. O risco do design foi reescrito.
- **A2 (o D6 dizia `git grep` com a palavra inteira, que não acha `trilha/tempo.py`):** aplicado. O D6 diz o `-E` com o limite do D5, como o código faz.
- **A3 (a busca das citações rodava antes das travas e da página, e avisaria o `.claude/settings.json` à toa):** aplicado. A busca roda no `atualizar`, depois da página; o teste confere que o `settings.json` não aparece.
- **A4 (a troca automática tirou a `trilha/guarda.py` do requisito "Settings.json somado do modelo inteiro"):** aplicado; o `GUARDAS` do código também a manteve.
- **A5 (a tarefa 1.1 nomeava só parte dos cenários MODIFIED):** aplicado. A tabela "Os cenários e os testes", no fim das tarefas, dá o teste de cada um dos 87 cenários; dois de antes desta change, sem mudança de comportamento, ficam comprovados só em parte, e a tabela o diz.
- **A6 (o critério do `git grep` na 2.3 não se cumpria, e os Purpose de quatro specs citavam a pasta):** aplicado. O critério diz o que fica de fora e o que sobra de propósito; os Purpose foram trocados.
- **A7 (o `ferramentas/validar-projeto.md` fora do escopo):** aplicado, na proposta e na 2.3.
- **Menores, aplicados:** a leitura das duas pastas no `confere_regras.py` fica e tem teste (o `test_kit_mais_novo_compara_pela_tag_e_avisa` lê uma tag de antes da 2.19); o `_caminhos` ganhou o `test_migracao_le_as_versoes_da_pasta_trilha`; o `__pycache__` não entra no aviso do arquivo a mais, e o D3 diz que ele sai sem o git o guardar; o limite do D5 não troca `src/trilha/` nem `../trilha/` (o `test_migracao_nao_troca_o_caminho_do_projeto`); a proposta diz a troca de toda citação no `CLAUDE.md` e os avisos, que o usuário aprovou além da descrição curta; o `mapa-da-trilha.html`, que não cita a pasta, saiu do escopo; o cenário ADDED passou a "Pasta trilha que não é do método" (o MODIFIED não pode ser renomeado, o OpenSpec o recusa); os riscos da sessão do Claude Code aberta e dos outros clones entraram, com o aviso no `atualizar`; a 3.2 roda com o `TRILHA_AI` e confere o projeto da 2.18 antes da migração.
