import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PORTA = 8001

PASTA_SAIDAS = Path("saidas")
ARQUIVO_LAUDO = PASTA_SAIDAS / "laudo_tecnico.json"
ARQUIVO_TELEMETRIA = PASTA_SAIDAS / "telemetria_real.json"
ARQUIVO_REDE = PASTA_SAIDAS / "rede_local.json"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODELO = os.getenv("OPENAI_MODEL", "openai/gpt-4o").replace("openai/", "")


def carregar_json(caminho):
    if not caminho.exists():
        return {}

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def montar_contexto():
    laudo = carregar_json(ARQUIVO_LAUDO)
    telemetria = carregar_json(ARQUIVO_TELEMETRIA)
    rede = carregar_json(ARQUIVO_REDE)

    return {
        "laudo_tecnico": laudo,
        "telemetria_real": telemetria,
        "rede_local": rede,
    }


def responder_agente(pergunta, agente):
    contexto = montar_contexto()

    if agente == "tecnico":
        papel = """
        Você é um agente técnico de informática.
        Explique o diagnóstico de forma clara para um técnico iniciante.
        Use linguagem didática, objetiva e segura.
        Não invente dados que não estejam no JSON.
        """

    elif agente == "orcamento":
        papel = """
        Você é um agente de orçamento técnico.
        Explique os cenários de orçamento presentes no laudo.
        Mostre o que é preventivo, recomendado e completo.
        Não crie valores novos se eles não estiverem no JSON.
        """

    elif agente == "seguranca":
        papel = """
        Você é um agente de segurança e responsável de TI.
        Explique riscos, cuidados e autorizações necessárias.
        Deixe claro que o aluno não deve alterar o computador sem autorização.
        """

    else:
        papel = """
        Você é um agente professor.
        Explique o projeto para alunos do nono ano, passo a passo,
        com linguagem simples e exemplos.
        """

    mensagem_usuario = f"""
    Dados reais do projeto em JSON:

    {json.dumps(contexto, ensure_ascii=False, indent=2)}

    Pergunta do técnico:
    {pergunta}
    """

    resposta = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": papel},
            {"role": "user", "content": mensagem_usuario},
        ],
        temperature=0.2,
    )

    return resposta.choices[0].message.content


HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Chat com Agentes Técnicos</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #172033;
        }

        header {
            background: linear-gradient(135deg, #0f4c81, #2563eb);
            color: white;
            padding: 28px 40px;
        }

        header h1 {
            margin: 0;
            font-size: 32px;
        }

        header p {
            margin-top: 8px;
            font-size: 18px;
        }

        main {
            max-width: 1000px;
            margin: auto;
            padding: 30px;
        }

        .painel {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        }

        label {
            font-weight: bold;
            color: #0f4c81;
            font-size: 18px;
        }

        select, input, button {
            width: 100%;
            margin-top: 10px;
            margin-bottom: 18px;
            font-size: 18px;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #cbd5e1;
            box-sizing: border-box;
        }

        input {
            height: 52px;
            background: white;
            color: #172033;
        }

        button {
            background: #f97316;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }

        button:hover {
            background: #ea580c;
        }

        .resposta {
            background: #eef6ff;
            border-left: 6px solid #2563eb;
            padding: 20px;
            border-radius: 12px;
            font-size: 18px;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        .exemplos {
            margin-top: 24px;
            background: #fff7ed;
            border-left: 6px solid #f97316;
            padding: 18px;
            border-radius: 12px;
        }

        .exemplos li {
            margin-bottom: 8px;
        }
    </style>
</head>

<body>
    <header>
        <h1>Chat com Agentes Técnicos</h1>
        <p>Converse com agentes de IA usando o laudo real do computador.</p>
    </header>

    <main>
        <div class="painel">
            <label>Escolha o agente:</label>
            <select id="agente">
                <option value="tecnico">Agente Técnico</option>
                <option value="orcamento">Agente de Orçamento</option>
                <option value="seguranca">Agente de Segurança / TI</option>
                <option value="professor">Agente Professor</option>
            </select>

            <label>Digite a pergunta do técnico:</label>
            <input
                id="pergunta"
                type="text"
                placeholder="Exemplo: Por que o disco está em atenção?"
                autocomplete="off"
            >

            <button onclick="enviarPergunta()">Perguntar ao agente</button>

            <h2>Resposta do agente</h2>
            <div id="resposta" class="resposta">
                A resposta aparecerá aqui.
            </div>

            <div class="exemplos">
                <strong>Exemplos de perguntas:</strong>
                <ul>
                    <li>Por que a classificação ficou em ATENÇÃO?</li>
                    <li>O que significa disco com 94% de uso?</li>
                    <li>Qual procedimento o técnico deve fazer primeiro?</li>
                    <li>O que posso explicar para o responsável de TI?</li>
                    <li>Qual orçamento é mais adequado?</li>
                </ul>
            </div>
        </div>
    </main>

    <script>
        async function enviarPergunta() {
            let pergunta = document.getElementById("pergunta").value;
            const agente = document.getElementById("agente").value;
            const resposta = document.getElementById("resposta");

            if (!pergunta.trim()) {
                pergunta = prompt("Digite sua pergunta para o agente:");
            }

            if (!pergunta || !pergunta.trim()) {
                resposta.innerText = "Nenhuma pergunta foi enviada.";
                return;
            }

            resposta.innerText = "O agente está analisando o laudo...";

            const retorno = await fetch("/perguntar", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    pergunta: pergunta,
                    agente: agente
                })
            });

            const dados = await retorno.json();
            resposta.innerText = dados.resposta;
        }
    </script>
</body>
</html>
"""


class ServidorChat(BaseHTTPRequestHandler):
    def do_GET(self):
        rota = urlparse(self.path).path

        if rota == "/" or rota == "/chat":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        rota = urlparse(self.path).path

        if rota == "/perguntar":
            tamanho = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tamanho)

            dados = json.loads(corpo.decode("utf-8"))
            pergunta = dados.get("pergunta", "")
            agente = dados.get("agente", "tecnico")

            try:
                resposta = responder_agente(pergunta, agente)
            except Exception as erro:
                resposta = f"Erro ao consultar o agente: {erro}"

            retorno = json.dumps(
                {"resposta": resposta},
                ensure_ascii=False
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(retorno.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def main():
    if not ARQUIVO_LAUDO.exists():
        print("Erro: o arquivo saidas/laudo_tecnico.json não foi encontrado.")
        print("Execute primeiro: uv run python 05_aplicacao_completa.py")
        return

    endereco = f"http://localhost:{PORTA}/chat"

    print("Chat com agentes iniciado.")
    print(f"Acesse: {endereco}")
    print("Para encerrar, aperte Ctrl + C no terminal.")

    webbrowser.open(endereco)

    servidor = ThreadingHTTPServer(("localhost", PORTA), ServidorChat)
    servidor.serve_forever()


if __name__ == "__main__":
    main()