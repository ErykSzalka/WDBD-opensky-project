import pandas as pd
from database.connection import connect_to_database
from database.repository import read_sql_file
import os

AIRPORTS_URL=os.getenv("AIRPORTS_URL")
COUNTRIES_URL =os.getenv("COUNTRIES_URL")


def import_airports(database_name):
    airports = pd.read_csv(AIRPORTS_URL)
    countries = pd.read_csv(COUNTRIES_URL)
    country_names = dict(zip(countries["code"], countries["name"]))
    airports = airports[
        airports["icao_code"].str.match(r"^[A-Z]{4}$", na=False)]

    insert_airport_sql = read_sql_file("insert_airport.sql")
    connection = connect_to_database(database_name)
    cursor = connection.cursor()

    try:
        for _, airport in airports.iterrows():
            city = airport["municipality"]
            if pd.isna(city):
                city = None
            country = country_names.get(airport["iso_country"])
            cursor.execute(
                insert_airport_sql,(airport["icao_code"],airport["name"],city,country),)
        connection.commit()
        print("zaimportowano słownik lotnisk.")
    except Exception as error:
        connection.rollback()
        print("bląd importowania lotnisk:", error)
        raise
    finally:
        cursor.close()
        connection.close()