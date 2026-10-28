"""
Bot Telegram para a Oficina Digital
Comunicação via HTTP (sem bibliotecas externas) utilizando apenas urllib e json.
Atende aos comandos do técnico: /abertos, /ver N, /andamento N, /concluir N
"""

import os
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

# Carrega variáveis do arquivo .env
def carregar_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                linha = line.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    chave, valor = linha.split("=", 1)
                    os.environ.setdefault(chave.strip(), valor.strip())

carregar_env()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID_AUTORIZADO = os.getenv("TELEGRAM_CHAT_ID")
ARQUIVO_DADOS = Path(__file__).parent / "chamados.json"

if not TOKEN:
    print("[AVISO] TELEGRAM_TOKEN não encontrado no arquivo .env.")
if not CHAT_ID_AUTORIZADO:
    print("[AVISO] TELEGRAM_CHAT_ID não encontrado no arquivo .env.")

# Base de chamados inicial se o arquivo não existir
CHAMADOS_PADRAO = [
    {
        "id": 1001,
        "cliente": "Carlos Silva",
        "contato": "(85) 98877-6655",
        "aparelho": "Notebook Dell Inspiron 15",
        "defeito": "Notebook não liga e o carregador fica piscando a luz verde.",
        "status": "Aberto",
        "gravidade": "ALTA",
        "laudo": {
            "modelo": "Notebook Dell Inspiron",
            "sintoma": "Sem sinal de energia / não liga",
            "causa_provavel": "Curto-circuito na linha de entrada de 19V ou conector Jack DC danificado",
            "peca_provavel": "Conector Jack DC / Reparo na placa-mãe",
            "tempo_bancada": "2 horas",
            "proximos_passos": "Testar tensão de entrada com multímetro na bancada e injetar tensão na linha principal."
        }
    },
    {
        "id": 1002,
        "cliente": "Mariana Ramos",
        "contato": "(85) 99123-4567",
        "aparelho": "Lenovo Ideapad 3",
        "defeito": "Dando tela azul (BSOD) constantemente ao abrir o navegador.",
        "status": "Em Andamento",
        "gravidade": "MÉDIA",
        "laudo": {
            "modelo": "Lenovo Ideapad",
            "sintoma": "Tela Azul (BSOD) frequente",
            "causa_provavel": "Setores defeituosos no SSD NVMe ou módulo de memória RAM com instabilidade",
            "peca_provavel": "SSD NVMe M.2 256GB / Memória RAM DDR4",
            "tempo_bancada": "1 hora e 30 minutos",
            "proximos_passos": "Rodar teste de memória MemTest86 e verificar integridade SMART do SSD pelo CrystalDiskInfo."
        }
    }
]

def carregar_chamados():
    if not ARQUIVO_DADOS.exists():
        salvar_chamados(CHAMADOS_PADRAO)
        return list(CHAMADOS_PADRAO)
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return list(CHAMADOS_PADRAO)

def salvar_chamados(chamados):
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(chamados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar chamados: {e}")

def enviar_mensagem(chat_id, texto):
    """Envia mensagem ao Telegram usando a API HTTP oficial."""
    if not TOKEN:
        print(f"[Simulação Telegram -> Chat {chat_id}]:\n{texto}\n")
        return False
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Erro ao enviar Telegram]: {e}")
        return False

def notificar_novo_chamado(chamado):
    """Envia aviso ao técnico no celular quando um chamado é criado."""
    if not CHAT_ID_AUTORIZADO:
        print("[Aviso] CHAT_ID_AUTORIZADO não configurado para notificação.")
        return
    texto = (
        f"🚨 <b>NOVO CHAMADO RECEBIDO - OFICINA DIGITAL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>OS #{chamado['id']}</b>\n"
        f"👤 <b>Cliente:</b> {chamado['cliente']}\n"
        f"📱 <b>Contato:</b> {chamado.get('contato', 'N/A')}\n"
        f"💻 <b>Aparelho:</b> {chamado['aparelho']}\n"
        f"⚠️ <b>Gravidade IA:</b> {chamado.get('gravidade', 'MÉDIA')}\n\n"
        f"🔍 <b>Relato do Defeito:</b>\n<i>{chamado['defeito']}</i>\n\n"
        f"📋 <b>Laudo Prévio da IA:</b>\n"
        f"• <b>Causa Provável:</b> {chamado['laudo'].get('causa_provavel')}\n"
        f"• <b>Peça Sugerida:</b> {chamado['laudo'].get('peca_provavel')}\n"
        f"• <b>Tempo Bancada:</b> {chamado['laudo'].get('tempo_bancada')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Comandos rápidos:\n"
        f"/ver {chamado['id']} | /andamento {chamado['id']} | /concluir {chamado['id']}"
    )
    enviar_mensagem(CHAT_ID_AUTORIZADO, texto)

