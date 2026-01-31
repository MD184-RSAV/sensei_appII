import streamlit as st
from openai import OpenAI
import json
import os
import random

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="Nihongo Flash", page_icon="📚")
st.markdown("""
    <style>
    .card {
        border: 2px solid #f0f2f6;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        background-color: #ffffff;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .kanji { font-size: 50px; font-weight: bold; color: #2e3136; }
    </style>
""", unsafe_allow_html=True)

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

tab1, tab2 = st.tabs(["➕ Ajouter", "🧠 Mode Flashcards"])

with tab1:
    st.subheader("Ajouter un mot")
    new_word = st.text_input("Mot en Japonais", placeholder="Ex: 猫 ou 食べる")
    
    if st.button("Enregistrer") and new_word:
        with st.spinner("L'IA prépare la carte..."):
            try:
                prompt = f"Pour '{new_word}', donne la lecture (Kana) et la traduction (Français). Réponds en JSON : {{\"kana\": \"...\", \"fr\": \"...\"}}"
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                details = json.loads(response.choices[0].message.content)
                entry = {"jap": new_word, "kana": details['kana'], "fr": details['fr']}
                st.session_state.collection.append(entry)
                save_data(st.session_state.collection)
                st.success(f"Ajouté : {new_word} !")
            except:
                st.error("Erreur de connexion.")

    st.write("---")
    st.write(f"Ma bibliothèque : {len(st.session_state.collection)} mots")

with tab2:
    if not st.session_state.collection:
        st.info("Ajoute des mots pour commencer à réviser.")
    else:
        # Mélanger les mots pour la session
        if "session_index" not in st.session_state:
            st.session_state.session_index = 0
            random.shuffle(st.session_state.collection)
            st.session_state.show_answer = False

        idx = st.session_state.session_index % len(st.session_state.collection)
        carte_actuelle = st.session_state.collection[idx]

        # --- AFFICHAGE DE LA CARTE ---
        st.write(f"Carte {idx + 1} / {len(st.session_state.collection)}")
        
        # Le Recto (Design CSS)
        st.markdown(f"""
            <div class="card">
                <div class="kanji">{carte_actuelle['jap']}</div>
            </div>
        """, unsafe_allow_html=True)

        # Bouton pour révéler
        if not st.session_state.show_answer:
            if st.button("👁️ Voir la réponse", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
        else:
            # Le Verso
            st.success(f"**Lecture :** {carte_actuelle['kana']}")
            st.info(f"**Traduction :** {carte_actuelle['fr']}")
            
            if st.button("Suivant ➡️", use_container_width=True):
                st.session_state.session_index += 1
                st.session_state.show_answer = False
                st.rerun()

        st.write("---")
        if st.button("🗑️ Vider la bibliothèque"):
            st.session_state.collection = []
            save_data([])
            st.rerun()
