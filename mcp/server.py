from fastapi import FastAPI
import sqlite3

app = FastAPI()

DB = "db/restaurant.sqlite"

def query(sql, params=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def execute(sql, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

@app.get("/getTables")
def get_tables():
    return query("SELECT * FROM tables WHERE available = 1")

@app.get("/findTable")
def find_table(guests: int, location: str):
    return query("""
        SELECT *
        FROM tables
        WHERE available = 1
        AND location = ?
        AND capacity >= ?
        ORDER BY capacity ASC
        LIMIT 1
    """, (location, guests))

@app.post("/reserveTable")
def reserve_table(table_id: int, name: str, guests: int, date: str, time: str):
    # marcar mesa ocupada
    execute("UPDATE tables SET available = 0 WHERE id = ?", (table_id,))
    # insertar reserva
    execute(
        "INSERT INTO reservations (table_id, name, guests, date, time) VALUES (?, ?, ?, ?, ?)",
        (table_id, name, guests, date, time),
    )
    return {"success": True, "table_id": table_id}