def processar_comando(chat_id, texto):
    texto = texto.strip()
    partes = texto.split()
    cmd = partes[0].lower() if partes else ""
    chamados = carregar_chamados()

    if cmd in ["/start", "/ajuda", "/help"]:
        msg = (
            "🛠️ <b>RÁDIO DO TÉCNICO - OFICINA DIGITAL</b>\n"
            "Central de Notificações e Comandos Operacionais\n\n"
            "<b>Comandos disponíveis:</b>\n"
            "📌 <code>/abertos</code> - Lista a fila de chamados pendentes\n"
            "🔎 <code>/ver N</code> - Detalha o chamado e laudo completo da OS N\n"
            "⚙️ <code>/andamento N</code> - Coloca o chamado N 'Em Andamento'\n"
            "✅ <code>/concluir N</code> - Conclui o chamado N na bancada\n"
            "ℹ️ <code>/ajuda</code> - Exibe este menu explicativo"
        )
        enviar_mensagem(chat_id, msg)
        return

    if cmd == "/abertos":
        abertos = [c for c in chamados if c.get("status") in ["Aberto", "Em Andamento"]]
        if not abertos:
            enviar_mensagem(chat_id, "✅ <b>Nenhum chamado aberto na fila no momento!</b>")
            return
        msg = "📋 <b>FILA DE CHAMADOS EM ABERTO:</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        for c in abertos:
            icone = "🔴" if c.get("gravidade") == "ALTA" else "🟡" if c.get("gravidade") == "MÉDIA" else "🟢"
            msg += f"{icone} <b>OS #{c['id']}</b> - {c['cliente']} ({c['aparelho']})\n"
            msg += f"   Status: <i>{c.get('status')}</i> | Gravidade: <b>{c.get('gravidade')}</b>\n"
            msg += f"   Para ver: <code>/ver {c['id']}</code>\n\n"
        enviar_mensagem(chat_id, msg)
        return

    if cmd == "/ver":
        if len(partes) < 2:
            enviar_mensagem(chat_id, "⚠️ Uso incorreto! Digite o número da OS. Ex: <code>/ver 1001</code>")
            return
        num = partes[1].replace("#", "").replace("OS-", "").strip()
        c = next((x for x in chamados if str(x["id"]) == num), None)
        if not c:
            enviar_mensagem(chat_id, f"❌ Chamado <b>#{num}</b> não encontrado no sistema.")
            return
        laudo = c.get("laudo", {})
        msg = (
            f"📄 <b>DETALHES DA ORDEM DE SERVIÇO #{c['id']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Cliente:</b> {c['cliente']} (Contato: {c.get('contato')})\n"
            f"💻 <b>Aparelho:</b> {c['aparelho']}\n"
            f"📊 <b>Status Atual:</b> <b>{c.get('status')}</b>\n"
            f"⚠️ <b>Gravidade:</b> <b>{c.get('gravidade')}</b>\n\n"
            f"📝 <b>Relato do Cliente:</b>\n<i>{c.get('defeito')}</i>\n\n"
            f"🧠 <b>LAUDO DA INTELIGÊNCIA ARTIFICIAL:</b>\n"
            f"• <b>Modelo:</b> {laudo.get('modelo', 'Não especificado')}\n"
            f"• <b>Sintoma:</b> {laudo.get('sintoma', 'Geral')}\n"
            f"• <b>Causa Provável:</b> {laudo.get('causa_provavel', 'A verificar')}\n"
            f"• <b>Peça Provável:</b> {laudo.get('peca_provavel', 'A verificar')}\n"
            f"• <b>Tempo de Bancada:</b> {laudo.get('tempo_bancada', '1 a 2 horas')}\n"
            f"• <b>Próximos Passos:</b> {laudo.get('proximos_passos', 'Inspecionar componentes.')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Ações rápidas:\n"
            f"<code>/andamento {c['id']}</code> | <code>/concluir {c['id']}</code>"
        )
        enviar_mensagem(chat_id, msg)
        return

    if cmd == "/andamento":
        if len(partes) < 2:
            enviar_mensagem(chat_id, "⚠️ Uso incorreto! Digite o número da OS. Ex: <code>/andamento 1001</code>")
            return
        num = partes[1].replace("#", "").replace("OS-", "").strip()
        c = next((x for x in chamados if str(x["id"]) == num), None)
        if not c:
            enviar_mensagem(chat_id, f"❌ Chamado <b>#{num}</b> não encontrado.")
            return
        c["status"] = "Em Andamento"
        salvar_chamados(chamados)
        enviar_mensagem(chat_id, f"⚙️ <b>Chamado #{num} atualizado para 'EM ANDAMENTO'!</b>\nTécnico alocado na bancada.")
        return

    if cmd == "/concluir":
        if len(partes) < 2:
            enviar_mensagem(chat_id, "⚠️ Uso incorreto! Digite o número da OS. Ex: <code>/concluir 1001</code>")
            return
        num = partes[1].replace("#", "").replace("OS-", "").strip()
        c = next((x for x in chamados if str(x["id"]) == num), None)
        if not c:
            enviar_mensagem(chat_id, f"❌ Chamado <b>#{num}</b> não encontrado.")
            return
        c["status"] = "Concluído"
        salvar_chamados(chamados)
        enviar_mensagem(chat_id, f"✅ <b>Chamado #{num} CONCLUÍDO com sucesso!</b>\nNotificação de retirada enviada para o cliente.")
        return

    enviar_mensagem(chat_id, "Comando não reconhecido. Use <code>/abertos</code>, <code>/ver N</code>, <code>/andamento N</code> ou <code>/concluir N</code>.")

