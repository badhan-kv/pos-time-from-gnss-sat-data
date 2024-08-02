import numpy as np

def calculate_elevation_angle(rx_x, rx_y, rx_z, sat_x, sat_y, sat_z):
    """
    Calculate the elevation angle from the receiver to the satellite.

    :param rx_x: Receiver's X coordinate in ECEF (meters)
    :param rx_y: Receiver's Y coordinate in ECEF (meters)
    :param rx_z: Receiver's Z coordinate in ECEF (meters)
    :param sat_x: Satellite's X coordinate in ECEF (meters)
    :param sat_y: Satellite's Y coordinate in ECEF (meters)
    :param sat_z: Satellite's Z coordinate in ECEF (meters)
    :return: Elevation angle in degrees
    """

    # Vector from receiver to satellite
    vec_r_to_s = np.array([sat_x - rx_x, sat_y - rx_y, sat_z - rx_z])

    # Normalize this vector
    unit_vec_r_to_s = vec_r_to_s / np.linalg.norm(vec_r_to_s)

    # Calculate the receiver's up vector
    # Assuming the receiver is located on the Earth's surface
    receiver_position = np.array([rx_x, rx_y, rx_z])
    unit_up_vector = receiver_position / np.linalg.norm(receiver_position)

    # Calculate the dot product between the up vector and the receiver-to-satellite vector
    dot_product = np.dot(unit_vec_r_to_s, unit_up_vector)

    # Calculate the elevation angle
    elevation_rad = np.arcsin(dot_product)
    elevation_deg = np.degrees(elevation_rad)

    return elevation_deg

def calculate_azimuth(rx_x, rx_y, rx_z, sat_x, sat_y, sat_z):
    """
    Calculate the azimuth angle from the receiver to the satellite in degrees.

    :param rx_x, rx_y, rx_z: Receiver's X, Y, Z coordinates in ECEF (meters).
    :param sat_x, sat_y, sat_z: Satellite's X, Y, Z coordinates in ECEF (meters).
    :return: Azimuth angle in degrees.
    """
    # Vector from receiver to satellite
    vec_r_to_s = np.array([sat_x - rx_x, sat_y - rx_y, sat_z - rx_z])

    # Normalize this vector
    unit_vec_r_to_s = vec_r_to_s / np.linalg.norm(vec_r_to_s)

    # East and North unit vectors at receiver's location
    east = np.array([-rx_y, rx_x, 0])  # East vector is perpendicular to the north and up vectors
    north = np.cross([0, 0, 1], east)  # North vector is cross product of up vector (0,0,1) and east vector

    # Normalize East and North vectors
    unit_east = east / np.linalg.norm(east)
    unit_north = north / np.linalg.norm(north)

    # Calculate azimuth
    azimuth_rad = np.arctan2(np.dot(unit_vec_r_to_s, unit_east), np.dot(unit_vec_r_to_s, unit_north))

    # Convert to degrees and ensure the angle is positive
    azimuth_deg = np.degrees(azimuth_rad)
    if azimuth_deg < 0:
        azimuth_deg += 360

    return azimuth_deg


def main():
    # Example usage
    rx_x, rx_y, rx_z = 4032241.29, 306056.35, 4919033.44  # Receiver's ECEF coordinates
    sat_x, sat_y, sat_z = 10637829.38, 21796193.97, -2077329.02  # Satellite's ECEF coordinates

    elevation_angle = calculate_elevation_angle(rx_x, rx_y, rx_z, sat_x, sat_y, sat_z)
    azimuth_angle = calculate_azimuth(rx_x, rx_y, rx_z, sat_x, sat_y, sat_z)
    print("Elevation Angle:", elevation_angle)
    print("Azimth Angle:", azimuth_angle)

if __name__ == '__main__':
    main()
