import numpy as np
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


def read_GNSS_data(rinex_file, sp3_file, sv_end, epoch, frequency):
    # Load the RINEX file
    rinex_data = gr.load(rinex_file)
    # Convert the data to a DataFrame
    rinex = rinex_data.to_dataframe().reset_index()
    
    # Load the SP3 file
    sp3_data = gr.load(sp3_file)
    # Convert the data to a DataFrame
    sp3 = sp3_data.to_dataframe().reset_index()
    
    # generate satellite id
    sv = ["G{:02}".format(i) for i in range(1, sv_end+1)]
    #print(sv)
    
    # Initialize the compiled_data DataFrame
    compiled_data = pd.DataFrame(columns=['time', 'sv', 'x', 'y', 'z', 'clock_bias', frequency])

    rows = []  # List to hold the row data
    # Loop over the SVs and append data to the rows list

    for satellite in sv:
        # Query for each satellite
        x_query = sp3.query("time == @epoch and sv == @satellite and ECEF == 'x'")
        y_query = sp3.query("time == @epoch and sv == @satellite and ECEF == 'y'")
        z_query = sp3.query("time == @epoch and sv == @satellite and ECEF == 'z'")
        clock_query = sp3.query("time == @epoch and sv == @satellite and ECEF == 'x'")
        frequency_query = rinex.query("time == @epoch and sv == @satellite")

        # Check if the specific column in the queries returned data, and skip the satellite if any data is missing
        if (x_query['position'].empty or y_query['position'].empty or z_query['position'].empty or 
            clock_query['clock'].empty or frequency_query.empty or pd.isna(frequency_query[frequency].values[0])):
            continue

        # Create a new row for each satellite with complete data
        new_row = {
            'time': epoch,
            'sv': satellite,
            'x': x_query['position'].values[0],
            'y': y_query['position'].values[0],
            'z': z_query['position'].values[0],
            'clock_bias': clock_query['clock'].values[0],
            frequency: frequency_query[frequency].values[0]
        }
        rows.append(new_row)

    
    # Convert the rows list to a DataFrame
    compiled_data = pd.DataFrame(rows)
    return compiled_data  # Return the compiled DataFrame

def main():
    rinex_file = 'zimm1000.23o'
    sp3_file = 'igs22571.sp3'
    epoch = '2023-04-10 11:00:00'
    sv_end = 32
    csv_file = 'compiled_data.csv'
    frequency = 'C1'
    
    compiled_df = read_GNSS_data(rinex_file, sp3_file, sv_end, epoch, frequency)
    print(compiled_df.head())
    compiled_df.to_csv(csv_file)

if __name__ == '__main__':
    main()
