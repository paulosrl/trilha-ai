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
A busca, que alimenta o aviso e o link, passa a reconhecer também `trilha/` depois de uma variável do shell (`$X/`, `${X}/`, `$(…)/`) ou de uma aspa seguida de barra (`"$X"/trilha/`), e o nome `trilha` sozinho entre aspas (`Path("trilha")`, `join(raiz, 'trilha')`). Continuam fora: `minhatrilha/`, `trilha-ai/`, `src/trilha/` e `../trilha/`. O `NA_TRILHA`, que reescreve o `CLAUDE.md` e o `check.sh`, não muda. Uma busca que acha a mais só mantém o link e o aviso por mais tempo, e esse é o lado seguro; achar a menos é que quebraria.

*Alternativa:* uma busca só para o link, deixando o aviso como estava: recusada, porque seriam duas listas diferentes para o mesmo fato.

### D3. Como se reconhece o link de transição
`trilha` é o link de transição quando é link simbólico e resolve para a `trilha-ai/` do mesmo projeto. Na ferramenta, o `_trilha_do_metodo` não o conta como a pasta do método (assim ele não migra), e o `_conferir_a_trilha` não o recusa. O link para outro lugar continua recusado como na 2.19. Na conferência das regras, a mesma regra.

### D4. O atualizar seguinte
Quando a pasta não migrou, mas o link existe, a busca roda no mesmo ponto. Se ela acha algo, o link fica, e a saída diz isso, com a lista. Se não acha nada, o link sai (`unlink`), e a saída diz por quê e lembra o `git config core.hooksPath trilha-ai/hooks` dos outros clones. A remoção entra no commit sugerido como parte da cópia.

### D5. A conferência das regras
O `avisos_das_travas` ganha dois avisos: o do link de transição, sempre que ele existe (lembra que ele sai pelo `atualizar` quando nada citar `trilha/`), e, com o link e o `core.hooksPath` em `trilha/hooks`, o da trava ligada pelo link, com o comando para trocar, no lugar de "desligada". Sem o link, `trilha/hooks` continua "desligada". Os dois são avisos, porque o `core.hooksPath` é de cada clone e o link é uma transição.

### D6. A versão
O método vai à 2.20: o comum, o `plugin.json` na 2.20.0 e a tag `v2.20`. O roteiro de validação (`ferramentas/validar-projeto.md`) passa a tratar `trilha` como link para a `trilha-ai/`, que não é migração pela metade.

## Risks / Trade-offs

- [Um caminho montado peça por peça (`"tri" + "lha"`, ou uma variável com o nome) escapa à busca, e o link pode sair com o projeto ainda o usando] → A busca cobre as formas que o ensaio achou e as comuns de shell e Python. Depois que o link sai, a verificação do projeto e o `pre-push` dele rodam no envio seguinte, e a saída do `atualizar` diz que o link saiu.
- [O link esconde que o projeto ainda depende da pasta antiga] → A conferência das regras o avisa em cada `check.sh`, e cada `atualizar` repete a lista.
- [Num clone sem suporte a link simbólico (`core.symlinks=false`), o link vira um arquivo de texto] → Nessa máquina, o caminho antigo volta a não existir, como sem esta change. O kit é usado no Linux, no macOS e no WSL.
- [Os outros clones ficam com o `core.hooksPath` em `trilha/hooks` depois que o link sai] → A saída da remoção dá o comando, e a conferência das regras avisa a trava desligada.

## Migration Plan

Nada a migrar no kit. Nos projetos, o próximo `kit.py atualizar` cria o link onde houver citação. Para voltar atrás antes do commit, `git reset --hard` e `git clean` no projeto, como em toda atualização.

## Revisão dos artefatos

Feita antes do apply, em 2026-10-24, pela coerência entre a proposta, os deltas, o design e as tarefas, e diante do código do `atualizar`.

- **A1 (a busca de hoje não acha `"$ROOT_DIR/trilha/hooks"`, a forma do `teste-pre-push` do Heimdall):** achada ao escrever o design e aplicada antes do commit do propose: o D2 alarga a busca, e o cenário "Arquivo do projeto que ainda cita a pasta trilha" ganhou a linha que a comprova.
- **A2 (o link nasce e sai antes do `_mudados` que separa a cópia do update do OpenSpec):** sem mudança: o D1 e o D4 põem o link no ponto do aviso das citações, que já roda antes dele, e assim a criação e a remoção contam como parte da cópia no commit sugerido.
- **A3 (no `atualizar` que só tira o link, o commit sugerido diz "cópia do kit, comum 2.20 → 2.20"):** recusado: é o texto de hoje para toda cópia que muda arquivo sem mudar a versão, e o link é parte da cópia.
