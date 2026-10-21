# Proposal

## Why

Pedido do usuário, de 2026-10-20 ("faça tudo que vc sugere"), depois da conferência do Xavier contra o kit 2.6. A conferência achou quatro divergências do modelo, e nenhuma ferramenta do kit as acusou:

1. As regras por artefato do `openspec/config.yaml` eram próprias do Xavier. O `kit.py atualizar` só imprimiu "compare à mão", e nenhum verificador compara as regras com as do kit, então a verificação do projeto seguiu verde.
2. O `.gitignore` não tinha `*.log`, `.DS_Store`, `*.db` nem `*.sqlite`. O aviso da parte fixa só olha as linhas que o kit mudou desde a versão do projeto, e o Xavier nunca tinha copiado essas linhas. Com o código do kit, o aviso sai vazio, e faltam oito linhas.
3. O perfil do OpenSpec da máquina estava só com comandos. Com ele, o `openspec update` apagaria as skills das cinco ferramentas do projeto. O `kit.py` só confere se o `verify` está no perfil.
4. A versão do OpenSpec da máquina nunca é comparada com a fixada no CI do projeto.

## What Changes

- O aviso da parte fixa do `kit.py atualizar` passa a citar toda linha do modelo atual que falta no projeto, e não só as acrescentadas desde a versão dele. Os blocos da parte da stack ficam de fora, porque o projeto troca ou apaga de propósito o que não é seu: os marcados "Parte da stack", em qualquer arquivo, e os de Python e Node do `.gitignore`. A linha do kit chamada dentro de uma linha do projeto (por uma função dele) conta como presente. O aviso das linhas que o kit tirou continua igual.
- Com `--fonte`, a conferência das regras reprova o projeto cujo bloco `rules:` do `openspec/config.yaml` difere do modelo do kit na versão do projeto. Também reprova quando falta, no `operations` do projeto, uma linha do `operations` do kit. Linhas próprias a mais no `operations` e chaves próprias no topo (o `githubCopilot`) passam.
- A conferência do método avisa, sem falhar, quando o `openspec update` mudaria os arquivos gerados do OpenSpec que o projeto versiona. O teste é o ensaio do próprio OpenSpec numa pasta temporária. O aviso nomeia os arquivos que ele apagaria, criaria ou trocaria.
- A mesma conferência avisa, sem falhar, quando a versão do OpenSpec da máquina difere da fixada no CI do projeto.
- A versão passa a 2.7 e o plugin `sdd` a 2.7.0.

**Fora desta change:**
- a versão do `gh`, do Claude Code e de outras ferramentas que o kit não fixa;
- o roteiro `ferramentas/validar-projeto.md`, que é texto do kit e muda fora de change, no mesmo ciclo;
- a atualização dos projetos (Xavier, Heimdall, HubIA), cada um depois, sob ordem do usuário;
- qualquer mudança no comum além da linha de versão.

## Capabilities

### New Capabilities

- `conferencia-do-openspec`: o que a conferência do método confere no OpenSpec da máquina: os arquivos gerados que o `openspec update` mudaria e a versão instalada diante da fixada no CI.

### Modified Capabilities

- `ferramenta-do-kit`: o "Aviso da parte fixa que mudou no kit" passa a valer para toda linha do modelo atual que falta no projeto, fora dos blocos da parte da stack, e aceita a linha do kit chamada dentro de uma linha do projeto.
- `conferencias`: um requisito novo, as regras por artefato do `openspec/config.yaml` iguais às do kit na versão do projeto.

## Impact

- `ferramentas/kit.py`: `_avisar_parte_fixa`, o `_presente` e uma função nova que separa os blocos da parte da stack.
- `modelo/trilha/confere_regras.py`: a comparação do `config.yaml` com o modelo, ao lado da comparação da pasta `trilha/`.
- `modelo/trilha/confere_metodo.py`: os avisos do OpenSpec, atrás do `--sem-plugin`, que a trava do commit já usa.
- `testes/test_kit.py`: os testes de cada cenário, sem rede e sem o OpenSpec instalado.
- `modelo/trilha/CLAUDE-comum.md` (só a linha de versão), `plugins/sdd/.claude-plugin/plugin.json` e o `README.md` do kit (o passo 4, o perfil com skills e comandos).
- Os projetos só passam a ter as conferências novas quando receberem a cópia da 2.7.
