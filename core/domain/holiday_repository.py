from abc import ABC, abstractmethod

class HolidayRepository(ABC):
    """Contrato para cualquier fuente de datos de festivos."""
    
    @abstractmethod
    def get_holiday_name(self, date_str: str) -> str | None:
        pass
