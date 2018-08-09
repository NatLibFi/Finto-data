package stuff;

import java.io.File;
import java.util.HashMap;
import java.util.HashSet;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;
import common.JenaHelpers;

public class UcumXml2Skos {

	private Document ucumXml;
	private Model ucum;
	private Resource currentResource;
	private int juoksevaNumero;

	private HashMap<String, Resource> propLabelitResurssitMap;
	private HashMap<String, Resource> classLabelitResurssitMap;
	
	private final String ucumNs = "http://www.yso.fi/onto/ucum/";
	private final String ucumMetaNs = "http://www.yso.fi/onto/ucum-meta/";
	private final String skosNs = "http://www.w3.org/2004/02/skos/core#";
	
	public UcumXml2Skos() {
		this.ucum = JenaHelpers.luoMalli();
		this.ucum.setNsPrefix("skos", this.skosNs);
		this.ucum.setNsPrefix("ucum", this.ucumNs);
		this.ucum.setNsPrefix("ucum-meta", this.ucumMetaNs);
		
		this.juoksevaNumero = 0;
		this.propLabelitResurssitMap = new HashMap<String, Resource>();
		this.classLabelitResurssitMap = new HashMap<String, Resource>();
	}
	
	public void readXml(String xmlFilePath) {
		try {
			File fXmlFile = new File(xmlFilePath);
			DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
			this.ucumXml = dBuilder.parse(fXmlFile);
		} catch (Exception e) {
			e.printStackTrace();
	    }
	}
	
	public void luoProperty(String propName) {
		Property prop = this.ucum.createProperty(this.ucumMetaNs + propName);
		this.ucum.add(prop, RDF.type, RDF.Property);
		Literal literal = this.ucum.createLiteral(propName, "en");
		this.ucum.add(prop, RDFS.label, literal);
	}
	
	public Resource haeClass(String className) {
		if (!this.classLabelitResurssitMap.containsKey(className)) {
			Resource skosConcept = this.ucum.createResource(this.skosNs + "Concept");
			Property skosPrefLabel = this.ucum.createProperty(this.skosNs + "prefLabel");
			this.juoksevaNumero++;
			Resource classRes = this.ucum.createResource(this.ucumNs + "p" + this.juoksevaNumero);
			this.ucum.add(classRes, RDF.type, skosConcept);
			this.ucum.add(classRes, skosPrefLabel, this.ucum.createLiteral(className, "en"));
			this.classLabelitResurssitMap.put(className, classRes);
		}
		return this.classLabelitResurssitMap.get(className);
	}
	
	public Resource haeProperty(String propName) {
		if (!this.propLabelitResurssitMap.containsKey(propName)) {
			Resource skosCollection = this.ucum.createResource(this.skosNs + "Collection");
			Property skosPrefLabel = this.ucum.createProperty(this.skosNs + "prefLabel");
			this.juoksevaNumero++;
			Resource propRes = this.ucum.createResource(this.ucumNs + "p" + this.juoksevaNumero);
			this.ucum.add(propRes, RDF.type, skosCollection);
			this.ucum.add(propRes, skosPrefLabel, this.ucum.createLiteral(propName, "en"));
			this.propLabelitResurssitMap.put(propName, propRes);
		}
		return this.propLabelitResurssitMap.get(propName);
	}
	
	public void xml2Skos(String xmlFilePath) {
		this.readXml(xmlFilePath);
		NodeList nodeList = this.ucumXml.getChildNodes();
		this.kasitteleNode(nodeList);
	}
	
