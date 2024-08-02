import numpy as np
from scipy.optimize import least_squares
import georinex as gr
import pandas as pd
from data_reading import read_GNSS_data

def compute_geometry_matrix(sat_positions_m, receiver_position_m):
    num_sats = sat_positions_m.shape[0]
    geometry_matrix = np.zeros((num_sats, 4))

    for i in range(num_sats):
        diff = sat_positions_m[i, :] - receiver_position_m[:3]
        norm = np.linalg.norm(diff)
        geometry_matrix[i, :3] = diff / norm
        geometry_matrix[i, 3] = 1  # Time bias component

    return geometry_matrix

def calculate_gdop(geometry_matrix):
    G = geometry_matrix
    Q = np.linalg.inv(G.T @ G)  # Compute the inverse of G'G
    gdop = np.sqrt(np.trace(Q))  # Square root of the trace of Q
    return gdop


def pseudorange_residuals(x, sat_positions_m, pseudoranges_m, c):
    """
    Calculates the residuals between the measured pseudoranges and the pseudoranges calculated from the estimated position.
    
    Parameters:
    x (numpy.array): Current estimate of the receiver's position and clock bias [x, y, z, dt_rec].
    sat_positions_m (numpy.array): Satellite positions in ECEF coordinates in meters.
    pseudoranges_m (numpy.array): Corrected pseudorange measurements to each satellite in meters.
    c (float): Speed of light in m/s.

    Returns:
    numpy.array: Residuals for each satellite.
    """
    estimated_ranges = np.sqrt(((sat_positions_m - x[:3])**2).sum(axis=1))
    estimated_pseudoranges = estimated_ranges + c * x[3]
    residuals = pseudoranges_m - estimated_pseudoranges
    return residuals

def calculate_position_clock_bias(sat_positions_km, pseudoranges_m, sat_clock_biases_us, initial_position_m, c=299792458):
    """
    Calculates the position and clock bias of a GNSS receiver using pseudorange measurements
    and accounting for satellite clock biases, using scipy.optimize.least_squares.

    Parameters:
    sat_positions_km (numpy.array): Satellite positions in ECEF coordinates in kilometers (shape: n x 3).
    pseudoranges_m (numpy.array): Pseudorange measurements to each satellite in meters (shape: n).
    sat_clock_biases_us (numpy.array): Satellite clock biases in microseconds (shape: n).
    initial_position_m (numpy.array): Initial guess for the receiver's position and clock bias in ECEF coordinates in meters (shape: 3).
    c (float): Speed of light in m/s.

    Returns:
    numpy.array: Estimated receiver position and clock bias [x, y, z, dt_rec] in meters and seconds respectively.
    """
    # Convert satellite positions to meters
    sat_positions_m = sat_positions_km * 1000.0
    
    # Convert satellite clock biases to seconds
    sat_clock_biases_s = sat_clock_biases_us * 1e-6

    # Correct the pseudoranges for the satellite clock biases
    corrected_pseudoranges_m = pseudoranges_m - c * sat_clock_biases_s

    # Initial guess for the receiver's position and clock bias [x, y, z, dt_rec]
    initial_guess = np.hstack((initial_position_m, 0))  # Append initial guess for receiver clock bias

    # Use least_squares to find the position and clock bias that minimize the residuals
    result = least_squares(pseudorange_residuals, initial_guess, args=(sat_positions_m, corrected_pseudoranges_m, c))

    # The solution is in result.x
    return result.x
def main():
    rinex_file = 'zimm1000.23o'
    sp3_file = 'igs22571.sp3'
    epoch = '2023-04-10 11:00:00'
    sv_end = 32
    frequencies = ['C1', 'C2', 'P2', 'C5']
    real_receiver_pos = np.array([4331297.3480, 567555.6390, 4633133.7280])
    results_filename = 'gnss_results.csv'
    initial_position_m = np.array([4331297.3480, 567555.6390, 4633133.7280])  # Arbitrary initial guess #4000000, 500000, 4000000
    

    # DataFrame to store the results
    results_df = pd.DataFrame(columns=['Frequency', 'Estimated_X', 'Estimated_Y', 'Estimated_Z', 'Clock_Bias', 
                                       'Position_Difference', 'GDOP', 'Num_Satellites', 'Real_X', 'Real_Y', 'Real_Z'])

    print("Type of results_df before loop:", type(results_df))  # Debugging print
    
    for frequency in frequencies:
        print(f"Calculating for frequency: {frequency}")

        # Read the compiled GNSS data for the specified frequency
        compiled_df = read_GNSS_data(rinex_file, sp3_file, sv_end, epoch, frequency)

        # Check if compiled_df is not empty
        if compiled_df.empty:
            print(f"No data available for frequency {frequency} at the specified epoch.")
            continue

        # Extract satellite positions, clock biases, and pseudoranges
        sat_positions = compiled_df[['x', 'y', 'z']].to_numpy()
        sat_clock_biases = compiled_df['clock_bias'].to_numpy()
        pseudoranges = compiled_df[frequency].to_numpy()

        # Calculate receiver position and clock bias
        position_and_clock_bias = calculate_position_clock_bias(sat_positions, pseudoranges, sat_clock_biases, initial_position_m)

        # Calculate GDOP
        geometry_matrix = compute_geometry_matrix(sat_positions, position_and_clock_bias[:3])
        gdop = calculate_gdop(geometry_matrix)

        # Calculate positional difference
        position_difference = np.linalg.norm(position_and_clock_bias[:3] - real_receiver_pos)

        # Append the results to the DataFrame
        result_row = {
            'Frequency': frequency,
            'Estimated_X': position_and_clock_bias[0],
            'Estimated_Y': position_and_clock_bias[1],
            'Estimated_Z': position_and_clock_bias[2],
            'Clock_Bias': position_and_clock_bias[3],
            'Position_Difference': position_difference,
            'GDOP': gdop,
            'Num_Satellites': len(pseudoranges),
            'Real_X': real_receiver_pos[0],
            'Real_Y': real_receiver_pos[1],
            'Real_Z': real_receiver_pos[2]
        }
        
        result_row_df = pd.DataFrame([result_row])
        results_df = pd.concat([results_df, result_row_df], ignore_index=True)

        print("Type of results_df inside loop:", type(results_df))  # Debugging print

    # Save the results to a CSV file
    results_df.to_csv(results_filename, index=False)
    print(f"Results saved to {results_filename}")

if __name__ == '__main__':
    main()