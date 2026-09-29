#!/usr/bin/env python3
"""Build a timestamped FinMeSH SKOS publication from current official sources.

The script discovers the current Svensk MeSH text-file export from the KIB
website and the same-year NLM Descriptor XML release, downloads both in memory,
and builds a fresh graph. The client-provided Finnish MASTER file is the only
content input that cannot be discovered publicly and must be supplied or be the
single MASTER*.txt file beside this script/current working directory.

The local mesh-skos-new.ttl is read as the stable data-model reference and
comparison baseline only. Its concept values are never copied into the output.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import io
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

KIB_INFO_URL = "https://mesh.kib.ki.se/info/om-webbplatsen"
NLM_XML_DIRECTORY_URL = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/"
DC = Namespace("http://purl.org/dc/elements/1.1/")
MESH_BASE = "http://www.yso.fi/onto/mesh/"
MESH_NS = Namespace(MESH_BASE)
MESH = URIRef(MESH_BASE)
MESHV_BASE = "http://id.nlm.nih.gov/mesh/vocab#"
MESHV_NS = Namespace(MESHV_BASE)
YEAR_URI_RE = re.compile(r"/mesh/\d{4}/")
REQUIRED_SOURCE_FILES = (
    "terms.csv",
    "synonyms.csv",
    "entryterms.csv",
    "mesh_numbers.csv",
    "scope_notes.csv",
    "swe_scope_notes.csv",
)
USER_AGENT = "FinMeSHPublisher/1.0 (source discovery; contact the local operator)"


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[Tuple[str, str]] = []
        self._href: Optional[str] = None
        self._text: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            text = data.strip()
            if text:
                self._text.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((" ".join(self._text), self._href))
            self._href = None
            self._text = []


def fetch_bytes(url: str, *, timeout: int = 90) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Download failed from {url}: {exc}") from exc


def fetch_links(url: str) -> List[Tuple[str, str]]:
    body = fetch_bytes(url).decode("utf-8", "replace")
    parser = AnchorParser()
    parser.feed(body)
    return parser.links


def discover_kib_text_export(requested_year: Optional[int]) -> Tuple[int, str, bytes]:
    info_links = fetch_links(KIB_INFO_URL)
    exports: Dict[int, str] = {}
    for _label, href in info_links:
        match = re.search(r"/(\d{4})_export/text_files/?$", href)
        if match:
            exports[int(match.group(1))] = urllib.parse.urljoin(KIB_INFO_URL, href)

    if requested_year is not None:
        if requested_year not in exports:
            available = ", ".join(map(str, sorted(exports))) or "none"
            raise RuntimeError(
                f"KIB's official page does not link to a {requested_year} text export. "
                f"Years linked from {KIB_INFO_URL}: {available}. Check the KIB page or "
                "ask KIB for the missing year's text-file export."
            )
        year = requested_year
    elif exports:
        year = max(exports)
    else:
        raise RuntimeError(
            f"No annual text-file download link was found on {KIB_INFO_URL}. "
            "Check that page for the current 'tab-separerade filer' link."
        )

    listing_url = exports[year]
    zip_links = [
        urllib.parse.urljoin(listing_url, href)
        for _label, href in fetch_links(listing_url)
        if urllib.parse.urlparse(href).path.lower().endswith(".zip")
    ]
    preferred = [url for url in zip_links if "textfiler" in url.lower() or "text_files" in url.lower()]
    candidates = preferred or zip_links
    if len(candidates) != 1:
        found = "\n  ".join(candidates) if candidates else "(no ZIP links found)"
        raise RuntimeError(
            f"Could not identify one unambiguous KIB text export ZIP in {listing_url}.\n"
            f"Found:\n  {found}\nOpen the official KIB page and select the annual tab-separated text export."
        )

    zip_url = candidates[0]
    archive_bytes = fetch_bytes(zip_url, timeout=180)
    return year, zip_url, archive_bytes


def read_kib_tables(archive_bytes: bytes, archive_url: str) -> Dict[str, bytes]:
    tables: Dict[str, bytes] = {}
    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as exc:
        raise RuntimeError(f"KIB download is not a valid ZIP archive: {archive_url}") from exc

    with archive:
        for member in archive.infolist():
            basename = Path(member.filename).name.lower()
            if basename in REQUIRED_SOURCE_FILES:
                if member.file_size > 100_000_000:
                    raise RuntimeError(f"Unexpectedly large source table in KIB archive: {member.filename}")
                tables[basename] = archive.read(member)

    missing = [name for name in REQUIRED_SOURCE_FILES if name not in tables]
    if missing:
        raise RuntimeError(
            f"The KIB archive {archive_url} does not contain required table(s): {', '.join(missing)}. "
            "Check the archive contents and the KIB export format before continuing."
        )
    return tables


def discover_nlm_descriptor_xml(requested_year: int) -> Tuple[str, bytes]:
    links = fetch_links("https://www.nlm.nih.gov/databases/download/mesh.html")
    directory = next(
        (urllib.parse.urljoin("https://www.nlm.nih.gov/databases/download/mesh.html", href)
         for _label, href in links if "xml format" in _label.lower()),
        NLM_XML_DIRECTORY_URL,
    )
    listing = fetch_links(directory)
    expected_name = f"desc{requested_year}.gz"
    source_url = next(
        (urllib.parse.urljoin(directory, href) for _label, href in listing
         if Path(urllib.parse.urlparse(href).path).name.lower() == expected_name),
        None,
    )
    if source_url is None:
        available = sorted({
            match.group(1)
            for _label, href in listing
            if (match := re.fullmatch(r"desc(\d{4})\.gz", Path(urllib.parse.urlparse(href).path).name.lower()))
        })
        raise RuntimeError(
            f"NLM does not currently publish {expected_name} in its official XML directory {directory}. "
            f"Available descriptor years: {', '.join(available) or 'none'}. "
            f"The KIB text export is for {requested_year}, so using another year's dates would be unsafe. "
            "Ask NLM/KIB for the matching-year Descriptor XML (descYEAR.gz); do not reuse an older date file."
        )
    return source_url, fetch_bytes(source_url, timeout=240)


def csv_rows(data: bytes, source_name: str, delimiter: str = "\t"):
    try:
        text = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8-sig", newline="")
        return list(csv.DictReader(text, delimiter=delimiter))
    except (UnicodeError, csv.Error) as exc:
        raise RuntimeError(f"Could not parse {source_name} as UTF-8 tab-separated data: {exc}") from exc


def clean_field(row: dict, name: str) -> str:
    return (row.get(name) or "").strip().strip('"')


def parse_master(path: Path) -> Dict[str, Dict[str, List[str]]]:
    groups: List[List[str]] = []
    current: List[str] = []
    for raw in path.read_text(encoding="utf-8-sig", errors="strict").splitlines():
        line = raw.strip()
        if not line:
            if current:
                groups.append(current)
                current = []
        else:
            current.append(line)
    if current:
        groups.append(current)

    data: Dict[str, Dict[str, List[str]]] = {}
    for group in groups:
        if len(group) < 2:
            continue
        english = group[0]
        data[norm(english)] = {"pref": group[1], "alts": group[2:]}
    if not data:
        raise RuntimeError(f"No MASTER label groups found in {path}")
    return data


def norm(value: str) -> str:
    value = value.strip().replace("&", " and ").replace("-", " ")
    return re.sub(r"\s+", " ", value).casefold()


def read_terms(data: bytes) -> Dict[str, Dict[str, str]]:
    result = {}
    for row in csv_rows(data, "terms.csv"):
        mesh_id = clean_field(row, "Mesh_UI") or clean_field(row, '\ufeff"Mesh_UI"')
        if mesh_id:
            result[mesh_id] = {
                "en": clean_field(row, "Mesh_eng"),
                "sv": clean_field(row, "Mesh_swe"),
            }
    return result


def read_grouped_table(data: bytes, id_column: str, value_column: str) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for row in csv_rows(data, Path(value_column).name):
        mesh_id = clean_field(row, id_column)
        value = clean_field(row, value_column)
        if mesh_id and value:
            result.setdefault(mesh_id, []).append(value)
    return result


def read_scope_notes(data: bytes) -> Dict[str, Dict[str, str]]:
    result: Dict[str, Dict[str, str]] = {}
    for row in csv_rows(data, "scope_notes.csv"):
        mesh_id = clean_field(row, "Mesh_UI")
        note = clean_field(row, "Scope_Note")
        if mesh_id and note:
            result.setdefault(mesh_id, {})["en"] = note
    return result


def read_swedish_scope_notes(data: bytes) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for row in csv_rows(data, "swe_scope_notes.csv"):
        mesh_id = clean_field(row, "Mesh_UI")
        note = clean_field(row, "Scope_Note")
        if mesh_id and note:
            result[mesh_id] = note
    return result


def read_mesh_numbers(data: bytes) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for row in csv_rows(data, "mesh_numbers.csv"):
        mesh_id = clean_field(row, "Mesh_UI")
        number = clean_field(row, "Mesh_No")
        if mesh_id and number:
            result.setdefault(mesh_id, []).append(number)
    return result


def hierarchy_links(numbers: Dict[str, List[str]]) -> Iterable[Tuple[str, str]]:
    number_to_ids: Dict[str, set] = {}
    for mesh_id, mesh_numbers in numbers.items():
        for number in mesh_numbers:
            number_to_ids.setdefault(number, set()).add(mesh_id)
    for mesh_id, mesh_numbers in numbers.items():
        for number in mesh_numbers:
            parts = number.split(".")
            for index in range(len(parts) - 1, 0, -1):
                parents = number_to_ids.get(".".join(parts[:index]), set())
                if parents:
                    for parent_id in parents:
                        if parent_id != mesh_id:
                            yield mesh_id, parent_id
                    break


def local_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def child(element: ET.Element, name: str) -> Optional[ET.Element]:
    return next((item for item in element if local_name(item) == name), None)


def text_child(element: Optional[ET.Element], name: str) -> str:
    if element is None:
        return ""
    found = child(element, name)
    return (found.text or "").strip() if found is not None else ""


def date_child(record: ET.Element, name: str) -> Optional[str]:
    date_element = child(record, name)
    if date_element is None:
        return None
    year = text_child(date_element, "Year")
    month = text_child(date_element, "Month")
    day = text_child(date_element, "Day")
    if not (year and month and day):
        return None
    try:
        return dt.date(int(year), int(month), int(day)).isoformat()
    except ValueError:
        return None


def read_nlm_descriptors(xml_gzip: bytes) -> Dict[str, Dict[str, object]]:
    descriptors: Dict[str, Dict[str, object]] = {}
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(xml_gzip)) as xml_stream:
            for _event, record in ET.iterparse(xml_stream, events=("end",)):
                if local_name(record) != "DescriptorRecord":
                    continue
                mesh_id = text_child(record, "DescriptorUI")
                name_element = child(record, "DescriptorName")
                english = text_child(name_element, "String")
                tree_list = child(record, "TreeNumberList")
                tree_numbers = [
                    (node.text or "").strip()
                    for node in (tree_list if tree_list is not None else [])
                    if local_name(node) == "TreeNumber" and (node.text or "").strip()
                ]
                created = date_child(record, "DateIntroduced")
                modified = date_child(record, "LastUpdated")
                if mesh_id:
                    descriptors[mesh_id] = {
                        "en": english,
                        "tree_numbers": tree_numbers,
                        "created": created,
                        "modified": modified,
                    }
                record.clear()
    except (OSError, ET.ParseError) as exc:
        raise RuntimeError(f"Could not parse the downloaded NLM Descriptor XML: {exc}") from exc
    if not descriptors:
        raise RuntimeError("The downloaded NLM XML contained no DescriptorRecord entries.")
    return descriptors


def discover_master(explicit: Optional[Path], script_dir: Path) -> Path:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise RuntimeError(f"MASTER file does not exist: {path}")
        return path

    candidates = set()
    for directory in {Path.cwd(), script_dir}:
        candidates.update(path.resolve() for path in directory.glob("MASTER*_Fintoon.txt") if path.is_file())
    if len(candidates) == 1:
        return next(iter(candidates))
    if not candidates:
        raise RuntimeError(
            "Could not find a client-provided MASTER*_Fintoon.txt file beside the script or in the current directory. "
            "This Finnish translation input is not public and cannot be fetched automatically. Supply it with --master PATH."
        )
    listed = "\n  ".join(map(str, sorted(candidates)))
    raise RuntimeError(f"More than one MASTER file was found; select the current one with --master PATH:\n  {listed}")


def add_literal(graph: Graph, subject: URIRef, predicate, value: str, language: str) -> None:
    if value and value.strip():
        graph.add((subject, predicate, Literal(value.strip(), lang=language)))


def add_scheme_metadata(graph: Graph, reference: Graph, release_year: int) -> None:
    generated_predicates = {SKOS.hasTopConcept, DCTERMS.modified, DC.description}
    for predicate, value in reference.predicate_objects(MESH):
        if predicate not in generated_predicates:
            graph.add((MESH, predicate, value))

    descriptions = {
        "en": (
            f"Medical Subject Headings (MeSH) is a structured thesaurus in medicine. "
            f"This SKOS version is based on the {release_year} MeSH release and includes "
            "the Finnish FinMeSH translation. MeSH is published and updated annually by "
            "the U.S. National Library of Medicine."
        ),
        "fi": (
            f"Medical Subject Headings (MeSH) on lääketieteen jäsennelty asiasanasto. "
            f"Tämä SKOS-muotoinen versio perustuu vuoden {release_year} MeSHiin ja sisältää "
            "suomenkielisen FinMeSH-käännöksen. MeSHiä julkaisee ja päivittää vuosittain "
            "Yhdysvaltain National Library of Medicine."
        ),
        "sv": (
            f"Medical Subject Headings (MeSH) är en strukturerad tesaurus inom medicin. "
            f"Denna SKOS-version baseras på {release_year} års MeSH-utgåva och innehåller "
            "den finska FinMeSH-översättningen. MeSH publiceras och uppdateras årligen av "
            "U.S. National Library of Medicine."
        ),
    }
    for language, description in descriptions.items():
        graph.add((MESH, DC.description, Literal(description, lang=language)))

    modified = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    graph.add((MESH, DCTERMS.modified, Literal(modified, datatype=XSD.dateTime)))


def build_graph(
    tables: Dict[str, bytes],
    descriptors: Dict[str, Dict[str, object]],
    master_path: Path,
    reference: Graph,
    release_year: int,
):
    terms = read_terms(tables["terms.csv"])
    synonyms = read_grouped_table(tables["synonyms.csv"], "Mesh_UI", "Synonym")
    entryterms = read_grouped_table(tables["entryterms.csv"], "Mesh_UI", "DESCRIPTOR")
    numbers = read_mesh_numbers(tables["mesh_numbers.csv"])
    english_notes = read_scope_notes(tables["scope_notes.csv"])
    swedish_notes = read_swedish_scope_notes(tables["swe_scope_notes.csv"])
    master = parse_master(master_path)

    descriptor_ids = set(descriptors)
    term_ids = set(terms)
    ids_without_terms = descriptor_ids - term_ids
    ids_outside_nlm = term_ids - descriptor_ids
    if ids_without_terms or ids_outside_nlm:
        details = []
        if ids_without_terms:
            details.append(f"NLM descriptors absent from KIB terms.csv ({len(ids_without_terms)}): {', '.join(sorted(ids_without_terms)[:20])}")
        if ids_outside_nlm:
            details.append(f"KIB terms absent from same-year NLM descriptors ({len(ids_outside_nlm)}): {', '.join(sorted(ids_outside_nlm)[:20])}")
        raise RuntimeError("Source ID sets do not match; refusing to publish incomplete or mixed-year data. " + "; ".join(details))

    missing_data = []
    master_misses = []
    for mesh_id in sorted(descriptor_ids):
        term = terms[mesh_id]
        english = term["en"]
        if not english:
            missing_data.append(f"{mesh_id}: English preferred label missing from KIB terms.csv")
        if not master.get(norm(english)):
            master_misses.append(f"{mesh_id} ({english})")
        record = descriptors[mesh_id]
        if not record["created"] or not record["modified"]:
            missing_data.append(f"{mesh_id}: DateIntroduced/LastUpdated missing from same-year NLM XML")
    if missing_data or master_misses:
        details = missing_data[:30] + [f"MASTER has no Finnish entry for {item}" for item in master_misses[:30]]
        extra = len(missing_data) + len(master_misses) - len(details)
        suffix = f"\n... and {extra} more issue(s)" if extra > 0 else ""
        raise RuntimeError(
            "Required current-year source data is incomplete; no output was written:\n  "
            + "\n  ".join(details) + suffix
            + "\nCheck the KIB export, matching NLM descYEAR.gz and client-provided MASTER file."
        )

    graph = Graph()
    add_scheme_metadata(graph, reference, release_year)

    for mesh_id in sorted(descriptor_ids):
        subject = MESH_NS[mesh_id]
        record = descriptors[mesh_id]
        item = terms[mesh_id]
        master_entry = master[norm(item["en"])]

        graph.add((subject, RDF.type, SKOS.Concept))
        graph.add((subject, RDF.type, MESHV_NS.TopicalDescriptor))
        graph.add((subject, SKOS.inScheme, MESH))
        graph.add((subject, SKOS.exactMatch, URIRef(f"http://id.nlm.nih.gov/mesh/{mesh_id}")))
        add_literal(graph, subject, SKOS.prefLabel, item["en"], "en")
        add_literal(graph, subject, SKOS.prefLabel, master_entry["pref"], "fi")
        add_literal(graph, subject, SKOS.prefLabel, item["sv"], "sv")

        for value in master_entry["alts"]:
            add_literal(graph, subject, SKOS.altLabel, value, "fi")
        for value in synonyms.get(mesh_id, []):
            add_literal(graph, subject, SKOS.altLabel, value, "sv")
        for value in entryterms.get(mesh_id, []):
            if value != item["en"]:
                add_literal(graph, subject, SKOS.altLabel, value, "en")

        if mesh_id in english_notes:
            add_literal(graph, subject, SKOS.scopeNote, english_notes[mesh_id].get("en", ""), "en")
        if mesh_id in swedish_notes:
            add_literal(graph, subject, SKOS.scopeNote, swedish_notes[mesh_id], "sv")

        graph.add((subject, DCTERMS.created, Literal(record["created"], datatype=XSD.date)))
        graph.add((subject, DCTERMS.modified, Literal(record["modified"], datatype=XSD.date)))

    for child_id, parent_id in hierarchy_links(numbers):
        if child_id in descriptor_ids and parent_id in descriptor_ids:
            graph.add((MESH_NS[child_id], SKOS.broader, MESH_NS[parent_id]))
            graph.add((MESH_NS[parent_id], SKOS.narrower, MESH_NS[child_id]))

    concepts = set(graph.subjects(RDF.type, SKOS.Concept))
    top_concepts = {concept for concept in concepts if not any(graph.objects(concept, SKOS.broader))}
    for concept in top_concepts:
        graph.add((MESH, SKOS.hasTopConcept, concept))
        graph.add((concept, SKOS.topConceptOf, MESH))

    for subject in concepts:
        pref_labels = set(graph.objects(subject, SKOS.prefLabel))
        for label in pref_labels:
            graph.remove((subject, SKOS.altLabel, label))

    return graph, {"concepts": len(concepts), "top_concepts": len(top_concepts), "dated_concepts": len(descriptor_ids)}


def concept_subjects(graph: Graph) -> set:
    return set(graph.subjects(RDF.type, SKOS.Concept))


def validate_against_model(graph: Graph, reference: Graph) -> None:
    reference_concepts = concept_subjects(reference)
    reference_types = {
        obj for subject in reference_concepts for obj in reference.objects(subject, RDF.type)
    }
    reference_predicates = {
        predicate for subject, predicate, _obj in reference if subject in reference_concepts
    }
    permitted_predicates = reference_predicates | {DCTERMS.created, DCTERMS.modified}
    output_concepts = concept_subjects(graph)
    errors = []

    for subject, predicate, obj in graph:
        if predicate == RDF.type and subject in output_concepts and obj not in reference_types:
            errors.append(f"type is absent from the reference model: {subject} a {obj}")
        if subject in output_concepts and predicate not in permitted_predicates:
            errors.append(f"predicate is absent from the reference model: {subject} {predicate}")
        if isinstance(subject, URIRef) and YEAR_URI_RE.search(str(subject)):
            errors.append(f"year-specific URI used as subject: {subject}")
        if isinstance(obj, URIRef) and YEAR_URI_RE.search(str(obj)):
            errors.append(f"year-specific URI used as object: {obj}")

    for subject in output_concepts:
        types = set(graph.objects(subject, RDF.type))
        if types != reference_types:
            errors.append(f"unexpected rdf:type set for {subject}: {sorted(map(str, types))}")
        for predicate in (DCTERMS.created, DCTERMS.modified):
            values = list(graph.objects(subject, predicate))
            if len(values) != 1 or values[0].datatype != XSD.date:
                errors.append(f"{subject} must have exactly one {predicate} value with datatype xsd:date")

    reference_scheme = Counter(predicate for predicate, _value in reference.predicate_objects(MESH))
    output_scheme = Counter(predicate for predicate, _value in graph.predicate_objects(MESH))
    if output_scheme != reference_scheme:
        errors.append(
            "ConceptScheme predicate/cardinality structure differs from the reference: "
            f"reference={dict(reference_scheme)}, output={dict(output_scheme)}"
        )

    if errors:
        raise RuntimeError("Output failed reference-model validation:\n  " + "\n  ".join(errors[:50]))


def compare_graphs(output: Graph, reference: Graph) -> None:
    output_data = {triple for triple in output if triple[0] != MESH}
    reference_data = {triple for triple in reference if triple[0] != MESH}
    only_output = output_data - reference_data
    only_reference = reference_data - output_data
    non_date_output = {triple for triple in only_output if triple[1] not in {DCTERMS.created, DCTERMS.modified}}
    date_output = only_output - non_date_output

    print("\n--- RDF comparison (ConceptScheme-subject triples excluded) ---")
    print(f"Triples in reference but not generated: {len(only_reference)}")
    if only_reference:
        for predicate, count in Counter(t[1] for t in only_reference).most_common():
            print(f"  missing {predicate}: {count}")
    print(f"Generated date triples not in reference (expected addition): {len(date_output)}")
    print(f"Other generated triples not in reference: {len(non_date_output)}")
    if non_date_output:
        for predicate, count in Counter(t[1] for t in non_date_output).most_common():
            print(f"  added/changed {predicate}: {count}")
    if not only_reference and not non_date_output:
        print("Current content matches the reference apart from the agreed concept date additions.")
    else:
        print("Differences also reflect source-content changes; review the per-predicate counts above.")


def create_output(graph: Graph, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    serialized = graph.serialize(format="turtle", encoding="utf-8")
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    for suffix in range(1000):
        extra = "" if suffix == 0 else f"-{suffix:02d}"
        path = directory / f"mesh-skos-{timestamp}{extra}.ttl"
        try:
            with path.open("xb") as stream:
                stream.write(serialized)
            return path
        except FileExistsError:
            continue
    raise RuntimeError(f"Could not choose a new timestamped output name in {directory}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, help="MeSH release year; default is the newest year linked by KIB")
    parser.add_argument("--master", type=Path, help="Client-provided Finnish MASTER file; auto-detected if exactly one is nearby")
    parser.add_argument("--compare", type=Path, help="Reference TTL (default: mesh-skos-new.ttl beside this script)")
    parser.add_argument("--out-dir", type=Path, default=Path("."), help="Directory for a new timestamped output file")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    reference_path = (args.compare or script_dir / "mesh-skos-new.ttl").expanduser().resolve()
    if not reference_path.is_file():
        raise RuntimeError(
            f"Reference/model file not found: {reference_path}. Supply the unchanged mesh-skos-new.ttl with --compare."
        )
    master_path = discover_master(args.master, script_dir)

    year, kib_url, archive_bytes = discover_kib_text_export(args.year)
    tables = read_kib_tables(archive_bytes, kib_url)
    nlm_url, nlm_bytes = discover_nlm_descriptor_xml(year)
    descriptors = read_nlm_descriptors(nlm_bytes)
    reference = Graph()
    reference.parse(reference_path, format="turtle")

    graph, stats = build_graph(tables, descriptors, master_path, reference, year)
    validate_against_model(graph, reference)
    compare_graphs(graph, reference)
    output_path = create_output(graph, args.out_dir.expanduser().resolve())

    print("\nSource discovery:")
    print(f"  KIB text export ({year}): {kib_url}")
    print(f"  NLM same-year Descriptor XML: {nlm_url}")
    print(f"  Client MASTER: {master_path}")
    print(f"  Reference/model (read-only): {reference_path}")
    print(f"Generated: {output_path}")
    print(f"Concepts: {stats['concepts']}; top concepts: {stats['top_concepts']}; concepts with both dates: {stats['dated_concepts']}")
    print("Dates use NLM DateIntroduced and LastUpdated, emitted as xsd:date without time.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
