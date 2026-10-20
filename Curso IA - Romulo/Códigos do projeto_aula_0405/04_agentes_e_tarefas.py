"""Quarto programa: criar agentes e tarefas sem chamar a API."""

from __future__ import annotations

from src.config import OPENAI_MODEL, chave_openai_configurada, criar_llm


def main() -> None:
    if not chave_openai_configurada():
        print(
            "OPENAI_API_KEY não configurada. Copie .env.example para .env "
            "antes de criar os agentes."
        )
        return 2

    from src.agentes import criar_agentes
    from src.tarefas import criar_tarefas

    llm = criar_llm()
    agentes = criar_agentes(llm)
    tarefas = criar_tarefas(agentes)

    print("Modelo configurado:", OPENAI_MODEL)
    print("\nAgentes criados:")
    for nome, agente in agentes.items():
        print(f"- {nome}: {agente.role}")

    print("\nTarefas criadas em ordem:")
    for indice, tarefa in enumerate(tarefas, start=1):
        print(f"{indice}. {tarefa.expected_output}")

    print("\nNenhuma tarefa foi executada ainda.")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
