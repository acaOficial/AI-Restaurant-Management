from infrastructure.db_repository import query, execute

def find_table(guests: int, location: str):
    result = query("""
        SELECT * FROM tables
        WHERE available = 1
        AND location = ?
        AND capacity >= ?
        ORDER BY capacity ASC
        LIMIT 1
    """, (location, guests))
    return result

def reserve_table(table_id: int, name: str, guests: int, date: str, time: str, phone: str):
    existing = query("""
        SELECT * FROM reservations
        WHERE date = ? AND phone = ?
    """, (date, phone))

    if existing:
        return {
            "success": False,
            "message": f"Ya existe una reserva registrada con el número {phone} para el {date}.",
        }

    execute("UPDATE tables SET available = 0 WHERE id = ?", (table_id,))
    execute(
        "INSERT INTO reservations (table_id, name, guests, date, time, phone) VALUES (?, ?, ?, ?, ?, ?)",
        (table_id, name, guests, date, time, phone),
    )
    return {"success": True, "table_id": table_id, "message": "Reserva creada con éxito."}


def get_tables():
    return query("SELECT * FROM tables WHERE available = 1")
