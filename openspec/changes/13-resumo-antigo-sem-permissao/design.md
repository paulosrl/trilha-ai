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
O `_ainda_repositorio` faz o `stat` do `.git` direto, sem o `exists()`: o `FileNotFoundError` e o `NotADirectoryError` dizem que o repositório não está lá (`False`); qualquer outro `OSError` (sem permissão, um disco que não responde) conta como repositório (`True`). O resultado é o mesmo em todo Python 3, e o erro leva ao caminho que não mexe em nada: o resumo de lá fica onde está, e o aviso da outra cópia sai como hoje, só quando não há resumo deste caminho.

*Alternativa:* `try: exists() except OSError: True`. Recusada: no Python 3.14 o `exists()` não levanta nada, e a cópia viva seria juntada.

### D2. O aviso do resumo antigo que não se lê
O texto passa a terminar com "corrija-o ou mova-o, e rode de novo", como o do resumo principal ilegível. O aviso continua a cada execução enquanto o arquivo estiver lá: é a única pista de que há horas presas nele.

### D3. A versão
"Versão 2.11, de 2026-10-21." no comum e `2.11.0` no plugin, antes de qualquer outro arquivo de `modelo/` mudar.

## Risks / Trade-offs

- [O teste de permissão não vale como root, que abre qualquer pasta] → Ele se pula quando o `os.geteuid()` é 0; o GitHub roda os testes como um usuário comum.
- [Um disco que falha por outro motivo segura o resumo antigo para sempre] → O aviso da outra cópia o cita na primeira execução, e o arquivo continua lá para ser juntado quando o disco voltar.

## Verificação

**Execução manual (tarefa 4.2), em 2026-10-21,** no Python 3.12.3, num repositório de teste vazio, com uma pasta de dados à parte que tinha o resumo de uma raiz antiga dentro de uma pasta sem permissão (modo 000):
- a 2.10, da `main`, terminou com o rastro de `PermissionError: [Errno 13] Permission denied: '.../fechada/proj/.git'`, sem gravar o resumo nem a página;
- a 2.11 terminou com o código 0, com o aviso da outra cópia (era a primeira execução neste caminho), gravou o resumo e a página deste caminho, e o resumo antigo ficou com o nome de antes.
