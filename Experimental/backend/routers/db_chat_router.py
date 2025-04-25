from fastapi import APIRouter, HTTPException, Depends
from typing import List, Any, Dict, Optional
import google.generativeai as genai
import json
import copy # Para copiar el historial de mensajes
import os
from models.db_chat_models import ChatRequest, ChatResponse, ChatMessageInput, MermaidFixRequest, MermaidFixResponse
# >>> Importa todas las configuraciones necesarias
from config import (
    MAX_SUGGESTED_REPLIES, GEMINI_MODEL_NAME, GENERATION_TEMPERATURE,
    JSON_RETRY_MODEL_NAME, JSON_RETRY_TEMPERATURE, MAX_JSON_RETRIES,
    JSON_FORMAT_REMINDER, MERMAID_FIX_MODEL_NAME, MERMAID_FIX_TEMPERATURE
)
from utils.ai_response_parser import parse_gemini_chat_response, AIResponseParsingError

router = APIRouter(
    prefix="/api/v1/db-chat",
    tags=["db-chat"],
)

# --- Prompts y Datos de Ejemplo (sin cambios) ---
# ... mermaid_syntax_examples, examples_json_string, SYSTEM_PROMPT_TEMPLATE ...
# ... FIX_MERMAID_SYSTEM_PROMPT ...

# --- Datos de Ejemplo para Mermaid ERD Syntax ---
mermaid_syntax_examples = {
  "info": "Referencia de sintaxis para diagramas Mermaid ERD. Úsala SIEMPRE para generar el código `mermaid_code`. Presta especial atención a la sintaxis exacta de las RELACIONES.",
  "diagram_start": "El código SIEMPRE debe empezar con 'erDiagram'.",
  "basic_table_syntax": "TABLA_NOMBRE {\n    tipo_dato nombre_columna [PK] [\"comentario\"]\n    # ... más columnas\n}",
  "common_datatypes": ["int", "string", "text", "datetime", "date", "float", "double", "boolean", "decimal"],
  "primary_key_marker": "Usa 'PK' después del nombre de la columna para indicar la Clave Primaria. Ejemplo: `int id PK`",
  "foreign_key_info": "Las Claves Foráneas (FK) se definen implícitamente a través de las líneas de relación. No necesitas marcar 'FK' en la columna generalmente, la relación lo indica.",
  "relationship_syntax_general": "TABLA_A [cardinalidad_A]--[cardinalidad_B] TABLA_B : \"etiqueta_relacion\"",
  "relationship_examples": [
    { "description": "Relación Uno a Muchos (1:N): Un 'USER' puede tener muchos 'POSTS'.", "syntax": "USER ||--o{ POST : creates" },
    { "description": "Relación Uno a Uno (1:1): Un 'USER' tiene exactamente un 'PROFILE'.", "syntax": "USER ||--|| PROFILE : has" },
    { "description": "Relación Muchos a Muchos (N:M): Un 'STUDENT' puede inscribirse en muchos 'COURSE', y un 'COURSE' puede tener muchos 'STUDENT'. (Implica tabla intermedia)", "syntax": "STUDENT }o--o{ COURSE : enrolls" },
    { "description": "Relación Cero o Uno a Muchos (0..1:N): Un 'AUTHOR' puede (o no) tener muchos 'BOOKS'.", "syntax": "AUTHOR |o--o{ BOOK : writes" },
    { "description": "Relación Cero o Uno a Uno (0..1:1): Una 'PERSON' puede (o no) tener un 'PASSPORT'.", "syntax": "PERSON |o--|| PASSPORT : holds" },
    { "description": "Relación Uno a Cero o Muchos (1:0..N): Un 'DEPARTMENT' debe existir, pero puede (o no) tener 'EMPLOYEES'. (Misma sintaxis que 1:N)", "syntax": "DEPARTMENT ||--o{ EMPLOYEE : employs" },
    { "description": "Relación Recursiva Uno a Muchos (1:N): Un 'EMPLOYEE' (manager) puede supervisar a muchos otros 'EMPLOYEES'.", "syntax": "EMPLOYEE ||--o{ EMPLOYEE : manages" },
    { "description": "Relación Recursiva Muchos a Muchos (N:M): Un 'COMPONENT' puede estar compuesto por muchos otros 'COMPONENT' (y ser parte de muchos otros).", "syntax": "COMPONENT }o--o{ COMPONENT : includes" },
    { "description": "Relación con etiqueta clara indicando acción.", "syntax": "CUSTOMER ||--o{ ORDER : places" },
    { "description": "Relación indicando pertenencia (lado 'muchos' hacia lado 'uno').", "syntax": "ORDER }o--|| CUSTOMER : belongs_to" }
  ],
  "table_examples": [
      { "name": "USERS (Tabla simple con PK)", "code": "USERS {\n    int id PK\n    string username unique \"Nombre de usuario único\"\n    string email\n    datetime created_at\n}" },
      { "name": "POSTS (Tabla con relación a USERS)", "code": "POSTS {\n    int id PK\n    string title\n    text content\n    datetime published_at\n    int user_id \"FK a USERS.id\"\n}" },
      { "name": "COMMENTS (Tabla con relaciones a USERS y POSTS)", "code": "COMMENTS {\n    int id PK\n    text body\n    int user_id \"FK a USERS.id\"\n    int post_id \"FK a POSTS.id\"\n    datetime commented_at\n}" },
      { "name": "EMPLOYEES (Para relación recursiva)", "code": "EMPLOYEES {\n    int employee_id PK\n    string name\n    int manager_id \"FK a EMPLOYEES.employee_id, puede ser null\"\n}" }
  ]
}

