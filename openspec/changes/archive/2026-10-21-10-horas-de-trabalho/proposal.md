# Proposal

## Why

Pedido do usuário, de 2026-10-20, ao ver uma página avulsa com as horas de trabalho do Xavier. A estimativa pelos commits errou para os dois lados: num dia com 2 commits, deu 30 minutos para 3h21 de atividade registrada; noutro, com 25 commits espalhados, deu 7h02 para 3h33. As conversas do Claude Code têm a hora exata de cada interação, mas cobriam só 13 dos 57 dias, porque o Claude Code as apaga depois de 30 dias (`cleanupPeriodDays`). O usuário recusou um gancho a cada interação, por custo, e pediu algo ágil, com menos detalhe e as mesmas respostas: quando trabalhou, quantas horas por dia e por dia da semana, e quanto foi dele e quanto foi da IA sozinha. A descrição curta foi aprovada pela delegação "prossiga como vc recomenda", que também aprovou o envio da branch.

## What Changes

- Um comando novo, `trilha/tempo.py`, rodado sob demanda (`python3 trilha/tempo.py`); nada roda a cada interação, e nenhum gancho é criado.
- Ele lê o que já existe na máquina: as conversas do Claude Code feitas dentro do repositório e o histórico de commits.
- Apura as horas de cada dia: o tempo seu (o que antecede cada pedido seu, em intervalos de até 30 minutos), o tempo da IA sozinha e o total; o dia sem conversa guardada é estimado pelos commits, pelo método de sessões, e cada dia diz a fonte usada.
- Guarda fora do repositório, na pasta de dados do usuário, um resumo só com datas e horas, completado a cada execução, para que as horas apuradas sobrevivam ao apagamento das conversas. Nenhum texto das conversas é guardado.
- Gera a página das horas (a linha do tempo semana a semana, as horas por dia da semana, a fonte e o método) também fora do repositório, sem nada carregado da rede, e diz onde a gravou.
- Avisa quando a guarda das conversas na máquina é curta, com a linha de configuração que resolve.
- A versão passa a 2.8 e o plugin `sdd` a 2.8.0.

**Fora desta change:**
- gancho e registro a cada interação, e o par ligar e desligar;
- envio de dados para fora da máquina;
- seção de horas na documentação versionada do projeto (`sdd/documentacao.html`);
- a configuração da guarda das conversas na máquina do usuário (o `README.md` do kit ganha a linha no passo 1, como texto do kit);
- os dados da página avulsa feita para o Xavier;
- a cópia da 2.8 nos projetos, cada um depois, sob ordem do usuário;
- qualquer mudança no comum além da linha de versão.

## Capabilities

### New Capabilities

- `horas-de-trabalho`: o que o `trilha/tempo.py` lê, como apura as horas de cada dia, o resumo que guarda, a página que gera e o aviso da guarda curta.

### Modified Capabilities

(nenhuma: o `kit.py` já copia toda a `modelo/trilha/`, e a conferência da pasta `trilha/` já cobre o arquivo novo)

## Impact

- `modelo/trilha/tempo.py` (novo) e `modelo/trilha/pagina_tempo_modelo.html` (novo, o visual da página).
- `testes/test_kit.py`: os testes de cada cenário, com conversas e repositórios de exemplo criados no teste, sem rede.
- `modelo/trilha/CLAUDE-comum.md` (só a linha de versão), `plugins/sdd/.claude-plugin/plugin.json` e o `README.md` do kit (a linha da guarda no passo 1 e o `tempo.py` na tabela do passo 3).
- Os projetos só passam a ter o comando quando receberem a cópia da 2.8; até lá, a conferência da pasta `trilha/` com `--fonte` não muda para eles.
