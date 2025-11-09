from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Reservation:
    table_id: int  # Mesa principal (o primera mesa si es combinación)
    name: str
    guests: int
    date: str
    time: str
    phone: str
    duration: int
    notes: Optional[str] = None
    calendar_event_id: Optional[str] = None
    merged_tables: Optional[str] = None  # JSON string con IDs de mesas combinadas: "[1,2,3]"
