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
                model = genai.GenerativeModel('models/gemini-2.5-flash-lite', generation_config=generation_config)

                # Definiamo il Prompt
                prompt = f"""
                Agisci come un esperto di riciclo e raccolta differenziata.
                Analizza questa immagine.
                Se l'oggetto è composto da più parti di materiali diversi (es. bottiglia di vetro con tappo di plastica, vasetto di yogurt con linguetta in alluminio), DEVI separare i componenti.

                Restituisci ESCLUSIVAMENTE un oggetto JSON con la seguente struttura:
                {{
                    "oggetto_principale": "Nome dell'oggetto intero (es. Bottiglia d'acqua)",
                    "materiali": "Elenca tutti i materiali presenti (es. Vetro e Plastica)",
                    "azione": "Azione complessiva da compiere (es. Separa il tappo dalla bottiglia e sciacqua entrambi)",
                    "note": "Breve consiglio o motivazione (max 1 frase)",
                    "componenti": [
                        {{
                            "nome": "Nome del componente (es. Bottiglia, Tappo)",
                            "destinazione": "Dove va buttato (Scegli tra: Plastica, Carta, Vetro, Organico, Indifferenziato, Rifiuto Speciale, Non identificato)"
                        }}
                    ]
                }}

                L'utente si trova in {citta}.

                1. Identifica l'oggetto principale.
                2. Descrivi i materiali e l'azione da compiere a livello globale per l'intero oggetto.
                3. Nella lista "componenti", inserisci SOLO la destinazione per ogni parte separabile.
                4. Se l'oggetto è monomateriale, la lista "componenti" avrà un solo elemento.
                    
                Se l'immagine non è un rifiuto o non è chiara, restituisci un unico componente con "destinazione": "Non identificato".
                """

                # Chiamata alle API e invio del prompt con l'immagine
                response = model.generate_content([prompt, image])

                # PARSING: Trasformiamo il testo JSON in un dizionario Python
                return json.loads(response.text)
            
    # Solleviamo un'eccezione in caso di errore, gestita poi in main.py
    except Exception as e:
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