from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ReservationRepository(ABC):
    """Contrato para cualquier fuente de datos de reservas."""
    
    @abstractmethod
    def find_by_phone_and_date(self, phone: str, date: str) -> List[Dict[str, Any]]:
        """Busca reservas por teléfono y fecha."""
        pass
    
    @abstractmethod
    def insert(self, reservation) -> None:
        """Inserta una nueva reserva."""
        pass
    
    @abstractmethod
    def delete_by_phone_and_date(self, phone: str, date: str) -> None:
        """Elimina una reserva por teléfono y fecha."""
        pass
    
    @abstractmethod
    def update(self, phone: str, date: str, updates: Dict[str, Any]) -> None:
        """Actualiza una reserva existente."""
        pass