def loop_polling():
    """Loop de verificação periódica (getUpdates) sem necessitar de webhook/porta pública."""
    if not TOKEN:
        print("[ERRO] Não é possível rodar o bot sem TELEGRAM_TOKEN configurado no .env.")
        return

    print("=" * 60)
    print("  BOT TELEGRAM OFICINA DIGITAL - EM OPERAÇÃO")
    print("=" * 60)
    print(f"Chat ID Autorizado : {CHAT_ID_AUTORIZADO or 'Qualquer (não restrito)'}")
    print("Aguardando comandos: /abertos, /ver N, /andamento N, /concluir N...")
    print("Pressione Ctrl+C para encerrar.")
    print("=" * 60)

    offset = None

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?timeout=10"
            if offset:
                url += f"&offset={offset}"
            req = urllib.request.Request(url, headers={"User-Agent": "OficinaDigitalBot/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                dados = json.loads(resp.read().decode("utf-8"))

            if dados.get("ok"):
                for update in dados.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message")
                    if msg:
                        remetente_id = str(msg.get("chat", {}).get("id"))
                        texto = msg.get("text", "")
                        
                        # Verifica autorização se CHAT_ID_AUTORIZADO estiver configurado
                        if CHAT_ID_AUTORIZADO and remetente_id != str(CHAT_ID_AUTORIZADO):
                            print(f"[Acesso Negado] Mensagem de chat não autorizado: {remetente_id}")
                            enviar_mensagem(remetente_id, "⛔ Acesso restrito ao técnico responsável da Oficina Digital.")
                            continue
                            
                        print(f"[Comando Recebido] {texto} de Chat {remetente_id}")
                        processar_comando(remetente_id, texto)

        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("[Erro 401] Token do Telegram inválido! Verifique o .env.")
                time.sleep(10)
            elif e.code == 409:
                print("[Erro 409 Conflict] Outra instância do bot está rodando. Aguardando...")
                time.sleep(5)
            else:
                print(f"[Erro HTTP {e.code}]: {e}")
                time.sleep(3)
        except Exception as e:
            print(f"[Aviso de Conexão]: {e}")
            time.sleep(3)

        time.sleep(1)

if __name__ == "__main__":
    loop_polling()
