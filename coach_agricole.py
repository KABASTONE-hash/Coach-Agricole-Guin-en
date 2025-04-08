import streamlit as st
import openai
import os
import json
from PIL import Image

# Chargement des données JSON
def charger_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

prix_data = charger_json("data/marches.json")
meteo_data = charger_json("data/meteo.json")

# Configuration API
openai.api_key = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else os.getenv("OPENAI_API_KEY")

# Page config
st.set_page_config(page_title="Coach Agricole Guinéen", page_icon="🌿")

# Logo
if os.path.exists("image.png"):
    image = Image.open("image.png")
    st.image(image, width=200)

# Titre
st.markdown("<h1 style='text-align: center;'>🌾 Coach Agricole Guinéen</h1>", unsafe_allow_html=True)
st.write("Pose ta question sur une culture, une maladie ou les prix du marché. Tu recevras des conseils agricoles adaptés à la Guinée.")

# Choix culture et région
culture = st.selectbox("🌱 Choisis ta culture :", list(prix_data.keys()))
ville = st.selectbox("📍 Dans quelle région ?", list(prix_data[culture].keys()))

# Zone de texte
question = st.text_area("❓ Pose ta question agricole :", placeholder="Ex : Ma plante jaunit, que faire ?")
go = st.button("🧠 Obtenir un conseil")

# Liste de pays non autorisés
pays_non_autorises = [
    "france", "canada", "sénégal", "mali", "côte d’ivoire", "usa", "paris", "dakar",
    "bamako", "abidjan", "new york", "bruxelles", "casablanca", "maroc"
]

# Prompt système
SYSTEM_PROMPT = """
Tu es un conseiller agricole guinéen. Tu aides les petits agriculteurs à améliorer leurs cultures.
Tu fournis des conseils selon la région, le climat, les maladies fréquentes, les produits accessibles et les prix du marché.

Sois simple, pratique et compréhensible.
"""

# Traitement
if go and question.strip():
    question_clean = question.lower()

    if any(pays in question_clean for pays in pays_non_autorises):
        st.warning("🚫 Ce coach est uniquement destiné à la République de Guinée.")
    else:
        prix = prix_data.get(culture, {}).get(ville)
        meteo = meteo_data.get(ville, {})

        full_question = f"{question.strip()} (Culture : {culture}, Région : {ville})"
        with st.spinner("Consultation du conseiller agricole…"):
            try:
                client = openai.OpenAI()
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": full_question}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                answer = response.choices[0].message.content
                st.success("Voici ton conseil 👇")
                st.markdown(answer)

                if prix:
                    st.info(f"💰 Prix estimé à {ville} pour {culture.lower()} : **{prix:,} GNF le sac**")
                if meteo:
                    st.info(f"🌦️ Météo à {ville} : {meteo['météo']} | Humidité : {meteo['humidité']} | Pluie : {meteo['prochaine_pluie']}")

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
else:
    st.info("Remplis tous les champs pour recevoir un conseil agricole.")
