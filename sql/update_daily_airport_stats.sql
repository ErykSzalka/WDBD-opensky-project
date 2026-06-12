INSERT INTO daily_airport_stats (
    icao_code,
    stat_date,
    arrival_count,
    avg_flight_duration_min
)
SELECT arrival_airport,
    arrival_time::date,
    COUNT(*),
    ROUND(AVG(flight_duration_min), 2)
FROM arrivals
WHERE arrival_airport IS NOT NULL
GROUP BY arrival_airport, arrival_time::date
ON CONFLICT (icao_code, stat_date)
DO UPDATE SET
    arrival_count = EXCLUDED.arrival_count,
    avg_flight_duration_min = EXCLUDED.avg_flight_duration_min;