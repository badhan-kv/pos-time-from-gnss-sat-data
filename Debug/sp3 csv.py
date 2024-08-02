import georinex as gr
import pandas as pd

def sp3_to_csv(sp3_file, csv_file, wide_csv_file, n):
    """
    Load an SP3 file and save its contents to a CSV file.

    Parameters:
    sp3_file (str): Path to the SP3 file.
    csv_file (str): Path for the output CSV file.
    """
    # Load the SP3 file
    sp3_data = gr.load(sp3_file)

    # Convert the data to a DataFrame
    sp3 = sp3_data.to_dataframe()

    print(sp3)

#     # Save the DataFrame to a CSV file
#     sp3.to_csv(csv_file)
#     print(f"Data saved to {csv_file}")
    
    print ('value of row ' + str(n))
    print (sp3.iloc[n])
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    print(sp3.loc[(epoch, satellite, 'x'), 'clock'])
    
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    print(sp3.query("time == @epoch and sv == @satellite and ECEF == 'x'")['clock'].values[0])
   
# Example usage
satellite = 'G03'
epoch='2023-04-10 11:00:00'
n = 4227
sp3_file = 'igs22571.sp3'  # Replace with the path to your SP3 file
csv_file = 'igs22571.csv'  # Path for the output CSV file
wide_csv_file = 'igs22571_wide.csv'  # Path for the output wide format CSV file
sp3_to_csv(sp3_file, csv_file, wide_csv_file, n)
