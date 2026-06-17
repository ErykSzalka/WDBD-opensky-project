# WDBD OpenSky Project

Python application for collecting, storing, and visualizing aviation data from the OpenSky Network API.

The project imports historical airport arrival data, stores it in PostgreSQL, calculates daily airport statistics, and displays the results in a Streamlit dashboard. It also collects live aircraft position snapshots over Poland so they can be displayed later on a time-based radar map.


## Features

- Fetches historical arrival data from the OpenSky Network API
- Fetches live aircraft state vectors over Poland
- Stores arrivals, aircraft, airports, airlines, import logs, and aircraft positions in PostgreSQL
- Imports airport and airline dictionaries from external public data sources
- Calculates daily airport statistics
- Runs separate collectors for arrivals and radar positions
- Provides a Streamlit dashboard with:
  - general arrival overview
  - arrivals over time
  - arrivals by hour
  - airport traffic ranking
  - daily airport statistics
  - most popular routes
  - most active aircraft
  - airline activity
  - filtering by city, flight duration, and selected airports
  - radar map based on saved aircraft position snapshots

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
|-- arrival_collector.py
|-- collector.py
|-- main.py
|-- radar_collector.py
|-- requirements.txt
|-- README.md
|-- database/
|   |-- connection.py
|   |-- setup.py
|   |-- repository.py
|   |-- airport_importer.py
|   |-- airline_importer.py
|   `-- __init__.py
|-- data_import/
|   |-- data_import.py
|   |-- data_organizer.py
|   |-- token_manager.py
|   `-- __init__.py
|-- sql/
|   |-- create_tables.sql
|   |-- insert_aircraft.sql
|   |-- insert_aircraft_position.sql
|   |-- insert_airport.sql
|   |-- insert_airline.sql
|   |-- insert_arrival.sql
|   |-- insert_import_log.sql
|   `-- update_daily_airport_stats.sql
`-- visualization/
    |-- dashboard.py
    |-- reader.py
    `-- wizualizacja.ipynb
```

## How It Works

The project has five main parts:

1. Database setup
2. Dictionary imports
3. Historical arrival collection
4. Live radar position collection
5. Dashboard visualization

### 1. Database Setup

The database is created and initialized by:

```text
database/setup.py
```

The SQL schema is stored in:

```text
sql/create_tables.sql
```

The main tables are:

- `airports`
- `airlines`
- `aircraft`
- `arrivals`
- `import_logs`
- `daily_airport_stats`
- `aircraft_positions`

### 2. Dictionary Imports

Airport and airline dictionaries are imported before collectors start.

Airport data is imported by:

```text
database/airport_importer.py
```

Airline data is imported by:

```text
database/airline_importer.py
```

The project uses these dictionary sources:

```env
AIRPORTS_URL=https://davidmegginson.github.io/ourairports-data/airports.csv
COUNTRIES_URL=https://davidmegginson.github.io/ourairports-data/countries.csv
AIRLINES_URL=https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat
```

### 3. Historical Arrival Collection

Historical arrival data is fetched from:

```text
https://opensky-network.org/api/flights/arrival
```

The current implementation downloads data for selected Polish airports, for example:

```python
polish_airports = [
    "EPWA",
    "EPKK",
    "EPGD",
    "EPKT",
    "EPWR",
    "EPMO",
    "EPPO",
    "EPRZ",
    "EPSC",
    "EPBY",
    "EPLL",
    "EPLB",
    "EPSY",
    "EPZG",
    "EPRA",
]
```

The collector is started through:

```text
arrival_collector.py
```

The collection loop is defined in:

```text
collector.py
```

By default, arrival data is collected once every 24 hours:

```python
INTERVAL_SECONDS = 24 * 60 * 60
```

### 4. Live Radar Position Collection

Live aircraft positions are fetched from:

```text
https://opensky-network.org/api/states/all
```

The request uses a bounding box covering Poland:

```python
params = {
    "lamin": 49.0,
    "lamax": 54.9,
    "lomin": 14.1,
    "lomax": 24.2,
}
```

The radar collector stores aircraft position snapshots in:

```text
aircraft_positions
```

The collector is started through:

```text
radar_collector.py
```

By default, radar data is collected every 10 minutes:

```python
RADAR_INTERVAL_SECONDS = 10 * 60
```

