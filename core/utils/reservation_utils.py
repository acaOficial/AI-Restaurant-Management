# utils/reservation_utils.py
from datetime import datetime
import json
import os
from dotenv import load_dotenv


load_dotenv()

# Cargar reglas de negocio desde .env
MIN_BOOKING_DURATION = int(os.getenv("MIN_BOOKING_DURATION_MINUTES", "60"))
MAX_BOOKING_DURATION = int(os.getenv("MAX_BOOKING_DURATION_MINUTES", "180"))
EXTRA_TIME_PER_GUEST = int(os.getenv("EXTRA_TIME_PER_GUEST_MINUTES", "15"))
LATE_DINNER_HOUR = int(os.getenv("LATE_DINNER_HOUR_THRESHOLD", "21"))
LATE_DINNER_EXTRA = int(os.getenv("LATE_DINNER_EXTRA_MINUTES", "30"))
OPEN_TIME = os.getenv("OPEN_TIME", "09:00")
CLOSE_TIME = os.getenv("CLOSE_TIME", "00:00")
HOLIDAYS_JSON = os.getenv("HOLIDAYS_JSON", "resources/holidays.json")

def estimate_duration(guests: int, time: str) -> int:
    """
    Estima la duración de la reserva (en minutos) según el número de personas y la hora.
    """
    base_duration = MIN_BOOKING_DURATION

    # Aumenta tiempo por cada persona adicional
    extra_time = max(0, guests - 2) * EXTRA_TIME_PER_GUEST

    # Cenas tardías suelen ser más largas
    hour = int(time.split(":")[0])
    if hour >= LATE_DINNER_HOUR:
        base_duration += LATE_DINNER_EXTRA

    duration = base_duration + extra_time

    # Limitar al máximo configurado
    return min(duration, MAX_BOOKING_DURATION)
