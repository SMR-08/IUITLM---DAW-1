from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessageInput(BaseModel):
    role: str = Field(..., pattern="^(user|model)$") # 'user' o 'model' (Gemini usa 'model')
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessageInput]

class ChatResponse(BaseModel):
    reply: str                   # Respuesta textual de la IA
    mermaid_code: Optional[str] = None # Código Mermaid generado
    suggested_replies: List[str] = [] # Lista de sugerencias para botones

# Modelos para la corrección de Mermaid
class MermaidFixRequest(BaseModel):
    incorrect_code: str = Field(..., description="Incorrect Mermaid ERD code string.")
    # Optional context can be added here if needed later

class MermaidFixResponse(BaseModel):
    fixed_code: Optional[str] = None # The corrected code if successful
    error_message: Optional[str] = None # An error message if correction failed