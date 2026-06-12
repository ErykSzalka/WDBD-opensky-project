import os

import pandas as pd

from database.connection import connect_to_database
from database.repository import read_sql_file


AIRLINES_URL = os.getenv("AIRLINES_URL")

def import_airlines(database_name):
    columns = [
        "airline_id",
        "airline_name",
        "alias",
        "iata_code",
        "icao_code",
        "callsign",
        "country",
        "active",]
    airlines = pd.read_csv(
        AIRLINES_URL,
        names=columns,
        na_values="\\N",
    )

    airlines = airlines[
        (airlines["active"] == "Y")& airlines["icao_code"].str.match(r"^[A-Z]{3}$", na=False,) ]

    insert_airline_sql = read_sql_file("insert_airline.sql")
    connection = connect_to_database(database_name)
    cursor = connection.cursor()

    try:
        for _, airline in airlines.iterrows():
            cursor.execute(
                insert_airline_sql,
                (
                    airline["icao_code"],
                    airline["airline_name"],
                ),
            )
        connection.commit()
        print("Zaimportowano słownik linii lotniczych.")
    except Exception as error:
        connection.rollback()
        print("Błąd importowania linii:", error)
        raise

    finally:
        cursor.close()
        connection.close()