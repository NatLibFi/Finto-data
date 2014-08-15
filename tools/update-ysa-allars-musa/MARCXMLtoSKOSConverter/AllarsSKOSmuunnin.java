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
import com.hp.hpl.jena.vocabulary.RDFS;

public class AllarsSKOSmuunnin {

	private final String skosNS = "http://www.w3.org/2004/02/skos/core#";
	private final String rdfNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
	private final String allarsNS = "http://www.yso.fi/onto/allars/";
	private final String ysaNS = "http://www.yso.fi/onto/ysa/";
	private final String rdfsNS = "http://www.w3.org/2000/01/rdf-schema#";
	private final String allarsMetaNS = "http://www.yso.fi/onto/allars-meta/";
	
	private Model allarsSkos;
	private Document allars;
	private Model ysaGroups;
	private HashMap<String, String> idMap;
	
	public AllarsSKOSmuunnin(String ysaGroupsinPolku) {
		this.idMap = new HashMap<String, String>();
		
		this.allarsSkos = ModelFactory.createDefaultModel();
		this.allarsSkos.setNsPrefixes(this.luoNimiavaruudet());
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
		na.setNsPrefix("", this.allarsNS);
		na.setNsPrefix("ysa", this.ysaNS);
		na.setNsPrefix("skos", this.skosNS);
		na.setNsPrefix("allars-meta", this.allarsMetaNS);
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
		this.luoRyhmatAllarsSkosiin();
		this.allars = AllarsSKOSmuunnin.parsi(muunnettavaTiedosto);
		NodeList recordNodelist = this.allars.getElementsByTagName("record");
		
		// Täytetään ensin HashMap idMap, jossa prefLabelit toimivat avaimina ID:ihin
		for (int i = 0; i < recordNodelist.getLength(); i++) {
			Node recordNode = recordNodelist.item(i);
			NodeList recordLapset = recordNode.getChildNodes();
			// kaivetaan ensin ID
			String id = this.allarsNS + "ONGELMA";
			id = this.allarsNS + "Y" + this.kaivaControlfieldinArvoRecordNodesta(recordNode, "001");
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
		// System.out.println("idMap valmis");
		
		for (int i = 0; i < recordNodelist.getLength(); i++) {
			Node recordNode = recordNodelist.item(i);
			NodeList recordLapset = recordNode.getChildNodes();
			// kaivetaan ensin ID
			String id = this.allarsNS + "ONGELMA";
			id = this.allarsNS + "Y" + this.kaivaControlfieldinArvoRecordNodesta(recordNode, "001");
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
							// prefLabel maantieteelliselle paikalla
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								this.kirjoitaMaantieteellinenLabelAllarsSkosiin(id, sisalto + " -- " + lisamaare, "sv");
							} else 
								this.kirjoitaMaantieteellinenLabelAllarsSkosiin(id, sisalto, "sv");
							if (sisalto.equals("ONGELMA")) System.out.println("Tag 151 ongelmissa asiasanassa " + id);
						} else if (tag.equals("150")) {
							// prefLabel
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								this.kirjoitaLabelAllarsSkosiin(id, sisalto + " -- " + lisamaare, "sv");
							} else 
								this.kirjoitaLabelAllarsSkosiin(id, sisalto, "sv");
							if (sisalto.equals("ONGELMA")) System.out.println("Tag 150 ongelmissa asiasanassa " + id);
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
							if (narrower) this.kirjoitaNarrowerAllarsSkosiin(id, objId);
							else if (broader) this.kirjoitaBroaderAllarsSkosiin(id, objId);
							else this.kirjoitaRelatedAllarsSkosiin(id, objId);
							if (sisalto.equals("ONGELMA")) System.out.println("Tag 550 tai 551 ongelmissa asiasanassa " + id);
						} else if (tag.equals("680")) {
							// note
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "i");
							if (sisalto.equals("ONGELMA")) sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							this.kirjoitaNoteAllarsSkosiin(id, sisalto, "sv");
							if (sisalto.equals("ONGELMA")) System.out.println("Tag 680 ongelmissa asiasanassa " + id);
						} else if (tag.equals("670")) {
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							this.kirjoitaSourceAllarsSkosiin(id, sisalto);
							if (sisalto.equals("ONGELMA")) System.out.println("Tag 670 ongelmissa asiasanassa " + id);
						} else if (tag.equals("667") ) {
							// sisäinen huomautus, ei laiteta allarsSkosiin
						} else if (tag.equals("450") || tag.equals("451")) {
							// altLabel
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								this.kirjoitaAltLabelAllarsSkosiin(id, sisalto + " -- " + lisamaare, "sv");
							} else
								this.kirjoitaAltLabelAllarsSkosiin(id, sisalto, "sv");
							if (sisalto.equals("ONGELMA")) System.out.println("Tag 450 ongelmissa asiasanassa " + id);
						} else if (tag.equals("750") || tag.equals("751")) {
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							String lisamaare = "ONGELMA";
							lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
							if (lisamaare.equals("ONGELMA")) lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "z");
							if (!lisamaare.equals("ONGELMA")) {
								this.kirjoitaLabelAllarsSkosiin(id, sisalto + " -- " + lisamaare, "fi");
							} else
								this.kirjoitaLabelAllarsSkosiin(id, sisalto, "fi");
							if (sisalto.equals("ONGELMA")) System.out.println("Tag 750 tai 751 ongelmissa asiasanassa " + id);
						} else if (tag.equals("072")) {
							sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
							this.kirjoitaRyhmaAllarsSkosiin(id, sisalto);
							if (sisalto.equals("ONGELMA")) System.out.println("Tag 072 ongelmissa asiasanassa " + id);
						} else if (!tag.equals("040") && !tag.equals("035")) {
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
		return this.allarsSkos.createResource(id);
	}
	
	// Tämä myös luo uuden käsitteen kannalta oleelliset muut määrittelyt
	public void kirjoitaLabelAllarsSkosiin(String id, String label, String kieli) {
		if (kieli.equals("se")) kieli = "sv";
		Property prefLabel = this.allarsSkos.createProperty(this.skosNS + "prefLabel");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.allarsSkos.createLiteral(label, kieli);
		this.allarsSkos.add(subj, prefLabel, obj);
		
		Property type = this.allarsSkos.createProperty(this.rdfNS + "type");
		Resource skosConcept = this.allarsSkos.createResource(this.skosNS + "Concept");
		this.allarsSkos.add(subj, type, skosConcept);
		
		Resource juuri = this.allarsSkos.createResource(this.allarsNS);
		Property inScheme = this.allarsSkos.createProperty(this.skosNS + "inScheme");
		this.allarsSkos.add(subj, inScheme, juuri);
	}

	public void kirjoitaMaantieteellinenLabelAllarsSkosiin(String id, String label, String kieli) {
		this.kirjoitaLabelAllarsSkosiin(id, label, kieli);
		Resource subj = this.luoKasiteresurssi(id);
		/*Property skosNote = this.allarsSkos.createProperty(this.skosNS + "note");
		Literal obj = this.allarsSkos.createLiteral("151");
		this.allarsSkos.add(subj, skosNote, obj);*/
		
		Property type = this.allarsSkos.createProperty(this.rdfNS + "type");
		Resource skosConcept = this.allarsSkos.createResource(this.skosNS + "Concept");
		Resource allarsGeographicConcept = this.allarsSkos.createResource(this.allarsMetaNS + "GeographicalConcept");
		this.allarsSkos.remove(subj, type, skosConcept);
		this.allarsSkos.add(subj, type, allarsGeographicConcept);
	}
	
	public void kirjoitaAltLabelAllarsSkosiin(String id, String label, String kieli) {
		Property pred = this.allarsSkos.createProperty(this.skosNS + "altLabel");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.allarsSkos.createLiteral(label, kieli);
		this.allarsSkos.add(subj, pred, obj);
	}
	
	public void kirjoitaBroaderAllarsSkosiin(String id, String laajemmanTerminId) {
		Property pred = this.allarsSkos.createProperty(this.skosNS + "broader");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(laajemmanTerminId);
		this.allarsSkos.add(subj, pred, obj);
	}
	            
	public void kirjoitaNarrowerAllarsSkosiin(String id, String suppeammanTerminId) {
		Property pred = this.allarsSkos.createProperty(this.skosNS + "narrower");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(suppeammanTerminId);
		this.allarsSkos.add(subj, pred, obj);
	}
	
	public void kirjoitaRelatedAllarsSkosiin(String id, String rinnakkaisTerminId) {
		Property pred = this.allarsSkos.createProperty(this.skosNS + "related");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(rinnakkaisTerminId);
		this.allarsSkos.add(subj, pred, obj);
	}
	
	public void kirjoitaNoteAllarsSkosiin(String id, String kommentti, String kieli) {
		Property pred = this.allarsSkos.createProperty(this.skosNS + "note");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.allarsSkos.createLiteral(kommentti, kieli);
		this.allarsSkos.add(subj, pred, obj);
	}
	
	public void luoRyhmatAllarsSkosiin() {
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
			
			Resource ryhma = this.allarsSkos.createResource(this.ysaNS + "ryhma_" + numero);
			String kuvaus = ((Literal)stmt.getObject()).getLexicalForm();
			
			Property type = this.allarsSkos.createProperty(this.rdfNS + "type");
			Resource skosCollection = this.allarsSkos.createResource(this.skosNS + "Collection");
			this.allarsSkos.add(ryhma, type, skosCollection);
			Property prefLabel = this.allarsSkos.createProperty(this.skosNS + "prefLabel");
			Literal obj = this.allarsSkos.createLiteral(numero + " " + kuvaus, lang);
			this.allarsSkos.add(ryhma, prefLabel, obj);
			// Tekee hiddenlabelit
			Property hiddenLabel = this.allarsSkos.createProperty(this.skosNS + "hiddenLabel");
			StringTokenizer st = new StringTokenizer(kuvaus, ".");
			while (st.hasMoreTokens()) {
				obj = this.allarsSkos.createLiteral(st.nextToken().trim(), lang);
				this.allarsSkos.add(ryhma, hiddenLabel, obj);
			}
			Resource juuri = this.allarsSkos.createResource(this.allarsNS);
			Property inScheme = this.allarsSkos.createProperty(this.skosNS + "inScheme");
			this.allarsSkos.add(ryhma, inScheme, juuri);
		}	
	}
	
	public void kirjoitaSourceAllarsSkosiin(String id, String lahde) {
		Property pred = this.allarsSkos.createProperty(this.allarsMetaNS + "source");
		Resource subj = this.luoKasiteresurssi(id);
		if (lahde.length() > 6)
			if (lahde.substring(0, 6).equals("Källa:")) {
				lahde = lahde.substring(6);
			}
		Literal obj = this.allarsSkos.createLiteral(lahde.trim(), "sv");
		this.allarsSkos.add(subj, pred, obj);
	}
	
	public void kirjoitaRyhmaAllarsSkosiin(String id, String sisalto) {
		String numero = sisalto.substring(3).trim();

		if (!numero.equals("")) {
			Resource ysaskosryhma = this.allarsSkos.createResource(this.ysaNS + "ryhma_" + numero);
			Resource subj = this.luoKasiteresurssi(id);
			Property member = this.allarsSkos.createProperty(this.skosNS + "member");
			this.allarsSkos.add(ysaskosryhma, member, subj);
		}
	}
	
	public void luoJuuri() {
		Resource juuri = this.allarsSkos.createResource(this.allarsNS);
		Property type = this.allarsSkos.createProperty(this.rdfNS + "type");
		Resource conceptScheme = this.allarsSkos.createResource(this.skosNS + "ConceptScheme");
		this.allarsSkos.add(juuri, type, conceptScheme);
		
		Resource property = this.allarsSkos.createProperty(this.rdfNS + "Property");
		Property ysaSource = this.allarsSkos.createProperty(this.allarsMetaNS + "source");
		Property rdfsLabel = this.allarsSkos.createProperty(this.rdfsNS + "label");
		Property domain = this.allarsSkos.createProperty(this.rdfsNS + "domain");
		Resource skosConcept = this.allarsSkos.createResource(this.skosNS + "Concept");
		Literal sourceLabelFi = this.allarsSkos.createLiteral("Lähde", "fi");
		Literal sourceLabelSv = this.allarsSkos.createLiteral("Källa", "sv");
		Literal sourceLabelEn = this.allarsSkos.createLiteral("Source", "en");
		
		this.allarsSkos.add(ysaSource, type, property);
		this.allarsSkos.add(ysaSource, domain, skosConcept);
		this.allarsSkos.add(ysaSource, rdfsLabel, sourceLabelFi);
		this.allarsSkos.add(ysaSource, rdfsLabel, sourceLabelSv);
		this.allarsSkos.add(ysaSource, rdfsLabel, sourceLabelEn);
		
		Resource owlClass = this.allarsSkos.createResource("http://www.w3.org/2002/07/owl#Class");
		Property subClassOf = this.allarsSkos.createProperty("http://www.w3.org/2000/01/rdf-schema#subClassOf");
		Resource allarsGeographicConcept = this.allarsSkos.createResource(this.allarsMetaNS + "GeographicalConcept");
		Literal geoLabelFi = this.allarsSkos.createLiteral("Maantieteellinen paikka", "fi");
		Literal geoLabelSv = this.allarsSkos.createLiteral("Geografisk plats", "sv");
		Literal geoLabelEn = this.allarsSkos.createLiteral("Geographical location", "en");
		this.allarsSkos.add(allarsGeographicConcept, type, owlClass);
		this.allarsSkos.add(allarsGeographicConcept, subClassOf, skosConcept);
		this.allarsSkos.add(allarsGeographicConcept, rdfsLabel, geoLabelFi);
		this.allarsSkos.add(allarsGeographicConcept, rdfsLabel, geoLabelSv);
		this.allarsSkos.add(allarsGeographicConcept, rdfsLabel, geoLabelEn);
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
		StmtIterator iter = this.allarsSkos.listStatements();
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getObject().isAnon()) {
				poistettavat.add(stmt);
			}
		}
		for (Statement s:poistettavat) this.allarsSkos.remove(s);
	}
	
	public void testaaEtsiOngelmat() {
		StmtIterator iter = this.allarsSkos.listStatements();
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
	
	public void kirjoitaYsaSkos(String allarsSkosinPolku) {
		try {
			FileOutputStream os = new FileOutputStream(allarsSkosinPolku);
			BufferedOutputStream bs = new BufferedOutputStream(os);
			RDFWriter kirjuri = this.allarsSkos.getWriter();
			kirjuri.setProperty("showXmlDeclaration", true);
			kirjuri.write(this.allarsSkos, bs, null);
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("SKOS-muunnettu Allärs kirjoitettiin tiedostoon " + allarsSkosinPolku);
	}
	
	public static void main(String[] args) {
		if (args.length != 3) {
			System.out.println("Anna kolme parametria: [muunnettava tiedosto] [uusi tiedosto] [YSA--Allärs-Groups -tiedosto]");
		}
		AllarsSKOSmuunnin ym = new AllarsSKOSmuunnin(args[2]);
		ym.muunna(args[0]);
		ym.poistaAnonyymejaNodejaSisaltavatTriplet();
		ym.kirjoitaYsaSkos(args[1]);
	}
	
}
