from dataclasses import dataclass

@dataclass
class Reservation:
    table_id: int
    name: str
    guests: int
    date: str
    time: str
    phone: str
    duration: int
