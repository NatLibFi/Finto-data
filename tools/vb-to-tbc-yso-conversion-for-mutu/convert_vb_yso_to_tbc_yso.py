#!/usr/bin/env python3
"""
Ajo:
  python3 convert_new_yso_to_old_yso_2.py --old old.ttl --new new.ttl --out [jokin valitsemasi nimi].ttl
"""
import argparse
from collections import Counter

from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS

# YSO-meta nimiavaruudet: vanha (2007) ja uusi (VocBench) versio
OLD_YM = "http://www.yso.fi/onto/yso-meta/2007-03-02/"
NEW_YM = "http://www.yso.fi/onto/yso-meta/"

YM_OLD = Namespace(OLD_YM)
YM_NEW = Namespace(NEW_YM)

# Peilaus-ontologian määrittelypredikaatti vanhan rakenteen mukaan
PEILAUS_DEFINED = URIRef("http://www.yso.fi/onto/yso-peilaus/2007-03-02/definedConcept")

SKOSEXT = Namespace("http://purl.org/finnonto/schema/skosext#")
ISO_THES = Namespace("http://purl.org/iso25964/skos-thes#")
DC11 = Namespace("http://purl.org/dc/elements/1.1/")

ONTOLOGY_URI = URIRef("http://www.yso.fi/onto/yso/")

# Deprekoitujen käsitteiden tyypit ja kokoelmat vanhassa ja uudessa mallissa 
DEPRECATED_TYPE = URIRef("http://purl.org/finnonto/schema/skosext#DeprecatedConcept")
DEPRECATED_CONCEPTS_NEW = URIRef(NEW_YM + "deprecatedConcepts")
DEPRECATED_CONCEPTS_OLD = URIRef(OLD_YM + "deprecatedConcepts")
STRUCTURING_CLASS = URIRef(OLD_YM + "StructuringClass")

# Juuret, jotka jätetään kokonaan pois tai epäselvät tapaukset
DROP_SUBJECTS = {
    "http://www.yso.fi/onto/allars/allars_juuri",
    "http://www.yso.fi/onto/ysa/ysa_juuri",
    "http://www.yso.fi/onto/allars/",
}


def is_yso_instance_uri(u: URIRef) -> bool:
    """Tarkistaa onko URI YSOn käsiteinstanssi (muotoa http://www.yso.fi/onto/yso/p...)"""
    return isinstance(u, URIRef) and str(u).startswith("http://www.yso.fi/onto/yso/p")


def map_yso_meta_uri(term):
    """Muuntaa uuden yso-meta-nimiavaruuden URI:t vanhaan yso-meta nimiavaruuteen"""
    if isinstance(term, URIRef):
        s = str(term)
        if s.startswith(NEW_YM):
            return URIRef(OLD_YM + s[len(NEW_YM):])
    return term


