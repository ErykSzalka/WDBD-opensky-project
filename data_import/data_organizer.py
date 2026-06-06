from dataclasses import dataclass
from typing import Optional

@dataclass
class Arrival:
    icao24: str
    firstSeen: int
    estDepartureAirport: Optional[str]
    lastSeen: int
    estArrivalAirport: Optional[str]
    callsign: Optional[str]
    estDepartureAirportHorizDistance: Optional[int]
    estDepartureAirportVertDistance: Optional[int]
    estArrivalAirportHorizDistance: Optional[int]
    estArrivalAirportVertDistance: Optional[int]
    departureAirportCandidatesCount: int
    arrivalAirportCandidatesCount: int

    @classmethod
    def from_api_dict(cls, data: dict) -> 'Arrival':
        clean_callsign = data.get("callsign")
        if clean_callsign:
            clean_callsign = clean_callsign.strip()


        return cls(
            icao24=data.get("icao24"),
            firstSeen=data.get("firstSeen"),
            estDepartureAirport=data.get("estDepartureAirport"),
            lastSeen=data.get("lastSeen"),
            estArrivalAirport=data.get("estArrivalAirport"),
            callsign=clean_callsign,
            estDepartureAirportHorizDistance=data.get("estDepartureAirportHorizDistance"),
            estDepartureAirportVertDistance=data.get("estDepartureAirportVertDistance"),
            estArrivalAirportHorizDistance=data.get("estArrivalAirportHorizDistance"),
            estArrivalAirportVertDistance=data.get("estArrivalAirportVertDistance"),
            departureAirportCandidatesCount=data.get("departureAirportCandidatesCount", 0),
            arrivalAirportCandidatesCount=data.get("arrivalAirportCandidatesCount", 0)
        )