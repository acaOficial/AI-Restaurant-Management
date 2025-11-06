from typing import Optional, List
from datetime import datetime, timedelta
import json
from core.domain.booking_date import BookingDate
from core.domain.reservation import Reservation
from core.domain.calendar_repository import CalendarRepository
from core.utils.reservation_utils import estimate_duration


class BookingService:
    """
    Capa de aplicación que coordina la lógica de reservas.
    Orquesta las entidades del dominio y los repositorios de infraestructura.
    """

    def __init__(self, reservation_repo, table_repo, holiday_repo, calendar_repo: Optional[CalendarRepository] = None):
        self.reservation_repo = reservation_repo
        self.table_repo = table_repo
        self.holiday_repo = holiday_repo
        self.calendar_repo = calendar_repo
    
    # ============================================================
    # CREAR RESERVA
    # ============================================================
    def create_reservation(
        self, 
        table_id: int, 
        name: str, 
        guests: int, 
        date: str, 
        time: str, 
        phone: str, 
        notes: Optional[str] = None,
        merged_tables: Optional[List[int]] = None
    ):
        """
        Crea una reserva. Puede ser para una mesa individual o mesas combinadas.
        
        Args:
            table_id: ID de la mesa principal
            merged_tables: Lista de IDs si son mesas combinadas (ej: [1, 2, 3])
        """
        booking_date = BookingDate(date, time, self.holiday_repo)
        normalized = booking_date.normalized_date()
        
        existing = self.reservation_repo.find_by_phone_and_date(phone, normalized)
        if existing:
            return {"success": False, "message": f"Ya existe una reserva registrada con el número {phone} para el {normalized}."}

        duration = estimate_duration(guests, time)
        
        # Verificar disponibilidad de todas las mesas (individual o combinadas)
        tables_to_check = merged_tables if merged_tables else [table_id]
        for tid in tables_to_check:
            if not self.table_repo.is_table_available(tid, normalized, time, duration):
                return {"success": False, "message": f"La mesa {tid} no está disponible a las {time} el {normalized}."}

        # Crear evento en Google Calendar si está configurado
        calendar_event_id = None
        if self.calendar_repo:
            table_info = f"mesas {merged_tables}" if merged_tables else f"mesa {table_id}"
            calendar_event_id = self._create_calendar_event(name, guests, normalized, time, duration, phone, table_info)
        
        # Convertir lista de mesas a JSON si existe
        merged_tables_json = json.dumps(merged_tables) if merged_tables else None
        
        # Crear reserva
        reservation = Reservation(
            table_id=table_id,
            name=name,
            guests=guests,
            date=normalized,
            time=time,
            phone=phone,
            duration=duration,
            notes=notes,
            calendar_event_id=calendar_event_id,
            merged_tables=merged_tables_json
        )
        self.reservation_repo.insert(reservation)
        
        # Mensaje de confirmación
        if merged_tables:
            table_msg = f"mesas combinadas {merged_tables}"
        else:
            table_msg = f"mesa {table_id}"
        
        message = f"Reserva creada con éxito para {table_msg} (duración estimada: {duration} min)."
        if calendar_event_id:
            message += " Evento sincronizado con Google Calendar."
        
        return {
            "success": True,
            "message": message,
            "table_id": table_id,
            "merged_tables": merged_tables,
            "duration": duration,
            "calendar_event_id": calendar_event_id
        }

    # ============================================================
    # OBTENER UNA RESERVA
    # ============================================================
    def get_reservation(self, phone: str, date: str):
        date = BookingDate(date, "00:00", self.holiday_repo).normalized_date()
        reservation = self.reservation_repo.find_by_phone_and_date(phone, date)
        if not reservation:
            return {"success": False, "message": f"No existe ninguna reserva con el número {phone} para el {date}."}
        return {"success": True, "reservation": reservation[0]}

    # ============================================================
    # CANCELAR RESERVA
    # ============================================================
    def cancel_reservation(self, phone: str, date: str):
        date = BookingDate(date, "00:00", self.holiday_repo).normalized_date()
        existing = self.reservation_repo.find_by_phone_and_date(phone, date)
        if not existing:
            return {"success": False, "message": f"No existe ninguna reserva con el número {phone} para el {date}."}
        
        # Eliminar evento de Google Calendar si existe
        reservation = existing[0]
        if self.calendar_repo and reservation.get("calendar_event_id"):
            self.calendar_repo.delete_event(reservation["calendar_event_id"])
        
        self.reservation_repo.delete_by_phone_and_date(phone, date)
        return {"success": True, "message": f"Reserva eliminada con éxito para el {date} y número {phone}."}

    # ============================================================
    # MODIFICAR RESERVA
    # ============================================================
    def modify_reservation(self, phone: str, date: str, updates: dict):
        # Normalizar la fecha de búsqueda
        date = BookingDate(date, "00:00", self.holiday_repo).normalized_date()
        existing = self.reservation_repo.find_by_phone_and_date(phone, date)
        if not existing:
            return {"success": False, "message": f"No existe una reserva con el número {phone} para el {date}."}
        
        # Normalizar la nueva fecha en updates si existe
        if "date" in updates:
            updates["date"] = BookingDate(updates["date"], "00:00", self.holiday_repo).normalized_date()
        
        # Actualizar evento en Google Calendar si existe
        reservation = existing[0]
        if self.calendar_repo and reservation.get("calendar_event_id"):
            self._update_calendar_event(
                reservation["calendar_event_id"],
                reservation,
                updates
            )
        
        self.reservation_repo.update(phone, date, updates)
        return {"success": True, "message": f"Reserva modificada con éxito."}
    
    # ============================================================
    # MÉTODOS PRIVADOS PARA GOOGLE CALENDAR
    # ============================================================
    def _create_calendar_event(
        self, 
        name: str, 
        guests: int, 
        date: str, 
        time: str, 
        duration: int, 
        phone: str,
        table_info: str = None
    ) -> Optional[str]:
        """Crea un evento en Google Calendar para la reserva."""
        try:
            # Construir fecha/hora en formato ISO 8601
            start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=duration)
            
            title = f"Reserva: {name} ({guests} personas)"
            description = f"Reserva para {guests} personas\nTeléfono: {phone}\nDuración estimada: {duration} min"
            
            if table_info:
                description += f"\n{table_info}"
            
            event_id = self.calendar_repo.create_event(
                title=title,
                description=description,
                start_datetime=start_dt.isoformat(),
                end_datetime=end_dt.isoformat()
            )
            
            return event_id
        except Exception as e:
            print(f"Error al crear evento en calendario: {e}")
            return None
    
    def _update_calendar_event(self, event_id: str, current_reservation: dict, updates: dict):
        """Actualiza un evento existente en Google Calendar."""
        try:
            # Determinar nuevos valores
            new_date = updates.get("date", current_reservation["date"])
            new_time = updates.get("time", current_reservation["time"])
            new_name = updates.get("name", current_reservation["name"])
            new_guests = updates.get("guests", current_reservation["guests"])
            new_duration = updates.get("duration", current_reservation["duration"])
            
            # Construir nuevas fechas
            start_dt = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=new_duration)
            
            title = f"Reserva: {new_name} ({new_guests} personas)"
            description = f"Reserva para {new_guests} personas\nTeléfono: {current_reservation['phone']}\nDuración estimada: {new_duration} min"
            
            self.calendar_repo.update_event(
                event_id=event_id,
                title=title,
                description=description,
                start_datetime=start_dt.isoformat(),
                end_datetime=end_dt.isoformat()
            )
        except Exception as e:
            print(f"Error al actualizar evento en calendario: {e}")
