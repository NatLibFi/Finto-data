#!/usr/bin/python3
# coding=utf-8

import argparse
import sys
import csv
from rdflib import Graph, URIRef, Namespace, RDF, Literal
from rdflib.namespace import SKOS

def readCommandLineArguments():
    parser = argparse.ArgumentParser(description="Program for extracting coordinates only for linked PNR places that are actually used in YSO Places ontology. Run before skosifying - will speed up the process. Writes turtle as output.")
    parser.add_argument("-p", "--pnr_input", nargs='?', type=argparse.FileType('r'), help="Input file location for PNR data, e.g., pnr.csv. Expects the following (comma separated) column order: 0: 'paikkaID', 1: 'paikkatyyppi', 2: 'WGS84_N', 3: 'WGS84_E", default=sys.stdin)
    parser.add_argument("-w", "--wd_input", nargs='?', type=argparse.FileType('r'), help="Input file location for Wikidata data, which contain Wikidata ids for matching PNR ids" , default=sys.stdin)
    parser.add_argument("-s", "--selector", nargs='?', type=argparse.FileType('r'), help="Input file location for used PNR ids, e.g., usedPNRs.csv. Single column expected. If not specified, will select all.", default=None)
    parser.add_argument("-o", "--output", type=argparse.FileType('w+'), help="Output file name, e.g., yso-paikat-used-pnr-coordinates.ttl", default=sys.stdout)

    args = parser.parse_args()
    return args

def main():
    args = readCommandLineArguments()
    sys.stdout = args.output
    select_all = False
    selected = set()

    g = Graph()
    g.parse(args.wd_input, format="ttl")

    pnr_wikidata_dict = dict()
    for concept in g.subjects(RDF.type):
        pnr_id = str(g.value(concept, SKOS.notation))
        if pnr_id:
            qid = str(concept).split("/")[-1]
            pnr_wikidata_dict[pnr_id] = qid

    if args.selector == None:
        select_all = True
    else:
        selected_reader = csv.reader(args.selector)
        for row in selected_reader:
            selected.add(row[0])

    reader = csv.reader(args.pnr_input)
    next(reader, None)
    print("@prefix wd: <http://www.wikidata.org/entity/> .")
    print("@prefix wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#> .")
    print("@prefix pnr: <http://paikkatiedot.fi/so/1000772/> .")
    print("@prefix ysometa: <http://www.yso.fi/onto/yso-meta/> .")
    for row in reader:
        if select_all or row[0] in selected:
            place_type = pnr_wikidata_dict[row[1]]
            print('pnr:' + row[0] + ' wgs84:lat "' + row[2] + '" .')
            print('pnr:' + row[0] + ' wgs84:long "' + row[3] + '" .')
            print('pnr:' + row[0] + ' ysometa:mmlPlaceType wd:' + place_type + ' .')


if __name__ == "__main__":
    main()
