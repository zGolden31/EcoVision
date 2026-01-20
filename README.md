♻️ **EcoVision: Smart Waste Sorting Assistant**

EcoVision è un'applicazione web intelligente progettata per ottimizzare la raccolta differenziata domestica. Utilizzando un approccio ibrido che combina LLM Multimodali e Geolocalizzazione, il sistema identifica i rifiuti e fornisce istruzioni di smaltimento basate sulle normative del comune specifico dell'utente.

🌟 **Funzionalità Principali**
- **Riconoscimento Multimodale**: Analisi visiva avanzata tramite Google Gemini 2.5 Flash per identificare materiali e stato del rifiuto.
- **Scomposizione Oggetti Complesso**: Capacità di distinguere e separare componenti di rifiuti multi-materiale (es. bottiglia e tappo) fornendo destinazioni diverse.
- **Geolocalizzazione Dinamica**: Adattamento delle regole di smaltimento in tempo reale basato sulla posizione GPS dell'utente (Reverse Geocoding).
- **Chatbot Integrato**: Assistente conversazionale con memoria di contesto per risolvere dubbi specifici post-analisi.
- **Mappe Isole Ecologiche**: Integrazione con Google Maps per localizzare i centri di raccolta per rifiuti speciali.

-----------------------------------------------------------------------------------------------------

🐳 **Guida all'installazione con Docker**

Questa sezione spiega come configurare l'ambiente e avviare l'applicazione utilizzando i container Docker, garantendo la massima coerenza tra i vari ambienti di sviluppo.

🛠 **Prerequisiti Hardware e Software**
Prima di iniziare, assicuratevi di aver configurato correttamente la vostra macchina:
- **Virtualizzazione:** deve essere abilitata nel BIOS del PC (Intel VT-x o AMD-V). Senza questa, Docker Desktop non si avvierà.
- **Docker Desktop:** scaricato, installato e con l'icona della "balena" in stato verde (running).
- **Database Comuni:** verificate che il file comuniitaliani.json sia presente nella cartella principale del progetto.

🔑 **Gestione API Key (Sicurezza)**

Per motivi di sicurezza, non carichiamo le chiavi API su Git. Ogni sviluppatore utilizzerà la propria chiave Gemini al momento dell'avvio del container. Il codice è già predisposto per leggere la chiave dalle variabili d'ambiente.

🚀 **Comandi per l'avvio**

**1. Build dell'Immagine**

Aprite il terminale nella root del progetto e create l'immagine Docker. Questo passaggio installa tutte le dipendenze (come google-genai, geopy, pandas) all'interno di un ambiente Linux isolato:

docker build -t ecovision-app .

**2. Esecuzione del Container**

Avviate l'applicazione passando la vostra chiave personale tramite la variabile d'ambiente -e:

docker run -p 8501:8501 -e GOOGLE_API_KEY="INSERISCI_QUI_LA_TUA_CHIAVE" ecovision-app

-p 8501:8501: Collega la porta del container alla porta del tuo PC;

-e GOOGLE_API_KEY: Inietta la chiave nel sistema in modo sicuro.

----------------------------------------------------------------------------------------------------
🌐 **Accesso all'App**

Una volta avviato il container, l'app sarà raggiungibile dal browser all'indirizzo: 👉 http://localhost:8501

_(Nota: Ignorate l'indirizzo 0.0.0.0 stampato nel terminale, è un riferimento interno al container)_

--------------------------------------------------------------------------------------------------📂 **Struttura del Progetto e Diagrammi**

Abbiamo aggiornato la documentazione tecnica che trovate nelle cartelle del repository:
- **Diagramma dei Casi d'Uso:** Include ora il Chatbot "Chiedi all'esperto" e la gestione API Key.
- **Diagramma delle Classi:** Riflette la struttura multi-componente dell'analisi AI (JSON parsing).
- **Diagramma di Sequenza:** Mostra il flusso asincrono verso l'SDK google-genai.

----------------------------------------------------------------------------------------------------
👥 Autori
Alessio Cappiello
Andrea Falcicchio
Giuseppe Fuzio

Progetto sviluppato per il corso di Ingegneria del Software - Politecnico di Bari (A.A. 2025/26)
