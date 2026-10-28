"""Terceiro programa: conferir as ferramentas e suas funções locais."""

from __future__ import annotations

from src.coleta_local import (
    calcular_orcamento_dados,
    coletar_telemetria_dados,
    verificar_rede_local_dados,
)
from src.ferramentas import calcular_orcamento, coletar_telemetria, verificar_rede_local


def main() -> None:
    print("Ferramentas registradas no CrewAI:")
    for ferramenta in (coletar_telemetria, verificar_rede_local, calcular_orcamento):
        print(f"- {ferramenta.name}")

    print("\n=== TELEMETRIA REAL ===")
    print(coletar_telemetria_dados())

    print("\n=== REDE LOCAL ===")
    print(verificar_rede_local_dados())

    print("\n=== ORÇAMENTO RECOMENDADO ===")
    print(calcular_orcamento_dados("recomendado"))


if __name__ == "__main__":
    main()
