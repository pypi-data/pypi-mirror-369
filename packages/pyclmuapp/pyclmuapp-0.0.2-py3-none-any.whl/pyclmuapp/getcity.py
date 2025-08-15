from haversine import haversine
import math

# https://github.com/zhonghua-zheng/UrbanClimateExplorer

def haversine_dist(a, b):
    """This is a function for getting the haversine distance

    Parameters
    ----------
    a: list 
        [lat, lon]
        e.g., (45.7597, 4.8422)
    b: list 
        [lat, lon]
        e.g., (48.8567, 2.3508)
    er: 
        Earth radius, default is 6371.0088 km

    Returns
    -------
    haversine_dist
        the haversine distance between a and b
    """
    a_n = (a[0], ((a[1] + 180) % 360) - 180)
    b_n = (b[0], ((b[1] + 180) % 360) - 180)
    return haversine(a_n, b_n)

def get_mask_cities(df_mask):
    """This is a function for getting urban mask and a list of cities' lat and lon

    Parameters
    ----------
    mask : xarray.DataArray
        urban mask

    Returns
    -------
    dict
        a dict of cities' lat and lon
    """
    
    # get mask dataframe
    #df_mask = mask.to_dataframe().reset_index() 
    df_mask = df_mask[df_mask["mask"]==True].reset_index(drop=True)[["lat","lon"]] # get available cities
    CitiesList = list(df_mask.transpose().to_dict().values()) # get a list of city lat/lon
    return CitiesList

def closest(data, v):
    """find the nearest urban grid cell in CESM using haversine distance
    reference: https://stackoverflow.com/questions/41336756/find-the-closest-latitude-and-longitude

    Parameters
    ----------
    data : dict
        a dict of cities' lat and lon, from get_mask_cities
    v : dict
        a dict of a city's lat and lon that we are interested in, e.g., {'lat': 40.1164, 'lon': -88.2434}

    Returns
    -------
    dict
        lat and lon of the nearest grid cell in Earth System Model
    """

    # find the nearest urban grid cell in CESM using haversine distance
    return min(data, key=lambda p: haversine_dist([v['lat'],v['lon']],[p['lat'],p['lon']]))




def adjust_longitude(longitude):
    while longitude < -180:
        longitude += 360
    while longitude > 180:
        longitude -= 360
    return longitude

def calculate_polygon_area(latitude_longitude_coords):
    adjusted_coords = [(lat, adjust_longitude(lon)) for lat, lon in latitude_longitude_coords]
    coords_rad = [(math.radians(lat), math.radians(lon)) for lat, lon in adjusted_coords]
    area = 0
    for i in range(len(coords_rad)):
        j = (i + 1) % len(coords_rad)
        area += (coords_rad[j][1] - coords_rad[i][1]) * (2 + math.sin(coords_rad[i][0]) + math.sin(coords_rad[j][0]))

    area = area / 2.0

    return abs(area)