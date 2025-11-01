from fastmcp import FastMCP
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services import booking_service

mcp = FastMCP("restaurant-mcp")

@mcp.tool
def find_table(guests: int, location: str, date: str, time: str):
    """
    Busca una mesa disponible para el número de comensales en una fecha/hora concretas.
    """
    return booking_service.find_table(guests, location, date, time)


@mcp.tool
def reserve_table(table_id: int, name: str, guests: int, date: str, time: str, phone: str):
    return booking_service.reserve_table(table_id, name, guests, date, time, phone)

@mcp.tool
def cancel_reservation(phone: str, date: str):
    return booking_service.cancel_reservation(phone, date)

@mcp.tool
def modify_reservation(phone: str, date: str, new_time: str = None, new_guests: int = None):
    return booking_service.modify_reservation(phone, date, new_time, new_guests)

@mcp.tool
def get_tables():
    return booking_service.get_tables()

@mcp.tool
def get_reservation(phone: str, date: str):
    return booking_service.get_reservation(phone, date)

@mcp.tool
def modify_reservation_by_id(reservation_id: int, new_time: str = None, new_date: str = None, new_guests: int = None):
    return booking_service.modify_reservation_by_id(reservation_id, new_time, new_date, new_guests)


if __name__ == "__main__":
    print("Iniciando servidor MCP de reservas...")
    mcp.run(transport="http", host="0.0.0.0", port=8000)
