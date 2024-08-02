import math
import numpy as np
import datetime

def calculate_ionospheric_delay(lat, lon, elevation, azimuth, epoch, alpha_coeffs, beta_coeffs):
    """
    Calculate the ionospheric delay using the Klobuchar model.

    :param lat: Receiver's latitude in degrees (positive for north, negative for south).
    :param lon: Receiver's longitude in degrees (positive for east, negative for west).
    :param elevation: Satellite elevation in degrees.
    :param azimuth: Satellite azimuth in degrees.
    :param gps_time: GPS time of day in seconds.
    :param alpha_coeffs: List of four alpha coefficients from the GPS navigation file.
    :param beta_coeffs: List of four beta coefficients from the GPS navigation file.
    :return: Ionospheric delay in seconds.
    """
    
    epoch_dt = datetime.datetime.strptime(epoch, '%Y-%m-%d %H:%M:%S')
    gps_time = (epoch_dt - epoch_dt.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

    # Convert angles to radians
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    elevation_rad = np.radians(elevation)
    azimuth_rad = np.radians(azimuth)

    # Earth-centered angle (semi-circle)
    psi = 0.0137 / (elevation_rad / np.pi + 0.11) - 0.022

    # Subionospheric lat/lon
    sub_lat = lat_rad / np.pi + psi * np.cos(azimuth_rad)
    if sub_lat > 0.416:
        sub_lat = 0.416
    elif sub_lat < -0.416:
        sub_lat = -0.416

    sub_lon = lon_rad / np.pi + psi * np.sin(azimuth_rad) / np.cos(sub_lat * np.pi)

    # Geomagnetic latitude (semi-circle)
    geomag_lat = sub_lat + 0.064 * np.cos((sub_lon - 1.617) * np.pi)

    # Local time (semi-circle)
    local_time = 43200 * sub_lon + gps_time
    local_time = local_time % 86400

    # Amplitude and phase of the model
    amp = alpha_coeffs[0] + alpha_coeffs[1]*geomag_lat + alpha_coeffs[2]*(geomag_lat**2) + alpha_coeffs[3]*(geomag_lat**3)
    if amp < 0:
        amp = 0

    per = beta_coeffs[0] + beta_coeffs[1]*geomag_lat + beta_coeffs[2]*(geomag_lat**2) + beta_coeffs[3]*(geomag_lat**3)
    if per < 72000:
        per = 72000

    # Phase calculation
    x = 2 * np.pi * (local_time - 50400) / per

    # Ionospheric delay
    if abs(x) < 1.57:
        delay = 5E-9 + amp * (1 - x**2 / 2 + x**4 / 24)
    else:
        delay = 5E-9

    delay = delay * (np.pi / 2) / np.sin(elevation_rad)

    return delay

# Example usage
def main():
    alpha_coeffs = [0.2608e-07, 0.1490e-07, -0.1192e-06, -0.5960e-07]  # Replace with your alpha coefficients
    beta_coeffs = [0.1290e+06, 0.1638e+05, -0.2621e+06, 0.3277e+06]  # Replace with your beta coefficients
    lat, lon = 49.6, 6.1  # Example latitude and longitude in degrees
    elevation, azimuth = 30, 180  # Example elevation and azimuth in degrees
    epoch = '2023-04-10 13:15:00'

    ionospheric_delay = calculate_ionospheric_delay(lat, lon, elevation, azimuth, epoch, alpha_coeffs, beta_coeffs)
    print(f"Ionospheric Delay: {ionospheric_delay} seconds")
    

if __name__ == '__main__':
    main()