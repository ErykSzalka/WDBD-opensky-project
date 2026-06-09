import subprocess
import sys
import time

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
    streamlit_process = start_streamlit()

    try:
        run_collector()
    finally:
        streamlit_process.terminate()


if __name__ == "__main__":
    main()