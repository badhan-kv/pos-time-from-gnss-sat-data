import numpy as np
from elevation_angle import calculate_elevation_angle
from xyz_lla import xyz2lla

def calculate_tropospheric_delay(receiver_pos_ecef, satellite_pos_ecef, temperature=20, pressure=1013.25, humidity=50):
    """
    Calculate tropospheric delay using the Saastamoinen model.

    :param receiver_pos_ecef: Receiver's position in ECEF coordinates.
    :param satellite_pos_ecef: Satellite's position in ECEF coordinates.
    :param temperature: Temperature in Celsius at the receiver's location.
    :param pressure: Atmospheric pressure in millibars at the receiver's location.
    :param humidity: Relative humidity in percent at the receiver's location.
    :return: Tropospheric delay in meters.
    """

    # Convert the receiver's ECEF position to LLA
    latitude, longitude, altitude = xyz2lla(*receiver_pos_ecef)

    # Calculate the elevation angle
    elevation_angle_deg = calculate_elevation_angle(*receiver_pos_ecef, *satellite_pos_ecef)
    elevation_angle_rad = np.radians(elevation_angle_deg)

    # Saastamoinen model
    zenith_delay = 2.312 / (pressure - 0.0001 * humidity * np.exp(-0.0346 * (pressure / (temperature + 273.15))))
    mapping_function = 1.0 / np.cos(elevation_angle_rad)  # Simplified mapping function

    tropospheric_delay = zenith_delay * mapping_function
    return tropospheric_delay

# Example usage
def main():
    receiver_pos_ecef = [4032241.29, 306056.35, 4919033.44]  # Example receiver's ECEF coordinates
    satellite_pos_ecef = [10637829.38, 21796193.97, -2077329.02]  # Example satellite's ECEF coordinates
    temperature = 20  # Example temperature in Celsius
    pressure = 1013.25  # Example atmospheric pressure in millibars
    humidity = 50  # Example relative humidity in percent

    tropospheric_delay = calculate_tropospheric_delay(receiver_pos_ecef, satellite_pos_ecef, temperature, pressure, humidity)
    print(f"Tropospheric Delay: {tropospheric_delay} meters")

if __name__ == "__main__":
    main()