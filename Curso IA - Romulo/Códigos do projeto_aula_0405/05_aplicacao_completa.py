"""Aplicação completa: coleta real, Crew sequencial e laudo final.

Comandos:

    uv run python 05_aplicacao_completa.py --apenas-coleta
    uv run python 05_aplicacao_completa.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.coleta_local import coletar_telemetria_dados, verificar_rede_local_dados
from src.config import OUTPUT_DIR, chave_openai_configurada, criar_llm


def salvar_json(nome: str, conteudo: Any) -> Path:
    """Salva um resultado legível na pasta saidas."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    caminho = OUTPUT_DIR / nome
    caminho.write_text(
        json.dumps(conteudo, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return caminho


def resultado_para_dict(resultado: Any) -> dict[str, Any]:
    """Converte CrewOutput em um dicionário sem perder o laudo estruturado."""

    modelo = getattr(resultado, "pydantic", None)
    if modelo is not None:
        return modelo.model_dump(mode="json")

    json_dict = getattr(resultado, "json_dict", None)
    if json_dict:
        return json_dict

    conversao = getattr(resultado, "to_dict", None)
    if callable(conversao):
        valor = conversao()
        if isinstance(valor, dict):
            return valor

    return {"resultado_bruto": getattr(resultado, "raw", str(resultado))}


def executar_aplicacao() -> int:
    """Executa o caminho real da aplicação."""

    if not chave_openai_configurada():
        print(
            "OPENAI_API_KEY não configurada. Copie .env.example para .env "
            "e informe a chave somente nesse arquivo local."
        )
        return 2

    # A coleta acontece antes da Crew para produzir uma evidência concreta.
    telemetria_inicial = coletar_telemetria_dados()
    rede_inicial = verificar_rede_local_dados()
    salvar_json("telemetria_real.json", json.loads(telemetria_inicial))
    salvar_json("rede_local.json", json.loads(rede_inicial))

    from crewai import Crew, Process

    from src.agentes import criar_agentes
    from src.tarefas import criar_tarefas

    llm = criar_llm()
    agentes = criar_agentes(llm)
    tarefas = criar_tarefas(agentes)

    crew = Crew(
        agents=list(agentes.values()),
        tasks=tarefas,
        process=Process.sequential,
        verbose=True,
    )

    print("\nIniciando a Crew com dados reais...\n")
    resultado = crew.kickoff(
        inputs={
            "telemetria_inicial": telemetria_inicial,
            "rede_inicial": rede_inicial,
        }
    )

    laudo = resultado_para_dict(resultado)
    caminho_laudo = salvar_json("laudo_tecnico.json", laudo)

    print("\n=== LAUDO FINAL ===")
    print(json.dumps(laudo, ensure_ascii=False, indent=2))
    print(f"\nLaudo salvo em: {caminho_laudo}")
    print("Aprovação do responsável de TI: PENDENTE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnóstico preventivo com dados reais")
    parser.add_argument(
        "--apenas-coleta",
        action="store_true",
        help="Lê o computador e a rede sem chamar a OpenAI.",
    )
    args = parser.parse_args()

    if args.apenas_coleta:
        telemetria = coletar_telemetria_dados()
        rede = verificar_rede_local_dados()
        salvar_json("telemetria_real.json", json.loads(telemetria))
        salvar_json("rede_local.json", json.loads(rede))
        print("=== TELEMETRIA REAL ===")
        print(telemetria)
        print("\n=== REDE LOCAL ===")
        print(rede)
        return 0

    return executar_aplicacao()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
