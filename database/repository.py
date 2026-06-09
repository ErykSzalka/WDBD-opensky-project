import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv

from database.connection import connect_to_database

load_dotenv()

SQL_FOLDER = Path(__file__).resolve().parent.parent / "sql"


def read_sql_file(file_name):
    file_path = SQL_FOLDER / file_name
    return file_path.read_text(encoding="utf-8")


def unix_to_datetime(unix_time):
    return datetime.fromtimestamp(unix_time, tz=timezone.utc).replace(tzinfo=None)


def get_flight_duration_minutes(first_seen, last_seen):
    return round((last_seen - first_seen) / 60, 2)


def save_arrivals_to_database(arrivals, errors=None):
    errors = errors or []

    if not arrivals:
        print("Brak danych do zapisania.")
        return

    insert_import_log_sql = read_sql_file("insert_import_log.sql")
    insert_airport_sql = read_sql_file("insert_airport.sql")
    insert_aircraft_sql = read_sql_file("insert_aircraft.sql")
    insert_arrival_sql = read_sql_file("insert_arrival.sql")

    database_name = os.getenv("DB_NAME")
    connection = connect_to_database(database_name)
    cursor = connection.cursor()

    try:
        data_range_start = unix_to_datetime(
            min(arrival.firstSeen for arrival in arrivals)
        )
        data_range_end = unix_to_datetime(
            max(arrival.lastSeen for arrival in arrivals)
        )

        download_status = "SUCCESS"

        if errors:
            download_status = "PARTIAL_SUCCESS"

        cursor.execute(
            insert_import_log_sql,
            (
                data_range_start,
                data_range_end,
                download_status
            )
        )

        log_id = cursor.fetchone()[0]

        airport_codes = set()

        for arrival in arrivals:
            if arrival.estDepartureAirport:
                airport_codes.add(arrival.estDepartureAirport)

            if arrival.estArrivalAirport:
                airport_codes.add(arrival.estArrivalAirport)

        for airport_code in airport_codes:
            cursor.execute(
                insert_airport_sql,
                (
                    airport_code,
                    airport_code,
                    None,
                    None
                )
            )

        for arrival in arrivals:
            cursor.execute(
                insert_aircraft_sql,
                (
                    arrival.icao24,
                    None
                )
            )

            departure_time = unix_to_datetime(arrival.firstSeen)
            arrival_time = unix_to_datetime(arrival.lastSeen)

            flight_duration_min = get_flight_duration_minutes(
                arrival.firstSeen,
                arrival.lastSeen
            )

            cursor.execute(
                insert_arrival_sql,
                (
                    log_id,
                    arrival.icao24,
                    arrival.estDepartureAirport,
                    arrival.estArrivalAirport,
                    arrival.callsign,
                    departure_time,
                    arrival_time,
                    flight_duration_min
                )
            )

        connection.commit()
        print("Zapisano dane do bazy.")

    except Exception as error:
        connection.rollback()
        print("Błąd zapisu do bazy:")
        print(error)

    finally:
        cursor.close()
        connection.close()