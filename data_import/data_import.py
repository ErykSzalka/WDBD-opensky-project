from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests


from token_manager import tokens

def fetch_opensky_data():
    url = "https://opensky-network.org/api/flights/arrival"

    end_time = int(time.time())
    begin_time = end_time - 86400

    polish_airports = ["EPWA", "EPKK", "EPGD", "EPKT", "EPWR"]
    # Warszawa(Chopin), Kraków(Balice), Gdańsk(Rębiechowo), Katowice (Pyrzowice), Wrocław (Strachowice)
    
    all_arrivals = []

    for airport_code in polish_airports:
        params = {
            "airport": airport_code,
            "begin": begin_time,
            "end": end_time
        }

        response = requests.get(url, params=params, headers=tokens.headers())

        


