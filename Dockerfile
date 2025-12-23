# 1. Usa un'immagine Python leggera come base
FROM python:3.11-slim

# 2. Imposta la cartella di lavoro all'interno del container
WORKDIR /app

# 4. Copia il file dei requisiti e installa le librerie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia tutto il resto del codice nel container
COPY . .

# 6. Esponi la porta usata da Streamlit (default 8501)
EXPOSE 8501

# 7. Configura Streamlit per girare correttamente in Docker
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 8. Comando per avviare l'app
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]