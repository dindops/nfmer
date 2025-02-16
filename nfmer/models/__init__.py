from datetime import date
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class NFM_Event:
    url: str = ""
    event_programme: Dict = field(default_factory=Dict)
    location: str = ""
    date: date = date(9999, 12, 31)
    hour: str = "00:00:00"
