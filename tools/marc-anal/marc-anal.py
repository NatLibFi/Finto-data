# coding: utf-8
# MARC-Analysaattori
import csv, operator, sys, time
from sets import Set
from pymarc import MARCReader, record_to_xml
from rdflib import *
from SPARQLWrapper import SPARQLWrapper, JSON, XML 

wordlist = Set(['aktivismi','kaanonit','diffuusio','aggregaatit','messianismi','satanismi','satanismi','estetismi','spiritualismi','alkeiskoulut','elintarvikeketjut'])

sparql = SPARQLWrapper('http://kk-sparql.onki.fi/onki-light/sparql')
sparql.setReturnFormat(XML)

related_terms = {}
relatedObjects = dict() 
keyword_counts = {}
onto_path = sys.argv[1]
g = Graph()

class RelatedHit:
  def __init__(self, triple):
    self.label = triple[2].value
    self.prop = triple[1]
    self.parentUri = triple[0].toPython()

def generateQuery(search_term):
  q_string = """
  prefix skos:  <http://www.w3.org/2004/02/skos/core#>
  CONSTRUCT {
    ?uri ?prop ?relabel .
  } WHERE {
    GRAPH <http://www.yso.fi/onto/yso/> {
      { 
        ?uri skos:prefLabel ?label .
        FILTER ( lcase(str(?label)) = '""" + search_term.decode('latin_1') + """' && langMatches(lang(?label), "fi"))
      }
      { OPTIONAL { ?uri skos:related ?reluri } }
      UNION
      { OPTIONAL { ?uri skos:broader ?reluri } }
      UNION
      { OPTIONAL { ?uri skos:narrower ?reluri } }
      
      OPTIONAL { 
        ?reluri skos:prefLabel ?relabel .
        FILTER (langMatches(lang(?relabel), "fi")) 
        ?uri ?prop ?reluri .
      }
    }
  }"""
  return q_string

def getRelateds(query_result):
  related_terms = [] 
  for triple in query_result:
    label = triple[2].value
    association = RelatedHit(triple)
    if association.parentUri not in relatedObjects: 
      relatedObjects[association.parentUri] = dict()
    relatedObjects[association.parentUri][association.label] = association

    if (label not in related_terms):
      related_terms.append(label)
  return related_terms

for keyword in wordlist: 
  print('performing query for term: ' + keyword)
  sparql.setQuery(generateQuery(keyword))
  query_result = sparql.query().convert()
  related_terms[keyword] = getRelateds(query_result)

print(relatedObjects)

def multiple650(filename, keywords):
  print('\n -=MARC Analyzer=-')
  print('Reading file: ' + filename)
  reader = MARCReader(open(filename))
  print ''
  for index, record in enumerate(reader):
    if index % 1000 == 0:
      readout = 'records read from ' + filename + ': ' + str(index)
      sys.stdout.write('\r' + readout)
    if record['650']:
      to_be_stored = False
      subjects = list()
      keyword_hit = list()
      for i, field in enumerate(record.get_fields('650')):
        if field['a']:
          subjects.append(field['a'])
          if field['a'] in keywords:
            to_be_stored = True
            if not field['a'] in keyword_hit:
              keyword_hit.append(field['a'])
              if not field['a'] in keyword_counts:
                keyword_counts[field['a']] = {}
      if to_be_stored:
        while keyword_hit:
          keyword = keyword_hit.pop()
          subjects.remove(keyword)
          subjects.sort()
          subjects.insert(0, keyword)
          for subject in subjects:
            #crude way to filter the keyword being it's own top result
            if keyword == subject or subject.decode('utf-8') in related_terms[keyword]: 
              continue 
            if not subject in keyword_counts[keyword]:
              keyword_counts[keyword][subject] = 1
            else:
              keyword_counts[keyword][subject] += 1

