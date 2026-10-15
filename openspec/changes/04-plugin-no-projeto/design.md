# Design

## Context

Hoje o `kit.py` soma ao `.claude/settings.json` do projeto só o hook da trava (`_ligar_travas`), lendo a entrada do `modelo/claude-settings.json`. A conferência do método (`confere_metodo.py`) lê `claude plugin list --json` na pasta de onde foi chamada e julga toda instalação `sdd@…` da lista.

Um experimento feito no propose, numa pasta descartável e desfeito depois (a lista de instalações da máquina voltou igual), mostrou como o Claude Code 2.1.301 trata o escopo de projeto:
- `claude plugin install sdd@trilha-ai --scope project` grava `enabledPlugins` no `.claude/settings.json` da pasta e cria na lista uma entrada com `"scope": "project"` e `"projectPath"`.
- Essa entrada aparece também quando a lista roda em **outra** pasta, com `"enabled": true`, mesmo sem valer ali. O `projectEnabled` só diz se o settings.json da pasta atual liga o plugin.
- O `enabled` de uma entrada de escopo `user` segue o settings.json da pasta atual: com o projeto declarando o plugin falso, a lista o dá desligado.
- Com a instalação do usuário e a do projeto, a lista traz as duas, cada uma com a sua versão.

## Goals / Non-Goals

**Goals:**
- Uma só fonte para o que o projeto declara: o `modelo/claude-settings.json`.
- O aviso do plugin certo para o projeto, e não para a máquina inteira.

**Non-Goals:**
- Rodar o `claude plugin install` pelo `kit.py`: é estado da máquina, como o perfil do OpenSpec, que a ferramenta só lê.
- Avisar a instalação de escopo `user` como excesso: ela ainda serve aos projetos não migrados.

## Decisions

1. **A soma do settings.json lê o modelo inteiro.** A função que hoje liga o hook passa a somar o modelo todo, de forma genérica: a chave que falta entra, o objeto presente nos dois é somado chave por chave, e o item de lista entra quando nenhum item do projeto o contém (contém = as chaves do item do modelo estão nele, com valores contidos; assim, o grupo do projeto que tem a trava e um gancho próprio não ganha a trava de novo). O valor que o projeto já deu fica, e com ele o `false` que o projeto pôs no plugin. Antes da soma, sai a trava de outra versão do kit (`scripts/guarda.py`, ou `trilha/guarda.py` chamada de outro jeito), com o grupo que só a tinha. Uma só comparação do arquivo inteiro, antes e depois, decide se ele é escrito, e por isso a segunda atualização não o toca. O settings.json que a soma não entende (JSON inválido, ou outro tipo, até `null`, onde o modelo tem objeto ou lista) é recusado no começo do `atualizar`, antes de mudar qualquer arquivo. *Alternativas descartadas:* sobrescrever as chaves com as do modelo (apagaria os plugins e marketplaces próprios do projeto); somar só as chaves listadas no código (a chave nova do modelo não chegaria aos projetos, sem aviso).

2. **O comando de instalação é impresso, nunca rodado.** O `novo` o põe nos próximos passos, no lugar do passo de instalar o plugin. O `atualizar` não o imprime por conta própria: a conferência do método, que ele roda, avisa quando o projeto declara o plugin e a máquina o tem só para o usuário (decisão 9). Assim o aviso aparece só quando vale, e também nas máquinas que recebem o projeto pelo git e nunca rodam o `kit.py`. O texto vem de uma constante no `kit.py`, e o da conferência, de outra no `confere_metodo.py`, que os projetos copiam sem o `kit.py`. Um teste confere que as duas dizem o mesmo comando. *Alternativa descartada:* importar uma da outra; o `confere_metodo.py` roda no projeto, onde o `kit.py` não existe.

3. **A lista roda na pasta do projeto** (`cwd` igual à raiz do projeto, a pasta acima de `trilha/`). Sem isso, o `enabled` da entrada `user` refletiria a pasta de onde o `check.sh` ou o CI chamou.

4. **Valem as instalações deste projeto e as da máquina inteira; todas são julgadas.** A entrada com `projectPath` de outra pasta é descartada (o caminho é comparado resolvido); as sem `projectPath` (`user`, ou outro escopo da máquina inteira) e as de escopo `local` ou `project` desta pasta são julgadas uma a uma, e o aviso de versão diz o escopo e dá `claude plugin update sdd@trilha-ai --scope <escopo>`. A primeira versão desta decisão ficava com a mais específica, pela precedência das configurações do Claude Code; a execução manual a desmentiu: com a instalação do usuário (1.35.0) e a do projeto (2.1.0), uma sessão aberta no projeto carregou a do usuário. Não foi possível separar "o usuário prevalece" de "vale a gravada primeiro" sem mexer na instalação real (o Claude Code recusou os marketplaces locais servidos por git num `CLAUDE_CONFIG_DIR` isolado). Julgar todas acerta nas duas hipóteses: a que carrega, seja qual for, é conferida. *Alternativas descartadas:* a mais específica (desmentida); a do usuário sempre (sem prova, e erraria se a regra for a ordem de gravação).

