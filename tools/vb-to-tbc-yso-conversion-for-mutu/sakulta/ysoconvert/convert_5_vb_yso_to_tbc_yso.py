#!/usr/bin/env python3
"""
Ajo:
  python3 convert_5_vb_yso_to_tbc_yso.py --old old.ttl --new new.ttl --out [jokin valitsemasi nimi].ttl
"""
import argparse
import os
from collections import Counter, defaultdict

from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS
from rdflib.util import guess_format

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

SKOSXL_NS = "http://www.w3.org/2008/05/skos-xl#"

YSO_BASE = "http://www.yso.fi/onto/yso/"

ONTOLOGY_URI = URIRef("http://www.yso.fi/onto/yso/")

# Deprekoitujen käsitteiden tyypit ja kokoelmat vanhassa ja uudessa mallissa 
DEPRECATED_TYPE = URIRef("http://purl.org/finnonto/schema/skosext#DeprecatedConcept")
# !! eri urit. Tarvitaan vaiheessa 2
DEPRECATED_CONCEPTS_NEW = URIRef(NEW_YM + "deprecatedConcepts")
DEPRECATED_CONCEPTS_OLD = URIRef(OLD_YM + "deprecatedConcepts")
STRUCTURING_CLASS = URIRef(OLD_YM + "StructuringClass")

# Juuret, jotka jätetään kokonaan pois tai epäselvät tapaukset
DROP_SUBJECTS = {
    "http://www.yso.fi/onto/allars/allars_juuri",
    "http://www.yso.fi/onto/ysa/ysa_juuri",
    "http://www.yso.fi/onto/allars/",
}

# tsekataan, että on todella todennäköisesti käsite
def is_yso_instance_uri(u: URIRef) -> bool:
    """Tarkistaa onko URI YSOn käsiteinstanssi (muotoa http://www.yso.fi/onto/yso/p...)"""
    return isinstance(u, URIRef) and str(u).startswith("http://www.yso.fi/onto/yso/p")

# Muuntaa VB:n yso-meta-nimiavaruuden TBC:n grand old...yso-meta/2007-03-02/-nimiavaruuteen 
# (kaikille predikaateille ja tyypeille)
def map_yso_meta_uri(term):
    if isinstance(term, URIRef):
        s = str(term)
        if s.startswith(NEW_YM):
            return URIRef(OLD_YM + s[len(NEW_YM):])
    return term

# Korjaa skos-xl-labelien resurssien urit: yso-meta/p[num]#tag -> yso/p[num]ag
def fix_skosxl_label_uri(u: URIRef) -> URIRef:
    s = str(u)
    if s.startswith(NEW_YM) and '#' in s:
        return URIRef(YSO_BASE + s[len(NEW_YM):])
    return u

# kerää kaikki VB:n deprekoidut käsitteet (owl:deprecated tai skosext:DeprecatedConcept)
# Tarvitaan broadMatch- ja tyyppimuunnosten haarautumiseen eli:
# Jos on deprekoitu -> deprecatedSubClassOf
# Jos ei ole deprekoitu -> broadMatch (TBC-malli)
# rdf:type:
#  - jos käsite on deprecated_aggregate_set:ssä -> deprecatedAggregateConcept
#  - jos ei ole -> normaali tyypin muunnos
# Lue: "deprecated_subjects"-joukko sisältää ehdot. Kkts. myöhemmin koodissa: viittaus 1 ja viittaus 2 
def build_deprecated_subject_set(g_new: Graph):
    deprecated = set()

    # Haetaan kaikki subjektit, joilla on owl:deprecated
    for s, _, _ in g_new.triples((None, OWL.deprecated, None)):
        if isinstance(s, URIRef):
            deprecated.add(s)

    # Haetaan kaikki skosext:DeprecatedConcept-tyyppiset
    for s, _, _ in g_new.triples((None, RDF.type, DEPRECATED_TYPE)):
        if isinstance(s, URIRef):
            deprecated.add(s)

    # Haetaan ne, joissa owl:deprecated = true
    for s, _, o in g_new.triples((None, OWL.deprecated, None)):
        if isinstance(o, Literal) and (str(o).lower() == "true" or o.value is True):
            if isinstance(s, URIRef):
                deprecated.add(s)

    return deprecated