# --- Convertir a cadena JSON para el prompt ---
# Usamos indent=None para una versión más compacta
examples_json_string = json.dumps(mermaid_syntax_examples, indent=None, ensure_ascii=False)


# --- Prompt del Sistema Mejorado ---
SYSTEM_PROMPT_TEMPLATE = f"""
**Tu Rol:** Eres 'DB-AI', un asistente experto y meticuloso especializado en diseño de bases de datos relacionales. Tu principal objetivo es ayudar al usuario a crear y refinar un diagrama Entidad-Relación (ERD) utilizando la sintaxis de Mermaid.

**Tu Misión:**
1.  **Comprender:** Analiza la solicitud del usuario en el contexto de TODA la conversación anterior.
2.  **Diseñar/Modificar:** Actualiza la estructura de la base de datos (tablas, columnas, tipos de datos, relaciones) según la petición.
3.  **Clarificar:** Si la solicitud es ambigua, especialmente sobre relaciones o tipos de datos, HAZ PREGUNTAS CLARAS Y CONCISAS para confirmar antes de implementar cambios complejos. No asumas relaciones sin confirmación. Pregunta sobre cardinalidad (uno, muchos, opcional).
4.  **Generar Código Mermaid:** Crea el código Mermaid ERD **completo y actualizado** que refleje el estado *actual* del diseño después de aplicar los cambios solicitados (o el estado anterior si solo hiciste preguntas). Usa **EXCLUSIVAMENTE** la sintaxis definida en la Referencia de Sintaxis Mermaid ERD proporcionada a continuación.
5.  **Responder:** Formula una respuesta conversacional clara (`chat_reply`) explicando qué cambios hiciste, por qué, o qué información necesitas.
6.  **Sugerir:** Proporciona EXACTAMENTE {{MAX_SUGGESTED_REPLIES}} sugerencias (`suggested_responses`) cortas y útiles para guiar al usuario sobre los próximos pasos lógicos (añadir otra tabla, definir una columna, establecer una relación, etc.).

**Referencia OBLIGATORIA de Sintaxis Mermaid ERD:**
Utiliza esta referencia SIEMPRE, especialmente para la sintaxis de las relaciones. Los tipos de datos comunes están listados.
```json
{examples_json_string}
```

**Reglas Estrictas de Salida (¡MUY IMPORTANTE!):**

Tu respuesta COMPLETA debe ser un ÚNICO BLOQUE DE CÓDIGO JSON VÁLIDO.

El objeto JSON raíz DEBE contener EXACTAMENTE estas tres claves:

"chat_reply": (string) Tu respuesta textual al usuario. Explica los cambios o haz preguntas.

"mermaid_code": (string o null) El código Mermaid ERD completo y actualizado según la referencia, empezando SIEMPRE con erDiagram. Usa null (el valor JSON null, no la cadena "null") si aún no hay nada que diagramar o si solo estás pidiendo clarificación sin cambiar el diagrama.

"suggested_responses": (array of strings) EXACTAMENTE {{MAX_SUGGESTED_REPLIES}} sugerencias cortas y accionables para el usuario. Debe ser un array JSON [], incluso si por alguna razón no puedes generar sugerencias.

ABSOLUTAMENTE NADA MÁS: No incluyas NINGÚN texto, explicación, saludo, comentario, ni bloques de código Markdown (como ```json ... ```) ANTES o DESPUÉS del objeto JSON. La respuesta debe empezar con {{ y terminar con }}.

**Ejemplo de Interacción y Salida JSON VÁLIDA Esperada:**

Usuario: "Necesito una tabla para usuarios con id y nombre."

Tu Salida (Solo el JSON):

{{
  "chat_reply": "¡Entendido! He creado la tabla 'USERS' con una columna 'id' de tipo entero como Clave Primaria (PK) y una columna 'name' de tipo string. ¿Qué otros detalles o tablas necesitas definir?",
  "mermaid_code": "erDiagram\\n    USERS {{\\n        int id PK\\n        string name\\n    }}",
  "suggested_responses": [
    "Añadir columna 'email' a USERS.",
    "Crear tabla 'ORDERS'.",
    "¿Debería 'name' ser único?"
  ]
}}

Usuario: "Añade email a usuarios y crea la tabla orders con id y customer_id. Relaciona users y orders."

Tu Salida (Solo el JSON):

{{
  "chat_reply": "Perfecto. He añadido la columna 'email' (string) a la tabla 'USERS'. También he creado la tabla 'ORDERS' con 'id' (int, PK) y 'customer_id' (int). Para relacionarlas, ¿asumo que un usuario puede tener muchos pedidos (relación uno a muchos)? Por favor, confirma la cardinalidad.",
  "mermaid_code": "erDiagram\\n    USERS {{\\n        int id PK\\n        string name\\n        string email\\n    }}\\n    ORDERS {{\\n        int id PK\\n        int customer_id\\n    }}",
  "suggested_responses": [
    "Sí, un usuario tiene muchos pedidos (1:N).",
    "No, la relación es diferente.",
    "Añadir columna 'order_date' a ORDERS."
  ]
}}

¡Ahora, procesa la solicitud del usuario siguiendo estas directrices!
"""

