# Design

## Context

Ver `proposal.md` (Why). Hoje o `atualizar` faz, em ordem: as recusas (o git, o trabalho não commitado, a branch, o `ANDAMENTO.md`, a `trilha/` de outra coisa, o `settings.json`), a conferência do kit, a migração do layout antigo, a cópia, a criação do que falta, as travas, as regras do `config.yaml`, os avisos da parte fixa, a página e, só então, com `--openspec` e a migração do `check.sh` feita, o `_atualizar_o_openspec`: a versão, o `npm install -g`, o dry-run e o update. Uma falha ali vira "FALHA: ...", com a cópia já feita.

Quem decide o que o `openspec update` apaga é o perfil da máquina (global, em `openspec config path`) diante dos arquivos gerados que o projeto tem (as skills e os comandos do OpenSpec). A cópia do kit não toca nenhum dos dois. Ela pode, porém, criar a pasta `openspec/`: o `openspec/config.yaml` é um dos arquivos que ela cria quando faltam, e o `openspec update` (também o dry-run) falha sem essa pasta ("No OpenSpec directory found.").

## Goals / Non-Goals

**Goals:**
- Tudo o que pode recusar o OpenSpec acontece antes de o projeto mudar, e a recusa deixa o projeto pronto para rodar de novo.

**Non-Goals:**
- Desfazer o que a cópia fez quando o `openspec update` falha depois dela: esse caso continua como hoje (a cópia fica, sem commit).
- Desfazer a instalação do OpenSpec na máquina quando o projeto é recusado.

## Decisions

### D1. A preparação do OpenSpec antes de mudar o projeto
Com `--openspec`, depois das recusas de hoje e da conferência do kit, e antes da migração e da cópia, vem a preparação: (0) a pasta `openspec/` do projeto, sem a qual o dry-run não roda (conferida antes até da previsão da migração do `check.sh`, porque não mexe na máquina), e a versão fixada no CI do modelo do kit; (1) o `openspec --version`; (2) o `npm install -g @fission-ai/openspec@X`, se a versão for outra ou faltar, e o `openspec --version` de novo, que tem de responder X; (3) o `openspec update --dry-run --json` na pasta, com os apagados separados entre os do projeto e os de fora, como hoje. Depois da cópia, só o `openspec update`, antes das conferências.

*Alternativa:* um segundo dry-run depois da cópia, para conferir que o plano não mudou. Recusada: a cópia não toca o que decide os apagados (o perfil e os arquivos gerados), então ele repetiria o primeiro e abriria de novo o caminho da falha com a cópia feita.

*O projeto sem a pasta `openspec/`:* a preparação recusa logo, antes do `npm`, mandando rodar o `atualizar` sem `--openspec`, fazer o commit e rodar de novo com `--openspec`. *Alternativa:* nesse caso, deixar o dry-run e o update para depois da cópia, que cria a pasta. Recusada: traria de volta, só para esse caso, o caminho da falha com a cópia feita, e todo projeto do método já tem a pasta `openspec/`.

### D2. A migração do check.sh prevista sem escrever
A regra de hoje (sem a migração do `check.sh`, nem o `npm` nem o update) depende de saber se a migração vai falhar, e a preparação vem antes dela. A troca sai do `_migrar_check` para uma função pura que recebe o texto do `check.sh` e devolve o texto migrado, ou nada quando não sabe trocar a parte fixa antiga. O `_migrar_check` passa a usá-la para escrever, e a preparação só roda quando o texto que ela devolve (ou o de hoje, sem parte antiga) não tem `scripts/confere_`. Assim, a previsão e a migração respondem igual também no caso em que a troca dá certo e sobra outra chamada aos `scripts/confere_*`. Quando responde que não, o `atualizar` avisa que o `--openspec` não roda por causa do `check.sh` e segue como hoje: copia, não chama o OpenSpec e termina com a FALHA da migração.

### D3. As falhas da preparação são recusas
O projeto sem a pasta `openspec/`, o CI do modelo do kit sem a versão do OpenSpec, o `npm` que falta ou falha, o `openspec` do PATH noutra versão depois da instalação, o dry-run com erro (ou sem o JSON dele) e os apagados do projeto sem `--aceitar-apagados` levantam a `Recusa`, como as outras condições do começo: "recusado: ..." na saída de erro e o código 1. A saída do `npm` e a do dry-run que falhou aparecem recuadas antes, como hoje; como a recusa sai pela saída de erro e o resto pela saída comum, o `main` esvazia a saída comum antes de imprimir a recusa, para a ordem valer também com as duas juntas num pipe. Como nada do projeto mudou, a recusa não fala em "arquivos copiados".

