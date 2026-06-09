INSERT INTO airports (
    icao_code,
    airport_name,
    city,
    country
)
VALUES (%s, %s, %s, %s)
ON CONFLICT (icao_code) DO NOTHING;