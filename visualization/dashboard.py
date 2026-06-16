import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from database.connection import connect_to_database

from visualization.reader import (
    flights_by_min_duration,
    airport_traffic_by_country,
    airlines_flights_above_count,
    daily_stats_for_airport,
    arrivals_by_airport,
    most_popular_routes,
    most_active_aircraft,
    avg_flight_duration_all_airports,
    arrivals_over_time,
    arrivals_by_hour,
    compare_specific_airports,
    get_all_cities,
    airport_traffic_by_multiple_cities
)

load_dotenv()

st.set_page_config(
    page_title="Dashboard OpenSky",
    layout="wide"
)

@st.cache_resource
def get_connection():
    database_name = os.getenv("DB_NAME")
    return connect_to_database(database_name)

conn = get_connection()

st.title("Dashboard lotów OpenSky")

# Pobieramy główną listę lotnisk raz, żeby nie męczyć bazy przy każdym kliknięciu
df_airports = arrivals_by_airport(conn)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Przegląd ogólny", "Lotniska", "Trasy", "Linie i samoloty", "Filtrowanie"])

with tab1:
    st.header("Przegląd ogólny")
    
    # Filtr agregacji czasu przeniesiony bezpośrednio nad wykres
    period_pl = st.selectbox("Agregacja czasu", ["dzien", "miesiac"])
    period = "day" if period_pl == "dzien" else "month"
    
    if not df_airports.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Liczba lotnisk", len(df_airports))
        with col2:
            st.metric("Łączna liczba przylotów", int(df_airports["arrival_count"].sum()))
        with col3:
            st.metric("Największy ruch", df_airports.iloc[0]["icao_code"])
    else:
        st.warning("Brak danych o przylotach w bazie, ale możesz przeglądać inne zakładki.")

    st.subheader("Liczba przylotów w czasie")
    df_time = arrivals_over_time(conn, period)
    if df_time is not None and not df_time.empty:
        fig = px.line(df_time, x="time_period", y="flight_count", title="Liczba przylotów w czasie", markers=True)
        st.plotly_chart(fig, width='stretch')

    st.subheader("Rozkład przylotów według godziny")
    df_hour = arrivals_by_hour(conn)
    if df_hour is not None and not df_hour.empty:
        fig = px.bar(df_hour, x="arrival_hour", y="flight_count", title="Liczba przylotów według godziny")
        st.plotly_chart(fig, width='stretch')


with tab2:
    st.header("Analiza lotnisk")

    st.subheader("Liczba przylotów według lotniska")
    # Osobny suwak limitu tylko dla tej sekcji
    limit_airports = st.slider("Liczba wyświetlanych lotnisk", 1, 100, 10)
    
    if not df_airports.empty:
        fig = px.bar(
            df_airports.head(limit_airports), x="icao_code", y="arrival_count", 
            hover_data=["airport_name"], title="Najbardziej aktywne lotniska"
        )
        st.plotly_chart(fig, width='stretch')
        st.dataframe(df_airports.head(limit_airports), width='stretch')

    st.subheader("Średni czas lotu dla lotnisk")
    df_avg = avg_flight_duration_all_airports(conn)
    if df_avg is not None and not df_avg.empty:
        fig = px.bar(
            df_avg.head(limit_airports), x="airport_name", y="avg_duration_min", 
            hover_data=["total_flights"], title="Średni czas lotu według lotniska"
        )
        st.plotly_chart(fig, width='stretch')

    st.subheader("Statystyki dzienne wybranego lotniska")
    if not df_airports.empty:
        selected_airport = st.selectbox("Wybierz lotnisko", df_airports["icao_code"].tolist())
        df_daily = daily_stats_for_airport(selected_airport, conn)

        if df_daily is not None and not df_daily.empty:
            fig = px.line(df_daily, x="stat_date", y="arrival_count", title=f"Dzienna liczba przylotów dla {selected_airport}", markers=True)
            st.plotly_chart(fig, width='stretch')

            fig = px.line(df_daily, x="stat_date", y="avg_flight_duration_min", title=f"Średni czas lotu dla {selected_airport}", markers=True)
            st.plotly_chart(fig, width='stretch')

            st.dataframe(df_daily, width='stretch')
        else:
            st.info("Brak danych dla wybranego lotniska.")


