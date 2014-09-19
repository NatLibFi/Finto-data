#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

def print_form(s):
  if s == None:
    return ""
  else:
    return str(s)

tree = ET.parse(sys.argv[1])
root = tree.getroot()

terms = {}

for r in root.iter('RECORD'):
  terms["fi"], terms["sv"], terms["en"] = "", "", ""

  for l in r.findall('LANG'):
    lang = l.attrib['value']
    for te in l.findall('TE'):
      for term in te.findall('TERM'):
        terms[lang] = print_form(term.text)
  
#  print("%s,%s,%s") % (terms["fi"], terms["fi"], terms["fi"])
  
  print(terms["fi"]+","+terms["sv"]+","+terms["en"])

