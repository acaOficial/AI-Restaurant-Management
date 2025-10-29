from fastmcp import FastMCP
import sqlite3
import os

# === CONFIGURACIÓN DE BASE DE DATOS ===
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "db", "restaurant.sqlite")

if not os.path.exists(DB_PATH):
    print(f"Error: no se encontró la base de datos en {DB_PATH}")
else:
    print(f"Usando base de datos: {DB_PATH}")

mcp = FastMCP("restaurant-mcp")


def query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def execute(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()


@mcp.tool
def find_table(guests: int, location: str):
    """Busca una mesa disponible con capacidad suficiente."""
    return query(
        """
        SELECT * FROM tables
        WHERE available = 1
        AND location = ?
        AND capacity >= ?
        ORDER BY capacity ASC
        LIMIT 1
        """,
        (location, guests),
    )


@mcp.tool
def reserve_table(table_id: int, name: str, guests: int, date: str, time: str):
    """Reserva una mesa y la marca como no disponible."""
    execute("UPDATE tables SET available = 0 WHERE id = ?", (table_id,))
    execute(
        "INSERT INTO reservations (table_id, name, guests, date, time) VALUES (?, ?, ?, ?, ?)",
        (table_id, name, guests, date, time),
    )
    return {"success": True, "table_id": table_id}


@mcp.tool
def get_tables():
    """Devuelve todas las mesas disponibles."""
    return query("SELECT * FROM tables WHERE available = 1")


if __name__ == "__main__":
    print("Iniciando servidor MCP de reservas...")
    print(f"Base de datos: {DB_PATH}")
    mcp.run(transport="http", host="0.0.0.0", port=8000)
