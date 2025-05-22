import requests

TOKEN = "TOKEN_DO_WPP"
PHONE_ID = "ID_DO_NUMERO"
DESTINATARIO = 'NUMERO_PARA_ENVIAR_O_HELLO_WORLD'

url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
data = {
    "messaging_product": "whatsapp",
    "to": DESTINATARIO,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {"code": "en_US"}
    }
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code, response.text)
