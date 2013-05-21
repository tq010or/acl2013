#!/usr/bin/env python
"""
Input: a Twitter user screen name (The Twitter user account should be non-protected)
Output: 
"""

import sys
import xmlrpclib
import time

proxy = xmlrpclib.ServerProxy("http://localhost:8999")


# heavy user queries for batching processing
screen_names = ["brooklynhan", "cpaulcook", "eltimster"]
for screen_name in screen_names:
    result = proxy.geolocate_cli(screen_name)
    print result
    time.sleep(60)
    print



# single user query for pre-research
screen_name = "brooklynhan" # case insensitive
result = proxy.geolocate_cli(screen_name)
print result
