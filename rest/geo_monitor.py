#!/usr/bin/env python 
"""
Monitor live geo stream in Twitter streaming API;
Geolocate users and save results;
"""

import os
pkg_path = os.environ["geoloc"]
import ujson as json
from time import gmtime, strftime
from geoloc.adapters import geo_stream_dispatcher
import geotagger

CACHED_USERS = 100
cache_dir = "./log"

def main():
    print "Begin monitoring"
    while True:
        cache_data = geo_stream_dispatcher.get_sname_list(CACHED_USERS)
        for sname in cache_data:
            result_dict = geotagger.predict_by_user(sname)

            #TODO: shall we save them to other places for further analysis?
            # skip users far from metro cities
            if "oc" not in result_dict:
                continue
            # skip users without coherent ground truth locations
            if result_dict["oconf"] == 2:
                continue

            cur_ts = strftime("%Y%m%d%H", gmtime())
            cur_folder = os.path.join(cache_dir, cur_ts)
            if not os.path.exists(cur_folder):
                os.makedirs(cur_folder)
            json.dump(result_dict, open("{0}/{1}.json".format(cur_folder, sname), "w"))
            print "{0} is saved!".format(sname)


if __name__ == "__main__":
    main()


