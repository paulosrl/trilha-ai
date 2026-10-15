# Design

## Context

O plugin vive em `../pipeline-prd-tdd-openspec` (público, 12 commits, versão 0.3.9), com os arquivos em `.claude-plugin/marketplace.json` e `plugins/sdd/` — os mesmos caminhos que ele terá no kit. Os dois repositórios só têm em comum `README.md` (conteúdos diferentes) e `LICENSE` (idênticos desde o item 2 do plano). O `modelo/scripts/confere_metodo.py` hoje compara o `plugin.json` da pasta vizinha com `~/.claude/plugins/installed_plugins.json`; ele roda no `check.sh`, no CI (sem Claude Code) e na trava do commit. A motivação está em proposal.md.

## Goals / Non-Goals

**Goals:**
- O kit como única fonte do plugin, com o histórico dele preservado.
- Uma versão para o kit e o plugin, com o teste como guarda.
- A conferência do plugin sem caminhos da máquina do autor.

**Non-Goals:**
- Mudar o texto das skills (só os metadados do manifesto: versão e endereço).
- Fixar a versão do plugin por projeto: o Claude Code não oferece isso (verificação 1c da auditoria).
- Arquivar o repositório antigo ou atualizar os projetos e o guia do curso.

## Decisions

**1. Merge de históricos não relacionados.** `git merge --allow-unrelated-histories` do repositório do plugin traz os 12 commits e deixa cada arquivo no caminho certo, sem renomear. O único conflito previsto é o `README.md`, resolvido mantendo o do kit; o conteúdo do README do plugin vai para `plugins/sdd/README.md`. Alternativas: cópia simples (perde o `git blame` das skills dentro do kit) e `git subtree` com prefixo (põe tudo numa subpasta e exigiria mover de volta).

**2. Versão `X.Y.0`.** O comum continua dono da versão ("Versão X.Y"); o manifesto usa a mesma, completada com `.0`, porque manifestos de plugin seguem o formato de três números. O salto de 0.3.9 para 1.35.0 é para a frente, então quem atualizar recebe a versão nova. Alternativa descartada: manter uma versão própria do plugin, que é o problema F18.

**3. `claude plugin list --json`, com prazo.** É o comando documentado (verificação 1e); o arquivo interno não promete formato. A chamada tem prazo de 10 s e qualquer falha (sem o comando, erro, texto que não é JSON, prazo vencido) vira silêncio, como no CI. São avaliadas todas as instalações `sdd@…` da lista (pode haver uma por escopo): a de fora do kit avisa, qualquer que seja o marketplace, e a do kit avisa se estiver desligada ou em outra versão. A consulta custa de 0,8 s a alguns segundos, por subir o Claude Code; por isso a trava do commit chama a conferência com `--sem-plugin`, e o aviso fica no `check.sh`, que o método manda rodar antes do commit (revisto depois da revisão independente; a primeira versão aceitava o custo na trava). A versão do projeto vem do `CLAUDE-comum.md` da raiz do projeto, que é o que os projetos têm hoje.

**4. Uma página de documentação.** `plugins/sdd/README.md` fica com o que só o plugin sabe dizer (o que cada skill faz, as perguntas frequentes) e remete ao kit para o ciclo, o versionamento e a instalação das outras ferramentas; `docs/`, `prompts/` e `exemplo/` saem. Os nomes `sdd:prd`, `sdd:tdd` e `sdd:briefing` não mudam, porque o plugin continua `sdd`.

**5. A versão 1.35 e a tag.** A linha de versão do comum sobe na change (o texto do comum não muda) e o `plugin.json` acompanha; a tag `v1.35` vai no merge commit da main, enviada com ele, como manda o `CLAUDE.md` do kit.

## Risks / Trade-offs

- [O guia do curso e os projetos citam o marketplace antigo] → o repositório antigo continua público e legível (arquivado, só leitura), então o comando antigo segue funcionando; o aviso da conferência mostra como migrar.
- [Duas instalações na mesma máquina, a antiga e a nova] → o aviso do marketplace antigo aparece até a antiga sair; a migração remove a antiga primeiro.
- [O formato do `claude plugin list --json` mudar] → leitura defensiva; formato desconhecido vira silêncio, nunca falha.
- [Mudança em `modelo/` ou `plugins/` sem versão nova, que o cache do plugin, por versão, não entregaria] → depois que a tag da versão existe, os testes do kit reprovam qualquer mudança nessas pastas.

## Migration Plan

1. Na branch: o merge do plugin, os metadados, o teste, a conferência e a documentação.
2. Execução manual, com a confirmação do usuário: `claude plugin uninstall sdd@pipeline-prd-tdd-openspec`, `claude plugin marketplace remove pipeline-prd-tdd-openspec`, `claude plugin marketplace add /home/pl/projetos/trilha-ai` e `claude plugin install sdd@trilha-ai`; conferir `claude plugin list --json` e o aviso num projeto descartável.
3. Depois do merge: trocar o marketplace local pelo do GitHub (`claude plugin marketplace remove trilha-ai` e `claude plugin marketplace add paulosrl/trilha-ai`), reinstalar e conferir a versão 1.35.0.
4. Volta atrás: reinstalar `sdd@pipeline-prd-tdd-openspec`, que continua disponível; reverter o merge da change.

## Respostas à revisão

O `/opsx:verify` não achou problema crítico nem aviso; a sugestão dele (um teste para o prazo vencido da lista de plugins) fica para quando o `confere_metodo.py` mudar por outro motivo, porque o spec não a pede. A revisão independente (`/code-review 1`) achou 9 pontos; o usuário escolheu aplicar 7 e recusar 2:

1. **Aplicada.** Um `sdd@` de outro marketplace escondia a falta do plugin do kit: o aviso de fora do kit vale para qualquer `sdd@` que não seja `sdd@trilha-ai`.
2. **Aplicada.** O `sdd@trilha-ai` desligado passava sem aviso: avisa, com `claude plugin enable sdd@trilha-ai`.
3. **Aplicada.** A trava do commit ficava lenta ao subir o Claude Code: ela usa `--sem-plugin`, e o aviso fica no `check.sh` (decisão 3 revista).
4. **Aplicada.** Os comandos ligados por `&&` deixariam de instalar se o marketplace já existisse: o aviso os dá separados.
5. **Aplicada.** Nada barrava a mudança em `plugins/` sem versão nova: depois da tag da versão atual, os testes a reprovam.
6. **Aplicada.** O teste repetia a leitura da versão: usa a do `kit.py`.
7. **Aplicada.** O PATH dos testes não voltava ao original: volta no fim do módulo.
8. **Recusada.** Texto fora do JSON na saída da lista de plugins: a saída `--json` é documentada como JSON, e o spec já manda silêncio para texto que não é JSON.
9. **Recusada.** A tag `v1.35` ausente: ela vai no merge commit da main, pela decisão 5 e pelo `CLAUDE.md` do kit.
