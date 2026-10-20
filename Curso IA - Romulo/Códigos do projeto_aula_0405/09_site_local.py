import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORTA = 8000
PASTA_SAIDAS = Path("saidas")
ARQUIVO_DASHBOARD = PASTA_SAIDAS / "dashboard.html"

def main():
    if not ARQUIVO_DASHBOARD.exists():
        print("Erro: o arquivo saidas/dashboard.html não foi encontrado.")
        print("Execute primeiro: uv run python 08_frontend.py")
        return

    endereco = f"http://localhost:{PORTA}/saidas/dashboard.html"

    print("Site local iniciado.")
    print(f"Acesse: {endereco}")
    print("Para encerrar, volte ao terminal e aperte Ctrl + C.")

    webbrowser.open(endereco)

    servidor = ThreadingHTTPServer(("localhost", PORTA), SimpleHTTPRequestHandler)
    servidor.serve_forever()

if __name__ == "__main__":
    main()