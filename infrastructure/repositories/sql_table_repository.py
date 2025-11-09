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
        """Verifica si una mesa está disponible en una fecha/hora específica.
        Debe considerar tanto reservas directas como mesas que forman parte de combinaciones."""
        
        # Buscar todas las reservas en la misma fecha
        all_reservations = query("""
            SELECT table_id, time, duration, merged_tables FROM reservations
            WHERE date = ?
        """, (date,))

        def to_minutes(t: str) -> int:
            """Convierte HH:MM a minutos desde medianoche."""
            h, m = map(int, t.split(":"))
            return h * 60 + m
        
        new_start = to_minutes(time)
        new_end = new_start + duration

        for r in all_reservations:
            existing_start = to_minutes(r["time"])
            existing_end = existing_start + r["duration"]
            
            # Verificar si hay solapamiento de horario
            if new_end <= existing_start or new_start >= existing_end:
                continue  # No hay solapamiento, pasar a siguiente reserva
            
            # Hay solapamiento de horario, verificar si afecta a esta mesa
            # 1. Verificar si la mesa está como table_id directo
            if r["table_id"] == table_id:
                return False
            
            # 2. Verificar si la mesa está en merged_tables
            if r["merged_tables"]:
                try:
                    import json
                    merged = json.loads(r["merged_tables"])
                    if table_id in merged:
                        return False
                except:
                    pass  # Si hay error al parsear JSON, ignorar
        
        return True

    def get_all_available(self) -> List[Dict[str, Any]]:
        """Obtiene todas las mesas disponibles."""
        return query("SELECT * FROM tables WHERE available = 1")

