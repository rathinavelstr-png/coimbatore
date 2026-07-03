"""
Kovai SkyWatch
Author: Anisha M.

Data source: Open-Meteo (free, no API key required)
Docs: https://open-meteo.com/en/docs
"""

import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Kovai SkyWatch",
    page_icon="🌤️",
    layout="wide",
)

# ----------------------------
# Constants
# ----------------------------
LATITUDE = 11.0168
LONGITUDE = 76.9558
CITY_NAME = "Coimbatore, Tamil Nadu"

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}

# ----------------------------
# Data fetching (cached for 5 minutes so we don't hammer the API,
# but still refreshes automatically to stay "live")
# ----------------------------
@st.cache_data(ttl=300)
def fetch_weather_data():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                   "precipitation,weather_code,wind_speed_10m,surface_pressure",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,"
                  "wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                 "weather_code",
        "timezone": "Asia/Kolkata",
        "forecast_days": 7,
    }
    response = requests.get(WEATHER_API_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def safe_fetch():
    try:
        return fetch_weather_data(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


# ----------------------------
# Header
# ----------------------------
st.title("🌤️ Kovai SkyWatch")
st.caption(f"Live weather data for {CITY_NAME} · Source: Open-Meteo")

col_refresh, col_time = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 Refresh now"):
        st.cache_data.clear()
        st.rerun()
with col_time:
    st.write(f"Last loaded: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")

data, error = safe_fetch()

if error:
    st.error(f"Could not fetch live weather data. Error: {error}")
    st.stop()

# ----------------------------
# Current conditions
# ----------------------------
current = data["current"]
weather_desc = WEATHER_CODES.get(current["weather_code"], "Unknown")

st.subheader("Current Conditions")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Temperature", f"{current['temperature_2m']} °C")
c2.metric("Feels Like", f"{current['apparent_temperature']} °C")
c3.metric("Humidity", f"{current['relative_humidity_2m']} %")
c4.metric("Wind Speed", f"{current['wind_speed_10m']} km/h")
c5.metric("Condition", weather_desc)

st.divider()

# ----------------------------
# Hourly temperature & humidity chart (next 48 hours = "live" trend)
# ----------------------------
hourly = data["hourly"]
df_hourly = pd.DataFrame({
    "time": pd.to_datetime(hourly["time"]),
    "temperature": hourly["temperature_2m"],
    "humidity": hourly["relative_humidity_2m"],
    "rain_probability": hourly["precipitation_probability"],
    "wind_speed": hourly["wind_speed_10m"],
})

# Keep only from now onward, next 48 hours
now = pd.Timestamp.now()
df_hourly = df_hourly[df_hourly["time"] >= now - pd.Timedelta(hours=1)].head(48)

st.subheader("Hourly Forecast — Next 48 Hours")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_hourly["time"], y=df_hourly["temperature"],
    mode="lines+markers", name="Temperature (°C)",
    line=dict(color="#e76f51", width=3),
))
fig.add_trace(go.Scatter(
    x=df_hourly["time"], y=df_hourly["humidity"],
    mode="lines", name="Humidity (%)",
    line=dict(color="#2a9d8f", width=2, dash="dot"),
    yaxis="y2",
))

fig.update_layout(
    xaxis_title="Time",
    yaxis=dict(title="Temperature (°C)"),
    yaxis2=dict(title="Humidity (%)", overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=450,
    margin=dict(l=10, r=10, t=30, b=10),
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Rain probability chart
# ----------------------------
st.subheader("Rain Probability — Next 48 Hours")
fig_rain = go.Figure()
fig_rain.add_trace(go.Bar(
    x=df_hourly["time"], y=df_hourly["rain_probability"],
    marker_color="#457b9d", name="Rain probability (%)",
))
fig_rain.update_layout(
    xaxis_title="Time", yaxis_title="Rain Probability (%)",
    height=350, margin=dict(l=10, r=10, t=30, b=10),
)
st.plotly_chart(fig_rain, use_container_width=True)

st.divider()

# ----------------------------
# 7-day outlook
# ----------------------------
st.subheader("7-Day Outlook")
daily = data["daily"]
df_daily = pd.DataFrame({
    "Date": pd.to_datetime(daily["time"]).strftime("%a, %d %b"),
    "Max Temp (°C)": daily["temperature_2m_max"],
    "Min Temp (°C)": daily["temperature_2m_min"],
    "Rainfall (mm)": daily["precipitation_sum"],
    "Condition": [WEATHER_CODES.get(c, "Unknown") for c in daily["weather_code"]],
})
st.dataframe(df_daily, use_container_width=True, hide_index=True)

fig_daily = go.Figure()
fig_daily.add_trace(go.Scatter(
    x=df_daily["Date"], y=df_daily["Max Temp (°C)"],
    mode="lines+markers", name="Max Temp", line=dict(color="#e63946"),
))
fig_daily.add_trace(go.Scatter(
    x=df_daily["Date"], y=df_daily["Min Temp (°C)"],
    mode="lines+markers", name="Min Temp", line=dict(color="#1d3557"),
))
fig_daily.update_layout(
    xaxis_title="Date", yaxis_title="Temperature (°C)",
    height=350, margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_daily, use_container_width=True)

st.caption("Data auto-refreshes every 5 minutes when the app is reloaded, or click 'Refresh now' for the latest reading. Powered by Open-Meteo (no API key required).")
