#!/usr/bin/env
"""
convert L0 adapter
"""


import os
pkg_path = os.environ["geoloc"]


def obtain_feature_map():
    index = 1
    city2fea_dict = dict()
    fea2city_dict = dict()
    for l in open("{0}/data/city_collapsed_all".format(pkg_path)):
        segs = l.rstrip().split("\t")
        city = segs[0]
        city2fea_dict[city] = index
        fea2city_dict[index] = city
        index += 1
    return city2fea_dict, fea2city_dict


def obtain_abbr_to_fullname():
    abbr_dict = dict()
    for l in open("{0}/data/country_abbr".format(pkg_path)):
        segs = l.rstrip().split("\t")
        abbr_dict[segs[0].lower()] = segs[1]
    return abbr_dict


city2fea_dict, fea2city_dict = obtain_feature_map()
abbr_dict = obtain_abbr_to_fullname()


def convert_readable(city):
    tokens = city.split('-')
    readable_city = []
    for word in tokens[0].split(' '):
        readable_city.append(word[0].upper() + word[1:])
    readable_city = " ".join(readable_city) + ", " + abbr_dict[tokens[2].lower()]
    return readable_city

def get_id_by_city(city):
    return city2fea_dict[city]

def get_city_by_id(fea_id):
    return fea2city_dict[fea_id]

def get_feature_number():
    return len(city2fea_dict)


if __name__ == "__main__":
    pass
