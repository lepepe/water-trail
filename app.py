import streamlit as st
from streamlit_folium import st_folium
import folium
from folium import plugins
import pandas as pd
import database as db
import json

st.set_page_config(page_title="Suwannee River Kayak Route", layout="wide")

# Database Connection
conn = db.create_connection()

# Sidebar for Trip Selection
st.sidebar.title("Kayak Trips")
trips = db.get_all_trips(conn)
trip_names = [trip[1] for trip in trips]
selected_trip_name = st.sidebar.selectbox("Select a Trip", trip_names)
selected_trip_id = trips[trip_names.index(selected_trip_name)][0]

# Add New Trip Form
st.sidebar.title("Add a New Trip")
new_trip_name = st.sidebar.text_input("Trip Name")
new_trip_description = st.sidebar.text_area("Trip Description")
points_json = st.sidebar.text_area(
"Points (JSON format)",
placeholder="""
[
    {
        "name": "Point 1",
        "coords": [30.1, -83.1],
        "icon": "fa-star",
        "color": "orange"
    }
]
""",
)
path_json = st.sidebar.text_area(
    "Path (JSON format)",
    placeholder="""
[
    [30.1, -83.1],
    [30.2, -83.2]
]
""",
)

if st.sidebar.button("Add Trip"):
    if new_trip_name and points_json and path_json:
        try:
            points_data = json.loads(points_json)
            path_data = json.loads(path_json)

            trip_id = db.add_trip(conn, new_trip_name, new_trip_description)

            for p in points_data:
                db.add_point(
                    conn,
                    trip_id,
                    p["name"],
                    p["coords"][0],
                    p["coords"][1],
                    p.get("icon", "fa-map-marker"),
                    p.get("color", "blue"),
                )

            for lat, lon in path_data:
                db.add_path(conn, trip_id, lat, lon)

            st.sidebar.success("Trip added successfully!")
            # Refresh the page to see the new trip in the selection
            st.experimental_rerun()

        except json.JSONDecodeError:
            st.sidebar.error("Invalid JSON format. Please check your input.")
        except Exception as e:
            st.sidebar.error(f"An error occurred: {e}")
    else:
        st.sidebar.warning("Please fill in all the required fields.")


# Load Trip Data
points_data, river_path_data = db.get_trip_data(conn, selected_trip_id)

points = [
    {
        "name": p[0],
        "coords": [p[1], p[2]],
        "icon": p[3],
        "color": p[4],
    }
    for p in points_data
]

river_path = [[lat, lon] for lat, lon in river_path_data]

# App Layout
st.title(selected_trip_name)
st.markdown(f"Explore the scenic kayak route for **{selected_trip_name}**.")

# Create map
# Recalculate center based on selected trip
if river_path:
    avg_lat = sum(p[0] for p in river_path) / len(river_path)
    avg_lon = sum(p[1] for p in river_path) / len(river_path)
    map_center = [avg_lat, avg_lon]
else:
    map_center = [30.28, -82.92]  # Default center

suwannee_map = folium.Map(location=map_center, zoom_start=10, tiles="OpenStreetMap")

# Add markers
for p in points:
    folium.Marker(
        location=p["coords"],
        popup=p["name"],
        tooltip=p["name"],
        icon=folium.Icon(color=p["color"], icon=p["icon"], prefix="fa"),
    ).add_to(suwannee_map)

# Add River Route (PolyLine)
if river_path:
    folium.PolyLine(
        river_path,
        color="#00FFFF",
        weight=6,
        opacity=0.9,
        popup=f"{selected_trip_name} Route",
    ).add_to(suwannee_map)

# Add plugins for enhanced user interaction
plugins.Fullscreen().add_to(suwannee_map)
plugins.MeasureControl(
    position="topleft",
    primary_length_unit="miles",
    secondary_length_unit="kilometers",
).add_to(suwannee_map)

col1, col2 = st.columns([2, 1])
with col1:
    # Display Map
    st.subheader("Interactive Route Map")
    st.markdown(
        "Use zoom, drag, and the new Measure tool (top left) to explore the full route."
    )
    st_folium(suwannee_map, width=1200, height=600, key=f"map_{selected_trip_id}")

with col2:
    st.subheader("📋 Waypoint Summary")
    if points:
        df = pd.DataFrame(points)
        df = df.rename(columns={"name": "Waypoint", "coords": "Latitude/Longitude"})
        df["Latitude"] = df["Latitude/Longitude"].apply(lambda x: f"{x[0]:.4f}")
        df["Longitude"] = df["Latitude/Longitude"].apply(lambda x: f"{x[1]:.4f}")
        df = df[["Waypoint", "Latitude", "Longitude"]]
        st.dataframe(df, hide_index=True)
    else:
        st.write("No waypoints for this trip.")

# Footer
st.caption("Data source: Suwannee River Water Management District, Florida DEP, USGS")

# Close Database Connection
conn.close()