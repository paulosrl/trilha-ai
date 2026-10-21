# Design

## Context

Ver `proposal.md` (Why). Na 2.10, o `_ainda_repositorio` do `trilha/tempo.py` devolve `(Path(caminho) / ".git").exists()`. No Python até o 3.13, o `exists()` só engole os erros de "não existe" (`ENOENT`, `ENOTDIR` e afins) e deixa passar o `PermissionError`; no 3.14, ele devolve `False` em qualquer `OSError`. O comando roda no Python 3 que a máquina tiver.

## Goals / Non-Goals

**Goals:**
- Na dúvida sobre a raiz antiga, nenhuma cópia viva é juntada, e o comando não falha.

**Non-Goals:**
- Os outros achados da revisão, no proposal.

## Decisions

### D1. A conferência do `.git`
Uma função só, `_tem_git(pasta)`, confere o `.git` com o `stat` direto, sem o `exists()`: o `FileNotFoundError` e o `NotADirectoryError` dizem que ele não está lá (`False`); qualquer outro `OSError` (sem permissão, um disco que não responde) e o `ValueError` (um caminho com caractere nulo, ou que não se codifica) dizem que não se confere (`None`). O resultado é o mesmo em todo Python 3. Ela serve aos dois lugares que conferiam o `.git` com o `exists()`:
- **a raiz antiga de um resumo de mesmo nome:** `True` é outra cópia (o aviso de hoje, só sem resumo deste caminho); `False` junta; `None` não junta nem renomeia, e avisa em toda execução que não deu para conferir, citando o resumo: é a única pista das horas presas lá;
- **as pastas entre o `cwd` de uma conversa e a raiz:** `None` conta como sem `.git`, e a pasta conta para a raiz, como a que já não existe.

*Alternativa:* `try: exists() except OSError: True`. Recusada: no Python 3.14 o `exists()` não levanta nada, e a cópia viva seria juntada.

### D2. O aviso do resumo antigo que não se lê
O texto passa a terminar com "corrija-o ou mova-o, e rode de novo", como o do resumo principal ilegível. O aviso continua a cada execução enquanto o arquivo estiver lá: é a única pista de que há horas presas nele.

### D3. A versão
"Versão 2.11, de 2026-10-21." no comum e `2.11.0` no plugin, antes de qualquer outro arquivo de `modelo/` mudar.

## Risks / Trade-offs

- [Os testes de permissão não valem como root, que abre qualquer pasta, nem sem o `os.geteuid` (Windows)] → Eles se pulam nesses casos; o GitHub roda os testes como um usuário comum.
- [Um disco que falha por outro motivo segura o resumo antigo] → O aviso o cita em toda execução, e o arquivo continua lá para ser juntado quando o disco voltar.

## Verificação

**Execução manual (tarefa 4.2), em 2026-10-21,** no Python 3.12.3, num repositório de teste vazio, com uma pasta de dados à parte que tinha o resumo de uma raiz antiga dentro de uma pasta sem permissão (modo 000):
- a 2.10, da `main`, terminou com o rastro de `PermissionError: [Errno 13] Permission denied: '.../fechada/proj/.git'`, sem gravar o resumo nem a página;
- a 2.11 terminou com o código 0, com o aviso da outra cópia (era a primeira execução neste caminho), gravou o resumo e a página deste caminho, e o resumo antigo ficou com o nome de antes.

## Respostas à revisão

O `/opsx:verify` e o `/code-review 13`, cada um por um agente sem o contexto da sessão, em 2026-10-21. O verify não achou nada crítico nem aviso; as duas sugestões dele são os pontos 5 e 6 do review. Todos aplicados, com a escolha do usuário:

| # | Origem | Achado | Decisão |
|---|---|---|---|
| 1 | review 1 | O `stat()` levanta `ValueError` num caminho com caractere nulo, e o comando parava. | Aplicado: o `ValueError` conta como "não se confere" (D1). Cenário "Raiz antiga com caminho inválido". |
| 2 | review 2 | O `_eh_da_raiz` ainda conferia o `.git` com o `exists()`, que para no erro de permissão até o Python 3.13. | Aplicado: os dois lugares usam o `_tem_git` (D1). Cenário "Subpasta sem permissão". |
| 3 | review 3 | Sem permissão, o aviso era o da outra cópia, e só na primeira execução; depois, as horas ficavam presas em silêncio. | Aplicado: um aviso próprio, em toda execução (D1). |
| 4 | review 4 | O `os.geteuid` não existe no Windows, e o `skipIf` quebraria o carregamento do arquivo de testes. | Aplicado: os testes de permissão se pulam sem ele. |
| 5 | review 5, verify 1 | O teste novo não conferia o aviso. | Aplicado: ele confere o aviso nas duas execuções. |
| 6 | review 6, verify 2 | Um `return True` repetido. | Aplicado: a função nova não o tem. |

**Execução manual depois das respostas, em 2026-10-21,** na mesma montagem da tarefa 4.2, já com o resumo deste caminho gravado: duas execuções seguidas terminaram com o código 0, cada uma com o aviso "não deu para conferir se .../fechada/proj ainda é um repositório", e o resumo antigo ficou com o nome de antes.
