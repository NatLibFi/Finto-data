#!/usr/bin/env python3
# coding=utf-8

from rdflib import Graph, Namespace, URIRef, BNode, Literal, RDF
from rdflib.namespace import SKOS, XSD, OWL, DC
from rdflib.namespace import DCTERMS as DCT
import pickle
import os
import argparse
import hashlib
import unicodedata
from configparser import ConfigParser, ExtendedInterpolation
import sys
import logging
from datetime import datetime, date
from collections import namedtuple
from collections.abc import Sequence
from pymarc import Record, Field, XMLWriter, MARCReader, parse_xml_to_array
from lxml import etree as ET

CREATOR_AGENCY = "FI-NL" # Tietueen luoja/omistaja & luetteloiva organisaatio, 003 & 040 kentat

MTS=Namespace('http://urn.fi/URN:NBN:fi:au:mts:')
ISOTHES=Namespace('http://purl.org/iso25964/skos-thes#')

GROUPINGCLASSES = [ISOTHES.ConceptGroup]

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

KEEPMODIFIEDAFTER = "ALL"
NORMALIZATION_FORM = "NFD" # käytetään UTF8-merkkien dekoodauksessa

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

# tuple helpottamaan getValues-apufunktion arvojen käsittelyä
ValueProp = namedtuple("ValueProp", ['value', 'prop'])

#haetaan ryhmäkäsitteiden alakäsitteet
def get_member_groups(g, group, uris):
    members = g.preferredLabel(group, labelProperties=[SKOS.member])   
    for m in members:
        uris.add(m[1])
        get_member_groups(g, m[1], uris)

def readCommandLineArguments():
    parser = argparse.ArgumentParser(description="Program for converting Finto SKOS-vocabularies into MARC (.mrcx).") 
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
    parser.add_argument("-log", "--log_file", help="Log file location.")
    parser.add_argument("-modificationDates", "--modification_dates",
        help="File location for pickle file, which contains latest modification dates for concepts (e. g. {'concept uri': 'YYYY-MM-DD'}) \
        The file is updated after new records are created, if keepModifiedAfter is left out of command line arguments") 
    parser.add_argument("-keepModifiedAfter", "--keep_modified_after",
        help="Create separate batch of MARC21 files for concepts modified after the date given (set in YYYY-MM-DD format).")
        
    args = parser.parse_args()
    return args

# funktio komentoriviparametrillä olevien monimutkaisten merkkijonojen lukemiseen ja siistimiseen
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

