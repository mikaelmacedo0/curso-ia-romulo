import subprocess
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PORTA = 8012
PORTA_CHAT = 8001

PASTA_SAIDAS = Path("saidas")

ARQUIVO_TELEMETRIA = PASTA_SAIDAS / "telemetria_real.json"
ARQUIVO_REDE = PASTA_SAIDAS / "rede_local.json"
ARQUIVO_LAUDO = PASTA_SAIDAS / "laudo_tecnico.json"
ARQUIVO_RELATORIO = PASTA_SAIDAS / "laudo_tecnico.html"
ARQUIVO_GRAFICOS = PASTA_SAIDAS / "graficos.html"
ARQUIVO_DASHBOARD = PASTA_SAIDAS / "dashboard.html"

PROCESSO_CHAT = None


def status_texto(caminho):
    if caminho.exists():
        return "FINALIZADO"
    return "PENDENTE"


def classe_status(caminho):
    if caminho.exists():
        return "finalizado"
    return "pendente"


def executar_comando(comando):
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        saida = resultado.stdout + "\n" + resultado.stderr

        if resultado.returncode == 0:
            return "Comando executado com sucesso.\n\n" + saida

        return "O comando apresentou erro.\n\n" + saida

    except Exception as erro:
        return f"Erro ao executar comando: {erro}"


def abrir_arquivo(caminho):
    if not caminho.exists():
        return f"Arquivo não encontrado: {caminho}"

    webbrowser.open(caminho.resolve().as_uri())
    return f"Arquivo aberto: {caminho}"


def abrir_chat():
    global PROCESSO_CHAT

    if not Path("10_chat_agentes.py").exists():
        return "Arquivo 10_chat_agentes.py não encontrado."

    if not ARQUIVO_LAUDO.exists():
        return (
            "O laudo técnico ainda não foi encontrado.\n\n"
            "Clique primeiro em:\n"
            "1. Executar diagnóstico completo"
        )

    if PROCESSO_CHAT is None or PROCESSO_CHAT.poll() is not None:
        PROCESSO_CHAT = subprocess.Popen(
            [sys.executable, "10_chat_agentes.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    endereco_chat = f"http://localhost:{PORTA_CHAT}/chat"
    webbrowser.open(endereco_chat)

    return f"Chat com agentes aberto em: {endereco_chat}"


def gerar_html():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>App de Diagnóstico com IA</title>

    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #172033;
        }}

        .layout {{
            display: grid;
            grid-template-columns: 280px 1fr;
            min-height: 100vh;
        }}

        aside {{
            background: #0f4c81;
            color: white;
            padding: 28px 22px;
        }}

        aside h1 {{
            font-size: 26px;
            margin: 0 0 10px 0;
        }}

        aside p {{
            font-size: 16px;
            line-height: 1.4;
            color: #dbeafe;
        }}

        .info-lateral {{
            background: rgba(255,255,255,0.13);
            padding: 14px;
            border-radius: 12px;
            margin-top: 14px;
            font-size: 15px;
            line-height: 1.4;
        }}

        .info-lateral strong {{
            color: #ffffff;
        }}

        main {{
            padding: 34px;
        }}

        .topo {{
            background: linear-gradient(135deg, #2563eb, #0f4c81);
            color: white;
            padding: 28px;
            border-radius: 18px;
            margin-bottom: 24px;
        }}

        .topo h2 {{
            font-size: 34px;
            margin: 0;
        }}

        .topo p {{
            font-size: 18px;
            margin-bottom: 0;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-bottom: 24px;
        }}

        .card {{
            background: white;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.10);
            border-top: 6px solid #f97316;
        }}

        .card h3 {{
            margin: 0 0 8px 0;
            color: #0f4c81;
            font-size: 17px;
        }}

        .status {{
            display: inline-block;
            padding: 8px 12px;
            border-radius: 18px;
            font-weight: bold;
            font-size: 14px;
        }}

        .finalizado {{
            background: #dcfce7;
            color: #166534;
        }}

        .pendente {{
            background: #ffedd5;
            color: #c2410c;
        }}

        .painel {{
            background: white;
            border-radius: 18px;
            padding: 28px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}

        h2 {{
            color: #0f4c81;
            border-bottom: 4px solid #f97316;
            padding-bottom: 8px;
        }}

        .grade {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 18px;
            margin-top: 24px;
        }}

        button {{
            border: none;
            padding: 18px;
            border-radius: 14px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            min-height: 88px;
            color: white;
        }}

        .laranja {{
            background: #f97316;
        }}

        .laranja:hover {{
            background: #ea580c;
        }}

        .azul {{
            background: #2563eb;
        }}

        .azul:hover {{
            background: #1d4ed8;
        }}

        .botao-descricao {{
            display: block;
            font-size: 14px;
            font-weight: normal;
            margin-top: 6px;
            opacity: 0.95;
        }}

        .saida {{
            margin-top: 28px;
            background: #eef6ff;
            border-left: 6px solid #2563eb;
            padding: 18px;
            border-radius: 12px;
            white-space: pre-wrap;
            font-size: 16px;
            min-height: 130px;
        }}

        .aviso {{
            background: #fff7ed;
            border-left: 6px solid #f97316;
            padding: 18px;
            border-radius: 12px;
            margin-top: 22px;
            font-size: 17px;
        }}

        @media print {{
            aside, button, .saida {{
                display: none;
            }}

            .layout {{
                display: block;
            }}

            body {{
                background: white;
            }}
        }}
    </style>