Each saved position contains fields such as:

- `snapshot_time`
- `icao24`
- `callsign`
- `origin_country`
- `latitude`
- `longitude`
- `baro_altitude`
- `geo_altitude`
- `velocity`
- `true_track`
- `vertical_rate`
- `squawk`
- `spi`
- `position_source`

The `snapshot_time` field is used later by the dashboard to display aircraft positions for a selected moment in time.

### 5. Dashboard Visualization

The dashboard is implemented in:

```text
visualization/dashboard.py
```

Database read queries are implemented in:

```text
visualization/reader.py
```

The dashboard contains sections for:

- general overview
- airports
- routes
- airlines and aircraft
- filtering
- radar map

The radar map uses saved snapshots from `aircraft_positions`. The user can select a snapshot time and display aircraft positions on a map of Poland.

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

Dependencies:

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

AIRPORTS_URL=https://davidmegginson.github.io/ourairports-data/airports.csv
COUNTRIES_URL=https://davidmegginson.github.io/ourairports-data/countries.csv
AIRLINES_URL=https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat
```

Do not commit real `.env` files to Git. The file may contain database credentials and OpenSky API credentials.

## Running the Project

Run the full application:

```bash
python main.py
```

This will:

1. create the database if needed,
2. create required tables,
3. import airport dictionary data,
4. import airline dictionary data,
5. start the Streamlit dashboard,
6. start the arrival collector process,
7. start the radar collector process.

## Running Individual Parts

Run only the dashboard:

```bash
streamlit run visualization/dashboard.py
```

Run only the arrival collector:

```bash
python arrival_collector.py
```

Run only the radar collector:

```bash
python radar_collector.py
```

## OpenSky API Notes

### Arrival Endpoint

The project uses:

```text
/flights/arrival
```

This endpoint has a time range limitation. A single request cannot cover a time interval larger than two days.

The current implementation uses a one-day range:

```python
end_time = int(time.time()) - (86400 * 6)
begin_time = end_time - 86400
```

If more days are needed, the data should be fetched in smaller chunks, for example one request per day.

### State Vectors Endpoint

The project also uses:

```text
/states/all
```

This endpoint returns current aircraft state vectors. The project filters them by a bounding box around Poland and stores them as position snapshots.

### Rate Limits

OpenSky may return:

```text
429 Too Many Requests
```

This means too many requests were sent in a short period of time. To avoid this:

- keep the airport list limited to relevant airports,
- add delays between airport requests,
- keep radar polling at a reasonable interval, such as 10 minutes,
- avoid running multiple collectors at the same time.

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

Stores imported historical arrival records.

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

Stores information about arrival import executions.

Main columns:

- `log_id`
- `execution_time`
- `data_range_start`
- `data_range_end`
- `download_status`

### daily_airport_stats

Stores aggregated daily statistics per destination airport.

Main columns:

- `stat_id`
- `icao_code`
- `stat_date`
- `arrival_count`
- `avg_flight_duration_min`

### aircraft_positions

Stores live aircraft position snapshots collected from `/states/all`.

Main columns:

- `position_id`
- `snapshot_time`
- `icao24`
- `callsign`
- `origin_country`
- `time_position`
- `last_contact`
- `longitude`
- `latitude`
- `baro_altitude`
- `geo_altitude`
- `on_ground`
- `velocity`
- `true_track`
- `vertical_rate`
- `squawk`
- `spi`
- `position_source`

The table has a uniqueness constraint on:

```text
snapshot_time, icao24
```

This prevents duplicate positions for the same aircraft in the same snapshot.

## Dashboard Sections

### General Overview

Shows:

- number of destination airports with arrivals
- total number of arrivals
- airport with the highest traffic
- arrivals over time
- arrivals by hour

### Airports

Shows:

- arrivals by airport
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

- selected Polish cities
- minimum flight duration
- selected airports for comparison

### Radar Map

Shows aircraft positions over Poland for a selected saved snapshot.

The planned workflow is:

1. The radar collector saves aircraft positions every 10 minutes.
2. The dashboard loads available `snapshot_time` values.
3. The user selects a snapshot time.
4. The dashboard displays aircraft points on a map.


## Authors

Project created for a database and data visualization assignment using OpenSky Network aviation data.
