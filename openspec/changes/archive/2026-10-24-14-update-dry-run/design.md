# Design

## Context

Ver `proposal.md` (Why). Na 2.15, o `_aviso_do_update` do `trilha/confere_metodo.py` copia os arquivos gerados que o projeto versiona (os que casam com `GERADO`) e o `openspec/config.yaml` para uma pasta temporária, copia a configuração global para um `XDG_CONFIG_HOME` temporário (a migração do OpenSpec a regrava), roda `openspec update <pasta>` e compara os arquivos byte a byte. São cerca de 55 linhas, com os testes de um `openspec` falso que mexe na pasta do ensaio.

Na 1.15.0, conferido em 2026-10-24:
- `openspec update --dry-run --json` responde `{"changes": [{"path", "action", "tool"}], "notes": [], "failures": []}`, com `action` em `add`, `update` ou `delete`;
- os caminhos dos arquivos do projeto vêm relativos à raiz (`.claude/commands/opsx/verify.md`); os de fora dela, como a configuração global que a migração regravaria (`tool: "openspec"`), vêm com `~/` quando ficam no HOME (o lugar padrão dela, `~/.config/openspec/config.json`) e com o caminho absoluto fora dele (o `toDisplayPath` do OpenSpec; corrigido depois do verify, achado V1);
- nada é escrito: nem o projeto nem a configuração global (o md5 dela ficou igual numa cópia sem o perfil);
- numa pasta sem `openspec/`, o código de saída é 1;
- a 1.14.1 não tem a opção, e o `commander` dele recusa a opção desconhecida com erro.

## Goals / Non-Goals

**Goals:**
- O aviso vem do OpenSpec, sem uma cópia própria do que ele faz.

**Non-Goals:**
- Mudar o texto do aviso, o portão da configuração global ou o dos arquivos gerados versionados.

## Decisions

### D1. O dry-run na raiz
O `_aviso_do_update` roda `openspec update --dry-run --json` com o `_saida` de hoje (a raiz como `cwd`, o `SEM_REDE` e o `PRAZO_DO_OPENSPEC`). Saem a pasta temporária, as cópias e o `XDG_CONFIG_HOME`. Dois dos três portões de antes ficam: sem a configuração global (`openspec config path`) ou sem nenhum arquivo gerado versionado, ele nem roda. Com o primeiro, o CI, que não tem perfil, não ganha um aviso do perfil padrão; com o segundo, o projeto que não usa o OpenSpec nas ferramentas fica quieto. O terceiro, o `openspec/config.yaml` no disco, saiu: ele só existia para ser copiado ao ensaio, e sem o `openspec/` o dry-run sai com 1, que é silêncio. O portão dos gerados olha só o índice do git, sem conferir o disco.

*Alternativa:* passar a raiz como argumento (`openspec update --dry-run --json <raiz>`). Recusada por não acrescentar nada: o `cwd` já é a raiz.

### D2. O que entra no aviso
Cada item de `changes` com o `path` dentro da raiz entra no grupo da ação: `delete` em "apagaria", `add` em "criaria", `update` em "trocaria". Fica de fora o que começa com `~` (o HOME, onde está a configuração global no lugar padrão), o absoluto e o que sai da raiz por `..`, conferido pelo `os.path.normpath` sem seguir links simbólicos; também a ação desconhecida e o item fora do formato. A ordem de cada grupo é a alfabética, e o corte em `MOSTRADOS` nomes fica igual.

*Alternativa:* filtrar pelo `GERADO`. Recusada: o OpenSpec é quem sabe o que gera, e um arquivo novo que ele passe a gerar com outro nome sumiria do aviso.

### D3. O dry-run que falha
O silêncio cobre o código diferente de 0 (o `_saida` devolve `None`), a saída que não é um objeto JSON com `changes` em lista, e o `failures` não vazio. O `openspec` anterior à 1.15 cai no primeiro caso.

### D4. A versão fixada e a do método
A 1.15.0 no `modelo/.github/workflows/verificacao.yml`, no `.github/workflows/testes.yml` e no README; os testes que citam a 1.14.1 como a versão do CI passam à 1.15.0. Os exemplos do spec principal (1.14.3 diante de 1.14.1) ficam: são só exemplos de versões diferentes. "Versão 2.16, de 2026-10-24." no comum e `2.16.0` no plugin, antes de qualquer outro arquivo de `modelo/` mudar.

## Risks / Trade-offs

