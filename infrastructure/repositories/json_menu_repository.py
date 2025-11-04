# TODO IMPLEMENTAR REPOSITORIO PARA LEER ITEMS DEL MENÚ DESDE UN FICHERO JSON
from core.domain.menu_repository import MenuRepository as IMenuRepository
import json
import os
from dotenv import load_dotenv

load_dotenv()
MENU_JSON = os.getenv("MENU_JSON", "resources/menu.json")

class JSONMenuRepository(IMenuRepository):
    def __init__(self, file_path=MENU_JSON):
        self.file_path = file_path
        self.menu_items = self.get_menu_items()

    def get_menu_items(self):
        """Devuelve todos los elementos del menú desde un fichero JSON."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            menu_items = json.load(file)
        return menu_items
    
    def get_menu_dishes(self):
        """Devuelve todos los platos del menú."""
        dishes = []
        for item in self.menu_items:
            if item['type'] == 'plato':
                dishes.append(item)
        
        return dishes
    
    def get_menu_drinks(self):
        """Devuelve todas las bebidas del menú."""
        drinks = []
        for item in self.menu_items:
            if item['type'] == 'bebida':
                drinks.append(item)
        
        return drinks
    
    def get_menu_dish_by_id(self, item_id):
        """Devuelve un plato del menú por su ID."""
        for item in self.menu_items:
            if item['type'] == 'plato' and item['id'] == item_id:
                return item
        return None
    
    def get_menu_drink_by_id(self, item_id):
        """Devuelve una bebida del menú por su ID."""
        for item in self.menu_items:
            if item['type'] == 'bebida' and item['id'] == item_id:
                return item
        return None
