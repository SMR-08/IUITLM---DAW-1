# -*- coding: utf-8 -*-
# File: /API/Python/ejercicios_python/EJ_NLP/procesamiento_nlp.py

import nltk
import spacy
import logging
from typing import List, Tuple

# Configurar logger
log_nlp = logging.getLogger(__name__)
log_nlp.setLevel(logging.INFO)

# --- Carga de Modelos (Intentar al inicio) ---
nlp_en_nltk_ready = False
nlp_es_spacy_ready = False
nlp_es = None

# Verificar recursos NLTK para inglés
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('tokenizers/punkt_tab') # Añadido por si acaso
    nltk.data.find('taggers/averaged_perceptron_tagger_eng') # Añadido por si acaso
    log_nlp.info("Recursos NLTK para inglés encontrados.")
    nlp_en_nltk_ready = True
except LookupError as e:
    log_nlp.warning(f"Recursos NLTK para inglés no encontrados: {e}. El procesamiento NLTK podría fallar.")

# Cargar modelo spaCy para español
try:
    nlp_es = spacy.load("es_core_news_sm")
    log_nlp.info("Modelo spaCy español (es_core_news_sm) cargado.")
    nlp_es_spacy_ready = True
except OSError:
    log_nlp.error("¡ERROR CRÍTICO! Modelo spaCy español (es_core_news_sm) no encontrado. "
                  "Asegúrate de ejecutar 'python -m spacy download es_core_news_sm' en el Dockerfile.")

# --- Funciones de Procesamiento NLTK (Inglés) ---

def etiquetar_palabras_nltk(texto_entrada: str) -> List[Tuple[str, str]]:
    """Etiqueta palabras usando NLTK (Penn Treebank tags). Ideal para inglés."""
    if not nlp_en_nltk_ready:
        log_nlp.error("NLTK (inglés) no está listo. Faltan recursos.")
        return [("Error:", "NLTK_RESOURCES_MISSING")]

    if not texto_entrada or not isinstance(texto_entrada, str):
        log_nlp.warning("etiquetar_palabras_nltk recibió entrada inválida.")
        return []
    try:
        palabras = nltk.tokenize.word_tokenize(texto_entrada)
        if not palabras: return []
        etiquetas_pos = nltk.pos_tag(palabras)
        log_nlp.debug(f"[NLTK] {len(etiquetas_pos)} etiquetas POS generadas.")
        return etiquetas_pos
    except Exception as e:
        log_nlp.error(f"Error inesperado durante NLTK pos_tag: {e}", exc_info=True)
        return [("Error procesando con NLTK:", str(e))]

# --- Función de Procesamiento spaCy (Español) ---

def procesar_texto_spacy(texto_entrada: str) -> List[Tuple[str, str]]:
    """Procesa texto usando spaCy (español) para obtener tokens y etiquetas POS universales."""
    if not nlp_es_spacy_ready or not nlp_es:
        log_nlp.error("spaCy (español) no está listo. Falta modelo.")
        return [("Error:", "SPACY_MODEL_MISSING")]

    if not texto_entrada or not isinstance(texto_entrada, str):
        log_nlp.warning("procesar_texto_spacy recibió entrada inválida.")
        return []
    try:
        doc = nlp_es(texto_entrada)
        resultado = [(token.text, token.pos_) for token in doc]
        log_nlp.debug(f"[spaCy ES] {len(resultado)} tokens/etiquetas generadas.")
        return resultado
    except Exception as e:
        log_nlp.error(f"Error inesperado durante procesamiento spaCy (ES): {e}", exc_info=True)
        return [("Error procesando con spaCy:", str(e))]

# --- Bloque de prueba (opcional) ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    texto_ejemplo_es = "Hola mundo. Esta es una frase de prueba en español. ¿Funciona bien spaCy?"
    texto_ejemplo_en = "Hello world. This is an English test sentence. Does NLTK work?"

    print("\n--- Probando spaCy (Español) ---")
    if nlp_es_spacy_ready:
        etiquetas_es = procesar_texto_spacy(texto_ejemplo_es)
        print(etiquetas_es)
    else:
        print("Modelo spaCy español no disponible para prueba.")

    print("\n--- Probando NLTK (Inglés) ---")
    if nlp_en_nltk_ready:
        etiquetas_en = etiquetar_palabras_nltk(texto_ejemplo_en)
        print(etiquetas_en)
    else:
        print("Recursos NLTK inglés no disponibles para prueba.")
    print("-" * 30)