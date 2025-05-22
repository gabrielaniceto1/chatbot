'''from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "TOKEN_DO_WPP"
PHONE_ID = "ID_DO_NUMERO"

def enviar_mensagem(numero, mensagem):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensagem}
    }
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code, response.text)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        mensagens = data["entry"][0]["changes"][0]["value"]["messages"]
        if mensagens:
            mensagem = mensagens[0]
            numero = mensagem["from"]
            texto = mensagem["text"]["body"]
            print(f"Recebido de {numero}: {texto}")
            enviar_mensagem(numero, f"Você disse: {texto}")
    except Exception as e:
        print("Erro:", e)
    return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)
'''

import requests
from flask import Flask, request
from database import iniciar_banco, salvar_etapa, atualizar_atendimento, gerar_protocolo
from chatgpt import consultar_chatgpt

app = Flask(__name__)
TOKEN = "TOKEN_DO_WPP"
PHONE_ID = "ID_DO_NUMERO"

# Inicializa o banco de dados ao iniciar o app
iniciar_banco()

usuarios = {}

@app.route("/webhook", methods=["GET"])
def verificar():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == "meu_token_seguro":
        return challenge
    return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        mensagens = data["entry"][0]["changes"][0]["value"].get("messages")
        if mensagens:
            mensagem = mensagens[0]
            numero = mensagem["from"]
            texto = mensagem["text"]["body"].strip()

            etapa = usuarios.get(numero, {}).get("etapa", 0)
            if etapa == 0:
                usuarios[numero] = {"etapa": 1, "dados": {}}
                return responder(numero, "Olá! Para iniciarmos, informe o nome da prefeitura onde você trabalha.")

            elif etapa == 1:
                usuarios[numero]["dados"]["prefeitura"] = texto
                usuarios[numero]["etapa"] = 2
                return responder(numero, "Qual hospital você representa?")

            elif etapa == 2:
                usuarios[numero]["dados"]["hospital"] = texto
                usuarios[numero]["etapa"] = 3
                return responder(numero, "Qual o setor?")

            elif etapa == 3:
                usuarios[numero]["dados"]["setor"] = texto
                usuarios[numero]["etapa"] = 4
                return responder(numero, "Informe seu nome completo.")

            elif etapa == 4:
                usuarios[numero]["dados"]["nome"] = texto
                usuarios[numero]["etapa"] = 5
                return responder(numero, "Informe seu e-mail ou matrícula (identificação interna).")

            elif etapa == 5:
                usuarios[numero]["dados"]["identificacao"] = texto
                usuarios[numero]["etapa"] = 6
                return responder(numero, "Obrigado. Qual é o tipo de problema?\n1. Computador\n2. Sistema\n3. Impressora\n4. Outro (digite o problema)")

            elif etapa == 6:
                categorias = {"1": "Computador", "2": "Sistema", "3": "Impressora"}
                categoria = categorias.get(texto, texto)
                usuarios[numero]["dados"]["problema"] = categoria
                usuarios[numero]["etapa"] = 7
                return responder(numero, "Descreva o problema com mais detalhes, por favor.")

            elif etapa == 7:
                usuarios[numero]["dados"]["descricao"] = texto
                dados = usuarios[numero]["dados"]
                resposta = consultar_chatgpt(dados["descricao"], dados["problema"])
                protocolo = gerar_protocolo()
                salvar_etapa(numero, dados, resposta, protocolo, encaminhado=False)
                usuarios[numero]["etapa"] = 8
                return responder(numero, f"Protocolo: {protocolo}\n{resposta}\n\nPosso te ajudar com mais alguma coisa? (sim/não)")

            elif etapa == 8:
                if texto.lower() in ["não", "nao"]:
                    usuarios.pop(numero)
                    return responder(numero, "Ok! Ficamos à disposição. Tenha um ótimo dia!")
                else:
                    protocolo = gerar_protocolo()
                    atualizar_atendimento(numero, protocolo)
                    usuarios.pop(numero)
                    return responder(numero, f"Sentimos muito. Encaminharemos sua solicitação para um profissional responsável.\nNovo protocolo: {protocolo}")

    except Exception as e:
        print("Erro no webhook:", e)
    return "ok", 200


def responder(numero, mensagem):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensagem}
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code} | Resposta: {response.text}")
    return "ok", 200


if __name__ == "__main__":
    app.run(port=5000)
