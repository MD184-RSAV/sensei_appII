import streamlit as st
from openai import OpenAI
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Nihongo Flash", page_icon="📚")

# --- CONNEXION ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- GESTION DU STOCKAGE ---
VOCAB_FILE = "mes_mots.json"

def load_data():
    if os.path.exists(VOCAB_FILE):
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "collection" not in st.session_state:
    st.session_state.collection = load_data()

# --- INTERFACE ---
st.title("📚 Nihongo Flash")
st.write("Gère ton vocabulaire et révise tes flashcards.")

tab1, tab2 = st.tabs(["➕ Ajouter des mots", "🧠 Réviser"])

with tab1:
    st.subheader("Nouveau vocabulaire")
    # Entrée manuelle simplifiée
    new_word = st.text_input("Mot en Japonais (Kanji ou Kana)")
    
    if st.button("Ajouter à ma collection") and new_word:
        with st.spinner("L'IA complète les détails..."):
            try:
                # On demande à l'IA de structurer le mot
                prompt = f"Pour le mot japonais '{new_word}', donne-moi la lecture en Hiragana/Katakana et la traduction française. Réponds uniquement en JSON: {{\"kana\": \"...\", \"fr\": \"...\"}}"
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                details = json.loads(response.choices[0].message.content)
                
                # Sauvegarde
                entry = {"jap": new_word, "kana": details['kana'], "fr": details['fr']}
                st.session_state.collection.append(entry)
                save_data(st.session_state.collection)
                st.success(f"Ajouté : {new_word} ({details['kana']})")
            except:
                st.error("Erreur de connexion.")

with tab2:
    if not st.session_state.collection:
        st.info("Ta collection est vide.")
    else:
        st.write(f"Tu as {len(st.session_state.collection)} mots à réviser.")
        for i, item in enumerate(st.session_state.collection):
            with st.expander(f"🇯🇵 {item['jap']}"):
                st.write(f"**Lecture :** {item['kana']}")
                st.write(f"**Français :** {item['fr']}")
                if st.button("Supprimer", key=f"del_{i}"):
                    st.session_state.collection.pop(i)
                    save_data(st.session_state.collection)
                    st.rerun()
