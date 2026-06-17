import os
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from database.connection import connect_to_database
load_dotenv()

SQL_FOLDER = Path(__file__).resolve().parent.parent / "sql"

def read_sql_file(file_name):
    return (SQL_FOLDER / file_name).read_text(encoding="utf-8")
def save_aircraft_positions_to_database(states, snapshot_timestamp, errors=None):
    database_name = os.getenv("DB_NAME")
    errors = errors or []
    if not states:
        print("Brak danych radarowych do zapisania.")
        return
    if snapshot_timestamp is None:
        print("Brak czasu snapshotu danych radarowych.")
        return
    insert_position_sql = read_sql_file("insert_aircraft_position.sql")
    connection =connect_to_database(database_name)
    cursor = connection.cursor()

    try:
        snapshot_time = datetime.fromtimestamp(snapshot_timestamp, tz=timezone.utc)
        saved_count =0
        for state in states:
            if state.latitude is None or state.longitude is None:
                continue
            time_position = (
                datetime.fromtimestamp(state.time_position, tz=timezone.utc)
                if state.time_position is not None
                else None
            )
            last_contact = (
                datetime.fromtimestamp(state.last_contact, tz=timezone.utc)
                if state.last_contact is not None
                else None
            )
            cursor.execute(
                insert_position_sql,
                (
                    snapshot_time,
                    state.icao24,
                    state.callsign,
                    state.origin_country,
                    time_position,
                    last_contact,
                    state.longitude,
                    state.latitude,
                    state.baro_altitude,
                    state.geo_altitude,
                    state.on_ground,
                    state.velocity,
                    state.true_track,
                    state.vertical_rate,
                    state.squawk,
                    state.spi,
                    state.position_source,
                ),
            )

            saved_count+=1

        connection.commit()
        print(f"Zapisano pozycje radarowe: {saved_count}")

    except Exception as error:
        connection.rollback()
        print("Błąd zapisu pozycji radarowych do bazy:")
        print(error)
        raise

    finally:
        cursor.close()
        connection.close()
def save_arrivals_to_database(arrivals, errors=None, requested_start=None, requested_end=None):
    if not arrivals:
        download_status = "FAILED" if errors else "EMPTY"
    elif errors:
        download_status = "PARTIAL_SUCCESS"
    else:
        download_status = "SUCCESS"
    database_name = os.getenv("DB_NAME")
    errors = errors or []

    insert_import_log_sql = read_sql_file("insert_import_log.sql")
    insert_airport_sql = read_sql_file("insert_airport.sql")
    insert_aircraft_sql = read_sql_file("insert_aircraft.sql")
    insert_arrival_sql = read_sql_file("insert_arrival.sql")
    update_daily_stats_sql = read_sql_file("update_daily_airport_stats.sql")
    connection = connect_to_database(database_name)
    cursor = connection.cursor()

    try:
        if not arrivals:
            print("Brak danych do zapisania.")
            return
        data_range_start = datetime.fromtimestamp(min(a.firstSeen for a in arrivals), tz=timezone.utc)
        data_range_end = datetime.fromtimestamp(max(a.lastSeen for a in arrivals), tz=timezone.utc)
        download_status = "PARTIAL_SUCCESS" if errors else "SUCCESS"
        cursor.execute(insert_import_log_sql, (data_range_start, data_range_end, download_status))
        log_id = cursor.fetchone()[0]

        airport_codes = set()
        for arrival in arrivals:
            if arrival.estDepartureAirport:
                airport_codes.add(arrival.estDepartureAirport)
            if arrival.estArrivalAirport:
                airport_codes.add(arrival.estArrivalAirport)
        for airport_code in airport_codes:
            cursor.execute(insert_airport_sql, (airport_code, airport_code, None, None))
        cursor.execute("SELECT airline_code FROM airlines")
        airline_codes = {row[0] for row in cursor.fetchall()}

        for arrival in arrivals:
            airline_code = None
            if arrival.callsign and len(arrival.callsign) >= 3:
                callsign_prefix = arrival.callsign[:3]
                if callsign_prefix in airline_codes:
                    airline_code = callsign_prefix
            cursor.execute(
                insert_aircraft_sql,
                (arrival.icao24, airline_code),
            )
            departure_time = datetime.fromtimestamp(arrival.firstSeen,tz=timezone.utc,)
            arrival_time = datetime.fromtimestamp(arrival.lastSeen, tz=timezone.utc)
            flight_duration_min = round((arrival.lastSeen - arrival.firstSeen) / 60, 2)
            cursor.execute(insert_arrival_sql, (log_id, arrival.icao24, arrival.estDepartureAirport, arrival.estArrivalAirport, arrival.callsign, departure_time, arrival_time, flight_duration_min))
        cursor.execute(update_daily_stats_sql)
        connection.commit()
        print("Zapisano dane do bazy.")

    except Exception as error:
        connection.rollback()
        print("Błąd zapisu do bazy:")
        print(error)
        raise

    finally:
        cursor.close()
        connection.close()