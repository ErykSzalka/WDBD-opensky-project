import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def connect_to_database(database_name):
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=database_name,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return connection