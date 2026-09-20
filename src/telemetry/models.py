from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class Observation:
    source: str
    source_series_id: str
    station_id: str
    
    metric: str
    value: Decimal | None
    unit: str 
    
    observed_at: datetime
    ingested_at: datetime
    
    latitude: float
    longitude: float
    
    source_quality: dict[str, object]
    