*Alternativa:* manter o "FALHA: ...". Recusada: no kit, "FALHA" quer dizer que o projeto mudou e reprovou; "recusado" quer dizer que ele não mudou, que é o caso agora.

### D4. A mensagem da recusa dos apagados
Ela nomeia todos os arquivos do projeto que o update apagaria, sem cortar a lista, e as duas saídas: conferir o perfil com `openspec config list` e ajustá-lo com `openspec config profile`, ou rodar de novo com `--aceitar-apagados` para deixá-los sair. Os apagados fora do projeto seguem só no aviso, sem recusar, como hoje.

### D5. A opção --aceitar-apagados
Um `store_true` do `argparse`. Sem o `--openspec`, o `parser.error` a recusa antes de qualquer coisa, como o `--openspec` no `novo` hoje (código 2), com a frase "o --aceitar-apagados só vale no atualizar, com o --openspec", que serve também ao `novo`. Com ela, os apagados do projeto viram um aviso que os nomeia ("o openspec update vai apagar, no projeto: ..."), e o update roda. Ela não muda nada quando o dry-run não apaga nada.

## Risks / Trade-offs

- [A máquina muda de versão mesmo quando o projeto é recusado] → É o pedido do `--openspec`, e o dry-run só vale na versão do kit. A saída do `npm` aparece antes da recusa, e o `README.md` diz isso.
- [O `--aceitar-apagados` apaga arquivos que o projeto versiona] → Só sob pedido explícito; o aviso os nomeia, o `git status` do fim os mostra, e nada é commitado.
- [O plano do dry-run e o update ficam separados pela cópia] → A cópia não toca o perfil nem os arquivos gerados (D1); um perfil mudado à mão nesse intervalo, de segundos, é o único caso, e o `git status` do fim mostraria o efeito.
- [A cópia cria a pasta `openspec/` que falta, e o dry-run feito antes dela falharia sempre] → A preparação confere a pasta antes de tudo e recusa com o caminho de saída (D1).

## Verificação

**Os testes antes do código (tarefas 1.1 a 1.3):** os quatro testes ajustados à recusa e os quatro novos da 1.2 falharam antes do código, pelo motivo esperado (a FALHA com a cópia feita no lugar da recusa; a opção desconhecida). O `test_atualizar_openspec_nao_roda_com_a_chamada_que_sobra` passou antes, como previsto: ele protege a previsão da D2, num comportamento que o código de antes já tinha.

**Execução manual (tarefa 3.2), em 2026-10-24,** com o OpenSpec 1.15.0 de verdade, num projeto descartável no scratchpad feito pelo `kit.py novo` e pelo `openspec init --tools claude`, com o `XDG_CONFIG_HOME` e o `HOME` no scratchpad e um perfil próprio sem o `onboard` (o `core` padrão o traz), a `trilha/verifica.sh` editada e uma skill `openspec-onboard` commitadas; o dry-run listava essa skill para apagar:
- o `kit.py atualizar --openspec` terminou com 1: "recusado: o openspec update apagaria .claude/skills/openspec-onboard/SKILL.md: confira o perfil com openspec config list e ajuste-o com openspec config profile, ou rode de novo com --aceitar-apagados para deixá-los sair; o projeto não mudou"; o `git status` ficou vazio e a edição da `trilha/` continuou lá;
- de novo, com `--aceitar-apagados`, terminou com 0, com o aviso "o openspec update vai apagar, no projeto: .claude/skills/openspec-onboard/SKILL.md"; a skill saiu e a `trilha/verifica.sh` voltou à do kit;
- com `--aceitar-apagados` sem `--openspec`: "kit.py: error: o --aceitar-apagados só vale com o --openspec", código 2.

**Depois das respostas à revisão (tarefa 4.2), em 2026-10-24,** no mesmo projeto, de volta ao estado commitado, com a saída de erro junta à comum (`2>&1`): a recusa veio por último, com o `git status` vazio; o `--aceitar-apagados` terminou como antes (a skill saiu e a `trilha/` voltou à do kit); e o `kit.py novo <pasta> --aceitar-apagados` respondeu "o --aceitar-apagados só vale no atualizar, com o --openspec", sem criar a pasta.

