from core.domain.booking_date import BookingDate
from core.utils.reservation_utils import estimate_duration

class TableService:
    def __init__(self, table_repo, holiday_repo):
        self.table_repo = table_repo
        self.holiday_repo = holiday_repo


    def find_table(self, guests: int, location: str, date: str, time: str):
        date = BookingDate(date, time, self.holiday_repo)
        candidate_tables = self.table_repo.find_by_location_and_capacity(location, guests)
        duration = estimate_duration(guests, time)

        available_tables = []
        for table in candidate_tables:
            if self.table_repo.is_table_available(table["id"], date.normalized_date(), time, duration):
                available_tables.append(table)

        if not available_tables:
            return {"success": False, "message": "No hay mesas disponibles para esa fecha y hora."}

        return {"success": True, "available_tables": available_tables}
    

    # ============================================================
    # LISTAR MESAS DISPONIBLES
    # ============================================================
    def get_tables(self):
        tables = self.table_repo.get_all_available()
        if not tables:
            return {"success": False, "message": "No hay mesas disponibles."}
        return {"success": True, "tables": tables}
