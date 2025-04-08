from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# Clé OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Prompt système pour GPT
SYSTEM_PROMPT = """
Tu es un conseiller agricole guinéen. Tu aides les agriculteurs à obtenir des conseils simples sur les cultures, les maladies, les prix du marché et la météo en Guinée.
Sois clair et pratique, en t’adressant à un public rural.
"""

@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body', '')
    print("Question reçue :", incoming_msg)

    # Préparer la réponse LLM
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": incoming_msg}
            ],
            temperature=0.7,
            max_tokens=500
        )
        content = response.choices[0].message.content
    except Exception as e:
        content = f"Erreur dans la génération de réponse : {e}"

    # Réponse Twilio
    twilio_response = MessagingResponse()
    twilio_response.message(content)
    return str(twilio_response)

# 🔁 Code compatible Render : bind sur 0.0.0.0 et port dynamique
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
