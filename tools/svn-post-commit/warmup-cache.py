#!/usr/bin/env python

import json
import urllib
import time

# TODO make these overridable parameters?
APIBASE="http://dev.kansalliskirjasto.onki.fi/rest/v1/"
URLBASE="http://dev.kansalliskirjasto.onki.fi/"

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
