from dataclasses import dataclass


@dataclass
class GeometryDTO:
    lat: float = None
    lng: float = None
    location_code = None
