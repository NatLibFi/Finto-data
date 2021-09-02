#!/usr/bin/python3
# coding=utf-8

import argparse
import sys


def printCoordinates(listing, current):
    point = sorted(listing, key=len)[-1].split()
    try:
        print(current + ' wgs84:long "' + "{:.5f}".format(float(point[0][7:])).rstrip('0').rstrip('.') + '" .')
        print(current + ' wgs84:lat "' + "{:.5f}".format(float(point[1][:-53])).rstrip('0').rstrip('.') + '" .')
    except (ValueError, IndexError):
        print ("Warning: '%s' has malformatted coordinates" % (current), file=sys.stderr)

def readCommandLineArguments():
    parser = argparse.ArgumentParser(description="Program for generating single value coordinates out of <http://www.wikidata.org/prop/direct/P625> predicate triple.")
    parser.add_argument("-i", "--input", nargs='?', type=argparse.FileType('r'), help="Input file location, e.g., wikidata-links.nt. Expects a sorted .nt file.", default=sys.stdin)
    parser.add_argument("-o", "--output", type=argparse.FileType('w+'), help="Output file name, e.g., wikidata-links-single-value-coordinates.ttl. Writes turtle.", default=sys.stdout)

    args = parser.parse_args()
    return args

def main():
        args = readCommandLineArguments()
        sys.stdout = args.output
        print("@prefix wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#> .")

        current = None
        listing = []
        for row in [line.rstrip() for line in args.input]:
            split = row.split()
            if current != split[0]:
                if len(listing):
                    printCoordinates(listing, current)
                listing = []

            current = split[0]
            if split[1] == "<http://www.wikidata.org/prop/direct/P625>":
                listing.append(" ".join(split[2:4]))
            else:
                print(row)
        if len(listing):
            printCoordinates(listing, current)

if __name__ == "__main__":
    main()
