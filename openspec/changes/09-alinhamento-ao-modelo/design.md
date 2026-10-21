# Design

## Context

Motivação: ver `proposal.md`, em "Why". O estado atual:

- O `kit.py atualizar` avisa a parte fixa de quatro arquivos (`.gitignore`, `scripts/check.sh`, o CI e o Dependabot). O `_avisar_parte_fixa` compara o modelo da versão do projeto com o atual. Só a linha nova que falta no projeto, ou a velha que sobra nele, vira aviso. A linha que já estava no modelo antigo e o projeto nunca copiou fica de fora. Para as regras do `config.yaml`, o `_sincronizar_regras` só troca as regras quando são as de uma versão do kit; senão, imprime "compare-as à mão".
- A conferência das regras, com `--fonte`, compara a pasta `trilha/` com a `modelo/trilha/` da versão do projeto: a cópia de trabalho do kit, na mesma versão; a tag `vX.Y`, noutra (`comparar_com_o_kit`). O `config.yaml` não é lido.
- A conferência do método só consulta a máquina para o plugin, pela lista do Claude Code, atrás do `--sem-plugin` que a trava do commit passa.
- O `openspec update [pasta]` regenera os arquivos gerados das ferramentas que acha na pasta, pelo perfil global (`openspec config path`), e apaga o que o perfil não pede. Ele aceita uma pasta como argumento. `OPENSPEC_NO_UPDATE_CHECK=1` desliga a consulta da versão nova, e `OPENSPEC_TELEMETRY=0`, a telemetria. Medido no Xavier, numa pasta temporária só com os 56 arquivos gerados e o `config.yaml`: 0,16 s com o perfil em dia ("All 5 tool(s) up to date"). Com o perfil antigo, por `XDG_CONFIG_HOME`, ele acusa as 21 pastas de skills que apagaria.

## Goals / Non-Goals

**Goals:**
- Cada divergência da conferência do Xavier ser acusada pela ferramenta do kit que olha aquele arquivo.
- Nenhuma conferência nova depender da rede, nem falhar pelo que é da máquina.

**Non-Goals:**
- Corrigir o projeto sozinho: o `kit.py` e as conferências só avisam ou reprovam.
- Reproduzir por conta própria a lógica do OpenSpec (o mapa entre fluxo e arquivo, a entrega por ferramenta): quem decide o que o `update` faz é o próprio OpenSpec.

## Decisions

**1. Parte fixa: o modelo atual inteiro contra o projeto.** As linhas que faltam passam a ser as linhas fixas do modelo atual (sem comentários, como hoje) que o projeto não tem, pelo `_presente` de hoje. As que sobram seguem pela diferença entre a versão do projeto e a atual, porque só ela sabe o que o kit tirou. Antes da comparação, saem do modelo os parágrafos (blocos separados por linha em branco) da parte da stack, que o próprio modelo manda trocar ou apagar: os que abrem com um comentário que começa por `# Parte da stack`, em qualquer arquivo, e, no `.gitignore`, os de título `# Python` ou `# Node`. Um teste confere que o modelo ainda tem essas marcas.
A presença ganha um caso: a linha do kit também está no projeto quando aparece numa linha dele depois de um espaço e seguida de espaço ou do fim da linha. É a chamada por uma função do projeto (`etapa "…" bash trilha/verifica.sh --vizinho …`, no Xavier). O `fi` continua faltando diante de `find .`. Essas duas regras vieram da primeira rodada da execução manual (tarefa 6.2), que achou os dois falsos positivos no `scripts/check.sh`. A segunda rodada achou o falso negativo de uma primeira versão, que tirava todo bloco com o comentário em qualquer linha: no CI, os passos fixos e o comentário da stack ficam no mesmo bloco, sem linha em branco, e o aviso do `setup-node` sumia. Por isso só sai o bloco que abre com o comentário; no CI e no Dependabot, a parte da stack é só comentário, que a comparação já ignora.
O texto do aviso passa de "mudou no kit desde a X.Y" para "difere do modelo do kit", porque agora cobre a linha antiga. Sem a versão do projeto (`?`), as que faltam são avisadas do mesmo jeito; só as que sobram dependem dela.
Alternativa descartada: avisar todo o arquivo, com os blocos da stack. O projeto de Node receberia, a cada atualização, as linhas do Python que apagou de propósito, e todo projeto com a stack preenchida, o `echo` do exemplo; o aviso viraria ruído.
Alternativa descartada: comparar o modelo inteiro só no `.gitignore` e manter os outros arquivos pela diferença entre as versões. Seria mais simples, mas a linha do CI que o projeto nunca copiou continuaria sem aviso, o mesmo defeito que esta change corrige.

