# backend/routers/db_chat_router.py

import io
import zipfile
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse

# Importar la NUEVA función de alineación
try:
    from ..utils.nlp_processing import alinear_frases_con_similitud_semantica
except ImportError:
    from utils.nlp_processing import alinear_frases_con_similitud_semantica

log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG) # Descomentar para más detalle

router = APIRouter(
    prefix="/api/v1/corpus",
    tags=["corpus-tools"],
)

@router.post(
    "/align",
    response_class=StreamingResponse,
    summary="Alinea dos corpus (ES y EN) usando similitud semántica y devuelve un ZIP.",
    description=(
        "Recibe dos archivos de texto (español e inglés). "
        "Para cada frase en español, encuentra la frase más similar en inglés usando embeddings. "
        "El texto en español mantiene su orden original. El texto en inglés se reordena "
        "para que la línea N del archivo inglés corresponda a la frase más similar "
        "a la línea N (frase N) del archivo español. "
        "Los dos archivos resultantes se empaquetan en un ZIP."
    )
)
async def align_corpus_files_semantic(
    corpus_es: UploadFile = File(..., description="Archivo de texto en español (.txt)"),
    corpus_en: UploadFile = File(..., description="Archivo de texto en inglés (.txt)")
):
    try:
        log.info(f"Recibidos archivos para alineación semántica: ES='{corpus_es.filename}', EN='{corpus_en.filename}'")

        text_es_bytes = await corpus_es.read()
        text_en_bytes = await corpus_en.read()

        try:
            text_es_str = text_es_bytes.decode('utf-8')
            log.info(f"Archivo ES decodificado (primeros 100 chars): {text_es_str[:100].replace(chr(10), ' ')}")
        except UnicodeDecodeError:
            log.error("Error al decodificar el archivo en español. Asegúrate que es UTF-8.")
            raise HTTPException(status_code=400, detail="El archivo en español no pudo ser decodificado como UTF-8.")

        try:
            text_en_str = text_en_bytes.decode('utf-8')
            log.info(f"Archivo EN decodificado (primeros 100 chars): {text_en_str[:100].replace(chr(10), ' ')}")
        except UnicodeDecodeError:
            log.error("Error al decodificar el archivo en inglés. Asegúrate que es UTF-8.")
            raise HTTPException(status_code=400, detail="El archivo en inglés no pudo ser decodificado como UTF-8.")

        if not text_es_str.strip(): # Permitir que el inglés esté vacío si es necesario, pero no el español (base)
            log.warning("El archivo de corpus en español está vacío o solo contiene espacios.")
            raise HTTPException(status_code=400, detail="El archivo de corpus en español no puede estar vacío.")

        log.info("Iniciando alineación de frases con similitud semántica...")
        # Llamar a la NUEVA función de alineación
        alignment_data = alinear_frases_con_similitud_semantica(text_es_str, text_en_str)

        if alignment_data.get('error'):
            log.error(f"Error durante la alineación semántica: {alignment_data['error']}")
            raise HTTPException(status_code=500, detail=f"Error en el proceso de alineación: {alignment_data['error']}")

        frases_es_originales: List[str] = alignment_data.get('frases_es_originales', [])
        frases_en_originales: List[str] = alignment_data.get('frases_en_originales', [])
        # alineacion_es_a_en es una lista de (idx_es, idx_en_mejor_match, score_similitud)
        alineacion_es_a_en: List[tuple] = alignment_data.get('alineacion_es_a_en', [])

        log.info(f"Alineación semántica completada. {len(alineacion_es_a_en)} frases ES procesadas para alineación.")

        # --- LÓGICA DE RECONSTRUCCIÓN BASADA EN EL NUEVO FORMATO DE ALINEACIÓN ---
        
        # El archivo español mantiene su orden original
        final_output_lines_es = [frase.strip() for frase in frases_es_originales]

        # Crear el archivo inglés reordenado
        # Inicializar con líneas vacías, con la misma longitud que el español
        final_output_lines_en = [""] * len(frases_es_originales)

        # Un diccionario para rastrear qué frases EN ya han sido usadas (para el mejor match)
        # Esto es una heurística simple para evitar que la misma frase EN se use para múltiples frases ES
        # si resulta ser el "mejor" match global para varias. Podría mejorarse con algoritmos de asignación.
        used_en_indices = set()


        # Llenar las líneas EN basadas en la alineación
        # Ordenar las alineaciones por el score de similitud DESCENDENTE
        # para que los mejores matches tengan prioridad al "reclamar" una frase EN.
        # Esto es una heurística. Para una asignación óptima global, se necesitaría algo como el algoritmo Húngaro.
        sorted_alignments = sorted(alineacion_es_a_en, key=lambda x: x[2], reverse=True)

        for es_idx, en_idx_match, score in sorted_alignments:
            if 0 <= es_idx < len(final_output_lines_en) and final_output_lines_en[es_idx] == "": # Si la línea ES aún no tiene un EN asignado
                if en_idx_match is not None and 0 <= en_idx_match < len(frases_en_originales):
                    if en_idx_match not in used_en_indices:
                        final_output_lines_en[es_idx] = frases_en_originales[en_idx_match].strip()
                        used_en_indices.add(en_idx_match)
                        # log.debug(f"  Asignado ES[{es_idx}] -> EN[{en_idx_match}] (Score: {score:.3f})")
                    # else:
                        # log.debug(f"  EN[{en_idx_match}] ya usado. ES[{es_idx}] no obtendrá este match (Score: {score:.3f}). Buscando alternativa...")
                        # Aquí podríamos buscar el siguiente mejor match para es_idx que no esté en used_en_indices,
                        # pero eso complica la lógica. Por ahora, si el mejor está usado, la línea ES podría quedar vacía.
                # else: # en_idx_match es None (si se implementó umbral y no se superó)
                    # log.debug(f"  ES[{es_idx}] no tuvo un match EN válido (o por debajo del umbral).")
                    # La línea en final_output_lines_en[es_idx] permanecerá vacía
            # else:
                # log.debug(f" ES[{es_idx}] ya tiene un match EN o está fuera de rango.")


        # Iteración secundaria para frases ES que no obtuvieron su *mejor* match porque estaba usado
        # Esta es una heurística adicional, puede no ser perfecta.
        # Es importante tener una copia de cosine_scores si no se regenera en nlp_processing
        # Para esta implementación simplificada, nos quedamos con la primera pasada.
        # Si quieres una mejor asignación, considera algoritmos de matching o una lógica más compleja aquí.


        final_text_es_content = "\n".join(final_output_lines_es)
        final_text_en_content = "\n".join(final_output_lines_en)
        # --- FIN DE LA LÓGICA DE RECONSTRUCCIÓN ---

        log.info(f"Textos reconstruidos finales. ES: {len(final_output_lines_es)} líneas, EN: {len(final_output_lines_en)} líneas.")
        if final_output_lines_es:
            preview_len = min(5, len(final_output_lines_es))
            log.info(f"Ejemplo alineación (primeras {preview_len} líneas):")
            for i in range(preview_len):
                log.info(f"  ES[{i}]: '{final_output_lines_es[i]}' --- EN[{i}]: '{final_output_lines_en[i]}'")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("aligned_corpus_es.txt", final_text_es_content.encode('utf-8'))
            zip_file.writestr("aligned_corpus_en.txt", final_text_en_content.encode('utf-8'))
        
        zip_buffer.seek(0) 
        log.info("Archivos ZIP creados y listos para enviar.")

        es_basename = corpus_es.filename.rsplit('.', 1)[0][:15] if corpus_es.filename else "corpus_es"
        en_basename = corpus_en.filename.rsplit('.', 1)[0][:15] if corpus_en.filename else "corpus_en"
        zip_filename = f"aligned_sem_{es_basename}_{en_basename}.zip" # Añadido "sem" para distinguirlo
        
        headers = {
            'Content-Disposition': f'attachment; filename="{zip_filename}"'
        }
        return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)

    except HTTPException:
        raise 
    except Exception as e:
        log.exception("Error inesperado en /corpus/align endpoint (semántico)") 
        raise HTTPException(status_code=500, detail=f"Error interno del servidor (semántico): {str(e)}")