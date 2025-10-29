from infrastructure.db_repository import query, execute
from core.utils.reservation_utils import estimate_duration

def find_table(guests: int, location: str, date: str, time: str):
    """
    Busca una mesa que esté libre para el número de comensales en la fecha/hora dadas.
    """
    candidate_tables = query("""
        SELECT * FROM tables
        WHERE location = ? AND capacity >= ?
        ORDER BY capacity ASC
    """, (location, guests))

    duration = estimate_duration(guests, time)

    for table in candidate_tables:
        if is_table_available(table["id"], date, time, duration):
            return [table]

    return []


def reserve_table(table_id: int, name: str, guests: int, date: str, time: str, phone: str):
    # Comprobar si ya hay una reserva con ese teléfono ese día
    existing = query("""
        SELECT * FROM reservations
        WHERE date = ? AND phone = ?
    """, (date, phone))

    if existing:
        return {
            "success": False,
            "message": f"Ya existe una reserva registrada con el número {phone} para el {date}.",
        }

    duration = estimate_duration(guests, time)

    # ⚠️ Nueva comprobación de solapamiento
    if not is_table_available(table_id, date, time, duration):
        return {
            "success": False,
            "message": f"La mesa {table_id} no está disponible a las {time} el {date}.",
        }

    # Crear reserva (sin bloquear la mesa globalmente)
    execute(
        "INSERT INTO reservations (table_id, name, guests, date, time, phone, duration) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (table_id, name, guests, date, time, phone, duration),
    )

    return {
        "success": True,
        "table_id": table_id,
        "duration": duration,
        "message": f"Reserva creada con éxito (duración estimada: {duration} min)."
    }


def is_table_available(table_id: int, date: str, time: str, duration: int) -> bool:
    """
    Comprueba si una mesa está libre en la fecha/hora dadas considerando las reservas existentes.
    """
    # Todas las reservas activas para esa mesa en el mismo día
    reservations = query("""
        SELECT time, duration FROM reservations
        WHERE table_id = ? AND date = ?
    """, (table_id, date))

    # Convertimos la nueva reserva a minutos desde medianoche
    new_start = _to_minutes(time)
    new_end = new_start + duration

    for r in reservations:
        existing_start = _to_minutes(r["time"])
        existing_end = existing_start + r["duration"]

        # Solapamiento si los intervalos se cruzan
        if not (new_end <= existing_start or new_start >= existing_end):
            return False

    return True


def _to_minutes(t: str) -> int:
    """Convierte 'HH:MM' a minutos desde medianoche."""
    h, m = map(int, t.split(":"))
    return h * 60 + m



def get_tables():
    return query("SELECT * FROM tables WHERE available = 1")

