#!/usr/bin/env python
"""
Geolocation prediction using RESTful Flask framework
"""

import os
pkg_path = os.environ["geoloc"]
import ujson as json
from flask import Flask, request, render_template
from time import gmtime, strftime
import geotagger
from threading import Lock
from geoloc.adapters import geo_stream_dispatcher

app = Flask(__name__)
lock = Lock()

def generate_summary(gt_dict):
    summary = None
    if gt_dict["oconf"] == 2:
        summary = "Summary: <b>{0}</b> has <b>{1}</b> recent status updates. </br> <b>{2}</b> of them are geotagged tweets and the home location is in <b>{3}</b>. </br> Our prediction error distance is <b>{4}</b> kilometers.".format(
                gt_dict["sname"],
                len(gt_dict["tweets"]),
                len(gt_dict["footprints"]),
                gt_dict["oc"],
                gt_dict["errdist"],
                )
    elif gt_dict["oconf"] == 1:
        summary = "Summary: <b>{0}</b> has <b>{1}</b> recent status updates. </br> <b>{2}</b> of them are geotagged tweets and the most frequent location (<b>{3}</b>) is assumed to be the home location. </br> Our prediction error distance is <b>{4}</b> kilometers.".format(
                gt_dict["sname"],
                len(gt_dict["tweets"]),
                len(gt_dict["footprints"]),
                gt_dict["oc"],
                gt_dict["errdist"],
                )
    else:
        summary = "Summary: <b>{0}</b> has <b>{1}</b> recent status updates. </br> None of them is geotagged.".format(gt_dict["sname"], len(gt_dict["tweets"]))
    return summary


def tailor_web_output(gt_dict):
    if gt_dict["error"]:
        return json.dumps(gt_dict)
    gt_dict["summary"] = generate_summary(gt_dict)
    gt_dict["pc"] = gt_dict["pc"]
    del gt_dict["rname"]
    gt_dict["tweets"] = gt_dict["tweets"][:10]
    return json.dumps(gt_dict)

def tailor_report_output(gt_dict):
    if gt_dict["error"]:
        return json.dumps(gt_dict)
    summary = None
    if gt_dict["oconf"] == 2:
        summary = "<b>{0}</b> is predicted to <b>{1}</b> and the true location is <b>{2}</b>. The prediction error distance is <b>{3}</b> km based on <b>{4}</b> tweets in prediction and <b>{5}</b> geotagged tweets for verification".format(gt_dict["sname"], gt_dict["pc"], gt_dict["oc"], gt_dict["errdist"], len(gt_dict["tweets"]), len(gt_dict["footprints"]))
    else:
        summary = "<b>{0}</b> is predicted to <b>{1}</b> and the estimated true location is <b>{2}</b>. The prediction error distance is <b>{3}</b> km based on <b>{4}</b> tweets in prediction and <b>{5}</b> geotagged tweets as ground truth data".format(gt_dict["sname"], gt_dict["pc"], gt_dict["oc"], gt_dict["errdist"], len(gt_dict["tweets"]), len(gt_dict["footprints"]))
    gt_dict["summary"] = summary
    gt_dict["pc"] = gt_dict["pc"]
    del gt_dict["rname"]
    gt_dict["tweets"] = gt_dict["tweets"][:10]
    return json.dumps(gt_dict)

def geolocate_web(sname, enable_cache = False):
    """    Service method for web demo    """
    gt_dict = stacked_logit.geolocate(sname, enable_cache)
    print "Error: ", gt_dict["error"]
    return tailor_web_output(gt_dict)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/geo')
def geo():
    return render_template("geo.html")

cache_data = []
@app.route('/report', methods=['post'])
def get_report():
    global cache_data
    data = None
    with lock:
        if not cache_data:
            cache_data = geo_stream_dispatcher.get_sname_list(100)
        data = cache_data.pop()
    result_dict = geotagger.predict_by_user(data);
    cur_time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    result_dict["last_time_stamp"] = cur_time_str
    return tailor_report_output(result_dict);

@app.route('/text', methods=['post'])
def geolocate_by_text():
    data = request.form['text']
    result_dict = geotagger.predict_by_text(data);
    result_dict["summary"] = "Summary: The predicted city is: <b>" + result_dict["pc"] + "</b>";
    return json.dumps(result_dict)

@app.route('/user', methods=['post'])
def geolocate_by_user():
    data = request.form['user']
    result_dict = geotagger.predict_by_user(data);
    return tailor_web_output(result_dict);


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = int(7000), debug = True)