**2. Regras do `config.yaml`: o bloco `rules:` igual e o `operations` contido.** A escolha da versão é a da pasta `trilha/`: a cópia de trabalho de `modelo/openspec/config.yaml` na mesma versão (ou sem versão no projeto); noutra, `git show refs/tags/vX.Y:modelo/openspec/config.yaml`. Sem conseguir ler a versão, a comparação é pulada, porque a da pasta `trilha/` já avisa ou reprova o mesmo caso. Os blocos são lidos por linhas: um bloco de topo começa numa linha sem recuo que abre com uma chave (`nome:`, como o `context: |` e o `rules:`), e não com `#`, e vai até a próxima. O `rules:` é comparado linha a linha, sem as linhas em branco e sem o espaço do fim. No `operations:`, cada linha não vazia do kit, sem o recuo, precisa estar entre as do projeto.
As linhas próprias a mais no `operations` passam porque o projeto pode ter um passo próprio do archive (o Xavier tem a trava dos 500 caracteres). As chaves de topo próprias (o `githubCopilot`, do próprio OpenSpec) passam porque não são do método.
Alternativa descartada: um leitor de YAML. A conferência é Python puro, sem dependências, e o `config.yaml` do modelo é escrito em linhas simples.
Alternativa descartada: só avisar. A regra do método vale para todo projeto, e o comum diz que o `config.yaml` traz as regras por artefato; a pasta `trilha/` diferente já reprova pelo mesmo motivo.

**3. O ensaio do `openspec update` numa pasta temporária.** Os passos:
- pula sem `openspec` no PATH, sem o arquivo de `openspec config path` ou sem resposta dele;
- lista os arquivos gerados pelo `git ls-files` do projeto: os `SKILL.md` em pastas `openspec-*`, os caminhos com um trecho que começa por `opsx` e o `.openspec-target`; sem nenhum, pula;
- copia esses arquivos e o `openspec/config.yaml` para uma `tempfile.TemporaryDirectory`, preservando os caminhos;
- roda `openspec update <pasta>`, com `OPENSPEC_NO_UPDATE_CHECK=1`, `OPENSPEC_TELEMETRY=0` e `DO_NOT_TRACK=1` no ambiente, num prazo de 60 segundos; com erro ou sem resposta, pula;
- compara: o copiado que sumiu, ele apagaria; o copiado de conteúdo diferente, ele trocaria; o arquivo novo na pasta, fora o `config.yaml`, que o projeto não tem igual, ele criaria;
- avisa uma vez, com até cinco nomes por grupo e a contagem do resto, mandando conferir o perfil com `openspec config list` antes de rodar o `update`.

O projeto nunca é tocado: o `update` só vê a pasta temporária.
Alternativa descartada: importar o `profile-sync-drift.js` do OpenSpec pelo `node`. É um módulo interno, sem contrato, e o caminho dele muda de uma versão para outra.
Alternativa descartada: um mapa próprio entre os fluxos do perfil e as pastas de cada ferramenta. Ele envelheceria a cada versão do OpenSpec, que já tem cinco ferramentas e a entrega por ferramenta (o Codex só usa skills).

**4. A versão do OpenSpec contra a do CI.** O `openspec --version` dá a versão. O pin vem da primeira ocorrência de `@fission-ai/openspec@<versão>` no `.github/workflows/verificacao.yml`. Diferentes, avisa, com `npm install -g @fission-ai/openspec@<pin>`. Sem o arquivo, sem o pin ou sem o `openspec`, nada.

**5. Atrás do `--sem-plugin`.** As duas conferências do OpenSpec rodam onde roda o aviso do plugin: no `scripts/check.sh`, e nunca na trava do commit. O nome da opção fica, porque a trava de cada projeto o usa; o texto de ajuda passa a dizer que ela pula o que depende da máquina (o plugin e o OpenSpec).

**6. Versão e texto.** O comum vai à 2.7 e o plugin à 2.7.0 antes de qualquer arquivo de `modelo/` mudar, porque o `test_kit_sem_mudanca_depois_da_tag` reprova a mudança em `modelo/` com o comum na 2.6, que já tem a tag; por isso o `kit.py`, que fica fora de `modelo/`, vem primeiro nas tarefas. O passo 4 do `README.md` do kit passa a pedir o perfil com skills e comandos, além do `verify`.

**Testes que mudam:**
- `test_atualizar_avisa_a_parte_fixa_que_mudou_no_kit`: o texto do aviso passa a "difere do modelo do kit", e a linha antiga que falta passa a aparecer.
- `test_aviso_da_parte_fixa_preciso`: ganha os casos da chamada dentro de uma linha do projeto, sem mudar os que já tem.
- `test_migracao_troca_a_parte_fixa_com_vizinhos` e a asserção do Dependabot no teste acima: o `assertNotIn` procurava o texto antigo ("mudou") e passaria sem conferir nada; passa a procurar "difere".
- Nenhum outro teste muda. Os novos simulam o `openspec` por um script falso no PATH, como os do Claude Code fazem com o `claude`.

