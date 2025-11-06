from fastmcp import FastMCP
import sys
import os
from dotenv import load_dotenv
from typing import Optional

# Añadir el directorio raíz al path para los imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar configuración
load_dotenv()

# Importar dependencias de las capas correctas
from core.services.booking_service import BookingService
from core.services.table_service import TableService
from core.services.information_service import InformationService

from infrastructure.repositories.sql_reservation_repository import SQLReservationRepository
from infrastructure.repositories.sql_table_repository import SQLTableRepository
from infrastructure.repositories.json_holiday_repository import JSONHolidayRepository
from infrastructure.repositories.google_calendar_repository import GoogleCalendarRepository

# ============================================================
# CONFIGURACIÓN DEL SERVIDOR MCP
# ============================================================
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "restaurant-mcp")
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

mcp = FastMCP(MCP_SERVER_NAME)

# ============================================================
# INYECCIÓN DE DEPENDENCIAS (FASE DE ARRANQUE)
# ============================================================
reservation_repo = SQLReservationRepository()
table_repo = SQLTableRepository()
holiday_repo = JSONHolidayRepository()

# Configurar Google Calendar si está habilitado
calendar_repo = None
if os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() == "true":
    try:
        calendar_repo = GoogleCalendarRepository(
            calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "resources/google_credentials.json")
        )
        print("✅ Google Calendar integrado correctamente")
    except Exception as e:
        print(f"⚠️ No se pudo conectar con Google Calendar: {e}")
        print("   Las reservas se crearán sin sincronización de calendario")

booking_service = BookingService(
    reservation_repo=reservation_repo,
    table_repo=table_repo,
    holiday_repo=holiday_repo,
    calendar_repo=calendar_repo
)

table_service = TableService(
    table_repo=table_repo,
    holiday_repo=holiday_repo
)

info_service = InformationService()

# ============================================================
# EXPOSICIÓN DE FUNCIONALIDADES A MCP
# ============================================================

@mcp.tool
def reserve_table(table_id: int, name: str, guests: int, date: str, time: str, phone: str, notes: Optional[str] = None):
    """Crea una nueva reserva. El parámetro 'notes' es opcional y puede incluir aclaraciones especiales (ej: silla para bebés, alergia, etc)."""
    return booking_service.create_reservation(table_id, name, guests, date, time, phone, notes)

@mcp.tool
def cancel_reservation(phone: str, date: str):
    """Cancela una reserva existente."""
    return booking_service.cancel_reservation(phone, date)

@mcp.tool
def modify_reservation_by_phone(phone: str, date: str, new_time: str = None, new_date: str = None, new_guests: int = None):
    """Modifica una reserva existente por teléfono."""
    updates = {k: v for k, v in {"time": new_time, "date": new_date, "guests": new_guests}.items() if v}
    return booking_service.modify_reservation(phone, date, updates)

@mcp.tool
def get_reservation(phone: str, date: str):
    """Obtiene la información de una reserva existente."""
    return booking_service.get_reservation(phone, date)

@mcp.tool
def find_table(guests: int, location: str, date: str, time: str):
    """Busca mesas disponibles."""
    return table_service.find_table(guests, location, date, time)

@mcp.tool
def get_tables():
    """Devuelve todas las mesas disponibles."""
    return table_service.get_tables()

@mcp.tool
def get_opening_hours():
    """Devuelve el horario de apertura del restaurante."""
    return info_service.get_opening_hours()

@mcp.tool
def is_open(date: str, time: str):
    """Indica si el restaurante está abierto en la fecha y hora especificadas. Devuelve el estado y la razón si está cerrado."""
    result = info_service.is_open(date, time, holiday_repo=holiday_repo)
    if not result:
        return {"status": "open", "message": "El restaurante está abierto en esa fecha y hora."}
    else:
        return {"status": "closed", "reason": result}

@mcp.tool
def get_opening_days():
    """Devuelve los días de apertura del restaurante."""
    return info_service.get_opening_days()


# ============================================================
# EJECUCIÓN DEL SERVIDOR MCP
# ============================================================
if __name__ == "__main__":
    print(f"Iniciando servidor MCP de reservas '{MCP_SERVER_NAME}'...")
    print(f"Host: {MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
    mcp.run(transport="http", host=MCP_SERVER_HOST, port=MCP_SERVER_PORT)
