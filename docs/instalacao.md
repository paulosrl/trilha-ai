# Instalação

Três formas de usar o pipeline, da mais simples à mais manual. O conteúdo é o mesmo em todas; muda apenas como ele chega até você.

## 1. Como plugin no Claude Code (recomendado)

No terminal, ou dentro de uma sessão do Claude Code (prefixe com `/` em vez de `claude`):

```bash
claude plugin marketplace add paulosrl/pipeline-prd-tdd-openspec
claude plugin install sdd@pipeline-prd-tdd-openspec
```

Verifique:

```bash
claude plugin list        # deve listar sdd@pipeline-prd-tdd-openspec, enabled
```

As skills ficam disponíveis com o prefixo do plugin:

| Comando | Estágio |
|---|---|
| `/sdd:prd` | 1 — PRD de produto, agnóstico de tecnologia |
| `/sdd:tdd` | 2 — Decisão técnica por entrevista, com ADRs |
| `/sdd:briefing` | 3 — Decomposição, briefing e auditoria para o OpenSpec |

Você também pode apenas descrever a tarefa ("preciso de um PRD para...") — o Claude aciona a skill certa pela descrição.

Atualizações: `claude plugin marketplace update pipeline-prd-tdd-openspec`.

## 2. Como skills avulsas (sem plugin)

Copie as pastas de skills para o diretório pessoal de skills:

```bash
git clone https://github.com/paulosrl/pipeline-prd-tdd-openspec.git
cp -r pipeline-prd-tdd-openspec/plugins/sdd/skills/* ~/.claude/skills/
```

As skills ficam disponíveis sem prefixo: `/prd`, `/tdd`, `/briefing`. Em caso de conflito com skills suas de mesmo nome, a precedência do Claude Code é: empresarial > pessoal > projeto.

Para disponibilizar a um time em um repositório específico, copie para `.claude/skills/` na raiz do repo e faça commit.

## 3. No claude.ai (web, desktop, Cowork)

Habilite cada skill na sua conta claude.ai (upload do diretório da skill nas configurações de skills). Elas sincronizam para sessões Cowork, sessões cloud e para o terminal logado na mesma conta.

## 4. Em outras plataformas de IA (ChatGPT, Gemini etc.)

Use os prompts portáteis da pasta [`prompts/`](../prompts/): cole o prompt do estágio no início da conversa e siga os gates de aprovação normalmente. Nenhuma instalação é necessária.

## Pré-requisito do Estágio 3

O estágio 3 (`briefing`) prepara e audita, mas quem gera os artefatos é o **OpenSpec** dentro do repositório do seu projeto, com um assistente de código (Claude Code, Cursor etc.):

```bash
npm install -g openspec   # ou o método de instalação vigente do OpenSpec
openspec init             # na raiz do repositório do projeto
```

Consulte a documentação do OpenSpec para a instalação atualizada.

## Personalização

Os defaults institucionais da skill `tdd` (PostgreSQL/pgvector, `uv`, `pnpm`, ruff, Biome, Docker Compose v2) refletem os padrões do autor. Para adotar os da sua organização, edite a seção "Defaults institucionais" em `plugins/sdd/skills/tdd/SKILL.md` — é a personalização esperada, não um desvio.
