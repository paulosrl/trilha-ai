# Roteiro de auditoria do kit Trilha AI

Versão 2, de 2026-10-16: uma passada só, só o que tem efeito em uso, e uma pergunta no fim. A rodada de 2026-10 usou a versão 1, de sete etapas: `git show 749abd8:docs/auditorias/roteiro.md`.

## Papel

Você audita o kit Trilha AI como crítico, não como revisor complacente: aponte o que quebra ou contradiz, mesmo que contrarie uma decisão já tomada. Não procure polimento.

## Contexto

Este repositório é a fonte do método que os projetos copiam: o que vai a eles fica em `modelo/`; o plugin `sdd`, em `plugins/`; o resto é só do kit. As regras de manutenção estão no `CLAUDE.md` da raiz. As auditorias anteriores estão nesta pasta: **não repita achado que um relatório anterior já registrou** (corrigido ou aceito), salvo se ele piorou.

## O que conta como achado

Só o que tem efeito em uso, em um destes critérios:

1. **OpenSpec:** estrutura, nome ou fluxo fora do que o OpenSpec instalado faz. O OpenSpec não se ajusta: o desvio se corrige no kit. Confira no código instalado ou na documentação oficial; sem confirmação, marque "a verificar".
2. **Contradição:** duas instruções que mandam coisas opostas, ou uma que anula outra (inclusive pela ordem de carregamento).
3. **Precedência:** um conflito que a ordem declarada não resolve.
4. **Fonte única:** a mesma regra em dois lugares, já com as duas versões divergindo.
5. **Replicação:** algo que impede criar ou atualizar um projeto sem limpeza à mão.
6. **Contexto:** o que entra sozinho em toda sessão e pesa sem servir.
7. **Defeito:** código, trava ou conferência que falha, deixa passar o que devia barrar ou barra o que é legítimo.

**Severidade:** crítica (quebra o uso hoje), alta (quebra em situação provável), média (dúvida ou divergência com efeito real). Entram só os críticos e altos e, no máximo, três médios baratos. Redação, repetição sem divergência e estilo não entram.

## Regras

1. Leia todos os arquivos versionados (`git ls-files`), sem amostragem. Não altere nada até a aprovação.
2. Todo achado cita o arquivo, a linha e o trecho literal. Quando der, prove executando, numa pasta descartável; diga se foi provado ou não.
3. Em conflito, recomende um lado e diga por quê.
4. No máximo dez achados. Se passar disso, fique com os mais graves e diga quantos ficaram de fora.

## A entrega: uma mensagem só

1. **Veredito,** em até três linhas: o kit está bom para uso? O que é mais grave?
2. **Achados,** numa tabela: ID | severidade | arquivo:linha | evidência (trecho literal) | efeito no uso | provado? | correção proposta.
3. **O pacote de correção:** o menor conjunto que resolve os achados. Prefira uma change do OpenSpec (para a ferramenta, os verificadores e as travas) e um commit de texto (para o método e o kit), com o esforço estimado e a versão que ele abre.
4. **Uma pergunta:** "aprova o pacote?".

Nada de etapas com confirmação no meio, inventário de arquivos ou checklist, salvo se o usuário pedir.

## Depois da aprovação

Execute o pacote no ciclo de uma change do `CLAUDE.md` do kit. Grave o relatório nesta pasta, como `AAAA-MM.md`, com os achados, as decisões e o andamento. O que ficar de fora vai ao relatório como aceito, sem trabalho previsto.
