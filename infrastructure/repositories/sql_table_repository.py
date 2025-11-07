"""Implementación SQL del repositorio de mesas."""
from typing import List, Dict, Any
from core.domain.table_repository import TableRepository as ITableRepository
from infrastructure.database.sql_connection import query


class SQLTableRepository(ITableRepository):
    """Implementación SQLite del repositorio de mesas."""
    
    def find_by_location_and_capacity(self, location: str, guests: int) -> List[Dict[str, Any]]:
        """Busca mesas por ubicación y capacidad mínima."""
        return query("""
            SELECT * FROM tables
            WHERE location = ? AND capacity >= ?
            ORDER BY capacity ASC
        """, (location, guests))

    def get_table_by_id(self, table_id: int) -> Dict[str, Any]:
        """Obtiene información de una mesa por su ID."""
        result = query("SELECT * FROM tables WHERE id = ?", (table_id,))
        return result[0] if result else None

    def is_table_available(self, table_id: int, date: str, time: str, duration: int) -> bool:
        """Verifica si una mesa está disponible en una fecha/hora específica."""
        reservations = query("""
            SELECT time, duration FROM reservations
            WHERE table_id = ? AND date = ?
        """, (table_id, date))

        def to_minutes(t: str) -> int:
            """Convierte HH:MM a minutos desde medianoche."""
            h, m = map(int, t.split(":"))
            return h * 60 + m
        
        new_start = to_minutes(time)
        new_end = new_start + duration

        for r in reservations:
            existing_start = to_minutes(r["time"])
            existing_end = existing_start + r["duration"]
            # Verificar si hay solapamiento
            if not (new_end <= existing_start or new_start >= existing_end):
                return False
        return True

    def get_all_available(self) -> List[Dict[str, Any]]:
        """Obtiene todas las mesas disponibles."""
        return query("SELECT * FROM tables WHERE available = 1")