# >>> Endpoint de corrección Mermaid (modificado para usar config)
# ... (MermaidFixRequest, MermaidFixResponse sin cambios) ...


@router.post("/", response_model=ChatResponse)
async def handle_db_chat(request: ChatRequest):
    base_gemini_history = []
    for msg in request.messages:
        role = "model" if msg.role == "assistant" else msg.role
        if role in ["user", "model"]:
            base_gemini_history.append({"role": role, "parts": [{"text": msg.content}]})
        else:
            print(f"Rol inválido encontrado y omitido: {msg.role}")

    if not base_gemini_history:
         raise HTTPException(status_code=400, detail="No valid messages found in the request.")

    # Configuración de generación inicial
    generation_config = genai.types.GenerationConfig(temperature=GENERATION_TEMPERATURE)
    retry_generation_config = genai.types.GenerationConfig(temperature=JSON_RETRY_TEMPERATURE)

    last_parsed_data = None
    last_parsing_error = None

    # Bucle de intentos (original + reintentos)
    for attempt in range(MAX_JSON_RETRIES + 1): # +1 porque el primer intento es el 0
        is_retry = attempt > 0
        current_model_name = JSON_RETRY_MODEL_NAME if is_retry else GEMINI_MODEL_NAME
        current_gen_config = retry_generation_config if is_retry else generation_config
        current_history = copy.deepcopy(base_gemini_history) # Copia para no modificar la base

        # >>> Añadir recordatorio al último mensaje del usuario
        if current_history[-1]["role"] == "user":
            # Asegúrate de que 'parts' existe y tiene al menos un elemento
            if current_history[-1].get("parts") and isinstance(current_history[-1]["parts"], list) and len(current_history[-1]["parts"]) > 0:
                 # Asegúrate de que el último part tiene 'text'
                 if "text" in current_history[-1]["parts"][-1]:
                      current_history[-1]["parts"][-1]["text"] += JSON_FORMAT_REMINDER
                 else:
                      # Si el último part no tiene 'text', crea uno o añade uno nuevo (menos probable)
                       current_history[-1]["parts"].append({"text": JSON_FORMAT_REMINDER})
            else:
                 # Si 'parts' no existe o está vacío, inicialízalo
                 current_history[-1]["parts"] = [{"text": current_history[-1].get("parts", "") + JSON_FORMAT_REMINDER}] # O añade al contenido original si lo tienes
        else:
            # Si el último mensaje no es del usuario, podríamos añadir un mensaje de sistema forzado?
            # Por ahora, solo lo añadimos si el último es del usuario.
            print("Advertencia: El último mensaje no era del usuario, no se añadió recordatorio de formato.")


        raw_ai_response_text = None
        try:
            print(f"Intento {attempt + 1}/{MAX_JSON_RETRIES + 1} llamando a {current_model_name} con temp {current_gen_config.temperature}")
            model = genai.GenerativeModel(
                model_name=current_model_name,
                generation_config=current_gen_config,
                system_instruction=SYSTEM_PROMPT_TEMPLATE
            )
            response = await model.generate_content_async(current_history)
            raw_ai_response_text = response.text

            # >>> Intentar parsear la respuesta
            data = parse_gemini_chat_response(raw_ai_response_text)
            last_parsed_data = data # Guardar la data parseada exitosamente
            last_parsing_error = None # Resetear error si parseó bien
            print(f"Intento {attempt + 1} exitoso.")
            break # Salir del bucle si el parseo fue exitoso

        except AIResponseParsingError as e:
            print(f"Intento {attempt + 1} falló el parseo: {e}")
            last_parsing_error = e # Guardar el último error de parseo
            if attempt >= MAX_JSON_RETRIES:
                 print("Máximo número de reintentos de parseo alcanzado.")
                 # Lanzar excepción HTTP usando el último error guardado
                 error_detail = f"Error al procesar la respuesta de la IA tras {MAX_JSON_RETRIES + 1} intentos: {last_parsing_error}. Texto recibido (limpio): '{last_parsing_error.cleaned_text}'"
                 raise HTTPException(status_code=500, detail=error_detail)
            # Si no es el último intento, el bucle continuará automáticamente
            continue # Ir al siguiente intento

        except Exception as e:
            # Capturar errores de comunicación con la API de Gemini u otros inesperados
            print(f"Error general en el intento {attempt + 1}: {e}")
            # Si falla la comunicación, probablemente no tenga sentido reintentar
            detail_message = f"Error al comunicarse con el servicio de IA en el intento {attempt + 1}: {e}"
            if raw_ai_response_text:
                 detail_message += f". Respuesta RAW de IA (si existió): '{raw_ai_response_text[:200]}...'"
            raise HTTPException(status_code=503, detail=detail_message) # Usar 503 para error de servicio

    # Si salimos del bucle sin error (es decir, con 'break'), procesamos la data
    if last_parsed_data:
        try:
             # Validar y extraer datos
             chat_reply = last_parsed_data.get("chat_reply", "Error: 'chat_reply' missing.")
             mermaid_code = last_parsed_data.get("mermaid_code")
             suggested_replies = last_parsed_data.get("suggested_responses", [])

             # Validaciones/Limpieza adicional (como antes)
             if not isinstance(chat_reply, str): chat_reply = str(chat_reply)
             if mermaid_code is not None and (not isinstance(mermaid_code, str) or not mermaid_code.strip()): mermaid_code = None
             if not isinstance(suggested_replies, list): suggested_replies = []
             suggested_replies = [str(item) for item in suggested_replies if isinstance(item, (str, int, float, bool))]

             # Crear y devolver la respuesta
             return ChatResponse(
                reply=chat_reply,
                mermaid_code=mermaid_code,
                suggested_replies=suggested_replies[:MAX_SUGGESTED_REPLIES]
             )
        except Exception as e:
             # Error inesperado DESPUÉS de parsear JSON pero ANTES de devolver ChatResponse
             print(f"Error procesando datos parseados exitosamente: {e}")
             raise HTTPException(status_code=500, detail=f"Error interno procesando datos válidos de la IA: {e}. Datos: {last_parsed_data}")

    else:
         # Si salimos del bucle sin 'break' y sin 'last_parsed_data' (aunque no debería pasar si la lógica de reintento está bien)
         print("Error: Se completaron los intentos pero no hay datos parseados válidos.")
         # Usar el último error de parseo si existe
         if last_parsing_error:
              error_detail = f"Error final tras reintentos: {last_parsing_error}. Texto recibido (limpio): '{last_parsing_error.cleaned_text}'"
              raise HTTPException(status_code=500, detail=error_detail)
         else:
              # Caso muy raro
              raise HTTPException(status_code=500, detail="Error desconocido tras completar los intentos de comunicación con la IA.")


