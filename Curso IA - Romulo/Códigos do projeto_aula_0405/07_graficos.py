import json
import webbrowser
from pathlib import Path

PASTA_SAIDAS = Path("saidas")
ARQUIVO_TELEMETRIA = PASTA_SAIDAS / "telemetria_real.json"
ARQUIVO_HTML = PASTA_SAIDAS / "graficos.html"

def gerar_barra(nome, valor, cor):
    return f"""
    <div class="item">
        <div class="linha">
            <span>{nome}</span>
            <strong>{valor:.1f}%</strong>
        </div>
        <div class="barra-fundo">
            <div class="barra" style="width: {valor}%; background: {cor};"></div>
        </div>
    </div>
    """

def main():
    if not ARQUIVO_TELEMETRIA.exists():
        print("Erro: o arquivo saidas/telemetria_real.json não foi encontrado.")
        print("Execute primeiro: uv run python 05_aplicacao_completa.py")
        return

    with open(ARQUIVO_TELEMETRIA, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    cpu = float(dados.get("cpu_percent", 0))
    memoria = float(dados.get("memoria_percent", 0))
    disco = float(dados.get("disco_percent", 0))

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Gráficos de Telemetria</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f7fb;
                color: #1f2937;
                margin: 40px;
            }}

            .pagina {{
                background: white;
                max-width: 850px;
                margin: auto;
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 4px 18px rgba(0,0,0,0.12);
            }}

            h1 {{
                color: #0f4c81;
                border-bottom: 4px solid #f97316;
                padding-bottom: 12px;
            }}

            .item {{
                margin: 28px 0;
            }}

            .linha {{
                display: flex;
                justify-content: space-between;
                font-size: 20px;
                margin-bottom: 8px;
            }}

            .barra-fundo {{
                background: #e5e7eb;
                border-radius: 20px;
                height: 34px;
                overflow: hidden;
            }}

            .barra {{
                height: 34px;
                border-radius: 20px;
            }}

            .observacao {{
                margin-top: 30px;
                background: #fff7ed;
                border-left: 6px solid #f97316;
                padding: 18px;
                font-size: 18px;
            }}

            @media print {{
                body {{
                    background: white;
                    margin: 0;
                }}

                .pagina {{
                    box-shadow: none;
                    border-radius: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="pagina">
            <h1>Gráficos de Telemetria do Computador</h1>

            {gerar_barra("Uso da CPU", cpu, "#2563eb")}
            {gerar_barra("Uso da memória", memoria, "#f97316")}
            {gerar_barra("Uso do disco", disco, "#0f4c81")}

            <div class="observacao">
                Estes gráficos foram gerados a partir do arquivo
                <strong>telemetria_real.json</strong>. Eles representam uma leitura
                real do computador no momento da execução do programa.
            </div>
        </div>
    </body>
    </html>
    """

    with open(ARQUIVO_HTML, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)

    print(f"Gráficos criados em: {ARQUIVO_HTML}")
    webbrowser.open(ARQUIVO_HTML.resolve().as_uri())

if __name__ == "__main__":
    main()