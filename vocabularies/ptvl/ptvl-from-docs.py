#!/usr/bin/env python

import csv, urllib, sys, codecs, requests
from urllib import urlencode

old_file_id = '1QhBpqiwg9u0nGWmBfWGwlvZzuCumLuK14fl0UjW5NZs'
old_gids = {'palveluluokat-fi.csv': 0,'palveluluokat-en.csv': 116734621,'palveluluokat-sv.csv': 29056597, 'kohderyhmat-fi.csv': 1079968119, 'kohderyhmat-en.csv': 961559206,'kohderyhmat-sv.csv': 1002033396,'elamantilanteet-fi.csv': 1305536407, 'elamantilanteet-en.csv': 817313259, 'elamantilanteet-sv.csv': 2061395118, 'tuottajatyypit-fi.csv': 15595321, 'tuottajatyypit-en.csv': 2034324229, 'tuottajatyypit-sv.csv': 1979600503,'toteutustavat-fi.csv': 1819670788,'toteutustavat-en.csv': 1660427312,'toteutustavat-sv.csv': 948474734}

file_id = '1s5h2QsNB6r0YIao_JEapbaeDIyXao-dWin6mdaPsW5A'
gids = {'palveluluokat.csv': 1454719279,'kohderyhmat.csv': 862026450,'elamantilanteet.csv': 732181190,'tuotantotavat.csv': 576918592, 'tuottajatyypit.csv': 1640884931}

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

