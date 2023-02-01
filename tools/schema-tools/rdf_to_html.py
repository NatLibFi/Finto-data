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

from rdflib import Graph, URIRef, BNode, Namespace, RDF, Literal
from rdflib.namespace import SKOS, XSD, OWL, DC, NamespaceManager
from lxml import etree
from helpers import add_sublement, defrag_iri
from io import StringIO
import argparse
import logging

HEADERS = {OWL.Class: 'Classes',
           OWL.ObjectProperty: 'Object Properties',
           OWL.DatatypeProperty: 'Datatype Properties',
           OWL.AnnotationProperty: 'Annotation Properties'}
           
TYPES = [OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty]

class RDFtoHTML:

    def __init__(self):
        parser = argparse.ArgumentParser(description="Conversion of data model from RDF to HTML")
        parser.add_argument("-pl", "--pref_label",
            help="Property name for preferred labels e. g. skos:prefLabel", required=True)
        parser.add_argument("-l", "--language",  
            help="Language code of main language used in HTML documentation", required=True)
        parser.add_argument("-i", "--input_path",  
            help="Input path for rdf file", required=True)
        parser.add_argument("-o", "--output_path",  
            help="Output path for html documentation file", required=True)
        parser.add_argument("-ns", "--name_space",  
            help="Namespace of concepts in input file", required=True)
        parser.add_argument("-u", "--base_url",  
            help="Base URL of published html file", required=True)
        parser.add_argument("-t", "--title",  
            help="Title of HTML document")
        parser.add_argument("-d", "--description",  
            help="HTML file containing description of data model to be included to output file")
        args = parser.parse_args()
        self.language = args.language
        self.pref_label = args.pref_label
        self.input_path = args.input_path
        self.output_path = args.output_path
        self.name_space = args.name_space
        self.base_url = args.base_url
        self.title = args.title
        self.description = args.description
        self.graph = Graph()
        self.parse_graph()
          
    def get_pref_label(self, subject):
        for probj in self.graph.predicate_objects(subject):
            prop = probj[0]
            obj = probj[1]
            prop_ns = prop.n3(self.graph.namespace_manager)
            language = None
            prop_name = prop_ns
            if prop_ns == self.pref_label:
                if Literal(probj[1]).language:
                    if self.language == Literal(probj[1]).language:
                        return(obj)
                else:    
                    return(obj)
     
    def sort_properties_with_id(self, properties):
        sorted_labels = sorted(properties.keys(), key=str.casefold)
        sorted_properties = {}
        for subject in sorted_labels:
            sorted_properties.update({subject: properties[subject]})
        return sorted_properties
        
    def sort_properties_with_label(self, properties):
        unsorted_properties = {}
        for prop in properties:
            pref_label = self.get_pref_label(prop)
            unsorted_properties[pref_label] = {prop: properties[prop]}
        sorted_labels = sorted(unsorted_properties.keys(), key=str.casefold)
        sorted_properties = {}
        for pref_label in sorted_labels:
            sorted_properties.update(unsorted_properties[pref_label])
        return sorted_properties
    
    def set_anchor(self, prop, value=None, urn=False):
        root = etree.Element('a')
        href_value = prop
        text_value = prop
        result = defrag_iri(prop)
        if result:
            tag = result[0]
            fragment = result[1]   
            if urn:
                result = defrag_iri(href_value)
                text_value = text_value.replace('http://urn.fi/', '')
            elif tag == self.name_space and prop != 'URN':
                
                text_value = self.get_pref_label(prop)
                if text_value:
                    result = defrag_iri(href_value)
                    href_value = "#" + result[1]
            elif prop != 'URN':
                prop_ns = prop.n3(self.graph.namespace_manager)
                text_value = prop_ns
                if value and Literal(value).language:
                    text_value += " (" + Literal(value).language + ")"
                root.set('target', '_blank')
        else:
            root.set('target', '_blank')
        root.text = str(text_value)
        root.set('href', str(href_value))
        return root
        
    def create_contents(self, html_doc, header, properties):
        header_element = add_sublement(html_doc, 'h2', text=header)
        paragraph = add_sublement(html_doc, 'p')
        for idx, subject in enumerate(properties):
            result = defrag_iri(subject)
            if result:
                fragment = result[1]
                text = fragment
                if idx < len(properties) - 1:
                    text = text + ", "
                anchor = add_sublement(paragraph, 'a', text) 
                anchor.set('href' , "#" + fragment)
        
    def create_properties(self, html_doc, header, properties):
        header_element = add_sublement(html_doc, 'h2', text=header)
        paragraph = add_sublement(html_doc, 'div')
        for subject in properties:
            result = defrag_iri(subject)
            if result:
                div = add_sublement(paragraph, 'div')
                div.set('class', 'property')
                anchor = add_sublement(div, 'a', result[1])
                anchor.set('id', result[1])
                table = add_sublement(paragraph, 'table')
                for prop in properties[subject]:
                    tablerow = add_sublement(table, 'tr')
                    prop_name = prop
                    tag = None
                    if type(prop) == URIRef:
                        root = self.set_anchor(prop)
                        td_key = etree.SubElement(tablerow, 'td')
                        td_key.append(root)
                    else:
                        td_key = add_sublement(tablerow, 'td', prop_name)
                    
                    td_key.set('class', 'key')
                    td_value = add_sublement(tablerow, 'td')
                    td_value.set('class', 'value')
                    text = ""
                    for idx, value in enumerate(properties[subject][prop]):
                        if type(value) == URIRef:
                            urn = False
                            if prop == 'URN':
                                urn = True
                            root = self.set_anchor(value, urn=urn)
                            if idx < len(properties[subject][prop]) - 1:
                                root.tail = ", "
                            td_value.append(root)
                        else:  
                            if Literal(value).language:
                                value = str(value) + " (" + Literal(value).language + ")"
                            text += str(value)
                            if idx < len(properties[subject][prop]) - 1:
                                text += ", "  
                    try:
                        text = etree.fromstring(text)
                        td_value.append(text)
                    except etree.XMLSyntaxError:
                        try:
                            text = etree.fromstring(text)
                            td_value.append(text)
                        except etree.XMLSyntaxError:
                            td_value.text = text
            
    def parse_graph(self):
        self.graph.parse(self.input_path, format="ttl")
        class_properties = set()         
        data_model = {}
        for ns in self.graph.namespaces():
            self.graph.namespace_manager.bind(ns[0], ns[1])
        for t in TYPES:
            data_model[t] = {}
            for subject in self.graph.subjects(RDF.type, t):
                fragment = None
                result = defrag_iri(subject)
                if result:
                    fragment = result[1]
                pref_label = self.get_pref_label(subject)
                if pref_label and fragment:    
                    sorted_properties  = {}
                    subject_properties = {}
                    sorted_properties['URN'] = [subject]
                    pref_labels = []
                    other_properties = []
                    for probj in self.graph.predicate_objects(subject):
                        prop = probj[0]
                        obj = probj[1]
                        prop_ns = prop.n3(self.graph.namespace_manager)
                        language = None
                        if Literal(probj[1]).language:
                            language = Literal(probj[1]).language
                        if isinstance(obj, URIRef):
                            obj_ns = self.graph.namespace_manager.normalizeUri(obj)
                        prop_dict = {'language': language, 'prop': prop, 'obj': obj}
                        if prop_ns == self.pref_label:
                            pref_labels.append(prop_dict)
                        else:
                            other_properties.append(prop_dict)
                            
                    sorted_languages = sorted(pref_labels, key=lambda k: (  
                        k['language'] != self.language,
                        k['language']
                    ))
                    
                    for sl in sorted_languages:
                        if sl['prop'] in sorted_properties:
                            sorted_properties[sl['prop']].append(sl['obj'])
                        else:
                            sorted_properties[sl['prop']] = [sl['obj']]
                    other_properties = sorted(other_properties, key=lambda k: (  
                        k['prop']
                    ))
                    for sl in other_properties:
                        if sl['prop'] in sorted_properties:
                            sorted_properties[sl['prop']].append(sl['obj'])
                        else:
                            sorted_properties[sl['prop']] = [sl['obj']]
                    data_model[t][subject] = sorted_properties

                else:
                    logging.warning("PrefLabel or URI fragment missing from %s"%subject)                      
                                
        html_doc = etree.Element("html")
        head = etree.SubElement(html_doc, "head")
        if self.title:
            title = add_sublement(head, 'title', self.title)
        meta = etree.SubElement(head, "meta")
        meta.set('http-equiv', 'Content-Type')
        meta.set('content', 'text/html; charset=utf-8')
        meta.tail = None
        link = add_sublement(head, "link", text=None)
        link.set('rel', 'stylesheet')
        link.set('href', 'stylesheet.css')
        link.tail = None
        body = etree.SubElement(html_doc, "body")
        if self.description:
            with open(self.description, 'r', encoding='utf-8') as fh:
                data = fh.read()
                parser = etree.HTMLParser()
                description = etree.parse(StringIO(data), parser)
                droot = description.getroot()
                body.append(droot) 
        for t in data_model:
            data_model[t] = self.sort_properties_with_id(data_model[t])
        for t in data_model:
            if data_model[t]:
                self.create_contents(html_doc, HEADERS[t], data_model[t])
        for t in data_model:
            if data_model[t]:
                self.create_properties(html_doc, HEADERS[t], data_model[t])
        with open(self.output_path, 'wb') as output:
            output.write(etree.tostring(html_doc, encoding='utf-8', pretty_print=True))
            
if __name__ == '__main__':
    RDFtoHTML()
    