5. **Os padrões técnicos são um arquivo a preencher.** `sdd/padroes-tecnicos.md` entra no `A_PREENCHER` do `kit.py`, com a origem `modelo/sdd/padroes-tecnicos.md`: o `novo` o copia, o `atualizar` só o cria quando falta e avisa, como os outros preenchidos, mas só na passagem de uma versão anterior à 2.2 (`APAGAVEIS`, com a versão que trouxe o arquivo): desde a 2.2, a falta dele é a escolha do projeto de ficar sem padrões, que a skill aceita, e a atualização não o recria. Não entra na parte fixa (`COM_PARTE_FIXA`): o arquivo é inteiro do projeto. O `novo` cria `sdd/` já com o arquivo, e o `mkdir` que havia sai. O conteúdo é a seção "Defaults institucionais" da skill, com a primeira linha dizendo para que serve e que o desvio vira ADR, e com o Python em `requires-python = ">=3.12.3"` na seção `[project]` do `pyproject.toml`. *Alternativa descartada:* o arquivo na raiz do projeto; o comum põe os documentos do método em `sdd/`, e é a skill `tdd` quem o lê.

6. **A skill lê o arquivo; o princípio 4 continua.** A seção 4 da skill `tdd` passa a "Padrões técnicos do projeto": ler o `sdd/padroes-tecnicos.md` quando existir e tomá-lo como ponto de partida, confirmado na entrevista; sem ele, recomendar só pela entrevista, sem inventar padrão. O princípio 4 ("declarados, nunca impostos") passa a apontar para o arquivo.

7. **O esqueleto do `CLAUDE.md` lista o arquivo** na linha de `sdd/`. O comum não muda além da versão.

8. **A conferência sem `sdd/` continua.** Projetos antigos podem não ter a pasta; o teste do aviso "sem a pasta sdd/" passa a apagar a pasta que a cópia do kit agora traz, e os testes que criam `sdd/` passam a aceitá-la existente. O aviso manda criar a pasta e copiar para ela o `modelo/sdd/padroes-tecnicos.md`. Como o `atualizar` agora pode criar `sdd/` num projeto antigo, ele só gera de novo a página que já existe: o `sdd/documentacao.html` nasce ao fechar uma etapa (o comum), e não vazio na atualização.

9. **O aviso da instalação que falta no projeto.** Quando o `.claude/settings.json` declara o plugin ligado e a lista o traz só para a máquina inteira, a conferência avisa `claude plugin install sdd@trilha-ai --scope project`. O projeto que não declara o plugin (o de antes da 2.2) segue sem esse aviso, com a instalação do usuário.

10. **O desligado vem das configurações da pasta.** A conferência lê a declaração do plugin que vale na pasta: o `.claude/settings.local.json`, que prevalece, e o `.claude/settings.json`; sem nenhuma, o "ligado" da lista, que segue o settings do usuário. O aviso sai uma vez, com `claude plugin enable sdd@trilha-ai --scope <escopo>` no escopo que desliga. Num teste em pasta descartável (Claude Code 2.1.301, desfeito depois, com as instalações e o settings do usuário iguais aos de antes): o `enable --scope project` grava `true` no settings.json da pasta mesmo com a instalação só do usuário; o `projectEnabled` da lista não lê o `settings.local.json`, e o `enabled` da instalação de projeto não segue a pasta. *Alternativa descartada:* julgar pelo `enabled` de cada instalação; a de projeto desligada pela pasta passaria por ligada, e com as duas instalações o aviso sairia duas vezes.

## Risks / Trade-offs

- [Com a instalação do usuário e a do projeto, não se sabe qual o Claude Code carrega em toda ordem de instalação] → a conferência julga as duas (decisão 4), e o README manda tirar a do usuário quando todos os projetos da máquina tiverem o plugin instalado no projeto, avisando que, até lá, ela pode ser a que a sessão carrega.
- [A lista do Claude Code pode mudar o formato da entrada de projeto] → sem `projectPath`, a entrada conta como da máquina inteira, que é o comportamento de hoje.
- [O projeto na 2.1 com o plugin 2.2 perde os padrões] → o aviso de versão diferente já existe e manda atualizar o que estiver atrás.

## Migration Plan

O `kit.py atualizar` de cada projeto traz a declaração e o arquivo dos padrões (item 10 do plano, com a ordem do usuário). Em cada máquina, depois: `claude plugin install sdd@trilha-ai --scope project` em cada projeto e, quando todos declararem o plugin, `claude plugin uninstall sdd@trilha-ai` (o escopo do usuário), como o README passa a dizer. Reverter é voltar à tag `v2.1`: a declaração a mais no settings.json não quebra nada.
