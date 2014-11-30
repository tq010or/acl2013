#!/usr/bin/env python
"""
Grab geo tweets from Twitter Streaming API
For English, geotagged users, grab his/her screen_name
most recent 200 tweets 
Throw any users that are not realiable (with fewer than 10 geotagged tweets or not 5 of them are from one location)
Predict users and save both input and result on disk in .gz format 
"""

import ujson as json
import langid
from twython import TwythonStreamer
import twython
import time
import sys

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        global index
        # filter geo and English records
        if 'coordinates' in data and data['coordinates']:
            if data['coordinates']["type"] == "Point":
                text = data["text"]
                if langid.classify(text)[0] == 'en':
                    uid = data["user"]["screen_name"]
                    print uid

    def on_error(self, status_code, data):
        pass
        #print status_code
        # stop trying to get data because of an error
        #self.disconnect()

def monitor_stream():
    # reading credentials
    credentials = sys.argv[1].split(" ")
    APP_KEY = credentials[0]
    APP_SECRET = credentials[1]
    OAUTH_TOKEN = credentials[2]
    OAUTH_TOKEN_SECRET = credentials[3]

    #TODO: incremental backup time interval?
    back_up_interval = 90
    while True:
        try:
            #TODO: Accept-Encoding: deflate, gzip
            stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
            stream.statuses.filter(locations='-180,-90,180,90')
        except twython.TwythonRateLimitError:
            time.sleep(back_up_interval)
        except twython.TwythonAuthError:
            time.sleep(back_up_interval)
        except twython.TwythonError:
            time.sleep(back_up_interval)
        except:
            time.sleep(30)

def main():
    monitor_stream()

if __name__ == "__main__":
    main()
