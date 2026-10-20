"""Segundo programa: validar a telemetria real com Pydantic."""

from __future__ import annotations

import json

from src.modelos import Telemetria
from src.telemetria import telemetria_real


def main() -> None:
    dados_brutos = telemetria_real()
    dados_validados = Telemetria.model_validate(dados_brutos)

    print("Telemetria real validada com Pydantic:")
    print(json.dumps(dados_validados.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