- [Numa máquina com o OpenSpec anterior à 1.15, o aviso dos gerados some] → O aviso da versão diferente da do CI aparece no mesmo `check.sh` e manda instalar a 1.15.0; com ela, o aviso volta.
- [A promessa de não escrever nada passa a ser do OpenSpec] → Conferida na 1.15.0 (o projeto e a configuração global intactos); o teste do projeto intacto continua, com o `openspec` falso.
- [O formato do JSON muda numa versão futura] → A saída fora do esperado é silêncio, nunca falha; a troca de versão do OpenSpec passa por uma change do kit, que roda o dry-run de verdade na execução manual.

## Verificação

**Execução manual (tarefa 3.2), em 2026-10-24,** com o OpenSpec 1.15.0, num projeto de teste feito pelo `kit.py novo` e inicializado com `openspec init --tools claude`, com o `verify.md` alterado e o `sync.md` apagado (os dois no índice do git):
- a conferência do método avisou "criaria: .claude/commands/opsx/sync.md; trocaria: .claude/commands/opsx/verify.md", e os arquivos do projeto e a configuração global da máquina ficaram iguais (md5 antes e depois);
- com a configuração global sem o perfil, num `XDG_CONFIG_HOME` à parte, o dry-run listou também essa configuração pelo caminho absoluto; o aviso foi o mesmo, sem citá-la, e ela ficou igual;
- a 1.14.1, pelo `npx`, recusou a opção com "error: unknown option '--dry-run'" e o código 1, que é o caso do silêncio.

**Depois do verify, achado V1, em 2026-10-24,** com o HOME numa pasta de teste, o `XDG_CONFIG_HOME` padrão e uma configuração `{}` nesse HOME: o dry-run listou `update ~/.config/openspec/config.json` ao lado dos dois comandos; a conferência avisou só os dois comandos, e a configuração ficou igual.

## Respostas à revisão

Do `/opsx:verify` (achados V1 a V6) e do `/code-review high 15` (achados C1 a C8), de 2026-10-24, rodados por um agente sem o contexto da sessão.

- **V1 e C2 (a configuração global no aviso, com `~/`; o `../`):** aplicados. O `_do_projeto` aceita só o caminho dentro da raiz (D2); o `test_openspec_caminho_fora_do_projeto_fica_fora_do_aviso` cobre o `~/`, o `../`, o absoluto e o `..` no meio, e falhou antes do código; o Context e a "Verificação" foram corrigidos. O `../` não acontece no 1.15.0, mas o filtro custa o mesmo.
- **V2 e C1 (os testes do projeto intacto e da configuração intacta não podiam falhar):** aplicados. O `openspec` falso chamado sem o `--dry-run` regrava a configuração e um comando do projeto, como o de verdade; tirar o `--dry-run` do código (a mutação, desfeita depois) fez os dois testes falharem.
- **V3 (o terceiro portão saiu sem registro):** aplicado no D1.
- **V4 e C6 (o `str(acao)` duplicado):** aplicados: `isinstance(acao, str) and acao in VERBOS`.
- **V5 (a quebra do docstring do módulo):** aplicado.
- **V6 (o commit dos arquivos gerados no PR):** recusado separar. O commit `2fb65ff` traz os arquivos que o `openspec update` da 1.15.0 gerou no kit (o `explore` e as skills, que o perfil `both` entrega); sem ele, o kit ficaria com os gerados da 1.14.1 diante do CI na 1.15.0. Fica registrado aqui, como parte da troca de versão.
- **C3 (um `failures` esconde as `changes` válidas das outras ferramentas):** recusado. Com uma falha, o próprio OpenSpec não conseguiu planejar o update, e o método não interpreta o resultado parcial de um comando que falhou: é o D3 e o cenário "Dry-run com falhas ou sem o JSON esperado". O `openspec update` de verdade mostra a falha a quem o rodar.
- **C4 (o `RecursionError` de uma saída aninhada fundo demais):** aplicado: o `except` o pega com o `ValueError`.
- **C5 (o portão pelo `GERADO` repete o ponto cego que o D2 recusou):** recusado mudar; a limitação fica registrada. O portão é de propósito (D1): sem ele, todo projeto que não usa o OpenSpec nas ferramentas rodaria o dry-run. Um nome novo que o OpenSpec passe a gerar entra no `GERADO` na change que trocar a versão, que roda o dry-run de verdade na execução manual.
- **C7 (o JSON do dry-run montado à mão em dois testes):** aplicado: o `_responde` monta a saída, e o `_dry_run` o usa.
- **C8 (o `git ls-files` do repositório inteiro a cada commit):** recusado. A premissa não vale: a trava do commit roda a conferência com `--sem-plugin`, que pula o OpenSpec (o requisito "Conferência do OpenSpec fora da trava do commit"); o `ls-files` só roda no `check.sh`, e o custo é anterior à change.