with tab3:
    st.header("Najpopularniejsze trasy")
    limit_routes = st.slider("Liczba wyświetlanych tras", 1, 100, 10)

    df_routes = most_popular_routes(conn, limit_routes)
    if df_routes is not None and not df_routes.empty:
        fig = px.bar(
            df_routes, x="flight_count", y="departure_airport", color="arrival_airport", 
            orientation="h", title="Najpopularniejsze trasy"
        )
        st.plotly_chart(fig, width='stretch')
        st.dataframe(df_routes, width='stretch')


with tab4:
    st.header("Linie lotnicze i samoloty")

    st.subheader("Linie lotnicze powyżej wybranej liczby lotów")
    min_flights = st.slider("Minimalna liczba lotów linii", 1, 500, 5)
    limit_airlines = st.slider("Liczba wyświetlanych linii", 1, 100, 10)
    
    df_airlines = airlines_flights_above_count(min_flights, conn)
    if df_airlines is not None and not df_airlines.empty:
        fig = px.bar(
            df_airlines.head(limit_airlines), x="airline_name", y="flight_count", title="Najbardziej aktywne linie lotnicze"
        )
        st.plotly_chart(fig, width='stretch')
        st.dataframe(df_airlines.head(limit_airlines), width='stretch')
    else:
        st.info("Brak linii spełniających warunek.")

    st.subheader("Najaktywniejsze samoloty")
    limit_aircraft = st.slider("Liczba wyświetlanych samolotów", 1, 100, 10)
    df_aircraft = most_active_aircraft(conn, limit_aircraft)
    if df_aircraft is not None and not df_aircraft.empty:
        fig = px.bar(
            df_aircraft, x="icao24", y="total_flights", hover_data=["airline_name"], title="Najaktywniejsze samoloty"
        )
        st.plotly_chart(fig, width='stretch')
        st.dataframe(df_aircraft, width='stretch')


with tab5:
    st.header("Filtrowanie danych")

    st.subheader("Ruch lotniczy według miast")

    available_cities = get_all_cities(conn)

    default_city = ["Warsaw"] if "Warsaw" in available_cities else []
    
    selected_cities = st.multiselect(
        "Wybierz jedno lub więcej miast",
        available_cities,
        default=default_city
    )


    if selected_cities:
        df_cities = airport_traffic_by_multiple_cities(selected_cities, conn)
        
        if df_cities is not None and not df_cities.empty:
            # Dynamiczny tytuł w zależności od tego, ile miast wybrano
            if len(selected_cities) <= 3:
                title_suffix = ", ".join(selected_cities)
            else:
                title_suffix = f"wybranych {len(selected_cities)} miast"
                
            fig = px.bar(
                df_cities, x="icao_code", y="total_arrivals", hover_data=["airport_name", "city"], 
                title=f"Ruch lotniczy: {title_suffix}"
            )
            st.plotly_chart(fig, width='stretch')
            st.dataframe(df_cities, width='stretch')
        else:
            st.info("Brak przylotów dla wybranych miast.")
    else:
        st.warning("Wybierz co najmniej jedno miasto z listy, aby zobaczyć dane.")

    st.subheader("Loty dłuższe niż wybrany czas")
    min_duration = st.slider("Minimalny czas lotu w minutach", 0, 1000, 60)
    df_duration = flights_by_min_duration(min_duration, conn)
    if df_duration is not None and not df_duration.empty:
        st.metric("Liczba lotów", len(df_duration))
        fig = px.histogram(
            df_duration, x="flight_duration_min", nbins=30, title="Rozkład czasu trwania lotów"
        )
        st.plotly_chart(fig, width='stretch')
        st.dataframe(df_duration, width='stretch')

    st.subheader("Porównanie wybranych lotnisk")
    if not df_airports.empty:
        selected_airports = st.multiselect(
            "Wybierz lotniska do porównania",
            df_airports["icao_code"].tolist(),
            default=df_airports["icao_code"].head(3).tolist()
        )

        if selected_airports:
            df_compare = compare_specific_airports(selected_airports, conn)
            if df_compare is not None and not df_compare.empty:
                fig = px.bar(
                    df_compare, x="icao_code", y="total_flights", hover_data=["airport_name", "avg_duration_min"], title="Porównanie lotnisk"
                )
                st.plotly_chart(fig, width='stretch')
                st.dataframe(df_compare, width='stretch')