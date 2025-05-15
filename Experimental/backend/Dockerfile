# Experimental/backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema si fueran necesarias (ej. build-essential para algunas libs)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar recursos de NLTK (punkt para tokenización de frases)
RUN python -m nltk.downloader punkt averaged_perceptron_tagger punkt_tab averaged_perceptron_tagger_eng

# Descargar modelo de spaCy para español (si la lógica NLP lo utiliza)
RUN python -m spacy download es_core_news_sm

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]