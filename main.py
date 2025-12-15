import streamlit as st              # Framework per la creazione della web app
from PIL import Image               # Manipolazione immagini   
import config                    # Configurazioni della pagina
from geo_loader import carica_dati_geografici, get_city_from_latlon_italian, disattiva_gps, disattiva_selezioneman  # Funzioni di caricamento dati geografici
import ai_engine                    # Funzioni di analisi e risposta AI
from streamlit_js_eval import get_geolocation  # Per ottenere la geolocalizzazione dell'utente

# --- CONFIFGURAZIONE PAGINA ---
config.configura_pagina()

# Mappatura dei colori e icone per i bidoni
CONFIG_BIDONI = {
    "plastica":        {"bg": "#FFEB3B", "text": "black", "icon": "./icons/yellow.png"},
    "carta":           {"bg": "#2196F3", "text": "white", "icon": "./icons/blue.png"},
    "cartone":         {"bg": "#2196F3", "text": "white", "icon": "./icons/blue.png"},
    "organico":        {"bg": "#795548", "text": "white", "icon": "./icons/brown.png"},
    "umido":           {"bg": "#795548", "text": "white", "icon": "./icons/brown.png"},
    "vetro":           {"bg": "#4CAF50", "text": "white", "icon": "./icons/green.png"},
    "indifferenziato": {"bg": "#9E9E9E", "text": "white", "icon": "./icons/grey.png"},
    "secco":           {"bg": "#9E9E9E", "text": "white", "icon": "./icons/grey.png"},
    "rifiuto speciale": {"bg": "#F44336", "text": "white", "icon": "./icons/red.png"},
    "raee":            {"bg": "#F44336", "text": "white", "icon": "./icons/red.png"}
}
# Stile di default per i bidoni
DEFAULT_STYLE = {"bg": "#f0f2f6", "text": "black", "icon": "./icons/grey.png"}

# Funzioni di utilità e interfaccia

