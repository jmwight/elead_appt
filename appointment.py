from dataclasses import dataclass
from eleadtime import Time

# Class that stores eleads appointment
@dataclass
class Appointment:
    when: Time
    new_or_used: bool
    vehicle: str
    confirmed: bool
    sold: bool
    salesperson: str
    private_cust: bool
