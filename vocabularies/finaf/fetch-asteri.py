#!/usr/bin/python3
import sickle
import re
import os
import sys
from time import sleep
from requests.exceptions import HTTPError
from lxml import etree

url = 'https://oai-pmh.api.melinda.kansalliskirjasto.fi/aut-names'

retry_sleep = 10
retry_error = 10

retry_count = 0
harvested = 0

def main():
  harvester = sickle.Sickle(url)

  set = sys.argv[1] if len(sys.argv) >= 2 and len(sys.argv[1]) > 0 else None
  from_param = sys.argv[2] if len(sys.argv) >= 3 else None
  until = sys.argv[3] if len(sys.argv) >= 4 else None

  iterator = harvester.ListRecords(**{'metadataPrefix': 'melinda_marc', 'set': set, 'from': from_param, 'until': until})

  harvest(iterator)

def harvest(iterator):
  global harvested, retry_count

  try:
    for response in iterator:
      harvested += 1
      record = response.xml.find('.//{http://www.loc.gov/MARC21/slim}record')
      if record is None:
        continue
      sys.stdout.buffer.write(etree.tostring(record))
      sys.stdout.buffer.write(b'\n')
  except HTTPError as e:
    if e.response.status_code == 500 and retry_count < retry_error:
       retry_count += 1
       print('Server responded with error, trying again {}/{}'.format(retry_count, retry_error))
       sleep(retry_sleep)
       harvest(iterator)
    elif e.response.status_code in [404,502,503]:
      print("Server temporarily unavailable. Trying again in {} seconds".format(retry_sleep))
      sleep(retry_sleep)
      harvest(iterator)
    else:
      raise e
    
if __name__ == '__main__':
  main()
