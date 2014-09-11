#!/usr/bin/env python

import json
import urllib
import time
import sys

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %d <urlbase>" % sys.argv[0]
    sys.exit(1)

URLBASE=sys.argv[1]
APIBASE=URLBASE + "rest/v1/"

def vocab_ids():
    url = APIBASE + "vocabularies?lang=en"
    result = urllib.urlopen(url)
    data = json.load(result)
    return [v['id'] for v in data['vocabularies']]

def vocab_languages(vocab_id):
    url = APIBASE + "%s/" % vocab_id
    result = urllib.urlopen(url)
    data = json.load(result)
    return data['languages']

for vid in vocab_ids():
    for lang in vocab_languages(vid):
        # determine vocabulary home page URL
        url = URLBASE + "%s/%s/" % (vid, lang)
        starttime = time.time()
        result = urllib.urlopen(url)
        length = len(result.read())
        endtime = time.time()
        print url, length, int((endtime-starttime)*1000)
