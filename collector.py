import time
from data_import.data_import import fetch_opensky_data
from database.repository import save_arrivals_to_database


INTERVAL_SECONDS = 60

def run_collector():
    while True:
        print("pobieranie danych z opensky...")
        arrivals, errors = fetch_opensky_data()
        print("pobrano przyloty:", len(arrivals))

        if errors:
            print("Błędy:")
            for error in errors:
                print(error)
        save_arrivals_to_database(arrivals, errors)
        print("Czekam na kolejne pobranie...")
        time.sleep(INTERVAL_SECONDS)
