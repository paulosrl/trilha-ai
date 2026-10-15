# Proposal

## Why

A auditoria de 2026-10-15 achou conferências do kit que não dizem o que o método diz. A conferência da decomposição procura `## 1.` e `## Ciclo` em qualquer ponto do texto e não exige o `## 2.`, e a falha não aponta o esqueleto da skill `sdd:briefing` (achado F02, a parte do código). Depois do gate 2, nada avisa a parte da stack que ficou como o modelo a deixou, e o CI segue sem lint e sem testes (F04, o aviso). O limite das regras carregadas a cada sessão mede linhas, não tamanho, e o comum pode engordar em largura sem acusar (F09). O `kit.py novo` não lembra o perfil do OpenSpec com o verify, que o ciclo usa no passo 5 (F32). Os testes fixam frases que já saíram do comum e do `config.yaml`, conferindo a redação e não o sentido (F31). E o verify da change 01 sugeriu um teste para a lista de plugins que não responde no prazo.

## What Changes

- A conferência do método exige os títulos `## 1.`, `## 2.` e `## Ciclo` no começo da linha da decomposição; a falha nomeia o título que falta e remete ao esqueleto da skill `sdd:briefing`.
- Com um `sdd/tdd-*.md`, a conferência das regras avisa, sem falhar, cada lugar da stack que ainda está como o modelo o deixou: `scripts/check.sh`, `.github/workflows/verificacao.yml`, `.github/dependabot.yml`, `.gitignore` e a linha "Stack" do `openspec/config.yaml`.
- O `CLAUDE.md` e o `trilha/CLAUDE-comum.md` somados passam a ter, além das 200 linhas, no máximo 32 KB (32.768 bytes); a conferência das regras reprova acima disso, e o comum diz o teto. No kit, um teste segura o comum sozinho em 16 KB, metade do teto, e o `CLAUDE.md` do kit diz isso.
- O `kit.py novo` põe o `openspec config profile` com o verify nos próximos passos e avisa quando o perfil do OpenSpec da máquina não o traz.
- O prazo da lista de plugins do Claude Code vira uma constante, e um teste prova o silêncio quando ela não responde nele.
- Saem dos testes as checagens de frases aposentadas; ficam as que guardam uma regra viva.
- O kit vai à versão 2.1 (o comum "Versão 2.1", o plugin 2.1.0); o `context` do `openspec/config.yaml` do kit passa a citar `modelo/trilha/` como a pasta do ruff.

**Fora desta change:** o plugin declarado no `.claude/settings.json` do projeto e os padrões técnicos da skill `tdd` (change 04); a revisão de texto do comum (item 8 do plano); o README e o mapa (item 9); a migração dos projetos reais (item 10).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `conferencias`: ganha a decomposição conferida pelo esqueleto da skill, o aviso da stack por preencher depois do TDD e o teto de tamanho das regras; o silêncio sem o Claude Code passa a cobrir a lista que não responde no prazo.
- `ferramenta-do-kit`: o projeto novo ganha o passo e o aviso do perfil do OpenSpec com o verify.

## Impact

- Kit: `modelo/trilha/confere_metodo.py`, `modelo/trilha/confere_regras.py`, `modelo/trilha/CLAUDE-comum.md` (o teto e a versão), `ferramentas/kit.py`, `testes/test_kit.py`, `plugins/sdd/.claude-plugin/plugin.json` (só a versão), o `CLAUDE.md` e o `openspec/config.yaml` do kit.
- Projetos: na próxima atualização, recebem a conferência nova. As decomposições dos projetos reais já têm os três títulos no começo da linha; o maior deles somaria 29,2 KB com o comum atual, abaixo do teto. Quem tem TDD e a stack por preencher passa a ver o aviso.
