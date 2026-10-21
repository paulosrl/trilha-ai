# Design

## Context

Ver `proposal.md` (Why). O `trilha/tempo.py` da 2.9:
- o `_eventos` lê todo arquivo que cita a raiz duas vezes: a primeira só procura o caminho, a segunda decodifica toda linha com `"cwd"`. No fim, ele descarta a conversa sem nenhum evento da raiz;
- o `main` recalcula cada conversa vista; com o resumo da versão 1, sem as horas guardadas dela;
- o `_commits` lê o `user.email` e os `trilha.email`, e o `_ler_commits` conta os e-mails de fora num dicionário recebido por argumento;
- o `_aviso_de_outra_pasta` só procura outro resumo quando não há o deste caminho, e o `main` cria esse resumo na mesma execução.

## Goals / Non-Goals

**Goals:**
- Nenhuma hora guardada fica presa num resumo que o comando não lê mais.
- Os commits que o git grava com o e-mail do usuário contam como do usuário.
- O aviso dos e-mails de fora tem um remédio que o cala sem errar as horas.

**Non-Goals:**
- O achado 2 e os outros itens de "Fora desta change" do proposal.

## Decisions

### D1. A leitura de um arquivo que cita a raiz
O primeiro passo decodifica só as linhas que citam a raiz, como na 2.8. Ele para na primeira linha que é um evento da raiz, e então o segundo passo decodifica, do começo, toda linha com `"cwd"`, como na 2.9. Se nenhuma linha que cita a raiz é evento dela, o arquivo não tem evento da raiz: os eventos "fora" que o primeiro passo achou valem, e o segundo passo não roda.

Assim, a conversa de outro repositório que só cita este caminho custa o que custava na 2.8. A conversa da raiz decodifica de novo só as linhas antes do primeiro evento dela.

*Alternativa:* decodificar no segundo passo só as linhas de conversas que já têm evento da raiz. Recusada: a saída da raiz pode vir antes do primeiro evento dela no arquivo, e o `sessionId` só se conhece decodificando.

### D2. A conversa sem evento da raiz
O `_eventos` deixa de descartar a conversa só com eventos "fora". Para cada conversa vista, o `main` junta as horas guardadas (só com o resumo da versão 2) às recalculadas; quando o resultado é vazio, a conversa sai do resumo, e não entra quando não estava. Com o resumo da versão 2, a conversa guardada e agora só "fora" mantém as horas guardadas, porque o `_juntar` delas com nada é o que já estava. Com o da versão 1, a conversa do repositório aninhado é recalculada para nada e sai.

O arquivo sem evento da raiz continua indo para os ignorados, como na 2.9: a conversa dele já foi recalculada nesta execução.

### D3. Os e-mails de autor do git
O git escolhe o e-mail de autor do commit nesta ordem: `GIT_AUTHOR_EMAIL`, `author.email`, `user.email`. O comando junta os três que existirem, não vazios, aos do `trilha.email`: os três são do usuário, e o commit antigo pode ter sido feito com qualquer um. Sem nenhum dos três, contam os commits de todos, como hoje.

*Alternativa:* o `git var GIT_AUTHOR_IDENT`. Recusada: sem e-mail configurado, ele inventa um a partir do nome da máquina (ou falha, com o `user.useConfigOnly`), e o caso "sem e-mail, contam todos" deixaria de valer.

### D4. O `trilha.outro`
Os e-mails de `git config --get-all trilha.outro` saem do aviso, sem diferença de maiúscula, como os de robôs. Os commits deles continuam fora da estimativa. O aviso passa a terminar com os dois comandos: `git config --add trilha.email <e-mail>` se o e-mail é do usuário, e `git config --add trilha.outro <e-mail>` se é de outra pessoa.

*Alternativa:* guardar no resumo os e-mails já avisados e avisar só os novos. Recusada: o aviso perdido na primeira execução nunca mais sairia, e os commits do usuário ficariam fora sem que ele soubesse.

### D5. O resumo de outra pasta
Os outros resumos se acham como na 2.9: o nome exato `<nome>-<8 hexadecimais>.json`, com a `raiz` gravada de mesmo nome e diferente da atual; o ilegível é ignorado. A busca agora roda em toda execução, depois de ler o resumo deste caminho:
- **a raiz gravada não existe mais:** as conversas dele entram no resumo atual, cada uma pelo `_juntar` com a deste resumo, se houver. O resumo atual é gravado, e só depois o antigo é renomeado para `<nome>.json.juntado`, sem ser apagado. O aviso diz que as horas de `<raiz antiga>` vieram e cita o arquivo renomeado;
- **a raiz gravada ainda existe** (outra cópia do repositório): só o aviso de hoje, e só quando não há resumo para este caminho.

As conversas do resumo antigo não se recalculam aqui: o `cwd` delas é a raiz antiga, que não é a atual. A versão do resumo antigo não importa: a 1 só guardava horas a mais das conversas que ainda existiam, e essas o resumo atual recalcula como em D2 se ele for da versão 1; as do antigo entram como estão. Os ignorados do resumo antigo não vêm: as datas e os tamanhos deles valiam para a raiz antiga.

Se a gravação do resumo atual falha, o antigo fica com o nome de sempre, e a execução seguinte junta de novo; o `_juntar` conta o repetido uma vez.

*Alternativa:* juntar só quando não há resumo deste caminho. Recusada: quem rodou o comando antes de apagar a pasta antiga, ou antes de movê-la, ficaria com as horas presas.

### D6. As limpezas
- O `_ler_commits(saida, emails)` devolve `(instantes, fora)`, com o `fora` num `Counter` dos e-mails de fora; sai o dicionário por hash: o `git log` já lista cada commit uma vez, e o dos instantes também vira lista.
- Na página, `palavra(n, um, varios)` devolve só a palavra, e o `pl` a usa. A frase "dia(s) com trabalho", em que o número fica em destaque separado, e o "commit(s)" do `dayTip` passam por ela.

### D7. A versão
"Versão 2.10, de <data do apply>." no comum e `2.10.0` no plugin, antes de qualquer outro arquivo de `modelo/` mudar.

## Risks / Trade-offs

- [Um repositório de mesmo nome, apagado, que não era este (outro projeto com o mesmo nome de pasta)] → As horas dele entrariam neste. É raro: pede o mesmo nome, a mesma pasta de dados e a pasta antiga apagada. O aviso cita a raiz antiga, e o arquivo `.juntado` fica para conferência.
- [A pasta antiga numa unidade desmontada parece apagada] → O mesmo caso: o aviso cita a raiz e o arquivo fica.
- [O `GIT_AUTHOR_EMAIL` do ambiente de quem roda o comando] → Ele vale para os commits dessa sessão; contá-lo como do usuário é o que o git faz.
- [Os testes herdavam o `GIT_AUTHOR_EMAIL` da máquina] → O `_rodar` dos testes o tira do ambiente, salvo quando o teste o passa.

## Migration Plan

Nada a migrar: o resumo continua na versão 2. O resumo da versão 1 que a 2.9 já gravou como versão 2 fica como está (fora, no proposal).
