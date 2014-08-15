#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

tree = ET.parse(sys.argv[1])
root = tree.getroot()

for r in root.iter('RECORD'):
  for l in r.findall('LANG'):
    if l.attrib['value'] == "fi":
      for te in l.findall('TE'):
        for term in te.findall('TERM'):
          print(term.text)
