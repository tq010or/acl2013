#! /usr/bin/env python

"""Calculate the Great Circle Distance between two points on earth

http://en.wikipedia.org/wiki/Great-circle_distance
"""


import math

earth_radius = 6372.8

def calc_dist_radian(pLat, pLon, lat, lon):
    cos_pLat = math.cos(pLat)
    sin_pLat = math.sin(pLat)
    cos_lat = math.cos(lat)
    sin_lat = math.sin(lat)
    long_diff = pLon - lon
    cos_long_diff = math.cos(long_diff)
    sin_long_diff = math.sin(long_diff)
    numerator = math.sqrt( math.pow(cos_lat * sin_long_diff, 2)+ math.pow(cos_pLat * sin_lat - sin_pLat * cos_lat * cos_long_diff, 2))
    denominator = sin_pLat*sin_lat + cos_pLat*cos_lat*cos_long_diff
    radian = math.atan2(numerator, denominator)
    return radian * earth_radius

def calc_dist_degree(pLat, pLon, lat, lon):
    pLat = degree_radian(pLat)
    pLon = degree_radian(pLon)
    lat = degree_radian(lat)
    lon = degree_radian(lon)
    return calc_dist_radian(pLat, pLon, lat, lon)

def degree_radian(degree):
    return (degree * math.pi)/180

def unit_test():
    pLat = 36.12
    pLon = -86.67
    lat = 33.94
    lon = -118.40
    #print calc_dist_degree(pLat, pLon, lat, lon)

    print calc_dist_degree(-6.4685741,106.8047473, -6.21462,106.84513) # jakarta
    print calc_dist_degree(-6.4685741,106.8047473, -6.11889,106.575) # sepatan

    print calc_dist_degree(-37.814, 144.96332, -37.56622, 143.84957) # melbourne Geelong
    #print calc_dist_degree(-26.20227, 28.04363, -26.26781, 27.85849) # melbourne Geelong

    print calc_dist_degree(55.7, 37.5, 56.34, 30.54517) # point vs. other
    print calc_dist_degree(55.7, 37.5, 55.75222, 37.61556 ) # point vs. moscow

    # melbourne vs. st. kilda
    print calc_dist_degree(-37.8676, 144.98099, -37.814, 144.96332) # point vs. other
    # ballarat vs. melb
    print calc_dist_degree(-37.56622, 143.84957, -37.814, 144.96332) # point vs. other
    # geelong vs. melb
    print calc_dist_degree(-38.14711, 144.36069 , -37.814, 144.96332) # point vs. other
    # hobart launceston
    print calc_dist_degree(-41.43876, 147.13467, -42.87936, 147.32941)# point vs. other

    # 
    print calc_dist_degree(42.35843, -71.05977, 42.63342, -71.31617)# point vs. other
    print calc_dist_degree(43.90012, -78.84957,43.70011, -79.4163 )# point vs. other
    
if __name__ == "__main__":
    unit_test()
