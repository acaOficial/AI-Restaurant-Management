from infrastructure.db_repository import query, execute

class ReservationRepository:
    def find_by_phone_and_date(self, phone: str, date: str):
        # print(f"[DEBUG] ReservationRepository.find_by_phone_and_date: phone='{phone}', date='{date}'")
        result = query("SELECT * FROM reservations WHERE phone = ? AND date = ?", (phone, date))
        # print(f"[DEBUG] ReservationRepository.find_by_phone_and_date: encontradas {len(result)} reservas")
        if result:
            for r in result:
                print(f"[DEBUG]   - Reserva: id={r.get('id')}, date='{r.get('date')}', time='{r.get('time')}'")
        return result

    def insert(self, reservation):
        execute("""
            INSERT INTO reservations (table_id, name, guests, date, time, phone, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (reservation.table_id, reservation.name, reservation.guests,
              reservation.date, reservation.time, reservation.phone, reservation.duration))

    def delete_by_phone_and_date(self, phone: str, date: str):
        execute("DELETE FROM reservations WHERE phone = ? AND date = ?", (phone, date))

    def update(self, phone: str, date: str, updates: dict):
        fields = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [phone, date]
        execute(f"UPDATE reservations SET {fields} WHERE phone = ? AND date = ?", tuple(values))
