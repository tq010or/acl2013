#!/usr/bin/env python
"""
LR-stacking module for geolocation prediction
"""


import os
pkg_path = os.environ["geoloc"]
import ujson as json
import xmlrpclib
from geoloc.adapters import twitter_adapter, feature_adapter, city_adapter
from geoloc.util import lib_grid_search, gcd_dist, lib_log
import liblinearutil


fea_num = city_adapter.get_feature_number()
#NOTE: Only text, loc, tz models are adopted, as they achieve comparable performance, but consumes much less memory than using the full model.
text_decoder = xmlrpclib.ServerProxy("http://localhost:9001")
loc_decoder = xmlrpclib.ServerProxy("http://localhost:9002")
tz_decoder = xmlrpclib.ServerProxy("http://localhost:9003")
#desc_decoder = xmlrpclib.ServerProxy("http://localhost:9004")
#rname_decoder = xmlrpclib.ServerProxy("http://localhost:9005")
stacked_model = liblinearutil.load_model('{0}/models/world.l1.train.model.text_loc_tz'.format(pkg_path))
#stacked_model = liblinearutil.load_model('{0}/models/world.l1.train.model.text_loc_tz_desc_rname'.format(pkg_path))
print "Geolocation models loaded"


def seek_cache(sname):
    """    Seek on disk cache (predicted GT-JSON)    """
    jobj = None
    try:
        assert(sname)
        cache_file = "{0}/cache/{1}".format(pkg_path, sname)
        jstr = open(cache_file).readline()
        jobj = json.loads(jstr.rstrip())
    except (AssertionError, IOError, ValueError):
        return None
    return jobj


def parse_input(data):
    """    Parse input string    """
    err_msg = None
    try:
        assert(isinstance(data, basestring))
        data = json.loads(data.strip()) 
    except AssertionError:
        err_msg = "Invalid input data format"
        #err_msg = "Invalid input data format: {0}".format(data)
        return (None, err_msg)
    except ValueError:
        try:
            assert(len(data) <= 15) # maiximum twitter screen name length
        except AssertionError:
            err_msg = "User screen name exceeds 15 characters"
            #err_msg = "User screen name exceeds 15 characters {0}".format(data)
            return (None, err_msg)
        else:
            return (data, err_msg) # return screen name
    else:
        gt_dict, err_msg = twitter_adapter.parse_user_timeline(data) # return parsed user timeline data
        if err_msg:
            #err_msg = "{0} {1}".format(err_msg, data)
            return (None, err_msg)
        return (gt_dict, err_msg)


def geolocate(data, enable_cache = True):
    """
    Input:
        1. user screen name
        2. user timeline JSON data (assuming the same user name)
    Ouptut:
        GT-dict
    Supported Options: caching;
    """
    # identify input format
    sname = None #user screen name
    gt_dict = None #JSON format result
    err_msg = None
    parsed_data, err_msg = parse_input(data)

    if isinstance(parsed_data, basestring):
        sname = parsed_data
    elif isinstance(parsed_data, dict):
        gt_dict = parsed_data
        sname = parsed_data["sname"]
    else:
        gt_dict = {"error":err_msg}
        err_msg = "{0} {1}".format(err_msg, data)
        lib_log.error(err_msg)
        return gt_dict
    
    sname = sname.lower()
    print "Predict:", sname

    # using cache?
    if enable_cache:
        cached = seek_cache(sname) 
        if cached:
            return cached

    # crawl data if input is user name
    if not gt_dict:
        gt_dict, err_msg = twitter_adapter.parse_user_timeline(sname)
        if err_msg:
            gt_dict = {"error":err_msg}
            err_msg = "{0} {1}".format(err_msg, sname)
            lib_log.error(err_msg)
            return gt_dict
    

    # sequential classifier
    text_pred = text_decoder.predict(feature_adapter.extract_text_features(gt_dict["tweets"]))
    loc_pred = loc_decoder.predict(feature_adapter.extract_ngram_features(gt_dict["loc"]))
    tz_pred = tz_decoder.predict(feature_adapter.extract_ngram_features(gt_dict["tz"]))
    #desc_pred = desc_decoder.predict(feature_adapter.extract_ngram_features(gt_dict["desc"]))
    #rname_pred = rname_decoder.predict(feature_adapter.extract_ngram_features(gt_dict["rname"]))
    print "L0 predictions:", text_pred, loc_pred, tz_pred
    #print text_pred, loc_pred, tz_pred, desc_pred, rname_pred

    text_id = city_adapter.get_id_by_city(text_pred) + fea_num * 0
    loc_id = city_adapter.get_id_by_city(loc_pred) + fea_num * 1
    tz_id = city_adapter.get_id_by_city(tz_pred) + fea_num * 2
    #desc_id = city_adapter.get_id_by_city(desc_pred) + fea_num * 3
    #rname_id = city_adapter.get_id_by_city(rname_pred) + fea_num * 4
    #libsvm_rec = "{0}:1 {1}:1 {2}:1\n".format(text_id, loc_id, tz_id)
    #libsvm_rec = "{0}:1 {1}:1 {2}:1 {3}:1 {4}:1\n".format(text_id, loc_id, tz_id, desc_id, rname_id)
    #print libsvm_rec
    fea_vec_liblinear = [{text_id:1, loc_id:1, tz_id:1}]
    #fea_vec_liblinear = [{text_id:1, loc_id:1, tz_id:1, desc_id:1, rname_id:1}]
    print "L1 data:", fea_vec_liblinear 
    p_label, p_acc, p_val = liblinearutil.predict([1], fea_vec_liblinear, stacked_model)
    slr_id = int(p_label[0]) # stacked logistic regression prediction label
    slr_pred = city_adapter.get_city_by_id(slr_id)
    print "L1 prediction:", slr_pred
    gt_dict["pc"] = slr_pred
    slr_lat, slr_lon = lib_grid_search.lookup_coords(slr_pred)
    print "L1 prediction coordinates:", slr_lat, slr_lon
    gt_dict["plat"] = slr_lat
    gt_dict["plon"] = slr_lon
    gt_dict["errdist"] = int(gcd_dist.calc_dist_degree(slr_lat, slr_lon, gt_dict["olat"], gt_dict["olon"])) if gt_dict["oc"] else None
    assert(not err_msg)
    gt_dict["error"] = err_msg
    gt_dict["text_pred"] = text_pred
    gt_dict["loc_pred"] = loc_pred
    gt_dict["tz_pred"] = tz_pred
    
    if enable_cache:
        open("{0}/cache/{1}".format(pkg_path, sname), "w").write("{0}\n".format(json.dumps(gt_dict)))

    return gt_dict


if __name__ == "__main__":
    geolocate("brooklynhan")
