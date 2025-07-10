"""
Schemas para notificaciones usando Pydantic
Validaciones y documentación de estructuras de datos
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

class TipoNotificacion(str, Enum):
    """Tipos de notificación disponibles"""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    SMS = "sms"

class EstadoNotificacion(str, Enum):
    """Estados de una notificación"""
    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    FALLIDA = "fallida"
    CANCELADA = "cancelada"

class NotificacionBase(BaseModel):
    """Schema base para notificaciones"""
    phone_number: str = Field(..., description="Número de teléfono del destinatario")
    message: str = Field(..., description="Mensaje a enviar")
    notification_type: TipoNotificacion = Field(..., description="Tipo de notificación")
    priority: Optional[str] = Field("normal", description="Prioridad de la notificación")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Valida formato de número de teléfono"""
        if not v or len(v) < 10:
            raise ValueError('Número de teléfono inválido')
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """Valida que el mensaje no esté vacío"""
        if not v or len(v.strip()) == 0:
            raise ValueError('El mensaje no puede estar vacío')
        return v.strip()

class NotificacionCreate(NotificacionBase):
    """Schema para crear una nueva notificación"""
    pass

class NotificacionUpdate(BaseModel):
    """Schema para actualizar una notificación existente"""
    phone_number: Optional[str] = None
    message: Optional[str] = None
    notification_type: Optional[TipoNotificacion] = None
    priority: Optional[str] = None
    status: Optional[EstadoNotificacion] = None

class NotificacionResponse(NotificacionBase):
    """Schema para respuesta de notificación"""
    id: int = Field(..., description="ID único de la notificación")
    status: EstadoNotificacion = Field(..., description="Estado actual de la notificación")
    created_at: str = Field(..., description="Fecha de creación")
    sent_at: Optional[str] = Field(None, description="Fecha de envío")
    error_message: Optional[str] = Field(None, description="Mensaje de error si falló")
    retry_count: int = Field(0, description="Número de reintentos")
    
    class Config:
        """Configuración del schema"""
        schema_extra = {
            "example": {
                "id": 1,
                "phone_number": "+5491112345678",
                "message": "Tu turno está confirmado para mañana a las 14:30",
                "notification_type": "whatsapp",
                "priority": "normal",
                "status": "enviada",
                "created_at": "2024-01-10T10:00:00Z",
                "sent_at": "2024-01-10T10:01:00Z",
                "error_message": None,
                "retry_count": 0
            }
        }

class NotificacionListResponse(BaseModel):
    """Schema para lista de notificaciones"""
    notificaciones: List[NotificacionResponse] = Field(..., description="Lista de notificaciones")
    total: int = Field(..., description="Total de notificaciones")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Notificaciones por página")

class RecordatorioSchema(BaseModel):
    """Schema para recordatorios de turnos"""
    turno_id: int = Field(..., description="ID del turno")
    phone_number: str = Field(..., description="Número de teléfono")
    appointment_date: str = Field(..., description="Fecha del turno")
    appointment_time: str = Field(..., description="Hora del turno")
    patient_name: Optional[str] = Field(None, description="Nombre del paciente")
    message_template: str = Field(..., description="Plantilla del mensaje")
    
    @validator('message_template')
    def validate_template(cls, v):
        """Valida que la plantilla tenga las variables necesarias"""
        required_vars = ['{fecha}', '{hora}', '{nombre_clinica}']
        for var in required_vars:
            if var not in v:
                raise ValueError(f'La plantilla debe incluir {var}')
        return v 