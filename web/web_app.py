#! /usr/bin/env python
"""
Web demo (interactive web pages).
Input: user screen name
Output: tailored GT-JSON results
"""


import BaseHTTPServer
import SimpleHTTPServer
import xmlrpclib
#import re

FILE = 'geo.html'
PORT = 9000
geolocator = xmlrpclib.ServerProxy("http://localhost:8999")
#sname_validator = re.comiple("^[A-Za-z0-9]{1,15}$")

class WebGeoLocHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.getheader("content-length"))
        sname = self.rfile.read(length)
        #TODO: remove harmful characters
        sname = "".join(sname.split()).lower()
        if sname[0] == "@":
            sname = sname[1:]
        try:
            gt_json = geolocator.geolocate_web(sname, False)
            print sname
            self.wfile.write(gt_json)
        except xmlrpclib.Fault as e:
            print "{0} {1}".format(sname, e)
            self.wfile.write("{'error':'XMLRPC service error'}")


def start_server():
    """Start the server."""
    server_address = ("", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, WebGeoLocHandler)
    print "Web demo started ..."
    server.serve_forever()


if __name__ == "__main__":
    import webbrowser;webbrowser.open("http://localhost:{0}/{1}".format(PORT, FILE))
    start_server()
