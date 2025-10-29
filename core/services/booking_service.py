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

def reserve_table(table_id: int, name: str, guests: int, date: str, time: str):
    execute("UPDATE tables SET available = 0 WHERE id = ?", (table_id,))
    execute(
        "INSERT INTO reservations (table_id, name, guests, date, time) VALUES (?, ?, ?, ?, ?)",
        (table_id, name, guests, date, time),
    )
    return {"success": True, "table_id": table_id}

def get_tables():
    return query("SELECT * FROM tables WHERE available = 1")
