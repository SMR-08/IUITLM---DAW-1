# Dockerfile para la API de Python

# Usa una imagen base de Python 3.9 slim-buster (ligera).
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Instalar herramientas de compilación necesarias (GCC, etc.)
# Actualizar lista de paquetes, instalar build-essential, y limpiar caché apt
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*
# --------------------------

# Copia el archivo de requisitos al contenedor.
# Es necesario copiarlo para poder instalar las dependencias en el siguiente paso.
# Asegúrate que la ruta relativa './Python/requisitos.txt' es correcta
# respecto al 'context' definido en docker-compose.yaml (que es ./API).
# La ruta en el host sería: ./API/Python/requisitos.txt
COPY ./Python/requisitos.txt /app/requisitos.txt

# Instala las dependencias listadas en requisitos.txt.
# '--no-cache-dir' ayuda a mantener la imagen más pequeña.
RUN pip install --no-cache-dir -r requisitos.txt

# Descargar los paquetes de datos necesarios de NLTK
# Usamos python -m nltk.downloader para ejecutarlo como módulo
RUN python -m nltk.downloader punkt averaged_perceptron_tagger punkt_tab averaged_perceptron_tagger_eng

# y los paquetes de spacy para el idioma español
RUN python -m spacy download es_core_news_sm

# NOTA: No se copia el código de la aplicación Python (.py) aquí,
# ya que se monta como un volumen en docker-compose.yaml para desarrollo.

# Comando por defecto para ejecutar la aplicación usando Gunicorn al iniciar el contenedor.
# 'app:app' -> busca la variable 'app' en el archivo 'app.py' (o el nombre que uses).
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]