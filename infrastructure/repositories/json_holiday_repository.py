import json, os
from core.domain.holiday_repository import HolidayRepository
from dotenv import load_dotenv

load_dotenv()
HOLIDAYS_JSON = os.getenv("HOLIDAYS_JSON", "data/holidays.json")

class JSONHolidayRepository(HolidayRepository):
    def get_holiday_name(self, date_str: str) -> str | None:
        try:
            if not os.path.exists(HOLIDAYS_JSON):
                print(f"[WARN] No se encontró {HOLIDAYS_JSON}")
                return None

            with open(HOLIDAYS_JSON, "r", encoding="utf-8") as f:
                holidays = json.load(f)

            for h in holidays:
                if h["date"].split(" ")[0] == date_str:
                    return h["name"]
            return None
        except Exception as e:
            print(f"[ERROR] JSONHolidayRepository: {e}")
            return None
