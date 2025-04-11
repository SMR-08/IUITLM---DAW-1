# -*- coding: utf-8 -*-
# File: /API/Python/ejercicios_python/EJ_NLP/procesamiento_nlp.py

import nltk
import spacy
import logging
from typing import List, Tuple, Dict, Any
from nltk.tokenize import sent_tokenize 
from nltk.translate import gale_church

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

def alinear_frases_gale_church(texto_es: str, texto_en: str) -> Dict[str, Any]:
    """
    Segmenta textos y los alinea usando el algoritmo Gale-Church.

    Args:
        texto_es: Texto en español.
        texto_en: Texto en inglés.

    Returns:
        Un diccionario con:
        - 'frases_es': Lista de frases en español.
        - 'frases_en': Lista de frases en inglés.
        - 'alineacion': Lista de tuplas (idx_es, idx_en) representando la alineación.
                         Puede incluir None si una frase no se alinea.
                         O puede ser una lista de listas si hay alineaciones M-N.
                         (Gale-Church devuelve [(s1, s2), ...])
         - 'error': Mensaje de error si lo hubo, sino None.
    """
    resultado = {
        'frases_es': [],
        'frases_en': [],
        'alineacion': [],
        'error': None
    }
    try:
        # 1. Segmentar frases (¡Es crucial especificar el idioma!)
        # Usar NLTK sent_tokenize para ambos por consistencia con Gale-Church
        # aunque spaCy también puede segmentar.
        if not nlp_en_nltk_ready: # Verificar si NLTK está listo
             raise RuntimeError("Recursos NLTK (punkt) necesarios para sent_tokenize no disponibles.")

        frases_es = sent_tokenize(texto_es, language='spanish')
        frases_en = sent_tokenize(texto_en, language='english')
        resultado['frases_es'] = frases_es
        resultado['frases_en'] = frases_en

        if not frases_es or not frases_en:
            log_nlp.warning("Uno o ambos textos no produjeron frases para alinear.")
            # Devolver frases vacías pero sin error explícito, alineación vacía.
            return resultado

        # 2. Calcular longitudes
        longitudes_es = [len(f) for f in frases_es]
        longitudes_en = [len(f) for f in frases_en]

        # 3. Alinear usando Gale-Church
        # align_blocks es más simple y devuelve la lista [(idx_es, idx_en), ...]
        # Los índices se refieren a la posición en las listas frases_es/frases_en
        # Nota: Puede devolver alineaciones 1-0, 0-1, 1-2, 2-1, 2-2 además de 1-1.
        # Necesitamos manejar esto en el frontend.
        # La función devuelve directamente la lista de tuplas.
        resultado['alineacion'] = gale_church.align_blocks(longitudes_es, longitudes_en)
        log_nlp.info(f"Alineación Gale-Church generada: {resultado['alineacion']}")

    except Exception as e:
        log_nlp.error(f"Error durante alineación Gale-Church: {e}", exc_info=True)
        resultado['error'] = f"Error en alineación: {e}"
        resultado['alineacion'] = [] # Asegurar que sea una lista vacía en error

    return resultado
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