from infrastructure.db_repository import query, execute
from core.utils.reservation_utils import estimate_duration, normalize_date, is_valid_time, is_open_day


# ============================================================
# BÚSQUEDA DE MESAS DISPONIBLES
# ============================================================
def find_table(guests: int, location: str, date: str, time: str):
    print(f"[DEBUG] find_table() called with guests={guests}, location={location}, date={date}, time={time}")
    date = normalize_date(date)

    candidate_tables = query("""
        SELECT * FROM tables
        WHERE location = ? AND capacity >= ?
        ORDER BY capacity ASC
    """, (location, guests))

    print(f"[DEBUG] find_table(): found {len(candidate_tables)} candidate tables")

    duration = estimate_duration(guests, time)
    print(f"[DEBUG] find_table(): estimated duration = {duration} min")

    for table in candidate_tables:
        if is_table_available(table["id"], date, time, duration):
            print(f"[DEBUG] find_table(): table {table['id']} is available")
            return [table]

    print("[DEBUG] find_table(): no tables available")
    return []


# ============================================================
# CREACIÓN DE RESERVAS
# ============================================================
def reserve_table(table_id: int, name: str, guests: int, date: str, time: str, phone: str):
    print(f"[DEBUG] reserve_table() called with table_id={table_id}, name={name}, guests={guests}, date={date}, time={time}, phone={phone}")
    date = normalize_date(date)

    if not is_valid_time(time) or not is_open_day(date):
        return {
            "success": False,
            "message": "El restaurante está cerrado en la fecha u hora solicitada.",
        }

    existing = query("""
        SELECT * FROM reservations
        WHERE date = ? AND phone = ?
    """, (date, phone))
    print(f"[DEBUG] reserve_table(): found {len(existing)} existing reservations for phone={phone} on date={date}")

    if existing:
        return {
            "success": False,
            "message": f"Ya existe una reserva registrada con el número {phone} para el {date}.",
        }

    duration = estimate_duration(guests, time)
    print(f"[DEBUG] reserve_table(): estimated duration = {duration} min")

    if not is_table_available(table_id, date, time, duration):
        print(f"[DEBUG] reserve_table(): table {table_id} not available at {time} on {date}")
        return {
            "success": False,
            "message": f"La mesa {table_id} no está disponible a las {time} el {date}.",
        }

    execute(
        "INSERT INTO reservations (table_id, name, guests, date, time, phone, duration) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (table_id, name, guests, date, time, phone, duration),
    )

    print(f"[DEBUG] reserve_table(): reservation created successfully for table {table_id}")

    return {
        "success": True,
        "table_id": table_id,
        "duration": duration,
        "message": f"Reserva creada con éxito (duración estimada: {duration} min)."
    }


# ============================================================
# CANCELACIÓN DE RESERVAS
# ============================================================
def cancel_reservation(phone: str, date: str):
    print(f"[DEBUG] cancel_reservation() called with phone={phone}, date={date}")
    date = normalize_date(date)

    existing = query("""
        SELECT * FROM reservations
        WHERE date = ? AND phone = ?
    """, (date, phone))
    print(f"[DEBUG] cancel_reservation(): found {len(existing)} reservations")

    if not existing:
        return {
            "success": False,
            "message": f"No existe ninguna reserva registrada con el número {phone} para el {date}.",
        }

    execute("DELETE FROM reservations WHERE date = ? AND phone = ?", (date, phone))
    print(f"[DEBUG] cancel_reservation(): reservation deleted for phone={phone} and date={date}")

    return {
        "success": True,
        "message": f"Reserva eliminada con éxito para el {date} y el número {phone}.",
    }


# ============================================================
# OBTENER Y MODIFICAR RESERVAS
# ============================================================
def get_reservation(phone: str, date: str):
    print(f"[DEBUG] get_reservation() called with phone={phone}, date={date}")
    date = normalize_date(date)

    result = query("""
        SELECT * FROM reservations
        WHERE phone = ? AND date = ?
    """, (phone, date))
    print(f"[DEBUG] get_reservation(): found {len(result)} results")

    if not result:
        return {
            "success": False,
            "message": f"No existe ninguna reserva registrada con el número {phone} para el {date}.",
        }

    return {"success": True, "reservation": result[0]}


def modify_reservation_by_id(reservation_id: int, new_time: str = None, new_date: str = None, new_guests: int = None):
    print(f"[DEBUG] modify_reservation_by_id() called with reservation_id={reservation_id}, new_time={new_time}, new_date={new_date}, new_guests={new_guests}")
    if new_date:
        new_date = normalize_date(new_date)

    if new_time and not is_valid_time(new_time) or (new_date and not is_open_day(new_date)):
        return {
            "success": False,
            "message": "El restaurante está cerrado en la fecha u hora solicitada.",
        }

    existing = query("SELECT * FROM reservations WHERE id = ?", (reservation_id,))
    print(f"[DEBUG] modify_reservation_by_id(): existing reservation found = {bool(existing)}")

    if not existing:
        return {"success": False, "message": f"No existe una reserva con ID {reservation_id}."}

    fields, values = [], []

    if new_date:
        fields.append("date = ?")
        values.append(new_date)
    if new_time:
        fields.append("time = ?")
        values.append(new_time)
    if new_guests:
        fields.append("guests = ?")
        values.append(new_guests)

    if not fields:
        print("[DEBUG] modify_reservation_by_id(): no new data provided")
        return {"success": False, "message": "No se proporcionaron nuevos datos para modificar."}

    set_clause = ", ".join(fields)
    values.append(reservation_id)

    execute(f"UPDATE reservations SET {set_clause} WHERE id = ?", tuple(values))
    print(f"[DEBUG] modify_reservation_by_id(): reservation {reservation_id} updated successfully")

    return {"success": True, "message": "Reserva modificada con éxito."}


# ============================================================
# DISPONIBILIDAD DE MESAS
# ============================================================
def is_table_available(table_id: int, date: str, time: str, duration: int) -> bool:
    print(f"[DEBUG] is_table_available() called with table_id={table_id}, date={date}, time={time}, duration={duration}")
    date = normalize_date(date)

    reservations = query("""
        SELECT time, duration FROM reservations
        WHERE table_id = ? AND date = ?
    """, (table_id, date))
    print(f"[DEBUG] is_table_available(): found {len(reservations)} reservations for that date")

    new_start = _to_minutes(time)
    new_end = new_start + duration

    for r in reservations:
        existing_start = _to_minutes(r["time"])
        existing_end = existing_start + r["duration"]
        if not (new_end <= existing_start or new_start >= existing_end):
            print(f"[DEBUG] is_table_available(): overlap detected with existing reservation from {r['time']} ({r['duration']} min)")
            return False

    print(f"[DEBUG] is_table_available(): table {table_id} is available")
    return True


# ============================================================
# UTILIDADES
# ============================================================
def _to_minutes(t: str) -> int:
    """Convierte 'HH:MM' a minutos desde medianoche."""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def get_tables():
    """Devuelve todas las mesas disponibles."""
    print("[DEBUG] get_tables() called")
    tables = query("SELECT * FROM tables WHERE available = 1")
    print(f"[DEBUG] get_tables(): found {len(tables)} tables available")
    return tables
