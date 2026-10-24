# Proposal

## Why

Pedido do usuário, de 2026-10-24, depois da troca do OpenSpec para a 1.15.0 (change 14): ao atualizar um projeto pelo kit, verificar a versão do OpenSpec ou atualizá-lo de forma automática. Hoje o `kit.py atualizar` não mexe no OpenSpec: a conferência do método só avisa a versão diferente da do CI e o que o `openspec update` mudaria, e o usuário instala e roda o update à mão, em cada projeto.

A descrição curta foi aprovada pelo usuário.

## What Changes

- O `kit.py atualizar <pasta> --openspec` instala o OpenSpec na versão fixada no CI do modelo do kit (`npm install -g @fission-ai/openspec@X`) só quando a da máquina é outra ou falta, e depois roda o `openspec update` na pasta do projeto, antes da conferência.
- Antes do update, ele roda o `openspec update --dry-run --json`: se o update fosse apagar algum arquivo do projeto (um perfil da máquina sem o que o projeto versiona), ele não roda o update e falha, nomeando os arquivos e o `openspec config list`.
- Uma falha da parte do OpenSpec (sem o `npm`, a instalação com erro, o dry-run ou o update com erro) termina com o código 1 e uma FALHA que diz o que faltou, sem sugerir o commit; o que o kit já copiou fica, sem commit, como na falha da conferência.
- Sem a opção, o `atualizar` não chama o `npm` nem o `openspec update`; quando a versão da máquina difere da do kit, ele avisa, citando a opção.
- O README e o uso no `kit.py` citam a opção.

**Fora desta change:**
- instalar o Node e o `npm`, ou o OpenSpec sem o Node;
- mudar o perfil do OpenSpec da máquina;
- o `kit.py novo`, que continua sem instalar nada;
- a versão do método: a ferramenta é só do kit, não vai aos projetos.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `ferramenta-do-kit`: a atualização do OpenSpec sob pedido no `kit.py atualizar`, com a recusa do update que apagaria arquivos, as falhas e o aviso da versão sem a opção.

## Impact

- `ferramentas/kit.py` (a opção `--openspec` no `atualizar`).
- `testes/test_kit.py`: um `npm` e um `openspec` falsos e os testes dos cenários.
- `README.md` (a atualização de um projeto).
