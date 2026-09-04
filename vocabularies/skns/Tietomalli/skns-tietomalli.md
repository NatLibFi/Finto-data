# SKNS-tietomalli (Suomenkielisten kielten nimien sanasto)

Aineistona [VocBenchistä 3.9.2026 exportattu SKNS](https://github.com/NatLibFi/Finto-data/blob/master/vocabularies/skns/skns-kehitystietomalli-vb-2026-09-05.ttl) (84 736 tripleä), laadittu 4.9.2026. Yhteystiedot: [mika.vaara@helsinki.fi](maito:mika.vaara@helsinki.fi)

#### Sisältö:
1. SKNS:n omat luokat
2. Käytetyt keskeiset propertyt
3. Luokkien ja käsitteiden väliset suhteet
4. Deprekointimallii

## 1. Luokkahierarkia

```text
skos:Concept
└── sknsmeta:Concept
    ├── sknsmeta:LangFamily          Kielikunta (TopConcept)
    ├── sknsmeta:LangGroup           Kieliryhmä
    ├── sknsmeta:Lang                Kieli
    └── sknsmeta:DeprecatedConcept   Käytöstä poistettu käsite
```

Huom: Yksittäinen deprekoitu resurssi voi säilyttää alkuperäisen tyyppinsä, esimerkiksi sknsmeta:LangGroup, mutta ei voi enää olla sknsmeta:Concept.

## 2. Luokat

| Luokka | Yläluokka | Selitys |
|---|---|:---|
| `sknsmeta:Concept` | `skos:Concept` | SKNS:n yleinen käsiteluokka. Kaikki kieli-, kieliryhmä- ja kielikuntakäsitteet ovat tämän aliluokkia. |
| `sknsmeta:LangFamily` | `sknsmeta:Concept` | Kielikunta |
| `sknsmeta:LangGroup` | `sknsmeta:Concept` | Kieliryhmä |
| `sknsmeta:Lang` | `sknsmeta:Concept` | Kielen nimi |
| `sknsmeta:DeprecatedConcept` | `sknsmeta:Concept` | Käytöstä poistettu SKNS-käsite. Säilyttää tiedon käsitteen aiemmista suhteista ja mahdollisesta korvaajasta. |

## 3. Keskeiset propertyt

Viitetiedoiksi (englanniksi):

[SKOS Core Guide](https://www.w3.org/TR/swbp-skos-core-guide/)<br>
[SKOS scheme relation](https://www.w3.org/TR/skos-primer/#secscheme)<br>
[SKOS eXtension for Labels (SKOS-XL)](https://www.w3.org/TR/skos-reference/#xl)<br>
[SKOS documentation property](https://www.w3.org/TR/skos-reference/#notes)<br>
[Object properties](https://www.w3.org/TR/owl-ref/#ObjectProperty-def)<br>
[owl:DatatypeProperty ](https://www.w3.org/TR/2004/REC-owl-semantics-20040210/#owl_DatatypeProperty)<br>
[rdf:property](https://www.w3.org/TR/rdf-schema/#ch_property)<br>
[Ontology and Annotation Properties](https://www.w3.org/TR/owl-ref/)<br>
[Dublin Core properties](https://www.dublincore.org/specifications/dublin-core/dces/)


| Property | Tyyppi | Käyttöalue → kohteen tyyppi | Selitys |
|---|---|---|:---|
| `skos:prefLabel` | SKOS labelling property | `skos:Concept → literaali` | Käsitteen ensisijainen termi/label, käytössä SKNS-käsitteillä. |
| `skos:altLabel` | SKOS labelling property | `skos:Concept → literaali` | Vaihtoehtoinen termi/label. |
| `skos:hiddenLabel` | SKOS labelling property | `skos:Concept → literaali` | Piilotettu termi, tyypillisesti hakuun ja varianttimuotoihin. |
| `skos:note` | SKOS documentation property | `skos:Concept → literaali` | Käsitteeseen liittyvä huomautus. |
| `skos:broader` | SKOS semantic relation | `skos:Concept → skos:Concept` | Hierarkkinen suhde alakäsitteestä yläkäsitteeseen. |
| `skos:narrower` | SKOS semantic relation | `skos:Concept → skos:Concept` | Hierarkkisen suhteen käänteinen suunta yläkäsitteestä alakäsitteeseen. |
| `skos:inScheme` | SKOS scheme relation | `skos:Concept → skos:ConceptScheme` | Liittää käsitteen käsiteskeemaan. |
| `skos:topConceptOf` | SKOS scheme relation | `skos:Concept → skos:ConceptScheme` | Merkitsee käsitteen skeeman ylimmäiseksi käsitteeksi. |
| `skos:hasTopConcept` | SKOS scheme relation | `skos:ConceptScheme → skos:Concept` | Liittää skeeman ylimmäiseen käsitteeseen. |
| `skos:closeMatch` | SKOS mapping relation | `skos:Concept → ulkoinen käsite` | Läheinen vastaavuussuhde, osittainen korvautuvuus ontologian ulkoiseen käsitteeseen. |
| `skosxl:prefLabel` | owl:ObjectProperty | `skos:Concept → skosxl:Label` | Liittää SKOS-XL-labelin ensisijaiseen labeliin (skos:prefLabel). |
| `skosxl:altLabel` | SKOS-XL property | `skos:Concept → skosxl:Label` | Liittää SKOS-XL-labelin vaihtoehtoiseen labeliin (skos:altLabel). |
| `skosxl:literalForm` | owl:DatatypeProperty | `skosxl:Label → literaali` | SKOS-XL-labelin tekstimuoto (string). |
| `sknsmeta:singularPrefLabel` | owl:DatatypeProperty | `sknsmeta:Concept → literaali` | skos:prefLabelin yksikkömuoto. |
| `sknsmeta:silCode` | rdf:Property | `SKNS-käsite → koodi` | ISO 639-3-koodi |
| `sknsmeta:silSource` | rdf:Property | `SKNS-käsite → lähdetieto` | ISO 639-3-koodin lähde. |
| `sknsmeta:glottologCode` | rdf:Property | `SKNS-käsite → koodi` | Glottolog-koodi |
| `sknsmeta:glottologSource` | rdf:Property | `SKNS-käsite → lähdetieto` | Glottolog-koodin lähde. |
| `sknsmeta:cldrCode` | rdf:Property | `SKNS-käsite → koodi` | CLDR-koodi. |
| `dct:spatial` | Dublin Core property | `SKNS-käsite → alue` | Käsitteen maantieteellinen kattavuus tai paikkatieto. |
| `dct:created` | Dublin Core property | `resurssi → ajankohta` | Resurssin luontipäivä. |
| `dct:modified` | Dublin Core property | `resurssi → ajankohta` | Resurssin muokkauspäivä. |
| `owl:deprecated` | OWL annotation property | `resurssi → boolean` | Ilmaisee, että resurssi on poistettu käytöstä. |
| `sknsmeta:deprecatedOn` | owl:DatatypeProperty | `sknsmeta:DeprecatedConcept → xsd:date` | Deprekoinnin päivämäärä. |
| `sknsmeta:deprecatedSubClassOf` | owl:ObjectProperty | `sknsmeta:DeprecatedConcept → skos:Concept` | Deprekoidun käsitteen entinen yläkäsite. |
| `sknsmeta:deprecatedSuperClassOf` | owl:ObjectProperty | `sknsmeta:DeprecatedConcept → skos:Concept` | Deprekoidun käsitteen entinen alakäsite. |
| `sknsmeta:deprecatedReplacedBy` | owl:ObjectProperty | `sknsmeta:DeprecatedConcept → skos:Concept` | Käsite, jolla deprekoitu käsite on korvattu. |
| `sknsmeta:deprecatedAssociativeRelation` | owl:ObjectProperty | `sknsmeta:DeprecatedConcept → skos:Concept` | Deprekoidun käsitteen aiempi assosiatiivinen suhde. |
| `sknsmeta:deprecatedExactMatch` | owl:ObjectProperty | `sknsmeta:DeprecatedConcept → skos:Concept` | Deprekoidun käsitteen aiempi vastaavuussuhde (ekvivalenssi). |

## 4. Rakenteelliset suhteet

| Käyttöalue | Property | Kohteen tyyppi | Selitys |
|---|---|---|:---|
| `sknsmeta:LangFamily` | `rdfs:subClassOf` | `sknsmeta:Concept` | Kielikunta on SKNS-käsite. |
| `sknsmeta:LangGroup` | `rdfs:subClassOf` | `sknsmeta:Concept` | Kieliryhmä on SKNS-käsite. |
| `sknsmeta:Lang` | `rdfs:subClassOf` | `sknsmeta:Concept` | Kieli on SKNS-käsite. |
| `sknsmeta:DeprecatedConcept` | `rdfs:subClassOf` | `sknsmeta:Concept` | Deprekoitu käsite on SKNS-käsite. |
| `sknsmeta:Concept` | `rdfs:subClassOf` | `skos:Concept` | SKNS:n käsiteluokka on SKOS Concept -luokan aliluokka. |
| `sknsmeta:Lang` | `skos:broader` | `sknsmeta:LangGroup` | Kieli kuuluu välittömästi kieliryhmään. Aineiston yleisin hierarkiasuhde. |
| `sknsmeta:Lang` | `skos:broader` | `sknsmeta:LangFamily` | Kieli voi kuulua välittömästi kielikuntaan ilman väliin mallinnettua kieliryhmää. |
| `sknsmeta:LangGroup` | `skos:broader` | `sknsmeta:LangGroup` | Kieliryhmä voi kuulua toiseen kieliryhmään. |
| `sknsmeta:LangGroup` | `skos:broader` | `sknsmeta:LangFamily` | Kieliryhmä voi kuulua kielikuntaan. |
| `skos:Concept` | `skos:inScheme` | `skns:` | Käytössä olevat (ei deprekoidut) SKNS-käsitteet kuuluvat SKNS-käsiteskeemaan. |
| `sknsmeta:DeprecatedConcept` | `skos:inScheme` | `skns:deprecatedconceptscheme` | Käytöstä poistettu käsite kuuluu erilliseen deprekoitujen käsitteiden skeemaan. |

## 5. Hierarkia käytännössä

Aineistossa `skos:broader` muodostaa kielten luokitteluhierarkian. Tyypilliset polut ovat:

```text
Kieli → Kieliryhmä → Kieliryhmä → ... → Kielikunta
Kieli → Kieliryhmä → Kielikunta
Kieli → Kielikunta
```

Aineiston välittömät `skos:broader`-suhteet:

- Lang → LangGroup
- Lang → LangFamily
- LangGroup → LangGroup
- LangGroup → LangFamily

## 6. Labelit ja SKOS-XL

Ensisijaisesti käytetään SKOSia:

```text
skos:Concept
 ├─ skos:prefLabel
 ├─ skos:altLabel
 └─ skos:hiddenLabel
```

Aineistossa on lisäksi SKOS-XL-rakenne sensitiivisyyshuomautuksia varten:

```text
skos:Concept
 └─ skosxl:prefLabel / skosxl:altLabel
       ↓
    skosxl:Label
       └─ skosxl:literalForm → literaali
```

## 7. Tunnisteet ja lähteet

Kieliin ja muihin SKNS-käsitteisiin liittyviä omia "tunnistepropertyja" ovat:

```text
sknsmeta:silCode
sknsmeta:silSource
sknsmeta:glottologCode
sknsmeta:glottologSource
sknsmeta:cldrCode
```

Lisäksi `dct:spatial` liittää käsitteitä (kielten nimiä) maantieteellisiin alueisiin (puhumavaltioihin).

## 8. Deprekointimalli

```text
sknsmeta:DeprecatedConcept
 ├─ owl:deprecated → true
 ├─ sknsmeta:deprecatedOn → xsd:date
 ├─ sknsmeta:deprecatedSubClassOf → aiempi yläkäsite
 ├─ sknsmeta:deprecatedSuperClassOf → aiempi alakäsite
 ├─ sknsmeta:deprecatedReplacedBy → korvaava käsite
 ├─ sknsmeta:deprecatedAssociativeRelation → aiempi assosiatiivinen suhde
 └─ sknsmeta:deprecatedExactMatch → aiempi vastaavuussuhde
```

Deprekoidut käsitteet kuuluvat erilliseen `skns:deprecatedconceptscheme`-skeemaan.

## 9. Huomautus!

Monet tietomallikuvauksessa käytetyt termit ovat hankalia suomentaa, koska niiden käytölle ei ole suomenkielisiä konventioita tai jos on, ne ovat liian alakohtaista jargonia, jota muiden lukijoiden voi olla hankala ymmärtää ilman kohtuutonta lisäperehtymistä. Ratkaisuna on ollut paikoitellen käyttää englanninkielisiä termejä taikka yleisesti käytettyjä mukautettuja lainoja.

#### Post Scriptum

Mikäli haluat muokata tätä tiedostoa ja tarvitset hierarkian kuvaamiseen erikoisia fi-näppäimistöstä puuttuvia ascii-merkkejä, tässä muutama:

└ Ctrl+Shift+U, 2514, Enter<br>
─ Ctrl+Shift+U, 2500, Enter<br>
├ Ctrl+Shift+U, 251C, Enter<br>
│ Ctrl+Shift+U, 2502, Enter<br>
┬ Ctrl+Shift+U, 252C, Enter<br>
┐ Ctrl+Shift+U, 2510, Enter<br>
← Ctrl+Shift+U, 2190, Enter<br>
↑ Ctrl+Shift+U, 2191, Enter<br>
→ Ctrl+Shift+U, 2192, Enter<br>
↓ Ctrl+Shift+U, 2193, Enter



