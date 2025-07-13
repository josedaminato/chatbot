"""
Schemas para usuarios del dashboard usando Pydantic
Validaciones y documentación de estructuras de datos
"""

from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import datetime

class RolUsuario(str, Enum):
    """Roles de usuario disponibles"""
    ADMIN = "admin"
    PROFESIONAL = "profesional"
    ASISTENTE = "asistente"

class EstadoUsuario(str, Enum):
    """Estados de un usuario"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"

class UsuarioBase(BaseModel):
    """Schema base para usuarios"""
    username: str = Field(..., description="Nombre de usuario único")
    email: EmailStr = Field(..., description="Email del usuario")
    full_name: str = Field(..., description="Nombre completo")
    role: RolUsuario = Field(..., description="Rol del usuario")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Valida formato de nombre de usuario"""
        if not v or len(v) < 3:
            raise ValueError('El nombre de usuario debe tener al menos 3 caracteres')
        if not v.isalnum():
            raise ValueError('El nombre de usuario solo puede contener letras y números')
        return v.lower()
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        """Valida nombre completo"""
        if not v or len(v.strip()) < 2:
            raise ValueError('El nombre completo debe tener al menos 2 caracteres')
        return v.strip()

class UsuarioCreate(UsuarioBase):
    """Schema para crear un nuevo usuario"""
    password: str = Field(..., description="Contraseña del usuario", min_length=8)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Valida fortaleza de la contraseña"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UsuarioUpdate(BaseModel):
    """Schema para actualizar un usuario existente"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[RolUsuario] = None
    status: Optional[EstadoUsuario] = None
    password: Optional[str] = Field(None, description="Nueva contraseña (opcional)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Valida fortaleza de la contraseña si se proporciona"""
        if v is not None:
            if len(v) < 8:
                raise ValueError('La contraseña debe tener al menos 8 caracteres')
            if not any(c.isupper() for c in v):
                raise ValueError('La contraseña debe contener al menos una mayúscula')
            if not any(c.islower() for c in v):
                raise ValueError('La contraseña debe contener al menos una minúscula')
            if not any(c.isdigit() for c in v):
                raise ValueError('La contraseña debe contener al menos un número')
        return v

class UsuarioResponse(UsuarioBase):
    """Schema para respuesta de usuario"""
    id: int = Field(..., description="ID único del usuario")
    status: EstadoUsuario = Field(..., description="Estado actual del usuario")
    created_at: str = Field(..., description="Fecha de creación")
    last_login: Optional[str] = Field(None, description="Último login")
    updated_at: Optional[str] = Field(None, description="Fecha de última actualización")
    
    class Config:
        """Configuración del schema"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "dr.perez",
                "email": "dr.perez@clinica.com",
                "full_name": "Dr. Juan Pérez",
                "role": "profesional",
                "status": "activo",
                "created_at": "2024-01-10T10:00:00Z",
                "last_login": "2024-01-15T14:30:00Z",
                "updated_at": "2024-01-10T10:00:00Z"
            }
        }

class UsuarioLogin(BaseModel):
    """Schema para login de usuario"""
    username: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")

class UsuarioListResponse(BaseModel):
    """Schema para lista de usuarios"""
    usuarios: List[UsuarioResponse] = Field(..., description="Lista de usuarios")
    total: int = Field(..., description="Total de usuarios")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Usuarios por página")

class CambioPassword(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., description="Nueva contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Valida fortaleza de la nueva contraseña"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v 