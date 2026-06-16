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
    icao24: str                     # [0] Unikalny kod samolotu
    callsign: Optional[str]         # [1] Znak wywoławczy (np. LOT123)
    origin_country: str             # [2] Kraj pochodzenia samolotu
    time_position: Optional[int]    # [3] Czas ostatniej aktualizacji pozycji (Unix timestamp)
    last_contact: int               # [4] Czas ostatniej jakiejkolwiek wiadomości (Unix)
    longitude: Optional[float]      # [5] Długość geograficzna
    latitude: Optional[float]       # [6] Szerokość geograficzna
    baro_altitude: Optional[float]  # [7] Wysokość barometryczna (w metrach)
    on_ground: bool                 # [8] Czy samolot jest na ziemi
    velocity: Optional[float]       # [9] Prędkość względem ziemi (m/s)
    true_track: Optional[float]     # [10] Kąt toru lotu (0-360 stopni)
    vertical_rate: Optional[float]  # [11] Prędkość wznoszenia/opadania (m/s)
    sensors: Optional[List[int]]    # [12] ID sensorów (zazwyczaj null dla darmowego konta)
    geo_altitude: Optional[float]   # [13] Wysokość geometryczna (metry)
    squawk: Optional[str]           # [14] Kod transpondera
    spi: bool                       # [15] Wskaźnik specjalnego przeznaczenia (Special Purpose Indicator)
    position_source: int            # [16] Źródło pozycji (0 = ADS-B, 1 = ASTERIX, 2 = MLAT, 3 = FLARM)

    @classmethod
    def from_api_list(cls, data: list) -> 'RadarState':
        """
        Tworzy obiekt RadarState na podstawie surowej listy zwróconej przez /states/all.
        """
        # Czyścimy callsign tak samo jak w klasie Arrival
        clean_callsign = data[1]
        if clean_callsign and isinstance(clean_callsign, str):
            clean_callsign = clean_callsign.strip()

        # Aby uniknąć błędu IndexError, w przypadku gdyby API nagle zwróciło krótszą listę
        # upewniamy się, że mamy przynajmniej 17 elementów (co jest standardem OpenSky).
        if len(data) < 17:
            # Uzupełnia brakujące elementy wartościami None
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