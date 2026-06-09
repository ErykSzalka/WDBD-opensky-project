from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests
import time

from token_manager import tokens
from data_organizer import Arrival

def fetch_opensky_data() -> tuple[list[dict], list]:
    url = "https://opensky-network.org/api/flights/arrival"

    end_time = int(time.time()) - (86400 * 5) # tutaj określamy ile dni wstecz chcemy
    begin_time = end_time - 86400
    #obecnie przedział czasu to jeden dzień
    polish_airports = ["EPWA", "EPKK", "EPGD", "EPKT", "EPWR"]
    # Warszawa(Chopin), Kraków(Balice), Gdańsk(Rębiechowo), Katowice (Pyrzowice), Wrocław (Strachowice)
    
    all_arrivals = []
    import_errors = []

    for airport_code in polish_airports:
        params = {
            "airport": airport_code,
            "begin": begin_time,
            "end": end_time
        }

        response = requests.get(url, params=params, headers=tokens.headers())

        if response.status_code == 200:
            data = response.json()

            if data:
                for raw_flight in data:
                    arrival_obj = Arrival.from_api_dict(raw_flight)
                    all_arrivals.append(arrival_obj)
            else:
                import_errors.append(f"Warning: Empty data for {airport_code}")
        else:
            import_errors.append(f"Failed to fetch {airport_code}. Status: {response.status_code}")
    
    return all_arrivals, import_errors




