from infrastructure.db_repository import DB_PATH, query

print("Ruta de la base de datos usada por el MCP:")
print(DB_PATH)
print()

try:
    tablas = query("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tablas detectadas:")
    for t in tablas:
        print(" -", t["name"])
except Exception as e:
    print("Error al leer la base de datos:", e)
