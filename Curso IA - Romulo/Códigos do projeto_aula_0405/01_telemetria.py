"""Primeiro programa: mostrar dados reais do computador em JSON.

Execute no terminal integrado do VS Code:

    uv run python 01_telemetria.py
"""

from __future__ import annotations

import json

from src.telemetria import telemetria_real


def main() -> None:
    dados = telemetria_real()
    print(json.dumps(dados, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
