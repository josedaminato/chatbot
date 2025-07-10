"""
Schemas del proyecto Asistente de Salud
Validaciones y documentación de estructuras de datos usando Pydantic
"""

from .turno_schema import (
    TurnoBase, TurnoCreate, TurnoUpdate, TurnoResponse, 
    TurnoListResponse, EstadoTurno
)

from .notification_schema import (
    NotificacionBase, NotificacionCreate, NotificacionUpdate, 
    NotificacionResponse, NotificacionListResponse, RecordatorioSchema,
    TipoNotificacion, EstadoNotificacion
)

from .user_schema import (
    UsuarioBase, UsuarioCreate, UsuarioUpdate, UsuarioResponse,
    UsuarioListResponse, UsuarioLogin, CambioPassword,
    RolUsuario, EstadoUsuario
)

__all__ = [
    # Turnos
    'TurnoBase', 'TurnoCreate', 'TurnoUpdate', 'TurnoResponse', 
    'TurnoListResponse', 'EstadoTurno',
    
    # Notificaciones
    'NotificacionBase', 'NotificacionCreate', 'NotificacionUpdate',
    'NotificacionResponse', 'NotificacionListResponse', 'RecordatorioSchema',
    'TipoNotificacion', 'EstadoNotificacion',
    
    # Usuarios
    'UsuarioBase', 'UsuarioCreate', 'UsuarioUpdate', 'UsuarioResponse',
    'UsuarioListResponse', 'UsuarioLogin', 'CambioPassword',
    'RolUsuario', 'EstadoUsuario'
]
