from dataclasses import dataclass
from typing import Optional
from typing import Optional, List

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

@dataclass
class RadarState:
    icao24: str               
    callsign: Optional[str]         
    origin_country: str            
    time_position: Optional[int]    
    last_contact: int               
    longitude: Optional[float]      
    latitude: Optional[float]       
    baro_altitude: Optional[float]  
    on_ground: bool                
    velocity: Optional[float]       
    true_track: Optional[float]     
    vertical_rate: Optional[float]  
    sensors: Optional[List[int]]    
    geo_altitude: Optional[float]   
    squawk: Optional[str]           
    spi: bool                       
    position_source: int            

    @classmethod
    def from_api_list(cls, data: list) -> 'RadarState':

        clean_callsign = data[1]
        if clean_callsign and isinstance(clean_callsign, str):
            clean_callsign = clean_callsign.strip()

        if len(data) < 17:
            data.extend([None] * (17 - len(data)))

        return cls(
            icao24=data[0],
            callsign=clean_callsign,
            origin_country=data[2],
            time_position=data[3],
            last_contact=data[4],
            longitude=data[5],
            latitude=data[6],
            baro_altitude=data[7],
            on_ground=bool(data[8]),
            velocity=data[9],
            true_track=data[10],
            vertical_rate=data[11],
            sensors=data[12],
            geo_altitude=data[13],
            squawk=data[14],
            spi=bool(data[15]),
            position_source=data[16] if data[16] is not None else 0
        )
