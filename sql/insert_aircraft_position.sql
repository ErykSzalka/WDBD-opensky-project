INSERT INTO aircraft_positions (
    snapshot_time,
    icao24,
    callsign,
    origin_country,
    time_position,
    last_contact,
    longitude,
    latitude,
    baro_altitude,
    geo_altitude,
    on_ground,
    velocity,
    true_track,
    vertical_rate,
    squawk,
    spi,
    position_source
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (snapshot_time, icao24)
DO NOTHING;