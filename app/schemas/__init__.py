# Schemas de validación

from .turno_schema import TurnoCreate, TurnoUpdate, TurnoResponse, TurnoListResponse, EstadoTurno
from .user_schema import UsuarioLogin, UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioListResponse, RolUsuario, EstadoUsuario
from .notification_schema import NotificacionCreate, NotificacionResponse, NotificacionListResponse
from .mensaje_entrada_schema import MensajeEntradaSchema

__all__ = [
    # Turno schemas
    'TurnoCreate', 'TurnoUpdate', 'TurnoResponse', 'TurnoListResponse', 'EstadoTurno',
    # User schemas
    'UsuarioLogin', 'UsuarioCreate', 'UsuarioUpdate', 'UsuarioResponse', 'UsuarioListResponse', 'RolUsuario', 'EstadoUsuario',
    # Notification schemas
    'NotificacionCreate', 'NotificacionResponse', 'NotificacionListResponse',
    # Message schemas
    'MensajeEntradaSchema'
]
