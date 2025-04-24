from fastapi import APIRouter, HTTPException, Depends
from typing import List
import google.generativeai as genai
import json
import os
# Importa los modelos Pydantic definidos en el paso 3
from models.db_chat_models import ChatRequest, ChatResponse, ChatMessageInput
# Importa configuración (si la separaste)
from config import MAX_SUGGESTED_REPLIES, GEMINI_MODEL_NAME # Import configuration from config.py

router = APIRouter(
    prefix="/api/v1/db-chat",
    tags=["db-chat"],
)

# --- Prompt del Sistema ---
# ¡Este prompt es CRUCIAL! Ajústalo según sea necesario.
SYSTEM_PROMPT_TEMPLATE = f"""
Eres un asistente experto en diseño de bases de datos relacionales. Tu objetivo es ayudar al usuario a definir y refinar
una estructura de base de datos (tablas, columnas, tipos de datos básicos [int, string, datetime, float, boolean], relaciones PK/FK).
Interactúa con el usuario de forma clara y concisa. Mantén la conversación enfocada en el diseño de la BD.
Basándote en TODA la conversación hasta ahora, genera el código Mermaid ER Diagram ACTUALIZADO que refleje el estado actual completo del diseño.
Además, proporciona exactamente {MAX_SUGGESTED_REPLIES} sugerencias útiles y cortas sobre qué podría preguntar o definir el usuario a continuación para avanzar.

IMPORTANTE: Debes formatear TODA tu respuesta como un único bloque de código JSON válido.
El JSON DEBE tener estas claves EXACTAS:
- "chat_reply": (string) Tu respuesta conversacional al último mensaje del usuario.
- "mermaid_code": (string o null) El código Mermaid ER Diagram completo y actualizado. Usa null si aún no hay nada que diagramar. El código debe empezar con 'erDiagram'.
- "suggested_responses": (array of strings) EXACTAMENTE {MAX_SUGGESTED_REPLIES} sugerencias de próximos pasos para el usuario. Debe ser un array, incluso si está vacío [].

NO incluyas NADA antes o después del bloque JSON. Ni explicaciones, ni saludos, ni ```json ```. Solo el JSON.

Ejemplo de respuesta JSON esperada:
{{
  "chat_reply": "Ok, he añadido la tabla 'Usuarios' con 'id' como PK y 'nombre'. ¿Qué otras columnas necesitas?",
  "mermaid_code": "erDiagram\\n    USERS {{ \\n        int id PK\\n        string nombre\\n    }}",
  "suggested_responses": [
    "Añadir columna 'email' de tipo string.",
    "¿El 'id' debe ser auto-incremental?",
    "Crear tabla 'Pedidos'."
  ]
}}
"""

@router.post("/", response_model=ChatResponse)
async def handle_db_chat(request: ChatRequest):
    # Remove the incorrect genai.api_key check here. API key is configured in config.py

    # Construir historial para Gemini (asegurando roles 'user'/'model')
    gemini_history = []
    for msg in request.messages:
         # Asegúrate de que el rol 'assistant' se mapea a 'model'
         role = "model" if msg.role == "assistant" else msg.role
         # Validar que solo sean user/model antes de añadir
         if role in ["user", "model"]:
              gemini_history.append({"role": role, "parts": [{"text": msg.content}]})
         else:
              print(f"Rol inválido encontrado y omitido: {msg.role}")


    # Configuración del modelo y generación
    # Considera añadir safety_settings si es necesario
    generation_config = genai.types.GenerationConfig(
         # candidate_count=1, # Por defecto es 1
         # stop_sequences=["..."], # Si necesitas detener en secuencias específicas
         # max_output_tokens=..., # Limitar tokens de salida
         temperature=0.6, # Ajusta creatividad
         # top_p=...,
         # top_k=...
    )

    try:
        # Initialize the model - wrap this in try/except as suggested
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            generation_config=generation_config,
            system_instruction=SYSTEM_PROMPT_TEMPLATE # Pasar el prompt como instrucción del sistema
        )
        # Enviar historial al modelo Gemini
        # El system prompt ya está en el modelo, solo pasamos el historial
        response = await model.generate_content_async(gemini_history) # Usar async

        # Extraer el texto de la respuesta (que esperamos sea un JSON)
        ai_response_text = response.text.strip() # strip() inicial quita espacios/saltos de línea externos

        # ----> NUEVO: Limpiar posible Markdown <----
        # Eliminar los ```json ... ``` si están presentes de forma segura
        cleaned_text = ai_response_text
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[len("```json"):].strip() # Quita el inicio y espacios/saltos internos
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-len("```")].strip() # Quita el final y espacios/saltos internos

        # Parsear el JSON de la respuesta de la IA (AHORA LIMPIA)
        try:
            # Usa la variable 'cleaned_text' que acabamos de preparar
            data = json.loads(cleaned_text)

            # Validar y extraer datos (con valores por defecto/manejo de errores)
            chat_reply = data.get("chat_reply", "Error: La IA no proporcionó una respuesta de chat.")
            mermaid_code = data.get("mermaid_code")
            suggested_replies = data.get("suggested_responses", [])

            # Validaciones/Limpieza adicional
            if not isinstance(chat_reply, str): chat_reply = str(chat_reply) # Forzar a string
            if mermaid_code is not None and not isinstance(mermaid_code, str): mermaid_code = None
            if not isinstance(suggested_replies, list): suggested_replies = []
            suggested_replies = [str(item) for item in suggested_replies if isinstance(item, (str, int, float))] # Limpiar sugerencias

            # Limpiar código Mermaid si está vacío o solo espacios
            if mermaid_code and not mermaid_code.strip():
                 mermaid_code = None

            # Crear y devolver la respuesta estructurada para el frontend
            return ChatResponse(
                reply=chat_reply,
                mermaid_code=mermaid_code,
                suggested_replies=suggested_replies[:MAX_SUGGESTED_REPLIES] # Asegurar el límite máximo
            )

        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON de Gemini: {e}")
            # Imprime AMBAS versiones para depurar si sigue fallando
            print(f"Respuesta ORIGINAL recibida de Gemini: {ai_response_text}")
            print(f"Respuesta LIMPIA intentada para JSON: {cleaned_text}")
            # Mantenemos el error 500 aquí porque es un fallo al procesar la estructura esperada
            raise HTTPException(status_code=500, detail="Error al procesar la respuesta estructurada de la IA.")
        except Exception as e: # Captura otras excepciones del parseo/validación
             print(f"Error procesando datos del JSON de Gemini: {e}")
             raise HTTPException(status_code=500, detail="Error interno al procesar datos de la IA.")


    except Exception as e:
        print(f"Error al interactuar con la API de Gemini: {e}")
        # Considera mapear errores específicos de la API de Gemini a códigos HTTP si es posible
        raise HTTPException(status_code=503, detail=f"Error al comunicarse con el servicio de IA: {e}")