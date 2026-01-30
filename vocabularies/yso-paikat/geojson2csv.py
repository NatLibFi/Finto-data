#!/usr/bin/python3
# coding=utf-8

import argparse
import sys
import csv
import json

def readCommandLineArguments():
    parser = argparse.ArgumentParser(description="Program for extracting coordinates only for linked PNR places that are actually used in YSO Places ontology. Run before skosifying - will speed up the process. Writes turtle as output.")
    parser.add_argument("-i", "--input", help="Input file location for GeoJSON data with place types and coordinates")
    parser.add_argument("-o", "--output", help="Output file name for csv file, e.g., pnr-complete-paikkaid-wgs84-coordinates-table.csv")

    args = parser.parse_args()
    return args

def main():
    args = readCommandLineArguments()
    with open(args.input) as fh:
        data = json.load(fh)
    with open(args.output, 'w', newline='') as fh:
        writer = csv.writer(fh)
        header = ["placeId", "placeType", "WGS84_N", "WGS84_E"]
        writer.writerow(header)
        for feature in data["features"]:
            place_id = feature["properties"]["placeId"]
            place_type = feature["properties"]["placeType"]
            wgs84_n = format(round (feature["geometry"]["coordinates"][1], 5), '.5f')
            wgs84_e = format(round (feature["geometry"]["coordinates"][0], 5), '.5f')
            writer.writerow([place_id, place_type, wgs84_n, wgs84_e])

if __name__ == "__main__":
    main()
