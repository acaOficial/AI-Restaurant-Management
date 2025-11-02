from core.domain.booking_date import BookingDate
from core.domain.reservation import Reservation
from core.utils.reservation_utils import estimate_duration


class BookingService:
    """
    Capa de aplicación que coordina la lógica de reservas.
    Orquesta las entidades del dominio y los repositorios de infraestructura.
    """

    def __init__(self, reservation_repo, table_repo, holiday_repo):
        self.reservation_repo = reservation_repo
        self.table_repo = table_repo
        self.holiday_repo = holiday_repo
    
    # ============================================================
    # CREAR RESERVA
    # ============================================================
    def create_reservation(self, table_id: int, name: str, guests: int, date: str, time: str, phone: str):
        booking_date = BookingDate(date, time, self.holiday_repo)

        reason = booking_date.get_invalid_reason()
        if reason:
            return {"success": False, "message": reason}

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

        # Usar la fecha normalizada para guardar en la base de datos
        # print(f"[DEBUG] create_reservation: creando reserva con fecha='{normalized}'")
        reservation = Reservation(table_id, name, guests, normalized, time, phone, duration)
        self.reservation_repo.insert(reservation)
        return {
            "success": True,
            "message": f"Reserva creada con éxito (duración estimada: {duration} min).",
            "table_id": table_id,
            "duration": duration
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
        
        self.reservation_repo.update(phone, date, updates)
        return {"success": True, "message": f"Reserva modificada con éxito."}
