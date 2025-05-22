import openai

# Substitua pela sua chave real da OpenAI
openai.api_key = "TOKRN_DO_GPT  "

def consultar_chatgpt(descricao, categoria):
    prompt = f"""
    Você é um atendente técnico de suporte. Um usuário relatou o seguinte problema na categoria '{categoria}':

    "{descricao}"

    Responda de forma educada, objetiva e útil. Se não for possível resolver, diga: \"Encaminharemos sua solicitação para um profissional especializado.\".
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de suporte técnico."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.5
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print("Erro ao consultar ChatGPT:", e)
        return "Encaminharemos sua solicitação para um profissional especializado."
