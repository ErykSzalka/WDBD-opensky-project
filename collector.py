import time
from data_import.data_import import fetch_opensky_data, fetch_opensky_radar_data
from database.repository import save_arrivals_to_database, save_aircraft_positions_to_database

INTERVAL_SECONDS = 24*60*60
def run_collector():
    while True:
        try:
            print("pobieranie danych z opensky...")
            arrivals, errors = fetch_opensky_data()
            print("pobrano przyloty:", len(arrivals))

            if errors:
                print("Błędy:")
                for error in errors:
                    print(error)

            save_arrivals_to_database(arrivals, errors)

        except Exception as error:
            print(f"Błąd kolektora: {error}")

        print("Czekam na kolejne pobranie...")
        time.sleep(INTERVAL_SECONDS)

RADAR_INTERVAL_SECONDS = 2*60

def run_radar_collector():
    while True:
        try:
            print("Pobieranie aktualnych pozycji samolotów nad Polską...")
            states, errors, snapshot_time = fetch_opensky_radar_data()
            print("Pobrano pozycje:", len(states))

            if errors:
                print("Błędy:")
                for error in errors:
                    print(error)

            save_aircraft_positions_to_database(states, snapshot_time, errors)

        except Exception as error:
            print(f"Błąd kolektora radarowego: {error}")

        print("Czekam na kolejne pobranie pozycji...")
        time.sleep(RADAR_INTERVAL_SECONDS)
