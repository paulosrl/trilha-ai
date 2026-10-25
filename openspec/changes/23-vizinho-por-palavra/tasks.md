# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha-ai/ ferramentas/` e com o mesmo `format --check`.

## 1. Os testes

- [x] 1.1 As formas novas nos testes, que falham antes do código: `trilha-ai.git` solto, `trilha-ai.v2`, `https://github.com/paulosrl/trilha-ai.wiki` e `https://github.com/paulosrl/trilha-ai.git.` no `test_andamento_reprova_o_vizinho_pelo_nome` ("Vizinho pelo nome", "Caminho que chega ao vizinho de fora"); `./trilha-ai` sem barra no `test_andamento_aceita_a_pasta_do_metodo` ("Pasta do método"); o teste novo `test_andamento_reprova_o_caminho_relativo_ate_outro_vizinho` ("Caminho relativo que começa em outro vizinho") (`python3 -m unittest discover -s testes -k test_andamento_`)

## 2. O código

- [x] 2.1 O `conferir_andamento` por palavra e por parte (D1), com a pasta do método pelo lugar do script (D2) e a docstring do `confere_metodo.py`; os testes da tarefa 1.1, o `test_andamento_aceita_o_nome_dentro_de_outro`, o `test_andamento_reprova_o_caminho_para_fora`, o `test_andamento_ignora_o_vizinho_vazio` e o `test_verifica_repassa_o_vizinho` passam (`python3 -m unittest discover -s testes -k test_andamento_ -k vizinho`)
- [x] 2.2 A versão 2.22 no comum e o `plugin.json` na 2.22.0 (D3); o teste da versão do plugin passa (`python3 -m unittest discover -s testes -k plugin`)

## 3. Integração

- [x] 3.1 O conjunto dos testes, o ruff (`check` e `format --check`) e o `openspec validate --all --no-interactive` passam
- [x] 3.2 A execução manual, por último: num projeto novo criado pelo `ferramentas/kit.py` no scratchpad, o `bash trilha-ai/verifica.sh --vizinho trilha-ai --vizinho heimdall` passa com o `ANDAMENTO.md` citando `./trilha-ai`, `trilha-ai/verifica.sh`, `hooks-pela-trilha-ai` e `heimdall.yaml`; reprova com `trilha-ai.git` solto e, à parte, com `heimdall/scripts/check.sh`; o resultado vai a "Verificação", no `design.md`

## 4. Respostas à revisão

- [x] 4.1 Os testes das formas da revisão, que falham antes do código: `test_andamento_reprova_o_nome_colado_a_um_sinal` ("Nome colado a um sinal"), `test_andamento_reprova_o_host_da_url` ("Host de uma URL") e `test_metodo_recusa_o_vizinho_com_separador` ("Vizinho com barra") (`python3 -m unittest discover -s testes -k test_andamento_ -k recusa_o_vizinho`)
- [x] 4.2 As partes no que não cabe num nome, sem o `_` das pontas, com o host da URL e a pasta só seguida de `/` (D1, D2), e a recusa do vizinho com separador (D4); os testes da tarefa 4.1 e os da tarefa 2.1 passam (`python3 -m unittest discover -s testes -k test_andamento_ -k vizinho`)
- [x] 4.3 O conjunto dos testes, o ruff (`check` e `format --check`) e o `openspec validate --all --no-interactive` passam, e a execução manual da tarefa 3.2 refeita com o código final, mais `trilha-ai#24` (reprova) e `--vizinho paulosrl/trilha-ai` (código 2); o resultado vai a "Verificação", no `design.md`

## Os cenários e os testes

| Capacidade | Requisito | Cenário | Teste |
| --- | --- | --- | --- |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Vizinho pelo nome | `test_andamento_reprova_o_vizinho_pelo_nome` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Caminho que chega ao vizinho de fora | `test_andamento_reprova_o_vizinho_pelo_nome` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Pasta do método | `test_andamento_aceita_a_pasta_do_metodo` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Nome colado a um sinal | `test_andamento_reprova_o_nome_colado_a_um_sinal` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Host de uma URL | `test_andamento_reprova_o_host_da_url` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Caminho relativo que começa em outro vizinho | `test_andamento_reprova_o_caminho_relativo_ate_outro_vizinho` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Nome dentro de outro nome | `test_andamento_aceita_o_nome_dentro_de_outro` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Caminho para fora do projeto | `test_andamento_reprova_o_caminho_para_fora` |
| conferencias | Vizinho citado pelo nome inteiro no ANDAMENTO | Vizinho vazio | `test_andamento_ignora_o_vizinho_vazio` |
| conferencias | Vizinho só com o nome de um repositório | Vizinho com barra | `test_metodo_recusa_o_vizinho_com_separador` |
