import streamlit as st              # Framework per la creazione della web app
from PIL import Image               # Manipolazione immagini   
import config                       # Configurazioni della pagina
import geo_loader                   # Funzioni di caricamento dati geografici
import ai_engine                    # Funzioni di analisi e risposta AI

# CONFIFGURAZIONE PAGINA
config.configura_pagina()

# INTESTAZIONE E UI PRINCIPALE
st.title("♻️ EcoVision: dove si butta?") # Titolo principale
st.markdown("""
Carica una foto di un rifiuto o scattala direttamente. 
L'Intelligenza Artificiale ti dirà **cos'è**, **se devi pulirlo** e **in quale bidone va buttato**.
""") # Descrizione in markdown

# CONFIGURAZIONE CONTESTO UTENTE (GEOLOCALIZZAZIONE)
# Carichiamo i dati PRIMA di disegnare l'interfaccia
comuni_italiani = geo_loader.carica_dati_geografici()

# Usiamo un expander per mantenere l'interfaccia pulita
# L'utente può scegliere di inserire la propria posizione per avere indicazioni più precise.
with st.expander("📍 Vuoi trovare l'isola ecologica? **Imposta la tua posizione**"):
    st.write("Inserisci la tua posizione per ricevere indicazioni personalizzate per lo smaltimento dei rifiuti e per l'isola ecologica più vicina a te.")
    
    # Usiamo una sola selectbox a larghezza intera per selezionare il comune
    citta = st.selectbox(
        "Cerca la tua città",
        options=comuni_italiani,
        index=None,
        placeholder="Scrivi qui il tuo comune (es. Bari)..."
    )
    # Conferma visiva dell'inserimento
    if citta:
        st.success(f"Posizione salvata: {citta}")
        # In futuro qui genereremo il link a Google Maps

# GESTIONE SICUREZZA E AUTENTICAZIONE API KEY
api_key = None
try:
    # Recupero chiave dai 'secrets' di Streamlit
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except Exception as e:
    st.warning("Chiave API non trovata nelle configurazioni segrete.")
    # Se non trovata, chiediamo all'utente di inserirla manualmente
    api_key = st.text_input("Inserisci manualmente la tua Google API Key:", type="password")

# ACQUISIZIONE IMMAGINE E LOGICA AI
if api_key:
    # Selezione metodo di input (Upload file e Fotocamera)
    option = st.radio("Come vuoi caricare l'immagine?", ("Carica file", "Scatta foto"))
    image_file = None

    if option == "Carica file":
        image_file = st.file_uploader("Scegli un'immagine...", type=["jpg", "jpeg", "png"])
    else:
        image_file = st.camera_input("Scatta una foto al rifiuto")

    # Elaborazione immagine se presente
    if image_file is not None:
        image = Image.open(image_file)
        st.image(image, caption="Immagine caricata", use_container_width=True)

        # Logica del bottone di analisi
        if st.button("Analizza Rifiuto 🔍"):
            try:
                # Chiamata alla funzione di analisi AI
                dati_rifiuto = ai_engine.analizza_immagine(image, api_key, citta)

                # VISUALIZZAZIONE RISULTATI
                # Se non è stato identificato
                if dati_rifiuto["destinazione"] == "Non identificato":
                    st.warning("⚠️ Non sono riuscito a capire di che oggetto si tratta. Prova con una foto più chiara.")
                    # Se l'oggetto è identificato correttamente, mostriamo i dettagli
                else:
                    st.success("Analisi completata!")
                    st.subheader(f"Oggetto: {dati_rifiuto['oggetto']}")
                        
                    col1, col2 = st.columns(2)
                    
                    # Colonna sinistra: Dettagli tecnici
                    with col1:
                        st.info(f"**Materiale:**\n{dati_rifiuto['materiale']}")
                        st.write(f"**Azione richiesta:**\n{dati_rifiuto['azione']}")
                    # Colonna destra: Indicazioni di smaltimento
                    with col2:
                        # Logica colori base
                        # Imposta il colore del box (Giallo, Blu, Verde, Rosso) in base al tipo di rifiuto per richiamare i bidoni reali.
                        dest = dati_rifiuto['destinazione'].lower()
                        if "plastica" in dest:
                            # Giallo
                            st.warning(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                        elif "carta" in dest:
                            # Blu
                            st.info(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                        elif "umido" in dest or "organico" in dest:
                            # Marrone
                            st.success(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                        else:
                            # Grigio
                            st.error(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                        
                    # Note in basso
                    st.markdown("---")
                    st.caption(f"💡 **Nota dell'esperto:** {dati_rifiuto['note']}")

            except Exception as e:
                st.error(f"Si è verificato un errore: {e}")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Gemini & Streamlit")