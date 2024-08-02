import georinex as gr
import pandas as pd

def rinex_to_csv(rinex_file, csv_file, n):
    """
    Load a RINEX file and save its contents to a CSV file.

    Parameters:
    rinex_file (str): Path to the RINEX file.
    csv_file (str): Path for the output CSV file.
    """
    try:
        # Load the RINEX file
        rinex_data = gr.load(rinex_file)

        # Convert the data to a DataFrame
        rinex = rinex_data.to_dataframe()
        print(rinex)

        # Save the DataFrame to a CSV file
        rinex.to_csv(csv_file)
        print(f"Data saved to {csv_file}")
        
        print ('value of row ' + str(n))
        print (rinex.iloc[n])
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        print(rinex.loc[(epoch, satellite), 'C1'])
        
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        print(rinex.query("time == @epoch and sv == @satellite")['C1'].values[0])
        

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
satellite = 'G02'
epoch='2023-04-10 11:00:00'
n = 40921
rinex_file = 'zimm1000.23n'  # Replace with the path to your RINEX file
csv_file = 'zimm1000n.csv'  # Path for the output CSV file
rinex_to_csv(rinex_file, csv_file, n)