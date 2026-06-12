import subprocess
import sys
import time
from database.setup import create_database
from database.setup import create_tables
from collector import run_collector


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

    streamlit_process = start_streamlit()
    try:
        run_collector()
    finally:
        streamlit_process.terminate()
        streamlit_process.wait()


if __name__ == "__main__":
    main()