def outputResults(limit, filename):
  writer = csv.writer(open(filename, 'w'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  sorted_counts = {}
  for keyword in keyword_counts:
    sorted_subjects = sorted(keyword_counts[keyword].iteritems(), key=operator.itemgetter(1), reverse=True)
    sorted_counts[keyword] = sorted_subjects
    writer.writerow(['asiasana: ' + keyword])
    for idx, subject in enumerate(sorted_subjects):
      writer.writerow(subject)
      if idx == limit: 
        break
    writer.writerow(['----------'])

def runFennica(wordlist):
  multiple650('fennica.mrc', wordlist)
  outputResults(10, 'fennica.csv')

def runArto(wordlist):
  multiple650('arto1.mrc', wordlist)
  multiple650('arto2.mrc', wordlist)
  outputResults(10, 'arto.csv')

runFennica(wordlist)
runArto(wordlist)

#teema1 = Set(['absurdi','ahneus','ajettavuus','tahallisuus','erot','menetys','kaamos','rakenne','läsnäolo','museoala'])
#teema2 = Set(['kärpäset','aarnikotkat','graafikot','afrikkalaiset','kalanviljelylaitokset','munuaiset','mystikot','juoksijat','rakennustarvikkeet','laivasto'])
#teema3 = Set(['aktivismi','kaanonit','diffuusio','aggregaatit','messianismi','satanismi','satanismi','estetismi','spiritualismi','alkeiskoulut','elintarvikeketjut'])
#teema4 = Set(['taide-elämä', 'taidehistoria', 'taidekauppa', 'taidepolitiikka', 'taidemusiikki', 'taidelainaamot', 'julkinen taide', 'barokki', 'modernismi', 'groteski', 'dadaismi', 'kitsch', 'värioppi'])
#teema5 = Set(['taide','taiteet','kirkko','kirkot','koulu','koulut','sokeri','sokerit','ooppera','oopperat', 'kala', 'kalat', 'seurakunnat', 'seurakunta', 'teatteri', 'teatterit', 'tiede', 'tieteet', 'perhe', 'perheet', 'karhu', 'karhut', 'paikallishistoria', 'paikallishistoriat', 'väri', 'värit', 'ääni', 'äänet', 'poliisi', 'poliisit', 'käsityö', 'käsityöt', 'kulttuuri', 'kulttuurit', 'uskonto', 'uskonnot'])
#teema6 = Set(['suomenruotsalaiset','suomenruotsalaisuus','suomalaiset','suomalaisuus','saunat','saunominen','aiheet','motiivit','teemat','etunimet', 'sukunimet', 'murha', 'tappo', 'rangaistukset', 'hevonen', 'ratsuhevoset', 'ratsastus', 'hirvi', 'metsästys', 'huippu-urheilu', 'doping', 'aseteknologia', 'sotatekniikka'])
#teema7 = Set(['ikä','sukulaiset','kauneudenhoito','elämänkaari','maku','kestävä kehitys','parisuhde','ympäristön tila','muutos','asiakassuhde', 'maatilat'])
#teema8 = Set(['kissa', 'keski-ikä', 'nautintoaineet', 'energiatehokkuus', 'aktivistit', 'ahven', 'talohistoriikit', 'pankit', 'kirjallisuudentutkimus', 'paperiteollisuus', 'kasvatus', 'laatu', 'lattiat'])
#teema9 = Set(['elämäntaito','hoitomenetelmät','integraatio','lapset','rakennemuutos','sosiaalipalvelut','terveydenhuolto','uskonelämä','ympäristönsuojelu','myytit','talvisota','kulttuuri'])
#teema10 = Set(['Ilmastonmuutosta koskeva Kioton pöytäkirja','Natura 2000','Eduskuntatalo','Urho Kekkosen Kansallispuisto','Yleissopimus lapsen oikeuksista','Word for Windows','Alzheimerin tauti','Kuninkaantie','Mars (planeetta)','Saimaan kanava'])
#teema11 = Set(['arviointi','vaikutukset','kehittäminen','kustannukset','käyttö','suunnittelu','seuranta','oppaat','riskit','strategia'])
#teema12 = Set(['terrorismi', 'terroristit', 'arabit', 'abortti', 'somalit', 'naiskauppa', 'romanit', ' ääriliikkeet', 'AIDS', 'homoseksuaalisuus', 'sotaveteraanit', 'ADHD'])
#teema13 = Set(['murha', 'aktivismi', 'maalaus', 'maalaukset', 'maalarit', 'taidemaalarit', 'maalaustaide', ' johtaminen', 'johtajat', 'maahanmuutto', 'maahanmuuttajat', 'muotoilu', 'muotoilijat', 'autoilu', 'autoilijat', 'matkailu', 'matkailijat', 'ympäristön saastuminen', 'päästöt', 'toipuminen', 'potilaat', 'kuolema', 'vainajat', 'sijoitustoiminta', 'sijoittajat'])
#teema14 = Set(['toimijuus', 'toimijat', 'rikollisuus', 'rikoksentekijät', 'opettajuus', 'opettajat', 'noituus', 'noidat', 'kansalaisuus', 'kansalaiset', 'ruumiillisuus', 'keho', 'ruumis', 'elämyksellisyys', 'elämys', 'etnisyys', 'etniset ryhmät', 'mieheys', 'miehet', 'äitiys', 'äidit', 'myrkyllisyys', 'myrkyt', 'työttömyys', 'työttömät'])
#teema15 = Set(['korjausrakentaminen', 'kaavoitus', 'elintarviketeollisuus', 'sukupuoli', 'rajat', 'julkinen sektori', 'suot', 'uupumus', 'harrastukset', 'yritysstrategiat', 'lama', 'islamilainen kulttuuri'])
#teema16 = Set(['esimiestyö', 'kasvuyritykset', 'luovat toimialat', 'kotona asuminen', 'varhainen puuttuminen', 'sosiaalinen media', 'eettinen kulutus', 'suomi toisena kielenä', 'hyvinvointipolitiikka', 'innovaatiotoiminta', 'digitaaliset pelit', 'vähähiilihydraattinen ruokavalio'])
#teema17 = Set(['mainonta', 'mainokset', 'järjestäminen', 'järjestys', 'analyysi', 'analyysimenetelmät', 'mittaus', 'mittausmenetelmät', 'opiskelu', 'kurssit', 'kvalitatiivinen tutkimus', 'hermeneutiikka', 'musiikintutkimus', 'musiikinteoria', 'empiirinen tutkimus', 'empirismi', 'haastattelututkimus', 'haastattelut', 'väittely', 'väitöskirjat'])


