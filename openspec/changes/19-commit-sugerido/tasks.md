# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Cada teste novo é escrito antes do código; o que já passa antes protege o comportamento de hoje.

## 1. Os testes

- [x] 1.1 Os testes do commit sugerido, os dois primeiros com o `update` falso mudando uma skill do projeto: `test_atualizar_openspec_commit_so_do_openspec` ("Só o OpenSpec muda", que passa antes do código e protege o achado R9 da change 16), `test_atualizar_openspec_commit_da_copia_e_do_openspec` ("A cópia e o OpenSpec mudam") e `test_atualizar_openspec_commit_so_da_copia` ("Só a cópia muda, com o --openspec"), que falham antes; e `test_atualizar_commit_sem_openspec` ("Sem o --openspec"), que passa antes e protege a mensagem sem a opção (`python3 -m unittest discover -s testes -k test_atualizar_openspec_commit -k test_atualizar_commit`)

## 2. O código

- [x] 2.1 No `kit.py`, o `_preparar_o_openspec` devolve se o dry-run previu mudanças no projeto, o `atualizar` lê o `git status` antes do update e monta a mensagem (D1 a D3), e a regra do `check.sh` vira uma função usada pelo `_check_migra` e pelo `_migrar_check` (D4); os testes da 1.1, os do `atualizar` e os da migração passam (`python3 -m unittest discover -s testes -k test_atualizar -k test_aceitar_apagados -k test_migra`)

## 3. Integração

- [x] 3.1 O conjunto dos testes, o ruff e o `openspec validate --all --no-interactive` passam
- [ ] 3.2 A execução manual, por último, com o OpenSpec 1.15.0 de verdade, só num projeto descartável no scratchpad, com o `XDG_CONFIG_HOME` e o `HOME` no scratchpad: com a `trilha/` editada e uma skill gerada alterada, o `kit.py atualizar --openspec` sugere a mensagem com as duas partes; o resultado vai a "Verificação", no `design.md`

## Workflow follow-up

- A revisão dos artefatos, o `/opsx:verify` e o code review, por um agente sem o contexto da sessão; as respostas vão a "Respostas à revisão", no `design.md`.
- O `/opsx:archive`, os passos do `operations.archive`, o envio e o merge, com o "sim" do usuário.
