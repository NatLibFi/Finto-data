#!/usr/bin/env python3
# coding=utf-8

from rdflib import Graph, Namespace, URIRef, BNode, Literal, RDF
from rdflib.namespace import SKOS, XSD, OWL, DC
from rdflib.namespace import DCTERMS as DCT
from SPARQLWrapper import SPARQLWrapper, SPARQLExceptions
import socket
import time
from pymarc import Record, Field, XMLWriter, MARCReader, parse_xml_to_array
from lxml import etree as ET
import shutil

import pickle
import os
import argparse
import hashlib
import unicodedata
from configparser import ConfigParser, ExtendedInterpolation
import sys
import logging
from datetime import datetime, date, timedelta
import subprocess
import urllib
from collections import namedtuple
from collections.abc import Sequence
from html.parser import HTMLParser

# globaalit muuttujat
CONVERSION_PROCESS = "Finto SKOS to MARC 1.03"
CONVERSION_URI = "https://www.kiwi.fi/x/XoK6B" # konversio-APIn uri tai muu dokumentti, jossa kuvataan konversio
CREATOR_AGENCY = "FI-NL" # Tietueen luoja/omistaja & luetteloiva organisaatio, 040-kentat

DEFAULTCREATIONDATE = "1980-01-01"
KEEPMODIFIEDAFTER = "ALL"
KEEPDEPRECATEDAFTER = "ALL"
ENDPOINT_ADDRESS = "http://api.dev.finto.fi/sparql"
ENDPOINTGRAPHS = [] # palvelupisteen graafien osoitteet, jotka ladataan läpikäytäviin muihin graafeihin
IGNOREOTHERGRAPHWARNINGS = False # lokitetaanko virheet muissa, kuin prosessoitavassa graafissa
NORMALIZATION_FORM = "NFD" # käytetään UTF8-merkkien dekoodauksessa

YSO=Namespace('http://www.yso.fi/onto/yso/')
YSOMETA=Namespace('http://www.yso.fi/onto/yso-meta/')
YSOPAIKATGRAPH=Namespace("http://www.yso.fi/onto/yso-paikat/")
YSA=Namespace('http://www.yso.fi/onto/ysa/')
YSAMETA=Namespace('http://www.yso.fi/onto/ysa-meta/')
ALLARS=Namespace('http://www.yso.fi/onto/allars/')
ALLARSMETA=Namespace("http://www.yso.fi/onto/allars-meta/")
KOKO=Namespace('http://www.yso.fi/onto/koko/')
LCSH=Namespace("http://id.loc.gov/authorities/subjects/")
LCGF=Namespace("http://id.loc.gov/authorities/genreForms/")
RDAU=Namespace('http://rdaregistry.info/Elements/u/')
ISOTHES=Namespace('http://purl.org/iso25964/skos-thes#')
SKOSEXT=Namespace('http://purl.org/finnonto/schema/skosext#')
SLM=Namespace("http://urn.fi/URN:NBN:fi:au:slm:")
UDC=Namespace("http://udcdata.info/")
WIKIDATA=Namespace("http://www.wikidata.org/entity/")

LANGUAGES = {
    'fi': 'fin',
    'sv': 'swe',
    'en': 'eng',
    'de': 'ger',
    'et': 'est',
    'fr': 'fre',
    'it': 'ita',
    'ru': 'rus',
    'sme': 'sme', # pohjoissaame
    'sma': 'sma', # eteläsaame
    'smn': 'smn', # inarinsaame
    'sms': 'sms', # koltansaame
    'smj': 'smj', # luulajansaame
}

#LCSH mäpättävät 1xx-kentät
LCSH_1XX_FIELDS = ["100", "110", "111", "130", "147", "148", "150", "151", "155", "162", "180", "181", "182", "185"]

TRANSLATIONS = {
    SKOSEXT.partOf: {
        "fi": "osa kokonaisuutta/käsitettä",
        "sv": "är en del av",
        "en": "is part of"
    },
    "682iDEFAULT": {
        "fi": "Käytöstä poistetun termin korvaava termi",
        "sv": "Termen som ersättar den avlagda termen",
        "en": "Term replacing the deprecated term"
    },
    "688aCREATED": {
        "fi": "Luotu",
        "sv": "Skapad",
        "en": "Created"
    },
    "688aMODIFIED": {
        "fi": "Viimeksi muokattu",
        "sv": "Senast editerad",
        "en": "Last modified"
    }
}

# arvot tulevat osakentan $w 1. merkkipaikkaan
SEEALSOPROPS = {
    SKOS.broader : 'g',
    SKOS.narrower : 'h',
    SKOS.related : 'n',
    RDAU.P60683 : 'a',
    RDAU.P60686 : 'b',
    SKOSEXT.partOf : 'i',
    ISOTHES.broaderPartitive : "g",
    ISOTHES.narrowerPartitive : "h"
}

SORT_5XX_W_ORDER = {
    'g': '001',
    'h': '002',
    'n': '003',
    'i': '004',
    'a': '005',
    'b': '006'
}

# paikka 5, 'n' = uusi, 'c' = muuttunut/korjattu, d = poistettu (ei seuraajia), x = 1 seuraaja, s = >= 2 seuraajaa
LEADERNEW = '00000nz  a2200000n  4500'
LEADERCHANGED = '00000cz  a2200000n  4500'
LEADERDELETED0 = '00000dz  a2200000n  4500'
LEADERDELETED1 = '00000xz  a2200000n  4500'
LEADERDELETED2 = '00000sz  a2200000n  4500'

CATALOGCODES = '|n|anznnbabn           | ana      '
CATALOGCODES_NA = '|n|enznnbbbn           | ana      '

GROUPINGCLASSES = [ISOTHES.ConceptGroup, ISOTHES.ThesaurusArray, SKOS.Collection, YSOMETA.Hierarchy]

# tuple helpottamaan getValues-apufunktion arvojen käsittelyä
ValueProp = namedtuple("ValueProp", ['value', 'prop'])

# apufunktiot

def readCommandLineArguments():
    parser = argparse.ArgumentParser(description="Program for converting Finto SKOS-vocabularies into MARC (.mrcx).")
    parser.add_argument("-c", "--config",
        help="Config file location. The key/value pairs defined in the config file are overwritten with possible CLI key/value pairs.")
    parser.add_argument("-cs", "--config_section",
        help="Config section identifier. Set if vocabulary code is different from section identifier.")    
    parser.add_argument("-e", "--endpoint", help="Endpoint address to be used for querying linked concepts.")
    parser.add_argument("-eg", "--endpoint_graphs",
        help="The graphs one wants to query from the endpoint, e.g., http://www.yso.fi/onto/yso/. In case of multiple, separate them with space.")
    parser.add_argument("-ignoreOtherGraphWarnings", "--ignore_other_graph_warnings",
        help="Do you want ignore warnings produced whilst processing other graphs? Set this flag only if you want to ignore.", action="store_true")
    parser.add_argument("-i", "--input", help="Input file location, e.g., yso-skos.ttl")
    parser.add_argument("-if", "--input_format", help="Input file format. Default: turtle")
    parser.add_argument("-o", "--output", help="Output file name, e.g., yso.mrcx.")
    parser.add_argument("-vocId", "--vocabulary_code", help="MARC code used in tag 040 subfield f.", required=True)
    parser.add_argument("-lang", "--languages",
        help="The RDF language tag of the language one is willing to convert. In case of multiple, separate them with space.")
    parser.add_argument("-m", "--multilanguage_vocabulary", action='store_true',
        help="Is the vocabulary using language specified vocabulary codes, e.g., yso/fin? Set this flag only if it is.")
    parser.add_argument("-gc", "--grouping_classes",
        help="Types of classes not meant for describing/cataloging items in the vocabulary, e.g, hierarchical ones. In case of multiple, seperate them with space.")
    parser.add_argument("-log", "--log_file", help="Log file location.")
    parser.add_argument("-locDir", "--loc_directory",
        help="Library of Congress directory from which to look for and download to LoC marcxml files. One shall not set if one does not want LoC links.")
    parser.add_argument("-pv", "--pickle_vocabulary",
        help="File location for the vocabulary in Python's pickle format for faster execution. \
        If file's modification date is earlier than today, the file is overwritten. Else the vocabulary is loaded from this file.")
    parser.add_argument("-modificationDates", "--modification_dates",
        help="File location for pickle file, which contains latest modification dates for concepts (e. g. {'concept uri': 'YYYY-MM-DD'}) \
        The file is updated after new records are created, if keepModifiedAfter is left out of command line arguments") 
    parser.add_argument("-keepModifiedAfter", "--keep_modified_after",
        help="Create separate batch of MARC21 files for concepts modified after the date given (set in YYYY-MM-DD format).")
    parser.add_argument("-defaultCreationDate", "--default_creation_date",
        help="Default creation date (set in YYYY-MM-DD format) for a concept if it has not been declared explicitly. Default: " + DEFAULTCREATIONDATE)
    parser.add_argument("-keepDeprecatedAfter", "--keep_deprecated_after",
        help="Keep deprecated concepts deprecated after (not inclusive) the date given (set in YYYY-MM-DD format). Set to 'ALL' for no limits and 'NONE' to discard all.")
    parser.add_argument("-keepGroupingClasses", "--keep_grouping_classes",
        help="Keep grouping classes defined in config file.")
        
    args = parser.parse_args()
    return args

