import os
import json
import time
import urllib.request
from pathlib import Path

def carregar_env():
    """Carrega variáveis do arquivo .env manualmente para não depender de pacotes externos."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                linha = line.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    chave, valor = linha.split("=", 1)
                    os.environ.setdefault(chave.strip(), valor.strip())

carregar_env()

token = os.getenv("TELEGRAM_TOKEN")

if not token or token == "seu_token_do_bot_father_aqui":
    print("ERRO: TELEGRAM_TOKEN não configurado no arquivo .env!")
    print("Abra o arquivo .env e adicione seu token obtido no @BotFather.")
    exit(1)

print("=" * 60)
print("  OFICINA DIGITAL - OBTENÇÃO DO ID DO TELEGRAM")
print("=" * 60)
print("1. Abra seu aplicativo do Telegram no celular ou computador.")
print("2. Procure pelo seu Bot e envie qualquer mensagem (ex: /start ou Olá).")
print("3. Aguardando mensagens do Telegram...")
print("=" * 60)

offset = None

while True:
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=10"
        if offset:
            url += f"&offset={offset}"
            
        req = urllib.request.Request(url, headers={"User-Agent": "OficinaDigitalBot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
            
        if dados.get("ok"):
            for update in dados.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message") or update.get("channel_post")
                if msg:
                    chat = msg.get("chat", {})
                    chat_id = chat.get("id")
                    nome = chat.get("first_name", "Usuário")
                    texto = msg.get("text", "")
                    
                    print(f"\n>>> MENSAGEM RECEBIDA!")
                    print(f"Nome do remetente : {nome}")
                    print(f"Número do Chat ID : {chat_id}  <--- COPIE ESTE NÚMERO!")
                    print(f"Texto enviado     : {texto}")
                    print(f"Salve este número no .env como TELEGRAM_CHAT_ID={chat_id}\n")
    except Exception as e:
        print(f"Aviso na comunicação: {e}")
        time.sleep(3)
        
    time.sleep(1)
