from rdflib import Graph, Dataset, URIRef

fileA = "the-last.ttl"
fileB = "the-first.ttl"
output_file = "combined.trig"

graphA = URIRef("http://example.org/graphA")
graphB = URIRef("http://example.org/graphB")

dataset = Dataset()

gA = dataset.graph(graphA)
gA.parse(fileA, format="turtle")

gB = dataset.graph(graphB)
gB.parse(fileB, format="turtle")

dataset.serialize(destination=output_file, format="trig")

print(f"The YSOs in files {fileA} and {fileB} were combined into the file {output_file} as separate graphs.")

