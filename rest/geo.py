from flask import Flask, request, render_template
try:
    import ujson as json
except ImportError:
    import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/text', methods=['post'])
def geolocate_by_text():
    data = request.form['text']
    print data
    footprints = [];
    footprints.append(("city0", -37.80, 144.90, "tweet text 0"))
    footprints.append(("city1", -37.81, 144.91, "tweet text 1"))
    footprints.append(("city2", -37.82, 144.92, "tweet text 2"))
    result_json = {}
    result_json["footprints"] = footprints
    print result_json
    return json.dumps(result_json)

@app.route('/user', methods=['post'])
def geolocate_by_user():
    data = request.form['user']
    print data
    footprints = [];
    footprints.append(("city0", -37.80, 144.90, "tweet text 0"))
    footprints.append(("city1", -37.81, 144.91, "tweet text 1"))
    footprints.append(("city2", -37.82, 144.92, "tweet text 2"))
    result_json = {}
    result_json["footprints"] = footprints
    print result_json
    return json.dumps(result_json)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = int(5000), debug = True)
