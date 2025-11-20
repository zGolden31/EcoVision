import streamlit as st
from PIL import Image
import os

# --- Configurazione della Pagina ---
st.set_page_config(
    page_title="Assistente Raccolta Differenziata",
    page_icon="♻️",
    layout="centered"
)

# --- Titolo e Introduzione ---
st.title("♻️ Dove lo butto?")
st.markdown("""
Carica una foto di un rifiuto o scattala direttamente. 
L'Intelligenza Artificiale ti dirà **cos'è**, **se devi pulirlo** e **in quale bidone va buttato**.
""")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Gemini & Streamlit")