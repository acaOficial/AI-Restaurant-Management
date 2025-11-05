"""Implementación SQL del repositorio de reservas."""
from typing import List, Dict, Any
from core.domain.reservation_repository import ReservationRepository as IReservationRepository
from infrastructure.database.sql_connection import query, execute


class SQLReservationRepository(IReservationRepository):
    """Implementación SQLite del repositorio de reservas."""
    
    def find_by_phone_and_date(self, phone: str, date: str) -> List[Dict[str, Any]]:
        """Busca reservas por teléfono y fecha."""
        return query("SELECT * FROM reservations WHERE phone = ? AND date = ?", (phone, date))

    def insert(self, reservation) -> None:
        """Inserta una nueva reserva."""
        execute("""
            INSERT INTO reservations (table_id, name, guests, date, time, phone, duration, calendar_event_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (reservation.table_id, reservation.name, reservation.guests,
              reservation.date, reservation.time, reservation.phone, reservation.duration,
              reservation.calendar_event_id))

    def delete_by_phone_and_date(self, phone: str, date: str) -> None:
        """Elimina una reserva por teléfono y fecha."""
        execute("DELETE FROM reservations WHERE phone = ? AND date = ?", (phone, date))

    def update(self, phone: str, date: str, updates: Dict[str, Any]) -> None:
        """Actualiza una reserva existente."""
        fields = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [phone, date]
        execute(f"UPDATE reservations SET {fields} WHERE phone = ? AND date = ?", tuple(values))

