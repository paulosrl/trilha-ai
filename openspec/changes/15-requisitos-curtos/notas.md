# Notas da change 15

## Verificação

**Execução manual (tarefa 2.2), em 2026-10-24,** com o OpenSpec 1.15.0, numa cópia do `openspec/` numa pasta à parte: o `openspec archive 15-requisitos-curtos --yes` de lá aplicou o delta ("+ 5, ~ 3, - 0, → 0"); o `openspec validate horas-de-trabalho --type spec --strict` passou, sem o aviso dos requisitos longos, e o `openspec show` listou 24 requisitos e 75 cenários (eram 19 e 70), com os 70 cenários de antes com o texto igual.
