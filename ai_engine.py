import streamlit as st # Framework per la creazione della web app
import json # Gestione dei dati JSON
import re # Gestione delle stringhe
from google import genai # API Google Gemini ("cervello")
from google.genai import types # Tipi di dati per Gemini

# Impostare come constanti il modello di Gemini
# Usiamo gemini-2.0-flash-lite
VISION_MODEL_ID = "gemini-2.0-flash-lite"
CHAT_MODEL_ID = "gemini-2.0-flash-lite"

def _get_client(api_key):
    """
    Funzione interna per inizializzare il Client GenAI.
    L'uso di un'istanza client evita problemi di configurazione globale.
    """
    return genai.Client(api_key=api_key)

def _clean_json_text(raw_text):
    """
    Funzione di supporto per ripulire i blocchi di codice markdown 
    se l'IA li include (es. ```json ... ```) usando le regex
    """
    try:
        # Regex per rimuovere ```json ... ``` o solo ``` ... ``` all'inizio/fine
        cleaned = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
        cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()
    except Exception:
        return raw_text

def analizza_immagine(image, api_key, citta):
    """
    Analizza un'immagine per identificare il tipo di rifiuto e le istruzioni di smaltimento.
    Restituisce un dizionario Python (JSON parsato).
    """
    client = _get_client(api_key)
    try:
        with st.spinner("Sto analizzando l'oggetto..."):

            # Configura lo schema della risposta usando il modulo "types"
            # Forziamo il tipo MIME JSON per ottenere un output strutturato
            config = types.GenerateContentConfig(
                response_mime_type="application/json"
                temperature = 0.2 # Temperatura bassa per risultati più deterministici e meno creativi
            )

            prompt = f"""
            Agisci come un esperto di riciclo e raccolta differenziata.
            Analizza questa immagine.
            Se l'oggetto è composto da più parti di materiali diversi (es. bottiglia di vetro con tappo di plastica), DEVI separare i componenti.

            Restituisci ESCLUSIVAMENTE un oggetto JSON con la seguente struttura:
            {{
                "oggetto_principale": "Nome dell'oggetto intero (es. Bottiglia d'acqua)",
                "materiali": "Elenca tutti i materiali presenti (es. Vetro e Plastica)",
                "azione": "Azione complessiva da compiere (es. Separa il tappo dalla bottiglia)",
                "note": "Breve consiglio o motivazione",
                "componenti": [
                    {{
                        "nome": "Nome del componente (es. Bottiglia, Tappo)",
                        "destinazione": "Dove va buttato (Scegli tra: Plastica, Carta, Vetro, Organico, Indifferenziato, Rifiuto Speciale, Non identificato)"
                    }}
                ]
            }}

            L'utente si trova in {citta}.
            1. Identifica l'oggetto principale.
            2. Descrivi i materiali e l'azione globale.
            3. Nella lista "componenti", inserisci SOLO la destinazione per ogni parte.
            4. Se l'immagine non è chiara, restituisci un componente con "destinazione": "Non identificato".
            """
            
            # Chiamate API usando client.models della nuova libreria
            response = client.models.generate_content(
                model_id=VISION_MODEL_ID,
                content=[prompt, image],
                config=config
            )

            # Parsing JSON con meccanismo di sicurezza
            try:
                # Puliamo il testo, rimuovento i backticks del codice markdown
                clean_text = _clean_json_text(response.text)
                return json.loads(clean_text)

            except json.JSONDecodeError as json_err:
                print(f"Errore Parsing JSON: {json_err}. Testo grezzo: {response.text}")
                # Dizionario di fallback per evitare che l'app vada in crash
                return {
                    "oggetto_principale": "Errore Analisi",
                    "materiali": "Sconosciuto",
                    "azione": "Riprova con una foto più chiara.",
                    "note": "L'IA non ha restituito un formato valido.",
                    "componenti": [{"nome": "Oggetto non identificato", "destinazione": "Non identificato"}]
                }
            except Exception as e:
                # Solleviamo l'eccezione al main.py per mostrarla nell'interfaccia utente
               raise e

def get_chatbot_response(user_query, context_data, api_key):
    """
    Genera una risposta del chatbot basata sui dati dell'analisi precedente.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash-lite') # Usiamo un modello veloce per la chat
        
        # Creiamo un contesto stringa dai dati JSON
        context_str = json.dumps(context_data, ensure_ascii=False, indent=2)
        
        prompt = f"""
        Sei un assistente esperto di riciclo. L'utente ha appena analizzato un rifiuto con EcoVision.
        Ecco i dati dell'analisi che hai appena fornito all'utente:
        {context_str}

        L'utente ora ti pone questa domanda: "{user_query}"

        Rispondi in modo gentile, diretto e utile. 
        Riferisciti all'oggetto analizzato se pertinente.
        Se la domanda non c'entra nulla col riciclo o con l'oggetto, rispondi educatamente che ti occupi solo di rifiuti.
        Mantieni le risposte concise.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Mi dispiace, c'è stato un problema nel generare la risposta: {e}"