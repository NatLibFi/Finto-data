#!/usr/bin/env python3
import argparse
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, SKOS
from rdflib.util import guess_format

YSO_META = Namespace("http://www.yso.fi/onto/yso-meta/2007-03-02/")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main():
    args = parse_args()

    graph = Graph()
    input_format = guess_format(args.input)
    graph.parse(args.input, format=input_format)

    for s, p, o in list(graph):
        if isinstance(o, Literal) and o.language == "sme":
            graph.remove((s, p, o))
            new_literal = Literal(str(o), lang="se", datatype=o.datatype)
            graph.add((s, p, new_literal))
            print(f"Muutettiin kielitagi @se:ksi labelille {str(o)}")

    deprecated_concepts = YSO_META["deprecatedConcepts"]
    deprecated_concept_type = YSO_META["DeprecatedConcept"]
    structuring_class_type = YSO_META["StructuringClass"]

    if (deprecated_concepts, RDF.type, deprecated_concept_type) in graph:
        graph.remove((deprecated_concepts, RDF.type, deprecated_concept_type))
        graph.add((deprecated_concepts, RDF.type, structuring_class_type))
        print("Käsitteen yso-meta:deprecatedConcepts muutettiin tyypiksi yso-meta:StructuringClass")

    if (deprecated_concepts, SKOS.broader, deprecated_concepts) in graph:
        graph.remove((deprecated_concepts, SKOS.broader, deprecated_concepts))
        print("Poistettiin käsitteeltä yso-meta:deprecatedConcepts tarpeeton yläluokkasuhde")

    output_format = guess_format(args.output) or input_format or "xml"
    graph.serialize(destination=args.output, format=output_format)

    print("Korjaukset valmiit")


if __name__ == "__main__":
    main()
