"""Interfaz abstracta para repositorios de calendario."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class CalendarRepository(ABC):
    """Contrato para cualquier servicio de calendario externo."""
    
    @abstractmethod
    def create_event(
        self,
        title: str,
        description: str,
        start_datetime: str,
        end_datetime: str,
        attendee_email: Optional[str] = None
    ) -> Optional[str]:
        """
        Crea un evento en el calendario.
        
        Args:
            title: Título del evento
            description: Descripción del evento
            start_datetime: Fecha/hora inicio (ISO 8601)
            end_datetime: Fecha/hora fin (ISO 8601)
            attendee_email: Email del invitado (opcional)
            
        Returns:
            ID del evento creado o None si falla
        """
        pass
    
    @abstractmethod
    def update_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None
    ) -> bool:
        """
        Actualiza un evento existente.
        
        Args:
            event_id: ID del evento a actualizar
            title: Nuevo título (opcional)
            description: Nueva descripción (opcional)
            start_datetime: Nueva fecha/hora inicio (opcional)
            end_datetime: Nueva fecha/hora fin (opcional)
            
        Returns:
            True si se actualizó correctamente
        """
        pass
    
    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """
        Elimina un evento del calendario.
        
        Args:
            event_id: ID del evento a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        pass
    
    @abstractmethod
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un evento.
        
        Args:
            event_id: ID del evento
            
        Returns:
            Diccionario con los datos del evento o None si no existe
        """
        pass
