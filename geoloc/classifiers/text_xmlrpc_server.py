#!/usr/bin/env python
"""
XML-PRC for text-based classifier.
Input: text features in python dict
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
server = SimpleXMLRPCServer(("localhost", 9001), requestHandler = RequestHandler)
server.register_introspection_functions()

model_file = "{0}/models/world.text.train.model".format(pkg_path)
print "Loading {0} ...".format(model_file)
text_decoder = mbayes_decoder.decoder(model_file)
print "{0} loaded".format(model_file)

# define location
def predict(arg_obj):
    pred = text_decoder.predict(arg_obj)
    return pred
server.register_function(predict)

print "Geolocation server (text) started ..."
server.serve_forever()

