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
                    "componenti": [
                        {{
                            "nome": "Nome del componente (es. Bottiglia, Tappo)",
                            "materiale": "Materiale (es. Plastica, Vetro, Carta, Poliaccoppiato)",
                            "destinazione": "Dove va buttato (Scegli tra: Plastica, Carta, Vetro, Organico, Indifferenziato, Rifiuto Speciale, Non identificato)",
                            "azione": "Azione richiesta (es. Sciacqua, Schiaccia, Stacca dal resto, Nessuna azione)",
                            "note": "Breve consiglio o motivazione (max 1 frase)"
                        }}
                    ]
                }}

                L'utente si trova in {citta}.

                1. Identifica l'oggetto principale.
                2. Se ci sono più materiali, crea un elemento nella lista "componenti" per ognuno.
                3. Se l'oggetto è monomateriale, la lista "componenti" avrà un solo elemento.
                4. Controlla se l'oggetto sembra sporco e indica l'azione di pulizia se necessaria.
                    
                Se l'immagine non è un rifiuto o non è chiara, restituisci un unico componente con "destinazione": "Non identificato".
                """

                # Chiamata alle API e invio del prompt con l'immagine
                response = model.generate_content([prompt, image])

                # PARSING: Trasformiamo il testo JSON in un dizionario Python
                return json.loads(response.text)
            
    # Solleviamo un'eccezione in caso di errore, gestita poi in main.py
    except Exception as e:
        raise e

    