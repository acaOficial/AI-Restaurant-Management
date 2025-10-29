import sqlite3

conn = sqlite3.connect("db/restaurant.sqlite")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tables (
    id INTEGER PRIMARY KEY,
    capacity INTEGER,
    location TEXT CHECK(location IN ('interior', 'terrace')),
    available INTEGER
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
    FOREIGN KEY(table_id) REFERENCES tables(id)
)
""")

# Ejemplo de mesas
cur.execute("DELETE FROM tables")
cur.executemany(
    "INSERT INTO tables (id, capacity, location, available) VALUES (?, ?, ?, ?)",
    [
        (1, 2, "interior", 1),
        (2, 4, "interior", 1),
        (3, 4, "terrace", 1),
        (4, 6, "interior", 1),
    ],
)

conn.commit()
conn.close()
print("✅ DB restaurante lista")
