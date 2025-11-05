from dataclasses import dataclass
from typing import Optional

@dataclass
class Reservation:
    table_id: int
    name: str
    guests: int
    date: str
    time: str
    phone: str
    duration: int
    calendar_event_id: Optional[str] = None
