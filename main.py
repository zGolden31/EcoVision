import streamlit as st              # Framework per la creazione della web app
from PIL import Image               # Manipolazione immagini   
import config                       # Configurazioni della pagina
from geo_loader import carica_dati_geografici, get_city_from_latlon_italian  # Funzioni di caricamento dati geografici
import ai_engine                    # Funzioni di analisi e risposta AI
from streamlit_js_eval import get_geolocation  # Per ottenere la geolocalizzazione dell'utente

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
comuni_italiani = carica_dati_geografici()
citta = None # inizializziamo la variabile città

# 1 GEOLOCALIZZAZIONE AUTOMATICA
# Creiamo un pulsante per chiedere esplicitamente l'azione all'utente
if st.checkbox("📍 Usa la mia posizione attuale per trovare l'isola ecologica"):
    
    # Questa funzione chiama il browser per il permesso GPS
    loc = get_geolocation()

    # Se l'utente ha detto SÌ e il browser ha risposto
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        citta = get_city_from_latlon_italian(lat, lon)
    
        st.success(f"Posizione rilevata! Lat: {lat}, Lon: {lon}, città: {citta}")
        st.info(f"Se la città non è corretta, puoi impostarla manualmente qui sotto")
    else:
        st.warning("In attesa del permesso GPS o segnale debole...")
else:
    st.info("Attiva la spunta sopra per localizzarti.")

# 2 GEOLOCALIZZAZIONE MANUALE (priorità sulla automatica)
# Usiamo un expander per mantenere l'interfaccia pulita
# L'utente può scegliere di inserire la propria posizione per avere indicazioni più precise.
with st.expander("📍 Vuoi trovare l'isola ecologica? **Imposta la tua posizione manualmente**"):
    st.write("Inserisci la tua posizione per ricevere indicazioni personalizzate per lo smaltimento dei rifiuti e per l'isola ecologica più vicina a te.")
    # Usiamo una sola selectbox a larghezza intera per selezionare il comune
    citta_man = st.selectbox(
        "Cerca la tua città",
        options=comuni_italiani,
        index=None,
        placeholder="Scrivi qui il tuo comune (es. Bari)..."
    )

# Conferma visiva dell'inserimento
if citta_man:
    if citta:
        st.info(f"Attenzione: hai già una città rilevata automaticamente: {citta}. La città manuale avrà la priorità.")
        citta = citta_man
    st.success(f"Posizione salvata: {citta_man}")


if citta:    
    url_maps_citta = f"https://www.google.com/maps?q={citta}&output=embed" # Link a Google Maps per città selezionata
    url_maps_isola = f"https://www.google.com/maps?q=isola+ecologica+{citta}&output=embed" # Link a Google Maps per l'isola ecologica
    st.write("Ecco la città in cui ti trovi:")    
    # Iframe HTML
    st.markdown(
        f'<iframe src="{url_maps_citta}" width="100%" height="350" style="border-radius:20px; border:1px solid #ddd;" allowfullscreen="" loading="lazy"></iframe>',
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
                        
                    # Funzione helper per creare box colorati
                    def show_custom_box(label, text, bg_color, text_color="black", icon="", is_small=False):
                        padding = "10px" if is_small else "15px"
                        title_tag = "h6" if is_small else "h5"
                        text_tag = "p" if is_small else "h3" # Use 'p' or 'h4' for smaller text
                        
                        st.markdown(f"""
                        <div style="background-color: {bg_color}; padding: {padding}; border-radius: 10px; margin-bottom: 10px; color: {text_color};">
                            <{title_tag} style="margin:0; color: {text_color}; font-weight: bold;">{icon} {label}</{title_tag}>
                            <{text_tag} style="margin:0; color: {text_color}; font-size: {'1.1em' if is_small else 'inherit'};">{text}</{text_tag}>
                        </div>
                        """, unsafe_allow_html=True)

                    # 1. MATERIALE (Neutro - Light Blue/Grey)
                    show_custom_box("Materiale", dati_rifiuto['materiale'], "#f0f2f6", "black", "📦")

                    # 2. AZIONE RICHIESTA (Neutro o evidenziato leggermente)
                    show_custom_box("Azione richiesta", dati_rifiuto['azione'], "#f0f2f6", "black", "⚠️")

                    # 3. DESTINAZIONE
                    dest = dati_rifiuto['destinazione'].lower()
                    dest_text = dati_rifiuto['destinazione'].upper()
                    
                    if "plastica" in dest:
                        # Giallo
                        show_custom_box("Dove buttarlo", dest_text, "#FFEB3B", "black", "🗑️")
                    elif "carta" in dest:
                        # Blu
                        show_custom_box("Dove buttarlo", dest_text, "#2196F3", "white", "🗑️")
                    elif "organico" in dest or "umido" in dest:
                        # Marrone
                        show_custom_box("Dove buttarlo", dest_text, "#795548", "white", "🗑️")
                    elif "vetro" in dest:
                        # Verde
                        show_custom_box("Dove buttarlo", dest_text, "#4CAF50", "white", "🗑️")
                    elif "indifferenziato" in dest or "secco" in dest:
                        # Grigio
                        show_custom_box("Dove buttarlo", dest_text, "#9E9E9E", "white", "🗑️")
                    elif "rifiuto speciale" in dest:
                        # Rosso
                        warning_text= "Questo rifiuto non va nei bidoni domestici. Portalo all'isola ecologica."
                        show_custom_box("Rifiuto Speciale", warning_text, "#F44336", "white", "⚠️")
                    else:
                        # Default
                        show_custom_box("Dove buttarlo", dest_text, "#f0f2f6", "black", "🗑️")
                    
                    if "rifiuto speciale" in dest or "isola ecologica" in dest:
                        if 'url_maps_isola' in locals() and url_maps_isola:
                            st.write("Ecco l'isola ecologica più vicina a te:")
                            st.markdown(
                                f'<iframe src="{url_maps_isola}" width="100%" height="350" style="border-radius:20px; border:1px solid #ddd;" allowfullscreen="" loading="lazy"></iframe>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning("⚠️ Per vedere l'isola ecologica più vicina, per favore imposta la tua posizione nel box in alto '📍 Vuoi trovare l'isola ecologica?'.")

                    # 4. NOTA DELL'ESPERTO (Neutro)
                    st.markdown("---")
                    show_custom_box("Nota dell'esperto", dati_rifiuto['note'], "#e8f5e9", "#1b5e20", "💡", is_small=True)

            except Exception as e:
                st.error(f"Si è verificato un errore: {e}")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Gemini & Streamlit")