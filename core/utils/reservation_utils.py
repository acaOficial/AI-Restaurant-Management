# utils/reservation_utils.py
from datetime import datetime

def estimate_duration(guests: int, time: str) -> int:
    """
    Estima la duración de la reserva (en minutos) según el número de personas y la hora.
    """
    base_duration = 60  # Duración mínima (1 hora)

    # Aumenta 15 min por cada persona adicional
    extra_time = max(0, guests - 2) * 15

    # Cenas suelen ser más largas
    hour = int(time.split(":")[0])
    if hour >= 21:
        base_duration += 30

    duration = base_duration + extra_time

    # Limitar a un máximo razonable (3 horas)
    return min(duration, 180)




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