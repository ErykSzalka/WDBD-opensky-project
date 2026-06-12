INSERT INTO aircraft (
    icao24,
    airline_code
)
VALUES (%s, %s)
ON CONFLICT (icao24) DO UPDATE SET
    airline_code = COALESCE(
        EXCLUDED.airline_code,
        aircraft.airline_code
    );