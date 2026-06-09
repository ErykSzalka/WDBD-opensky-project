INSERT INTO arrivals (
    log_id,
    icao24,
    departure_airport,
    arrival_airport,
    callsign,
    departure_time,
    arrival_time,
    flight_duration_min
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (icao24, departure_time, arrival_time, arrival_airport)
DO NOTHING;