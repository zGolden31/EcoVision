import streamlit as st  # Framework per la creazione della web app
import pandas as pd     # Aggiungiamo pandas per gestire facilmente i dati

@st.cache_data # Cache dei dati per evitare ricaricamenti inutili
def carica_dati_geografici():
    '''
        Scarica e processa il file JSON dei comuni italiani.
        Restituisce una lista di stringhe formattate: "Comune, Regione, Italy".
    '''
    # URL ufficiale o raw github con i comuni italiani aggiornati
    URL_comuni = "https://github.com/NotMatte/JSON-Comuni-Italiani/blob/main/data.json?raw=true"
    
    # Leggiamo il JSON direttamente in un DataFrame pandas
    # 'orient=index': Fondamentale perché il JSON è strutturato come un dizionario
    # (es. {"AGLIÈ": {dati}, ...}) invece di essere una lista di oggetti.
    df = pd.read_json(URL_comuni, orient='index') 

    # Creazione della stringa di ricerca univoca (Stile Google Maps)
    # Combiniamo le colonne per ottenere: "NomeCittà, NomeRegione, Italy"
    lista_comuni = df["comune"]+ ", " + df["regione"] + ", Italy"
    
    # Restituiamo la lista ordinata alfabeticamente per facilitare la ricerca
    return lista_comuni.sort_values().tolist()