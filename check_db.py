import sqlite3
import pandas as pd

# Conectar a la base de datos
conn = sqlite3.connect("db/restaurant.sqlite")

# Obtener todas las tablas
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print("=== TABLAS ENCONTRADAS ===")
print(tables, "\n")

# Mostrar todas las filas de cada tabla
for t in tables["name"]:
    print(f"==================== {t.upper()} ====================")
    try:
        df = pd.read_sql_query(f"SELECT * FROM {t};", conn)
        if df.empty:
            print("(La tabla está vacía)\n")
        else:
            print(df.to_string(index=False), "\n")
    except Exception as e:
        print(f"(Error leyendo {t}: {e})\n")

conn.close()