def readEndpointGraphs(settings): 
    sparql = SPARQLWrapper(settings.get("endpoint"))
    queryStart = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    CONSTRUCT {
        ?concept skos:prefLabel ?prefLabel .
        ?concept skos:inScheme ?inScheme .
        ?concept owl:deprecated ?deprecated .
        ?concept a ?types .
    }"""

    queryEnd = """
    WHERE {
      ?concept a skos:Concept .
      ?concept skos:prefLabel ?prefLabel .
      ?concept a ?types .

      OPTIONAL {?concept skos:inScheme ?inScheme .}
      OPTIONAL {?concept owl:deprecated ?deprecated .}
    }
    """
    
    queryFrom = ""
    ret = Graph()

    for endpointGraphIRI in settings.get("endpointGraphs").split(","):
        sparql.setQuery(queryStart + "\nFROM <" + str(endpointGraphIRI) + ">" + queryEnd)
        sparql.setMethod("GET")
        sparql.setTimeout(600)
        ret_length = len(ret)
        try:
            ret += sparql.query().convert()
            if ret_length == len(ret):
                logging.warning("Querying graph <" + str(endpointGraphIRI) +
                "> from endpoint " + settings.get("endpoint") +
                " returned 0 triples. Continuing.")
        except (SPARQLExceptions.SPARQLWrapperException) as err:
            logging.warning("Whilst querying endpoint " + settings.get("endpoint") + 
                  " for graph <" + str(endpointGraphIRI) +
                  "> the following error occurred: " + err.__class__.__name__ + ": " + err.msg + 
                  ". Skipping the graph.")
        except (urllib.error.HTTPError, urllib.error.URLError) as err:
            logging.warning("SPARQL endpoint not found in url " + settings.get("endpoint") +
                ". Skipping querying linked concepts.")
            break
        except socket.timeout as e:
            logging.warning("SPARQL endpoint now answering within timeout limit. " +
                "Skipping querying linked concepts.") 
    return ret

# funktio konfiguraatiotiedostoissa olevien monimutkaisten merkkijonojen lukemiseen ja siistimiseen
def readConfigVariable(string, separator=None):
    if separator:
        return [x.strip() for x in string.split(separator) if len(x.strip()) > 0]
    else:
        return string.strip()

# funktio åäöÅÄÖ-kirjainten muuttamiseksi takaisin UTF8-merkeiksi (decomposed -> composed)
def decomposedÅÄÖtoUnicodeCharacters(string):
    return (string.replace("A\u030a", "Å").replace("a\u030a", "å").
          replace("A\u0308", "Ä").replace("a\u0308", "ä").
          replace("O\u0308", "Ö").replace("o\u0308", "ö"))
    
def getValues(graph, target, props, language=None, literal_datatype=None):
    """Given a subject, get all values for a list of properties
    in the order in which those properties were defined.

    Args:
        graph (Graph): The graph from which to search for the properties of the target.
        target (URIRef|BNode): Concept.
        props (URIRef|sequence(URIRef)): Property or list of properties to search for.
        language (str, optional): Language of literals. Defaults to None (return all literals with languages).
            Set to empty string ("") for empty lang tag.
        literal_datatype (URIRef, optional): Datatype of datatyped literals. Defaults to None (return all literals with datatypes).
        
    Returns:
        list(TypeValue): List containing TypeValue namedtuples
            prop (URIRef): Matched property
            value (URIRef|BNode|Literal): For matched property, object value

    Raises:
        ValueError: If parameters do not respect the required types

    """
    if isinstance(props, URIRef):
        # cast to list in order to uniform code
        props = [props]
    
    if not (isinstance(target, URIRef) or isinstance(target, BNode)):
        raise ValueError("Parameter 'target' must be of type URIRef or BNode.")
    elif isinstance(props, str) or not isinstance(props, Sequence):
        raise ValueError(
            "Type of parameter 'props' must be a URIRef or sequence; got %s." % (type(props)))
    elif language is not None and not isinstance(language, str):
        raise ValueError("Parameter 'language' must be string if set.")
    elif literal_datatype is not None and not isinstance(literal_datatype, URIRef):
        raise ValueError("Parameter 'datatype' must be URIRef if set.") 
    
    v = []
    
    # setup the language filtering
    if language is not None:
        if language == '':  # we only want not language-tagged literals
            langfilter = lambda l: l.language == None
        else:
            langfilter = lambda l: l.language == language
    else:  # we don't care about language tags
        langfilter = lambda l: True
    
    # setup the datatype filtering
    if literal_datatype is not None:
        typefilter = lambda l: l.datatype == literal_datatype
    else:
        typefilter = lambda l: True
    
    for prop in props:
        if not isinstance(prop, URIRef):
            raise ValueError(
            "Types of properties must be URIRefs; got %s from property '%s'." % (type(prop), str(prop)))
        
        # values that pass restrictions are returned
        values = [l for l in graph.objects(target, prop) if 
                  (isinstance(l, URIRef) or isinstance(l, BNode)) or 
                  (l.datatype == None and langfilter(l)) or
                  (l.datatype != None and typefilter(l))
                 ]
        
        # loop through the values and add them to the list
        for val in values:
            v.append(ValueProp(value=val, prop=prop))
    return v

# apufunktio urlien parsimiseen merkkijonosta
# mietittävä uudelleen, jos näitä rakenteistetaan
def getURLs(string):
    urls = []
    for word in string:
        if len(word) < 10:
            continue
        if word[0] in ["(", "["]:
            word = word[1:-1]
        res = urllib.parse.urlparse(word)
        if res.scheme in ("http", "https") and \
            len(res.netloc) > 3 and "." in res.netloc:
            urls.append(word)
    return urls
    
class ConvertHTMLYSOATags(HTMLParser):
    '''
    Korvaa mahdolliset yso-linkit $a-osakenttämerkillä siten, että käytettävä termi
    jää näkyviin. Muu osa tekstistä on $i-osakentissä. Käytetään mm. kentässä 680
    
    TODO: Virheiden käsittely ja HTML-erikoisentiteettien/kommenttien käsittely
    '''
    merkkijono = ["$i"]
    in_a_yso = False
    ended_a_yso = False
    
    def initialize(self):
        self.merkkijono = ["$i"]
        self.in_a_yso = False
        self.ended_a_yso = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    link = attr[1]
                    if link.startswith(YSO):
                        self.in_a_yso = True
                        self.merkkijono[-1] = self.merkkijono[-1].rstrip()
                        self.merkkijono.append("$a")
                        return
        
        self.merkkijono.append("<" + tag)
        for attr in attrs:
            self.merkkijono.append(" " + attr[0] + "='" + attr[1] + "'")
        
        self.merkkijono.append(">")
        
    def handle_endtag(self, tag):
        if tag == "a" and self.in_a_yso:
            self.in_a_yso = False
            self.ended_a_yso = True
        else:
            self.merkkijono.append("</" + tag + ">")
        
        
    def handle_data(self, data):
        if self.ended_a_yso:
            self.merkkijono.append("$i")
            self.ended_a_yso = False
        
        # korjaa normaalien tekstistä löytyvien '<'-merkkien käsittely
        # TODO: Selvitä, tarvitseeko samanlainen korjaus tehdä myös alla
        # määritellyille funktioille
         
        if self.merkkijono[-1] != "$i" and self.merkkijono[-1] != "$a":
            self.merkkijono[-1] += data
        else:
            # tavallinen tapaus - lisätään vain käsitelty teksti uuteen osioon
            self.merkkijono.append(data)
        

    def handle_comment(self, data):
        self.merkkijono.append(data)

    def handle_entityref(self, name):
        # TODO: tarkista, mitä nämä esimerkkikoodit tekevät
        #c = chr(name2codepoint[name])
        self.merkkijono.append(name)

    def handle_charref(self, name):
        # TODO: tarkista, mitä nämä esimerkkikoodit tekevät
        #if name.startswith('x'):
        #    c = chr(int(name[1:], 16))
        #else:
        #    c = chr(int(name))
        self.merkkijono.append(name)

    def handle_decl(self, data):
        self.merkkijono.append(data)

# pääfunktio
def convert(cs, vocabulary_name, language, g, g2):
    # kääntää graafin (g) kielellä (language) ConfigParser-sektion (cs) ohjeiden mukaisesti MARCXML-muotoon
    # g2 sisältää vieraat graafit (poislukien mahdolliset lcsh & lcgf-viitteet), joista etsitään
    # käytettyjä termejä 7XX kenttiin
    # vocabulary_name-parametriä tarvitaan tunnistamaan, että kyseessä YSO-paikat-ontolohgia, joihin tehdään 670-kenttiä
 
    vocId = cs.get("vocabulary_code")
    
    # variable for a bit complicated constants and casting/converting them to appropiate types
    helper_variables = {
        "vocCode" : (cs.get("vocabulary_code") + "/" + LANGUAGES[language] \
            if cs.getboolean("multilanguage", fallback=False) \
            else vocId),
        "groupingClasses" : [URIRef(x) for x in cs.get("groupingClasses", fallback=",".join(GROUPINGCLASSES)).split(",")],
        "groupingClassesDefault" : [URIRef(x) for x in cs.parser.get("DEFAULT", "groupingClasses", fallback=",".join(GROUPINGCLASSES)).split(",")],
        'modificationDates': cs.get("modificationDates", fallback=None),
        'keepModified' : cs.get("keepModifiedAfter", fallback=None),
        'keepDeprecated' : cs.get("keepDeprecatedAfter", fallback=KEEPDEPRECATEDAFTER).lower() != "none",
        'keepGroupingClasses' : cs.getboolean("keepGroupingClasses", fallback=False),
        'write688created' : cs.get("defaultCreationDate", fallback=None) != None,
        'defaultOutputFileName' : "yso2marc-" + cs.name.lower() + "-" + language + ".mrcx"
    }

    if helper_variables['keepModified']:
        helper_variables['keepModifiedLimit'] = False \
        if cs.get("keepModifiedAfter", fallback=KEEPMODIFIEDAFTER).lower() == "all" \
        else datetime.date(datetime.strptime(cs.get("keepModifiedAfter"), "%Y-%m-%d"))

    if helper_variables['keepDeprecated']:   
        helper_variables['keepDeprecatedLimit'] = False \
        if cs.get("keepDeprecatedAfter", fallback=KEEPDEPRECATEDAFTER).lower() == "all" \
        else datetime.date(datetime.strptime(cs.get("keepDeprecatedAfter"), "%Y-%m-%d"))

    if cs.get("output", fallback=None):
        parts = cs.get("languages").split(",")
        if len(parts) > 1:
            output = cs.get("output")
            if len(output.split(".")) > 1:
                helper_variables["outputFileName"] = ".".join(output.split(".")[:-1]) + "-" + language + "." + output.split(".")[-1]
            else:
                helper_variables["outputFileName"] = output + "-" + language
    if not "outputFileName" in helper_variables:
        helper_variables["outputFileName"] = cs.get("output", fallback=helper_variables["defaultOutputFileName"])

    #modified_dates on dict-objekti, joka sisältää tietueen id:n avaimena ja 
    #arvona tuplen, jossa on tietueen viimeinen muokkauspäivämäärä ja tietueen sisältö MD5-tiivisteenä
    if helper_variables['modificationDates']:
        if os.path.isfile(helper_variables['modificationDates']):
            with open(helper_variables['modificationDates'], 'rb') as pickle_file: 
                try:
                    modified_dates = pickle.load(pickle_file)
                except EOFError:
                    logging.error("The file %s for modification dates is empty "%helper_variables['modificationDates'])
                    sys.exit(2)
        else:
            modified_dates = {}

    logging.info("Processing vocabulary with vocabulary code '%s' in language '%s'" % (vocId, language))
    incrementor = 0
    deprecated_counter = 0
    writer_records_counter = 0
    ysoATagParser = ConvertHTMLYSOATags()
    ET_namespaces = {"marcxml": "http://www.loc.gov/MARC21/slim",
                     "atom": "http://www.w3.org/2005/Atom"}

    handle = open(cs.get("output", fallback=helper_variables["defaultOutputFileName"]), "wb")
    writer = XMLWriter(handle)
    
    pref_labels = set()
    for conc in g.subjects(RDF.type, SKOS.Concept):
        pref_label = g.preferredLabel(conc, lang=language)
        if pref_label:
            pref_labels.add(str(pref_label[0][1]).lower())

    concs = []
    
    

    # haetaan Kongressin kirjaston päivitykset viimeisen viikon ajalta, 
    # jos ohjelmaa ei ole ajettu aiemmin samana päivänä
    loc_update_dict = {}
    update_loc_concepts = True
    loc_update_file = os.path.join(cs.get("locDirectory"), "updates.pkl")
    if os.path.exists(loc_update_file):
        timestamp = os.path.getmtime(loc_update_file)
        file_date = date.fromtimestamp(timestamp)
        if file_date == date.today():
            update_loc_concepts = False
        with open(loc_update_file, 'rb') as input_file: 
            try:     
                loc_update_dict = pickle.load(input_file)
            except EOFError:
                logging.error("EOFError in "%loc_update_file)

    limit_date = date.today() - timedelta(days=7)
    lc_namespaces = [LCGF, LCSH]
    feed_prefix = "feed/"
    for ns in lc_namespaces:
        limit_reached = False
        for idx in range(1,100):
            if limit_reached:
                break
            file_path = os.path.join(str(ns), feed_prefix, str(idx))
            try:
                with urllib.request.urlopen(file_path, timeout=5) as atom_xml:
                    recordNode = ET.parse(atom_xml)
                    root = recordNode.getroot()
                    for entry in root.findall("atom:entry", ET_namespaces):
                        label = None
                        for updated in entry.findall("atom:updated", ET_namespaces):
                            updated = datetime.strptime(updated.text[:10], "%Y-%m-%d").date()
                            if updated >= limit_date:
                                for link in entry.findall("atom:link", ET_namespaces):
                                    if not 'type' in link.attrib:
                                        uri = link.attrib['href']
                                        if uri in loc_update_dict:
                                            if loc_update_dict[uri]['date'] < updated:
                                                loc_update_dict[uri]['date'] = updated
                                                loc_update_dict[uri]['updatable'] = True
                            else:
                                limit_reached = True
            except ET.ParseError as e:
                logging.warning("Failed to parse Library of Congress update feed")
        if not limit_reached:
            logging.warning("More than 10 000 updates in Library of Congress feed %s"%ns)
        
    if helper_variables['keepModified']:
        # käydään läpi vain muuttuneet käsitteet
        for uri in modified_dates:
            if modified_dates[uri][0] >= helper_variables['keepModifiedLimit']:  
                concs.append(URIRef(uri))
    else:    
        concs = g.subjects(RDF.type, SKOS.Concept)

    for concept in sorted(concs):
        incrementor += 1
        if incrementor % 1000 == 0:
            logging.info("Processing %sth concept" % (incrementor))
        
        # skipataan deprekoidut, jos niitä ei haluta mukaan. Jos haetaan muuttuneita käsitteitä, tulostetaan kaikki
        if not helper_variables['keepModified'] and (concept, OWL.deprecated, Literal(True)) in g:
            if not helper_variables['keepDeprecated']:
                deprecated_counter += 1
                continue
        
        #skipataan ryhmittelevät käsitteet
        if not helper_variables['keepGroupingClasses']:
            if any (conceptType in helper_variables["groupingClasses"] for conceptType in g.objects(concept, RDF.type)):
                continue
        
        rec = Record()   
        deprecatedString = ""

        loc_concept_downloaded = False

        # dct:modified -> 005 EI TULOSTETA, 688 
        # tutkitaan, onko käsite muuttunut vai alkuperäinen
        # ja valitaan leader sen perusteella
        mod = g.value(concept, DCT.modified, None)
        if mod is None:
            rec.leader = cs.get("leaderNew", fallback=LEADERNEW)
        else:
            rec.leader = cs.get("leaderChanged", fallback=LEADERCHANGED)
            modified = mod.toPython() # datetime.date or datetime.datetime object
            if not type(modified) in [date, datetime]:
                logging.error("Modification date invalid in concept %s "%concept)
                modified = None
  
        # dct:created -> 008
        crt = g.value(concept, DCT.created, None)
        if crt is None:
            created = datetime.date(datetime.strptime(cs.get("defaultCreationDate", fallback=DEFAULTCREATIONDATE), "%Y-%m-%d"))
        else:
            created = crt.toPython() # datetime.date or datetime.datetime object
            if not type(created) in [date, datetime]:
                logging.error("Creation date invalid in concept %s "%concept)
                created = datetime.date(datetime.strptime(cs.get("defaultCreationDate", fallback=DEFAULTCREATIONDATE), "%Y-%m-%d"))
        
        code = cs.get("catalogCodes", fallback=CATALOGCODES)
        
        # asetetaan kuvailukielto käsitteelle, jos tyypiä ryhmittelevä käsite
        for conceptType in g.objects(concept, RDF.type):
            if conceptType in helper_variables["groupingClasses"]:
                code = cs.get("catalogCodes_na", fallback=CATALOGCODES_NA)
                break
        # jos kyseessä on poistettu käsite, asetetaan leaderit ja koodit asianmukaisesti
        if (concept, OWL.deprecated, Literal(True)) in g:
            replacers = sorted(g.objects(concept, DCT.isReplacedBy))
            if len(replacers) == 0:
                rec.leader = cs.get("leaderDeleted0", fallback=LEADERDELETED0)
            elif len(replacers) == 1:
                rec.leader = cs.get("leaderDeleted1", fallback=LEADERDELETED1)
            else:
                rec.leader = cs.get("leaderDeleted2", fallback=LEADERDELETED2)
             
            code = cs.get("catalogCodes_na", fallback=CATALOGCODES_NA)
            
            # jos on lisäksi asetettu jokin päivämäärärajoite
            if helper_variables['keepDeprecatedLimit']:
                # mikäli scopeNote puuttuu, poistettu tulkitaan uudeksi poistoksi ja sen tulkitaan
                # "ylittävän" asetetun limitin eli jää tulosjoukkoon
                for valueProp in sorted(getValues(g, concept, SKOS.scopeNote, language=""),
                                                           key=lambda o: str(o.value)):    
                    if valueProp.value.startswith("deprecated on"):
                        deprecatedString = str(valueProp.value)
                        break
                if deprecatedString:
                    deprecatedDateString = deprecatedString.split(" ")[-1]
                    try:
                        # yritetään parsia päivämäärä kahdessa eri formaatissa
                        deprecatedDate = datetime.date(datetime.strptime(deprecatedDateString, "%d.%m.%Y"))
                        if helper_variables['keepDeprecatedLimit'] > deprecatedDate:
                            deprecated_counter += 1
                            continue # skipataan ennen vanhentamisrajaa vanhennetut termit
                    except ValueError:
                        try:
                            deprecatedDate = datetime.date(datetime.strptime(deprecatedDateString, "%Y-%m-%d"))
                            if helper_variables['keepDeprecatedLimit'] > deprecatedDate:
                                deprecated_counter += 1
                                continue # skipataan ennen vanhentamisrajaa vanhennetut termit
                        except ValueError:
                            logging.warning("Converting deprecated date failed for concept %s. Proceeding." %
                          (concept))
        
        if not created and not helper_variables["write688created"]:
            logging.warning("No explicit creation date defined for concept %s. Using default value '%s' for character positions 00-05 in tag 008." % (
                concept, datetime.date(datetime.strptime(DEFAULTCREATIONDATE, "%Y-%m-%d")).strftime('%y%m%d')))

        rec.add_field(
            Field(
                tag='008',
                data=created.strftime('%y%m%d') + code
            )
        )
        
        # 024 muut standarditunnukset - käsitteen URI tallennetaan tähän
        rec.add_field(
            Field(
                tag='024',
                indicators = ['7', ' '],
                subfields = [
                    'a', concept,
                    '2', "uri"
                ]
            )
        )
        
        # 034 paikkojen koordinaatit - yso-paikat?
        # 035 yso-tietueen numero?
        
        # 040 luetteloiva organisaatio
        rec.add_field(
            Field(
                tag='040',
                indicators = [' ', ' '],
                subfields = [
                    'a', cs.get("creatorAgency", fallback=CREATOR_AGENCY),
                    'b', LANGUAGES[language],
                    'f', helper_variables["vocCode"]
                ]
            )
        )
        # 043 - ysopaikat, käytetäänkö
        # http://marc21.kansalliskirjasto.fi/aukt/01X-09X.htm#043
        
        # 045 - yso-ajanjaksot, käytetäänkö
        # http://marc21.kansalliskirjasto.fi/aukt/01X-09X.htm#045
        
        # 046 - erikoiskoodatut ajanjaksot? 
        
        # 052 - maantieteellinen luokitus
        # 7#$a(480)$2udc$0http://udcdata.info/004604
        # jos 151 kaytossa, pitaisiko kayttaa? Jarmo: UDC-luokitus, Suomi "(480)"
        
        #ConceptGroup / skos:member -> 065 yso-aihealuekoodi
        # vain siina tapauksessa, kun ne halutaan mukaan Asteriin
        # jos luokkanumeroa ei löydy, ei tulosteta
        # vain jos vocId = "yso", tehdään tämä
        if vocId == "yso":
            for group in sorted(g.subjects(SKOS.member, concept)):
                if not helper_variables['keepDeprecated'] and \
                (group, OWL.deprecated, Literal(True)) in g:
                    continue # skip deprecated group concepts
                if (group, RDF.type, ISOTHES.ConceptGroup) not in g:
                    continue
                # ryhmätunnuksen ekstraktointi: yritä ensin kaivaa skos:notationista, muuten prefLabelista
                groupno = g.value(group, SKOS.notation, None)
                if groupno is None:
                    valueProps = sorted(getValues(g, group, SKOS.prefLabel, language=language),
                                       key=lambda o: o.value)
                    if len(valueProps) == 0: 
                        logging.warning("Could not find preflabel for target %s in language: %s. Skipping property %s target for concept %s." %
                          (group, language, SKOS.member, concept))
                        continue
                    elif len(valueProps) != 1:
                        logging.warning("Multiple prefLabels detected for concept %s in language %s. Taking the first only." %
                          (concept, language)) 
                    groupname = str(valueProps[0].value)
                    try:
                        groupno = str(groupname[0:groupname.index(" ")])
                        groupname = str(groupname[len(groupno) + 1:])
                    except ValueError:
                        logging.warning("Tried to parse group number for group %s from concept %s in language %s but failed." %
                          (group, valueProps[0].value, language))
                        continue

                rec.add_field(
                    Field(
                           tag='065',
                           indicators = [' ', ' '],
                           subfields = [
                               'a', groupno,
                               'c', decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, groupname)),
                               #'c', groupname,
                               '0', group,
                               '2', vocId
                           ]
                    )
                )
        
        # 080 - UDK-luokka. Asiasanaan liittyva UDK-luokka
        
        # 147 Tapahtuman nimi. Ei kayteta?
        
        # 148 Aikaa merkitseva termi. Selvitetaan.
        
        # skos:prefLabel -> 150 aihetta ilmaiseva termi
        valueProps = sorted(getValues(g, concept, SKOS.prefLabel, language=language),
                                   key=lambda o: o.value)
        if len(valueProps) == 0:
            logging.warning("Could not find preflabel for concept %s in language %s. Skipping the whole concept." %
              (concept, language))
            continue
        elif len(valueProps) != 1:
            logging.warning("Multiple prefLabels detected for concept %s in language %s. Choosing the first." %
                  (concept, language)) 
            
        # tunnistetaan käsitteen tyyppi (aika, yleinen, paikka, genre)
        # -> 148, 150, 151, 155, 162
        # tukee tällä hetkellä tavallisia asiasanoja (150), YSO-paikkoja (151) & SLM:ää (155)
        tag = "150"
        if (concept, SKOS.inScheme, YSO.places) in g:
            tag = "151"
        elif vocId == "slm":
            tag = "155"

        rec.add_field(
            Field(
                tag=tag,
                indicators = [' ', ' '],
                subfields=[
                            'a', decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(valueProps[0].value)))
                            #'a', str(valueProps[0].value)
                          ]
            )
        )
        
        # skos:altLabel -> 447, 448, 450, 451, 455
        # 450 katso-viittaus
        # poistetaan toisteiset skos:hiddenLabelit
        # jätetään tuottamatta 45X-kentät, jotka ovat toisessa käsitteessä 15X-kenttinä, paitsi altLabelein kohdalla
        # OLETUS: poistettujen käsitteiden seuraajien tietoihin EI merkitä poistetun käsitteen
        # skos:prefLabelia näihin kenttiin, sillä sen oletetaan jo olevan skos:altLabelina kun siihen
        # on haluttu viitata vanhalla muodolla
        seen_values = set()
        
        for valueProp in sorted(getValues(g, concept, [SKOS.altLabel, YSOMETA.singularPrefLabel,
                                                YSOMETA.singularAltLabel, SKOS.hiddenLabel], language=language),
                                key=lambda o: str(o.value)):
            #  singularPrefLabel, singularAltLabel ja hiddenLabel jätetään pois 45X-kentistä,
            #  jos ne kirjainkoosta riippumatta ovat jossain 15X-kentässä
            if valueProp.prop != SKOS.altLabel and str(valueProp.value.lower()) in pref_labels:
                continue
            if valueProp.prop == SKOS.hiddenLabel:
                if str(valueProp.value) in seen_values:
                    continue            
            seen_values.add(str(valueProp.value))
            
            tag = "450"
            if (concept, SKOS.inScheme, YSO.places) in g:
                tag = "451"
            elif vocId == "slm":
                tag = "455"

            rec.add_field(
                Field(
                    tag = tag,
                    indicators = [' ', ' '],
                    subfields = [
                        'a', decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(valueProp.value)))
                        #'a', str(valueProp.value)
                    ]
                )
            )
        
        # broader/narrower/related/successor/predecessor/skosext:partOf
        # -> 550 "katso myos" viittaus
        # HUOM: Objektit vain olioita
        # TODO: ysoon lisätään myöhemmin partOf-suhteiden käänteinen suhde
        # TODO: useat erityyppiset i-kentät eivät toimi tällä hetkellä
        fields = list()

        for prop, wval in SEEALSOPROPS.items():
            for target in sorted(g.objects(concept, prop)):
                if not helper_variables['keepDeprecated'] and \
                (target, OWL.deprecated, Literal(True)) in g:
                    continue # skip deprecated concepts
                
                valueProps = getValues(g, target, SKOS.prefLabel, language=language)
                if len(valueProps) == 0:
                    logging.warning("Could not find preflabel for target %s in language %s. Skipping property %s target for concept %s." %
                      (target, language, prop, concept))
                    continue
                elif len(valueProps) != 1:
                    logging.warning("Multiple prefLabels detected for target %s in language %s. Choosing the first." %
                          (target, language)) 
                label = valueProps[0].value
                
                tag = "550" # alustetaan 550-arvoon
                if (target, SKOS.inScheme, YSO.places) in g:
                    tag = "551"
                elif vocId == "slm":
                    tag = "555"
                
                subfields = []
                
                #TODO: YSOn mahdolliset SKOSEXT-ominaisuudet?
                #TODO: tarkista tämä YSOn tietomalliuudistusta varten
                if wval == "i":
                    if (target, SKOS.inScheme, YSO.places) in g:
                        if prop == SKOSEXT.partOf:
                            subfields.extend(('w', 'g'))
                        elif prop == SKOSEXT.hasPart:
                            subfields.extend(('w', 'h'))
                        else:
                            subfields.extend(('w', wval,
                                     "i", TRANSLATIONS[prop][language]
                                    ))
                    else:
                        subfields.extend(('w', wval,
                                     "i", TRANSLATIONS[prop][language]
                                    ))
                else:
                    subfields.extend(('w', wval))
                    
                subfields.extend(('a', 
                                  decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(label)))
                                  #str(label)
                                 ))
                subfields.extend(('0', target))
                # yso-paikoissa on sekä ISOTHES.broaderPartitive, että
                # SKOS.broader redundanttina, 
                # samoin ISOTHES.narrowerPartitive - SKOS.narrower
                # Otetaan kuitenkin toistaiseksi varmuudeksi kummatkin konversioon mukaan 
                # ja poistetaan tuplakentät tässä
                see_also_field = Field(
                    tag = tag,
                    indicators = [' ', ' '],
                    subfields = subfields
                    )
                if not any(str(see_also_field) == str(f) for f in fields):
                    fields.append(see_also_field)
        # järjestä 5XX-kentät ja lisää ne tietueeseen
        for sorted_field in sorted(fields, key=lambda o: (
            o.tag, 
            SORT_5XX_W_ORDER[o.get_subfields("w")[0]] if o.get_subfields("w") else "999",
            o.get_subfields('a')[0]
            )):
            rec.add_field(sorted_field)
        
        # TODO: JS: laitetaan 667 kenttään SLM:n käsiteskeemat jokaiselle käsitteelle
        
        # dc:source -> 670 kasitteen tai kuvauksen lahde
        # tulostetaan vain yso-paikkojen kohdalla url, joka closeMatchissa 
        # haetaan ensin lähdetiedoista Maanmittauslaitoksen paikannimirekisterin tyyppitieto
        # liitetään se paikkatieto-URIin closeMatchissa, jos kumpiakin on vain yksi 
        if vocabulary_name == "YSO-PAIKAT":
            subfield_list = []
            subfield_b = None
            geographical_types = set()
            for valueProp in sorted(getValues(g, concept, DC.source, language=language), key=lambda o: str(o.value)):
                if "Maanmittauslaitoksen paikannimirekisteri; " in valueProp.value:
                    geographical_type = valueProp.value.split("; ")
                    if len(geographical_type) > 1:
                        geographical_type = geographical_type[1]
                        geographical_types.add(geographical_type)
                elif not any(substring in valueProp.value for substring in ["Wikidata", 
                                                                            "Sijaintitietojen lähde", 
                                                                            "Källa för positionsinformation"]):
                    # dc:sourcessa on ollut myös URLeja. Siivotaan ne tässä pois
                    if not valueProp.value.startswith("http"):
                        subfield_list.append([
                            'a', decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, valueProp.value))
                        ])
            if len(geographical_types) == 1:
                subfield_b = next(iter(geographical_types))
            # ruotsinkieliseen sanastoon ei laiteta paikanninimirekisterilinkkejä, koska ruotsinkielinen selite puuttuu
            for valueProp in sorted(getValues(g, concept, SKOS.closeMatch, language=language), key=lambda o: str(o.value)):  
                if "http://paikkatiedot.fi" in valueProp.value:
                    if subfield_b:
                        subfield_list.append([
                            'a', 'Maanmittauslaitoksen paikannimirekisteri',
                            'b', subfield_b,
                            'u', valueProp.value
                        ])

            for subfields in subfield_list:
                rec.add_field(
                    Field(
                        tag='670',
                        indicators = [' ', ' '],
                        subfields = subfields
                    )
                )
        # skos:definition -> 677 huomautus määritelmästä
        # määritelmän lähde voidaan merkitä osakenttään $v
        # sitä varten tulee sopia tavasta merkitä tämä lähde, jotta
        # se voidaan koneellisesti erottaa tekstistä
        # JS ehdottaa: jos tekstissä on merkkijono ". Lähde: ",
        # kaikki sen perässä oleva teksti merkitään osakenttään $v
        # entä jos linkki lähteen perässä?
        # JS ehdottaa: linkki aivan viimeisenä sanana
        # 4.5.2018 - palataan myöhemmin tähän
        # 6.8.2018 - ei vielä käsitelty
        # 5.9.2018 - määritelmän lähde tulee määritelmän jälkeen kahdella tavuviivalla (--) erotettuna
        # jätetään toistaiseksi paikalleen (13 kpl)
        for valueProp in sorted(getValues(g, concept, SKOS.definition, language=language),
                                key=lambda o: str(o.value)):
            subfields = [
                'a', 
                decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(valueProp.value)))
                #str(valueProp.value)
            ]
            # TODO: linkkien koodaus tarkistetaan/tehdään myöhemmin
            #urls = getURLs(valueProp.value)
            #for url in urls:
            #    subfields.append("u")
            #    subfields.append(url)
                
            rec.add_field(
                Field(
                    tag='677',
                    indicators = [' ', ' '],
                    subfields = subfields
                )
            )
        
        # skos:note -> 680 yleinen huomautus, julkinen
        for valueProp in sorted(getValues(g, concept, [SKOS.note, SKOS.scopeNote, SKOS.example], language=language),
                                key=lambda o: str(o.value)):
            
            ysoATagParser.initialize()
            ysoATagParser.feed(valueProp.value)
            
            if len(ysoATagParser.merkkijono)%2 == 1:
                logging.warning("Parsing the property %s for concept %s into seperate subfields failed. Continuing with complete value." % (valueProp.prop, concept))
                subfieldCodeValuePair = ("i", valueProp.value.strip())
                if len(subfieldCodeValuePair[1]) == 0:
                    subfieldCodeValuePair = []
            else:
                subfieldCodeValuePair = [[x[1], ysoATagParser.merkkijono[ind+1].strip()] for (ind,x) in enumerate(ysoATagParser.merkkijono) if ind%2 == 0]
                # poistetaan viimeinen i-tägi, jos se on vain 1 merkin mittainen (loppupisteet)
                if subfieldCodeValuePair[-1][0] == "i" and len(subfieldCodeValuePair[-1][1]) <= 1 and len(subfieldCodeValuePair) > 1:
                    subfieldCodeValuePair[-2][1] = subfieldCodeValuePair[-2][1] + subfieldCodeValuePair[-1][1]
                    subfieldCodeValuePair = subfieldCodeValuePair[:-1]
            
            subfield_values = []
            
            for subfield in subfieldCodeValuePair:
                subfield_values.extend(
                    (subfield[0], decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, subfield[1])))
                    #(subfield[0], subfield[1])
                )
            
            rec.add_field(
                Field(
                    tag='680',
                    indicators = [' ', ' '],
                    subfields = subfield_values
                )
            )
        # mahdollinen deprekointitieto lisätään erikseen
        if deprecatedString:
            rec.add_field(
                Field(
                    tag='680',
                    indicators = [' ', ' '],
                    subfields = ['i', deprecatedString]
                )
            )
        # owl:deprecated -> 682 Huomautus poistetusta otsikkomuodosta (ei toistettava)
        # Ohjaus uuteen/uusiin käsitteisiin
        # seuraaja-suhde
        # a-kenttään seuraajan preflabel, 0-kenttään URI, i selite
        # TODO: onko seuraajaa vai ei, lisäksi mietittävä deprekoidun käsitteen
        # tyyppi (onko hierarkia jne.). Deprekaattorin huomautustekstiä kehitettävä
        # (kentät mietittävä uudelleen - EI skos:scopeNote kuten nyt on 4.5.2018)
        # 2018-12-05 Huomattiin, että ei ole toistettavissa --> ongelma useiden korvaajien tapauksessa ($0)
        # kongressin kirjasto on työstämässä parhaista käytännöistä $0-kentän toistettavuudesta vielä tämän vuoden aikana
        # päätettiin jättää tässä vaiheessa $0-kentät kokonaan pois
        if (concept, OWL.deprecated, Literal(True)) in g:
            target = None
            labels = []
            for target in sorted(g.objects(concept, DCT.isReplacedBy)):
                if not helper_variables['keepDeprecated'] and \
                (target, OWL.deprecated, Literal(True)) in g:
                    continue # skip deprecated concepts
                    
                valueProps = sorted(getValues(g, target, SKOS.prefLabel, language=language), key=lambda o: str(o.value))
                replacedByURIRef = URIRef(target)
                if len(valueProps) > 1:
                    logging.warning("Multiple prefLabels detected for target %s in language %s. Choosing the first." %
                      (target, language)) 
                elif len(valueProps) == 0:
                    logging.warning("Could not find preflabel for target %s in language: %s. Skipping property %s target for concept %s." %
                          (target, language, DCT.isReplacedBy, concept))
                    continue
                label = valueProps[0].value
                labels.append(valueProps[0].value)
                #rec.add_field(
                #    Field(
                #        tag = '682',
                #        indicators = [' ', ' '],
                #        subfields = [
                #            'i', TRANSLATIONS["682iDEFAULT"][language],
                #            'a', decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(label))),
                #            #'a', str(label),
                #            '0', target
                #        ]
                #    )
                #)
            if len(labels) > 0:
                subfield_values = ['i', TRANSLATIONS["682iDEFAULT"][language]]

                for label in labels[:-1]:
                    subfield_values.extend(('a', 
                                      decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(label) + ","))
                                      #str(label)
                                     ))
                subfield_values.extend(('a', 
                                      decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(labels[-1])))
                                      #str(label)
                                     ))
                #subfield_values.extend(('0', target)) #TODO: seurataan kongressin kirjaston tulevia ohjeistuksia
                rec.add_field(
                    Field(
                        tag='682',
                        indicators = [' ', ' '],
                        subfields = subfield_values
                    )
                )
        
        if helper_variables["write688created"]:
            rec.add_field(
                Field(
                    tag = '688',
                    indicators = [' ', ' '],
                    subfields = [
                        'a',  TRANSLATIONS["688aCREATED"][language] + ": " + created.strftime('%Y-%m-%d')
                    ]
                )
            )
        
        if mod and modified:
            rec.add_field(
                Field(
                    tag = '688',
                    indicators = [' ', ' '],
                    subfields = [
                        'a', TRANSLATIONS["688aMODIFIED"][language] + ": " + modified.strftime('%Y-%m-%d')
                    ]
                )
            )
                  
        # all skos:match*es -> 7XX linkkikenttiin
        # halutaan linkit kaikkiin kieliversioihin
        # lisäksi saman sanaston erikieliset preflabelit tulevat tänne
        # graafit on haettu etukäteen ohjelman muistiin ohjelman alussa
        # 750 $a label, $4 relaatiotyyppi, $2 sanastolahde, $0 uri
        # miten $w? JS: ei oteta mukaan ollenkaan
        # 2.5.2018-kokouksessa päätettiin, että DCT.spatialia ei käännetä
        # MARC-muotoon
        # 13.8.2018 LCSH/LCGF käsitellään erikseen; niille on tehty oma kansio, joka
        # on tallennettu locDirectory-muuttujaan. Puuttuvat loc-linkit haetaan
        # dynaamisesti tarvittaessa ja lisätään kansioon, josta ne sitten luetaan ohjelman käyttöön
        valueProps = getValues(g, concept, [SKOS.prefLabel, SKOS.exactMatch, SKOS.closeMatch,
                                 SKOS.broadMatch, SKOS.narrowMatch, 
                                 SKOS.relatedMatch])
        fields = list() # kerätään kentät tähän muuttujaan, joka sitten lopuksi järjestetään
       
        for valueProp in valueProps:
            if valueProp.prop == SKOS.prefLabel:
                # suodatetaan samankieliset, jotka menivät jo 1xx-kenttiin
                # valueProp.value sisältää tässä poikkeuksellisesti jo halutun literaalin
                # (vrt. kun muissa on solmu)
                if valueProp.value.language == language:
                    continue
                matchURIRef = URIRef(concept)
            else:
                # tehdään osumasta URIRef 
                matchURIRef = URIRef(valueProp.value)
                #if not helper_variables['keepDeprecated'] and \
                if (matchURIRef, OWL.deprecated, Literal(True)) in g2:
                    # skip deprecated matches
                    # 19.12.2018 käyty keskustelua tästä - päätetty tässä vaiheessa
                    # olla seuraamatta dct:isReplacedBy-suhteita ja lisäämättä näitä
                    # TODO-listalle?
                    continue 
                # 27.12.2018 pitäisikö tarkistaa myös groupingClassesien varalta?
                # Ratkaisu: Ei - nämä on merkitty omissa tietueissaan ei-käytettäviksi

            second_indicator = "7"
            tag = "750"
            loc_object = None 
            
            if (matchURIRef, SKOS.inScheme, YSO.places) in g2 or \
            (matchURIRef, SKOS.inScheme, YSO.places) in g: #or matchType == DCT.spatial:
                tag = "751"
            # TODO: nimetyt graafit, kohdista kyselyt niihin?
            # Comment: if we want to direct queries to spesific graphs, one per vocab,
            # that graph needs to be selected here based on the void:uriSpace
            
            sub0 = concept
            sub2 = ""
            if matchURIRef.startswith(LCSH):
                second_indicator = "0"
                loc_object = {"prefix": str(LCSH), "id": matchURIRef.split("/")[-1]}
            elif matchURIRef.startswith(LCGF):
                sub2 = "lcgft" 
                loc_object = {"prefix": str(LCGF), "id": matchURIRef.split("/")[-1]}
                
            elif matchURIRef.startswith(ALLARS):
                if (matchURIRef, RDF.type, ALLARSMETA.GeographicalConcept) in g2: #or matchType == DCT.spatial:
                    tag = "751"
                sub2 = "allars"
                #continue
            elif matchURIRef.startswith(KOKO):
                continue # skip KOKO concepts
            elif matchURIRef.startswith(SLM):
                tag = "755"
                sub2 = "slm"
                
            elif matchURIRef.startswith(YSA):
                if (matchURIRef, RDF.type, YSAMETA.GeographicalConcept) in g2: #or matchType == DCT.spatial:
                    tag = "751"
                sub2 = "ysa"
                #continue
            elif matchURIRef.startswith(YSO):
                sub2 = "yso"
            else:
                second_indicator = "4"
                if not cs.getboolean("ignoreOtherGraphWarnings", fallback=IGNOREOTHERGRAPHWARNINGS):
                    logging.warning("Matched target %s did not belong to any known vocabulary" % (str(matchURIRef)))
                    # do not put subfield 2 in this case
            
            if not ((matchURIRef, None, None) in g or
                (matchURIRef, None, None) in g2):
                if not loc_object and not cs.getboolean("ignoreOtherGraphWarnings", fallback=IGNOREOTHERGRAPHWARNINGS): 
                    logging.warning("Matched target %s did not belong to any known vocabulary. Skipping." % (str(matchURIRef)))
                    continue
            
            sub4 = ""
            if valueProp.prop == SKOS.broadMatch:
                sub4 = "BM"
            elif valueProp.prop == SKOS.narrowMatch:
                sub4 = "NM"
            elif valueProp.prop == SKOS.exactMatch:
                sub4 = "EQ"
            elif valueProp.prop == SKOS.prefLabel:
                sub4 = "EQ"

                # kovakoodattu yso ja slm - muuten niiden tulisi olla jossain globaalissa muuttujassa
                if sub2 == "yso" or sub2 == "slm" or cs.getboolean("multilanguage", fallback=False):
                    sub2 = sub2 + "/" + LANGUAGES[valueProp.value.language]
                    # englanninkielisten YSO-paikkojen prefLabelit ovat Wikidatasta peräisin
                    if tag == "751" and LANGUAGES[valueProp.value.language] in ["en", "eng"]:
                        wdEntities = []
                        closeMatches = getValues(g, concept, [SKOS.closeMatch])
                        for closeMatch in closeMatches:
                            if closeMatch.value.startswith(WIKIDATA):
                                wdEntities.append(URIRef(closeMatch.value))
                        if len(wdEntities) == 1:
                            sub0 = wdEntities[0]
                            sub2 = "wikidata"
                            sub4 = "~EQ"
                        else:
                            sub2 = None
                            sub4 = None
                if sub2 and sub4:
                    fields.append(
                        Field(
                            tag=tag,
                            indicators = [' ', second_indicator],
                            subfields = [
                                'a', decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(valueProp.value))),
                                '4', sub4,
                                '2', sub2,
                                '0', sub0
                            ]
                        )
                    )
                continue
            elif valueProp.prop == SKOS.closeMatch:
                sub4 = "~EQ"
            else:
                sub4 = "RM"
                
            # library of congress -viitteet käsitellään erikseen
            if loc_object:
                if cs.get("locDirectory", fallback=None) == None:
                    continue
                recordNode = None
                local_loc_source = os.path.join(cs.get("locDirectory"), loc_object["id"] + ".marcxml.xml")
                if matchURIRef not in loc_update_dict:
                    loc_update_dict[matchURIRef] = {'date': date.today()}
                    if os.path.exists(local_loc_source):
                        loc_update_dict[matchURIRef]['updatable'] = False
                    else:
                        loc_update_dict[matchURIRef]['updatable'] = True
                if not loc_update_dict[matchURIRef]['updatable'] and os.path.exists(local_loc_source):
                    try:
                        with open(local_loc_source, encoding="utf-8") as f:
                            recordNode = ET.parse(f)
                    except ET.ParseError as e:
                        logging.warning("Failed to parse the following file: %s. Skipping the property for concept %s." %
                                (local_loc_source, concept))
                elif update_loc_concepts:
                    try:
                        # Kongressin kirjastosta voi ladata 120 käsitettä minuutissa, varmistetaan aikaviiveellä, ettei raja ylity
                        time.sleep(0.5)
                        with urllib.request.urlopen(loc_object["prefix"] + loc_object["id"] + ".marcxml.xml", timeout=5) as marcxml, \
                            open(local_loc_source, 'wb') as out_file:
                            shutil.copyfileobj(marcxml, out_file)
                            logging.info("Downloaded LCSH link to %s." %
                                (local_loc_source))
                            loc_concept_downloaded = True
                            loc_update_dict[matchURIRef]['updatable'] = False
                    except urllib.error.URLError as e:
                        logging.warning('Unable to load the marcxml for %s. Reason: %s. Skipping the property for concept %s.' %
                            (loc_object["id"], e.reason, concept))
                    except OSError as e:
                        logging.warning("Failed to create a file for %s under %s directory. Skipping the property for concept %s." %
                            (loc_object["id"], cs.get("locDirectory"), concept))
                
                if loc_concept_downloaded:
                    try:
                        with open(local_loc_source, encoding="utf-8") as f:
                            recordNode = ET.parse(f)
                    except OSError as e:
                        logging.warning("Failed to read the file for %s under %s directory. Skipping the property for concept %s" %
                            (loc_object["id"], cs.get("locDirectory"), concept))
                    except ET.ParseError as e:
                        logging.warning("Failed to parse the following file: %s. Skipping the property for concept %s." %
                            (local_loc_source, concept))
                            
                
                if recordNode:
                    tagNode = None

                    for tagNumber in LCSH_1XX_FIELDS:
                        tagNode = recordNode.find("./marcxml:datafield[@tag='" + tagNumber + "']", ET_namespaces)
                        if tagNode is not None:
                            # otetaan ensimmäinen
                            break

                    if tagNode is not None:
                        tag = "7" + tagNode.attrib["tag"][1:]
                        first_indicator = tagNode.attrib["ind1"]
                        subfields = []

                        for child in tagNode:
                            subfields.extend((child.attrib["code"], 
                                              decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(child.text)))
                                              #str(child.text)
                                             ))

                        subfields.extend(("4", sub4))
                        if second_indicator == "7":
                            subfields.extend(("2", sub2))
                        subfields.extend(("0", str(matchURIRef)))

                        fields.append(
                            Field(
                                tag = tag,
                                indicators = [first_indicator, second_indicator],
                                subfields = subfields
                            )
                        )

                    else:
                        logging.warning("Could not find any marcxml:datafield objects with a tag number in the following list: %s for the following record: %s. %s" %
                          (LCSH_1XX_FIELDS, loc_object["id"], "Skipping the property for concept " + concept + "."))
                        #continue

            else:
                #käsitellään kaikki muut sanastot paitsi lcsh & lcgf
                prefLabel = None
                multipleLanguages = False
                languagesEncountered = set()
                sortedPrefLabels = sorted(g2.preferredLabel(matchURIRef,
                                        labelProperties=(SKOS.prefLabel)))
                for label in sortedPrefLabels:
                    languagesEncountered.add(label[1].language)
                    if len(languagesEncountered) > 1:
                        multipleLanguages = True
                        break
                processedLanguages = set()             
                for type2, prefLabel in sortedPrefLabels:
                    prefLabelLanguage = prefLabel.language if prefLabel.language != None else ""
                    
                    if prefLabelLanguage:
                        if LANGUAGES.get(prefLabelLanguage):
                            pass
                        else:
                            if not cs.getboolean("ignoreOtherGraphWarnings", fallback=IGNOREOTHERGRAPHWARNINGS):
                                logging.warning("LANGUAGES dictionary has no key for language '%s' found from the skos:prefLabel %s of target %s. Skipping." %
                                    (prefLabelLanguage, matchURIRef, concept))
                            continue
                    
                    if prefLabelLanguage in processedLanguages:
                        if not cs.getboolean("ignoreOtherGraphWarnings", fallback=IGNOREOTHERGRAPHWARNINGS):
                            logging.warning("Multiple prefLabels detected for target %s in language %s. Skipping prefLabel %s." %
                          (matchURIRef, prefLabelLanguage, prefLabel))
                        continue

                    processedLanguages.add(prefLabelLanguage)
                    
                    subfields = [
                        'a', decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(prefLabel))),
                        #'a', str(prefLabel),
                        '4', sub4
                    ]
                    
                    
                    if prefLabelLanguage == "":
                        multipleLanguagesEnd = ""
                    else:
                        # kovakoodattu yso & slm tännekin
                        multipleLanguagesEnd = "/" + LANGUAGES[prefLabel.language] if sub2 in ["yso", "slm"] or multipleLanguages else ""
                    if second_indicator != "4":
                        subfields.extend(("2", 
                            sub2 + multipleLanguagesEnd
                        ))
                        
                    subfields.extend(("0", str(matchURIRef)))
                    
                    fields.append(
                        Field(
                            tag=tag,
                            indicators = [' ', second_indicator],
                            subfields = subfields
                        )
                    )
                if not prefLabel and not cs.getboolean("ignoreOtherGraphWarnings", fallback=IGNOREOTHERGRAPHWARNINGS): 
                    logging.warning("Could not find preflabel for target %s. Skipping property %s target for concept %s." %
                      (str(matchURIRef), str(valueProp.prop), concept))
                    #continue
        
        # sort fields and add them
        for sorted_field in sorted(fields, key=lambda o: (
            o.tag,
            o.value().lower()
            )):
            rec.add_field(sorted_field)
            
        writer_records_counter += 1
        writer.write(rec)

        if helper_variables['modificationDates']:
            md5 = hashlib.md5()        
            md5.update(str.encode(str(rec)))
            hash = md5.hexdigest()
            if str(concept) in modified_dates:
                if not hash == modified_dates[str(concept)][1] or loc_concept_downloaded:
                    modified_dates[str(concept)] = (date.today(), hash)
            else:  
                modified_dates[str(concept)] = (date.today(), hash)
    
    if helper_variables['keepModified']:
        concs = []
        for conc in g.subjects(RDF.type, SKOS.Concept):
            concs.append(str(conc))
        for conc in modified_dates:
            if conc not in concs:
                #jos muokkauspäivämäärissä oleva käsite puuttuu, luodaan deprekoitu käsite
                rec = Record()
                rec.leader = cs.get("leaderDeleted0", fallback=LEADERDELETED0)
                rec.add_field(
                    Field(
                        tag='024',
                        indicators = ['7', ' '],
                        subfields = [
                            'a', conc,
                            '2', "uri"
                        ]
                    )
                )
                rec.add_field(
                    Field(
                        tag='040',
                        indicators = [' ', ' '],
                        subfields = [
                            'a', cs.get("creatorAgency", fallback=CREATOR_AGENCY),
                            'b', LANGUAGES[language],
                            'f', helper_variables["vocCode"]
                        ]
                )
        )
                writer_records_counter += 1
                writer.write(rec)
    
    if handle is not sys.stdout:
        writer.close()

    if helper_variables['modificationDates']:
        with open(helper_variables['modificationDates'], 'wb') as output:
            pickle.dump(modified_dates, output, pickle.HIGHEST_PROTOCOL)

    with open(loc_update_file, 'wb') as output:
        pickle.dump(loc_update_dict, output, pickle.HIGHEST_PROTOCOL)

    # tuotetaan tuotetaan lopuksi käsitteet laveassa XML-muodossa
    parser = ET.XMLParser(remove_blank_text=True,strip_cdata=False)
    file_path = helper_variables["outputFileName"]
    tree = ET.parse(file_path, parser)
    e = tree.getroot()
    handle = open(cs.get("output", fallback=helper_variables["defaultOutputFileName"]), "wb")
    handle.write(ET.tostring(e, encoding='UTF-8', pretty_print=True, xml_declaration=True))

    if handle is not sys.stdout:
        handle.close()

    # lokitetaan vähän tietoa konversiosta
    if helper_variables['keepDeprecated']:
        logging.info(
            "Processed %s concepts, from which %s were left out because of deprecation. Wrote %s MARCXML records." %
            (incrementor, deprecated_counter, writer_records_counter)
        )
    else:
        logging.info(
            "Processed %s concepts. Wrote %s MARCXML records." %
            (incrementor, writer_records_counter)
        )

    if cs.get("outputSpecified", fallback=None) == None:
        outputChannel = sys.stdout.buffer
        with open(cs.get("output", fallback=helper_variables['defaultOutputFileName']), "rb") as f:
            shutil.copyfileobj(f, outputChannel)
    if cs.get("outputSpecified", fallback=None) == None:
        os.remove(cs.get("output", fallback=helper_variables['defaultOutputFileName']))

    logging.info("Conversion completed: %s"%datetime.now().replace(microsecond=0).isoformat())
# MAIN

def main():    
    settings = ConfigParser(interpolation=ExtendedInterpolation())
    args = readCommandLineArguments()
    
    if args.config:
        settings.read(args.config)
    else:
        settings.add_section(args.vocabulary_code.upper())
    
    # for extracting meaningful leading/trailing spaces
    # (removing double quotes around the string)
    for sec in settings.sections():
        for (key, val) in settings.items(sec):
            if len(val) > 0 and val[-1] == '"' and val[0] == '"':
                settings.set(sec, key, val[1:-1])
    
    cs = args.vocabulary_code.upper() # default config section to vocabulary code

    settings.set("DEFAULT", "vocabulary_code", cs.lower())
    # Used in MARC code used in tag 040 subfield f
    # and 7XX foreign language prefLabels
    graphi = Graph()
    other_graphs = Graph()

    if args.config_section:
        # override default config section
        cs = args.config_section.upper()

    # prepare settings
  
    # configure logging
    
    loglevel = logging.INFO
    logFormatter = logging.Formatter('%(levelname)s - %(message)s')
    
    if args.log_file:
        logging.basicConfig(filename=args.log_file, filemode="w")
    
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    logger.propagate = False
    logging.info("Conversion started: %s"%datetime.now().replace(microsecond=0).isoformat())

    if args.endpoint:
        settings.set(cs, "endpoint", args.endpoint)
    
    # normalize endpoint graphs
    if args.endpoint_graphs:
        settings.set(cs, "endpointGraphs", ",".join(readConfigVariable(args.endpoint_graphs, " ")))
    elif settings.get(cs, "endpointGraphs", fallback=None) != None:
        settings.set(cs, "endpointGraphs", ",".join(readConfigVariable(settings.get(cs, "endpointGraphs"), ",")))
    else:
        settings.set(cs, "endpointGraphs", ",".join(ENDPOINTGRAPHS))
    
    if args.ignore_other_graph_warnings:
        settings.set(cs, "ignoreOtherGraphWarnings", "true")
    
    if args.grouping_classes:
        settings.set(cs, "groupingClasses", ",".join(readConfigVariable(args.grouping_classes, " ")))
    elif settings.get(cs, "groupingClasses", fallback=None) != None:
        settings.set(cs, "groupingClasses", ",".join(readConfigVariable(settings.get(cs, "groupingClasses"), ",")))
    else:
        settings.set(cs, "groupingClasses", "")

    if not args.input:
        logging.error("Input is required.")
        sys.exit(2)

    if args.input_format:
        settings.set(cs, "inputFormat", args.input_format)

    graphi = Graph()
    graph_loaded = False

    if args.pickle_vocabulary:
        pickleFile = args.pickle_vocabulary
    else:   
        pickleFile = settings.get(cs, "pickleVocabulary", fallback=None)
    if pickleFile:
        if os.path.isfile(pickleFile):
            timestamp = os.path.getmtime(pickleFile)
            file_date = date.fromtimestamp(timestamp)
            if file_date == date.today():
                with open(pickleFile, 'rb') as input_file: 
                    try:     
                        graphi = pickle.load(input_file)
                        graph_loaded = True
                    except EOFError:
                        logging.error("EOFError in "%pickleFile)
       
    if not graph_loaded:
        graphi += Graph().parse(args.input, format=settings.get(cs, "inputFormat", fallback="turtle"))
        if pickleFile:
            with open(pickleFile, 'wb') as output:
                pickle.dump(graphi, output, pickle.HIGHEST_PROTOCOL)

    if args.output:
        settings.set(cs, "output", args.output)
        settings.set(cs, "outputSpecified", "true")

    if args.languages != None:
        settings.set(cs, "languages", ",".join(readConfigVariable(args.languages, " ")))
    elif settings.get(cs, "languages", fallback=None) == None:
        logging.error("Language is required. Set with --languages.")
        sys.exit(2)
    else:
        settings.set(cs, "languages", ",".join(readConfigVariable(settings.get(cs, "languages"), ",")))

    if args.multilanguage_vocabulary:
        settings.set(cs, "multilanguage", "true")
    
    if args.loc_directory:
        settings.set(cs, "locDirectory", args.loc_directory)
     
    if args.keep_modified_after and not args.modification_dates:
        logging.error('Arguments required with --keep_modified_after: --modification_dates')
        sys.exit(2)
    if args.modification_dates:    
        settings.set(cs, "modificationDates", args.modification_dates)
    if args.keep_modified_after:
        settings.set(cs, "keepModifiedAfter", args.keep_modified_after)
        modifiedLimit = settings.get(cs, "keepModifiedAfter")
        if modifiedLimit.lower() == "all":
            pass
        elif modifiedLimit.lower() == "none":
            pass
        else:
            try:
                datetime.date(datetime.strptime(modifiedLimit, "%Y-%m-%d"))
            except ValueError:
                logging.error("Cannot interpret 'keepModifiedAfter' value set in configuration file or given as a CLI parameter. Possible values are 'ALL', 'NONE' and ISO 8601 format for dates.")
                sys.exit(2)

    if args.default_creation_date:
        settings.set(cs, "defaultCreationDate", args.default_creation_date)
    if settings.get(cs, "defaultCreationDate", fallback=None) != None:
        try:
            datetime.date(datetime.strptime(settings.get(cs, "defaultCreationDate"), "%Y-%m-%d"))
        except ValueError:
            logging.error("Cannot interpret 'defaultCreationDate' value set in configuration file or given as a CLI parameter. Possible values: ISO 8601 format for dates.")
            sys.exit(2)
    
    if args.keep_deprecated_after:
        settings.set(cs, "keepDeprecatedAfter", args.keep_deprecated_after)
    if settings.get(cs, "keepDeprecatedAfter", fallback=None) != None:
        deprecationLimit = settings.get(cs, "keepDeprecatedAfter")
        if deprecationLimit.lower() == "all":
            pass
        elif deprecationLimit.lower() == "none":
            pass
        else:
            try:
                datetime.date(datetime.strptime(deprecationLimit, "%Y-%m-%d"))
            except ValueError:
                logging.error("Cannot interpret 'keepDeprecatedAfter' value set in configuration file or given as a CLI parameter. Possible values are 'ALL', 'NONE' and ISO 8601 format for dates.")
                sys.exit(2)
    
    if settings.get(cs, "endpointGraphs"):
        if settings.get(cs, "endpoint", fallback=None) == None:
            logging.warning("No endpoint address for endpoint graphs (set with --endpoint). Skipping endpoint graphs.")
        else:
            other_graphs += readEndpointGraphs(settings[cs])
            pass
    
    for lang in settings.get(cs, "languages").split(","):
        convert(settings[cs], cs, lang, graphi, other_graphs)
    
if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        logging.exception(e)
