# WDBD OpenSky Project

A Python project for collecting, storing, and visualizing flight arrival data from the OpenSky Network API.

The application downloads airport arrival data, stores it in a PostgreSQL database, calculates daily airport statistics, and displays the results in an interactive Streamlit dashboard.

## Features

- Fetches arrival data from the OpenSky Network API
- Stores flights, aircraft, airports, airlines, and import logs in PostgreSQL
- Imports airport and airline dictionary data from external CSV sources
- Calculates daily airport statistics
- Provides an interactive Streamlit dashboard with:
  - general arrival overview
  - arrivals over time
  - arrivals by hour
  - airport traffic ranking
  - daily airport statistics
  - most popular routes
  - most active aircraft
  - airline activity
  - filtering by flight duration and country

## Tech Stack

- Python
- PostgreSQL
- Streamlit
- Pandas
- Plotly
- Requests
- psycopg2
- python-dotenv

## Project Structure

```text
WDBD-opensky-project/
├── collector.py
├── main.py
├── requirements.txt
├── README.md
├── database/
│   ├── connection.py
│   ├── setup.py
│   ├── repository.py
│   ├── airport_importer.py
│   ├── airline_importer.py
│   └── __init__.py
├── data_import/
│   ├── data_import.py
│   ├── data_organizer.py
│   ├── token_manager.py
│   └── __init__.py
├── sql/
│   ├── create_tables.sql
│   ├── insert_airport.sql
│   ├── insert_airline.sql
│   ├── insert_aircraft.sql
│   ├── insert_arrival.sql
│   ├── insert_import_log.sql
│   └── update_daily_airport_stats.sql
└── visualization/
    ├── dashboard.py
    ├── reader.py
    └── wizualizacja.ipynb
```

## How It Works

The project consists of four main parts:

1. Database setup
2. Data import
3. Data storage and aggregation
4. Data visualization

### 1. Database Setup

The database is created and initialized using files from the `database/` and `sql/` directories.

The main database tables are:

- `airports`
- `airlines`
- `aircraft`
- `arrivals`
- `import_logs`
- `daily_airport_stats`

The table structure is defined in:

```text
sql/create_tables.sql
```

### 2. Data Import

Flight arrival data is fetched from the OpenSky Network API in:

```text
data_import/data_import.py
```

The current implementation downloads arrival data for selected Polish airports:

```python
polish_airports = ["EPWA", "EPKK", "EPGD", "EPKT", "EPWR"]
```

These airports represent:

- EPWA - Warsaw Chopin Airport
- EPKK - Krakow John Paul II International Airport
- EPGD - Gdansk Lech Walesa Airport
- EPKT - Katowice Airport
- EPWR - Wroclaw Airport

The OpenSky API endpoint used by the project is:

```text
https://opensky-network.org/api/flights/arrival
```

The downloaded data is converted into `Arrival` objects defined in:

```text
data_import/data_organizer.py
```

### 3. Data Storage

Downloaded arrivals are saved into PostgreSQL by:

```text
database/repository.py
```

The project also stores:

- import execution logs
- aircraft data
- airline assignments based on callsign prefixes
- airport data
- daily airport statistics

After inserting arrivals, the project updates the `daily_airport_stats` table using:

```text
sql/update_daily_airport_stats.sql
```

### 4. Dashboard

The dashboard is implemented in:

```text
visualization/dashboard.py
```

It uses helper queries from:

```text
visualization/reader.py
```

The dashboard allows the user to explore:

- total arrivals by airport
- arrivals over time
- hourly arrival distribution
- most popular routes
- most active aircraft
- airline activity
- flight duration filters
- traffic by country
- airport comparisons

## Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

The main dependencies are:

```text
pandas
plotly
psycopg2-binary
python-dotenv
requests
streamlit
```

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=opensky_db
DB_USER=postgres
DB_PASSWORD=your_password

OPENSKY_CLIENT_ID=your_client_id
OPENSKY_CLIENT_SECRET=your_client_secret

