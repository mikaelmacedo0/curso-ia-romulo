import json
import webbrowser
from pathlib import Path

PASTA_SAIDAS = Path("saidas")
ARQUIVO_JSON = PASTA_SAIDAS / "laudo_tecnico.json"
ARQUIVO_HTML = PASTA_SAIDAS / "laudo_tecnico.html"

def lista_html(itens):
    if not itens:
        return "<p>Não informado.</p>"
    return "<ul>" + "".join(f"<li>{item}</li>" for item in itens) + "</ul>"

def gerar_html(dados):
    orcamentos_html = ""

    for orcamento in dados.get("orcamentos", []):
        itens_html = ""
        for item in orcamento.get("itens", []):
            itens_html += f"""
            <tr>
                <td>{item.get("codigo", "")}</td>
                <td>{item.get("descricao", "")}</td>
                <td>{item.get("quantidade", "")}</td>
                <td>R$ {item.get("valor_unitario", 0):.2f}</td>
                <td>R$ {item.get("subtotal", 0):.2f}</td>
            </tr>
            """

        orcamentos_html += f"""
        <section>
            <h2>{orcamento.get("nome", "Orçamento")}</h2>
            <table>
                <tr>
                    <th>Código</th>
                    <th>Descrição</th>
                    <th>Qtd.</th>
                    <th>Valor unitário</th>
                    <th>Subtotal</th>
                </tr>
                {itens_html}
            </table>
            <p><strong>Total de materiais:</strong> R$ {orcamento.get("total_materiais", 0):.2f}</p>
            <p><strong>Mão de obra:</strong> R$ {orcamento.get("total_mao_de_obra", 0):.2f}</p>
            <p><strong>Total:</strong> R$ {orcamento.get("total", 0):.2f}</p>
        </section>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Laudo Técnico Preventivo</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f7fb;
                color: #1f2937;
                margin: 40px;
            }}

            .pagina {{
                background: white;
                max-width: 900px;
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

            h2 {{
                color: #0f4c81;
                margin-top: 32px;
            }}

            .classificacao {{
                display: inline-block;
                background: #ffedd5;
                color: #c2410c;
                padding: 10px 18px;
                border-radius: 20px;
                font-weight: bold;
            }}

            section {{
                margin-top: 24px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 12px;
            }}

            th {{
                background: #0f4c81;
                color: white;
                padding: 10px;
                text-align: left;
            }}

            td {{
                border-bottom: 1px solid #ddd;
                padding: 10px;
            }}

            li {{
                margin-bottom: 8px;
            }}

            .assinatura {{
                margin-top: 50px;
                border-top: 1px solid #999;
                width: 320px;
                text-align: center;
                padding-top: 8px;
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
            <h1>Laudo Técnico Preventivo</h1>

            <p><strong>Classificação:</strong></p>
            <p class="classificacao">{dados.get("classificacao", "Não informado")}</p>

            <section>
                <h2>Resumo</h2>
                <p>{dados.get("resumo", "Não informado.")}</p>
            </section>

            <section>
                <h2>Evidências encontradas</h2>
                {lista_html(dados.get("evidencias", []))}
            </section>

            <section>
                <h2>Possíveis diagnósticos</h2>
                {lista_html(dados.get("possiveis_diagnosticos", []))}
            </section>

            <section>
                <h2>Procedimentos recomendados</h2>
                {lista_html(dados.get("procedimentos", []))}
            </section>

            <section>
                <h2>Orçamentos</h2>
                {orcamentos_html}
            </section>

            <section>
                <h2>Limitações da análise</h2>
                {lista_html(dados.get("limitacoes", []))}
            </section>

            <section>
                <h2>Aprovação do responsável de TI</h2>
                <p><strong>Status:</strong> {dados.get("aprovacao_responsavel_ti", "PENDENTE")}</p>
            </section>

            <div class="assinatura">
                Responsável técnico
            </div>
        </div>
    </body>
    </html>
    """

def main():
    if not ARQUIVO_JSON.exists():
        print("Erro: o arquivo saidas/laudo_tecnico.json não foi encontrado.")
        print("Execute primeiro: uv run python 05_aplicacao_completa.py")
        return

    with open(ARQUIVO_JSON, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    html = gerar_html(dados)

    with open(ARQUIVO_HTML, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)

    print(f"Relatório criado em: {ARQUIVO_HTML}")
    webbrowser.open(ARQUIVO_HTML.resolve().as_uri())

if __name__ == "__main__":
    main()