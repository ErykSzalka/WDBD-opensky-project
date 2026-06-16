import subprocess
import sys
from database.setup import create_database
from database.setup import create_tables
from collector import run_collector
from database.airport_importer import import_airports
import os
from database.airline_importer import import_airlines
def start_streamlit():
    return subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "visualization/dashboard.py"
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
    try:
        run_collector()
    finally:
        streamlit_process.terminate()
        streamlit_process.wait()


if __name__ == "__main__":
    main()