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
HOLIDAYS_JSON = os.getenv("HOLIDAYS_JSON", "data/holidays.json")

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


def is_valid_time(time_str: str) -> bool:
    """Comprueba si la hora está dentro del horario del restaurante."""
    try:
        time_requested = datetime.strptime(time_str, "%H:%M").time()
        return time_requested >= datetime.strptime(OPEN_TIME, "%H:%M").time() and time_requested <= datetime.strptime(CLOSE_TIME, "%H:%M").time()
    except ValueError:
        return False


def is_open_day(date_str: str) -> bool:
    """Devuelve True si el restaurante está abierto (martes a domingo)."""
    try:
        date = datetime.strptime(date_str, "%d/%m/%Y")
        return date.weekday() != 0  # 0 = lunes
    except ValueError:
        return False
    

def is_holiday(date_str: str):
    """Devuelve el nombre del festivo si la fecha es festiva, None si no lo es."""
    try:
        # Normalizar la fecha de entrada a formato YYYY-MM-DD
        date_normalized = normalize_date(date_str)
        
        # Leer el archivo de festivos
        if not os.path.exists(HOLIDAYS_JSON):
            print(f"[WARNING] Holidays file not found: {HOLIDAYS_JSON}")
            return None
            
        with open(HOLIDAYS_JSON, "r", encoding="utf-8") as f:
            holidays = json.load(f)
        
        # Comparar con cada festivo (extraer solo la fecha sin hora)
        for holiday in holidays:
            holiday_date = holiday["date"].split(" ")[0]  # "2025-01-01 00:00:00" -> "2025-01-01"
            if holiday_date == date_normalized:
                print(f"[DEBUG] is_holiday(): {date_normalized} es festivo ({holiday['name']})")
                return holiday['name']
        
        return None
    except Exception as e:
        print(f"[ERROR] is_holiday() error: {e}")
        return None
