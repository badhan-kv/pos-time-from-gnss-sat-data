#Code to convert ECEF to LLA and LLA to ECEF with WGS84 ellipsoid

import numpy as np

a = 6378137.0  # semi-major axis in meters
e = 8.1819190842622e-2  # first eccentricity

def xyz2lla(x, y, z):
    # Constants
    a = 6378137.0  # semi-major axis
    e = 8.1819190842622e-2  # first eccentricity

    # Longitude
    lon = np.arctan2(y, x)

    # Preliminary latitude
    p = np.sqrt(x**2 + y**2)
    lat = np.arctan2(z, p * (1 - e**2))

    # Iterative process to compute latitude and altitude
    for _ in range(5):  # Usually converges in a few iterations
        N = a / np.sqrt(1 - e**2 * np.sin(lat)**2)
        alt = p / np.cos(lat) - N
        lat = np.arctan2(z, p * (1 - e**2 * N / (N + alt)))

    # Convert latitude and longitude to degrees
    lat = np.degrees(lat)
    lon = np.degrees(lon)

    # Normalize latitude
    # Latitude values exceeding 90 degrees are wrapped around, preserving the sign
    lat = np.where(lat > 90, 180 - lat, lat)
    lat = np.where(lat < -90, -180 - lat, lat)
    
    # Normalize longitude to be within -180 to 180 degrees
    lon = (lon + 180) % 360 - 180

    return lat, lon, alt

def lla2xyz(lat, lon, alt):
    # Convert lat and lon to radians
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    # Equations for ECEF conversion
    N = a / np.sqrt(1 - e**2 * np.sin(lat_rad)**2)
    x = (N + alt) * np.cos(lat_rad) * np.cos(lon_rad)
    y = (N + alt) * np.cos(lat_rad) * np.sin(lon_rad)
    z = ((1 - e**2) * N + alt) * np.sin(lat_rad)

    return x, y, z


def diff_org (original_1, original_2, original_3, converted_1, converted_2, converted_3): #function to calculate difference from original
    dif_1 = original_1 - converted_1
    dif_2 = original_2 - converted_2
    dif_3 = original_3 - converted_3
    
    return dif_1, dif_2, dif_3

if __name__ == "__main__":
    #LLA to ECEF example
    lat, lon, alt = 49.61563086184349, 6.13245686027482, 311.5 #location my bouldering gym in Luxembourg in degrees, degrees and meters in ellipsoidal
    x, y, z = lla2xyz(lat, lon, alt)
    print("x= ", x, "y= ", y, "z= ", z) #output in meters
    
    #ECEF to lla example
    lat_1, lon_1, alt_1 = xyz2lla(x, y, z)
    print("lat_1= ", lat_1, "lon_1= ", lon_1, "alt_1= ", alt_1)
    
    #Difference between converted and orginal
    diff_lat, diff_lon, diff_alt = diff_org(lat, lon, alt, lat_1, lon_1, alt_1)
    print("diff_lat= ", diff_lat, "diff_lon= ", diff_lon, "diff_alt= ", diff_alt)
    