# Kerää skos-xl-labeleiden resurssien urit vanhan graafin (vaiheessa 1) suodatusta varten.
def build_skosxl_subject_set(g: Graph) -> set:
    subjects = set()
    for s, p, o in g:
        if not isinstance(s, URIRef):
            continue
        # Uri sisältää #:n. Käsitteet, jotka osoittavat labeleihin, jätetään siis pois (tuli aiemmin vahingossa mukaan)
        if '#' not in str(s):
            continue
        if str(p).startswith(SKOSXL_NS):
            subjects.add(s)
        if isinstance(o, URIRef) and str(o).startswith(SKOSXL_NS):
            subjects.add(s)
    return subjects

# Päättele output-formaatti tiedostopäätteestä. Oletuksena turtle.
def resolve_output_format(filename: str) -> str:
    fmt = guess_format(filename)
    return fmt if fmt else "turtle"

# Kerää kaikki ThesaurusArray-resurssit VB-graafista (käytännössä: iso-thes:ThesaurusArray).
# Tarvitaan memberOf-kohdetyypin tarkistukseen ja yläkäsitteen päättelyyn
def build_thesaurus_array_set(g: Graph) -> set:
    return set(g.subjects(RDF.type, ISO_THES.ThesaurusArray))

# Kerää DeprecatedAggregateConcept-urit TBC-versiosta, mallista.
# VB:ssä nämä näkyvät pelkästään DeprecatedConcept-tyyppisinä ja AggregateConcept-tieto
# on kadonnut VB:een siirryttäessä. Tyyppi on siis pöllittävä suoraan TBC-versiosta
def build_deprecated_aggregate_set(g_old: Graph) -> set:
    # Mä rakastan tätä RdfLibin kaikkiin, johonkin triplen jäseniin kohdistettavan toimenpiteen
    # mahdollistumista. Voisiko enää ytimekkäämpää olla!
    DAC = URIRef(OLD_YM + "DeprecatedAggregateConcept")
    return set(g_old.subjects(RDF.type, DAC))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="Polku vanhaan old.ttl (TBC)")
    ap.add_argument("--new", required=True, help="Polku uuteen new.ttl, konversoitavaan (VocBench)")
    ap.add_argument("--out", required=True, help="Outputti TTL:nä")
    args = ap.parse_args()

    g_old = Graph()
    g_old.parse(args.old) # päättele formaatti automaattisesti

    g_new = Graph()
    g_new.parse(args.new) # päättele formaatti automaattisesti

    deprecated_subjects = build_deprecated_subject_set(g_new)

    # Kerää skos-xl-subjektit myöhempää vanhasta mukaan vedettävien subjektien poissuodatusta varten
    skosxl_subjects = build_skosxl_subject_set(g_old)

    # Kerää ThesaurusArray-resurssit
    # Käytetään myöhemmin memberOf-kohdetyypin tarkistukseen, jota tarvitaan hierarkian päättelyyn
    thesaurus_array_set = build_thesaurus_array_set(g_new)

    # Kerää DeprecatedAggregateConceptien urit tbc-versiosta.
    # Näiden tyyppi kirjoitetaan suoraan outputiin koska,
    # AggregateConcept-tieto on kadonnut VB:hen siirryttäessä ja pitää ottaa mallitiedostosta.
    deprecated_aggregate_set = build_deprecated_aggregate_set(g_old)

    # Tämä on ollut koko skriptin devaamisessa hankalin asia, mutta aika simppeli toteutus lopulta.
    # VB:ssä ja TBC:ssä hierarkia on rakennettu eri tavalla GroupConceptien kohdalla:
    # VB:ssä p1115 (kodintekstiilit) osoittaa suoraan yläkäsitteeseen, eli:
    # yso:p1115  skos:broader  yso:p13512   (tekstiilit)
    # yso:p1115  yso-meta:memberOf  yso:p10093   (tekstiilit käyttöpaikan mukaan)
    # TBC:ssä p1115 osoittaa GroupConceptiin, joka puolestaan osoittaa ylöspäin:
    # yso:p1115   rdfs:subClassOf  yso:p10093   (GroupConcept)
    # yso:p10093  rdfs:subClassOf  yso:p13512   (tekstiilit)
    # Nimetään toteutus vaikka interception:iksi eli tarkoittaa sitä, että skripti nappaa suoran skos:broader-muunnoksen
    # ja "ohjaa" sen GroupConceptin kautta, kun seuraava ehto täyttyy:
    # käsitteellä C on yso-meta:memberOf -> ThesaurusArray T
    # JA TBC:ssä T rdfs:subClassOf B
    # JA VB:ssä C skos:broader B
    # -> kirjoitetaan reverse fileeseen: C rdfs:subClassOf T (ei C rdfs:subClassOf B)
    tbc_gc_parents = {}
    for gc in g_old.subjects(RDF.type, YM_OLD.GroupConcept):
        sc = list(g_old.objects(gc, RDFS.subClassOf))
        tbc_gc_parents[gc] = {"subClassOf": sc[0] if sc else None, "deprecatedSubClassOf": None}
    for gc in g_old.subjects(RDF.type, YM_OLD.DeprecatedGroupConcept):
        # Tässä tuli jstk syystä ajatusvirhe, koska deprekoidut eivät ole normisti hierarkiassa, mutta testauksen
        # viemän ajan takia jätetään näin, kun ei oikeastaan haittaakaan.
        sc = list(g_old.objects(gc, RDFS.subClassOf))
        dsc = list(g_old.objects(gc, YM_OLD.deprecatedSubClassOf))
        tbc_gc_parents[gc] = {
            "subClassOf": sc[0] if sc else None,
            "deprecatedSubClassOf": dsc[0] if dsc else None,
        }

    # Käänteistä meininkiä: ThesaurusArray -> sen TBC-mallin mukainen yläkäsite (sen uri).
    # Jos broader-kohde on TA:n yläkäsite tbc-mallissa, niin
    # käsite osoittaa suoraan TA:han eikä yläkäsitteeseen.
    ta_to_tbc_parent = {}
    for ta in thesaurus_array_set:
        if ta in tbc_gc_parents and tbc_gc_parents[ta]["subClassOf"]:
            ta_to_tbc_parent[ta] = tbc_gc_parents[ta]["subClassOf"]

    # ThesaurusArray-setti: VB:n memberOf-relaatioista
    concept_to_ta = defaultdict(set)
    for ta in thesaurus_array_set:
        for member in g_new.objects(ta, SKOS.member):
            concept_to_ta[member].add(ta)

    # TBC:n StructuringClassit (joilla siis yso:p[num]), jotka eivöt löydy VB:stä, 
    # kopioidaan sellaisenaan tbc-maalista, kuten vaikka yso:p61
    SC_OLD_URI = YM_OLD.StructuringClass
    tbc_only_structuring = set()
    for sc_inst in g_old.subjects(RDF.type, SC_OLD_URI):
        if is_yso_instance_uri(sc_inst) and len(list(g_new.predicate_objects(sc_inst))) == 0:
            tbc_only_structuring.add(sc_inst)

    # Poimi VB:n ei-yso:p[num]-tyyppiset StructuringClass "käsitteet" (esim. yso-update:muuttuneetEn), 
    # jotka eivät muuten läpäise myöhempi käsittelujä eli ovat hieman nonstandard-osastoa tässä kontekstissa
    SC_NEW_URI = YM_NEW.StructuringClass
    vb_nonstandard_sc = set(
        s for s in g_new.subjects(RDF.type, SC_NEW_URI)
        if not is_yso_instance_uri(s)
    )

    g_out = Graph()

    # Kopioi nimiavaruusmäärittelyt vanhasta tbc-ajan graafista
    for prefix, ns in g_old.namespaces():
        g_out.bind(prefix, ns)

    report = Counter()

    # Vaihe 1: Kopioi vanhasta tbc-graafista kaikki muu, paitsi YSO-käsitteet
    # eli säilytetään metatiedot, rakenne ja old style määrittelyt, 
    # mutta ei yksittäisiä käsitteitä.
    for s, p, o in g_old:
        # Ohita blank nodet
        if isinstance(s, BNode):
            continue
        # Kopioi koko tbc-ajan -graafi outputiin, paitsi yso:p[num]-käsitteet, koska ovat dataa ja 
        # tulevat VB:stä):
        # - deprecatedConcepts-härdelli (rakennetaan uudelleen)
        # - skos-xl-labeleiden resurssit (korvataan VB:n versioilla) eli on poikkeus! 
        # - vain tbc:ssä olleet StructuringClass-apuluokat (yso:p61 jne) kopioidaan
        if is_yso_instance_uri(s) and s not in tbc_only_structuring:
            continue
        # Ohita vanha deprecated-collection, joka rakennetaan uudelleen
        if s == DEPRECATED_CONCEPTS_OLD:
            continue
        # Ohita skos-xl-labelien resurssit
        if s in skosxl_subjects:
            report["dropped_skosxl_label_resource"] += 1
            continue
        # Ohita myös triplet, joissa predikaatti tai objekti on skos-xl-nimiavaruudessa
        if str(p).startswith(SKOSXL_NS) or (isinstance(o, URIRef) and str(o).startswith(SKOSXL_NS)):
            report["dropped_skosxl_triple"] += 1
            continue
        g_out.add((s, p, o))


    # VAIHE 2: Käsittele "uudesta" VB-graafista YSO-käsitteet ja ontologia-URI (http://www.yso.fi/onto/yso/).
    # Käännetään VocBenchin SKOS-pohjainen rakenne takaisin vanhaan
    # yso-meta-tyyliin, jossa käytetään RDFS-luokkia SKOS-käsitteiden tilalla.
    # Käsittele yso:p[num]-urit, ontologia-URI, deprecatedConcepts- ja ei-standardit apuluokat
    for s, p, o in g_new:
        if isinstance(s, BNode):
            continue

        # JATKA TÄSTÄ
        if not (is_yso_instance_uri(s) or s == ONTOLOGY_URI or s == DEPRECATED_CONCEPTS_NEW
                or s in vb_nonstandard_sc):
            continue

        if str(s) in DROP_SUBJECTS:
            report["dropped_subject_explicit"] += 1
            continue

        s2 = map_yso_meta_uri(s)
        p2 = map_yso_meta_uri(p)

        if isinstance(o, URIRef):
            fixed = fix_skosxl_label_uri(o)
            if fixed is not o:
                o2 = fixed
            else:
                o2 = map_yso_meta_uri(o)
        else:
            o2 = o


        if s == DEPRECATED_CONCEPTS_NEW:
            if p == YM_NEW.deprecatedNarrower:
                g_out.add((DEPRECATED_CONCEPTS_OLD, YM_OLD.deprecatedSuperClassOf, o2))
                report["map_deprecatedNarrower_to_deprecatedSuperClassOf"] += 1
                continue
            
            if p == RDF.type and o == DEPRECATED_TYPE:
                g_out.add((DEPRECATED_CONCEPTS_OLD, RDF.type, STRUCTURING_CLASS))
                report["mapped_deprecatedConcepts_type_to_StructuringClass"] += 1
                continue

            if p == RDF.type and o == SKOS.Concept:
                report["dropped_skos_Concept_from_deprecatedConcepts"] += 1
                continue
            
            if p == SKOS.inScheme:
                report["dropped_skos_inScheme_from_deprecatedConcepts"] += 1
                continue
            
            if p == SKOS.topConceptOf:
                report["dropped_skos_topConceptOf_from_deprecatedConcepts"] += 1
                continue
            
            if p == DCTERMS.modified:
                report["dropped_dct_modified_from_deprecatedConcepts"] += 1
                continue
        
            if p == SKOS.scopeNote:
                g_out.add((DEPRECATED_CONCEPTS_OLD, YM_OLD.comment, o2))
                report["mapped_scopeNote_to_yso-meta_comment"] += 1
                continue
            
            g_out.add((DEPRECATED_CONCEPTS_OLD, p2, o2))
            continue

        if p == YM_NEW.deprecatedBroader:
            g_out.add((s2, YM_OLD.deprecatedSubClassOf, o2))
            report["mapped_deprecatedBroader_to_deprecatedSubClassOf"] += 1
            continue

        if p == RDF.type:
            if o == SKOS.Concept:
                report["dropped_type_skosConcept"] += 1
                continue

            if o == SKOS.Collection:
                report["dropped_type_skosCollection"] += 1
                continue

            if o == ISO_THES.ThesaurusArray:
                cls = YM_OLD.DeprecatedGroupConcept if s in deprecated_subjects else YM_OLD.GroupConcept
                g_out.add((s2, RDF.type, cls))
                report["mapped_ThesaurusArray_to_GroupConcept"] += 1
                continue

            if o == ISO_THES.ConceptGroup:
                g_out.add((s2, RDF.type, YM_OLD.ThematicGroup))
                report["mapped_ConceptGroup_to_ThematicGroup"] += 1
                continue

            if o == YM_NEW.ConceptGroup:
                g_out.add((s2, RDF.type, YM_OLD.ThematicGroup))
                report["mapped_vb_ConceptGroup_to_ThematicGroup"] += 1
                continue

            if o == DEPRECATED_TYPE:
                report["dropped_type_skosextDeprecatedConcept"] += 1
                continue

            if o == SKOS.ConceptScheme:
                report["dropped_type_skosConceptScheme"] += 1
                continue

            # viittaus 1:
            if s in deprecated_aggregate_set:
                g_out.add((s2, RDF.type, YM_OLD.DeprecatedAggregateConcept))
                report["mapped_type_to_DeprecatedAggregateConcept"] += 1
                continue

            # Muut tyypit sellaisenaan
            g_out.add((s2, p2, o2))
            continue

        if p == SKOS.inScheme:
            report["dropped_skos_inScheme"] += 1
            continue

        if p == SKOS.narrower:
            report["dropped_skos_narrower"] += 1
            continue

        if p == SKOS.broaderTransitive:
            report["dropped_skos_broaderTransitive"] += 1
            continue

        if p == SKOS.member:
            report["dropped_skos_member"] += 1
            continue

        if p == SKOS.broader:
            intercepted = False
            for ta in concept_to_ta.get(s, set()):
                if ta_to_tbc_parent.get(ta) == o:
                    g_out.add((s2, RDFS.subClassOf, ta))
                    report["mapped_skos_broader_via_groupconcept"] += 1
                    intercepted = True
                    break
            if not intercepted:
                g_out.add((s2, RDFS.subClassOf, o2))
                report["mapped_skos_broader_to_rdfs_subClassOf"] += 1
            continue

        # YSO-metan kustoimidut predikaatit

        if p == YM_NEW.memberOf:
            if o in thesaurus_array_set:
                report["dropped_memberOf_to_ThesaurusArray"] += 1
            else:
                g_out.add((s2, YM_OLD.hasThematicGroup, o2))
                report["mapped_memberOf_to_hasThematicGroup"] += 1
            continue

        if p == SKOSEXT.partOf:
            g_out.add((s2, YM_OLD.partOf, o2))
            report["mapped_skosext_partOf_to_yso_meta_partOf"] += 1
            continue

        if p == SKOS.exactMatch:
            g_out.add((s2, PEILAUS_DEFINED, o2))
            report["mapped_skos_exactMatch_to_definedConcept"] += 1
            continue

        if p == DCTERMS.isReplacedBy:
            g_out.add((s2, YM_OLD.deprecatedReplacedBy, o2))
            report["mapped_dct_isReplacedBy_to_deprecatedReplacedBy"] += 1
            continue

        if p == SKOS.relatedMatch:
            g_out.add((s2, YM_OLD.deprecatedAssociativeRelation, o2))
            report["mapped_relatedMatch_to_deprecatedAssociativeRelation"] += 1
            continue

        # viittaus 2
        if p == SKOS.broadMatch:
            if s in deprecated_subjects:
                g_out.add((s2, YM_OLD.deprecatedSubClassOf, o2))
                report["mapped_broadMatch_to_deprecatedSubClassOf"] += 1
            else:
                g_out.add((s2, SKOS.broadMatch, o2))
                report["kept_broadMatch_on_normal_concept"] += 1
            continue

        if p == YM_NEW.deprecatedNarrower:
            report["dropped_deprecatedNarrower_on_concept"] += 1
            continue

        # Metatiedot

        if p == DC11.source:
            report["dropped_dc_source"] += 1
            continue

        if p == DCTERMS.modified:
            report["dropped_dct_modified"] += 1
            continue

        if p == SKOSEXT.hasPart:
            report["dropped_skosext_hasPart"] += 1
            continue

        if p == DC11.coverage:
            report["dropped_dc_coverage"] += 1
            continue

        if p == ISO_THES.broaderPartitive:
            report["dropped_iso_thes_broaderPartitive"] += 1
            continue

        if p == SKOS.hasTopConcept:
            report["dropped_skos_hasTopConcept"] += 1
            continue

        if p == SKOS.topConceptOf:
            report["dropped_skos_topConceptOf"] += 1
            continue

        g_out.add((s2, p2, o2))

    # VaihE 3: ThesaurusArray-käsitteiden yläkäsitteet
    for ta in thesaurus_array_set:
        if ta in tbc_gc_parents:
            info = tbc_gc_parents[ta]
            if info["subClassOf"]:
                g_out.add((ta, RDFS.subClassOf, info["subClassOf"]))
            if info["deprecatedSubClassOf"]:
                g_out.add((ta, YM_OLD.deprecatedSubClassOf, info["deprecatedSubClassOf"]))
            report["ta_hierarchy_from_tbc"] += 1
        else:
            members = list(g_new.objects(ta, SKOS.member))
            broaders = Counter()
            for m in members:
                for b in g_new.objects(m, SKOS.broader):
                    broaders[b] += 1
            if len(broaders) == 1:
                parent = list(broaders.keys())[0]
                g_out.add((ta, RDFS.subClassOf, parent))
                report["ta_hierarchy_inferred_single"] += 1
            elif len(broaders) > 1:
                parent = broaders.most_common(1)[0][0]
                g_out.add((ta, RDFS.subClassOf, parent))
                report["ta_hierarchy_inferred_most_common"] += 1
            else:
                report["ta_hierarchy_missing"] += 1

    skosxl_subjects_vb = build_skosxl_subject_set(g_new)
    for vb_subj in skosxl_subjects_vb:
        if not isinstance(vb_subj, URIRef):
            continue
        s_str = str(vb_subj)
        if s_str.startswith(NEW_YM) and '#' in s_str:
            new_subj = URIRef(YSO_BASE + s_str[len(NEW_YM):])
        else:
            new_subj = vb_subj
        for vb_p, vb_o in g_new.predicate_objects(vb_subj):
            if vb_p == DCTERMS.modified:
                report["dropped_dct_modified_skosxl"] += 1
                continue
            p2 = map_yso_meta_uri(vb_p)
            if isinstance(vb_o, URIRef):
                fixed = fix_skosxl_label_uri(vb_o)
                o2 = fixed if fixed is not vb_o else map_yso_meta_uri(vb_o)
            else:
                o2 = vb_o
            g_out.add((new_subj, p2, o2))
        report["copied_skosxl_label_resource"] += 1

    out_format = resolve_output_format(args.out)
    g_out.serialize(destination=args.out, format=out_format)

    print("Kirjoitettiin:", args.out)
    print("Formaatti:", out_format)
    print("Triplejä:", len(g_out))
    print("Raportti:")
    for k, v in report.most_common():
        if v:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
