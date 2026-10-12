"""O kit é coerente: a versão, o esqueleto, o verificador e o gerador da página (Python 3 puro)."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DO_KIT = (
    "CLAUDE-comum.md",
    "CLAUDE.md",
    "ANDAMENTO.md",
    "openspec/config.yaml",
    "scripts/check.sh",
    "scripts/confere_regras.py",
    "scripts/gerar_pagina_sdd.py",
    "scripts/pagina_sdd_modelo.html",
    ".gitignore",
)
ESQUELETO_DO_CLAUDE = RAIZ / "CLAUDE.md"  # o deste repositório não é o esqueleto; o esqueleto é copiado abaixo


def _copia_do_kit(destino: Path) -> None:
    for nome in DO_KIT:
        alvo = destino / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        origem = RAIZ / ("esqueleto-CLAUDE.md" if nome == "CLAUDE.md" else nome)
        shutil.copy(origem if origem.exists() else RAIZ / nome, alvo)


class Kit(unittest.TestCase):
    def test_arquivos_existem(self) -> None:
        faltam = [n for n in DO_KIT if n != "CLAUDE.md" and not (RAIZ / n).is_file()]
        self.assertEqual(faltam, [])

    def test_versao_no_comum(self) -> None:
        for arquivo in ("CLAUDE-comum.md",):
            texto = (RAIZ / arquivo).read_text(encoding="utf-8")
            self.assertIsNotNone(re.search(r"^Versão \d+\.\d+, de \d{4}-\d\d-\d\d\.", texto, re.M), arquivo)

    def test_comum_nao_cita_curso(self) -> None:
        comum = (RAIZ / "CLAUDE-comum.md").read_text(encoding="utf-8")
        self.assertNotIn("curso", comum.lower().replace("em curso", ""))

    def test_regras_falam_do_usuario(self) -> None:
        for arquivo in ("CLAUDE-comum.md", "esqueleto-CLAUDE.md"):
            texto = (RAIZ / arquivo).read_text(encoding="utf-8")
            self.assertNotRegex(texto, r"\b[àa] pessoa\b", arquivo)

    def test_verificador_aprova_um_repositorio_feito_do_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            saida = subprocess.run(
                [sys.executable, "-I", str(destino / "scripts/confere_regras.py"), tmp, "--fonte", str(RAIZ)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(saida.returncode, 0, saida.stderr)

    def test_gerador_da_pagina_nao_inventa_etapas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp)
            _copia_do_kit(destino)
            saida = subprocess.run(
                [sys.executable, "-I", str(destino / "scripts/gerar_pagina_sdd.py")],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(saida.returncode, 0, saida.stderr)
            pagina = (destino / "sdd/documentacao.html").read_text(encoding="utf-8")
            self.assertIn('"prd": ""', pagina)
            self.assertIn("Trilha AI", pagina)


if __name__ == "__main__":
    unittest.main()
