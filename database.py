
import sqlite3
import json

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('kayak_trips.db')
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Create tables for the kayak trips database."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                icon TEXT,
                color TEXT,
                FOREIGN KEY (trip_id) REFERENCES trips (id)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                FOREIGN KEY (trip_id) REFERENCES trips (id)
            );
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def add_trip(conn, name, description):
    """Add a new trip to the trips table."""
    sql = ''' INSERT INTO trips(name,description)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (name, description))
    conn.commit()
    return cur.lastrowid

def add_point(conn, trip_id, name, latitude, longitude, icon, color):
    """Add a new point to the points table."""
    sql = ''' INSERT INTO points(trip_id, name, latitude, longitude, icon, color)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (trip_id, name, latitude, longitude, icon, color))
    conn.commit()
    return cur.lastrowid

def add_path(conn, trip_id, latitude, longitude):
    """Add a new path point to the paths table."""
    sql = ''' INSERT INTO paths(trip_id, latitude, longitude)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (trip_id, latitude, longitude))
    conn.commit()
    return cur.lastrowid

def get_all_trips(conn):
    """Query all rows in the trips table."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips")
    rows = cur.fetchall()
    return rows

def get_trip_data(conn, trip_id):
    """Query points and path for a given trip_id."""
    cur = conn.cursor()
    cur.execute("SELECT name, latitude, longitude, icon, color FROM points WHERE trip_id=?", (trip_id,))
    points = cur.fetchall()
    cur.execute("SELECT latitude, longitude FROM paths WHERE trip_id=?", (trip_id,))
    path = cur.fetchall()
    return points, path

def setup_database():
    """Create and populate the database with initial data."""
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        # Check if data already exists
        if not get_all_trips(conn):
            # Add Suwannee River trip
            trip_id = add_trip(conn, "Suwannee River Kayak Adventure", "A scenic kayak route along the Suwannee River.")
            
            points_data = [
                {"name": "Dowling Park River Camp (Start, Mile 113)", "coords": [30.2463, -83.2461], "icon": "fa-water", "color": "blue"},
                {"name": "Lafayette Blue Springs State Park (Night 1, Mile 103.3)", "coords": [30.1272, -83.2255], "icon": "fa-campground", "color": "green"},
                {"name": "Peacock Slough River Camp (Night 2, Mile 95.8)", "coords": [30.1024, -83.1383], "icon": "fa-campground", "color": "green"},
                {"name": "Adams Tract River Camp (Take-Out, Mile 85.2)", "coords": [30.0352, -83.0189], "icon": "fa-anchor", "color": "red"}
            ]
            
            river_path_data = [
                [30.2463, -83.2461], [30.2300, -83.2450], [30.2100, -83.2400], [30.1800, -83.2350],
                [30.1500, -83.2300], [30.1272, -83.2255], [30.1200, -83.2100], [30.1150, -83.2000],
                [30.1100, -83.1850], [30.1050, -83.1650], [30.1030, -83.1500], [30.1024, -83.1383],
                [30.1000, -83.1250], [30.0900, -83.1100], [30.0800, -83.0900], [30.0650, -83.0650],
                [30.0550, -83.0450], [30.0450, -83.0300], [30.0352, -83.0189]
            ]

            for p in points_data:
                add_point(conn, trip_id, p['name'], p['coords'][0], p['coords'][1], p['icon'], p['color'])
            
            for lat, lon in river_path_data:
                add_path(conn, trip_id, lat, lon)
        
        conn.close()

if __name__ == '__main__':
    setup_database()
