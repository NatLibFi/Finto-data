from pymarc import Record, Field, MARCReader, XMLWriter, parse_xml_to_array
from lxml import etree as ET
import sys
import logging
import argparse
import pickle
from datetime import datetime, date
import os.path

def compare_records(input_file_1, input_file_2, mrcx_file, pickle_file, date_1, date_2):
    """
    input_file_1: Vertailtavien MARC-tietueiden tiedostonimi
    input_file_2: Tiedostonimi MARC-tietueille, joista tallennetaan muokatut ja uudet
    output_file: muokatuista ja uusista tietueista muodostetun MARCXML-tiedoston nimi
    pickle_file: tallettaa muutospäivämäärät pickle-tiedostoon date_1 ja date_2 parametrien mukaan
    date_1: alkuperäinen päivämäärä
    date_2: muutospäivämäärä
    """
    #git rev-list -1 --before="2019-08-23 23:59" master
    #git log
    modified_records = 0    
    new_records = 0
    all_records = {}

    if date_1:
        old_date = datetime.date(datetime.strptime(date_1, "%Y-%m-%d"))
    else:
        old_date = date.fromtimestamp(os.path.getmtime(input_file_1))
    
    if date_2:
        new_date = datetime.date(datetime.strptime(date_2, "%Y-%m-%d"))
    else:
        new_date = date.fromtimestamp(os.path.getmtime(input_file_2))    
    
    writer = XMLWriter(open(mrcx_file, "wb"))
    records = parse_xml_to_array(input_file_1)
    
    old_records_dict = {}
    for record in records:
        for field in record.get_fields('024'):
            old_records_dict.update({field['a']: record})
    records = parse_xml_to_array(input_file_2)

    for record in records:
        record_id = None
        modified = False
        modified_date = old_date
        for field in record.get_fields('024'):
            record_id = field['a']
        if record_id:
            if record_id in old_records_dict:
                old_record = old_records_dict[record_id]
                if not str(old_record) == str(record):
                    modified = True
                    modified_records += 1
            else:
                modified = True
                new_records += 1
        else:
            logging.warning("Record id missing")
        if modified:
            writer.write(record)
            modified_date = new_date
        all_records.update({record_id: modified_date})
                    
    print("Number of modified records: %s"%modified_records)
    print("Number of new records: %s"%new_records)
    
    if pickle_file:
        with open(pickle_file, 'wb') as output:
            pickle.dump(all_records, output, pickle.HIGHEST_PROTOCOL)
            output.close()    
    
    writer.close()
   
    parser = ET.XMLParser(remove_blank_text=True,strip_cdata=False)
    tree = ET.parse(mrcx_file, parser)
    e = tree.getroot()
    handle = open(mrcx_file, "wb")
    handle.write(ET.tostring(e, encoding='UTF-8', pretty_print=True))
   
def readCommandLineArguments():
    parser = argparse.ArgumentParser(description="Ohjelma, \
        joka vertailee kahta MARCXML-tiedostoa \
        ja tuottaa uuden tiedoston muuntuneista ja uusista käsitteistä.")
    parser.add_argument("-i1", "--first_input_file", help="File name for record to be compared", required=True)
    parser.add_argument("-i2", "--second_input_file", help="File name for records whose changes are detected", required=True)    
    parser.add_argument("-o1", "--output_mrcx", help="Output file name for changed MARC XML records", required=True)
    parser.add_argument("-o2", "--output_pkl", help="Output file name for pickle file for dates of modifications")
    parser.add_argument("-dd", "--default_date", help="Default date for records without modifications (set in YYYY-MM-DD format)")
    parser.add_argument("-md", "--modified_date", help="Modification date for records with modifications (set in YYYY-MM-DD format)")
    args = parser.parse_args()
    return args

def main():
    args = readCommandLineArguments()
    compare_records(input_file_1=args.first_input_file, 
                    input_file_2=args.second_input_file, 
                    mrcx_file=args.output_mrcx,
                    pickle_file=args.output_pkl,
                    date_1=args.default_date,
                    date_2=args.modified_date)
   
if __name__ == "__main__":
    main()