AIRPORTS_URL=https://example.com/airports.csv
COUNTRIES_URL=https://example.com/countries.csv
AIRLINES_URL=https://example.com/airlines.dat
```

The database connection is configured in:

```text
database/connection.py
```

The API token logic is handled in:

```text
data_import/token_manager.py
```

## Running the Project

To run the full application:

```bash
python main.py
```

This will:

1. create the database if it does not exist,
2. create required tables,
3. import airport dictionary data,
4. import airline dictionary data,
5. start the Streamlit dashboard,
6. start the collector loop.

The collector downloads data periodically. The interval is configured in:

```text
collector.py
```

Default interval:

```python
INTERVAL_SECONDS = 24 * 60 * 60
```

This means the collector runs once every 24 hours.

## Running Only the Dashboard

If the database already contains data, the dashboard can be started directly with:

```bash
streamlit run visualization/dashboard.py
```

## OpenSky API Time Range

The project uses the OpenSky arrivals endpoint:

```text
/flights/arrival
```

This endpoint has a time range limitation. A single request cannot cover a time interval larger than two days.

For this reason, the current implementation downloads data for a one-day period:

```python
end_time = int(time.time()) - (86400 * 5)
begin_time = end_time - 86400
```

This means:

- `end_time` is set to 5 days before the current time,
- `begin_time` is set to 1 day before `end_time`,
- the request covers a 24-hour period.

If more days are needed, the data should be downloaded in smaller chunks, for example one request per day.

## Database Tables

### airports

Stores airport dictionary data.

Main columns:

- `icao_code`
- `airport_name`
- `city`
- `country`

### airlines

Stores airline dictionary data.

Main columns:

- `airline_code`
- `airline_name`

### aircraft

Stores aircraft detected in imported arrivals.

Main columns:

- `icao24`
- `airline_code`
- `first_detected_at`

### arrivals

Stores imported flight arrival records.

Main columns:

- `arrival_id`
- `log_id`
- `icao24`
- `departure_airport`
- `arrival_airport`
- `callsign`
- `departure_time`
- `arrival_time`
- `flight_duration_min`

### import_logs

Stores information about each import execution.

Main columns:

- `log_id`
- `execution_time`
- `data_range_start`
- `data_range_end`
- `download_status`

### daily_airport_stats

Stores aggregated daily statistics per airport.

Main columns:

- `stat_id`
- `icao_code`
- `stat_date`
- `arrival_count`
- `avg_flight_duration_min`

## Dashboard Sections

### General Overview

Shows basic information about imported arrivals, including:

- number of destination airports with arrivals
- total number of arrivals
- airport with the highest traffic
- arrivals over time
- arrivals by hour

### Airports

Shows:

- number of arrivals by airport
- average flight duration by airport
- daily statistics for a selected airport

### Routes

Shows the most popular routes based on imported arrival records.

### Airlines and Aircraft

Shows:

- airlines with at least a selected number of flights
- most active aircraft

### Filtering

Allows filtering by:

- minimum flight duration
- airport country
- selected airports for comparison

## Notes

This project analyzes imported arrival records, not global real-time air traffic.

The statistics shown in the dashboard depend on:

- selected airports in the import script,
- selected time range,
- OpenSky API availability,
- completeness of OpenSky data,
- imported airport and airline dictionaries.

## Common Issues

### psycopg2 DLL Error on Windows

If you see an error similar to:

```text
ImportError: DLL load failed while importing _psycopg
```

it may be caused by using Python from the Microsoft Store or by Windows application control policies.

Recommended solution:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Using a standard Python installation from python.org is recommended.

### Empty API Response

OpenSky may return an empty response if:

- the selected time range has no data,
- the requested period is too recent,
- the API limit was reached,
- the airport had no arrivals in the selected period.

### Time Range Too Large

The OpenSky arrivals endpoint does not allow large time intervals in one request. Use daily chunks when downloading data for multiple days.

## Authors

Project created for a database and data visualization assignment using OpenSky Network flight data.
