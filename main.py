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
        "vizualize/app.py"
    ])


def main():
    #streamlit_process = start_streamlit()

    #try:
        #run_collector()
    #finally:
        #streamlit_process.terminate()
    create_database()
    create_tables()
    run_collector()


if __name__ == "__main__":
    main()