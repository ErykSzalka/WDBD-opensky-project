import pandas as pd

def flights_by_min_duration(min_minutes: float, connection) -> pd.DataFrame | None:
    """
    Zwraca loty których czas trwania >= min_minutes
    """
    if not isinstance(min_minutes, (int, float)):
        raise ValueError("Czas trwania musi być liczbą")
    
    if min_minutes < 0:
        raise ValueError("Czas trwania musi być dodatni")
    
    zapytanie = f"""
    SELECT
    arrival_id,
    callsign,
    departure_airport,
    arrival_airport,
    flight_duration_min
    FROM arrivals
    WHERE flight_duration_min >= {min_minutes}
    ORDER BY flight_duration_min DESC;
    """
    return pd.read_sql(zapytanie, connection)

def airport_traffic_by_country(country_name: str, connection) -> pd.DataFrame | None:
    """
    Zwraca ruch lotniczy dla danego kraju
    """
    if not isinstance(country_name, str):
        raise ValueError("Niepoprawna nazwa kraju")
    
    zapytanie = f"""
    SELECT
    a.icao_code AS icao_code,
    a.airport_name AS airport_name,
    a.city AS city,
    COUNT(arr.arrival_id) AS total_arrivals
    FROM airports a
    JOIN arrivals arr ON a.icao_code = arr.arrival_airport
    WHERE a.country = '{country_name}'
    GROUP BY a.icao_code, a.airport_name, a.city
    ORDER BY total_arrivals DESC;
    """
    return pd.read_sql(zapytanie, connection)

def airlines_flights_above_count(min_flights: int, connection) -> pd.DataFrame | None:
    """
    Zwraca linie lotnicze które obsluzyly liczbe lotow >= min_flights
    """
    if not isinstance(min_flights, int):
        raise ValueError("Liczba lotów musi być liczbą całkowitą")
    
    if min_flights < 0:
        raise ValueError("Liczba lotów musi być dodatnia")
    

    zapytanie = f"""
    SELECT
    COALESCE(al.airline_code, 'UNK') AS airline_code,
    COALESCE(al.airline_name, 'Nieznana linia') AS airline_name,
    COUNT(arr.arrival_id) AS flight_count
    FROM arrivals arr
    JOIN aircraft ac ON arr.icao24 = ac.icao24
    LEFT JOIN airlines al ON ac.airline_code = al.airline_code
    GROUP BY al.airline_code, al.airline_name
    HAVING COUNT(arr.arrival_id) >= {min_flights}
    ORDER BY flight_count DESC;
    """
    return pd.read_sql(zapytanie, connection)

def daily_stats_for_airport(airport_icao: str, connection) -> pd.DataFrame | None:
    """
    Zwraca dzienny ruch dla lotniska
    """
    if not isinstance(airport_icao, str):
        raise ValueError("Niepoprawny kod ICAO lotniska")
    
    zapytanie = f"""
    SELECT
    stat_date,
    arrival_count,
    avg_flight_duration_min
    FROM daily_airport_stats
    WHERE icao_code = '{airport_icao}'
    ORDER BY stat_date ASC;
    """
    return pd.read_sql(zapytanie, connection)

def arrivals_by_airport(connection) -> pd.DataFrame | None:
    """
    Zwraca łączną liczbę przylotów dla lotniska
    """
    zapytanie = """
    SELECT 
        a.icao_code AS icao_code,
        a.airport_name AS airport_name,
        COUNT(arr.arrival_id) AS arrival_count
    FROM airports a
    JOIN arrivals arr ON a.icao_code = arr.arrival_airport
    GROUP BY a.icao_code, a.airport_name
    ORDER BY arrival_count DESC;
    """
    return pd.read_sql(zapytanie, connection)


def most_popular_routes(connection, limit: int = 10) -> pd.DataFrame | None:
    """
    Zwraca najpopularniejsze trasy
    """
    if not isinstance(limit, int):
        return None

    zapytanie = f"""
    SELECT 
        dep.airport_name AS departure_airport,
        arr.airport_name AS arrival_airport,
        COUNT(a.arrival_id) AS flight_count
    FROM arrivals a
    JOIN airports dep ON a.departure_airport = dep.icao_code
    JOIN airports arr ON a.arrival_airport = arr.icao_code
    GROUP BY dep.airport_name, arr.airport_name
    ORDER BY flight_count DESC
    LIMIT {limit};
    """
    return pd.read_sql(zapytanie, connection)


