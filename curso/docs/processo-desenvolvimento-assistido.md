# Processo de desenvolvimento assistido: <nome do produto>

Registro de cada etapa feita com um assistente de IA neste repositório, como manda o `CLAUDE-curso.md` ("Documentar cada etapa, no mesmo turno"): o prompt literal do usuário, sem corrigir a digitação, o que foi feito, o que saiu (arquivos e commits), as decisões humanas e os incidentes. Nada reconstruído é apresentado como literal.

## 1. Linha do tempo

| Data | O que aconteceu | Commit |
|---|---|---|
| <AAAA-MM-DD> | Repositório criado a partir do kit de partida (seção 3.1) | este commit |

## 2. Onde estamos agora

- **Em andamento:** nada. (O `ANDAMENTO.md` da raiz diz o estado exato.)
- **Próxima etapa:** o PRD, com a skill `sdd:prd` (etapa 1 do guia).
- **Próxima seção deste registro:** 3.2.
- **Commits por enviar ao remoto:** <conferir com `git status -sb`>.

## 3. Etapas

### 3.1 Repositório criado a partir do kit de partida (<AAAA-MM-DD>)

**Prompt:**

```text
<o pedido do usuário, como foi digitado>
```

**O que foi feito:** o repositório nasceu com `git init`; os arquivos do kit copiados para a raiz, como manda o LEIA-ME dele (inclusive este registro e o resumo); `openspec init` e `codegraph init` rodados; o `CLAUDE.md` e o `config.yaml` preenchidos no que já se sabe antes do PRD.

**Conferências:** `scripts/check.sh` verde (só a parte das regras, até a etapa 2).

**Decisões:** nenhuma. **Incidentes:** nenhum.
