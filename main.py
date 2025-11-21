import streamlit as st    # Streamlit per l'interfaccia web
from PIL import Image    # Libreria per la gestione delle immagini
import google.generativeai as genai  # API Google Gemini ("cervello")  

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


# --- Configurazione Posizione (Menu nel corpo principale) ---
# Usiamo un expander per non occupare spazio se non serve, ma renderlo visibile nel flusso
with st.expander("📍 Vuoi trovare l'isola ecologica? **Imposta la tua posizione**"):
    st.write("Inserisci la tua posizione per ricevere indicazioni personalizzate per lo smaltimento dei rifiuti e per l'isola ecologica più vicina a te.")
    
    # Creiamo due colonne per affiancare i campi Città e Regione
    col1, col2 = st.columns(2)
    
    with col1:
        citta = st.text_input("Città", placeholder="Es. Roma")
    with col2:
        regione = st.text_input("Regione", placeholder="Es. Lazio")
    
    # Feedback visivo immediato
    if citta and regione:
        st.success(f"Posizione salvata: {citta} ({regione})")
        # In futuro qui genereremo il link a Google Maps

# --- Gestione API Key (Sicurezza) ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Fallback per inserimento manuale se non presente nei secrets
    api_key = st.text_input("Inserisci la tua Google API Key:", type="password")

# --- Input Immagine ---
if api_key:
    option = st.radio("Come vuoi caricare l'immagine?", ("Carica file", "Scatta foto"))
    image_file = None

    if option == "Carica file":
        image_file = st.file_uploader("Scegli un'immagine...", type=["jpg", "jpeg", "png"])
    else:
        image_file = st.camera_input("Scatta una foto al rifiuto")

    # Anteprima immagine (blocco esistente)
    if image_file is not None:
        image = Image.open(image_file)
        st.image(image, caption="Immagine caricata", use_container_width=True)

        # --- Logica dell'Applicazione (NUOVA PARTE) ---
        if st.button("Analizza Rifiuto 🔍"):
            # Configura Gemini
            try:
                genai.configure(api_key=api_key)
                
                with st.spinner("Sto analizzando l'oggetto..."):
                    # Carichiamo il modello 
                    model = genai.GenerativeModel('models/gemini-2.0-flash')

                    # Definiamo il Prompt
                    prompt = """
                    Agisci come un esperto di riciclo e raccolta differenziata.
                    Analizza questa immagine.
                    1. Identifica l'oggetto principale.
                    2. Controlla se l'oggetto sembra sporco (es. residui di cibo, salsa, liquido).
                    3. Fornisci istruzioni chiare:
                        - Se è sporco, dì esplicitamente come pulirlo (es. sciacquare, svuotare).
                        - Dimmi in quale bidone va gettato (Plastica, Carta, Vetro, Umido/Organico, Secco/Indifferenziato, Metallo).
                    
                    Rispondi in italiano usando un elenco puntato e un tono amichevole. Usa delle emoji.
                    Se l'immagine non è chiara o non contiene rifiuti, dillo chiaramente.
                    """

                    # Chiamata alle API
                    response = model.generate_content([prompt, image])
                    
                    st.success("Analisi completata!")
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"Errore durante l'analisi: {e}")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Gemini & Streamlit")