"""
Schema para validar datos entrantes del webhook (mensajes de WhatsApp/Twilio)
"""
from pydantic import BaseModel, Field
from typing import Optional

class MensajeEntradaSchema(BaseModel):
    From: str = Field(..., description="Número de teléfono del remitente (formato WhatsApp)")
    Body: str = Field(..., description="Texto del mensaje recibido")
    MediaContentType0: Optional[str] = Field(None, description="Tipo de contenido multimedia si existe")
    MediaUrl0: Optional[str] = Field(None, description="URL de la imagen o archivo multimedia si existe")
    MessageSid: Optional[str] = Field(None, description="SID del mensaje (para status webhooks)")
    MessageStatus: Optional[str] = Field(None, description="Estado del mensaje (para status webhooks)") 