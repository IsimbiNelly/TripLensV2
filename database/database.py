import pandas as pd
import sqlite3
import os

# Define file paths
current_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(current_dir, 'triplens.db')
target_trip_dir = os.path.join(current_dir, '../docs/trip.csv')
target_location_dir = os.path.join(current_dir, '../docs/location.csv')
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON;")

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS vendor(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS location(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pickup_longitude REAL NOT NULL,
    pickup_latitude REAL NOT NULL,
    dropoff_longitude REAL NOT NULL,
    dropoff_latitude REAL NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS trip(
    id TEXT PRIMARY KEY,
    vendor_id INTEGER NOT NULL,
    pickup_date TEXT NOT NULL,
    dropoff_date TEXT NOT NULL,
    passenger_count INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    store_and_fwd_flag TEXT NOT NULL CHECK (store_and_fwd_flag IN ('Y','N')),
    trip_duration INTEGER NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendor(id),
    FOREIGN KEY (location_id) REFERENCES location(id)
)
""")

# create indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_pickup_date ON trip(pickup_date);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_dropoff_date ON trip(dropoff_date);")

# Insert vendors
vendors = [
    ('Yego Taxi', 'A popular taxi service in Rwanda'),
    ('SafeBoda', 'A leading motorcycle taxi service in East Africa')
]

for name, desc in vendors:
    cursor.execute("""
        INSERT OR IGNORE INTO vendor (Name, Description) VALUES (?, ?)
    """, (name, desc))


conn.commit()

# Load CSVs with pandas
locations_df = pd.read_csv(target_location_dir)
locations_df.to_sql("location", conn, if_exists="append", index=False)

trips_df = pd.read_csv(target_trip_dir)

# Rename columns to match table
trips_df.rename(columns={
    'pickup_datetime': 'pickup_date',
    'dropoff_datetime': 'dropoff_date',
}, inplace=True)

trips_df.to_sql("trip", conn, if_exists="append", index=False)

conn.commit()
conn.close()