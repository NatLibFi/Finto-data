#!/usr/bin/python3
# coding=utf-8

import argparse
import sys
import csv

def readCommandLineArguments():
    parser = argparse.ArgumentParser(description="Program for extracting coordinates only for linked PNR places that are actually used in YSO Places ontology. Run before skosifying - will speed up the process. Writes turtle as output.")
    parser.add_argument("-i", "--input", nargs='?', type=argparse.FileType('r'), help="Input file location, e.g., pnr.csv. Expects the following (comma separated) column order: 0: 'paikkaID', 1: 'WGS84_N', 2: 'WGS84_E", default=sys.stdin)
    parser.add_argument("-s", "--selector", nargs='?', type=argparse.FileType('r'), help="Input file location for used PNR ids, e.g., usedPNRs.csv. Single column expected. If not specified, will select all.", default=None)
    parser.add_argument("-o", "--output", type=argparse.FileType('w+'), help="Output file name, e.g., yso-paikat-used-pnr-coordinates.ttl", default=sys.stdout)

    args = parser.parse_args()
    return args

def main():
    args = readCommandLineArguments()
    sys.stdout = args.output
    select_all = False
    selected = set()

    if args.selector == None:
        select_all = True
    else:
        selected_reader = csv.reader(args.selector)
        for row in selected_reader:
            selected.add(row[0])

    reader = csv.reader(args.input)
    next(reader, None)
    print("@prefix wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#> .")
    print("@prefix pnr: <http://paikkatiedot.fi/so/1000772/> .")
    for row in reader:
        if select_all or row[0] in selected:
            print('pnr:' + row[0] + ' wgs84:lat "' + row[1] + '" .')
            print('pnr:' + row[0] + ' wgs84:long "' + row[2] + '" .')


if __name__ == "__main__":
    main()
