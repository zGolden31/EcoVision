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
        st.write("Ecco l'isola ecologica più vicina a te:")
        nome_comune = citta.split(",")[0].strip() # Prendiamo solo il nome del comune ; .strip() rimuove eventuali spazi vuoti accidentali)
        url_maps = f"https://www.google.com/maps?q=isola+ecologica+{nome_comune}&output=embed" # Link a Google Maps per l'isola ecologica
        
        # Iframe HTML
        st.markdown(
            f'<iframe src="{url_maps}" width="100%" height="350" style="border-radius:20px; border:1px solid #ddd;" allowfullscreen="" loading="lazy"></iframe>',
            unsafe_allow_html=True
        )
        # SPIEGAZIONE DEL CODICE iframe:
            # f'<iframe '--> Inizio della f-string: serve per inserire variabili Python (come {url_maps}) dentro il testo
            # f'src="{url_maps}" --> Qui inseriamo dinamicamente l'URL che la finestra deve visualizzare
            # [width]: LARGHEZZA. "100%" significa "occupa tutto lo spazio orizzontale disponibile".
            # [height]: ALTEZZA. Fissa l'altezza della mappa a 350 pixel.
            # [style]: STILE CSS. Serve per abbellire il riquadro.
            # "border-radius:20px": Arrotonda gli angoli di 20px per un aspetto più morbido.
            # "border:1px solid #ddd": Crea un bordo sottile grigio chiaro attorno alla mappa.
            # [allowfullscreen]: Piacere utente. Abilita il pulsante nella mappa per aprirla a tutto schermo.
            # [loading]: PERFORMANCE. "lazy" (pigro) significa: "Non caricare la mappa finché l'utente 
            # non scorre la pagina fino a qui". Rende l'avvio dell'app molto più veloce.
            # '</iframe>' Chiusura del tag iframe
            # [unsafe_allow_html]: SICUREZZA. 
            # Di base Streamlit blocca l'HTML per sicurezza. Con "True" forziamo Streamlit 
            # a fidarsi di noi e a disegnare l'iframe invece di scriverlo come testo.

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
        image_file = st.file_uploader("Scegli un'immagine...", type=["jpg", "jpeg", "png", "webp"])
    else:
        image_file = st.camera_input("Scatta una foto al rifiuto")

    # Elaborazione immagine se presente
    if image_file is not None:
        image = Image.open(image_file)
        if option == "Carica file":
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
                        
                    # 1. MATERIALE
                    st.info(f"📦 **Materiale:**\n### {dati_rifiuto['materiale']}")

                    # 2. AZIONE RICHIESTA
                    st.warning(f"⚠️ **Azione richiesta:**\n### {dati_rifiuto['azione']}")

                    # 3. DESTINAZIONE
                    # Logica colori base
                    dest = dati_rifiuto['destinazione'].lower()
                    if "plastica" in dest:
                        # Giallo
                        st.warning(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                    elif "carta" in dest:
                        # Blu
                        st.info(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                    elif "organico" in dest:
                        # Marrone
                        st.success(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}") # Usa un colore diverso se possibile, ma success è ok (verde/marrone)
                    elif "vetro" in dest:
                        # Verde
                        st.success(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                    elif "indifferenziato" in dest:
                        # Grigio
                        st.error(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                    elif "rifiuto speciale" in dest:
                        # Rosso o speciale
                        st.error(f"⚠️ **Rifiuto Speciale:**\n## {dati_rifiuto['destinazione'].upper()}")
                        st.write("Questo rifiuto non va nei bidoni domestici. Portalo all'isola ecologica.")
                    else:
                        st.write(f"🗑️ **Dove buttarlo:**\n## {dati_rifiuto['destinazione'].upper()}")
                    
                    if "rifiuto speciale" in dest or "isola ecologica" in dest:
                        st.write("Ecco l'isola ecologica più vicina a te:")
                        st.markdown(
                            f'<iframe src="{url_maps}" width="100%" height="350" style="border-radius:20px; border:1px solid #ddd;" allowfullscreen="" loading="lazy"></iframe>',
                            unsafe_allow_html=True
                        )

                    # 4. NOTA DELL'ESPERTO
                    st.markdown("---")
                    st.success(f"💡 **Nota dell'esperto:**\n{dati_rifiuto['note']}")

            except Exception as e:
                st.error(f"Si è verificato un errore: {e}")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Gemini & Streamlit")