</head>

<body>
    <div class="layout">
        <aside>
            <h1>Diagnóstico com IA</h1>
            <p>
                Aplicativo local para coletar dados reais do computador,
                gerar laudo técnico e conversar com agentes de IA.
            </p>

            <div class="info-lateral">
                <strong>Como usar:</strong><br>
                Primeiro execute o diagnóstico completo. Depois gere o relatório,
                visualize gráficos, abra o dashboard ou converse com os agentes.
            </div>

            <div class="info-lateral">
                <strong>Importante:</strong><br>
                O diagnóstico e o chat usam a API da OpenAI. Relatório, gráficos
                e dashboard usam arquivos locais já gerados.
            </div>
        </aside>

        <main>
            <div class="topo">
                <h2>Painel Principal do Aplicativo</h2>
                <p>Última abertura do painel: {agora}</p>
            </div>

            <div class="cards">
                <div class="card">
                    <h3>Coleta do computador</h3>
                    <span class="status {classe_status(ARQUIVO_TELEMETRIA)}">
                        {status_texto(ARQUIVO_TELEMETRIA)}
                    </span>
                </div>

                <div class="card">
                    <h3>Rede local</h3>
                    <span class="status {classe_status(ARQUIVO_REDE)}">
                        {status_texto(ARQUIVO_REDE)}
                    </span>
                </div>

                <div class="card">
                    <h3>Laudo da IA</h3>
                    <span class="status {classe_status(ARQUIVO_LAUDO)}">
                        {status_texto(ARQUIVO_LAUDO)}
                    </span>
                </div>

                <div class="card">
                    <h3>Relatório imprimível</h3>
                    <span class="status {classe_status(ARQUIVO_RELATORIO)}">
                        {status_texto(ARQUIVO_RELATORIO)}
                    </span>
                </div>
            </div>

            <div class="painel">
                <h2>Comandos do aplicativo</h2>

                <div class="grade">
                    <button class="laranja" onclick="acao('/diagnostico')">
                        1. Executar diagnóstico completo
                        <span class="botao-descricao">
                            Coleta dados reais, aciona os agentes e gera o laudo técnico.
                        </span>
                    </button>

                    <button class="azul" onclick="acao('/relatorio')">
                        2. Gerar e abrir relatório
                        <span class="botao-descricao">
                            Cria o relatório HTML e abre para impressão.
                        </span>
                    </button>

                    <button class="azul" onclick="acao('/graficos')">
                        3. Gerar e abrir gráficos
                        <span class="botao-descricao">
                            Mostra CPU, memória e disco em barras visuais.
                        </span>
                    </button>

                    <button class="azul" onclick="acao('/dashboard')">
                        4. Gerar e abrir dashboard
                        <span class="botao-descricao">
                            Mostra cards, resumo, gráficos e evidências.
                        </span>
                    </button>

                    <button class="laranja" onclick="acao('/chat')">
                        5. Conversar com agentes
                        <span class="botao-descricao">
                            Abre uma tela para o técnico perguntar sobre o laudo.
                        </span>
                    </button>
                </div>

                <div class="aviso">
                    Acompanhe os cards acima: quando o arquivo existir, o status muda de
                    PENDENTE para FINALIZADO.
                </div>

                <h2>Saída do sistema</h2>
                <div id="saida" class="saida">
                    Aguardando comando...
                </div>
            </div>
        </main>
    </div>

    <script>
        async function acao(rota) {{
            const saida = document.getElementById("saida");
            saida.innerText = "Executando, aguarde...";

            const resposta = await fetch(rota);
            const texto = await resposta.text();

            saida.innerText = texto;

            setTimeout(() => {{
                location.reload();
            }}, 2500);
        }}
    </script>
</body>
</html>
"""


class ServidorApp(BaseHTTPRequestHandler):
    def responder_texto(self, texto):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(texto.encode("utf-8"))

    def do_GET(self):
        rota = urlparse(self.path).path

        if rota == "/" or rota == "/app":
            html = gerar_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        elif rota == "/diagnostico":
            texto = executar_comando("uv run python 05_aplicacao_completa.py")
            self.responder_texto(texto)

        elif rota == "/relatorio":
            texto_geracao = executar_comando("uv run python 06_saida.py")
            texto_abertura = abrir_arquivo(ARQUIVO_RELATORIO)
            self.responder_texto(texto_geracao + "\n\n" + texto_abertura)

        elif rota == "/graficos":
            texto_geracao = executar_comando("uv run python 07_graficos.py")
            texto_abertura = abrir_arquivo(ARQUIVO_GRAFICOS)
            self.responder_texto(texto_geracao + "\n\n" + texto_abertura)

        elif rota == "/dashboard":
            texto_geracao = executar_comando("uv run python 08_frontend.py")
            texto_abertura = abrir_arquivo(ARQUIVO_DASHBOARD)
            self.responder_texto(texto_geracao + "\n\n" + texto_abertura)

        elif rota == "/chat":
            texto = abrir_chat()
            self.responder_texto(texto)

        else:
            self.send_response(404)
            self.end_headers()


def main():
    endereco = f"http://localhost:{PORTA}/app"

    print("Aplicativo melhorado iniciado.")
    print(f"Acesse: {endereco}")
    print("Para encerrar, aperte Ctrl + C no terminal.")

    webbrowser.open(endereco)

    servidor = ThreadingHTTPServer(("localhost", PORTA), ServidorApp)
    servidor.serve_forever()


if __name__ == "__main__":
    main()