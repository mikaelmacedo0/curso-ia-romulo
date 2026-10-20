import json
import webbrowser
from pathlib import Path

PASTA_SAIDAS = Path("saidas")

ARQUIVO_TELEMETRIA = PASTA_SAIDAS / "telemetria_real.json"
ARQUIVO_REDE = PASTA_SAIDAS / "rede_local.json"
ARQUIVO_LAUDO = PASTA_SAIDAS / "laudo_tecnico.json"

ARQUIVO_HTML = PASTA_SAIDAS / "dashboard.html"


def carregar_json(caminho):
    if not caminho.exists():
        return None

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def lista_html(itens):
    if not itens:
        return "<p>Não informado.</p>"

    texto = "<ul>"
    for item in itens:
        texto += f"<li>{item}</li>"
    texto += "</ul>"

    return texto


def barra(nome, valor, cor):
    return f"""
    <div class="grafico-item">
        <div class="grafico-texto">
            <span>{nome}</span>
            <strong>{valor:.1f}%</strong>
        </div>
        <div class="barra-fundo">
            <div class="barra" style="width: {valor}%; background-color: {cor};"></div>
        </div>
    </div>
    """


def main():
    telemetria = carregar_json(ARQUIVO_TELEMETRIA)
    rede = carregar_json(ARQUIVO_REDE)
    laudo = carregar_json(ARQUIVO_LAUDO)

    if telemetria is None or rede is None or laudo is None:
        print("Erro: faltam arquivos JSON na pasta saidas.")
        print("Execute primeiro: uv run python 05_aplicacao_completa.py")
        return

    cpu = float(telemetria.get("cpu_percent", 0))
    memoria = float(telemetria.get("memoria_percent", 0))
    disco = float(telemetria.get("disco_percent", 0))

    classificacao = laudo.get("classificacao", "Não informado")
    resumo = laudo.get("resumo", "Não informado.")
    temperatura = telemetria.get("temperatura", "não coletada")
    sistema = telemetria.get("sistema_operacional", "não informado")
    processos = telemetria.get("processos_ativos", "não informado")
    hostname = rede.get("hostname", "não informado")

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard de Diagnóstico com IA</title>

        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f4f7fb;
                color: #172033;
            }}

            header {{
                background: linear-gradient(135deg, #0f4c81, #2563eb);
                color: white;
                padding: 32px 48px;
            }}

            header h1 {{
                margin: 0;
                font-size: 34px;
            }}

            header p {{
                font-size: 18px;
                margin-top: 8px;
            }}

            main {{
                padding: 32px 48px;
                max-width: 1100px;
                margin: auto;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 18px;
                margin-bottom: 28px;
            }}

            .card {{
                background: white;
                padding: 22px;
                border-radius: 16px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.10);
                border-top: 5px solid #f97316;
            }}

            .card h2 {{
                font-size: 17px;
                color: #0f4c81;
                margin: 0 0 10px 0;
            }}

            .card p {{
                font-size: 24px;
                font-weight: bold;
                margin: 0;
            }}

            section {{
                background: white;
                padding: 28px;
                border-radius: 16px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.10);
                margin-bottom: 28px;
            }}

            section h2 {{
                color: #0f4c81;
                margin-top: 0;
                border-bottom: 3px solid #f97316;
                padding-bottom: 8px;
            }}

            .classificacao {{
                display: inline-block;
                background: #ffedd5;
                color: #c2410c;
                padding: 10px 18px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 20px;
            }}

            .grafico-item {{
                margin: 22px 0;
            }}

            .grafico-texto {{
                display: flex;
                justify-content: space-between;
                font-size: 20px;
                margin-bottom: 8px;
            }}

            .barra-fundo {{
                background: #e5e7eb;
                border-radius: 20px;
                height: 32px;
                overflow: hidden;
            }}

            .barra {{
                height: 32px;
                border-radius: 20px;
            }}

            li {{
                margin-bottom: 8px;
                font-size: 18px;
            }}

            .botao-imprimir {{
                background: #f97316;
                color: white;
                border: none;
                padding: 14px 22px;
                border-radius: 12px;
                font-size: 18px;
                cursor: pointer;
            }}

            .botao-imprimir:hover {{
                background: #ea580c;
            }}

            @media print {{
                .botao-imprimir {{
                    display: none;
                }}

                body {{
                    background: white;
                }}

                section, .card {{
                    box-shadow: none;
                    border: 1px solid #ddd;
                }}
            }}
        </style>
    </head>

    <body>
        <header>
            <h1>Dashboard de Diagnóstico com IA</h1>
            <p>Projeto educacional com Python, CrewAI, OpenAI e dados reais do computador</p>
        </header>

        <main>
            <button class="botao-imprimir" onclick="window.print()">Imprimir ou salvar em PDF</button>

            <div class="cards">
                <div class="card">
                    <h2>CPU</h2>
                    <p>{cpu:.1f}%</p>
                </div>

                <div class="card">
                    <h2>Memória</h2>
                    <p>{memoria:.1f}%</p>
                </div>

                <div class="card">
                    <h2>Disco</h2>
                    <p>{disco:.1f}%</p>
                </div>

                <div class="card">
                    <h2>Processos</h2>
                    <p>{processos}</p>
                </div>
            </div>

            <section>
                <h2>Classificação da IA</h2>
                <p class="classificacao">{classificacao}</p>
                <p>{resumo}</p>
            </section>

            <section>
                <h2>Gráficos de uso do computador</h2>
                {barra("Uso da CPU", cpu, "#2563eb")}
                {barra("Uso da memória", memoria, "#f97316")}
                {barra("Uso do disco", disco, "#0f4c81")}
            </section>

            <section>
                <h2>Informações do computador</h2>
                <p><strong>Nome do computador:</strong> {hostname}</p>
                <p><strong>Sistema operacional:</strong> {sistema}</p>
                <p><strong>Temperatura:</strong> {temperatura}</p>
            </section>

            <section>
                <h2>Evidências encontradas</h2>
                {lista_html(laudo.get("evidencias", []))}
            </section>

            <section>
                <h2>Procedimentos recomendados</h2>
                {lista_html(laudo.get("procedimentos", []))}
            </section>
        </main>
    </body>
    </html>
    """

    with open(ARQUIVO_HTML, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)

    print(f"Dashboard criado em: {ARQUIVO_HTML}")
    webbrowser.open(ARQUIVO_HTML.resolve().as_uri())


if __name__ == "__main__":
    main()