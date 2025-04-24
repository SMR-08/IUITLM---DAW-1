from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("¡ADVERTENCIA! GEMINI_API_KEY no encontrada en las variables de entorno.")
    # Considera lanzar un error si es crítico para el inicio
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Google Generative AI configurado correctamente.")
    except Exception as e:
         print(f"Error configurando Google Generative AI: {e}")

# Configuración adicional
MAX_SUGGESTED_REPLIES = int(os.getenv("MAX_SUGGESTED_REPLIES", 3)) # Número de sugerencias
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # O el modelo que uses