Fora do escopo, visto aqui: com a versão do comum igual à do kit, o commit sugerido é o "dos arquivos gerados pelo OpenSpec" (change 16), mesmo quando a cópia também trocou um arquivo da `trilha/`, como neste teste, que a editou de propósito.

## Respostas à revisão

### Revisão dos artefatos, antes do apply

De 2026-10-24, por um agente sem o contexto da sessão; as correções entraram pelo `/opsx:update`.

- **A1 (o projeto sem a pasta `openspec/` seria recusado para sempre):** aplicado. A preparação confere a pasta antes do `npm` e recusa com o caminho de saída (D1, D3); o cenário "Projeto sem a pasta openspec" e o `test_atualizar_openspec_sem_a_pasta_openspec_recusa`.
- **A2 (a previsão da migração não cobria a chamada aos `scripts/confere_*` que sobra depois da troca):** aplicado. A troca vira uma função pura que a migração e a previsão usam (D2); o `test_atualizar_openspec_nao_roda_com_a_chamada_que_sobra`.
- **A3 (o teste da opção sem o `--openspec` passaria antes do código):** aplicado. O cenário pede a frase de que o `--aceitar-apagados` só vale com o `--openspec`, e o teste confere a ausência de "unrecognized arguments".
- **A4 (o comando da tarefa 2.1 rodaria um teste da 2.2):** aplicado. As duas viraram a 2.1.
- **A5 (o CI do modelo sem a versão fora da lista das recusas):** aplicado, no D3 e no requisito.
- **A6 (a execução manual sem isolar a configuração global e sem dizer como criar a skill fora do perfil):** aplicado, na tarefa 3.2.

### O verify e o code review

Do `/opsx:verify` (V1 a V3) e do `/code-review` da branch, no nível high (R1 a R6), de 2026-10-24, cada um por um agente sem o contexto da sessão. Nenhum achado crítico; todos aplicados, com o teste escrito antes do código quando o achado é de comportamento.

- **V1 e R3 (a ajuda do `--openspec` não cita o `--aceitar-apagados` e diz que toda falha recusa):** aplicado. A ajuda diz que o dry-run vem antes de mudar o projeto, que o que falha ali recusa, e que o update roda depois da cópia, se o dry-run não apagar arquivo do projeto ou com o `--aceitar-apagados`.
- **V2 (o docstring sem a recusa antes da cópia e sem a máquina que muda):** aplicado, numa linha a mais no uso.
- **V3 e R6 (o CI do modelo sem a versão sem cenário nem teste):** aplicado. O cenário "CI do modelo sem a versão do OpenSpec" e o `test_atualizar_openspec_ci_do_modelo_sem_a_versao_recusa`, que passou antes do código, porque a recusa já estava lá: faltava cobri-la.
- **R1 (a recusa sai antes da saída que ela cita, com as duas saídas juntas num pipe):** aplicado. O `main` esvazia a saída comum antes da recusa (D3); o `test_atualizar_openspec_recusa_depois_da_saida_que_cita`, que falhou antes.
- **R2 (o projeto sem `openspec/` e com o `check.sh` fora do padrão não é recusado, e o `--openspec` some calado):** aplicado. A pasta `openspec/` é conferida antes da previsão da migração, e o `--openspec` que não roda por causa do `check.sh` avisa (D1, D2); o `test_atualizar_openspec_sem_a_pasta_openspec_e_check_antigo_recusa` e o aviso no `test_atualizar_openspec_nao_roda_com_a_migracao_que_falha`, que falharam antes.
- **R4 (o README dá o remédio do perfil para toda falha):** aplicado. A frase das falhas em geral ("a recusa diz o que falhou; corrija e rode de novo") fica separada da dos apagados (o perfil ou o `--aceitar-apagados`).
- **R5 (o `novo --aceitar-apagados` leva a um segundo erro):** aplicado. A frase do erro passa a "só vale no atualizar, com o --openspec".
- **Os achados que o code review deixou de fora**, recusados com o motivo dele: a regra `"scripts/confere_" not in migrado` repetida em duas funções (sem efeito); a recusa sem dizer que a máquina pode ter mudado (o README, a ajuda e o docstring já dizem, e a saída do `npm` aparece antes). O teste que carregava o `kit.py` de novo passou a usar o `FERRAMENTA` dos testes.