def build_deprecated_subject_set(g_new: Graph):
    """
    Kerää kaikki deprekoidut käsitteet uudesta graafista.
    Käsite on vanhentunut jos,
    - sillä on owl:deprecated predikaatti
    - sen tyyppi on skosext:DeprecatedConcept
    - owl:deprecated-literaali on "true"
    """
    deprecated = set()

    # Haetaan kaikki subjektit, joilla on owl:deprecated
    for s, _, _ in g_new.triples((None, OWL.deprecated, None)):
        if isinstance(s, URIRef):
            deprecated.add(s)

    # Haetaan kaikki skosext:DeprecatedConcept-tyyppiset
    for s, _, _ in g_new.triples((None, RDF.type, DEPRECATED_TYPE)):
        if isinstance(s, URIRef):
            deprecated.add(s)

    # Haetaan ne, joissa owl:deprecated = true (literaalina)
    for s, _, o in g_new.triples((None, OWL.deprecated, None)):
        if isinstance(o, Literal) and (str(o).lower() == "true" or o.value is True):
            if isinstance(s, URIRef):
                deprecated.add(s)

    return deprecated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="Polku vanhaan old.ttl (TBC)")
    ap.add_argument("--new", required=True, help="Polku uuteen new.ttl, konversoitavaan (VocBench)")
    ap.add_argument("--out", required=True, help="Outputti TTL:nä")
    args = ap.parse_args()

    g_old = Graph()
    g_old.parse(args.old, format="turtle")

    g_new = Graph()
    g_new.parse(args.new, format="turtle")

    deprecated_subjects = build_deprecated_subject_set(g_new)

    g_out = Graph()

    # Kopioi nimiavaruusmäärittelyt vanhasta grafista
    for prefix, ns in g_old.namespaces():
        g_out.bind(prefix, ns)

    report = Counter()

    # VAIHE 1: Kopioi vanhasta grafista kaikki MUU paitsi YSO-käsitteet
    # Tämä säilyttää ontologian metatiedot, rakenteen ja vanhan
    # tyyliset määrittelyt, mutta ei yksittäisiä käsitteitä.
    for s, p, o in g_old:
        # Ohita blank nodet
        if isinstance(s, BNode):
            continue
        # Ohita YSO-käsitteet (tulevat uudesta)
        if is_yso_instance_uri(s):
            continue
        # Ohita vanha deprecated-collection (rakennetaan uudelleen)
        if s == DEPRECATED_CONCEPTS_OLD:
            continue
        g_out.add((s, p, o))


    # VAIHE 2: Käsittele uudesta grasfista YSO-käsitteet ja ontologia-URI
    # Tässä muunnetaan VocBenchin SKOS-pohjainen rakenne takaisin vanhaan
    # yso-meta-tyyliin, jossa käytetään RDFS-luokkia SKOS-käsitteiden tilalla.
    for s, p, o in g_new:
        # Blank nodet ohitettava.
        if isinstance(s, BNode):
            continue

        # Käsitellään ainoastaan: YSO-käsitteet, ontologia-URI ja deprecated-collection.
        if not (is_yso_instance_uri(s) or s == ONTOLOGY_URI or s == DEPRECATED_CONCEPTS_NEW):
            continue

        # Pudota eksplisiittisesti määritellyt, ei-toivotut subjektit.
        if str(s) in DROP_SUBJECTS:
            report["dropped_subject_explicit"] += 1
            continue

        # Muunna yso-meta-urit uudesta vanhaan nimiavaruuteen
        s2 = map_yso_meta_uri(s)
        p2 = map_yso_meta_uri(p)
        o2 = map_yso_meta_uri(o) if isinstance(o, URIRef) else o

        # käsittelyy deprecatedConcepts:ille
        # Vanhassa mallissa tämä on StructuringClass-tyyppinen raktaisu,
        # uudessa se on skos:Concept. Käsitellään kaikki sen predikaatit erikseen.

        if s == DEPRECATED_CONCEPTS_NEW:
        # Muunna deprecatedNarrower -> deprecatedSuperClassOf
        # Uudessa: "narrower" -> yksittäinen deprecated-käsite
        # Vanhassa: "superClassOf" -> yksittäinen deprecated-käsite
        # (Hierarkia käännetty)
            if p == YM_NEW.deprecatedNarrower:
                g_out.add((DEPRECATED_CONCEPTS_OLD, YM_OLD.deprecatedSuperClassOf, o2))
                report["map_deprecatedNarrower_to_deprecatedSuperClassOf"] += 1
                continue
            
            # Korvaa skosext:DeprecatedConcept tyyppi -> yso-meta:StructuringClass
            # Vanhassa tämä on "rakenteellinen" luokka, ei varsinainen käsite    
            if p == RDF.type and o == DEPRECATED_TYPE:
                g_out.add((DEPRECATED_CONCEPTS_OLD, RDF.type, STRUCTURING_CLASS))
                report["mapped_deprecatedConcepts_type_to_StructuringClass"] += 1
                continue

            # Poista skos:Concept-tyyppi (ei ole käsite vanhassa mallissa)
            if p == RDF.type and o == SKOS.Concept:
                report["dropped_skos_Concept_from_deprecatedConcepts"] += 1
                continue
            
            # Poista skos:inScheme (vanhassa ei käytetä SKOS-skeemoja)
            if p == SKOS.inScheme:
                report["dropped_skos_inScheme_from_deprecatedConcepts"] += 1
                continue
            
            # Poista skos:topConceptOf (ei tarvita vanhassa)
            if p == SKOS.topConceptOf:
                report["dropped_skos_topConceptOf_from_deprecatedConcepts"] += 1
                continue
            
            # Poista dct:modified (ei tallenneta muokkausaikoja tähän kohtaa)
            if p == DCTERMS.modified:
                report["dropped_dct_modified_from_deprecatedConcepts"] += 1
                continue
        
            # Muunna skos:scopeNote -> yso-meta:comment
            # Vanhassa käytetään omaa comment-predikaattia SKOS:n scopeNoten sijaan    
            if p == SKOS.scopeNote:
                g_out.add((DEPRECATED_CONCEPTS_OLD, YM_OLD.comment, o2))
                report["mapped_scopeNote_to_yso-meta_comment"] += 1
                continue
            
            # Kaikki muut deprecatedConcepts:in predikaatit sellaisenaan
            # (esim. owl:deprecated, skos:editorialNote)
            g_out.add((DEPRECATED_CONCEPTS_OLD, p2, o2))
            continue

        # Poista deprecatedBroader kokonaan (ei käytetä vanhassa)
        if p == YM_NEW.deprecatedBroader:
            report["dropped_deprecatedBroader"] += 1
            continue

        # rdf:type käsittelyt: muunnetaan SKOS-tyypit YSO-meta tyypeiksi
        if p == RDF.type:
            # Poista skos:Concept tyyppi (vanhassa käytetään RDFS-luokkia)
            if o == SKOS.Concept:
                report["dropped_type_skosConcept"] += 1
                continue

            # SKOS Collections ja ISO ThesaurusArrayt -> GroupConcept/DeprecatedGroupConcept
            # Vanhassa mallissa ryhmät toteutettu omilla luokilla
            if o == SKOS.Collection or o == ISO_THES.ThesaurusArray:
                cls = YM_OLD.DeprecatedGroupConcept if s in deprecated_subjects else YM_OLD.GroupConcept
                g_out.add((s2, RDF.type, cls))
                report["mapped_collection_to_groupconcept"] += 1
                continue

            # Poista skosext:DeprecatedConcept tyyppi (tieto säilyy muilla tavoin)
            if o == DEPRECATED_TYPE:
                report["dropped_type_skosextDeprecatedConcept"] += 1
                continue

            # Muut tyypit sellaisenaan
            g_out.add((s2, p2, o2))
            continue

        # SKOS-predikaattien käsittely ja muunnokset

        # Poista skos:inScheme (vanhassa ei käytetä scheme-rakennetta)
        if p == SKOS.inScheme:
            report["dropped_skos_inScheme"] += 1
            continue

        # Poista skos:narrower (vanhassa hierarkia ilmaistaan vain broader/subClassOf suunnassa)
        if p == SKOS.narrower:
            report["dropped_skos_narrower"] += 1
            continue

        # Poista skos:member (collection-membership hoidetaan toisin vanhassa)
        if p == SKOS.member:
            report["dropped_skos_member"] += 1
            continue

        # skos:broader -> rdfs:subClassOf (vanhassa käytetään RDFS-luokkahierarkiaa)
        if p == SKOS.broader:
            g_out.add((s2, RDFS.subClassOf, o2))
            report["mapped_skos_broader_to_rdfs_subClassOf"] += 1
            continue

        # YSO-meta custom-predikaatit

        # memberOf -> hasThematicGroup (ryhmittelyn ilmaisu vanhassa)
        if p == YM_NEW.memberOf:
            g_out.add((s2, YM_OLD.hasThematicGroup, o2))
            report["mapped_memberOf_to_hasThematicGroup"] += 1
            continue

        # skosext:partOf -> yso-meta:partOf
        if p == SKOSEXT.partOf:
            g_out.add((s2, YM_OLD.partOf, o2))
            report["mapped_skosext_partOf_to_yso_meta_partOf"] += 1
            continue

        # Mapping-suhteet muille ontologioille

        # skos:exactMatch -> peilaus:definedConcept (nämä vastaavuudet toiseen ontologiaan eivät ihan vielä auenneet)
        if p == SKOS.exactMatch:
            g_out.add((s2, PEILAUS_DEFINED, o2))
            report["mapped_skos_exactMatch_to_definedConcept"] += 1
            continue

        # Deprecated-käsitteiden suhteet

        # dcterms:isReplacedBy -> deprecatedReplacedBy
        if p == DCTERMS.isReplacedBy:
            g_out.add((s2, YM_OLD.deprecatedReplacedBy, o2))
            report["mapped_dct_isReplacedBy_to_deprecatedReplacedBy"] += 1
            continue

        # skos:relatedMatch -> deprecatedAssociativeRelation (assosiaatiosuhde reprekoidun ja toisen ontologian välillä)
        if p == SKOS.relatedMatch:
            g_out.add((s2, YM_OLD.deprecatedAssociativeRelation, o2))
            report["mapped_relatedMatch_to_deprecatedAssociativeRelation"] += 1
            continue

        # skos:broadMatch -> deprecatedSubClassOf (hierarkkinen suhde toiseen ontologiaan deprekoidun käsitteen osalta)
        if p == SKOS.broadMatch:
            g_out.add((s2, YM_OLD.deprecatedSubClassOf, o2))
            report["mapped_broadMatch_to_deprecatedSubClassOf"] += 1
            continue

        # Metatiedot

        # dc:source -> ysoSource
        if p == DC11.source:
            g_out.add((s2, YM_OLD.ysoSource, o2))
            report["mapped_dc_source_to_ysoSource_ambiguous"] += 1
            continue

        # Kaikki muut predikaatit sellaisenaan (labelit, määritelmät, yms. yms. etc)
        g_out.add((s2, p2, o2))

    # Ja sitten maaliin, serialisoidaan
    g_out.serialize(destination=args.out, format="turtle")

    print("Kirjoitettiin:", args.out)
    print("Triplejä:", len(g_out))
    print("Raportti:")
    for k, v in report.most_common():
        if v:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
