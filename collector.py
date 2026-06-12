import time
from data_import.data_import import fetch_opensky_data
from database.repository import save_arrivals_to_database


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