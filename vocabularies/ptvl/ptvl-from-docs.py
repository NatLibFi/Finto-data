#!/usr/bin/env python3

import csv, urllib, sys, codecs, requests
from urllib.parse import urlencode

file_id = '1QhBpqiwg9u0nGWmBfWGwlvZzuCumLuK14fl0UjW5NZs'
gids = {'palveluluokat.csv': 0,'kohderyhmat.csv': 1079968119,'elamantilanteet.csv': 1305536407,'tuottajatyypit.csv': 15595321,'toteutustavat.csv': 1819670788}

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

