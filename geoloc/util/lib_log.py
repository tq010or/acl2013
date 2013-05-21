#!/usr/bin/env python

"""
Customised global logger
"""

import os
pkg_path = os.environ["geoloc"]
import logging
#import datetime
#time_stamp = datetime.datetime.now()
#time_stamp = time_stamp.strftime("%Y%m%d%H%M")
logger = logging.getLogger('geoloc')
hdlr = logging.FileHandler('{0}/log/app.log'.format(pkg_path))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

def error(msg):
    logger.error(msg)

def info(msg):
    logger.info(msg)

def debug(msg):
    logger.debug(msg)