# pääfunktio
def convert(cs, language, g):

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
        'keepGroupingClasses' : cs.getboolean("keepGroupingClasses", fallback=False),
        'defaultOutputFileName' : "yso2marc-" + cs.name.lower() + "-" + language + ".mrcx"
    }

    if helper_variables['keepModified']:
        helper_variables['keepModifiedLimit'] = False \
        if cs.get("keepModifiedAfter", fallback=KEEPMODIFIEDAFTER).lower() == "all" \
        else datetime.date(datetime.strptime(cs.get("keepModifiedAfter"), "%Y-%m-%d"))

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
    writer_records_counter = 0
    ET_namespaces = {"marcxml": "http://www.loc.gov/MARC21/slim"}

    handle = open(cs.get("output", fallback=helper_variables["defaultOutputFileName"]), "wb")
    writer = XMLWriter(handle)
    
    # listataan preflabelit, jotta voidaan karsia alt_labelit, jotka toisessa käsitteessä pref_labelina
    pref_labels = set()
    for conc in g.subjects(RDF.type, SKOS.Concept):
        pref_label = g.preferredLabel(conc, lang=language)
        if pref_label:
            pref_labels.add(str(pref_label[0][1]))
    
    # vain nämä mts-käsiteryhmät otetaan mukaan, ryhmän nimestä ei tehdä MARC21-tietuetta
    ids = {"occupations": ['m2332'],
        "titles": ['m121', 
                   'm3764'],
        "organisation types": ['m196'],
        "family categories": ['m4865']
        }
    marc21_locations = {"occupations": {'code suffix': '74', 'subfield code': 'a'},
                        "titles": {'code suffix': '68', 'subfield code': 'd'},
                        "organisation types": {'code suffix': '68', 'subfield code': 'a'},
                        "family categories": {'code suffix': '76', 'subfield code': 'a'}
    }

    uris = {}
    for key in ids:
        uris[key] = set()
        for id in ids[key]:
            uris[key].add(MTS + id)
    for group in g.subjects(RDF.type, ISOTHES.ConceptGroup):
        for key in uris:
            if any(str(group).endswith(uri) for uri in uris[key]):
                get_member_groups(g, group, uris[key])
    concs = []
    if helper_variables['keepModified']:
        concs = []    
        for uri in modified_dates:
            if modified_dates[uri][0] >= helper_variables['keepModifiedLimit']:  
                concs.append(URIRef(uri))
    else:
        for conc in g.subjects(RDF.type, SKOS.Concept):
            concs.append(conc)

    #luotujen käsitteiden tunnukset, joilla voidaan selvittää modification_dates-listan avulla poistetut käsitteet
    created_concepts = set()

    for concept in concs:
        #vain ammateista ja arvonimistä luodaan MARC21-tietueet         
        if not any(concept in uris[key] for key in uris):
            continue
        created_concepts.add(str(concept))
        incrementor += 1
        if incrementor % 1000 == 0:
            logging.info("Processing %sth concept" % (incrementor))

        #skipataan ryhmittelevät käsitteet
        if not helper_variables['keepGroupingClasses']:
            if any (conceptType in helper_variables["groupingClasses"] for conceptType in g.objects(concept, RDF.type)):
                continue

        rec = Record()   

        rec.leader = cs.get("leaderNew", fallback=LEADERNEW)

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

        valueProps = sorted(getValues(g, concept, SKOS.prefLabel, language=language),
                                   key=lambda o: o.value)
        if len(valueProps) == 0:
            logging.warning("Could not find preflabel for concept %s in language %s. Skipping the whole concept." %
              (concept, language))
            continue
        elif len(valueProps) != 1:
            logging.warning("Multiple prefLabels detected for concept %s in language %s. Choosing the first." %
                  (concept, language)) 

        for key in uris:
            if concept in uris[key]:
                tag = "1" + marc21_locations[key]['code suffix']
                subfield_code = marc21_locations[key]['subfield code']

        rec.add_field(
            Field(
                tag=tag,
                indicators = [' ', ' '],
                subfields=[
                            subfield_code, decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(valueProps[0].value)))
                          ]
            )
        )

        # skos:altLabel -> 467, 474
        # 450 katso-viittaus
        # jätetään tuottamatta 45X-kentät, jotka ovat toisessa käsitteessä 15X-kenttinä, paitsi altLabelein kohdalla
        seen_values = set()
        
        for valueProp in sorted(getValues(g, concept, [SKOS.altLabel], language=language),
                                key=lambda o: str(o.value)): 
            if valueProp.prop != SKOS.altLabel and str(valueProp.value) in pref_labels:
                continue
            if valueProp.prop == SKOS.hiddenLabel:
                if str(valueProp.value) in seen_values:
                    continue            
            seen_values.add(str(valueProp.value))
            for key in uris:
                if concept in uris[key]:
                    tag = "4" + marc21_locations[key]['code suffix']
                    subfield_code = marc21_locations[key]['subfield code']

            rec.add_field(
                Field(
                    tag=tag,
                    indicators = [' ', ' '],
                    subfields=[
                                subfield_code, decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(valueProp.value)))
                            ]
                )
            )

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
               
            else:
                # otetaan vain viittaukset samaan sanastoon
                continue

            for key in uris:
                if concept in uris[key]:
                    tag = "7" + marc21_locations[key]['code suffix']
                    subfield_code = marc21_locations[key]['subfield code']
            
            sub2 = "mts" + "/" + LANGUAGES[valueProp.value.language]
            fields.append(
                Field(
                    tag=tag,
                    indicators = [' ', ' '],
                    subfields = [
                        subfield_code, decomposedÅÄÖtoUnicodeCharacters(unicodedata.normalize(NORMALIZATION_FORM, str(valueProp.value))), 
                        '4', 'EQ',
                        '2', sub2,
                        '0', concept
                    ]
                )
            )

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
                if not hash == modified_dates[str(concept)][1]:
                    modified_dates[str(concept)] = (date.today(), hash)
            else:  
                modified_dates[str(concept)] = (date.today(), hash)

    #tuotetaan poistetut käsitteet, kun haetaan muuttuneet käsitteet
    #jos tietue on modified_dates-parametrillä määritettyssä tiedostossa, mutta ei graafissa, tulkitana poistetuksi tietueeksi
    #mts:ssä ei ole deprekointipäiviä
    #

    if helper_variables['keepModified']:
        concs = []
        for conc in g.subjects(RDF.type, SKOS.Concept):
            if any(conc in uris[key] for key in uris):
                concs.append(str(conc))
        for conc in modified_dates:
            if conc not in concs:
                #jos ei ole hajautussummaa (tuplen 2. arvo), luodaan deprekoitu käsite
                if modified_dates[conc][1]:
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
                    modified_dates[conc] = (date.today(), "")  
                    writer_records_counter += 1
                    writer.write(rec)
        
    if handle is not sys.stdout:
        writer.close()

    if helper_variables['modificationDates']:
        with open(helper_variables['modificationDates'], 'wb') as output:
            pickle.dump(modified_dates, output, pickle.HIGHEST_PROTOCOL)

    #jos luodaan kaikki käsitteet, tuotetaan tuotetaan lopuksi käsitteet laveassa XML-muodossa
    #if not helper_variables['keepModified']:
    parser = ET.XMLParser(remove_blank_text=True,strip_cdata=False)
    file_path = helper_variables["outputFileName"]
    tree = ET.parse(file_path, parser)
    e = tree.getroot()
    handle = open(cs.get("output", fallback=helper_variables["defaultOutputFileName"]), "wb")
    handle.write(ET.tostring(e, encoding='UTF-8', pretty_print=True, xml_declaration=True))

    if handle is not sys.stdout:
        handle.close()

    # lokitetaan vähän tietoa konversiosta
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

      
def main():    
    settings = ConfigParser(interpolation=ExtendedInterpolation())
    args = readCommandLineArguments()
    
    settings.add_section(args.vocabulary_code.upper())
    
    # for extracting meaningful leading/trailing spaces
    # (removing double quotes around the string)
    for sec in settings.sections():
        for (key, val) in settings.items(sec):
            if len(val) > 0 and val[-1] == '"' and val[0] == '"':
                settings.set(sec, key, val[1:-1])
    
    cs = args.vocabulary_code.upper() # default config section to vocabulary code
    settings.set("DEFAULT", "vocabulary_code", cs.lower())

    loglevel = logging.INFO
  
    if args.log_file:
        logging.basicConfig(filename=args.log_file, filemode="w")
    
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    logger.propagate = False
    logging.info("Conversion started: %s"%datetime.now().replace(microsecond=0).isoformat())
    
    if args.ignore_other_graph_warnings:
        settings.set(cs, "ignoreOtherGraphWarnings", "true")

    if not args.input:
        logging.error("Input is required.")
        sys.exit(2)

    if args.input_format:
        settings.set(cs, "inputFormat", args.input_format)

    graphi = Graph()
    graphi += Graph().parse(args.input, format=settings.get(cs, "inputFormat", fallback="turtle"))

    if args.output:
        settings.set(cs, "output", args.output)
        settings.set(cs, "outputSpecified", "true")

    if args.languages != None:
        settings.set(cs, "languages", ",".join(readConfigVariable(args.languages, " ")))
    else: 
        logging.error("Language is required. Set with --languages.")
        sys.exit(2)

    if args.multilanguage_vocabulary:
        settings.set(cs, "multilanguage", "true")
     
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
        
    for lang in settings.get(cs, "languages").split(","):
        convert(settings[cs], lang, graphi)
    
if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        logging.exception(e)