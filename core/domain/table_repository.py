from abc import ABC, abstractmethod
from typing import List, Dict, Any


class TableRepository(ABC):
    """Contrato para cualquier fuente de datos de mesas."""
    
    @abstractmethod
    def find_by_location_and_capacity(self, location: str, guests: int) -> List[Dict[str, Any]]:
        """Busca mesas por ubicación y capacidad mínima."""
        pass
    
    @abstractmethod
    def is_table_available(self, table_id: int, date: str, time: str, duration: int) -> bool:
        """Verifica si una mesa está disponible en una fecha/hora específica."""
        pass
    
    @abstractmethod
    def get_all_available(self) -> List[Dict[str, Any]]:
        """Obtiene todas las mesas disponibles."""
        pass
