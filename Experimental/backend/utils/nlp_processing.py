# backend/utils/nlp_processing.py

import nltk
import spacy # Aunque no se usa directamente en la función de alineación semántica
import logging
from typing import List, Tuple, Dict, Any
from nltk.tokenize import sent_tokenize

# Sentence Transformers y Similitud de Coseno
from sentence_transformers import SentenceTransformer, util
import numpy as np 

# Configurar logger
log_nlp = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG) # Descomentar para detalle

# --- Carga de Modelos (Intentar al inicio) ---
nlp_en_nltk_ready = False
# nlp_es_spacy_ready = False # Ya no es relevante aquí
# nlp_es = None # Ya no es relevante aquí

# Modelo de Sentence Transformers
embedder_model_name = 'paraphrase-multilingual-mpnet-base-v2'
sbert_model = None # Inicializar como None
try:
    sbert_model = SentenceTransformer(embedder_model_name)
    log_nlp.info(f"Modelo SentenceTransformer '{embedder_model_name}' cargado correctamente.")
except Exception as e:
    log_nlp.error(f"¡ERROR CRÍTICO! No se pudo cargar el modelo SentenceTransformer '{embedder_model_name}': {e}", exc_info=True)
    # sbert_model permanece None

# Verificar recursos NLTK para tokenización de frases
try:
    nltk.data.find('tokenizers/punkt')
    log_nlp.info("Recurso NLTK 'punkt' (para sent_tokenize) encontrado.")
    nlp_en_nltk_ready = True
except LookupError as e:
    log_nlp.warning(f"Recurso NLTK 'punkt' no encontrado: {e}. La segmentación de frases podría fallar. "
                    "Asegúrate de que 'punkt' se descarga en el Dockerfile (RUN python -m nltk.downloader punkt).")


# ------ ESTA ES LA FUNCIÓN QUE NECESITAS ASEGURARTE QUE ESTÉ ASÍ ------
def segmentar_frases(texto: str, idioma: str = 'english') -> List[str]: # <--- DEBE TENER EL PARÁMETRO 'idioma'
    """Segmenta un texto en frases usando NLTK."""
    if not nlp_en_nltk_ready:
        # Si 'punkt' no está, sent_tokenize fallará para cualquier idioma.
        log_nlp.error("Recurso NLTK 'punkt' para segmentación de frases no disponible.")
        raise RuntimeError("Recurso NLTK 'punkt' para segmentación de frases no disponible.")
    
    if not texto or not isinstance(texto, str):
        return []
    
    # Validar que el idioma sea uno que NLTK sent_tokenize espera para 'punkt'
    # 'punkt' soporta muchos idiomas, incluyendo 'spanish' y 'english'.
    # Aquí solo hacemos una verificación simple, podrías expandirla.
    idioma_nltk = idioma.lower() # NLTK suele usar nombres de idioma en minúsculas
    if idioma_nltk not in ['english', 'spanish', 'french', 'german', 'italian', 'portuguese']: # Añade más si los necesitas
        log_nlp.warning(f"Idioma '{idioma}' no es directamente reconocido por NLTK sent_tokenize con nombre canónico. Se intentará de todas formas.")
        # sent_tokenize podría funcionar si el nombre es un alias válido o si 'punkt' tiene un tokenizador para ese idioma
        # con un nombre ligeramente diferente.

    try:
        return sent_tokenize(texto, language=idioma_nltk) # <--- SE USA 'language=idioma_nltk'
    except Exception as e:
        log_nlp.error(f"Error segmentando frases para idioma '{idioma_nltk}': {e}", exc_info=True)
        return []
# ------ FIN DE LA FUNCIÓN IMPORTANTE ------


