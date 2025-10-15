import pandas as pd
import os

# Define file paths
current_dir = os.path.dirname(os.path.abspath(__file__))
source_file = os.path.join(current_dir, '../docs/train.csv')
target_trip_dir = os.path.join(current_dir, '../docs/trip.csv')
target_location_dir = os.path.join(current_dir, '../docs/location.csv')

# Read only the required columns for trip
trip_df = pd.read_csv(
    source_file,
    usecols=['id','vendor_id','pickup_datetime','dropoff_datetime','passenger_count','store_and_fwd_flag','trip_duration']
)

# Read only the required columns for location
location_df = pd.read_csv(
    source_file,
    usecols=['pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude']
)

# Add location_id to the new csv
trip_df['location_id'] = range(1, len(trip_df) + 1)

# Save new CSVs
trip_df.to_csv(target_trip_dir, index=False)
location_df.to_csv(target_location_dir, index=False)
