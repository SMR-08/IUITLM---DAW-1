# -*- coding: utf-8 -*-
# File: /API/Python/ejercicios_python/EJ_NLP/procesamiento_nlp.py

import nltk
import logging
from typing import List, Tuple # Corrección: Tuple se importa de typing

# Configurar un logger específico para este módulo si se desea
log_nlp = logging.getLogger(__name__)
log_nlp.setLevel(logging.INFO) # O el nivel que prefieras

# --- Verificación de Recursos NLTK (Opcional pero recomendado) ---
# Intenta asegurar que los recursos se cargaron durante el build.
# Si falla aquí, el contenedor no debería haber construido bien.
try:
    # nltk.data.find busca los recursos, si no los encuentra lanza LookupError
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    log_nlp.info("Recursos NLTK 'punkt' y 'averaged_perceptron_tagger' encontrados.")
except LookupError as e:
    log_nlp.critical(f"¡Error CRÍTICO! Recursos NLTK no encontrados: {e}. "
                     "Asegúrate que 'RUN python -m nltk.downloader...' se ejecutó en el Dockerfile.")
    # Podrías lanzar una excepción aquí para evitar que la app use estas funciones si fallan
    # raise RuntimeError(f"Faltan recursos NLTK: {e}")

# --- Funciones de Procesamiento ---

def tokenizar_frases(texto_entrada: str) -> List[str]:
    """
    Divide un texto en una lista de frases utilizando NLTK.

    Args:
        texto_entrada: El texto a tokenizar.

    Returns:
        Una lista de strings, donde cada string es una frase detectada.
        Devuelve una lista vacía si la entrada es vacía o nula.
        Devuelve una lista con el texto original si ocurre un error inesperado.
    """
    if not texto_entrada or not isinstance(texto_entrada, str):
        log_nlp.warning("tokenizar_frases recibió entrada vacía o no válida.")
        return []

    try:
        frases = nltk.tokenize.sent_tokenize(texto_entrada)
        log_nlp.debug(f"Texto tokenizado en {len(frases)} frases.")
        return frases
    except Exception as e:
        # Captura errores inesperados de NLTK (poco común con sent_tokenize)
        log_nlp.error(f"Error inesperado durante sent_tokenize: {e}", exc_info=True)
        # Devolver algo seguro, como una lista con el texto original
        return [texto_entrada]


def etiquetar_palabras(texto_entrada: str) -> List[Tuple[str, str]]:
    """
    Tokeniza un texto en palabras y asigna etiquetas gramaticales (POS tags) a cada palabra.

    Args:
        texto_entrada: El texto a etiquetar.

    Returns:
        Una lista de tuplas (palabra, etiqueta_POS).
        Devuelve una lista vacía si la entrada es vacía o nula.
        Devuelve una lista vacía si ocurre un error inesperado.
    """
    if not texto_entrada or not isinstance(texto_entrada, str):
        log_nlp.warning("etiquetar_palabras recibió entrada vacía o no válida.")
        return []

    try:
        # 1. Tokenizar en palabras
        palabras = nltk.tokenize.word_tokenize(texto_entrada)
        log_nlp.debug(f"Texto tokenizado en {len(palabras)} palabras.")

        if not palabras:
            return [] # No hay palabras para etiquetar

        # 2. Etiquetar las palabras
        etiquetas_pos = nltk.pos_tag(palabras)
        log_nlp.debug(f"Se generaron {len(etiquetas_pos)} etiquetas POS.")

        return etiquetas_pos

    except Exception as e:
        # Captura errores inesperados de NLTK (más probable con word_tokenize o pos_tag)
        log_nlp.error(f"Error inesperado durante word_tokenize o pos_tag: {e}", exc_info=True)
        # Devolver lista vacía en caso de error
        return []

# --- Bloque de prueba (opcional, para ejecutar directamente) ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG) # Habilitar DEBUG para pruebas locales
    texto_ejemplo = "Hola mundo. Esta es una frase de prueba. ¿NLTK funciona correctamente?"

    print("--- Probando tokenizar_frases ---")
    frases_resultado = tokenizar_frases(texto_ejemplo)
    print(frases_resultado)
    print("-" * 30)

    print("--- Probando etiquetar_palabras ---")
    etiquetas_resultado = etiquetar_palabras(texto_ejemplo)
    print(etiquetas_resultado)
    print("-" * 30)

    print("--- Probando con entrada vacía ---")
    print("Frases:", tokenizar_frases(""))
    print("Etiquetas:", etiquetar_palabras(""))
    print("-" * 30)