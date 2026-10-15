# Proposal

## Why

O método tem duas fontes com versões independentes: o kit (`trilha-ai`, versão 1.34 no comum) e o plugin `sdd` (`pipeline-prd-tdd-openspec`, versão 0.3.9). As skills citam regras do comum pelo texto, sem nenhuma compatibilidade declarada, e a conferência do plugin depende de o repositório do plugin estar na pasta vizinha e de um arquivo interno do Claude Code. A auditoria do método registrou isso como decisão D1 (um repositório e uma versão para todo o método) e como os achados F18 (o que se copia muda sem versão nova), F19 (conferências presas ao layout de pastas do autor e a um arquivo interno), F15 (documentação do plugin instala o pacote errado do OpenSpec), F16 (caminhos anunciados que não existem: `prompts/`, `exemplo/`), F17 (instalação avulsa que quebra os nomes `sdd:*` que o kit cita) e F24 (diagrama do pipeline sem a skill `briefing` e com um ciclo que diverge do comum). É a base dos demais itens do plano: as correções no texto das skills precisam do lugar definitivo delas.

## What Changes

- O kit passa a publicar o plugin `sdd`: o repositório do plugin entra no kit por merge de históricos não relacionados, preservando os commits, e os arquivos ficam nos mesmos caminhos (`.claude-plugin/marketplace.json` e `plugins/sdd/`). As três skills vêm sem mudança de texto.
- **BREAKING** O marketplace passa a se chamar `trilha-ai`: a instalação passa a ser `claude plugin marketplace add paulosrl/trilha-ai` e `claude plugin install sdd@trilha-ai`. Quem tem `sdd@pipeline-prd-tdd-openspec` instalado migra uma vez.
- A versão do plugin passa a ser a do kit (`X.Y.0` para a "Versão X.Y" do comum), conferida por teste; toda mudança em `modelo/` ou em `plugins/` sobe a versão. Esta change leva o kit à 1.35.
- O `confere_metodo.py` deixa de procurar `../pipeline-prd-tdd-openspec` e de ler `~/.claude/plugins/installed_plugins.json`: lê o plugin instalado por `claude plugin list --json` e avisa quando ele é de fora do kit (o marketplace antigo ou outro), quando está desligado ou quando a versão difere da do comum do projeto. Sem o Claude Code instalado (o CI), não avisa nada. Continua só aviso, e a trava do commit não o consulta: ele aparece no `check.sh`.
- A documentação do plugin vira uma página só, `plugins/sdd/README.md`: só a instalação como plugin, o pacote `@fission-ai/openspec`, o encadeamento das três skills, e o ciclo e o versionamento remetidos ao comum. Saem `docs/`, `prompts/` e `exemplo/`. O README do kit cita o comando novo.

**Fora desta change:** o texto das skills (itens 4 e 8 do plano); a pasta `trilha/` nos projetos (item 5); declarar o plugin no `.claude/settings.json` do projeto (item 7); os projetos e o guia do curso, que citam o comando antigo; o arquivamento do repositório `pipeline-prd-tdd-openspec`, passo à parte, com ordem do usuário nomeando-o.

## Capabilities

### New Capabilities
- `plugin-sdd`: como o kit publica o plugin `sdd` (o marketplace, o lugar das skills) e a regra que amarra a versão do plugin à do kit.
- `conferencias`: o que os verificadores que os projetos copiam conferem e avisam; nesta change, só o aviso sobre o plugin instalado.

### Modified Capabilities
- (nenhuma; o kit ainda não tem specs)

## Impact

- Código: `modelo/scripts/confere_metodo.py` (a leitura do plugin instalado) e `testes/test_kit.py` (a versão do plugin, o marketplace, o aviso).
- Arquivos novos no kit: `.claude-plugin/marketplace.json`, `plugins/sdd/` (o manifesto, as três skills e o README); o histórico do plugin passa a fazer parte do kit.
- Texto: `modelo/CLAUDE-comum.md` (só a linha da versão), `CLAUDE.md` do kit (a regra de versão), `README.md` do kit (o comando de instalação).
- Máquina do usuário: o plugin instalado troca de marketplace, uma vez.
- Projetos: recebem o `confere_metodo.py` novo na próxima atualização do kit, com a ordem do usuário.
