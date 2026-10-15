# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`; o ruff, com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check`. O teste novo é escrito antes do código e falha antes dele.

## 1. O CodeGraph opcional no projeto novo

- [ ] 1.1 O teste `test_novo_cita_o_codegraph_como_opcional`, em `testes/test_kit.py`, roda o `kit.py novo` numa pasta descartável e confere, nos próximos passos, que a linha do `codegraph init` diz "se usar o CodeGraph" e que o passo do `openspec init` não cita o `codegraph init`; ele falha antes do código (`python3 -m unittest discover -s testes -k test_novo_cita_o_codegraph_como_opcional`)
- [ ] 1.2 Os próximos passos do `kit.py novo` passam a trazer o `codegraph init` num passo próprio, opcional; o teste da 1.1 passa e comprova o cenário "Projeto novo com o CodeGraph opcional" (`-k test_novo_cita_o_codegraph_como_opcional`), e o `test_novo_com_o_verify_no_perfil_nao_avisa` e o `test_novo_imprime_o_comando_de_instalacao` continuam passando
- [ ] 1.3 O conjunto de testes, o ruff (check e format), cada um sozinho, e o `openspec validate --all --no-interactive`, sem erro

## 2. Execução manual

- [ ] 2.1 Com o usuário olhando: `python3 ferramentas/kit.py novo` numa pasta descartável do scratchpad, com a saída dos próximos passos lida inteira; depois, a pasta apagada

## Workflow follow-up

- Depois do archive: `openspec validate --all --no-interactive`, os testes e o ruff do kit. Sem versão nova: nada em `modelo/` nem em `plugins/` muda.
