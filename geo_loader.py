import streamlit as st  # Framework per la creazione della web app
import pandas as pd     # Aggiungiamo pandas per gestire facilmente i dati
from geopy.geocoders import Nominatim


@st.cache_data # Cache dei dati per evitare ricaricamenti inutili
def carica_dati_geografici():
    '''
        Scarica e processa il file JSON dei comuni italiani.
        Restituisce una lista di stringhe formattate: "Comune, Regione, Italy".
    '''
    # URL ufficiale o raw github con i comuni italiani aggiornati
    file_comuni = "comuniitaliani.json"
    
    # Leggiamo il JSON direttamente in un DataFrame pandas
    # 'orient=index': Fondamentale perché il JSON è strutturato come un dizionario
    # (es. {"AGLIÈ": {dati}, ...}) invece di essere una lista di oggetti.
    df = pd.read_json(file_comuni, orient='index') 

    # Creazione della stringa di ricerca univoca (Stile Google Maps)
    # Combiniamo le colonne per ottenere: "NomeCittà, NomeRegione, Italy"
    lista_comuni = df["comune"]+ ", " + df["regione"] + ", Italy"
    
    # Restituiamo la lista ordinata alfabeticamente per facilitare la ricerca
    return lista_comuni.sort_values().tolist()


def get_city_from_latlon_italian(lat, lon):
    # 'user_agent' è obbligatorio, metti un nome a caso per la tua app
    geolocator = Nominatim(user_agent="eco_vision_app")
    
    try:
        # language='it' per ottenere i nomi in italiano
        location = geolocator.reverse(f"{lat}, {lon}", language='it')
        address = location.raw.get('address', {})
        
        # Cerca la città in vari campi (a volte è sotto 'town' o 'village')
        citta = address.get('city') or address.get('town') or address.get('village') or address.get('municipality')
        
        if citta:
            return citta
        else:
            return "Città non identificata"
            
    except Exception as e:
        return "Errore di connessione"

