import georinex as gr
import pandas as pd

# Path to your RINEX file
file_path = r'C:\Users\KhushaldasBadhan\OneDrive - ODYSSEUS SPACE\Documents\semester\GNSS\HW5\zimm1000.23o'

# Read the RINEX file
obs = gr.load(file_path)

print(obs)

# Convert the xarray.Dataset to a pandas.DataFrame
# The argument 'time' in to_dataframe() stacks all the data along the time dimension
df = obs.to_dataframe()

# Save the DataFrame as a CSV file
csv_file_path = 'output_observation_data.csv'
df.to_csv(csv_file_path)

print(f"Observation data saved to {csv_file_path}")