def show_custom_box(label, text, bg_color, text_color="black", icon="", is_small=False):
    """
    Renderizza un box colorato con stile HTML.
    """
    # Configurazione dimensioni e tag
    padding = "10px" if is_small else "15px"
    title_tag = "h6" if is_small else "h5"
    text_tag = "p" if is_small else "h3"
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: {padding}; border-radius: 10px; margin-bottom: 10px; color: {text_color};">
        <{title_tag} style="margin:0; color: {text_color}; font-weight: bold;">{icon} {label}</{title_tag}>
        <{text_tag} style="margin:0; color: {text_color}; font-size: {'1.1em' if is_small else 'inherit'};">{text}</{text_tag}>
    </div>
    """, unsafe_allow_html=True)

def mostra_mappa(citta, tipo_mappa=0):
    """
    Mostra la mappa tramite Google Maps
    tipo_mappa: 0 per città generica, 1 per ricerca 'isola ecologica'    
    """
    if not citta:
        return
    url_maps = f"http://googleusercontent.com/maps.google.com/{tipo_mappa}{citta}&output=embed"
    st.markdown(
        f"<iframe src='{url_maps}' width='100%' height='350' style='border-radius:20px; border:1px solid #ddd;' allowfullscreen='' loading='lazy'></iframe>", 
        unsafe_allow_html=True
        )

# INTESTAZIONE E UI PRINCIPALE
st.title("♻️ EcoVision: dove si butta?")
st.markdown("""
Carica una foto di un rifiuto o scattala direttamente. 
L'Intelligenza Artificiale ti dirà **cos'è**, **se devi pulirlo** e **in quale bidone va buttato**.
""")
# Mostra la legenda dei bidoni
config.mostra_legenda_bidoni() 


# --- CONFIGURAZIONE GEOLOCALIZZAZIONE ---
comuni_italiani = carica_dati_geografici()
citta = None # inizializziamo la variabile città

# Checkbox per GPS (disattiva la selezione manuale) 
usa_gps = st.checkbox("📍 Usa la mia posizione attuale per trovare l'isola ecologica", key="usa_gps", on_change=disattiva_selezioneman)


if usa_gps:
    # Questa funzione chiama il browser per il permesso GPS
    loc = get_geolocation()

    # Se l'utente ha detto SÌ e il browser ha risposto
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        citta = get_city_from_latlon_italian(lat, lon)
        st.success(f"Posizione rilevata: {citta}")
    else:
        st.warning("In attesa del permesso GPS o segnale debole...")
else:
    st.info("Attiva la spunta sopra per localizzarti automaticamente")

# 2 GEOLOCALIZZAZIONE MANUALE (priorità sulla automatica)

with st.expander("📍 Imposta la città manualmente"):
    citta_man = st.selectbox(
        "Cerca la tua città",
        options=comuni_italiani,
        index=None,
        placeholder="Scrivi qui il tuo comune (es. Bari)...",
        key="select_citta_manuale",
        # Disattiviamo il GPS se l'utente seleziona manualmente la città
        on_change=disattiva_gps 
    )

# Se la città è stata selezionata manualmente, la salviamo
if citta:
    citta = citta_man
    st.success(f"Posizione salvata: {citta}")

# Mostra mappa della città corrente (solo se definita)
if citta:    
    st.write("Ecco la città in cui ti trovi:")
    mostra_mappa(citta,0) # tipo_mappa=0 per mappa standard

# Linea di separazione
st.markdown("---") 


# --- GESTIONE SICUREZZA E AUTENTICAZIONE API KEY ---
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.warning("Chiave API non trovata.")
    api_key = st.text_input("Inserisci manualmente la tua Google API Key:", type="password")

# --- LOGICA DI INPUT E ANALISI ---
if api_key:
    # Selezione metodo di input (Upload file e Fotocamera)
    option = st.radio("Come vuoi caricare l'immagine?", ("Carica file", "Scatta foto"), horizontal=True, label_visibility="collapsed")
    
    image_file = None
    if option == "Carica file":
        image_file = st.file_uploader("Scegli un'immagine...", type=["jpg", "jpeg", "png", "webp"])
    else:
        image_file = st.camera_input("Scatta una foto")

    # Elaborazione immagine se presente
    if image_file is not None:
        image = Image.open(image_file)
        if option == "Carica file":
            st.image(image, caption="Immagine caricata", use_container_width=True)


        # Logica del bottone di analisi
        if st.button("Analizza Rifiuto 🔍", use_container_width=True):
            try:
                # Chiamata alla funzione di analisi AI
                st.session_state.analysis_result = ai_engine.analizza_immagine(image, api_key, citta)
                # Resetta la chat quando si analizza un nuovo oggetto
                st.session_state.chat_history = [] 
            except Exception as e:
                st.error(f"Si è verificato un errore durante l'analisi: {e}")

        # --- VISUALIZZAZIONE RISULTATI ---
        if "analysis_result" in st.session_state:
            dati = st.session_state.analysis_result
            
            # Se non è stato identificato (controlliamo il primo componente)
            if not dati.get("componenti") or dati["componenti"][0]["destinazione"] == "Non identificato":
                st.warning("⚠️ Non sono riuscito a capire di che oggetto si tratta. Prova con una foto più chiara.")
            else:
                st.subheader(f"Oggetto: {dati.get('oggetto_principale', 'Sconosciuto')}")
                    
                # Info materiale
                if dati.get('materiali'):
                    show_custom_box("Materiali", dati['materiali'], "#f0f2f6", "black", "📦")

                # Info azione
                if dati.get('azione'):
                    show_custom_box("Azione richiesta", dati['azione'], "#f0f2f6", "black", "⚠️")

                st.markdown("---")

                # ITERAZIONE SUI COMPONENTI 
                flag_rifiuto_speciale = False # Flag per tracciare se mostrare la mappa DOPO il ciclo
                
                for comp in dati['componenti']:
                    nome_comp = comp['nome']
                    destinazione = comp['destinazione'].lower()
                    dest_display = comp['destinazione'].upper()

                    # Titolo dinamico
                    label = f"Dove buttarlo: {nome_comp}" if len(dati['componenti']) > 1 else "Dove buttarlo"

                    # Stile dinamico tramite dizionario
                    stile = DEFAULT_STYLE
                    # Cerca una parola chiave (es. "plastica") dentro la destinazione (es. "plastica rigida")
                    for key, value in CONFIG_BIDONI.items():
                        if key in destinazione:
                            stile = value
                            break
                    # Gestione specifica per Rifiuti speciali
                    if "rifiuto speciale" in destinazione or "raee" in destinazione:
                        flag_rifiuto_speciale = True
                        warning = "Non va nei bidoni di casa. Portalo all'isola ecologica."
                        show_custom_box(label, warning, stile["bg"], stile["text"], "🚫")
                    else:
                        # Rendering standard
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            show_custom_box(label, dest_display, stile["bg"], stile["text"], "🗑️")
                        with c2:
                            st.image(stile["icon"], width=100)
                # Mappa isola ecologia (fuori dal for loop)
                if flag_rifiuto_speciale:
                    st.warning("⚠️ Questo oggetto richiede smaltimento speciale.")
                    if citta:
                        st.write("📍 Ecco l'isola ecologica più vicina a te:")
                        mostra_mappa(citta, 1) # 1 = Mappa Isola Ecologica
                    else:
                        st.warning("Per favore, seleziona una città per ottenere la mappa.")

                # Note dell'esperto
                if dati.get('note'):
                    st.markdown("---")
                    show_custom_box("Nota dell'esperto", dati['note'], "#e8f5e9", "#1b5e20", "💡", is_small=True)

                # --- CHATBOT ---
                st.markdown("---")
                st.subheader("💬 Hai dubbi? Chiedi all'esperto!")
                
                # Inizializza la storia della chat se non esiste
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []

                # Mostra la storia della chat
                for msg in st.session_state.chat_history:
                    st.chat_message(msg["role"]).markdown(msg["content"])
                if prompt := st.chat_input("Es. Devo staccare l'etichetta?"):
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    st.chat_message("user").markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("..."):
                            reply = ai_engine.get_chatbot_response(prompt, dati, api_key)
                            st.markdown(reply)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})

st.markdown("---")
st.caption("Powered by Google Gemini & Streamlit")