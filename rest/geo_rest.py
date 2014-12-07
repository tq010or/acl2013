#!/usr/bin/env python
"""
Geolocation prediction using RESTful Flask framework
"""

import os
pkg_path = os.environ["geoloc"]
import ujson as json
from flask import Flask, request, render_template
from time import gmtime, strftime, sleep
import geotagger
from threading import Lock
from geoloc.adapters import geo_stream_dispatcher

app = Flask(__name__)
lock = Lock()

log_folder = "./log"
suffix = ".tsl"
correct = 0
wrong = 0
tsls = []
max_tsls = 2
prev_ts = strftime("%Y%m%d%H", gmtime())
cache_data = []
result_data = []

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

@app.route('/report', methods=['post'])
def get_report():
    global correct, wrong, prev_ts
    # read files that are fully written
    cur_ts = strftime("%Y%m%d%H", gmtime())
    cur_folder = os.path.join(log_folder, cur_ts)
    plog_file = None
    while True:
        try:
            plogs = [plog for plog in os.listdir(cur_folder) if plog.endswith(".json")]
            plogs.sort(key=lambda x: os.stat(os.path.join(cur_folder, x)).st_mtime)
            plog_file = os.path.join(cur_folder, plogs[-2])
            print plog_file
            break
        except IndexError:
            sleep(10)
        except OSError:
            sleep(30)
    # judge results
    result_dict = json.loads(open(plog_file).readline())
    if result_dict["oc"] == result_dict["pc"]:
        correct += 1
    else:
        wrong += 1

    result_dict["last_time_stamp"] = strftime("%Y-%m-%d %H:%M:%S ", gmtime())
    result_dict["correct"] = correct
    result_dict["wrong"] = wrong

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

def init_server():
    global tsls, correct, wrong
    tsls = sorted([pflog for pflog in os.listdir(log_folder) if pflog.endswith(suffix)])
    if tsls:
        with open(tsls[-1]) as fr:
            for l in fr:
                jobj = json.loads(l)
                correct = jobj["correct"]
                wrong = jobj["wrong"]

def update_pflog(ts):
    jobj = dict()
    jobj["correct"] = correct
    jobj["wrong"] = wrong
    json.dump(jobj, open("{0}{1}{2}".format(log_folder, ts, suffix), "w"))
    tsls = sorted([pflog for pflog in os.listdir(log_folder) if pflog.endswith(suffix)])
    if len(tsls) > max_tsls:
        os.remove(tsls[0])

if __name__ == '__main__':
    init_server()
    app.run(host = '0.0.0.0', port = int(7000), debug = True)
