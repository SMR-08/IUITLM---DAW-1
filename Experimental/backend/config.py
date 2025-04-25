from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("¡ADVERTENCIA! GEMINI_API_KEY no encontrada en las variables de entorno.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Google Generative AI configurado correctamente.")
    except Exception as e:
         print(f"Error configurando Google Generative AI: {e}")

# --- Configuración de Generación Principal ---
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # Modelo principal
MAX_SUGGESTED_REPLIES = int(os.getenv("MAX_SUGGESTED_REPLIES", 3))
GENERATION_TEMPERATURE = float(os.getenv("GENERATION_TEMPERATURE", 0.6)) # Temperatura para generación normal

# --- Configuración para Reintento de Formato JSON ---
# Puedes usar el mismo modelo o uno diferente si lo tienes
JSON_RETRY_MODEL_NAME = os.getenv("JSON_RETRY_MODEL_NAME", GEMINI_MODEL_NAME)
JSON_RETRY_TEMPERATURE = float(os.getenv("JSON_RETRY_TEMPERATURE", 0.2)) # Temperatura más BAJA para forzar estructura
MAX_JSON_RETRIES = int(os.getenv("MAX_JSON_RETRIES", 1)) # Número de reintentos (1 = 1 intento original + 1 reintento)

# --- Configuración para Corrección de Mermaid ---
# Puede ser un modelo más capaz o el mismo
MERMAID_FIX_MODEL_NAME = os.getenv("MERMAID_FIX_MODEL_NAME", GEMINI_MODEL_NAME)
MERMAID_FIX_TEMPERATURE = float(os.getenv("MERMAID_FIX_TEMPERATURE", 0.1)) # Temperatura muy baja para precisión sintáctica

# --- Texto para el Recordatorio de Formato ---
# Se añadirá al final del último mensaje del usuario
JSON_FORMAT_REMINDER = """
\n\n**¡ORDEN IMPORTANTE!** Tu respuesta DEBE ser **únicamente** el objeto JSON válido especificado en mis instrucciones iniciales, comenzando con `{` y terminando con `}`. No incluyas ningún otro texto ni markdown.
"""