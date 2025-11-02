import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener la ruta de la base de datos desde .env o usar valor por defecto
DB_PATH = os.getenv("DATABASE_PATH", "db/restaurant.sqlite")

print("DB_PATH:", DB_PATH)
print("¿Existe la base de datos?:", os.path.exists(DB_PATH))
print("Directorio actual de ejecución:", os.getcwd())

def get_connection():
    return sqlite3.connect(DB_PATH)

def query(sql, params=()):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def execute(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()
