#!/usr/bin/env python
"""
Geolocation prediction xmlrpc server, using port: 8999
"""

import ujson as json
from flask import Flask, request, render_template
from time import gmtime, strftime
import geotagger

app = Flask(__name__)

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

@app.route('/report', methods=['post'])
def get_report():
    data = request.form['last_time_stamp']
    result_dict = dict() 
    cur_time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    result_dict["last_time_stamp"] = cur_time_str
    return json.dumps(result_dict)

@app.route('/text', methods=['post'])
def geolocate_by_text():
    data = request.form['text']
    result_dict = geotagger.predict_by_text(data);
    return json.dumps(result_dict)

@app.route('/user', methods=['post'])
def geolocate_by_user():
    data = request.form['user']
    result_dict = geotagger.predict_by_user(data);
    return json.dumps(result_dict)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = int(5000), debug = True)
