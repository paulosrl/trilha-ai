# Notas da change 17

## Verificação

**Execução manual (tarefa 3.2), em 2026-10-24,** no Python 3.12, num repositório de teste vazio (`repo`), com uma pasta dos dados à parte que tinha um `repo-0123abcd.json` com o texto "isto não é json": o `python3 -I modelo/trilha/tempo.py` do kit terminou com 0 nas duas execuções seguidas, as duas com o aviso que cita o arquivo e diz "corrija-o ou mova-o", e o arquivo ficou igual (md5 antes e depois).
