# TODO IMplementar el repositorio para el menú
from abc import ABC, abstractmethod

class MenuRepository(ABC):
    """Contrato para cualquier fuente de datos del menú."""

    @abstractmethod
    def get_menu_items(self):
        """Devuelve todos los elementos del menú."""
        pass
    
    @abstractmethod
    def get_menu_dishes(self):
        """Devuelve todos los platos del menú."""
        pass

    @abstractmethod
    def get_menu_drinks(self):
        """Devuelve todas las bebidas del menú."""
        pass

    @abstractmethod
    def get_menu_dish_by_id(self, item_id):
        """Devuelve un plato del menú por su ID."""
        pass

    @abstractmethod
    def get_menu_drink_by_id(self, item_id):
        """Devuelve una bebida del menú por su ID."""
        pass
