import pandas as pd
import psycopg2
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh
 
DB_CONFIG = {
    "dbname": "truck_telemetry",
    "user": "postgres",
    "password": "boomesh1329",
    "host": "localhost",
    "port": "5432",
}
 
st.set_page_config(page_title="Truck Fleet Dashboard", layout="wide")
st.title("🚚 Truck101 Live Telemetry Dashboard")
 
# Refresh the whole page every 3 seconds to pick up new readings.
st_autorefresh(interval=3000, key="refresh")
 
 
def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(
        """
        SELECT reading_time, engine_temp, fuel_level, speed, latitude, longitude
        FROM truck_readings
        ORDER BY reading_time DESC
        LIMIT 50
        """,
        conn,
    )
    conn.close()
    return df.sort_values("reading_time")
 
 
try:
    df = load_data()
except Exception as e:
    st.error(f"Could not connect to the database: {e}")
    st.stop()
 
if df.empty:
    st.warning("No data yet -- make sure publisher.py and mqtt_to_db.py are running.")
    st.stop()
 
latest = df.iloc[-1]
 
# --- Top row: live metric numbers ---
col1, col2, col3 = st.columns(3)
col1.metric("Engine Temp", f"{latest['engine_temp']} °C")
col2.metric("Fuel Level", f"{latest['fuel_level']} %")
col3.metric("Speed", f"{latest['speed']} km/h")
 
st.divider()
 
 
def make_chart(df, y_col, title, color):
    fig = px.line(df, x="reading_time", y=y_col, markers=True)
    fig.update_traces(line_color=color)
    fig.update_layout(
        title=title,
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title=None,
        yaxis_title=None,
    )
    return fig
 
 
# --- Grid: 2 charts per row instead of one long stacked list ---
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.plotly_chart(
        make_chart(df, "engine_temp", "Engine Temperature (°C)", "#FF6B6B"),
        use_container_width=True,
    )
with row1_col2:
    st.plotly_chart(
        make_chart(df, "fuel_level", "Fuel Level (%)", "#4ECDC4"),
        use_container_width=True,
    )
 
row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.plotly_chart(
        make_chart(df, "speed", "Speed (km/h)", "#FFD166"),
        use_container_width=True,
    )
with row2_col2:
    st.subheader("Last Known GPS Location")
    st.map(pd.DataFrame(
        {"lat": [latest["latitude"]], "lon": [latest["longitude"]]}
    ))
 
st.caption(f"Last updated: {latest['reading_time']}")