#!/usr/bin/env python
"""
Geolocation prediction xmlrpc server, using port: 8999
"""


import ujson as json
import pprint
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from geoloc.classifiers import stacked_logit
from geoloc.adapters import twitter_adapter, city_adapter


def tailor_bot_output(sname, gt_dict):
    if gt_dict["error"]:
        return None
    lat = gt_dict["plat"]
    lon = gt_dict["plon"]
    pc = gt_dict["pc"]
    oc = gt_dict["oc"]
    rpc = city_adapter.convert_readable(pc)
    msg = None
    if oc:
        if pc == oc:
            msg = "Dear @{0}, I am confident that your home location is near {1}({2},{3})".format(sname, rpc, lat, lon)
        else:
            msg = "Dear @{0}, I think your home location is near {1}({2},{3}), but probably I am wrong".format(sname, rpc, lat, lon)
    else:
        msg = "Dear @{0}, I think your home location is near {1}({2},{3}). Please tell me if I am wrong.".format(sname, rpc, lat, lon)
    return msg


def generate_summary(gt_dict):
    summary = None
    if gt_dict["oconf"] == 2:
        summary = "Summary: <b>{0}</b> has <b>{1}</b> recent status updates. <b>{2}</b> of them are geotagged tweets and the home location is in <b>{3}</b>. Our prediction error distance is <b>{4}</b> kilometers.".format(
                gt_dict["sname"],
                len(gt_dict["tweets"]),
                len(gt_dict["footprints"]),
                city_adapter.convert_readable(gt_dict["oc"]),
                gt_dict["errdist"],
                )
    elif gt_dict["oconf"] == 1:
        summary = "Summary: <b>{0}</b> has <b>{1}</b> recent status updates. <b>{2}</b> of them are geotagged tweets and the most frequent location (<b>{3}</b>) is assumed to be the home location. Our prediction error distance is <b>{4}</b> kilometers.".format(
                gt_dict["sname"],
                len(gt_dict["tweets"]),
                len(gt_dict["footprints"]),
                city_adapter.convert_readable(gt_dict["oc"]),
                gt_dict["errdist"],
                )
    else:
        summary = "Summary: <b>{0}</b> has <b>{1}</b> recent status updates. None of them is geotagged.".format(gt_dict["sname"], len(gt_dict["tweets"]))
    return summary


def tailor_web_output(gt_dict):
    if gt_dict["error"]:
        return json.dumps(gt_dict)
    gt_dict["summary"] = generate_summary(gt_dict)
    gt_dict["pc"] = city_adapter.convert_readable(gt_dict["pc"])
    del gt_dict["rname"]
    gt_dict["tweets"] = gt_dict["tweets"][:10]
    return json.dumps(gt_dict)


def tailor_cli_output(gt_dict):
    return pprint.pformat(gt_dict)


# For safety reasons, restricts the access
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("localhost", 8999), requestHandler = RequestHandler, allow_none = True)
server.register_introspection_functions()
geoloc_cmd = "geolocate me"


def geolocate_bot(stream_dump, enable_cache = False):
    """    Service method for Twitter bot account    """
    jobj = None
    err_msg = None
    try:
        jobj = json.loads(stream_dump.strip())
        assert("user" in jobj)
        text = jobj["text"].lower().strip()
        if geoloc_cmd not in text:
            err_msg = 'No "{0}" in tweet'.format(geoloc_cmd)
        assert(jobj["user"]["screen_name"])
    except (AssertionError, ValueError, KeyError):
        err_msg = "Invalid Streaming API dump"
    if err_msg:
        print err_msg
        return None
    sname = jobj["user"]["screen_name"]
    print sname
    gt_dict = stacked_logit.geolocate(sname, enable_cache)
    err_msg = gt_dict["error"]
    if err_msg:
        print err_msg
        return None
    else:
        dm = tailor_bot_output(sname, gt_dict)
        print dm
        twitter_adapter.post_direct_message(sname, dm)
        return dm
server.register_function(geolocate_bot)


def geolocate_web(sname, enable_cache = False):
    """    Service method for web demo    """
    gt_dict = stacked_logit.geolocate(sname, enable_cache)
    print "Error: ", gt_dict["error"]
    return tailor_web_output(gt_dict)
server.register_function(geolocate_web)


def geolocate_cli(data, enable_cache = False):
    """    Service method for command line test    """
    gt_dict = stacked_logit.geolocate(data, enable_cache)
    #cli_output = tailor_cli_output(gt_dict)
    #print cli_output
    return gt_dict
server.register_function(geolocate_cli)


print "Geolocation prediction server started ..."
server.serve_forever()

