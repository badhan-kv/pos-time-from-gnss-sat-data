import numpy as np
from scipy.optimize import least_squares
import georinex as gr
import pandas as pd
from data_reading import read_GNSS_data, find_satellite_clock_correction
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='georinex')
from datetime import datetime, timedelta
from tropospheric_delay import calculate_tropospheric_delay
from ionospheric_delay import calculate_ionospheric_delay
from Weather_data import get_weather_data  # Assuming you have a function to fetch weather data
from elevation_angle import calculate_elevation_angle, calculate_azimuth
from xyz_lla import xyz2lla
from xyz_neu import xyz2neu

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

def calculate_pdop(G):
    Q = np.linalg.inv(G.T @ G)  # Inverse of G'G
    pdop = np.sqrt(np.trace(Q[:3, :3]))  # Square root of the trace of the top-left 3x3 submatrix of Q
    return pdop

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
    nav_file = 'zimm1000.23n'
    start_epoch = datetime(2023, 4, 10)
    end_epoch = datetime(2023, 4, 11)
    interval = timedelta(minutes=15)
    frequency = 'C2'
    api_key = 'YBCMMAGSU8YPFWHQBUU2PAAAL'  # Replace with your actual API key for weather data
    results_filename = 'gnss_results_full_day.csv'
    c = 299792458  # Speed of light in m/s
    real_receiver_pos = np.array([4331297.3480, 567555.6390, 4633133.7280])  # Replace with the real receiver position

    alpha_coeffs = [0.2608e-07, 0.1490e-07, -0.1192e-06, -0.5960e-07] #from navigation file
    beta_coeffs = [0.1290e+06, 0.1638e+05, -0.2621e+06, 0.3277e+06] #from navigation file

    results = []

    current_epoch = start_epoch
    while current_epoch < end_epoch:
        compiled_df = read_GNSS_data(rinex_file, sp3_file, 32, current_epoch.strftime('%Y-%m-%d %H:%M:%S'), frequency)

        if not compiled_df.empty:
            sat_positions = compiled_df[['x', 'y', 'z']].to_numpy()
            pseudoranges = compiled_df[frequency].to_numpy()
            corrected_pseudoranges = np.zeros_like(pseudoranges)

            for i, satellite in enumerate(compiled_df['sv']):
                try:
                    actual_epoch, SVclockBias, SVclockDrift, SVclockDriftRate = find_satellite_clock_correction(nav_file, satellite, current_epoch.strftime('%Y-%m-%d %H:%M:%S'))
                    time_difference = (current_epoch - actual_epoch).total_seconds()
                    total_clock_bias = SVclockBias + SVclockDrift * time_difference + SVclockDriftRate * time_difference ** 2
                    corrected_pseudoranges[i] = pseudoranges[i] - total_clock_bias * c
                except ValueError:
                    corrected_pseudoranges[i] = np.nan

            valid_indices = ~np.isnan(corrected_pseudoranges)
            valid_sat_positions = sat_positions[valid_indices]
            valid_pseudoranges = corrected_pseudoranges[valid_indices]

            if valid_sat_positions.size > 0:
                # Initial position calculation
                initial_position_m = [0, 0, 0]  # Initial guess for receiver's position
                position_and_clock_bias = calculate_position_clock_bias(valid_sat_positions, valid_pseudoranges, np.zeros(len(valid_pseudoranges)), initial_position_m)

                receiver_pos_ecef = position_and_clock_bias[:3]
                latitude, longitude, _ = xyz2lla(*receiver_pos_ecef)
                coarse_position_difference = np.linalg.norm(position_and_clock_bias[:3] - real_receiver_pos)

                # Correct pseudoranges for tropospheric and ionospheric delays
                for i, satellite_pos_ecef in enumerate(valid_sat_positions):
                    elevation = calculate_elevation_angle(*receiver_pos_ecef, *satellite_pos_ecef)
                    azimuth = calculate_azimuth(*receiver_pos_ecef, *satellite_pos_ecef)
                    
                    # Fetch weather data for tropospheric delay calculation
                    weather_data = get_weather_data(api_key, latitude, longitude, current_epoch.strftime('%Y-%m-%dT%H:%M:%S'))
                    temperature = weather_data['temperature']
                    pressure = weather_data['pressure']
                    humidity = weather_data['humidity']

                    # Calculate tropospheric delay
                    tropo_delay = calculate_tropospheric_delay(receiver_pos_ecef, satellite_pos_ecef, temperature, pressure, humidity)

                    # Calculate ionospheric delay
                    iono_delay = calculate_ionospheric_delay(latitude, longitude, elevation, azimuth, current_epoch.strftime('%Y-%m-%d %H:%M:%S'), alpha_coeffs, beta_coeffs)
                    iono_delay_meters = iono_delay * c  # Convert ionospheric delay from seconds to meters


                    # Correct the pseudoranges using the calculated delays
                    valid_pseudoranges[i] -= (tropo_delay + iono_delay_meters)

                # Recalculate the receiver's position with the refined pseudoranges
                refined_position_and_clock_bias = calculate_position_clock_bias(valid_sat_positions, valid_pseudoranges, np.zeros(len(valid_pseudoranges)), receiver_pos_ecef)
                refined_position_difference = np.linalg.norm(refined_position_and_clock_bias[:3] - real_receiver_pos)
                
                #refined xyz
                refined_receiver_pos_ecef = refined_position_and_clock_bias[:3]
                latitude, longitude = 0, 0
                
                north, east, up = xyz2neu(receiver_pos_ecef[0], receiver_pos_ecef[1], receiver_pos_ecef[2], latitude, longitude, 0)
                
                geometry_matrix = compute_geometry_matrix(sat_positions, position_and_clock_bias[:3])
                pdop = calculate_pdop(geometry_matrix)
                

                results.append({
                    'epoch': current_epoch,
                    'coarse_x': position_and_clock_bias[0],
                    'coarse_y': position_and_clock_bias[1],
                    'coarse_z': position_and_clock_bias[2],
                    'Coarse_Position_Difference': coarse_position_difference,
                    'refined_x': refined_position_and_clock_bias[0],
                    'refined_y': refined_position_and_clock_bias[1],
                    'refined_z': refined_position_and_clock_bias[2],
                    'Refined_Position_Difference': refined_position_difference,
                    'North_Component': north,
                    'East_Component': east,
                    'Up_Component': up,
                    'pdop': pdop,
                    'Num_Satellites': len(valid_sat_positions)
                })

        current_epoch += interval

    results_df = pd.DataFrame(results)
    results_df.to_csv(results_filename, index=False)
    print(f"Results saved to {results_filename}")

if __name__ == '__main__':
    main()