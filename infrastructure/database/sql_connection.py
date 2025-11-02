"""Módulo de conexión y operaciones básicas de base de datos."""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener la ruta de la base de datos desde .env
DB_PATH = os.getenv("DATABASE_PATH", "resources/bookings.sqlite")


def get_connection():
    """Obtiene una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_PATH)


def query(sql: str, params: tuple = ()):
    """
    Ejecuta una consulta SELECT y retorna los resultados como lista de diccionarios.
    
    Args:
        sql: Sentencia SQL SELECT
        params: Parámetros para la consulta
        
    Returns:
        Lista de diccionarios con los resultados
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def execute(sql: str, params: tuple = ()):
    """
    Ejecuta una sentencia INSERT, UPDATE o DELETE.
    
    Args:
        sql: Sentencia SQL
        params: Parámetros para la sentencia
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()