## Risks / Trade-offs

- [O CI do projeto difere do modelo de propósito (o Xavier tirou o `setup-node`)] → O aviso do `kit.py` aparece a cada atualização, e não na verificação. É o "traga à mão" de hoje, e quem atualiza decide.
- [Uma versão nova do OpenSpec gera outros nomes de arquivo] → O ensaio usa o próprio OpenSpec. Só a lista dos arquivos copiados depende de nomes (`openspec-*`, `opsx`, `.openspec-target`); um nome novo fora dela vira "criaria", o que avisa em vez de esconder.
- [O ensaio custa tempo na verificação] → 0,16 s medidos com o perfil em dia; o prazo de 60 segundos só vale para um OpenSpec que não responde.
- [Os projetos na 2.6 reprovariam ao receber a 2.7] → É o efeito pedido. O Heimdall e o HubIA têm regras próprias e reprovam até alinhá-las, o que a atualização de cada um, sob ordem do usuário, faz.

## Verificação

- Grupos 1, 3 e 4: cada teste novo rodado antes do código, com a falha esperada (1.1; 3.2, 3.3 e 3.5; 4.1 a 4.3, 4.5, 4.6, 4.8, 4.9 e 4.11) ou passando por guardar o que já valia (1.2; 3.1, 3.4 e 3.6; 4.4, 4.7 e 4.10), e verde depois dele (`python3 -m unittest discover -s testes -k <nome>`).
- 6.1: `python3 -m unittest discover -s testes` → 229 testes, OK, código 0; `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` → código 0; o mesmo com `format --check` → código 0; `openspec validate --all --no-interactive` → 6 itens válidos.
- 6.2, primeira rodada (2026-10-20), o `kit.py atualizar` numa cópia descartável do Xavier no commit `e2115a8`: o `.gitignore` avisado com as seis linhas fora dos blocos da stack (`*.db`, `*.db-shm`, `*.db-wal`, `*.log`, `*.sqlite`, `.DS_Store`; o `*.py[cod]` e o `.next/` estão nos blocos `# Python` e `# Node`, como a decisão 1 manda); a conferência das regras reprovou o bloco `rules:` e a linha do `operations.archive` que faltava; a conferência do método avisou que o `openspec update` apagaria o `ff` e o `onboard`, que o perfil da máquina não tem. Dois falsos positivos no `scripts/check.sh`: o `bash trilha/verifica.sh`, que o Xavier chama dentro de uma função própria (`etapa "…" bash trilha/verifica.sh --vizinho …`), e o `echo` do bloco "Parte da stack", que o modelo manda trocar. A correção muda o requisito e volta ao usuário antes de seguir. O usuário escolheu a opção A ("faça o que sugere"): os blocos que abrem com "Parte da stack" e a chamada dentro de uma linha do projeto (tarefas 1.6 a 1.8).
- 6.2, segunda rodada: os dois falsos positivos sumiram, mas o aviso do `actions/setup-node` do CI também (falso negativo): a primeira versão tirava todo bloco com o comentário em qualquer linha. Corrigido para o bloco que abre com ele, com o cenário e o teste da tarefa 1.9.
- 6.2, terceira rodada, a que vale (2026-10-20), com o kit no commit da tarefa 1.9 e a suíte com 232 testes verde:
  - o `kit.py atualizar` na cópia do Xavier no `e2115a8`: o `.gitignore` com as seis linhas (`*.db`, `*.db-shm`, `*.db-wal`, `*.log`, `*.sqlite`, `.DS_Store`); o CI com o `actions/setup-node` e o `node-version: "22"`, que o Xavier tirou; nenhuma linha do `scripts/check.sh`; a conferência das regras reprovou o bloco `rules:` e a linha do `operations.archive`; a conferência do método avisou que o `openspec update` apagaria o `ff` e o `onboard`; saída 1, os arquivos copiados, sem commit;
  - a conferência do método da mesma cópia com o perfil antigo da máquina (`XDG_CONFIG_HOME` com a configuração de antes, só comandos): "apagaria: .agents/skills/openspec-explore/SKILL.md, …" e "e mais 37";
  - o `kit.py atualizar` numa cópia do Xavier de hoje, já alinhado (`cc4199c`): saída 0; só o aviso do `setup-node` do CI, divergência real que a atualização do Xavier à 2.7 decide;
  - o repositório do Xavier não mudou (`git status` limpo, o último commit `cc4199c`).
  Os resultados foram mostrados ao usuário na conversa, que acompanha a change.

## Respostas à revisão

(o verify e o `/code-review` preenchem: cada sugestão aplicada ou recusada, com o motivo)
