from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Dispositives(Enum):
    HEATPUMP = 0
    LIGHTBULB = 1
    TEMPERATURE_SENSOR = 2
    PRESENCE_SENSOR = 3

@dataclass
class SensorData:
    timestamp: datetime
    user_id: str
    value: int
    sensor: Dispositives

@dataclass
class Event:
    value: int
    timestamp: datetime = field(default_factory=datetime.now)

    
@dataclass
class Action:
    value: int
    user_id: str
    actuator: Dispositives