	public void kasitteleNode(NodeList nodeList) {
		Resource skosConcept = this.ucum.createResource(this.skosNs + "Concept");
		Property skosPrefLabel = this.ucum.createProperty(this.skosNs + "prefLabel");
		Property skosRelated = this.ucum.createProperty(this.skosNs + "related");
		Property skosMember = this.ucum.createProperty(this.skosNs + "member");
		Property skosInScheme = this.ucum.createProperty(this.skosNs + "inScheme");
		
		Property ucumCode = this.ucum.createProperty(this.ucumMetaNs + "code");
		this.luoProperty("code");
		Property ucumCODE = this.ucum.createProperty(this.ucumMetaNs + "CODE");
		this.luoProperty("CODE");
		Property ucumIsMetric = this.ucum.createProperty(this.ucumMetaNs + "isMetric");
		this.luoProperty("isMetric");
		Property ucumIsSpecial = this.ucum.createProperty(this.ucumMetaNs + "isSpecial");
		this.luoProperty("isSpecial");
		
		for (int count = 0; count < nodeList.getLength(); count++) {

			Node tempNode = nodeList.item(count);

			// make sure it's element node.
			if (tempNode.getNodeType() == Node.ELEMENT_NODE) {
				
				if (tempNode.getNodeName().equals("unit") || tempNode.getNodeName().equals("base-unit")) {
					
					this.juoksevaNumero++;
					this.currentResource = this.ucum.createResource(this.ucumNs + "p" + this.juoksevaNumero);
					this.ucum.add(this.currentResource, RDF.type, skosConcept);
					this.ucum.add(this.currentResource, skosInScheme, this.ucumNs);
					
					NamedNodeMap nnm = tempNode.getAttributes();
					if (nnm.getNamedItem("Code") != null)
					this.ucum.add(currentResource, ucumCode, this.ucum.createLiteral(nnm.getNamedItem("Code").getNodeValue(), "en"));
					if (nnm.getNamedItem("CODE") != null)
					this.ucum.add(currentResource, ucumCODE, this.ucum.createLiteral(nnm.getNamedItem("CODE").getNodeValue(), "en"));
					if (nnm.getNamedItem("isMetric") != null)
					this.ucum.add(currentResource, ucumIsMetric, this.ucum.createLiteral(nnm.getNamedItem("isMetric").getNodeValue(), "en"));
					if (nnm.getNamedItem("isSpecial") != null)
					this.ucum.add(currentResource, ucumIsSpecial, this.ucum.createLiteral(nnm.getNamedItem("isSpecial").getNodeValue(), "en"));
					if (nnm.getNamedItem("class") != null) {
						Resource classRes = this.haeClass(nnm.getNamedItem("class").getNodeValue());
						this.ucum.add(currentResource, skosRelated, classRes);
					}
					
					NodeList childNodes = tempNode.getChildNodes();
					for (int j = 0; j < childNodes.getLength(); j++) {
						Node childNode = childNodes.item(j);
						if (childNode.getNodeType() == Node.ELEMENT_NODE) {
							if (childNode.getNodeName().equals("name")) {
								Literal literal = this.ucum.createLiteral(childNode.getTextContent(), "en");
								this.ucum.add(this.currentResource, skosPrefLabel, literal);
								//System.out.println(childNode.getTextContent());
							} else if (childNode.getNodeName().equals("property")) {
								//System.out.println(childNode.getTextContent());
								String propName = childNode.getTextContent();
								Resource propRes = this.haeProperty(propName);
								this.ucum.add(propRes, skosMember, this.currentResource);
							}
						}
					}
				}

				/*
				// get node name and value
				System.out.println("\nNode Name =" + tempNode.getNodeName() + " [OPEN]");
				System.out.println("Node Value =" + tempNode.getTextContent());

				if (tempNode.hasAttributes()) {

					// get attributes names and values
					NamedNodeMap nodeMap = tempNode.getAttributes();

					for (int i = 0; i < nodeMap.getLength(); i++) {

						Node node = nodeMap.item(i);
						System.out.println("attr name : " + node.getNodeName());
						System.out.println("attr value : " + node.getNodeValue());

					}

				}*/

				if (tempNode.hasChildNodes()) {

					// loop again if has child nodes
					kasitteleNode(tempNode.getChildNodes());

				}
			}
		}

	}
	
	public void kirjoitaUusiMalli(String uudenPolku) {
			boolean onTtl = false;
			if (uudenPolku.endsWith(".ttl")) onTtl = true;
			JenaHelpers.kirjoitaMalli(this.ucum, uudenPolku, onTtl);
	}
	
	public static void main(String[] args) {
		UcumXml2Skos ux2s = new UcumXml2Skos();
		ux2s.xml2Skos(args[0]);
		ux2s.kirjoitaUusiMalli(args[1]);
	}
	
}
