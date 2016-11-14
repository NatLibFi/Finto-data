#!/usr/bin/env python3

import csv, urllib, sys, codecs, requests
from urllib.parse import urlencode

file_id = '1QhBpqiwg9u0nGWmBfWGwlvZzuCumLuK14fl0UjW5NZs'
gids = {'palveluluokat-fi.csv': 0,'palveluluokat-en.csv': 116734621, 'kohderyhmat-fi.csv': 1079968119, 'kohderyhmat-en.csv': 961559206,'elamantilanteet-fi.csv': 1305536407, 'elamantilanteet-en.csv': 817313259, 'tuottajatyypit-fi.csv': 15595321,'toteutustavat-fi.csv': 1819670788}

def loadSheet(file_id, filename, sheet_gid):
  params = urlencode({'exportFormat': 'csv', 'gid': sheet_gid})
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

for filename in gids:
  loadSheet(file_id, filename, gids[filename])

