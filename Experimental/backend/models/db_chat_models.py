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