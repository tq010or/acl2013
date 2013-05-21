#! /usr/bin/env python

"""
Map a pair of coordinates to a unique city, or return None if no valid city is found
"""


import sys
import itertools
import gcd_dist
import math
import ujson as json
import os


grid_size = 0.5 #measured by degree
pkg_path = os.environ["geoloc"]

def load_city_info():
    """    Get city information    """
    city_info = dict()
    counter = 0
    for l in open("{0}/data/city_collapsed_all".format(pkg_path)):
        name, tz, lat, lon, population = l.rstrip().lower().split('\t') 
        city_info[name] = (float(lat), float(lon), counter)
        counter += 1
    return city_info

def round_prec(num):
    """    round coordinates to appropriate grid size    """
    fraction, integer = math.modf(num)
    if fraction >= 0.5:
        fraction = 0.5
    else:
        fraction = 0
    return integer + fraction

def build_city_grids(city_info_dict):
    """    map cities into grid_size specified cells    """
    city_grids = dict()
    for city_name in city_info_dict:
        lat, lon, counter = city_info_dict[city_name]
        key = "{0},{1}".format(round_prec(lat), round_prec(lon))
        rec = (city_name, lat, lon)
        try:
            city_grids[key].append(rec)
        except KeyError:
            city_grids[key] = [rec]
    #print "city grid number is :{0}".format(len(city_grids))
    return city_grids
    
def zoom_search(lat, lon):
    """    search the nearest city by lat and lon    """
    # generate search areas, nine blocks search
    grid_lat = round_prec(lat)
    lats = [grid_lat - grid_size, grid_lat, grid_lat + grid_size]
    grid_lon = round_prec(lon)
    lons = [grid_lon - grid_size, grid_lon, grid_lon + grid_size]
    keys = itertools.product(lats, lons)

    # find the most suitable key
    results = []
    for key in keys:
        klat, klon = key
        city_key = "{0},{1}".format(klat, klon)
        try:
            city_list = city_grids[city_key]
        except KeyError:
            continue 
        for city in city_list:
            name, clat, clon = city
            gcd_error_distance = gcd_dist.calc_dist_degree(clat, clon, lat, lon)
            results.append((name, gcd_error_distance))
    if len(results) > 0:
        sorted_results = sorted(results, key = lambda k:k[1])
        return sorted_results[0]
    else:
        return (None, None)

def lookup_city(lat, lon):
    city, offset_distance = zoom_search(lat, lon)
    if city:
        return city
    else:
        return None

def lookup_coords(city):
    if city in city_info:
        lat, lon = city_info[city][:2]
        return lat, lon
    else:
        return None
    
city_info = load_city_info()
city_grids = build_city_grids(city_info)

if __name__ == "__main__":
    print zoom_search(44.86503177,-85.51900375)
    print zoom_search(54.64403, -2.69027)
    print zoom_search(53.76667, -2.71667)
    print gcd_dist.calc_dist_degree(54.64403, -2.69027, 53.76667, -2.71667)
    print zoom_search(4.77742, 7.0134)
