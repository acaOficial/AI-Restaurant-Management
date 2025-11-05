"""Implementación del repositorio de calendario usando Google Calendar API."""
from typing import Optional, Dict, Any
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.domain.calendar_repository import CalendarRepository
from infrastructure.external.google_auth import GoogleAuthManager


class GoogleCalendarRepository(CalendarRepository):
    """Repositorio para Google Calendar."""
    
    def __init__(self, calendar_id: str, credentials_path: str):
        """
        Inicializa el repositorio de Google Calendar.
        
        Args:
            calendar_id: ID del calendario de Google (ej: 'primary' o email)
            credentials_path: Ruta al archivo credentials.json
        """
        self.calendar_id = calendar_id
        self.auth_manager = GoogleAuthManager(credentials_path)
        self._service = None
    
    @property
    def service(self):
        """Obtiene el servicio de Google Calendar (lazy loading)."""
        if self._service is None:
            creds = self.auth_manager.get_credentials()
            if creds is None:
                raise Exception("No se pudieron obtener credenciales de Google")
            self._service = build('calendar', 'v3', credentials=creds)
        return self._service
    
    def create_event(
        self,
        title: str,
        description: str,
        start_datetime: str,
        end_datetime: str,
        attendee_email: Optional[str] = None
    ) -> Optional[str]:
        """
        Crea un evento en Google Calendar.
        
        Args:
            title: Título del evento
            description: Descripción
            start_datetime: Inicio en formato ISO 8601 (ej: '2025-01-15T20:00:00')
            end_datetime: Fin en formato ISO 8601
            attendee_email: Email del invitado (opcional)
            
        Returns:
            ID del evento creado o None si falla
        """
        try:
            # Preparar el evento
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'Europe/Madrid',  # Ajustar según tu zona horaria
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'Europe/Madrid',
                },
            }
            
            # Añadir invitado si se proporciona
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
                event['sendNotifications'] = True
            
            # Crear el evento
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                sendNotifications=bool(attendee_email)
            ).execute()
            
            return created_event.get('id')
            
        except HttpError as e:
            print(f"Error al crear evento en Google Calendar: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None
    
    def update_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None
    ) -> bool:
        """
        Actualiza un evento existente en Google Calendar.
        
        Args:
            event_id: ID del evento
            title: Nuevo título (opcional)
            description: Nueva descripción (opcional)
            start_datetime: Nueva fecha/hora inicio (opcional)
            end_datetime: Nueva fecha/hora fin (opcional)
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            # Obtener el evento actual
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Actualizar campos proporcionados
            if title:
                event['summary'] = title
            if description:
                event['description'] = description
            if start_datetime:
                event['start'] = {
                    'dateTime': start_datetime,
                    'timeZone': 'Europe/Madrid',
                }
            if end_datetime:
                event['end'] = {
                    'dateTime': end_datetime,
                    'timeZone': 'Europe/Madrid',
                }
            
            # Guardar cambios
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"Error al actualizar evento: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Elimina un evento de Google Calendar.
        
        Args:
            event_id: ID del evento a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return True
            
        except HttpError as e:
            print(f"Error al eliminar evento: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un evento.
        
        Args:
            event_id: ID del evento
            
        Returns:
            Diccionario con los datos del evento o None si no existe
        """
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                'id': event.get('id'),
                'title': event.get('summary'),
                'description': event.get('description'),
                'start': event.get('start', {}).get('dateTime'),
                'end': event.get('end', {}).get('dateTime'),
                'status': event.get('status'),
            }
            
        except HttpError as e:
            print(f"Error al obtener evento: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None
