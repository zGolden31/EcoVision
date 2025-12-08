import google.generativeai as genai     # API Google Gemini ("cervello")
import json                        # Per la gestione dei dati JSON  
import streamlit as st             # Framework per la creazione della web app
 
def analizza_immagine(image, api_key, citta):
    try:
        # Configura Gemini
            genai.configure(api_key=api_key)
                
            with st.spinner("Sto analizzando l'oggetto..."):

                # Forzare la risposta in formato JSON
                generation_config = {"response_mime_type": "application/json"}
                        
                # Carichiamo il modello 
                model = genai.GenerativeModel('models/gemini-2.5-flash', generation_config=generation_config)

                # Definiamo il Prompt
                prompt = f"""
                Agisci come un esperto di riciclo e raccolta differenziata.
                Analizza questa immagine.
                Restituisci ESCLUSIVAMENTE un oggetto JSON con i seguenti campi:
                - "oggetto": Nome breve dell'oggetto identificato.
                - "materiale": Il materiale prevalente (es. Plastica, Vetro, Carta, Poliaccoppiato).
                - "destinazione": Dove va buttato. Scegli SOLO tra questi: ["Plastica", "Carta", "Vetro", "Organico", "Indifferenziato", "Rifiuto Speciale", "Non identificato"].
                - "azione": Cosa fare prima di buttarlo (es. "Sciacqua bene", "Schiaccia", "Separa il tappo", "Nessuna azione").
                - "note": Una spiegazione brevissima o un consiglio specifico (max 1 frase).
                L'utente si trova in {citta}.

                1. Identifica l'oggetto principale.
                2. Scegli la categoria corretta tra quelle consentite.
                3. Controlla se l'oggetto sembra sporco (es. residui di cibo, salsa, liquido).
                4. Fornisci istruzioni chiare:
                    - Se è sporco, dì esplicitamente come pulirlo.
                    
                Se l'immagine non è un rifiuto o non è chiara, restituisci "destinazione": "Non identificato".
                """

                # Chiamata alle API e invio del prompt con l'immagine
                response = model.generate_content([prompt, image])

                # PARSING: Trasformiamo il testo JSON in un dizionario Python
                return json.loads(response.text)
            
    # Solleviamo un'eccezione in caso di errore, gestita poi in main.py
    except Exception as e:
        raise e

    