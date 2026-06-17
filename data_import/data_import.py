from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import os
import pandas as pd
import requests
import time

from data_import.token_manager import tokens
from data_import.data_organizer import Arrival, RadarState
from database.connection import connect_to_database

def fetch_opensky_data() -> tuple[list[dict], list]:
    url = "https://opensky-network.org/api/flights/arrival"

    end_time = int(time.time()) - (86400 * 3) # tutaj określamy ile dni wstecz chcemy
    begin_time = end_time - 86400
    #obecnie przedział czasu to jeden dzień

    polish_airports = [
    "EPWA",  # Warszawa (Chopin)
    "EPKK",  # Kraków (Balice)
    "EPGD",  # Gdańsk (Rębiechowo)
    "EPKT",  # Katowice (Pyrzowice)
    "EPWR",  # Wrocław (Strachowice)
    "EPMO",  # Warszawa (Modlin)
    "EPPO",  # Poznań (Ławica)
    "EPRZ",  # Rzeszów (Jasionka)
    "EPSC",  # Szczecin (Goleniów)
    "EPBY",  # Bydgoszcz (Szwederowo)
    "EPLL",  # Łódź (Lublinek)
    "EPLB",  # Lublin (Świdnik)
    "EPSY",  # Olsztyn (Mazury)
    "EPZG",  # Zielona Góra (Babimost)
    "EPRA"   # Radom (Sadków)
]
    
    all_arrivals = []
    import_errors = []

    for airport_code in polish_airports:
        params = {
            "airport": airport_code,
            "begin": begin_time,
            "end": end_time
        }

        response = requests.get(
            url,
            params=params,
            headers=tokens.headers(),
            timeout=(5, 30),
        )

        if response.status_code == 200:
            data = response.json()

            if data:
                for raw_flight in data:
                    arrival_obj = Arrival.from_api_dict(raw_flight)
                    all_arrivals.append(arrival_obj)
            else:
                import_errors.append(f"Warning: Empty data for {airport_code}")
            time.sleep(1)
        elif response.status_code == 401:
            tokens.invalidate()
            response = requests.get(
                url,
                params=params,
                headers=tokens.headers(),
                timeout=(5, 30),
            )
            if response.status_code == 200:
                data = response.json()
                for raw_flight in data:
                    arrival_obj = Arrival.from_api_dict(raw_flight)
                    all_arrivals.append(arrival_obj)
            else:
                import_errors.append(
                    f"Failed after token refresh for {airport_code}. "
                    f"Status: {response.status_code}"
                )




        elif response.status_code == 404:
            continue
        else:
            import_errors.append(f"Failed to fetch {airport_code}. Status: {response.status_code}")
    return all_arrivals, import_errors

def fetch_opensky_radar_data():
    url = "https://opensky-network.org/api/states/all"

    params = {
        "lamin": 49.0,
        "lamax": 54.9,
        "lomin": 14.1,
        "lomax": 24.2
    }

    all_states = []
    import_errors = []
    snapshot_time = None

    response = requests.get(
        url,
        params=params,
        headers=tokens.headers(),
        timeout=(5, 30),
    )

    if response.status_code == 200:
        data = response.json()
        snapshot_time = data.get("time")
        states = data.get("states")

        if states:
            for raw_state in states:
                state_obj = RadarState.from_api_list(raw_state)
                all_states.append(state_obj)
        else:
            import_errors.append("Warning: Empty radar data for Poland")

    elif response.status_code == 401:
        tokens.invalidate()
        response = requests.get(
            url,
            params=params,
            headers=tokens.headers(),
            timeout=(5, 30),
        )

        if response.status_code == 200:
            data = response.json()
            snapshot_time = data.get("time")
            states = data.get("states")

            if states:
                for raw_state in states:
                    state_obj = RadarState.from_api_list(raw_state)
                    all_states.append(state_obj)
            else:
                import_errors.append("Warning: Empty radar data for Poland after token refresh")
        else:
            import_errors.append(f"Failed after token refresh. Status: {response.status_code}")

    elif response.status_code == 404:
        import_errors.append("Radar endpoint returned 404")
    else:
        import_errors.append(f"Failed to fetch radar data. Status: {response.status_code}")

    return all_states, import_errors, snapshot_time


