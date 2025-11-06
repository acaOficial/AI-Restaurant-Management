from core.domain.booking_date import BookingDate
from core.utils.reservation_utils import estimate_duration
from typing import List, Dict, Any, Optional
import json


class TableService:
    def __init__(self, table_repo, holiday_repo):
        self.table_repo = table_repo
        self.holiday_repo = holiday_repo

    def find_table(self, guests: int, location: str, date: str, time: str):
        """
        Busca una mesa disponible. Si no hay una mesa individual suficiente,
        intenta combinar mesas de la misma ubicación.
        """
        date_obj = BookingDate(date, time, self.holiday_repo)
        normalized_date = date_obj.normalized_date()
        duration = estimate_duration(guests, time)

        # 1. Buscar mesa individual que cumpla la capacidad
        candidate_tables = self.table_repo.find_by_location_and_capacity(location, guests)
        
        available_tables = []
        for table in candidate_tables:
            if self.table_repo.is_table_available(table["id"], normalized_date, time, duration):
                available_tables.append(table)

        if available_tables:
            return {"success": True, "available_tables": available_tables, "merged": False}

        # 2. Si no hay mesa individual, buscar combinación de mesas
        merged_option = self._find_merged_tables(guests, location, normalized_date, time, duration)
        
        if merged_option:
            return {
                "success": True,
                "available_tables": [merged_option],
                "merged": True,
                "message": f"Se combinarán {len(merged_option['table_ids'])} mesas para acomodar a {guests} personas"
            }

        return {"success": False, "message": "No hay mesas disponibles para esa fecha y hora."}
    
    def _find_merged_tables(
        self, 
        guests: int, 
        location: str, 
        date: str, 
        time: str, 
        duration: int
    ) -> Optional[Dict[str, Any]]:
        """
        Encuentra una combinación de mesas en la misma ubicación que sumen
        la capacidad necesaria.
        """
        # Obtener todas las mesas de esa ubicación (sin filtro de capacidad mínima)
        all_tables = self.table_repo.find_by_location_and_capacity(location, 1)
        
        # Filtrar solo las disponibles
        available_tables = []
        for table in all_tables:
            if self.table_repo.is_table_available(table["id"], date, time, duration):
                available_tables.append(table)
        
        if not available_tables:
            return None
        
        # Ordenar por capacidad descendente para optimizar combinaciones
        available_tables.sort(key=lambda t: t["capacity"], reverse=True)
        
        # Buscar combinación más eficiente (mínimo número de mesas)
        best_combination = self._find_best_combination(available_tables, guests)
        
        if not best_combination:
            return None
        
        # Crear objeto virtual de mesa combinada
        table_ids = [t["id"] for t in best_combination]
        total_capacity = sum(t["capacity"] for t in best_combination)
        
        return {
            "id": table_ids[0],  # Usar el ID de la primera mesa como principal
            "capacity": total_capacity,
            "location": location,
            "table_ids": table_ids,
            "merged_from": table_ids,
            "is_merged": True
        }
    
    def _find_best_combination(
        self, 
        tables: List[Dict[str, Any]], 
        target_capacity: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Encuentra la mejor combinación de mesas (mínimo número de mesas)
        que sume al menos la capacidad objetivo.
        """
        # Intentar con 2 mesas primero
        for i in range(len(tables)):
            for j in range(i + 1, len(tables)):
                if tables[i]["capacity"] + tables[j]["capacity"] >= target_capacity:
                    return [tables[i], tables[j]]
        
        # Intentar con 3 mesas
        for i in range(len(tables)):
            for j in range(i + 1, len(tables)):
                for k in range(j + 1, len(tables)):
                    if tables[i]["capacity"] + tables[j]["capacity"] + tables[k]["capacity"] >= target_capacity:
                        return [tables[i], tables[j], tables[k]]
        
        # Si necesita más de 3 mesas, no combinar (política del restaurante)
        return None
    

    # ============================================================
    # LISTAR MESAS DISPONIBLES
    # ============================================================
    def get_tables(self):
        tables = self.table_repo.get_all_available()
        if not tables:
            return {"success": False, "message": "No hay mesas disponibles."}
        return {"success": True, "tables": tables}
