INSERT INTO aircraft (
    icao24,
    airline_code
)
VALUES (%s, %s)
ON CONFLICT (icao24) DO NOTHING;