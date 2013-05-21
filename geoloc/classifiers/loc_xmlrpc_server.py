#!/usr/bin/env python
"""
XML-PRC for loc-based classifier.
Input: loc 4gram list
Output: canonical predicted city name
"""


from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import os
pkg_path = os.environ["geoloc"]
import mbayes_decoder

# For safety reasons, restricts access
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("localhost", 9002), requestHandler = RequestHandler)
server.register_introspection_functions()

model_file = "{0}/models/world.loc.train.model".format(pkg_path)
print "Loading {0} ...".format(model_file)
loc_decoder = mbayes_decoder.decoder(model_file)
print "{0} loaded".format(model_file)

# define location
def predict(arg_obj):
    pred = loc_decoder.predict(arg_obj)
    return pred
server.register_function(predict)

print "Geolocation server (loc) started ..."
server.serve_forever()

