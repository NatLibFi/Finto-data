"""
 Copyright 2021 University Of Helsinki (The National Library Of Finland)
 
 Licensed under the GNU, General Public License, Version 3.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     https://www.gnu.org/licenses/gpl-3.0.html
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from rdflib import Graph, RDF
from rdflib.namespace import OWL
from lxml import etree, html
from urllib.parse import urldefrag
import argparse
import logging
import io

def validate_xml(validation_file, xml):
    with open(validation_file, 'rb') as fh:
        xmlschema_doc = etree.parse(fh)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        test_xml = etree.tostring(xml, encoding='unicode', method='xml')
        string_xml = io.StringIO(test_xml)
        doc = etree.parse(string_xml)
        xmlschema.assert_(doc)
            
def add_sublement(element, tag, text=None):
    subelement = etree.SubElement(element, tag)
    if text:
        subelement.text = text
    return subelement    
       
class HTMLtoURN:

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-ns", "--urn_namespace",
            help="URN namespace for data model", required=True)
        parser.add_argument("-p", "--url_prefix",  
            help="Prefix used in HTML formatted data model", required=True)
        parser.add_argument("-i", "--input_path",  
            help="Input path for turtle formatted file", required=True)
        parser.add_argument("-o", "--output_path",  
            help="Output path for XML file", required=True)
        parser.add_argument("-v", "--validation_file",  
            help="File path for XSD file for validating XMl")   
        args = parser.parse_args()
        self.urn_namespace = args.urn_namespace
        self.url_prefix = args.url_prefix
        self.output_path = args.output_path
        self.input_path = args.input_path
        self.validation_file = args.validation_file
        self.parse_graph()
        
    def create_xml(self, fragments):
        root = etree.Element("records")
        etree.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        etree.register_namespace('xmlns', 'urn:nbn:se:uu:ub:epc-schema:rs-location-mapping')
        root.set('xmlns', 'urn:nbn:se:uu:ub:epc-schema:rs-location-mapping')
        root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                 'urn:nbn:se:uu:ub:epc-schema:rs-location-mapping http://urn.kb.se/resolve?urn=urn:nbn:se:uu:ub:epc-schema:rs-location-mapping&amp;godirectly')
        add_sublement(root, "protocol-version", '3.0')
        
        for fragment in fragments:
            record = etree.SubElement(root, "record")
            header = etree.SubElement(record, "header")
            identifier = add_sublement(header, "identifier", self.urn_namespace + fragment)
            destinations = etree.SubElement(header, "destinations")
            destination = etree.SubElement(destinations, "destination")
            destination.set('status', 'activated')
            url = add_sublement(destination, "url", self.url_prefix + fragment)
        return root
            
    def parse_graph(self):
        g = Graph()
        g.parse(self.input_path, format="ttl")
        fragments = []
         
        for t in types:
            for subject in g.subjects(RDF.type, t):
                result = urldefrag(subject)
                if result:
                    tag = result[1]
                    if tag:
                        if tag in fragments:
                            logging.error("Multiple fragments with same name %s "%tag)
                        else:
                            fragments.append(tag)
                    else:
                        logging.error("Fragment missing from subject %s "%subject)
                else:
                    logging.error("Fragment missing from subject %s "%subject)
        xml = self.create_xml(fragments)
        et = etree.ElementTree(xml)
        if self.validation_file:
           validate_xml(validation_file, xml)
        et.write(self.output_path, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        
if __name__ == '__main__':
    HTMLtoURN()