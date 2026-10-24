# Proposal

## Why

Pedido do usuário, de 2026-10-24, ao ver o aviso do `openspec validate --strict` no spec `horas-de-trabalho`: três requisitos têm a descrição acima de 500 caracteres ("Conversas do repositório", "Estimativa pelos commits nos dias sem conversa" e "Repositório que mudou de pasta"). O OpenSpec pede uma regra por requisito, e só divide um requisito existente numa change feita para isso.

A descrição curta foi aprovada pelo usuário.

## What Changes

- Os três requisitos ficam com uma regra só cada um, no MODIFIED, com o nome e todos os cenários de antes.
- As regras que saem viram requisitos novos, cada um com o seu cenário:
  - de "Conversas do repositório": a subpasta que não se confere;
  - de "Estimativa pelos commits nos dias sem conversa": quais são os commits do usuário;
  - de "Repositório que mudou de pasta": o resumo antigo que não se lê, a raiz antiga que não se confere e a raiz antiga que ainda é um repositório.
- O comportamento não muda, nem o código.

**Fora desta change:**
- os outros specs e os requisitos do `horas-de-trabalho` abaixo de 500 caracteres;
- a versão do método: o spec é do kit, não de `modelo/`.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `horas-de-trabalho`: três requisitos divididos, uma regra por requisito, sem mudar o comportamento.

## Impact

- `openspec/specs/horas-de-trabalho/spec.md`, no archive.
- Nenhum código e nenhum teste: os cenários novos são comprovados por testes que já existem em `testes/test_kit.py`.
