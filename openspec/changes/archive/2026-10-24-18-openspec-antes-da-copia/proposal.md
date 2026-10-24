# Proposal

## Why

Pedido do usuário, de 2026-10-24, depois da revisão do plano de migração dos projetos: quando o `openspec update` apagaria arquivos do projeto, o `kit.py atualizar --openspec` só descobre isso depois de copiar o kit. Ele sai com o código 1 e deixa a cópia sem commit, e rodá-lo de novo é recusado ("há trabalho não commitado"). O plano teve de documentar um caminho de quatro passos à mão para sair desse beco.

A descrição curta foi aprovada pelo usuário.

## What Changes

- Com `--openspec`, o `kit.py atualizar` põe o OpenSpec da máquina na versão do kit (o `npm install -g`, só quando a da máquina é outra ou falta) e roda o `openspec update --dry-run --json` **antes** de mudar qualquer arquivo do projeto.
- Se o dry-run listar arquivos do projeto a apagar, a ferramenta recusa sem mudar nada no projeto. A recusa nomeia os arquivos e as duas saídas: ajustar o perfil (`openspec config list`, `openspec config profile`) ou rodar de novo com `--aceitar-apagados`.
- A opção nova `--aceitar-apagados`, que só vale com `--openspec`, deixa o update apagar esses arquivos e os lista num aviso. Sem ela, nada se apaga, como hoje.
- As outras falhas do OpenSpec que acontecem antes da cópia (o `npm` que falta ou falha, o `openspec` do PATH noutra versão depois da instalação, o dry-run com erro) também passam a recusar sem mudar o projeto. Só o `openspec update` com erro, que roda depois da cópia, continua deixando a cópia sem commit.
- Como o projeto fica como estava depois da recusa, basta rodar o comando de novo, sem passo à mão.
- O uso no `kit.py` e o `README.md` citam a opção nova.

**Fora desta change:**
- a limpeza do legado do OpenSpec: o update do kit continua sem `--force`;
- a troca da versão do OpenSpec no CI do projeto, que continua à mão, com o aviso de hoje;
- o perfil do OpenSpec da máquina, que continua escolha do usuário;
- o plano de migração e o roteiro de validação (`docs/plano-migracao-projetos.md` e `ferramentas/validar-projeto.md`), que perdem o caminho à mão depois do merge, fora da change;
- a versão do método: a ferramenta é só do kit, não vai aos projetos.

**Efeito que fica:** a máquina pode mudar de versão mesmo quando o projeto é recusado, porque o dry-run só vale na versão do kit.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `ferramenta-do-kit`: o dry-run do `--openspec` antes da cópia, a recusa sem mudar o projeto (quando o update apagaria arquivos e quando o OpenSpec falha antes da cópia) e a opção `--aceitar-apagados`.

## Impact

- `ferramentas/kit.py`: a ordem do `atualizar` com `--openspec`, a opção `--aceitar-apagados` e o uso.
- `testes/test_kit.py`: os testes do `--openspec` ajustados à recusa e os novos (rodar de novo depois da recusa, o aceite dos apagados, a opção sem o `--openspec`).
- `README.md`: a atualização de um projeto.
