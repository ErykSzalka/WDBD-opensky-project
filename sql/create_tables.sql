-- tabela słownikowa lotniska
CREATE TABLE IF NOT EXISTS airports (
    icao_code VARCHAR(4) PRIMARY KEY,
    airport_name VARCHAR(255) NOT NULL,
    city VARCHAR (100),
    country VARCHAR (100)
);

-- tabela techniczna logi importu
CREATE TABLE IF NOT EXISTS import_logs (
    log_id SERIAL PRIMARY KEY,
    execution_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_range_start TIMESTAMP NOT NULL,
    data_range_end TIMESTAMP NOT NULL,
    download_status VARCHAR(50) NOT NULL 
);

-- tabela merytoryczna linie lotnicze
CREATE TABLE IF NOT EXISTS airlines (
    airline_code VARCHAR(3) PRIMARY KEY,
    airline_name VARCHAR(255) NOT NULL
);

-- tabela merytoryczna samoloty
CREATE TABLE IF NOT EXISTS aircraft (
    icao24 VARCHAR(6) PRIMARY KEY,
    airline_code VARCHAR(3),
    first_detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_aircraft_airline
        FOREIGN KEY (airline_code)
        REFERENCES airlines(airline_code)
);

-- tabela merytoryczna przyloty
CREATE TABLE IF NOT EXISTS arrivals (
    arrival_id SERIAL PRIMARY KEY,
    log_id INT NOT NULL,
    icao24 VARCHAR(6) NOT NULL,
    departure_airport VARCHAR(4),
    arrival_airport VARCHAR(4),
    callsign VARCHAR(20),
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    flight_duration_min NUMERIC(6, 2) NOT NULL,

    CONSTRAINT fk_arrivals_log
        FOREIGN KEY (log_id)
        REFERENCES import_logs(log_id),
    
    CONSTRAINT fk_arrivals_aircraft 
        FOREIGN KEY (icao24) 
        REFERENCES aircraft(icao24),

    CONSTRAINT fk_arrivals_dep_airport 
        FOREIGN KEY (departure_airport) 
        REFERENCES airports(icao_code),

    CONSTRAINT fk_arrivals_arr_airport 
        FOREIGN KEY (arrival_airport) 
        REFERENCES airports(icao_code),
    CONSTRAINT unique_arrival
        UNIQUE (icao24, departure_time, arrival_time, arrival_airport)
);

-- tabela merytoryczna statystyki lotnisk (dzienne)
CREATE TABLE IF NOT EXISTS daily_airport_stats (
    stat_id SERIAL PRIMARY KEY,
    icao_code VARCHAR(4),
    stat_date DATE NOT NULL,
    arrival_count INT DEFAULT 0,
    avg_flight_duration_min NUMERIC(8, 2),

    CONSTRAINT fk_stats_airport
        FOREIGN KEY (icao_code)
        REFERENCES airports(icao_code),

    CONSTRAINT unique_daily_airport_stat
        UNIQUE (icao_code, stat_date)
);
CREATE TABLE IF NOT EXISTS aircraft_positions (
    position_id SERIAL PRIMARY KEY,
    snapshot_time TIMESTAMP NOT NULL,
    icao24 VARCHAR(6) NOT NULL,
    callsign VARCHAR(20),
    origin_country VARCHAR(100),
    time_position TIMESTAMP,
    last_contact TIMESTAMP,
    longitude NUMERIC(9, 6),
    latitude NUMERIC(9, 6),
    baro_altitude NUMERIC(10, 2),
    geo_altitude NUMERIC(10, 2),
    on_ground BOOLEAN,
    velocity NUMERIC(10, 2),
    true_track NUMERIC(10, 2),
    vertical_rate NUMERIC(10, 2),
    squawk VARCHAR(10),
    spi BOOLEAN,
    position_source INT,

    CONSTRAINT unique_aircraft_position
        UNIQUE (snapshot_time, icao24)
);
