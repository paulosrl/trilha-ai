# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha-ai/ ferramentas/` e com o mesmo `format --check`.

## 1. Os testes

- [ ] 1.1 As formas novas nos testes, que falham antes do código: `trilha-ai.git` solto, `trilha-ai.v2`, `https://github.com/paulosrl/trilha-ai.wiki` e `https://github.com/paulosrl/trilha-ai.git.` no `test_andamento_reprova_o_vizinho_pelo_nome` ("Vizinho pelo nome", "Caminho que chega ao vizinho de fora"); `./trilha-ai` sem barra no `test_andamento_aceita_a_pasta_do_metodo` ("Pasta do método"); o teste novo `test_andamento_reprova_o_caminho_relativo_ate_outro_vizinho` ("Caminho relativo que começa em outro vizinho") (`python3 -m unittest discover -s testes -k test_andamento_`)

## 2. O código

- [ ] 2.1 O `conferir_andamento` por palavra e por parte (D1), com a pasta do método pelo lugar do script (D2) e a docstring do `confere_metodo.py`; os testes da tarefa 1.1, o `test_andamento_aceita_o_nome_dentro_de_outro`, o `test_andamento_reprova_o_caminho_para_fora`, o `test_andamento_ignora_o_vizinho_vazio` e o `test_verifica_repassa_o_vizinho` passam (`python3 -m unittest discover -s testes -k test_andamento_ -k vizinho`)
- [ ] 2.2 A versão 2.22 no comum e o `plugin.json` na 2.22.0 (D3); o teste da versão do plugin passa (`python3 -m unittest discover -s testes -k plugin`)

## 3. Integração

- [ ] 3.1 O conjunto dos testes, o ruff (`check` e `format --check`) e o `openspec validate --all --no-interactive` passam
- [ ] 3.2 A execução manual, por último: num projeto novo criado pelo `ferramentas/kit.py` no scratchpad, o `bash trilha-ai/verifica.sh --vizinho trilha-ai --vizinho heimdall` passa com o `ANDAMENTO.md` citando `./trilha-ai`, `trilha-ai/verifica.sh`, `hooks-pela-trilha-ai` e `heimdall.yaml`; reprova com `trilha-ai.git` solto e, à parte, com `heimdall/scripts/check.sh`; o resultado vai a "Verificação", no `design.md`

## Os cenários e os testes

| Capacidade | Requisito | Cenário | Teste |
| --- | --- | --- | --- |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Vizinho pelo nome | `test_andamento_reprova_o_vizinho_pelo_nome` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Caminho que chega ao vizinho de fora | `test_andamento_reprova_o_vizinho_pelo_nome` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Pasta do método | `test_andamento_aceita_a_pasta_do_metodo` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Caminho relativo que começa em outro vizinho | `test_andamento_reprova_o_caminho_relativo_ate_outro_vizinho` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Nome dentro de outro nome | `test_andamento_aceita_o_nome_dentro_de_outro` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Caminho para fora do projeto | `test_andamento_reprova_o_caminho_para_fora` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Vizinho vazio | `test_andamento_ignora_o_vizinho_vazio` |
