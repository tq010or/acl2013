#!/usr/bin/env python
"""
Receive and filter Streaming API dump data by geotagging restrictions
Geotagged users have at least 10 geotagged tweets and more than 50% of locations are from one city (the home city).
"""

import os
import sys
from geoloc.util import lib_grid_search, gcd_dist
import xmlrpclib
import ujson as json


data_dir = "../live"
data_files = os.listdir(data_dir)
proxy = xmlrpclib.ServerProxy("http://localhost:8999")

error_list = []
cc_list = []


def evaluate():
    fw = open("../result/eval.results", "w")
    flag = True
    counter = 0
    for df in data_files:
        counter += 1
        df = os.path.join(data_dir, df)
        jstr = open(df).read()
        res_dict = proxy.geolocate_cli(jstr, True)
        err = res_dict["error"]
        if err:
            print err
            continue
        sname = res_dict["sname"].lower()
        oconf = res_dict["oconf"]
        # here to ensure 10 geotagged tweets, and 50% hurdle
        if oconf != 2:
            continue
        pc = res_dict["pc"]
        oc = res_dict["oc"]
        plat, plon = lib_grid_search.lookup_coords(pc)
        olat, olon = lib_grid_search.lookup_coords(oc)

        error = gcd_dist.calc_dist_degree(plat, plon, olat, olon)
        error_list.append(error)
        if oc[-2:] == pc[-2:]:
            cc_list.append(True)
        text_pred = res_dict["text_pred"]
        loc_pred = res_dict["loc_pred"]
        tz_pred = res_dict["tz_pred"]
        tweet_num = len(res_dict["tweets"])
        rec = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n".format(sname, oc, pc, text_pred, loc_pred, tz_pred, error, tweet_num)
        print counter, rec,
        fw.write(rec)

    divisor = float(len(error_list))
    acc = len([error for error in error_list if error == 0.0]) / divisor
    cacc = sum(1.0 for c in cc_list if c) / divisor
    acc161 = len([error for error in error_list if error <= 161.0]) / divisor
    mean = sum(error_list) / divisor
    median = sorted(error_list)[int(divisor)/2]
    fw.write("Acc: {0}\n".format(acc))
    print "Acc: {0}\n".format(acc),
    fw.write("Acc161: {0}\n".format(acc161))
    print "Acc161: {0}\n".format(acc161),
    fw.write("AccCountry: {0}\n".format(cacc))
    print "AccCountry: {0}\n".format(cacc),
    fw.write("Median: {0}\n".format(median))
    print "Median: {0}\n".format(median),
    fw.write("Mean: {0}\n".format(mean))
    print "Mean: {0}\n".format(mean),
    fw.close()
    print "All finished"


if __name__ == "__main__":
    evaluate()
