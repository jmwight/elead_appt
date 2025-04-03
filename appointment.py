from dataclasses import dataclass
from eleadtime import Time, TimeDelta

# Class that stores eleads appointment
@dataclass
class Appointment:
    start_time: Time
    delta: TimeDelta
    new: bool
    vehicle: str
    confirmed: bool
    sold: bool
    salesperson: str
    private_cust: bool
