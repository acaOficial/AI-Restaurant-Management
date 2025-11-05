from core.domain.holiday_repository import HolidayRepository
from datetime import date, datetime
from dotenv import load_dotenv
import json
import os

load_dotenv()
OPEN_TIME = os.getenv("OPEN_TIME", "09:00")
CLOSE_TIME = os.getenv("CLOSE_TIME", "00:00")
MAX_BOOKING_TIME = os.getenv("MAX_BOOKING_TIME", "22:00")

class BookingDate:
    def __init__(self, date_str: str, time_str: str, holiday_repo: HolidayRepository):
        self.date_str = date_str
        self.time_str = time_str
        self.holiday_repo = holiday_repo
        
        self.date = self._parse_date(date_str)
        self.time = self._parse_time(time_str)

    def is_valid(self) -> bool:
        return not self.get_invalid_reason()
    
    def get_invalid_reason(self) -> str | None:
        # Usar la fecha normalizada
        normalized = self.normalized_date()
        holiday_name = self.holiday_repo.get_holiday_name(normalized)

        if holiday_name:
            return f"El restaurante está cerrado por festivo ({holiday_name}) el {normalized}."
        if self._is_closed_day():
            return f"El restaurante está cerrado por descanso el {normalized}. Los lunes no abrimos."
        if not self._is_within_opening_hours():
            return f"El restaurante está cerrado a las {self.time_str}. Nuestro horario de reserva es de {OPEN_TIME} a {MAX_BOOKING_TIME}."
        return None

    def _parse_date(self, date_str: str) -> datetime.date:
        """Normaliza y convierte la fecha a objeto date."""
        # Intentar varios formatos
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Formato de fecha no válido: {date_str}")

    def _parse_time(self, time_str: str) -> datetime.time:
        """Convierte una hora normalizada (HH:MM) a objeto time."""
        return datetime.strptime(time_str, "%H:%M").time()
    
    def _is_closed_day(self) -> bool:
        # El restaurante está cerrado el lunes
        return self.date.weekday() == 0

    def _is_within_opening_hours(self) -> bool:
        """Verifica si la hora está dentro del horario de apertura.
        
        Maneja el caso especial donde CLOSE_TIME es 00:00 (medianoche),
        que significa el final del día (23:59:59).
        """
        open_time = datetime.strptime(OPEN_TIME, "%H:%M").time()
        close_time = datetime.strptime(MAX_BOOKING_TIME, "%H:%M").time()
        
        if close_time == datetime.strptime("00:00", "%H:%M").time():
            return self.time >= open_time
        print(f"Comparando horas: {open_time} <= {self.time} <= {close_time}")
        return open_time <= self.time <= close_time
    
    def normalized_date(self) -> str:
        """Devuelve la fecha normalizada en formato YYYY-MM-DD."""
        return self.date.strftime("%Y-%m-%d")