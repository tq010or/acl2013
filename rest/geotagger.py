#!/usr/bin/env python
"""
Geolocation Prediction service
"""

import os
pkg_path = os.environ["geoloc"]
import ujson as json
from geoloc.adapters import twitter_adapter, feature_adapter, city_adapter
from geoloc.util import lib_grid_search, gcd_dist, lib_log
from geoloc.classifiers import liblinearutil, mbayes_decoder

print "Loading text model ..."
text_decoder = mbayes_decoder.decoder("{0}/models/world.text.train.model".format(pkg_path))
print "Loading loc model ..."
loc_decoder = mbayes_decoder.decoder("{0}/models/world.loc.train.model".format(pkg_path))
print "Loading tz model ..."
tz_decoder = mbayes_decoder.decoder("{0}/models/world.tz.train.model".format(pkg_path))
print "Loading stacking model ..."
stacked_model = liblinearutil.load_model('{0}/models/world.l1.train.model.text_loc_tz'.format(pkg_path))
print "All models loaded"

fea_num = city_adapter.get_feature_number()

def parse_input(data):
    """    Parse input string    """
    err_msg = None
    try:
        assert(isinstance(data, basestring))
        data = json.loads(data.strip()) 
    except AssertionError:
        err_msg = "Invalid input data format"
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

    # crawl data if input is user name
    if not gt_dict:
        gt_dict, err_msg = twitter_adapter.parse_user_timeline(sname)
        if err_msg:
            gt_dict = {"error":err_msg}
            err_msg = "{0} {1}".format(err_msg, sname)
            lib_log.error(err_msg)
            return gt_dict
    

    # sequential classifier
    text_features = feature_adapter.extract_text_features(gt_dict["tweets"])
    text_pred = text_decoder.predict(text_features)
    loc_pred = loc_decoder.predict(feature_adapter.extract_ngram_features(gt_dict["loc"]))
    tz_pred = tz_decoder.predict(feature_adapter.extract_ngram_features(gt_dict["tz"]))
    print "L0 predictions:", text_pred, loc_pred, tz_pred
    #print text_pred, loc_pred, tz_pred, desc_pred, rname_pred

    text_id = city_adapter.get_id_by_city(text_pred) + fea_num * 0
    loc_id = city_adapter.get_id_by_city(loc_pred) + fea_num * 1
    tz_id = city_adapter.get_id_by_city(tz_pred) + fea_num * 2
    fea_vec_liblinear = [{text_id:1, loc_id:1, tz_id:1}]

    print "L1 data:", fea_vec_liblinear 
    p_label, p_acc, p_val = liblinearutil.predict([1], fea_vec_liblinear, stacked_model)
    slr_id = int(p_label[0]) # stacked logistic regression prediction label
    slr_pred = city_adapter.get_city_by_id(slr_id)
    print "L1 prediction:", slr_pred
    gt_dict["pc"] = slr_pred
    slr_lat, slr_lon = lib_grid_search.lookup_coords(slr_pred)

    print "L1 prediction coordinates:", slr_lat, slr_lon
    gt_dict["liw"] = text_features
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

def predict_by_text(text):
    features = feature_adapter.extract_text_features([text])
    print features
    text_pred = text_decoder.predict(features)
    print text_pred
    gt_dict = dict()
    slr_lat, slr_lon = lib_grid_search.lookup_coords(text_pred)
    gt_dict["liw"] = features
    gt_dict["pc"] = text_pred
    gt_dict["plat"] = slr_lat
    gt_dict["plon"] = slr_lon
    gt_dict["errdist"] = "";
    gt_dict["error"] = None;
    gt_dict["text_pred"] = text_pred
    gt_dict["loc_pred"] = ""
    gt_dict["tz_pred"] = ""
    return gt_dict

def predict_by_user(user):
    return geolocate(user)

if __name__ == "__main__":
    print predict_by_text("yinz cmu is indicative enough");
    print predict_by_user("brooklynhan");

