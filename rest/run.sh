#!/usr/bin/env bash

export PYTHONPATH=/Users/hanb/git/acl2013:$PYTHONPATH;
export geoloc=/Users/hanb/git/acl2013/geoloc;
clear;
#python geotagger.py
python geo-rest.py 
