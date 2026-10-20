import os
import shutil
import subprocess
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

PORTA = 8013
PORTA_CHAT = 8001

PASTA_SAIDAS = Path("saidas")

ARQUIVO_TELEMETRIA = PASTA_SAIDAS / "telemetria_real.json"
ARQUIVO_REDE = PASTA_SAIDAS / "rede_local.json"
ARQUIVO_LAUDO = PASTA_SAIDAS / "laudo_tecnico.json"
ARQUIVO_RELATORIO = PASTA_SAIDAS / "laudo_tecnico.html"
ARQUIVO_GRAFICOS = PASTA_SAIDAS / "graficos.html"
ARQUIVO_DASHBOARD = PASTA_SAIDAS / "dashboard.html"

PROCESSO_CHAT = None


def chave_configurada():
    chave = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(chave) and "cole_sua_chave" not in chave


def modelo_usado():
    return os.getenv("OPENAI_MODEL", "openai/gpt-4o")


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


def limpar_saidas():
    PASTA_SAIDAS.mkdir(exist_ok=True)

    arquivos_para_remover = [
        ARQUIVO_TELEMETRIA,
        ARQUIVO_REDE,
        ARQUIVO_LAUDO,
        ARQUIVO_RELATORIO,
        ARQUIVO_GRAFICOS,
        ARQUIVO_DASHBOARD,
        PASTA_SAIDAS / "relatorio_completo_json.txt",
        PASTA_SAIDAS / "laudo_tecnico_para_imprimir.txt",
    ]

    removidos = []

    for arquivo in arquivos_para_remover:
        if arquivo.exists() and arquivo.is_file():
            arquivo.unlink()
            removidos.append(str(arquivo))

    gitkeep = PASTA_SAIDAS / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")

    if not removidos:
        return "Nenhum arquivo de saída foi removido."

    return "Arquivos removidos:\n\n" + "\n".join(removidos)


def gerar_pagina_como_funciona():
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Como o aplicativo funciona</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #172033;
            margin: 40px;
        }

        .pagina {
            background: white;
            max-width: 950px;
            margin: auto;
            padding: 40px;
            border-radius: 18px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }

        h1 {
            color: #0f4c81;
            border-bottom: 5px solid #f97316;
            padding-bottom: 12px;
        }

        h2 {
            color: #0f4c81;
            margin-top: 30px;
        }

        li {
            margin-bottom: 10px;
            font-size: 18px;
        }

        p {
            font-size: 18px;
            line-height: 1.5;
        }

        .caixa {
            background: #fff7ed;
            border-left: 6px solid #f97316;
            padding: 18px;
            border-radius: 12px;
            margin-top: 24px;
        }
    </style>
</head>
<body>
    <div class="pagina">
        <h1>Como este aplicativo funciona?</h1>

        <p>
            Este aplicativo foi criado para mostrar, de forma prática, como Python,
            dados reais do computador, inteligência artificial e front-end podem trabalhar juntos.
        </p>

        <h2>1. Coleta de dados</h2>
        <p>
            O Python lê informações reais do computador, como uso de CPU, memória,
            disco, sistema operacional e rede local.
        </p>

        <h2>2. Arquivos JSON</h2>
        <p>
            Os dados coletados são salvos em arquivos JSON. JSON é um formato usado
            para organizar informações de forma estruturada.
        </p>

        <h2>3. Agentes de IA</h2>
        <p>
            Os agentes analisam os dados e ajudam a gerar um laudo técnico preventivo.
            Eles não consertam o computador; eles ajudam a interpretar os dados.
        </p>

        <h2>4. Relatório</h2>
        <p>
            O relatório transforma o JSON em uma página bonita, pronta para impressão
            ou para salvar como PDF.
        </p>

        <h2>5. Dashboard</h2>
        <p>
            O dashboard mostra os principais resultados em cards, gráficos e listas.
        </p>

        <h2>6. Chat com agentes</h2>
        <p>
            O técnico pode conversar com agentes especializados para entender melhor
            o laudo, os riscos, os procedimentos e os orçamentos.
        </p>

        <div class="caixa">
            <strong>Resumo para os alunos:</strong>
            <ul>
                <li>Python faz a coleta e organiza os dados.</li>
                <li>JSON guarda os resultados.</li>
                <li>A IA interpreta os dados.</li>
                <li>O front-end mostra tudo em uma tela visual.</li>
                <li>O técnico toma decisões com base no laudo.</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

    caminho = PASTA_SAIDAS / "como_funciona.html"
    PASTA_SAIDAS.mkdir(exist_ok=True)
    caminho.write_text(html, encoding="utf-8")
    webbrowser.open(caminho.resolve().as_uri())
    return f"Página explicativa aberta: {caminho}"


