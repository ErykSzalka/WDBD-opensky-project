import os
from pathlib import Path

from psycopg2 import sql
from dotenv import load_dotenv

from database.connection import connect_to_database

load_dotenv()


database_name = os.getenv("DB_NAME")
sql_file = Path(__file__).resolve().parent.parent / "sql" / "create_tables.sql"


def create_database():
    connection = connect_to_database("postgres")
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s",(database_name,))

    database_already_exists = cursor.fetchone()
    if database_already_exists:
        print("Baza danych już istnieje.")
    else:
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(database_name)
            )
        )

        print("Utworzono bazę danych.")

    cursor.close()
    connection.close()


def create_tables():
    connection = connect_to_database(database_name)
    cursor = connection.cursor()
    script = sql_file.read_text(encoding="utf-8")
    cursor.execute(script)
    connection.commit()
    cursor.close()
    connection.close()

    print("Wykonano skrypt SQL.")


def main():
    create_database()
    create_tables()

    print("Baza danych jest gotowa.")


if __name__ == "__main__":
    main()