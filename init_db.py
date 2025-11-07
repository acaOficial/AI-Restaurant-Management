import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener la ruta de la base de datos desde .env
DB_PATH = os.getenv("DATABASE_PATH", "db/restaurant.sqlite")

# Crear el directorio si no existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Eliminar tablas existentes para recrearlas con la nueva estructura
cur.execute("DROP TABLE IF EXISTS reservations")
cur.execute("DROP TABLE IF EXISTS tables")
cur.execute("DROP TABLE IF EXISTS orders")

cur.execute("""
CREATE TABLE IF NOT EXISTS tables (
    id INTEGER PRIMARY KEY,
    capacity INTEGER,
    location TEXT CHECK(location IN ('interior', 'terrace'))
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id INTEGER,
    name TEXT,
    guests INTEGER,
    date TEXT,
    time TEXT,
    phone TEXT,
    duration INTEGER,
    notes TEXT,
    calendar_event_id TEXT,
    merged_tables TEXT,
    FOREIGN KEY(table_id) REFERENCES tables(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    items TEXT,
    total_price REAL,
    status TEXT,
    customer_phone TEXT,
    delivery_address TEXT
)""")


# Ejemplo de mesas
cur.execute("DELETE FROM tables")
cur.executemany(
    "INSERT INTO tables (id, capacity, location) VALUES (?, ?, ?)",
    [
        (1, 2, "interior"),
        (2, 2, "interior"),
        (3, 4, "interior"),
        (4, 3, "terrace"),
        (5, 3, "terrace"),
        (6, 6, "interior")
    ],
)

conn.commit()
conn.close()
print(f"✅ Base de datos creada en: {DB_PATH}")