def gerar_html():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    chave_status = "CONFIGURADA" if chave_configurada() else "NÃO CONFIGURADA"
    chave_classe = "finalizado" if chave_configurada() else "pendente"

    bloqueado = "disabled" if not ARQUIVO_LAUDO.exists() else ""
    dica_bloqueado = "" if ARQUIVO_LAUDO.exists() else "Execute primeiro o diagnóstico completo para liberar relatório, gráficos, dashboard e chat."

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>App Final de Diagnóstico com IA</title>

    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #172033;
        }}

        .layout {{
            display: grid;
            grid-template-columns: 290px 1fr;
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
            grid-template-columns: repeat(3, 1fr);
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

        .card p {{
            margin: 8px 0 0 0;
            font-size: 15px;
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
            min-height: 90px;
            color: white;
        }}

        button:disabled {{
            background: #94a3b8;
            cursor: not-allowed;
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

        .vermelho {{
            background: #dc2626;
        }}

        .vermelho:hover {{
            background: #b91c1c;
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
                Aplicativo local para coletar dados reais, gerar laudo técnico,
                visualizar gráficos e conversar com agentes.
            </p>

            <div class="info-lateral">
                <strong>Ordem correta:</strong><br>
                1. Executar diagnóstico<br>
                2. Gerar relatório<br>
                3. Abrir gráficos/dashboard<br>
                4. Conversar com agentes
            </div>

            <div class="info-lateral">
                <strong>Uso de créditos:</strong><br>
                O diagnóstico e o chat podem usar créditos da OpenAI.
                Relatório, gráficos e dashboard usam arquivos locais.
            </div>

            <div class="info-lateral">
                <strong>Modelo:</strong><br>
                {modelo_usado()}
            </div>
        </aside>

        <main>
            <div class="topo">
                <h2>Painel Final do Aplicativo</h2>
                <p>Última abertura do painel: {agora}</p>
            </div>

            <div class="cards">
                <div class="card">
                    <h3>Chave OpenAI</h3>
                    <span class="status {chave_classe}">{chave_status}</span>
                    <p>A chave não é exibida por segurança.</p>
                </div>

                <div class="card">
                    <h3>Coleta do computador</h3>
                    <span class="status {classe_status(ARQUIVO_TELEMETRIA)}">
                        {status_texto(ARQUIVO_TELEMETRIA)}
                    </span>
                    <p>Arquivo: telemetria_real.json</p>
                </div>

                <div class="card">
                    <h3>Rede local</h3>
                    <span class="status {classe_status(ARQUIVO_REDE)}">
                        {status_texto(ARQUIVO_REDE)}
                    </span>
                    <p>Arquivo: rede_local.json</p>
                </div>

                <div class="card">
                    <h3>Laudo da IA</h3>
                    <span class="status {classe_status(ARQUIVO_LAUDO)}">
                        {status_texto(ARQUIVO_LAUDO)}
                    </span>
                    <p>Arquivo: laudo_tecnico.json</p>
                </div>

                <div class="card">
                    <h3>Relatório imprimível</h3>
                    <span class="status {classe_status(ARQUIVO_RELATORIO)}">
                        {status_texto(ARQUIVO_RELATORIO)}
                    </span>
                    <p>Arquivo: laudo_tecnico.html</p>
                </div>

                <div class="card">
                    <h3>Chat com agentes</h3>
                    <span class="status {classe_status(ARQUIVO_LAUDO)}">
                        {"DISPONÍVEL" if ARQUIVO_LAUDO.exists() else "PENDENTE"}
                    </span>
                    <p>Depende do laudo técnico.</p>
                </div>
            </div>

            <div class="painel">
                <h2>Comandos do aplicativo</h2>

                <div class="grade">
                    <button class="laranja" onclick="acao('/diagnostico')">
                        1. Executar diagnóstico completo
                        <span class="botao-descricao">
                            Coleta dados reais, aciona agentes e gera o laudo técnico.
                        </span>
                    </button>

                    <button class="azul" onclick="acao('/relatorio')" {bloqueado}>
                        2. Gerar e abrir relatório
                        <span class="botao-descricao">
                            Cria o relatório HTML e abre para impressão.
                        </span>
                    </button>

                    <button class="azul" onclick="acao('/graficos')" {bloqueado}>
                        3. Gerar e abrir gráficos
                        <span class="botao-descricao">
                            Mostra CPU, memória e disco em barras visuais.
                        </span>
                    </button>

                    <button class="azul" onclick="acao('/dashboard')" {bloqueado}>
                        4. Gerar e abrir dashboard
                        <span class="botao-descricao">
                            Mostra cards, resumo, gráficos e evidências.
                        </span>
                    </button>

                    <button class="laranja" onclick="acao('/chat')" {bloqueado}>
                        5. Conversar com agentes
                        <span class="botao-descricao">
                            Abre uma tela para o técnico perguntar sobre o laudo.
                        </span>
                    </button>

                    <button class="azul" onclick="acao('/como-funciona')">
                        6. Como funciona o app?
                        <span class="botao-descricao">
                            Abre uma explicação didática para os alunos.
                        </span>
                    </button>

                    <button class="vermelho" onclick="confirmarLimpeza()">
                        7. Limpar saídas
                        <span class="botao-descricao">
                            Remove os arquivos gerados para começar novamente.
                        </span>
                    </button>

                    <button class="azul" onclick="location.reload()">
                        8. Atualizar status
                        <span class="botao-descricao">
                            Recarrega os cards depois de executar uma etapa.
                        </span>
                    </button>
                </div>

                <div class="aviso">
                    {dica_bloqueado}
                    Acompanhe os cards acima: quando o arquivo existir, o status muda para FINALIZADO.
                    Depois de executar o diagnóstico, clique em "Atualizar status".
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

            try {{
                const resposta = await fetch(rota);
                const texto = await resposta.text();

                saida.innerText = texto;
            }} catch (erro) {{
                saida.innerText = "A conexão com o servidor local foi interrompida. Verifique o terminal e tente novamente.";
            }}
        }}

        async function confirmarLimpeza() {{
            const confirmar = confirm(
                "Tem certeza que deseja limpar os arquivos de saída?\\n\\n" +
                "Isso removerá os JSON, relatório, gráficos e dashboard gerados."
            );

            if (!confirmar) {{
                return;
            }}

            await acao("/limpar");
        }}
    </script>
</body>
</html>
"""


class ServidorApp(BaseHTTPRequestHandler):
    def responder_texto(self, texto):
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(texto.encode("utf-8"))
        except (ConnectionAbortedError, BrokenPipeError):
            pass

    def do_GET(self):
        rota = urlparse(self.path).path

        if rota == "/" or rota == "/app":
            html = gerar_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        elif rota == "/diagnostico":
            if not chave_configurada():
                self.responder_texto(
                    "A chave da OpenAI não está configurada.\n\n"
                    "Verifique o arquivo .env antes de executar o diagnóstico."
                )
                return

            texto = executar_comando("uv run python 05_aplicacao_completa.py")
            self.responder_texto(texto)

        elif rota == "/relatorio":
            if not ARQUIVO_LAUDO.exists():
                self.responder_texto("Execute primeiro o diagnóstico completo.")
                return

            texto_geracao = executar_comando("uv run python 06_saida.py")
            texto_abertura = abrir_arquivo(ARQUIVO_RELATORIO)
            self.responder_texto(texto_geracao + "\n\n" + texto_abertura)

        elif rota == "/graficos":
            if not ARQUIVO_LAUDO.exists():
                self.responder_texto("Execute primeiro o diagnóstico completo.")
                return

            texto_geracao = executar_comando("uv run python 07_graficos.py")
            texto_abertura = abrir_arquivo(ARQUIVO_GRAFICOS)
            self.responder_texto(texto_geracao + "\n\n" + texto_abertura)

        elif rota == "/dashboard":
            if not ARQUIVO_LAUDO.exists():
                self.responder_texto("Execute primeiro o diagnóstico completo.")
                return

            texto_geracao = executar_comando("uv run python 08_frontend.py")
            texto_abertura = abrir_arquivo(ARQUIVO_DASHBOARD)
            self.responder_texto(texto_geracao + "\n\n" + texto_abertura)

        elif rota == "/chat":
            texto = abrir_chat()
            self.responder_texto(texto)

        elif rota == "/como-funciona":
            texto = gerar_pagina_como_funciona()
            self.responder_texto(texto)

        elif rota == "/limpar":
            texto = limpar_saidas()
            self.responder_texto(texto)

        else:
            self.send_response(404)
            self.end_headers()


def main():
    endereco = f"http://localhost:{PORTA}/app"

    print("Aplicativo final iniciado.")
    print(f"Acesse: {endereco}")
    print("Para encerrar, aperte Ctrl + C no terminal.")

    webbrowser.open(endereco)

    servidor = ThreadingHTTPServer(("localhost", PORTA), ServidorApp)
    servidor.serve_forever()


if __name__ == "__main__":
    main()