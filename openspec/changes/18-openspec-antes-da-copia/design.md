# Design

## Context

Ver `proposal.md` (Why). Hoje o `atualizar` faz, em ordem: as recusas (o git, o trabalho não commitado, a branch, o `ANDAMENTO.md`, a `trilha/` de outra coisa, o `settings.json`), a conferência do kit, a migração do layout antigo, a cópia, a criação do que falta, as travas, as regras do `config.yaml`, os avisos da parte fixa, a página e, só então, com `--openspec` e a migração do `check.sh` feita, o `_atualizar_o_openspec`: a versão, o `npm install -g`, o dry-run e o update. Uma falha ali vira "FALHA: ...", com a cópia já feita.

Quem decide o que o `openspec update` apaga é o perfil da máquina (global, em `openspec config path`) diante dos arquivos gerados que o projeto tem (as skills e os comandos do OpenSpec). A cópia do kit não toca nenhum dos dois.

## Goals / Non-Goals

**Goals:**
- Tudo o que pode recusar o OpenSpec acontece antes de o projeto mudar, e a recusa deixa o projeto pronto para rodar de novo.

**Non-Goals:**
- Desfazer o que a cópia fez quando o `openspec update` falha depois dela: esse caso continua como hoje (a cópia fica, sem commit).
- Desfazer a instalação do OpenSpec na máquina quando o projeto é recusado.

## Decisions

### D1. A preparação do OpenSpec antes de mudar o projeto
Com `--openspec`, depois das recusas de hoje e da conferência do kit, e antes da migração e da cópia, vem a preparação: (1) o `openspec --version`; (2) o `npm install -g @fission-ai/openspec@X`, se a versão for outra ou faltar, e o `openspec --version` de novo, que tem de responder X; (3) o `openspec update --dry-run --json` na pasta, com os apagados separados entre os do projeto e os de fora, como hoje. Depois da cópia, só o `openspec update`, antes das conferências.

*Alternativa:* um segundo dry-run depois da cópia, para conferir que o plano não mudou. Recusada: a cópia não toca o que decide os apagados (o perfil e os arquivos gerados), então ele repetiria o primeiro e abriria de novo o caminho da falha com a cópia feita.

### D2. A migração do check.sh prevista sem escrever
A regra de hoje (sem a migração do `check.sh`, nem o `npm` nem o update) depende de saber se a migração vai falhar, e a preparação vem antes dela. A condição sai do `_migrar_check` para uma função que só lê o `check.sh` e responde se a parte fixa antiga, se existir, é a que o kit sabe trocar. O `_migrar_check` passa a usá-la, e a preparação só roda quando ela responde que sim. Quando responde que não, o `atualizar` segue como hoje: copia, não chama o OpenSpec e termina com a FALHA da migração.

### D3. As falhas da preparação são recusas
O `npm` que falta ou falha, o `openspec` do PATH noutra versão depois da instalação, o dry-run com erro (ou sem o JSON dele) e os apagados do projeto sem `--aceitar-apagados` levantam a `Recusa`, como as outras condições do começo: "recusado: ..." na saída de erro e o código 1. A saída do `npm` e a do dry-run que falhou aparecem recuadas antes, como hoje. Como nada do projeto mudou, a recusa não fala em "arquivos copiados".

*Alternativa:* manter o "FALHA: ...". Recusada: no kit, "FALHA" quer dizer que o projeto mudou e reprovou; "recusado" quer dizer que ele não mudou, que é o caso agora.

### D4. A mensagem da recusa dos apagados
Ela nomeia todos os arquivos do projeto que o update apagaria, sem cortar a lista, e as duas saídas: conferir o perfil com `openspec config list` e ajustá-lo com `openspec config profile`, ou rodar de novo com `--aceitar-apagados` para deixá-los sair. Os apagados fora do projeto seguem só no aviso, sem recusar, como hoje.

### D5. A opção --aceitar-apagados
Um `store_true` do `argparse`. Sem o `--openspec`, o `parser.error` a recusa antes de qualquer coisa, como o `--openspec` no `novo` hoje (código 2). Com ela, os apagados do projeto viram um aviso que os nomeia ("o openspec update vai apagar, no projeto: ..."), e o update roda. Ela não muda nada quando o dry-run não apaga nada.

## Risks / Trade-offs

- [A máquina muda de versão mesmo quando o projeto é recusado] → É o pedido do `--openspec`, e o dry-run só vale na versão do kit. A saída do `npm` aparece antes da recusa, e o `README.md` diz isso.
- [O `--aceitar-apagados` apaga arquivos que o projeto versiona] → Só sob pedido explícito; o aviso os nomeia, o `git status` do fim os mostra, e nada é commitado.
- [O plano do dry-run e o update ficam separados pela cópia] → A cópia não toca o perfil nem os arquivos gerados (D1); um perfil mudado à mão nesse intervalo, de segundos, é o único caso, e o `git status` do fim mostraria o efeito.
