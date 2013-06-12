===========
Geolocation Prediction for Public Twitter Users
===========

This package provides a city-level geolocation prediction for non-protected Twitter users.

The code and data is used in the following paper:

Bo Han, Paul Cook and Timothy Baldwin, (to appear) A Stacking-based Approach to Twitter User Geolocation Prediction, In Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics (ACL 2013), Demo Session, Sofia, Bulgaria.



Quick Start
=========
1. The system requires the following prerequisites:
* python 2.65 (python 2.7.3 is also tested)
* ujson (https://pypi.python.org/pypi/ujson) 
* twython library (git://github.com/ryanmcgrath/twython.git)
* liblinear (http://www.csie.ntu.edu.tw/~cjlin/cgi-bin/liblinear.cgi?+http://www.csie.ntu.edu.tw/~cjlin/liblinear+zip)


2. Set environment variable.
Suppose you are using Ubuntu Linux and you have extracted the package to your home folder, e.g., /home/YOUR_NAME/acl2013.
$ cd ~
$ vim .bashrc 
Add the following "exports" in /.bashrc
export PYTHONPATH=/home/YOUR_NAME/acl2013:$PYTHONPATH
export geoloc=/home/YOUR_NAME/acl2013/geoloc


3. get pre-trained models and set your program credentials
Decompress pre-trained models as follows,
$ cd /home/YOUR_NAME/acl2013/geoloc/models
$ tar -zxvf world.models.tar.gz
Then save your credentials in four lines in /home/YOUR_NAME/acl2013/geoloc/data/credentials.txt according to the following order.
consumer_token
consumer_secret
access_token
access_secret


4. start the service
Open 4 terminal windows, and start each of the service in the "classifier" folder.
Alternatively, you can use "screen" command to simulate multiple terminals.
$ cd /home/YOUR_NAME/acl2013/geoloc/classifiers
$ python text_xmlrpc_server.py 
$ python loc_xmlrpc_server.py 
$ python tz_xmlrpc_server.py 
$ python geo_xmlrpc_server.py


5. test the live service
This little demo geolocates authors
$ cd /home/YOUR_NAME/acl2013/api
$ python geoloc_cli.py


6. test the website (currently only Google Chrome browser is supported).
$ cd /home/YOUR_NAME/acl2013/web
$ python web_app.py



Experiment Replication
=========
Because of Twitter API policy, we are not able to share the raw data, but provide the user ids we used for our experiments (see more in the paper).
You can crawl them for evaluation. Please note that because of the tweet and user account deletion in Twitter, some user tweets may be not available after the release.

The English user screen names are put in /home/acl2013/evaluation/data/live.unames, one screen name per user. Note this also include users with only a few geo-tagged tweets or with lower than 50% coherence. We exclude them in later evaluation, the process is transparent.
We only use LIVETEST (see more in the paper) for demonstration.

When crawling data using Twitter API, please save all the raw tweet dump in /home/YOUR_NAME/evaluation/live and name the tweet dump after the user name.
Suppose a user named "tuser", when you run following command,
$ less /home/YOUR_NAME/evaluation/live/tuser
the following format data will show
[{tweet dump_1}, {tweet dump_2}, ... {tweet dump_n}]
It is a list of tweet dump (in JSON dict format).

To run the evaluation, simply run
$ python /home/YOUR_NAME/evaluation/code/eval_livetest.py

If everything is correct, you should get the prediction results and summary (31629 lines in total) printed in the standard output.
The last five lines are like:
Acc: 0.405957500632
Acc161: 0.613995699469
AccCountry: 0.900613458133
Median: 39.9827729857
Mean: 937.655151249



Citations
=========
Please cite the following paper whenever appropriate:

Bo Han, Paul Cook and Timothy Baldwin, (to appear) A Stacking-based Approach to Twitter User Geolocation Prediction, In Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics (ACL 2013), Demo Session, Sofia, Bulgaria.



MISC
=========
We also offer some off-the-shelf demos, but the availability of these services are without warranty.

For web access: <http://hum.csse.unimelb.edu.au:9000/geo.html>
For Twitter bot access: @melbltfsd



TODOs:
=========
0. Lots of refactoring work.
1. Documentation.
2. Parallel decoding (using openMP for instance).


Contact
=========
Comments and suggestions are highly welcomed.

Bo Han, hanb@student.unimelb.edu.au