def most_active_aircraft(connection, limit: int = 10) -> pd.DataFrame | None:
    """
    Zwraca najaktywniejsze samoloty
    """
    if not isinstance(limit, int):
        return None

    zapytanie = f"""
    SELECT 
        ac.icao24 AS icao24,
        COALESCE(al.airline_name, 'Nieznana linia') AS airline_name,
        COUNT(arr.arrival_id) AS total_flights
    FROM arrivals arr
    JOIN aircraft ac ON arr.icao24 = ac.icao24
    LEFT JOIN airlines al ON ac.airline_code = al.airline_code
    GROUP BY ac.icao24, al.airline_name
    ORDER BY total_flights DESC
    LIMIT {limit};
    """
    return pd.read_sql(zapytanie, connection)

def avg_flight_duration_all_airports(connection) -> pd.DataFrame | None:
    """
    Zwraca średni czas lotu w minutach dla poszczególnych lotnisk
    """
    zapytanie = """
    SELECT 
        a.airport_name AS airport_name,
        ROUND(AVG(arr.flight_duration_min), 2) AS avg_duration_min,
        COUNT(arr.arrival_id) AS total_flights
    FROM arrivals arr
    JOIN airports a ON arr.arrival_airport = a.icao_code
    GROUP BY a.airport_name
    ORDER BY avg_duration_min DESC;
    """
    return pd.read_sql(zapytanie, connection)


def arrivals_over_time(connection, period: str = 'day') -> pd.DataFrame | None:
    """
    Zwraca liczbę przylotów w czasie agregacja dzienna lub miesięczna
    """
    if period not in ['day', 'month']:
        return None

    date_format = "YYYY-MM-DD" if period == 'day' else "YYYY-MM"

    zapytanie = f"""
    SELECT 
        TO_CHAR(arrival_time, '{date_format}') AS time_period,
        COUNT(arrival_id) AS flight_count
    FROM arrivals
    GROUP BY time_period
    ORDER BY time_period ASC;
    """
    return pd.read_sql(zapytanie, connection)

def arrivals_by_hour(connection) -> pd.DataFrame | None:
    """
    Zwraca rozkład przylotów w zależności od godziny lądowania (0-23)
    """
    zapytanie = """
    SELECT 
        EXTRACT(HOUR FROM arrival_time) AS arrival_hour,
        COUNT(arrival_id) AS flight_count
    FROM arrivals
    GROUP BY arrival_hour
    ORDER BY arrival_hour ASC;
    """
    return pd.read_sql(zapytanie, connection)

def compare_specific_airports(icao_codes: list, connection) -> pd.DataFrame | None:
    """
    Porównuje statystyki (liczbę przylotów) dla wybranych kodów ICAO lotnisk.
    """
    if not isinstance(icao_codes, list) or len(icao_codes) == 0:
        return None

    formatted_codes = ", ".join([f"'{code}'" for code in icao_codes])

    zapytanie = f"""
    SELECT 
        a.icao_code AS icao_code,
        a.airport_name AS airport_name,
        COUNT(arr.arrival_id) AS total_flights,
        ROUND(AVG(arr.flight_duration_min), 2) AS avg_duration_min
    FROM airports a
    LEFT JOIN arrivals arr ON a.icao_code = arr.arrival_airport
    WHERE a.icao_code IN ({formatted_codes})
    GROUP BY a.icao_code, a.airport_name
    ORDER BY total_flights DESC;
    """
    return pd.read_sql(zapytanie, connection)

def get_all_cities(connection) -> list:
    """
    Pobiera wszystkie unikalne miasta z bazy, aby zasilić rozwijaną listę.
    """
    zapytanie = """
    SELECT DISTINCT city 
    FROM airports 
    WHERE city IS NOT NULL AND country = 'Poland'
    ORDER BY city ASC;
    """
    df = pd.read_sql(zapytanie, connection)
    return df['city'].tolist()

def airport_traffic_by_multiple_cities(cities: list, connection) -> pd.DataFrame | None:
    """
    Zwraca ruch lotniczy dla listy wybranych miast.
    """
    if not isinstance(cities, list) or len(cities) == 0:
        return None

    formatted_cities = ", ".join([f"'{city}'" for city in cities])

    zapytanie = f"""
    SELECT
        a.icao_code AS icao_code,
        a.airport_name AS airport_name,
        a.city AS city,
        COUNT(arr.arrival_id) AS total_arrivals
    FROM airports a
    LEFT JOIN arrivals arr ON a.icao_code = arr.arrival_airport
    WHERE a.city IN ({formatted_cities})
    GROUP BY a.icao_code, a.airport_name, a.city
    ORDER BY total_arrivals DESC;
    """
    return pd.read_sql(zapytanie, connection)