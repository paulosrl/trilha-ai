# Proposal

## Why

A auditoria de outubro de 2026 (`docs/auditorias/2026-10.md`) achou que o `--fonte` da conferência das regras compara a pasta `trilha/` do projeto com a cópia de trabalho do kit ao lado (achado N01). Quando o kit sobe de versão, todo projeto que ainda não foi atualizado reprova no `scripts/check.sh` local, embora o kit mande atualizar cada projeto só sob ordem do usuário; no CI, sem o kit ao lado, o mesmo projeto passa. A mensagem dessa falha manda copiar a pasta, que o comum proíbe editar (conflito C02). A auditoria achou também que o `"disableAllHooks": true` no `.claude/settings.local.json` desliga a trava do Claude Code sem aviso (achado N15). A correção vem agora porque é o primeiro passo da versão 2.4: sem ela, a própria 2.4 reprovaria os projetos.

## What Changes

- Com o kit ao lado, a conferência das regras compara a pasta `trilha/` do projeto com a `modelo/trilha/` da versão do projeto: a cópia de trabalho do kit, quando as versões são iguais; a tag `vX.Y` do kit, quando são diferentes. Kit noutra versão só avisa, com o `kit.py atualizar`; sem a tag da versão do projeto, avisa que a pasta não foi comparada.
- A falha da cópia divergente passa a dizer para rodar o `kit.py atualizar`, nunca para editar a pasta.
- A conferência das regras avisa quando o `"disableAllHooks": true` está no `.claude/settings.json` ou no `.claude/settings.local.json` do projeto.
- O kit vai à 2.4 (o comum e o `plugin.json`), e os textos que descrevem o `--fonte` acompanham.

**Fora desta change:** a migração dos projetos; o CI dos projetos; o `kit.py`; os achados aceitos da auditoria (N02, N11, N14, N25 e os de texto); o que o usuário escolhe por sessão (`--bare`, `--settings`), que a trava do commit continua conferindo.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `conferencias`: a cópia da pasta do método é comparada com a versão do projeto, e não com a cópia de trabalho do kit; as travas desligadas pela configuração ganham requisito, com o aviso do `disableAllHooks`.

## Impact

- Kit: `modelo/trilha/confere_regras.py` e o comentário do `modelo/trilha/verifica.sh`; `testes/test_kit.py`; a versão no `modelo/trilha/CLAUDE-comum.md` e no `plugins/sdd/.claude-plugin/plugin.json`; o README.
- Projetos: a próxima cópia do kit (a 2.4) traz a conferência nova; até lá, nada muda neles.