def alinear_frases_con_similitud_semantica(
    texto_es: str,
    texto_en: str
) -> Dict[str, Any]:
    """
    Alinea frases entre dos textos (español e inglés) usando similitud semántica de embeddings.
    Para cada frase en español, encuentra la frase en inglés más similar.

    Retorna:
        Un diccionario con:
        - 'frases_es_originales': Lista de frases segmentadas del texto en español.
        - 'frases_en_originales': Lista de frases segmentadas del texto en inglés.
        - 'alineacion_es_a_en': Lista de tuplas (idx_frase_es, idx_frase_en_alineada, similitud).
        - 'error': Mensaje de error si lo hubo, sino None.
    """
    resultado = {
        'frases_es_originales': [],
        'frases_en_originales': [],
        'alineacion_es_a_en': [], 
        'error': None
    }

    if not sbert_model:
        resultado['error'] = "El modelo de SentenceTransformer no está disponible para la alineación semántica."
        log_nlp.error(resultado['error'])
        return resultado

    try:
        # Asegúrate de pasar el nombre del idioma correctamente a NLTK
        frases_es = segmentar_frases(texto_es, idioma='spanish') # <--- 'idioma' en minúsculas
        frases_en = segmentar_frases(texto_en, idioma='english') # <--- 'idioma' en minúsculas
        
        resultado['frases_es_originales'] = frases_es
        resultado['frases_en_originales'] = frases_en

        if not frases_es or not frases_en:
            msg = "Uno o ambos textos no produjeron frases para alinear."
            if not frases_es: msg += " Corpus español sin frases."
            if not frases_en: msg += " Corpus inglés sin frases."
            log_nlp.warning(msg)
            return resultado

        log_nlp.info(f"Segmentación: {len(frases_es)} frases ES, {len(frases_en)} frases EN.")

        log_nlp.info("Generando embeddings para frases en español...")
        embeddings_es = sbert_model.encode(frases_es, convert_to_tensor=True, show_progress_bar=False)
        log_nlp.info("Generando embeddings para frases en inglés...")
        embeddings_en = sbert_model.encode(frases_en, convert_to_tensor=True, show_progress_bar=False)
        log_nlp.info("Embeddings generados.")

        cosine_scores = util.cos_sim(embeddings_es, embeddings_en)
        
        for i in range(len(frases_es)):
            best_match_idx_en = np.argmax(cosine_scores[i])
            best_match_score = cosine_scores[i][best_match_idx_en].item() 

            resultado['alineacion_es_a_en'].append(
                (i, int(best_match_idx_en), float(best_match_score))
            )
            log_nlp.debug(f"  ES[{i}]:'{frases_es[i][:30]}...' -> EN[{int(best_match_idx_en)}]:'{frases_en[int(best_match_idx_en)][:30]}...' (Sim: {best_match_score:.4f})")
            
        log_nlp.info(f"Alineación ES->EN (idx_es, idx_en, score) generada: {len(resultado['alineacion_es_a_en'])} pares.")

    except RuntimeError as e: # Capturar RuntimeError de segmentar_frases
        log_nlp.error(f"Error de ejecución durante segmentación: {e}", exc_info=True)
        resultado['error'] = str(e) # Propagar el mensaje de error específico
    except Exception as e:
        log_nlp.error(f"Error durante alineación semántica: {e}", exc_info=True)
        resultado['error'] = f"Error en alineación semántica: {e}"
        resultado['alineacion_es_a_en'] = []

    return resultado


# Bloque de prueba
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG) 
    
    if not sbert_model:
        print("El modelo SentenceTransformer no se cargó. Abortando prueba.")
    elif not nlp_en_nltk_ready:
        print("Recursos NLTK 'punkt' no disponibles. Abortando prueba.")
    else:
        test_es = (
            "El sol brilla intensamente hoy.\n"
            "Los pájaros cantan melodías alegres en los árboles altos."
        )
        test_en = (
            "The birds are singing joyful melodies in the tall trees.\n"
            "The sun is shining brightly today."
        )

        print("\n--- Probando Alineación Semántica ---")
        alineacion = alinear_frases_con_similitud_semantica(test_es, test_en)
        
        if alineacion['error']:
            print(f"Error: {alineacion['error']}")
        else:
            print(f"Frases ES: {len(alineacion['frases_es_originales'])}")
            print(f"Frases EN: {len(alineacion['frases_en_originales'])}")
            print("Alineaciones (ES_idx, EN_idx, Similitud):")
            if alineacion['alineacion_es_a_en']:
                for es_idx, en_idx, score in alineacion['alineacion_es_a_en']:
                    es_frase = alineacion['frases_es_originales'][es_idx]
                    # Manejar caso donde en_idx podría ser None si se implementa un umbral
                    en_frase_txt = "---NO MATCH---"
                    if en_idx is not None and 0 <= en_idx < len(alineacion['frases_en_originales']):
                        en_frase_txt = alineacion['frases_en_originales'][en_idx][:50] + "..."
                    else:
                        en_frase_txt = f"---ÍNDICE EN ({en_idx}) INVÁLIDO---"
                        
                    print(f"  ES[{es_idx}]: {es_frase[:50]}... -> EN[{en_idx}]: {en_frase_txt} (Score: {score:.3f})")
            else:
                print("  No se generaron alineaciones.")