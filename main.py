import os
import subprocess
import sys

from database.airline_importer import import_airlines
from database.airport_importer import import_airports
from database.setup import create_database
from database.setup import create_tables


def start_streamlit():
    return subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "visualization/dashboard.py"
    ])


def start_arrival_collector():
    return subprocess.Popen([
        sys.executable,
        "arrival_collector.py"
    ])


def start_radar_collector():
    return subprocess.Popen([
        sys.executable,
        "radar_collector.py"
    ])


def main():
    create_database()
    create_tables()

    try:
        import_airports(os.getenv("DB_NAME"))
    except Exception as error:
        print("Nie udało się zaktualizować słownika lotnisk:", error)

    try:
        import_airlines(os.getenv("DB_NAME"))
    except Exception as error:
        print("Nie udało się zaimportować linii:", error)

    streamlit_process = start_streamlit()
    arrival_process = start_arrival_collector()
    #zakomentowywac podczas zbierania danych radar! przy ostatnim odpaleniu odkomentowac
    radar_process = start_radar_collector()

    try:
        streamlit_process.wait()
    finally:
        arrival_process.terminate()
        arrival_process.wait()

        radar_process.terminate()
        radar_process.wait()

        streamlit_process.terminate()
        streamlit_process.wait()


if __name__ == "__main__":
    main()