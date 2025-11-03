import os

OPEN_TIME = os.getenv("OPEN_TIME", "09:00")
CLOSE_TIME = os.getenv("CLOSE_TIME", "00:00")

class InformationService:
    def __init__(self): 
        pass

    def get_opening_hours(self) -> str:
        return f"El restaurante está abierto de {OPEN_TIME} a {CLOSE_TIME}, excepto los lunes que está cerrado."
    
    def get_opening_days(self) -> str:
        return "El restaurante está abierto de martes a domingo. Los lunes está cerrado."
    
    def get_menu_info(self) -> str:
        pass