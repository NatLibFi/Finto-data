import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.StringTokenizer;
import java.util.Vector;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.FactoryConfigurationError;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.RDFWriter;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.shared.PrefixMapping;
import com.hp.hpl.jena.util.FileManager;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;

public class YSASKOSmuunnin {

	private final String skosNS = "http://www.w3.org/2004/02/skos/core#";
	private final String rdfNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
	private final String ysaNS = "http://www.yso.fi/onto/ysa/";
	private final String ysaMetaNS = "http://www.yso.fi/onto/ysa-meta/";
	private final String rdfsNS = "http://www.w3.org/2000/01/rdf-schema#";
	
	private Model ysaSkos;
	private Model ysaGroups;
	private Model allarsSkos;
	private Document ysa;
	private HashMap<String, String> idMap;
	
	public YSASKOSmuunnin(String ysaGroupsinPolku) {
		this.idMap = new HashMap<String, String>();
		
		this.ysaSkos = ModelFactory.createDefaultModel();
		this.ysaSkos.setNsPrefixes(this.luoNimiavaruudet());
		this.ysaGroups = ModelFactory.createDefaultModel();
		
		InputStream in = FileManager.get().open(ysaGroupsinPolku);
		if (in == null) {
		    throw new IllegalArgumentException("File: " + ysaGroupsinPolku + " not found");
		}
		this.ysaGroups.read(in, "");

		try {
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public PrefixMapping luoNimiavaruudet() {
		PrefixMapping na = PrefixMapping.Factory.create();
		na.setNsPrefix("", this.ysaNS);
		na.setNsPrefix("skos", this.skosNS);
		na.setNsPrefix("ysa-meta", this.ysaMetaNS);
		return na;
	}
	
	public static Document parsi(String tiedosto) {
		try {
			String encoding = "UTF-8";
			BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(tiedosto), encoding));
 			InputSource is = new InputSource(br);
			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			DocumentBuilder builder = factory.newDocumentBuilder();
			Document document = builder.parse(is);
			return document;
		}
		catch (FactoryConfigurationError e) {
			System.out.println("unable to get a document builder factory");
		} 
		catch (ParserConfigurationException e) {
			System.out.println("parser was unable to be configured");
		}
		catch (SAXException e) {
			System.out.println("parsing error");
		} 
		catch (IOException e) {
			System.out.println("i/o error");
		}
		return null;
	}
	
	public void muunna(String muunnettavaTiedosto) {
		this.luoJuuri();
		this.luoRyhmatYsaSkosiin();
		this.ysa = YSASKOSmuunnin.parsi(muunnettavaTiedosto);
		NodeList recordNodelist = this.ysa.getElementsByTagName("record");
		
		// Täytetään ensin HashMap idMap, jossa prefLabelit toimivat avaimina ID:ihin
		for (int i = 0; i < recordNodelist.getLength(); i++) {
			Node recordNode = recordNodelist.item(i);
			NodeList recordLapset = recordNode.getChildNodes();
			// kaivetaan ensin ID
			String id = this.ysaNS + "ONGELMA";
			id = this.ysaNS + "Y" + this.kaivaControlfieldinArvoRecordNodesta(recordNode, "001");
			// kaivetaan ominaisuudet
			for (int j = 0; j < recordLapset.getLength(); j++) {
				Node recordLapsinode = recordLapset.item(j);
				if (recordLapsinode.getNodeType() == Node.ELEMENT_NODE) {
					String ele = recordLapsinode.getNodeName();
					if (ele.equals("datafield")) {
						String tag = "ONGELMA";
						NamedNodeMap datafieldAttribuutit = recordLapsinode.getAttributes();
						for (int k = 0; k < datafieldAttribuutit.getLength(); k++) {
							tag = datafieldAttribuutit.getNamedItem("tag").getNodeValue();
						}
						if (tag.equals("ONGELMA")) System.out.println("Ongelma asiasanan " + id + " datafieldin tagissa.");

						NodeList subfieldNodet = recordLapsinode.getChildNodes();
						String sisalto = "ONGELMA";
						if (tag.equals("151") || tag.equals("150")) {
							// prefLabel fi
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								this.idMap.put(sisalto + " -- " + lisamaare, id);
							} else 
								this.idMap.put(sisalto, id);
							
						}
					}
				}
			}
		}
		//System.out.println("idMap valmis");
		
