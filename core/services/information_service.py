import os
from infrastructure.repositories.json_menu_repository import JSONMenuRepository

OPEN_TIME = os.getenv("OPEN_TIME", "09:00")
CLOSE_TIME = os.getenv("CLOSE_TIME", "00:00")

class InformationService:
    def __init__(self):
        self.menu_repo = JSONMenuRepository()
        pass

    def get_opening_hours(self) -> str:
        return f"El restaurante está abierto de {OPEN_TIME} a {CLOSE_TIME}, excepto los lunes que está cerrado."
    
    def get_opening_days(self) -> str:
        return "El restaurante está abierto de martes a domingo. Los lunes está cerrado."
    
    def get_menu_info(self) -> str:
        """Devuelve información del menú en formato legible."""
        dishes = self.menu_repo.get_menu_dishes()
        drinks = self.menu_repo.get_menu_drinks()

        info = "🍽️ *Menú del restaurante:*\n\n"

        info += "🍲 *Platos:*\n"
        for dish in dishes:
            info += f"{dish["id"]} - {dish["name"]}: {dish["price"]}€\n"

        info += "\n🍹 *Bebidas:*\n"
        for drink in drinks:
            info += f"{drink["id"]} - {drink["name"]}: {drink["price"]}€\n"
        
        return info
