#!/usr/bin/env python3

import csv, urllib, sys, codecs, requests
from urllib.parse import urlencode

file_ids = {'classes.csv': '1rhHmuR6SpJc-hRbVyge2mlHobGHiWuv6yH8TxXnu-Ds',
            'glossary.csv': '1ldnNZjhGb_e3XztUiUh7kPt_PUg9lwbEUdDV4bHfTxY',
            'metadata.csv': '1zjZw8Oa6KCSbRR9nk4rwprt-2JGNUzJitCtKMrb_K7A'}

def loadSheet(file_id, filename):
  params = urlencode({'exportFormat': 'csv'})
  api = 'https://docs.google.com/spreadsheets/d/' + file_id + '/export?'
  url = api + params
  try:                                                                           
    output = codecs.open(filename, 'w', encoding='utf8')
    response = requests.get(url)
    response.encoding = 'utf-8'
    print('wrote: ' + filename)
    output.write(response.text)
    output.close()
  except:
    print(sys.exc_info()[0].message)
    print('failed loading: ' + url)

for filename, file_id in file_ids.items():
  loadSheet(file_id, filename)