		for (int i = 0; i < recordNodelist.getLength(); i++) {
			Node recordNode = recordNodelist.item(i);
			NodeList recordLapset = recordNode.getChildNodes();
			// kaivetaan ensin ID
			String id = this.ysaNS + "ONGELMA";
			id = this.ysaNS + "Y" + this.kaivaControlfieldinArvoRecordNodesta(recordNode, "001");
			// kaivetaan ominaisuudet
			for (int j = 0; j < recordLapset.getLength(); j++) {
				Node recordLapsinode = recordLapset.item(j);
				if (recordLapsinode.getNodeType() == Node.ELEMENT_NODE) {
					String ele = recordLapsinode.getNodeName();
					if (ele.equals("datafield")) {
						String tag = "ONGELMA";
						NamedNodeMap datafieldAttribuutit = recordLapsinode.getAttributes();
						for (int k = 0; k < datafieldAttribuutit.getLength(); k++) {
							tag = datafieldAttribuutit.getNamedItem("tag").getNodeValue();
						}
						if (tag.equals("ONGELMA")) System.out.println("Ongelma asiasanan " + id + " datafieldin tagissa.");

						NodeList subfieldNodet = recordLapsinode.getChildNodes();
						String sisalto = "ONGELMA";
						if (tag.equals("151")) {
							// prefLabel fi maantieteelliselle paikalla
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								this.kirjoitaMaantieteellinenLabelYsaSkosiin(id, sisalto + " -- " + lisamaare, "fi");
							} else 
								this.kirjoitaMaantieteellinenLabelYsaSkosiin(id, sisalto, "fi");
						} else if (tag.equals("150")) {
							// prefLabel fi
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								this.kirjoitaLabelYsaSkosiin(id, sisalto + " -- " + lisamaare, "fi");
							} else 
								this.kirjoitaLabelYsaSkosiin(id, sisalto, "fi");
						} else if (tag.equals("550") || tag.equals("551")) {
							// broader, narrower tai related
							boolean narrower = this.subfieldissaOnAttribuuttiKoodilla(subfieldNodet, "w", "h");
							boolean broader = this.subfieldissaOnAttribuuttiKoodilla(subfieldNodet, "w", "g");
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								sisalto = sisalto + " -- " + lisamaare;
							}							
							String objId = this.kaivaIdAsiasananPerusteella(sisalto);
							if (narrower) this.kirjoitaNarrowerYsaSkosiin(id, objId);
							else if (broader) this.kirjoitaBroaderYsaSkosiin(id, objId);
							else this.kirjoitaRelatedYsaSkosiin(id, objId);
						} else if (tag.equals("035")) {
							// id tagissa
						} else if (tag.equals("667")) {
							// Sisäinen huomautus, ei laiteta YSASkosiin
						} else if (tag.equals("670")) {
							// Lähde
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							this.kirjoitaSourceYsaSkosiin(id, sisalto);
						} else if (tag.equals("680")) {
							// note
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "i");
							if (sisalto.equals("ONGELMA")) {
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							}
							this.kirjoitaNoteYsaSkosiin(id, sisalto, "fi");
						} else if (tag.equals("450") || tag.equals("451")) {
							// altLabel
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								this.kirjoitaAltLabelYsaSkosiin(id, sisalto + " -- " + lisamaare, "fi");
							} else
								this.kirjoitaAltLabelYsaSkosiin(id, sisalto, "fi");
						} else if (tag.equals("072")) {
							// ryhma TODO
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							this.kirjoitaRyhmaYsaSkosiin(id, sisalto);
						} else if (!tag.equals("040")) {
							System.out.println(id + " - tuntematon tag: " + tag);	
						}	
					}
				}
			}
		}
	}
		
	public String kaivaIdAsiasananPerusteella(String asiasana) {
		return this.idMap.get(asiasana);
	}
	
	public String kaivaControlfieldinArvoRecordNodesta(Node recordNode, String haettavaTag) {
		String palautettava = "ONGELMA";
		NodeList recordLapset = recordNode.getChildNodes();
		for (int j = 0; j < recordLapset.getLength(); j++) {
			Node recordLapsinode = recordLapset.item(j);
			if (recordLapsinode.getNodeType() == Node.ELEMENT_NODE) {
				String ele = recordLapsinode.getNodeName();
				if (ele.equals("controlfield")) {
					Node controlfieldNode = recordLapsinode;
					String tag = "ONGELMA";
					NamedNodeMap controlfieldAttribuutit = controlfieldNode.getAttributes();
					for (int k = 0; k < controlfieldAttribuutit.getLength(); k++) {
						tag = controlfieldAttribuutit.getNamedItem("tag").getNodeValue();
					}
					if (tag.equals("ONGELMA")) System.out.println("ongelma controlfielding tagin lukemisessa");
					else if (tag.equals(haettavaTag)) {
						palautettava = controlfieldNode.getFirstChild().getTextContent();
					}
				}
			}
		}
		
		return palautettava;
	}
	
	public String kaivaDatafieldinArvoRecordNodesta(Node recordNode, String haettavaTag, String haettavaCode) {
		String palautettava = "ONGELMA";
		
		NodeList recordLapset = recordNode.getChildNodes();
		for (int j = 0; j < recordLapset.getLength(); j++) {
			Node recordLapsinode = recordLapset.item(j);
			if (recordLapsinode.getNodeType() == Node.ELEMENT_NODE) {
				String ele = recordLapsinode.getNodeName();
				if (ele.equals("datafield")) {
					Node datafieldNode = recordLapsinode;
					String tag = "ONGELMA";
					NamedNodeMap datafieldAttribuutit = datafieldNode.getAttributes();
					for (int k = 0; k < datafieldAttribuutit.getLength(); k++) {
						tag = datafieldAttribuutit.getNamedItem("tag").getNodeValue();
					}
					if (tag.equals("ONGELMA")) System.out.println("Ongelma datafieldin tagissa.");
					
					NodeList subfieldNodet = datafieldNode.getChildNodes();
					
					if (tag.equals(haettavaTag)) {
						palautettava = this.kaivaSubfieldinArvo(subfieldNodet, haettavaCode);
					}
				}
			}
		}
		return palautettava;
	}
	
	public String kaivaSubfieldinArvo(NodeList subfieldNodet, String code) {
		String palautettava = "ONGELMA";
		for (int h = 0; h < subfieldNodet.getLength(); h++) {
			Node subfieldNode = subfieldNodet.item(h);
			if (subfieldNode.getNodeType() == Node.ELEMENT_NODE) {
				NamedNodeMap subfieldAttribuutit = subfieldNode.getAttributes();
				for (int l = 0; l < subfieldAttribuutit.getLength(); l++) {
					Node attr = subfieldAttribuutit.item(l);
					if (attr.getNodeValue().equals(code)) {
						palautettava = subfieldNode.getFirstChild().getTextContent();
					}
				}
			}
		}
		return palautettava;
	}
	
	public boolean subfieldissaOnAttribuuttiKoodilla(NodeList subfieldNodet, String code, String kysyttyValue) {
		boolean loytyi = false;
		for (int h = 0; h < subfieldNodet.getLength(); h++) {
			Node subfieldNode = subfieldNodet.item(h);
			if (subfieldNode.getNodeType() == Node.ELEMENT_NODE) {
				NamedNodeMap subfieldAttribuutit = subfieldNode.getAttributes();
				for (int l = 0; l < subfieldAttribuutit.getLength(); l++) {
					Node attr = subfieldAttribuutit.item(l);
					if (attr.getNodeValue().equals(code)) {
						if (subfieldNode.getFirstChild().getTextContent().equals(kysyttyValue)) loytyi = true;
					}
				}
			}
		}
		return loytyi;
	}
	
	public Resource luoKasiteresurssi(String id) {
		return this.ysaSkos.createResource(id);
	}
	
	// Tämä myös luo uuden käsitteen kannalta oleelliset muut määrittelyt
	public void kirjoitaLabelYsaSkosiin(String id, String label, String kieli) {
		if (kieli.equals("se")) kieli = "sv";
		Property prefLabel = this.ysaSkos.createProperty(this.skosNS + "prefLabel");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.ysaSkos.createLiteral(label, kieli);
		this.ysaSkos.add(subj, prefLabel, obj);
		
		Property type = this.ysaSkos.createProperty(this.rdfNS + "type");
		Resource skosConcept = this.ysaSkos.createResource(this.skosNS + "Concept");
		this.ysaSkos.add(subj, type, skosConcept);
		
		Resource juuri = this.ysaSkos.createResource(this.ysaNS);
		Property inScheme = this.ysaSkos.createProperty(this.skosNS + "inScheme");
		this.ysaSkos.add(subj, inScheme, juuri);
	}

	public void kirjoitaMaantieteellinenLabelYsaSkosiin(String id, String label, String kieli) {
		this.kirjoitaLabelYsaSkosiin(id, label, kieli);
		Resource subj = this.luoKasiteresurssi(id);
		Property skosNote = this.ysaSkos.createProperty(this.skosNS + "note");
		Literal obj = this.ysaSkos.createLiteral("151");
		this.ysaSkos.add(subj, skosNote, obj);
		
		Property type = this.ysaSkos.createProperty(this.rdfNS + "type");
		Resource skosConcept = this.ysaSkos.createResource(this.skosNS + "Concept");
		Resource ysaGeographicalConcept = this.ysaSkos.createResource(this.ysaMetaNS + "GeographicalConcept");
		this.ysaSkos.remove(subj, type, skosConcept);
		this.ysaSkos.add(subj, type, ysaGeographicalConcept);
	}
	
	public void kirjoitaAltLabelYsaSkosiin(String id, String label, String kieli) {
		Property pred = this.ysaSkos.createProperty(this.skosNS + "altLabel");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.ysaSkos.createLiteral(label, kieli);
		this.ysaSkos.add(subj, pred, obj);
	}
	
	public void kirjoitaBroaderYsaSkosiin(String id, String laajemmanTerminId) {
		Property pred = this.ysaSkos.createProperty(this.skosNS + "broader");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(laajemmanTerminId);
		this.ysaSkos.add(subj, pred, obj);
	}
	            
	public void kirjoitaNarrowerYsaSkosiin(String id, String suppeammanTerminId) {
		Property pred = this.ysaSkos.createProperty(this.skosNS + "narrower");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(suppeammanTerminId);
		this.ysaSkos.add(subj, pred, obj);
	}
	
	public void kirjoitaRelatedYsaSkosiin(String id, String rinnakkaisTerminId) {
		Property pred = this.ysaSkos.createProperty(this.skosNS + "related");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(rinnakkaisTerminId);
		this.ysaSkos.add(subj, pred, obj);
	}
	
	public void kirjoitaNoteYsaSkosiin(String id, String kommentti, String kieli) {
		Property pred = this.ysaSkos.createProperty(this.skosNS + "note");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.ysaSkos.createLiteral(kommentti, kieli);
		this.ysaSkos.add(subj, pred, obj);
	}
	
	public void kirjoitaSourceYsaSkosiin(String id, String lahde) {
		Property pred = this.ysaSkos.createProperty(this.ysaMetaNS + "source");
		Resource subj = this.luoKasiteresurssi(id);
		if (lahde.substring(0, 6).equals("Lähde:")) {
			lahde = lahde.substring(6);
		}
		Literal obj = this.ysaSkos.createLiteral(lahde.trim(), "fi");
		this.ysaSkos.add(subj, pred, obj);
	}
	
	public void luoRyhmatYsaSkosiin() {
		Property kuvausProp = this.ysaGroups.createProperty("http://yso.fi/ysa-groups#kuvaus");
		StmtIterator iter = this.ysaGroups.listStatements((Resource)null, kuvausProp, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			String lang = stmt.getLanguage();
			
			String numero = "";
			StmtIterator iter2 = this.ysaGroups.listStatements(stmt.getSubject(), RDFS.label, (RDFNode)null);
			while(iter2.hasNext()) {
				Literal lit = ((Literal)(iter2.nextStatement().getObject()));
				numero = lit.getLexicalForm().substring(6);
			}
			if (numero.equals("")) {
				System.out.println("Ongelma YSA-Allars-groupsin kanssa: " + stmt.getSubject().getURI() + " numerossa häikkää");
			}
			
			Resource ryhma = this.ysaSkos.createResource(this.ysaNS + "ryhma_" + numero);
			String kuvaus = ((Literal)stmt.getObject()).getLexicalForm();
			
			Property type = this.ysaSkos.createProperty(this.rdfNS + "type");
			Resource skosCollection = this.ysaSkos.createResource(this.skosNS + "Collection");
			this.ysaSkos.add(ryhma, type, skosCollection);
			Property prefLabel = this.ysaSkos.createProperty(this.skosNS + "prefLabel");
			Literal obj = this.ysaSkos.createLiteral(numero + " " + kuvaus, lang);
			this.ysaSkos.add(ryhma, prefLabel, obj);
			// Tekee hiddenlabelit
			Property hiddenLabel = this.ysaSkos.createProperty(this.skosNS + "hiddenLabel");
			StringTokenizer st = new StringTokenizer(kuvaus, ".");
			while (st.hasMoreTokens()) {
				obj = this.ysaSkos.createLiteral(st.nextToken().trim(), lang);
				this.ysaSkos.add(ryhma, hiddenLabel, obj);
			}
			Resource juuri = this.ysaSkos.createResource(this.ysaNS);
			Property inScheme = this.ysaSkos.createProperty(this.skosNS + "inScheme");
			this.ysaSkos.add(ryhma, inScheme, juuri);
		}	
	}
	
	public void kirjoitaRyhmaYsaSkosiin(String id, String sisalto) {
		String numero = sisalto.substring(3).trim();
		if (!numero.equals("")) {
			Resource ysaskosryhma = this.ysaSkos.createResource(this.ysaNS + "ryhma_" + numero);
			Resource subj = this.luoKasiteresurssi(id);
			Property member = this.ysaSkos.createProperty(this.skosNS + "member");
			this.ysaSkos.add(ysaskosryhma, member, subj);
		}
	}
	
	public void luoJuuri() {
		Resource juuri = this.ysaSkos.createResource(this.ysaNS);
		Property type = this.ysaSkos.createProperty(this.rdfNS + "type");
		Resource conceptScheme = this.ysaSkos.createResource(this.skosNS + "ConceptScheme");
		this.ysaSkos.add(juuri, type, conceptScheme);
		
		Resource property = this.ysaSkos.createProperty(this.rdfNS + "Property");
		Property ysaSource = this.ysaSkos.createProperty(this.ysaMetaNS + "source");
		Property rdfsLabel = this.ysaSkos.createProperty(this.rdfsNS + "label");
		Property domain = this.ysaSkos.createProperty(this.rdfsNS + "domain");
		Resource skosConcept = this.ysaSkos.createResource(this.skosNS + "Concept");
		Literal sourceLabelFi = this.ysaSkos.createLiteral("Lähde", "fi");
		Literal sourceLabelSv = this.ysaSkos.createLiteral("Källa", "sv");
		Literal sourceLabelEn = this.ysaSkos.createLiteral("Source", "en");
		
		this.ysaSkos.add(ysaSource, type, property);
		this.ysaSkos.add(ysaSource, domain, skosConcept);
		this.ysaSkos.add(ysaSource, rdfsLabel, sourceLabelFi);
		this.ysaSkos.add(ysaSource, rdfsLabel, sourceLabelSv);
		this.ysaSkos.add(ysaSource, rdfsLabel, sourceLabelEn);
		
		Property hiddenNote = this.ysaSkos.createProperty(this.ysaMetaNS + "hiddenNote");
		this.ysaSkos.add(hiddenNote, type, property);
		this.ysaSkos.add(hiddenNote, domain, skosConcept);
		
		Resource owlClass = this.ysaSkos.createResource("http://www.w3.org/2002/07/owl#Class");
		Property subClassOf = this.ysaSkos.createProperty("http://www.w3.org/2000/01/rdf-schema#subClassOf");
		Resource ysaGeographicalConcept = this.ysaSkos.createResource(this.ysaMetaNS + "GeographicalConcept");
		Literal geoLabelFi = this.ysaSkos.createLiteral("Maantieteellinen paikka", "fi");
		Literal geoLabelSv = this.ysaSkos.createLiteral("Geografisk plats", "sv");
		Literal geoLabelEn = this.ysaSkos.createLiteral("Geographical location", "en");
		this.ysaSkos.add(ysaGeographicalConcept, type, owlClass);
		this.ysaSkos.add(ysaGeographicalConcept, subClassOf, skosConcept);
		this.ysaSkos.add(ysaGeographicalConcept, rdfsLabel, geoLabelFi);
		this.ysaSkos.add(ysaGeographicalConcept, rdfsLabel, geoLabelSv);
		this.ysaSkos.add(ysaGeographicalConcept, rdfsLabel, geoLabelEn);
	}
	
	public String muutaUriksi(String muutettava) {
		muutettava = muutettava.replace('ä', 'a');
		muutettava = muutettava.replace('ö', 'o');
		muutettava = muutettava.replace(' ', '_');
		muutettava = muutettava.toLowerCase();
		return muutettava;
	}
	
	/*
	 * Anonyymeja nodeja tulee siitä, että joillakin YSA:n ei-maantieteellisillä
	 * termeillä on kuitenkin suhde maantieteelliseen termiin (esim. etelänavalla on suhde
	 * Antarktikseen)
	 */
	public void poistaAnonyymejaNodejaSisaltavatTriplet() {
		Vector<Statement> poistettavat = new Vector<Statement>();
		StmtIterator iter = this.ysaSkos.listStatements();
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getObject().isAnon()) {
				poistettavat.add(stmt);
			}
		}
		for (Statement s:poistettavat) this.ysaSkos.remove(s);
	}

	public void lisaaRuotsinkielisetLabelit(String allarsSkosinPolku) {
		this.allarsSkos = ModelFactory.createDefaultModel();
		
		InputStream in = FileManager.get().open(allarsSkosinPolku);
		if (in == null) {
		    throw new IllegalArgumentException("File: " + allarsSkosinPolku + " not found");
		}
		this.allarsSkos.read(in, "");

		try {
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}

		Property skosPrefLabel = this.ysaSkos.createProperty(this.skosNS + "prefLabel");
		HashMap<String, Resource> ysaLabelitSubjektit = new HashMap<String, Resource>();
		StmtIterator iter = this.ysaSkos.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String labelString = ((Literal)stmt.getObject()).getLexicalForm();
				ysaLabelitSubjektit.put(labelString, stmt.getSubject());
			}
		}
		
		HashMap<Resource, String> allarsSubjektitLabelit = new HashMap<Resource, String>();
		iter = this.allarsSkos.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String labelString = ((Literal)stmt.getObject()).getLexicalForm();
				allarsSubjektitLabelit.put(stmt.getSubject(), labelString);
			}
		}
		
		iter = this.allarsSkos.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("sv")) {
				String svLabelString = ((Literal)stmt.getObject()).getLexicalForm();
				String fiLabelString = allarsSubjektitLabelit.get(stmt.getSubject());
				Resource ysaSubj = ysaLabelitSubjektit.get(fiLabelString);
				Literal ysaObj = this.ysaSkos.createLiteral(svLabelString, "sv");
				if (ysaSubj != null) {
					this.ysaSkos.add(ysaSubj, RDFS.label, ysaObj);
				} else System.out.println(fiLabelString + " ei löydy YSAsta, mutta Allärsistä kyllä");
			}
		}
		
		Property skosAltLabel = this.ysaSkos.createProperty(this.skosNS + "prefLabel");
		iter = this.allarsSkos.listStatements((Resource)null, skosAltLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("sv")) {
				String svLabelString = ((Literal)stmt.getObject()).getLexicalForm();
				String fiLabelString = allarsSubjektitLabelit.get(stmt.getSubject());
				Resource ysaSubj = ysaLabelitSubjektit.get(fiLabelString);
				Literal ysaObj = this.ysaSkos.createLiteral(svLabelString, "sv");
				if (ysaSubj != null)
					this.ysaSkos.add(ysaSubj, skosAltLabel, ysaObj);
			}
		}
	}
	
	public void poistaRuotsalaisetPrefLabelitJaMuuta151NotetHiddenNoteiksi() {
		Property skosPrefLabel = this.ysaSkos.createProperty(this.skosNS + "prefLabel");
		Property skosNote = this.ysaSkos.createProperty(this.skosNS + "note");
		Property hiddenNote = this.ysaSkos.createProperty(this.ysaMetaNS + "hiddenNote");
		
		Vector<Statement> poistettavat = new Vector<Statement>();
		Vector<Statement> lisattavat = new Vector<Statement>();
		
		StmtIterator iter2 = this.ysaSkos.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter2.hasNext()) {
			Statement stmt2 = iter2.nextStatement();
			if (stmt2.getLanguage().equals("sv")) poistettavat.add(stmt2);
		}
		
		iter2 = this.ysaSkos.listStatements((Resource)null, skosNote, (RDFNode)null);
		while (iter2.hasNext()) {
			Statement stmt = iter2.nextStatement();
			Literal obj = (Literal)stmt.getObject();
			if (obj.getLexicalForm().equals("151")) {
				poistettavat.add(stmt);
				lisattavat.add(this.ysaSkos.createStatement(stmt.getSubject(), hiddenNote, obj));
			}
		}
		
		for (Statement s:poistettavat) this.ysaSkos.remove(s);
		for (Statement s:lisattavat) this.ysaSkos.add(s);
	}
		
	public void testaaEtsiOngelmat() {
		StmtIterator iter = this.ysaSkos.listStatements();
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			Property pred = stmt.getPredicate();
			RDFNode obj = stmt.getObject();
			boolean onOngelma = false;
			if (!subj.getURI().contains("http")) onOngelma = true;
			if (!pred.getURI().contains("http")) onOngelma = true;
			if (obj.isURIResource())
				if (!((Resource)obj).getURI().contains("http")) onOngelma = true;
			if (onOngelma) { 
				if (obj.isURIResource()) System.out.println(subj.getURI() + " " + pred.getURI() + " " + ((Resource)obj).getURI());
				else  System.out.println(subj.getURI() + " " + pred.getURI() + " " + obj.toString());
			}
		}
		
	}
	
	public void muutaRuotsiLabelitLinkeiksiJaSamaAllarsiinJaKirjoitaAllars(String allarsSkosinPolku) {
		Vector<Statement> ysaPoistettavat = new Vector<Statement>();
		Vector<Statement> allarsPoistettavat = new Vector<Statement>();
		Vector<Statement> ysaLisattavat = new Vector<Statement>();
		Vector<Statement> allarsLisattavat = new Vector<Statement>();
		
		HashMap<String, Resource> ysaRuotsiLabelSubjectHashMap = new HashMap<String, Resource>();
		HashMap<String, Vector<Resource>> ysaRuotsiSetitHashMap = new HashMap<String, Vector<Resource>>();
		StmtIterator iter = this.ysaSkos.listStatements((Resource)null, RDFS.label, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("sv")) {
				String ruotsiLabel = ((Literal)stmt.getObject()).getLexicalForm();
				if (ysaRuotsiSetitHashMap.containsKey(ruotsiLabel)) {
					Vector<Resource> resurssit = ysaRuotsiSetitHashMap.get(ruotsiLabel);
					resurssit.add(stmt.getSubject());
					ysaRuotsiSetitHashMap.put(ruotsiLabel, resurssit);
				} else if (ysaRuotsiLabelSubjectHashMap.containsKey(ruotsiLabel)) {
					Vector<Resource> resurssit = new Vector<Resource>();
					resurssit.add(ysaRuotsiLabelSubjectHashMap.get(ruotsiLabel));
					resurssit.add(stmt.getSubject());
					ysaRuotsiSetitHashMap.put(ruotsiLabel, resurssit);
					ysaRuotsiLabelSubjectHashMap.remove(ruotsiLabel);
				} else {
					ysaRuotsiLabelSubjectHashMap.put(ruotsiLabel, stmt.getSubject());
				}
				ysaPoistettavat.add(stmt);
			}
		}

		Property skosExactMatch = ysaSkos.createProperty(this.skosNS + "exactMatch");
		int linkkienMaaraAllarsissa = 0;
		int linkkienMaaraYsassa = 0;
		
		HashMap<String, Resource> allarsSuomiLabelSubjectHashMap = new HashMap<String, Resource>();
		HashMap<String, Vector<Resource>> allarsSuomiSetitHashMap = new HashMap<String, Vector<Resource>>();
		
		Property skosPrefLabel = this.ysaSkos.createProperty(this.skosNS + "prefLabel");
		iter = this.allarsSkos.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String suomiLabel = ((Literal)stmt.getObject()).getLexicalForm();
				if (allarsSuomiSetitHashMap.containsKey(suomiLabel)) {
					Vector<Resource> resurssit = allarsSuomiSetitHashMap.get(suomiLabel);
					resurssit.add(stmt.getSubject());
					allarsSuomiSetitHashMap.put(suomiLabel, resurssit);
				} else if (allarsSuomiLabelSubjectHashMap.containsKey(suomiLabel)) {
					Vector<Resource> resurssit = new Vector<Resource>();
					resurssit.add(allarsSuomiLabelSubjectHashMap.get(suomiLabel));
					resurssit.add(stmt.getSubject());
					allarsSuomiSetitHashMap.put(suomiLabel, resurssit);
					allarsSuomiLabelSubjectHashMap.remove(suomiLabel);
				} else {
					allarsSuomiLabelSubjectHashMap.put(suomiLabel, stmt.getSubject());
				}
				allarsPoistettavat.add(stmt);
			} else if (stmt.getLanguage().equals("sv")) {
				String ruotsiLabel = ((Literal)stmt.getObject()).getLexicalForm();
				if (ysaRuotsiLabelSubjectHashMap.containsKey(ruotsiLabel)) {
					linkkienMaaraAllarsissa++;
					allarsLisattavat.add(this.allarsSkos.createStatement(stmt.getSubject(), skosExactMatch, ysaRuotsiLabelSubjectHashMap.get(ruotsiLabel)));
				} else if (ysaRuotsiSetitHashMap.containsKey(ruotsiLabel)) {
					Property skosBroadMatch = this.allarsSkos.createProperty(this.skosNS + "broadMatch");
					Vector<Resource> resurssit = ysaRuotsiSetitHashMap.get(ruotsiLabel);
					for (Resource r:resurssit) {
						allarsLisattavat.add(this.allarsSkos.createStatement(stmt.getSubject(), skosBroadMatch, r));
					}
				} else {
					System.out.println("Ei löytynyt ysasta vastinetta allärsin termille " + ruotsiLabel);
				}
			}
		}
		
		iter = this.ysaSkos.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String suomiLabel = ((Literal)stmt.getObject()).getLexicalForm();
				if (allarsSuomiLabelSubjectHashMap.containsKey(suomiLabel)) {
					linkkienMaaraYsassa++;
					ysaLisattavat.add(this.ysaSkos.createStatement(stmt.getSubject(), skosExactMatch, allarsSuomiLabelSubjectHashMap.get(suomiLabel)));
				} else if (allarsSuomiSetitHashMap.containsKey(suomiLabel)) {
					Property skosNarrowMatch = this.ysaSkos.createProperty(this.skosNS + "narrowMatch");
					Vector<Resource> resurssit = allarsSuomiSetitHashMap.get(suomiLabel);
					for (Resource r:resurssit) {
						ysaLisattavat.add(this.ysaSkos.createStatement(stmt.getSubject(), skosNarrowMatch, r));
					}
				} else {
					System.out.println("Ei löytynyt allärsista vastinetta ysan termille " + suomiLabel);
				}
			} else {
				System.out.println("Ysassa ei-suomenkielinen prefLabel subjektilla " + stmt.getSubject().getURI());
			}
		}
		
		// YSA-ryhmat ja Allars-ryhmat
		Resource skosCollection = this.ysaSkos.createResource(this.skosNS + "Collection");
		Property skosHiddenLabel = this.ysaSkos.createProperty(this.skosNS + "hiddenLabel");
		iter = this.ysaSkos.listStatements((Resource)null, RDF.type, skosCollection);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			ysaPoistettavat.add(this.ysaSkos.createStatement(stmt.getSubject(), skosExactMatch, stmt.getSubject()));
			StmtIterator iter2 = this.ysaSkos.listStatements(stmt.getSubject(), skosHiddenLabel, (RDFNode)null);
			while (iter2.hasNext()) {
				Statement stmt2 = iter2.nextStatement();
				if (stmt2.getLanguage().equals("sv")) ysaPoistettavat.add(stmt2);
			}
		}
		iter = this.allarsSkos.listStatements((Resource)null, RDF.type, skosCollection);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			allarsPoistettavat.add(this.allarsSkos.createStatement(stmt.getSubject(), skosExactMatch, stmt.getSubject()));
			StmtIterator iter2 = this.allarsSkos.listStatements(stmt.getSubject(), skosHiddenLabel, (RDFNode)null);
			while (iter2.hasNext()) {
				Statement stmt2 = iter2.nextStatement();
				if (stmt2.getLanguage().equals("fi")) allarsPoistettavat.add(stmt2);
			}
		}
		/*
		// Skosnote 151 pois Allärsista
		Property skosNote = this.allarsSkos.createProperty(this.skosNS + "note");
		iter = this.allarsSkos.listStatements((Resource)null, skosNote, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (((Literal)stmt.getObject()).getLexicalForm().equals("151")) {
				allarsPoistettavat.add(stmt);
			}
		}*/
		
		for (Statement s:ysaPoistettavat) this.ysaSkos.remove(s);
		for (Statement s:allarsPoistettavat) this.allarsSkos.remove(s);
		
		for (Statement s:ysaLisattavat) this.ysaSkos.add(s);
		for (Statement s:allarsLisattavat) this.allarsSkos.add(s);
		
		this.kirjoitaAllarsSkos(allarsSkosinPolku);
	}
	
	public void kirjoitaYsaSkos(String ysaskosinPolku) {
		try {
			FileOutputStream os = new FileOutputStream(ysaskosinPolku);
			BufferedOutputStream bs = new BufferedOutputStream(os);
			RDFWriter kirjuri = this.ysaSkos.getWriter();
			kirjuri.setProperty("showXmlDeclaration", true);
			kirjuri.write(this.ysaSkos, bs, null);
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("SKOS-muunnettu YSA kirjoitettiin tiedostoon " + ysaskosinPolku);
	}
	
	public void kirjoitaAllarsSkos(String allarsSkosinPolku) {
		try {
			FileOutputStream os = new FileOutputStream(allarsSkosinPolku);
			BufferedOutputStream bs = new BufferedOutputStream(os);
			RDFWriter kirjuri = this.allarsSkos.getWriter();
			kirjuri.setProperty("showXmlDeclaration", true);
			kirjuri.write(this.allarsSkos, bs, null);
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("YSA-linkitetty AllärsSkos kirjoitettiin tiedostoon " + allarsSkosinPolku);
	}
	
	public static void main(String[] args) {
		if (args.length != 4) {
			System.out.println("Anna neljä parametria: [muunnettava tiedosto] [uusi tiedosto] [ysa-groups-tiedost] [Allärs-tiedosto]");
		}
		YSASKOSmuunnin ym = new YSASKOSmuunnin(args[2]);
		ym.muunna(args[0]);
		ym.poistaAnonyymejaNodejaSisaltavatTriplet();
		if (args[3] != null) {
			ym.lisaaRuotsinkielisetLabelit(args[3]);
			ym.poistaRuotsalaisetPrefLabelitJaMuuta151NotetHiddenNoteiksi();
			ym.muutaRuotsiLabelitLinkeiksiJaSamaAllarsiinJaKirjoitaAllars(args[3]);
		}
		ym.kirjoitaYsaSkos(args[1]);
		
	}
	
}
