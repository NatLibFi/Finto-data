#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

tree = ET.parse(sys.argv[1])
root = tree.getroot()

for m in root.iter("metadata"):
  for k in m.findall("kieli"):
    if k.text == "FI":
      for n in m.findall("nimi"):
        print(n.text)
