import streamlit as st
from streamlit_folium import st_folium
import folium
from folium import plugins
from folium.plugins import MeasureControl
import pandas as pd

st.set_page_config(page_title="Suwannee River Kayak Route", layout="wide")
st.title("Suwannee River Kayak Adventure")
st.markdown("""
Explore the scenic kayak route along the **Suwannee River** — from White Springs to Mayo — 
with camps and cabins marked along the way!
""")

points = [
    {
        "name": "White Springs Launch (Mile 171)",
        "coords": [30.3319, -82.7598],
        "icon": "fa-water",
        "color": "darkblue",
    },
    {
        "name": "Holton Creek River Camp (Mile 140.9)",
        "coords": [30.4741, -83.2234],
        "icon": "fa-campground",
        "color": "green",
    },
    {
        "name": "Suwannee River State Park Cabins (Mile 127.7)",
        "coords": [30.3843, -83.1707],
        "icon": "fa-house",
        "color": "orange",
    },
    {
        "name": "Dowling Park River Camp (Mile 113)",
        "coords": [30.2322, -83.1803],
        "icon": "fa-campground",
        "color": "green",
    },
    {
        "name": "Mayo Take-Out / Suwannee River Rendezvous (Mile ~98)",
        "coords": [30.0529, -83.1712],
        "icon": "fa-anchor",
        "color": "red",
    },
]

# River-like curved path (used for the PolyLine)
river_path = [
    [30.3319, -82.7598], # White Springs Launch
    [30.3380, -82.7950],
    [30.3470, -82.8350],
    [30.3600, -82.8700],
    [30.3750, -82.9050],
    [30.3850, -82.9400],
    [30.4050, -82.9700],
    [30.4200, -83.0000],
    [30.4350, -83.0300],
    [30.4500, -83.0600],
    [30.4600, -83.0900],
    [30.4700, -83.1250],
    [30.4741, -83.1600], # Approaching Holton Creek
    [30.4741, -83.2234], # Holton Creek River Camp (Mile 140.9)
    [30.4500, -83.2250],
    [30.4300, -83.2150],
    [30.4050, -83.2000],
    [30.3843, -83.1707], # Suwannee River State Park Cabins (Mile 127.7)
    [30.3700, -83.1650],
    [30.3500, -83.1700],
    [30.3300, -83.1750],
    [30.3100, -83.1800],
    [30.2900, -83.1805],
    [30.2700, -83.1810],
    [30.2500, -83.1810],
    [30.2322, -83.1803], # Dowling Park River Camp (Mile 113)
    [30.2100, -83.1800],
    [30.1900, -83.1790],
    [30.1700, -83.1770],
    [30.1500, -83.1750],
    [30.1300, -83.1730],
    [30.1100, -83.1720],
    [30.0900, -83.1715],
    [30.0700, -83.1712],
    [30.0529, -83.1712], # Mayo Take-Out / Suwannee River Rendezvous (Mile ~98)
]

# Create map
suwannee_map = folium.Map(location=[30.28, -82.92], zoom_start=10, tiles="OpenStreetMap")

# Add markers
for p in points:
    folium.Marker(
        location=p["coords"],
        popup=p["name"],
        tooltip=p["name"],
        icon=folium.Icon(color=p["color"], icon=p["icon"], prefix="fa"),
    ).add_to(suwannee_map)

# Add River Route (PolyLine)
folium.PolyLine(
    river_path,
    color="#00FFFF",
    weight=6,
    opacity=0.9,
    popup="Suwannee River Kayak Route",
).add_to(suwannee_map)

# Add plugins for enhanced user interaction
# 1. Fullscreen button
plugins.Fullscreen().add_to(suwannee_map)

# 2. Measure control (for measuring distance on the map)
plugins.MeasureControl(
    position="topleft",
    primary_length_unit="miles",
    secondary_length_unit="kilometers",
).add_to(suwannee_map)

col1, col2 = st.columns([2, 1]) 
with col1:
    # Display Map
    st.subheader("Interactive Route Map")
    st.markdown("Use zoom, drag, and the new Measure tool (top left) to explore the full route.")
    st_folium(suwannee_map, width=1200, height=600, key="suwannee_map_key")

with col2:
    # Route Summary Table
    st.subheader("📋 Waypoint Summary")
    df = pd.DataFrame(points)
    df = df.rename(columns={"name": "Waypoint", "coords": "Latitude/Longitude"})
    df["Latitude"] = df["Latitude/Longitude"].apply(lambda x: f"{x[0]:.4f}")
    df["Longitude"] = df["Latitude/Longitude"].apply(lambda x: f"{x[1]:.4f}")
    df = df[["Waypoint", "Latitude", "Longitude"]]
    st.dataframe(df, hide_index=True)

# Footer
st.caption("Data source: Suwannee River Water Management District, Florida DEP, USGS")