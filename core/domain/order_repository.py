from abc import ABC, abstractmethod
from typing import List, Dict, Any


class OrderRepository(ABC):
    """Contrato para cualquier fuente de datos de órdenes."""
    
    @abstractmethod
    def insert(self, order) -> None:
        """Insert a new order into the database."""
        pass