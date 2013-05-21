#!/usr/bin/env python
"""
Oauth-enabled Twitter adapter
"""


import os
pkg_path = os.environ["geoloc"]
import ujson as json
import twitter
from geoloc.util import tokeniser, lib_grid_search, lib_util, lib_log


#TODO: Add your credential information in the following file.
credential_obj = open("{0}/data/credential.txt".format(pkg_path)).readlines()
consumer_token = credential_obj[0]
consumer_secret = credential_obj[1]
access_token = credential_obj[2]
access_secret = credential_obj[3]

api = twitter.Api(consumer_key = consumer_token,
        consumer_secret = consumer_secret,
        access_token_key = access_token,
        access_token_secret = access_secret)

t_tokeniser = tokeniser.MicroTokeniser()


def post_direct_message(receiver_sname, dm):
    return api.PostDirectMessage(receiver_sname, dm)


def anonymise_text(text):
    tokens = []
    for token in text.split(' '):
        if token.startswith("@"):
            tokens.append("@user")
        else:
            tokens.append(token)
    return " ".join(tokens)


def get_tokenised(s):
    if not s:
        return ""
    return " ".join(t_tokeniser.tokenise(s))


def simplify_twitter_obj(status):
    """Parse and filter Twitter obj (Twitter.Status)"""
    err_msg = None
    jobj = dict()
    try:
        jobj["text"] = anonymise_text(get_tokenised(status.text))
        jobj["loc"] = get_tokenised(status.user.location)
        jobj["tz"] = get_tokenised(status.user.time_zone)
        jobj["desc"] = get_tokenised(status.user.description)
        jobj["rname"] = status.user.name
        jobj["sname"] = status.user.screen_name
        jobj["lang"] = status.user.lang
        lat, lon = None, None
        if status.geo and status.geo["type"] == "Point":
            if "coordinates" in status.geo:
                lat = status.geo["coordinates"][0]
                lon = status.geo["coordinates"][1]
        jobj["lat"] = lat
        jobj["lon"] = lon 
    except:
        err_msg = "Twitter object processing error"
        lib_log.error(err_msg)
        return (None, err_msg)
    return (jobj, err_msg)


def simplify_twitter_json(jobj):
    """Parse and filter Twitter JSON data"""
    err_msg = None
    try:
        assert(jobj)
        assert("user" in jobj)
    except AssertionError:
        err_msg = "Invalid JSON dump data"
        lib_log.error("err_msg")
        return (None, err_msg)

    jfields = dict()
    jfields["lon"] = None
    jfields["lat"] = None
    if jobj["coordinates"]:
        coordinates= jobj["coordinates"]["coordinates"]
        jfields["lon"] = coordinates[0]
        jfields["lat"] = coordinates[1]
    #TODO: filter English tweets?
    user = jobj["user"]
    jfields["lang"] = user["lang"]
    jfields["rname"] = user["name"]
    jfields["sname"] = user["screen_name"]
    jfields["text"] = get_tokenised(jobj["text"])
    jfields["loc"] = get_tokenised(user["location"])
    jfields["tz"] = get_tokenised(user["time_zone"])
    jfields["desc"] = get_tokenised(user["description"])
    assert(not err_msg)
    return (jfields, err_msg)


def evaluate_oracle_confidence(oc, footprints):
    """
    A confidence indicator of the ground truth data reliability
    2: Confident oracle city
    1: Estimated oracle city
    0: No oracle city
    Most frequent city is selected as the oracle city (oc), we are confident if oc accounts more than 50% footprints and occurs at least 2 times.
    """
    if not oc:
        return 0
    c1 = sum(1.0 for fp in footprints if fp[0] == oc)
    c2 = c1 / len(footprints)
    if c1 >= 10 and c2 >= 0.5:
        return 2
    return 1


def distill_data(statuses, distill_func):
    err_msg = None
    gt_dict = dict()
    gt_dict["oc"] = [] #short for oracle city
    gt_dict["footprints"] = []
    gt_dict["loc"] = []
    gt_dict["tz"] = []
    gt_dict["desc"] = []
    gt_dict["tweets"] = []
    one_off_flag = True
    for status in statuses:
        jobj, err_msg = distill_func(status)
        if err_msg and not jobj:
            return (None, err_msg)
        text = anonymise_text(jobj["text"])
        loc = jobj["loc"]
        tz = jobj["tz"]
        desc = jobj["desc"]
        lat = jobj["lat"]
        lon = jobj["lon"]
        city = None
        if lat and lon:
            city = lib_grid_search.lookup_city(lat, lon)
        if city:
            gt_dict["oc"].append(city)
            gt_dict["footprints"].append((city, lat, lon, text))
        if loc:
            gt_dict["loc"].append(loc)
        if tz:
            gt_dict["tz"].append(tz)
        if desc:
            gt_dict["desc"].append(desc)

        if one_off_flag:
            gt_dict["rname"] = jobj["rname"]
            gt_dict["sname"] = jobj["sname"]
            one_off_flag = False
        gt_dict["tweets"].append(text)
    gt_dict["loc"] = lib_util.most_freq_item(gt_dict["loc"]) if gt_dict["loc"] else ""
    gt_dict["tz"] = lib_util.most_freq_item(gt_dict["tz"]) if gt_dict["tz"] else ""
    gt_dict["desc"] = lib_util.most_freq_item(gt_dict["desc"]) if gt_dict["desc"] else ""
    gt_dict["oc"] = lib_util.most_freq_item(gt_dict["oc"]) if gt_dict["oc"] else None
    oc = gt_dict["oc"]
    gt_dict["oconf"] = evaluate_oracle_confidence(oc, gt_dict["footprints"])
    if oc:
        olat, olon = lib_grid_search.lookup_coords(oc)
        gt_dict["olat"] = olat
        gt_dict["olon"] = olon
    else:
        gt_dict["olat"] = None
        gt_dict["olon"] = None
    gt_dict["error"] = err_msg
    assert(not err_msg)
    return (gt_dict, err_msg)


def parse_user_timeline(input_data):
    """    Parse user timeline data    """
    err_msg = None
    if isinstance(input_data, basestring): # Crawl and parse up to 200 recent statuses from user timeline using Oauth
        try:
            input_data = api.GetUserTimeline(screen_name = input_data, count = 200)
        except twitter.TwitterError:
            err_msg = "Please check <b>" + input_data  + "</b> is correctly spelt and not protected."
            return (None, err_msg) 
        else:
            return distill_data(input_data, simplify_twitter_obj)
    elif isinstance(input_data, list):
        return distill_data(input_data, simplify_twitter_json)
    else:
        err_msg = "Invalida input for parsing user timeline"
        lib_log.error(err_msg)
        return (None, err_msg)


if __name__ == "__main__":
    print api.VerifyCredentials()
