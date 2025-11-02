from infrastructure.db_repository import query

class TableRepository:
    def find_by_location_and_capacity(self, location: str, guests: int):
        return query("""
            SELECT * FROM tables
            WHERE location = ? AND capacity >= ?
            ORDER BY capacity ASC
        """, (location, guests))

    def is_table_available(self, table_id: int, date: str, time: str, duration: int):
        reservations = query("""
            SELECT time, duration FROM reservations
            WHERE table_id = ? AND date = ?
        """, (table_id, date))

        def to_minutes(t): h, m = map(int, t.split(":")); return h * 60 + m
        new_start, new_end = to_minutes(time), to_minutes(time) + duration

        for r in reservations:
            existing_start = to_minutes(r["time"])
            existing_end = existing_start + r["duration"]
            if not (new_end <= existing_start or new_start >= existing_end):
                return False
        return True

    def get_all_available(self):
        return query("SELECT * FROM tables WHERE available = 1")
