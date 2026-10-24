# Design

## Context

Ver `proposal.md` (Why). Na 2.15, o `_aviso_do_update` do `trilha/confere_metodo.py` copia os arquivos gerados que o projeto versiona (os que casam com `GERADO`) e o `openspec/config.yaml` para uma pasta temporária, copia a configuração global para um `XDG_CONFIG_HOME` temporário (a migração do OpenSpec a regrava), roda `openspec update <pasta>` e compara os arquivos byte a byte. São cerca de 55 linhas, com os testes de um `openspec` falso que mexe na pasta do ensaio.

Na 1.15.0, conferido em 2026-10-24:
- `openspec update --dry-run --json` responde `{"changes": [{"path", "action", "tool"}], "notes": [], "failures": []}`, com `action` em `add`, `update` ou `delete`;
- os caminhos dos arquivos do projeto vêm relativos à raiz (`.claude/commands/opsx/verify.md`); a configuração global que a migração regravaria vem com o caminho absoluto e `tool: "openspec"`;
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
O `_aviso_do_update` roda `openspec update --dry-run --json` com o `_saida` de hoje (a raiz como `cwd`, o `SEM_REDE` e o `PRAZO_DO_OPENSPEC`). Saem a pasta temporária, as cópias e o `XDG_CONFIG_HOME`. Os dois portões de antes ficam: sem a configuração global (`openspec config path`) ou sem nenhum arquivo gerado versionado, ele nem roda. Com o primeiro, o CI, que não tem perfil, não ganha um aviso do perfil padrão; com o segundo, o projeto que não usa o OpenSpec nas ferramentas fica quieto.

*Alternativa:* passar a raiz como argumento (`openspec update --dry-run --json <raiz>`). Recusada por não acrescentar nada: o `cwd` já é a raiz.

### D2. O que entra no aviso
Cada item de `changes` com o `path` relativo entra no grupo da ação: `delete` em "apagaria", `add` em "criaria", `update` em "trocaria". O caminho absoluto (a configuração global, ou um arquivo de outra ferramenta fora do projeto) e a ação desconhecida ficam de fora. A ordem de cada grupo é a alfabética, e o corte em `MOSTRADOS` nomes fica igual.

*Alternativa:* filtrar pelo `GERADO`. Recusada: o OpenSpec é quem sabe o que gera, e um arquivo novo que ele passe a gerar com outro nome sumiria do aviso.

### D3. O dry-run que falha
O silêncio cobre o código diferente de 0 (o `_saida` devolve `None`), a saída que não é um objeto JSON com `changes` em lista, e o `failures` não vazio. O `openspec` anterior à 1.15 cai no primeiro caso.

### D4. A versão fixada e a do método
A 1.15.0 no `modelo/.github/workflows/verificacao.yml`, no `.github/workflows/testes.yml` e no README; os testes que citam a 1.14.1 como a versão do CI passam à 1.15.0. Os exemplos do spec principal (1.14.3 diante de 1.14.1) ficam: são só exemplos de versões diferentes. "Versão 2.16, de 2026-10-24." no comum e `2.16.0` no plugin, antes de qualquer outro arquivo de `modelo/` mudar.

## Risks / Trade-offs

- [Numa máquina com o OpenSpec anterior à 1.15, o aviso dos gerados some] → O aviso da versão diferente da do CI aparece no mesmo `check.sh` e manda instalar a 1.15.0; com ela, o aviso volta.
- [A promessa de não escrever nada passa a ser do OpenSpec] → Conferida na 1.15.0 (o projeto e a configuração global intactos); o teste do projeto intacto continua, com o `openspec` falso.
- [O formato do JSON muda numa versão futura] → A saída fora do esperado é silêncio, nunca falha; a troca de versão do OpenSpec passa por uma change do kit, que roda o dry-run de verdade na execução manual.
