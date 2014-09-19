#!/usr/bin/env python3
# coding: utf-8
import csv, json, urllib, codecs, sys, operator, time
from urllib.request import urlopen
from urllib.parse import urlencode
import argparse
import csv

def pstrip(term):
  return term.strip('"\' ') #stripping quote chars surrounding the term

# Lemmatizes a term
def lemmatize(term):
  params = urlencode({ 'text': term , 'locale': 'fi'})
  seco_api = 'http://demo.seco.tkk.fi/las/baseform?'
  url = seco_api + params 
  response = urlopen(url).readall().decode('utf-8')
  return pstrip(response)

# sees if a term exists in the ontology
def lookup(term, vocab_id):
#  print(term)
  params = urlencode({'label': pstrip(term), 'lang': 'fi'})
  finto_api = 'http://api.finto.fi/rest/v1/' + vocab_id + '/lookup?' 
  url = finto_api + params 
  try:
    response = urlopen(url)
  except:
    return False
  return True

# reads in lemmas and URIs from a file
def read_lemmas(filepath):
  f = open(filepath)
  r = csv.reader(f)

  d = {}
  for l in r:
    d[l[0]] = l[1:]

  return d

################

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("termfile", help="file containing the terms of the matched vocabulary")
  parser.add_argument("--lemmafile", help="file containing lemmatized labels and URIs")
  args = parser.parse_args()
  
  
  found_terms = []
  unfound_terms = []
  
  lemmed_terms = []
  
  #vocab_id = sys.argv[2]
  vocab_id = 'jupo'
  #termfile = sys.argv[1] # input file containing the terms on different lines
  seco_api = 'http://demo.seco.tkk.fi/las/baseform?'
  finto_api = 'http://api.finto.fi/rest/v1/' + vocab_id + '/lookup?'
  terms = []
  
  
  lemmas = {}
  if args.lemmafile is not None:
    lemmas = read_lemmas(args.lemmafile)
  
  
  found = 0
  not_found = 0
  lemmed_found = 0
  
  file_handle = open(args.termfile, 'r')
  for row in file_handle:
    term = row.strip('"\' \t\n').lower()
  #  term = row.strip().lower()
    if term not in terms:
      terms.append(term)
      if lookup(term, vocab_id):
        # found from the vocab
        found += 1
        found_terms.append(term)
      else:
        # trying to find from the vocab after lemmatizing
        lemmed = lemmatize(term)
        if lemmed not in terms:
          terms.append(lemmed)
          if lookup(lemmed, vocab_id):
            # found match from the ontology by lemmatizing the term
            #found += 1
            #found_terms.append(lemmed)
            lemmed_terms.append(lemmed)
            lemmed_found += 1
          else:
            if args.lemmafile is not None:
              # performing matching the lemmatized term against the lemmatized labels
              # only done if the lemmas are loaded
              if lemmed in lemmas:
                lemmed_terms.append(lemmed)
                lemmed_found += 1
                continue
            not_found += 1
            unfound_terms.append(lemmed)
  #exit(0)
  
  print('terms in input file: ' + str(len(terms)))
  print('total amount of unique terms' ': ' + str(found + not_found + lemmed_found))
  print('found in ' + vocab_id + ': ' + str(found))
  print('lemmed found in ' + vocab_id + ': ' + str(lemmed_found))
  print('not found in ' + vocab_id + ': ' + str(not_found))
  print(str(round((found+lemmed_found)/(not_found+found+lemmed_found)*100)) + '% unique terms found in ' + vocab_id)
  
  print('*******************')
  print('*** FOUND TERMS ***')
  for t in found_terms:
    print(t)
  
  print('**************************')
  print('*** LEMMED FOUND TERMS ***')
  for t in lemmed_terms:
    print(t.strip('"'))
  
  print('*********************')
  print('*** UNFOUND TERMS ***')
  for t in unfound_terms:
    print(t.strip('"'))
  
