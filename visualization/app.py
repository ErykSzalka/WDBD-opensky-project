import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="OpenSky Dashboard",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 16px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

df = pd.DataFrame({
    "airport": ["WAW", "KRK", "GDN", "WAW", "KRK", "WRO", "WAW", "GDN", "POZ", "KTW"],
    "aircraft": ["SP001", "SP002", "SP003", "SP004", "SP005", "SP006", "SP007", "SP008", "SP009", "SP010"],
    "country": ["Poland", "Germany", "Poland", "France", "Poland", "Italy", "Germany", "Norway", "Spain", "Poland"],
    "flight_type": ["arrival", "departure", "arrival", "departure", "arrival", "departure", "arrival", "departure", "arrival", "departure"],
    "delay_min": [5, 12, 0, 25, 7, 3, 18, 9, 14, 2]
})

st.title("OpenSky Flight Analytics")
st.caption("Testowy dashboard przed podpięciem bazy PostgreSQL")

with st.sidebar:
    st.header("Filtry")

    selected_airports = st.multiselect(
        "Lotniska",
        df["airport"].unique(),
        default=df["airport"].unique()
    )

    selected_types = st.multiselect(
        "Typ lotu",
        df["flight_type"].unique(),
        default=df["flight_type"].unique()
    )

filtered_df = df[
    (df["airport"].isin(selected_airports)) &
    (df["flight_type"].isin(selected_types))
]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Liczba lotów", len(filtered_df))
col2.metric("Samoloty", filtered_df["aircraft"].nunique())
col3.metric("Lotniska", filtered_df["airport"].nunique())
col4.metric("Śr. opóźnienie", f"{filtered_df['delay_min'].mean():.1f} min")

left, right = st.columns(2)

airport_counts = filtered_df["airport"].value_counts().reset_index()
airport_counts.columns = ["airport", "flights"]

fig_airports = px.bar(
    airport_counts,
    x="airport",
    y="flights",
    title="Liczba lotów według lotniska",
    text_auto=True
)

fig_airports.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=60, b=20)
)

type_counts = filtered_df["flight_type"].value_counts().reset_index()
type_counts.columns = ["flight_type", "count"]

fig_types = px.pie(
    type_counts,
    names="flight_type",
    values="count",
    title="Przyloty vs odloty",
    hole=0.45
)

fig_types.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=60, b=20)
)

with left:
    st.plotly_chart(fig_airports, use_container_width=True)

with right:
    st.plotly_chart(fig_types, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

fig_delay = px.box(
    filtered_df,
    x="airport",
    y="delay_min",
    title="Rozkład opóźnień według lotniska"
)

fig_delay.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=60, b=20)
)

country_counts = filtered_df["country"].value_counts().reset_index()
country_counts.columns = ["country", "count"]

fig_country = px.bar(
    country_counts,
    x="country",
    y="count",
    title="Liczba lotów według kraju",
    text_auto=True
)

fig_country.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=60, b=20)
)

with bottom_left:
    st.plotly_chart(fig_delay, use_container_width=True)

with bottom_right:
    st.plotly_chart(fig_country, use_container_width=True)

st.subheader("Dane szczegółowe")
st.dataframe(filtered_df, use_container_width=True)