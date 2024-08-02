import numpy as np
from xyz_lla import lla2xyz, diff_org

def xyz2neu(x, y, z, lat_ref, lon_ref, alt_ref):
    # Use the imported lla2xyz function
    x_ref, y_ref, z_ref = lla2xyz(lat_ref, lon_ref, alt_ref)

    # Compute the differences
    dx = x - x_ref
    dy = y - y_ref
    dz = z - z_ref

    # Rotation matrix
    lat_ref_rad = np.radians(lat_ref)
    lon_ref_rad = np.radians(lon_ref)
    R = np.array([[-np.sin(lon_ref_rad), np.cos(lon_ref_rad), 0],
                  [-np.sin(lat_ref_rad)*np.cos(lon_ref_rad), -np.sin(lat_ref_rad)*np.sin(lon_ref_rad), np.cos(lat_ref_rad)],
                  [np.cos(lat_ref_rad)*np.cos(lon_ref_rad), np.cos(lat_ref_rad)*np.sin(lon_ref_rad), np.sin(lat_ref_rad)]])

    # Compute NEU
    neu = R @ np.array([dx, dy, dz])
    return neu[0], neu[1], neu[2]

def neu2xyz(n, e, u, lat_ref, lon_ref, alt_ref):
    # Use the imported lla2xyz function
    x_ref, y_ref, z_ref = lla2xyz(lat_ref, lon_ref, alt_ref)

    # Inverse rotation matrix
    lat_ref_rad = np.radians(lat_ref)
    lon_ref_rad = np.radians(lon_ref)
    R_inv = np.array([[-np.sin(lon_ref_rad), -np.sin(lat_ref_rad)*np.cos(lon_ref_rad), np.cos(lat_ref_rad)*np.cos(lon_ref_rad)],
                      [np.cos(lon_ref_rad), -np.sin(lat_ref_rad)*np.sin(lon_ref_rad), np.cos(lat_ref_rad)*np.sin(lon_ref_rad)],
                      [0, np.cos(lat_ref_rad), np.sin(lat_ref_rad)]])

    # Convert NEU to ECEF differences
    dxyz = R_inv @ np.array([n, e, u])

    # Add differences to reference ECEF coordinates
    x = x_ref + dxyz[0]
    y = y_ref + dxyz[1]
    z = z_ref + dxyz[2]

    return x, y, z


if __name__ == "__main__":
    # Example usage
    x, y, z = 4117028.194835351, 442342.3779282228, 4835436.473811239
    lat_ref, lon_ref, alt_ref = 49.62678219068248, 6.159455465069763, 338.4
    
    north, east, up = xyz2neu(x, y, z, lat_ref, lon_ref, alt_ref)
    print("north= ", north, "east= ", east, "up= ", up)
    
    x_1, y_1, z_1 = neu2xyz(north, east, up, lat_ref, lon_ref, alt_ref)
    print("x= ", x_1, "y= ", y_1, "z= ", z_1)
    
    diff_x, diff_y, diff_z = diff_org(x, y, z, x_1, y_1, z_1)
    print("diff_x= ", diff_x, "diff_y= ", diff_y, "diff_z= ", diff_z)