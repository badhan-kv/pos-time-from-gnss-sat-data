import georinex as gr
import pandas as pd

def find_satellite_clock_correction(nav_file, satellite_id, epoch):
    # Load the navigation data using georinex
    nav_data = gr.load(nav_file)
    
    # Convert to a DataFrame and reset index
    nav_df = nav_data.to_dataframe().reset_index()

    # Convert the epoch string to a pandas.Timestamp
    epoch = pd.to_datetime(epoch)

    # Filter the DataFrame for the selected satellite and create a separate copy
    sat_data = nav_df[nav_df['sv'] == satellite_id].copy()

    # Ensure the 'time' column is in datetime format and sort by time in descending order
    sat_data['time'] = pd.to_datetime(sat_data['time'])
    sat_data.sort_values('time', ascending=False, inplace=True)

    # Iterate through the sorted data to find the first entry with valid data before the specified time
    for index, row in sat_data.iterrows():
        if row['time'] <= epoch and not pd.isna(row['SVclockBias']):
            # Extract the clock correction parameters
            actual_epoch = row['time']
            SVclockBias = row['SVclockBias']
            SVclockDrift = row['SVclockDrift']
            SVclockDriftRate = row['SVclockDriftRate']
            return actual_epoch, SVclockBias, SVclockDrift, SVclockDriftRate

    raise ValueError(f"No valid data found for satellite {satellite_id} before or at {epoch}")

# Example usage
nav_file = 'zimm1000.23n'
satellite_id = 'G03'
epoch= '2023-04-10 13:15:00'

actual_epoch, SVclockBias, SVclockDrift, SVclockDriftRate = find_satellite_clock_correction(nav_file, satellite_id, epoch)
print(f"Actual Epoch: {actual_epoch}, SVclockBias: {SVclockBias}, SVclockDrift: {SVclockDrift}, SVclockDriftRate: {SVclockDriftRate}")