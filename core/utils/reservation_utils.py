# utils/reservation_utils.py
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Cargar reglas de negocio desde .env
MIN_BOOKING_DURATION = int(os.getenv("MIN_BOOKING_DURATION_MINUTES", "60"))
MAX_BOOKING_DURATION = int(os.getenv("MAX_BOOKING_DURATION_MINUTES", "180"))
EXTRA_TIME_PER_GUEST = int(os.getenv("EXTRA_TIME_PER_GUEST_MINUTES", "15"))
LATE_DINNER_HOUR = int(os.getenv("LATE_DINNER_HOUR_THRESHOLD", "21"))
LATE_DINNER_EXTRA = int(os.getenv("LATE_DINNER_EXTRA_MINUTES", "30"))

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




def normalize_date(date_str: str) -> str:
    """
    Convierte fechas tipo '16/11/2025', '16-11-2025' o '2025/11/16'
    al formato estándar ISO 'YYYY-MM-DD'.
    """
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str