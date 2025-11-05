from typing import Optional
from datetime import datetime, timedelta
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
    def create_reservation(self, table_id: int, name: str, guests: int, date: str, time: str, phone: str):
        booking_date = BookingDate(date, time, self.holiday_repo)

        # Debug: imprimir la fecha normalizada y buscar duplicados
        normalized = booking_date.normalized_date()
        # print(f"[DEBUG] create_reservation: fecha original='{date}', normalizada='{normalized}'")
        # print(f"[DEBUG] create_reservation: buscando duplicados con phone='{phone}', date='{normalized}'")
        
        existing = self.reservation_repo.find_by_phone_and_date(phone, normalized)
        # print(f"[DEBUG] create_reservation: reservas encontradas={len(existing) if existing else 0}")
        if existing:
            print(f"[DEBUG] create_reservation: reservas existentes: {existing}")
        
        if existing:
            return {"success": False, "message": f"Ya existe una reserva registrada con el número {phone} para el {normalized}."}

        duration = estimate_duration(guests, time)
        if not self.table_repo.is_table_available(table_id, normalized, time, duration):
            return {"success": False, "message": f"La mesa {table_id} no está disponible a las {time} el {normalized}."}

        # Crear evento en Google Calendar si está configurado
        calendar_event_id = None
        if self.calendar_repo:
            calendar_event_id = self._create_calendar_event(name, guests, normalized, time, duration, phone)
        
        # Usar la fecha normalizada para guardar en la base de datos
        # print(f"[DEBUG] create_reservation: creando reserva con fecha='{normalized}'")
        reservation = Reservation(table_id, name, guests, normalized, time, phone, duration, calendar_event_id)
        self.reservation_repo.insert(reservation)
        
        message = f"Reserva creada con éxito (duración estimada: {duration} min)."
        if calendar_event_id:
            message += " Evento sincronizado con Google Calendar."
        
        return {
            "success": True,
            "message": message,
            "table_id": table_id,
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
    def _create_calendar_event(self, name: str, guests: int, date: str, time: str, duration: int, phone: str) -> Optional[str]:
        """Crea un evento en Google Calendar para la reserva."""
        try:
            # Construir fecha/hora en formato ISO 8601
            start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=duration)
            
            title = f"Reserva: {name} ({guests} personas)"
            description = f"Reserva para {guests} personas\nTeléfono: {phone}\nDuración estimada: {duration} min"
            
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
