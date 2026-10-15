# Proposal

## Why

A auditoria de 2026-10-15 achou o CodeGraph tratado como obrigatório em parte do kit e ausente das ferramentas do método no comum (achado F36). A escolha foi declará-lo opcional: o índice do código ajuda o Claude, mas o método funciona sem ele, e indexar um repositório é decisão do usuário. O README e o mapa já dizem isso desde o commit `60bb345`. Os próximos passos do `kit.py novo` ainda mandam rodar o `codegraph init` junto do `openspec init`, como passo obrigatório.

## What Changes

- Nos próximos passos do `kit.py novo`, o `codegraph init` passa a vir como opcional ("se usar o CodeGraph"), num item próprio, separado do `openspec init`, e diz que roda em cada clone, porque o índice fica fora do git.
- Os próximos passos passam a ter os números do README (3 a 6), e o passo 4, "inicialize as ferramentas", agrupa o OpenSpec, o plugin e o CodeGraph, um item cada, como no passo 4 do README.
- Um teste confere a saída.

**Fora desta change:** o resto da saída do `novo` (os outros passos, o aviso do perfil do OpenSpec); o `kit.py atualizar`; as conferências; o texto do método (comum, skills, `config.yaml` modelo). O kit não sobe de versão, porque nada em `modelo/` nem em `plugins/` muda.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `ferramenta-do-kit`: os próximos passos do projeto novo citam o CodeGraph como opcional.

## Impact

- Kit: `ferramentas/kit.py` (a função `novo`, só o texto dos próximos passos) e `testes/test_kit.py`.
- Projetos: nenhum efeito; a saída do `novo` só aparece na criação de um projeto.