# >>> Endpoint de corrección Mermaid (modificado para usar config)
# ... (MermaidFixRequest, MermaidFixResponse sin cambios) ...
@router.post("/fix-mermaid", response_model=MermaidFixResponse)
async def fix_mermaid_code(request: MermaidFixRequest):
    if not request.incorrect_code or not request.incorrect_code.strip():
         return MermaidFixResponse(error_message="No code provided to fix.")

    fix_messages = [{"role": "user", "parts": [{"text": request.incorrect_code}]}]

    # >>> Usa la configuración para el modelo y temperatura de corrección
    fix_generation_config = genai.types.GenerationConfig(temperature=MERMAID_FIX_TEMPERATURE)
    current_fix_model_name = MERMAID_FIX_MODEL_NAME

    raw_fix_ai_response_text = None
    try:
        print(f"Llamando a modelo de corrección {current_fix_model_name} con temp {MERMAID_FIX_TEMPERATURE}")
        fix_model = genai.GenerativeModel(
            model_name=current_fix_model_name,
            generation_config=fix_generation_config,
            system_instruction=FIX_MERMAID_SYSTEM_PROMPT
        )
        fix_response = await fix_model.generate_content_async(fix_messages)
        raw_fix_ai_response_text = fix_response.text.strip()

        fixed_code = raw_fix_ai_response_text
        if not fixed_code or not fixed_code.strip().startswith("erDiagram"):
             print(f"AI fix model did not return valid looking code. Response: '{fixed_code}'")
             return MermaidFixResponse(
                 fixed_code=None,
                 error_message=f"El modelo no devolvió código Mermaid válido. Respuesta: '{fixed_code[:100]}...'"
             )

        return MermaidFixResponse(fixed_code=fixed_code)

    except Exception as e:
        print(f"Error calling AI fix model: {e}")
        error_detail = f"Error interno al intentar corregir: {e}"
        if raw_fix_ai_response_text:
             error_detail += f". Respuesta RAW: '{raw_fix_ai_response_text[:100]}...'"
        return MermaidFixResponse(fixed_code=None, error_message=error_detail)