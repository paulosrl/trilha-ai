# Spec Delta

## ADDED Requirements

### Requirement: Perfil do OpenSpec com o verify no projeto novo
O `kit.py novo` SHALL listar, nos próximos passos, o `openspec config profile` com o verify marcado, e MUST avisar, sem falhar, quando o perfil do OpenSpec da máquina não trouxer o verify ou quando o OpenSpec não estiver instalado. A ferramenta só lê o perfil, nunca o muda.

#### Scenario: Perfil sem o verify
- **WHEN** o `kit.py novo` roda numa máquina cujo perfil do OpenSpec é o padrão (`core`), ou um perfil próprio sem o verify
- **THEN** a ferramenta avisa que o verify falta no perfil, com o comando `openspec config profile`
- **AND** termina com o código de saída 0

#### Scenario: Perfil com o verify
- **WHEN** o `kit.py novo` roda numa máquina cujo perfil do OpenSpec é próprio (`custom`) e traz o verify
- **THEN** a ferramenta não avisa sobre o perfil
- **AND** os próximos passos citam o `openspec config profile`

#### Scenario: OpenSpec ausente
- **WHEN** o comando `openspec` não existe no PATH
- **THEN** a ferramenta avisa que o OpenSpec falta
- **AND** termina com o código de saída 0
