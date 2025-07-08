import enum
from pymarc import Record, Subfield, XMLWriter, parse_xml_to_array
from aleph_seq_reader import AlephSeqReader
from lxml import etree as ET
import logging
import argparse
import copy
import unicodedata

CREATOR_AGENCY = "FI-NL"
LEADERDELETED0 = '00000dz  a2200000n  4500'

def deprecate_record(record):
    if record['024'] and record['040']:
        deprecated_record = Record()
        deprecated_record.leader = LEADERDELETED0
        deprecated_record.add_field(record['024'])
        deprecated_record.add_field(record['040'])
        return deprecated_record

def remove_extra_subfield_whitespaces(record):
    for field in record.get_fields():
        if hasattr(field, "subfields"):
            for idx, sf in enumerate(field.subfields):
                value = sf.value.strip()
                if '  ' in value:
                    while '  ' in value:
                        value = value.replace('  ', ' ')
                field.subfields[idx] = Subfield(code=field.subfields[idx].code, value=value)

    return record

def trim_record(record):
    # drops unnecessary data from record for comparing two records
    record_copy = copy.deepcopy(record)
    removable_fields = ['001', '005', '008', '035']
    removable_subfields = ['0', '2', '7']
    record_copy.leader = ""
    for field in record_copy.get_fields('040'):
        field.delete_subfield('f')
    for field in record_copy.get_fields():
        if not field.tag.isdigit():
            removable_fields.append(field.tag)
    for rf in removable_fields:
        record_copy.remove_fields(rf)
    record_copy = remove_extra_subfield_whitespaces(record_copy)
    for field in record_copy.get_fields():
        for rf in removable_subfields:
            field.delete_subfield(rf)
    record_copy = unicodedata.normalize('NFD', str(record_copy))

    return record_copy

def compare_records(args):

    input_file_1 = args.aleph_dump_file
    input_file_2 = args.input_marcxml 
    mrcx_file = args.output_marcxml
    voc_tags = []
    write_count = 0
    max_records = int(args.max_records) if args.max_records else None
    if args.vocabulary_name == "yso-aika":
        voc_tags = ["148"]
    if args.vocabulary_name == "yso":
        voc_tags = ["150"]
    if args.vocabulary_name == "yso-paikat":
        voc_tags = ["151"]
    if args.vocabulary_name == "slm":
        voc_tags = ["155"]
    if args.vocabulary_name == "mts":
        voc_tags = ["168", "172", "174", "175", "176"]
    
    loglevel = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(loglevel)

    aleph_records = {}
  
    fh = open(input_file_1, 'r')
    reader = AlephSeqReader(fh)
    for record in reader:
        if record:
            if record['001']:
                if not any(tag in record for tag in voc_tags) or not any(field.tag.startswith('1') for field in record.get_fields()):
                    continue
                
                language = None                               
                for field in record.get_fields("040"):
                    for sf in field.get_subfields('b'):
                        language = sf
                if args.vocabulary_language != language:
                    continue

                for field in record.get_fields('024'):
                    record_id = field['a']
                    if record_id in aleph_records:
                        aleph_record = aleph_records[record_id]
                        if '001' in aleph_record:
                            aleph_id = record['001'].data
                            duplicate_id = aleph_record['001'].data
                            if record.leader[5] not in ['d', 's', 'x']:
                                logging.warning(f'Record with URI {record_id} and id {aleph_id} has duplicate {duplicate_id} in Aleph')
                    aleph_records[record_id] = record

    fh.close()

    writer = XMLWriter(open(mrcx_file, "wb"))
    records = parse_xml_to_array(input_file_2)

    new_records = {}
    modified_records_number = 0    
    new_records_number = 0

    for record in records:
        if record:
            record_id = None
            modified = False
            for field in record.get_fields('024'):
                record_id = field['a']
            if record_id:
                new_records[record_id] = record
                if record_id in aleph_records:
                    aleph_record = aleph_records[record_id]
                    record1 = trim_record(record)
                    record2 = trim_record(aleph_record)
                    if aleph_record.leader[5] not in ['d', 's', 'x'] and record1 != record2:
                        modified = True
                        modified_records_number += 1
                else:
                    modified = True
                    new_records_number += 1
            else:
                logging.warning("Record id missing")
            if modified:
                if max_records and write_count > max_records: 
                    pass
                else:
                    writer.write(record)
                    write_count += 1

    for uri in aleph_records:
        if uri not in new_records and aleph_records[uri].leader[5] not in ['d', 's', 'x']:
            record = aleph_records[uri]
            if any(field.tag.startswith('1') for field in record.get_fields()):
                record = deprecate_record(aleph_records[uri])
                if max_records and write_count > max_records:
                    pass
                else:
                    writer.write(record)
                    write_count += 1

    logging.info("Number of modified records: %s"%modified_records_number)
    logging.info("Number of new records: %s"%new_records_number)

    writer.close()
   
    parser = ET.XMLParser(remove_blank_text=True,strip_cdata=False)
    tree = ET.parse(mrcx_file, parser)
    e = tree.getroot()
    handle = open(mrcx_file, "wb")
    handle.write(ET.tostring(e, encoding='UTF-8', pretty_print=True, xml_declaration=True))
    
def readCommandLineArguments():
    parser = argparse.ArgumentParser(description=" Program that compares two files of MARC records and outputs changed and new records of the latter file")
    parser.add_argument("-a", "--aleph_dump_file", help="File path for Aleph records to be compared, file format aleph sequential", required=True)
    parser.add_argument("-i", "--input_marcxml", help="File path for records whose changes are to be detected, file format must me MARCXML", required=True)    
    parser.add_argument("-o", "--output_marcxml", help="Output file name for new, changed and deprecate MARC XML records", required=True)
    parser.add_argument("-vn", "--vocabulary_name", help="Define vocabulary name ", choices=['yso', 'yso-aika', 'yso-paikat', 'slm', 'mts'], required=True)
    parser.add_argument("-vl", "--vocabulary_language", help="Define vocabulary language, e g. 'fin', 'swe'",required=True)
    parser.add_argument("-m", "--max_records", help="Maximum number of new records for output file")
    args = parser.parse_args()
    return args

def main():
    args = readCommandLineArguments()
    compare_records(args)
   
if __name__ == "__main__":
    main()
