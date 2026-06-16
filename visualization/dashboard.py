import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from database.connection import connect_to_database

from reader import (
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
    compare_specific_airports
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

conn = get_connection()

st.title("Dashboard lotów OpenSky")
st.sidebar.header("Ustawienia statystyk")
period = st.sidebar.selectbox("Agregacja czasu",["dzien", "miesiac"])


limit = st.sidebar.slider("Liczba wyników",1,100,10)

min_duration = st.sidebar.slider("Minimalny czas lotu w minutach",0,1000,60)

min_flights = st.sidebar.slider("Minimalna liczba lotów linii",1,500,5)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Przegląd ogólny","Lotniska","Trasy","Linie i samoloty","Filtrowanie"])


with tab1:
    st.header("Przegląd ogólny")
    if period=="dzien":
        period="day"
    else:
        period="month"
    df_time = arrivals_over_time(conn, period)
    df_hour = arrivals_by_hour(conn)
    df_airports = arrivals_by_airport(conn)
    if df_airports.empty:
        st.warning("Brak danych o przylotach w bazie.")
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Lotniska docelowe z przylotami", len(df_airports))
    with col2:
        st.metric("Łączna liczba przylotów", int(df_airports["arrival_count"].sum()))
    with col3:
        top_airport = df_airports.iloc[0]
        st.metric("Największy ruch",top_airport["icao_code"],f'{int(top_airport["arrival_count"])} przylotów')
    st.subheader("Liczba przylotow w czasie")

    fig = px.line(
        df_time,
        x="time_period",
        y="flight_count",
        title="Liczba przylotów w czasie",
        markers=True
    )
    st.plotly_chart(fig, width='stretch')

    st.subheader("Rozkład przylotów według godziny")
    fig = px.bar(
        df_hour,
        x="arrival_hour",
        y="flight_count",
        title="Liczba przylotów według godziny"
    )
    st.plotly_chart(fig, width='stretch')


with tab2:
    st.header("Analiza lotnisk")

    df_airports = arrivals_by_airport(conn)

    st.subheader("Liczba przylotów według lotniska")

    fig = px.bar(
        df_airports.head(limit),
        x="icao_code",
        y="arrival_count",
        hover_data=["airport_name"],
        title="Najbardziej aktywne lotniska"
    )
    st.plotly_chart(fig, width='stretch')

    st.dataframe(df_airports, width='stretch')

    st.subheader("Średni czas lotu dla lotnisk")

    df_avg = avg_flight_duration_all_airports(conn)

    fig = px.bar(
        df_avg.head(limit),
        x="airport_name",
        y="avg_duration_min",
        hover_data=["total_flights"],
        title="Średni czas lotu według lotniska"
    )
    st.plotly_chart(fig, width='stretch')

    st.subheader("Statystyki dzienne wybranego lotniska")

    selected_airport = st.selectbox(
        "Wybierz lotnisko",
        df_airports["icao_code"].tolist()
    )

    df_daily = daily_stats_for_airport(selected_airport, conn)

    if not df_daily.empty:
        fig = px.line(
            df_daily,
            x="stat_date",
            y="arrival_count",
            title=f"Dzienna liczba przylotów dla {selected_airport}",
            markers=True
        )
        st.plotly_chart(fig, width='stretch')

        fig = px.line(
            df_daily,
            x="stat_date",
            y="avg_flight_duration_min",
            title=f"Średni czas lotu dla {selected_airport}",
            markers=True
        )
        st.plotly_chart(fig, width='stretch')

        st.dataframe(df_daily, width='stretch')
    else:
        st.info("Brak danych dla wybranego lotniska.")


with tab3:
    st.header("Najpopularniejsze trasy")

    df_routes = most_popular_routes(conn, limit)

    fig = px.bar(
        df_routes,
        x="flight_count",
        y="departure_airport",
        color="arrival_airport",
        orientation="h",
        title="Najpopularniejsze trasy"
    )
    st.plotly_chart(fig, width='stretch')

    st.dataframe(df_routes, width='stretch')


with tab4:
    st.header("Linie lotnicze i samoloty")

    st.subheader("Linie lotnicze powyżej wybranej liczby lotów")

    df_airlines = airlines_flights_above_count(min_flights, conn)

    if not df_airlines.empty:
        fig = px.bar(
            df_airlines.head(limit),
            x="airline_name",
            y="flight_count",
            title="Najbardziej aktywne linie lotnicze"
        )
        st.plotly_chart(fig, width='stretch')

        st.dataframe(df_airlines, width='stretch')
    else:
        st.info("Brak linii spełniających warunek.")

    st.subheader("Najaktywniejsze samoloty")

    df_aircraft = most_active_aircraft(conn, limit)

    fig = px.bar(
        df_aircraft,
        x="icao24",
        y="total_flights",
        hover_data=["airline_name"],
        title="Najaktywniejsze samoloty"
    )
    st.plotly_chart(fig, width='stretch')

    st.dataframe(df_aircraft, width='stretch')


with tab5:
    st.header("Filtrowanie danych")

    st.subheader("Loty dłuższe niż wybrany czas")

    df_duration = flights_by_min_duration(min_duration, conn)

    st.metric("Liczba lotów", len(df_duration))

    fig = px.histogram(
        df_duration,
        x="flight_duration_min",
        nbins=30,
        title="Rozkład czasu trwania lotów"
    )
    st.plotly_chart(fig, width='stretch')

    st.dataframe(df_duration, width='stretch')

    st.subheader("Ruch lotniczy według kraju")

    country = st.text_input("Podaj kraj", "Poland")

    if country:
        df_country = airport_traffic_by_country(country, conn)

        if not df_country.empty:
            fig = px.bar(
                df_country,
                x="icao_code",
                y="total_arrivals",
                hover_data=["airport_name", "city"],
                title=f"Ruch lotniczy w kraju: {country}"
            )
            st.plotly_chart(fig, width='stretch')

            st.dataframe(df_country, width='stretch')
        else:
            st.info("Brak danych dla tego kraju.")

    st.subheader("Porównanie wybranych lotnisk")

    df_airports = arrivals_by_airport(conn)

    selected_airports = st.multiselect(
        "Wybierz lotniska do porównania",
        df_airports["icao_code"].tolist(),
        default=df_airports["icao_code"].head(3).tolist()
    )

    if selected_airports:
        df_compare = compare_specific_airports(selected_airports, conn)
        fig = px.bar(
            df_compare,
            x="icao_code",
            y="total_flights",
            hover_data=["airport_name", "avg_duration_min"],
            title="Porównanie lotnisk"
        )
        st.plotly_chart(fig, width='stretch')

        st.dataframe(df_compare, width='stretch')