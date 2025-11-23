import streamlit as st              # Framework per la creazione della web app
import pandas as pd  # Aggiungiamo pandas per gestire facilmente i dati
from PIL import Image               # Manipolazione immagini   
import google.generativeai as genai # API Google Gemini ("cervello")  
import json                         # Per la gestione dei dati JSON

@st.cache_data # Cache dei dati per evitare ricaricamenti inutili
def carica_dati_geografici():
    '''
        Scarica e processa il file JSON dei comuni italiani.
        Restituisce una lista di stringhe formattate: "Comune, Regione, Italy".
    '''
    # URL ufficiale o raw github con i comuni italiani aggiornati
    url_comuni = "https://github.com/NotMatte/JSON-Comuni-Italiani/blob/main/data.json?raw=true"
    
    # Leggiamo il JSON direttamente in un DataFrame pandas
    # 'orient=index': Fondamentale perché il JSON è strutturato come un dizionario
    # (es. {"AGLIÈ": {dati}, ...}) invece di essere una lista di oggetti.
    df = pd.read_json(url_comuni, orient='index') 

    # Creazione della stringa di ricerca univoca (Stile Google Maps)
    # Combiniamo le colonne per ottenere: "NomeCittà, NomeRegione, Italy"
    lista_comuni = df["comune"]+ ", " + df["regione"] + ", Italy"
    
    # Restituiamo la lista ordinata alfabeticamente per facilitare la ricerca
    return lista_comuni.sort_values().tolist()

# CONFIGURAZIONE PAGINA
st.set_page_config(
    page_title="Assistente Raccolta Differenziata", # Titolo della pagina
    page_icon="♻️", # Icona della pagina
    layout="centered" # Layout centrato, moderno
) 

# INTESTAZIONE E UI PRINCIPALE
st.title("♻️ Dove lo butto?") # Titolo principale
st.markdown("""
Carica una foto di un rifiuto o scattala direttamente. 
L'Intelligenza Artificiale ti dirà **cos'è**, **se devi pulirlo** e **in quale bidone va buttato**.
""") # Descrizione in markdown


# CONFIGURAZIONE CONTESTO UTENTE (GEOLOCALIZZAZIONE)
# Carichiamo i dati PRIMA di disegnare l'interfaccia
comuni_italiani = carica_dati_geografici()
# Usiamo un expander per mantenere l'interfaccia pulita
#L'utente può scegliere di inserire la propria posizione per avere indicazioni più precise.
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
                # Configura Gemini
                genai.configure(api_key=api_key)
                
                with st.spinner("Sto analizzando l'oggetto..."):

                    # Forzare la risposta in formato JSON
                    generation_config = {"response_mime_type": "application/json"}
                        
                    # Carichiamo il modello 
                    model = genai.GenerativeModel('models/gemini-2.0-flash', generation_config=generation_config)

                    # Definiamo il Prompt
                    prompt = f"""
                    Agisci come un esperto di riciclo e raccolta differenziata.
                    Analizza questa immagine.
                    Restituisci ESCLUSIVAMENTE un oggetto JSON con i seguenti campi:
                    - "oggetto": Nome breve dell'oggetto identificato.
                    - "materiale": Il materiale prevalente (es. Plastica, Vetro, Carta, Poliaccoppiato).
                    - "destinazione": Dove va buttato (es. Plastica, Carta, Vetro, Umido, Secco, Isola Ecologica).
                    - "azione": Cosa fare prima di buttarlo (es. "Sciacqua bene", "Schiaccia", "Separa il tappo", "Nessuna azione").
                    - "note": Una spiegazione brevissima o un consiglio specifico (max 1 frase).
                    L'utente si trova in {citta}, {regione}.

                    1. Identifica l'oggetto principale.
                    2. Controlla se l'oggetto sembra sporco (es. residui di cibo, salsa, liquido).
                    3. Fornisci istruzioni chiare:
                        - Se è sporco, dì esplicitamente come pulirlo (es. sciacquare, svuotare).
                        - Dimmi in quale bidone va gettato (Plastica, Carta, Vetro, Umido/Organico, Secco/Indifferenziato, Metallo).
                    
                     Se l'immagine non è un rifiuto o non è chiara, restituisci "destinazione": "Non identificato".
                    """

                    # Chiamata alle API e invio del prompt con l'immagine
                    response = model.generate_content([prompt, image])

                     # PARSING: Trasformiamo il testo JSON in un dizionario Python
                    dati_rifiuto = json.loads(response.text)

                    # VISUALIZZAZIONE RISULTATI
                    # Se non è stato identificato
                    if dati_rifiuto["destinazione"] == "Non identificato":
                        st.warning("⚠️ Non sono riuscito a capire di che oggetto si tratta. Prova con una foto più chiara.")
                    # Oggetto identificato correttamente, mostriamo i dettagli
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