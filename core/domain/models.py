from dataclasses import dataclass

@dataclass
class Table:
    id: int
    capacity: int
    location: str
    available: bool

@dataclass
class Reservation:
    id: int
    table_id: int
    name: str
    guests: int
    date: str
    time: str
