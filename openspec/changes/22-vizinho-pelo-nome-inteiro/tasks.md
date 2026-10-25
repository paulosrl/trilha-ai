# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha-ai/ ferramentas/` e com o mesmo `format --check`.

## 1. Os testes

- [ ] 1.1 Os testes novos, que falham antes do código onde o comportamento muda: `test_andamento_reprova_o_vizinho_pelo_nome` ("Vizinho pelo nome"), `test_andamento_aceita_a_pasta_do_metodo` ("Pasta do método"), `test_andamento_aceita_o_nome_dentro_de_outro` ("Nome dentro de outro nome") e `test_andamento_reprova_o_caminho_para_fora` ("Caminho para fora do projeto") (`python3 -m unittest discover -s testes -k test_andamento_`)

## 2. O código

- [ ] 2.1 O `conferir_andamento` pelo nome inteiro (D1), com a docstring do `confere_metodo.py`; a versão 2.21 no comum e o `plugin.json` na 2.21.0 (D2); os testes da tarefa 1.1, o `test_verifica_repassa_o_vizinho` e o teste da versão do plugin passam (`python3 -m unittest discover -s testes -k test_andamento_ -k vizinho -k plugin`)

## 3. Integração

- [ ] 3.1 O conjunto dos testes, o ruff (`check` e `format --check`) e o `openspec validate --all --no-interactive` passam
- [ ] 3.2 A execução manual, por último: a conferência do método do kit desta change rodada num clone descartável do Heimdall, com o `ANDAMENTO.md` citando `hooks-pela-trilha-ai` e `trilha-ai/verifica.sh`, passa; com "o kit trilha-ai" solto, reprova; o resultado vai a "Verificação", no `design.md`

## Os cenários e os testes

| Capacidade | Requisito | Cenário | Teste |
| --- | --- | --- | --- |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Vizinho pelo nome | `test_andamento_reprova_o_vizinho_pelo_nome` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Pasta do método | `test_andamento_aceita_a_pasta_do_metodo` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Nome dentro de outro nome | `test_andamento_aceita_o_nome_dentro_de_outro` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Caminho para fora do projeto | `test_andamento_reprova_o_caminho_para_fora` |
