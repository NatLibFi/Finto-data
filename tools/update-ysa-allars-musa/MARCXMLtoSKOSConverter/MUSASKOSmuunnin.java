import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
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

public class MUSASKOSmuunnin {

	private final String skosNS = "http://www.w3.org/2004/02/skos/core#";
	private final String rdfNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
	private final String musaNS = "http://www.yso.fi/onto/musa/";
	private final String rdfsNS = "http://www.w3.org/2000/01/rdf-schema#";
	
	private Model musaskos;
	private Document musa;
	private HashMap<String, String> idMap;
	
	public MUSASKOSmuunnin() {
		this.idMap = new HashMap<String, String>();
		this.musaskos = ModelFactory.createDefaultModel();
		this.musaskos.setNsPrefixes(this.luoNimiavaruudet());
	}
	
	public PrefixMapping luoNimiavaruudet() {
		PrefixMapping na = PrefixMapping.Factory.create();
		na.setNsPrefix("", this.musaNS);
		na.setNsPrefix("skos", this.skosNS);
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
		this.musa = MUSASKOSmuunnin.parsi(muunnettavaTiedosto);
		NodeList recordNodelist = this.musa.getElementsByTagName("record");
		
		for (int i = 0; i < recordNodelist.getLength(); i++) {
			Node recordNode = recordNodelist.item(i);
			NodeList recordLapset = recordNode.getChildNodes();
			// Tutkitaan ensin, että kyseessä on MUSA:n (eikä CILLA:n) termi
			boolean onMusasta = this.kaivaDatafieldinArvoRecordNodesta(recordNode, "040", "f").equals("musa");				
			if (onMusasta) {	
				// kaivetaan ensin ID
				String id = this.musaNS + "ONGELMA";
				id = this.musaNS + "p" + this.kaivaControlfieldinArvoRecordNodesta(recordNode, "001");
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
							if (tag.equals("150")) {
								// prefLabel fi
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
								String lisamaare = "ONGELMA";
								lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
								if (!lisamaare.equals("ONGELMA")) {
									this.idMap.put(sisalto + " -- " + lisamaare, id);
								} else 
									this.idMap.put(sisalto, id);
							}
						}
					}
				}
			}
		}
		
		
		for (int i = 0; i < recordNodelist.getLength(); i++) {
			Node recordNode = recordNodelist.item(i);
			NodeList recordLapset = recordNode.getChildNodes();
			// Tutkitaan ensin, että kyseessä on MUSA:n (eikä CILLA:n) termi
			boolean onMusasta = this.kaivaDatafieldinArvoRecordNodesta(recordNode, "040", "f").equals("musa");				
			if (onMusasta) {	
				// kaivetaan ensin ID
				String id = this.musaNS + "ONGELMA";
				id = this.musaNS + "p" + this.kaivaControlfieldinArvoRecordNodesta(recordNode, "001");
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
							if (tag.equals("150")) {
								// prefLabel fi
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
								String lisamaare = "ONGELMA";
								lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
								if (!lisamaare.equals("ONGELMA")) {
									this.kirjoitaLabelMusaskosiin(id, sisalto + " -- " + lisamaare, "fi");
								} else 
								this.kirjoitaLabelMusaskosiin(id, sisalto, "fi");
							} else if (tag.equals("550")) {
								// broader, narrower tai related
								boolean narrower = this.subfieldissaOnAttribuuttiKoodilla(subfieldNodet, "w", "h");
								boolean broader = this.subfieldissaOnAttribuuttiKoodilla(subfieldNodet, "w", "g");
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
								String lisamaare = "ONGELMA";
								lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
								if (!lisamaare.equals("ONGELMA")) {
									sisalto = sisalto + " -- " + lisamaare;
								}
								String objId = this.kaivaIdAsiasananPerusteella(sisalto);
								if (narrower) this.kirjoitaNarrowerMusaskosiin(id, objId);
								else if (broader) this.kirjoitaBroaderMusaskosiin(id, objId);
								else this.kirjoitaRelatedMusaskosiin(id, objId);
							} else if (tag.equals("680")) {
								// note
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "i");
								this.kirjoitaNoteMusaskosiin(id, sisalto, "fi");
							} else if (tag.equals("750")) {
								// prefLabel sv
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
								String lisamaare = "ONGELMA";
								lisamaare= this.kaivaSubfieldinArvo(subfieldNodet, "x");
								if (!lisamaare.equals("ONGELMA")) {
									this.kirjoitaLabelMusaskosiin(id, sisalto + " -- " + lisamaare, "sv");
								} else
								this.kirjoitaLabelMusaskosiin(id, sisalto, "sv");
							} else if (tag.equals("450")) {
								// altLabel
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
								String lisamaare = "ONGELMA";
								lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
								if (!lisamaare.equals("ONGELMA")) {
									this.kirjoitaAltLabelMusaskosiin(id, sisalto + " -- " + lisamaare, "fi");
								} else
								this.kirjoitaAltLabelMusaskosiin(id, sisalto, "fi");
							} else if (tag.equals("035")) {
								// id tagissa
							} else if (!tag.equals("040")) {
								System.out.println("tuntematon tag: " + tag);	
							}
						}
					}
				}
			} else {
				// kaivetaan ruotsinkieliset notet ja altLabelit
				// kaivetaan ensin ID
				String id = this.musaNS + "ONGELMA";
				id = this.musaNS + "c" + this.kaivaControlfieldinArvoRecordNodesta(recordNode, "001");
				
				// kaivetaan notet ja altLabelit
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
							if (tag.equals("680")) {
								// note
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "i");
								this.kirjoitaNoteMusaskosiin(id, sisalto, "sv");
							} else if (tag.equals("450")) {
								// altLabel
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
								String lisamaare = "ONGELMA";
								lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
								if (!lisamaare.equals("ONGELMA")) {
									this.kirjoitaAltLabelMusaskosiin(id, sisalto + " -- " + lisamaare, "sv");
								} else 
								this.kirjoitaAltLabelMusaskosiin(id, sisalto, "sv");
							} else if (tag.equals("750")) {
								// musa-prefLabel, jolla matchataan lopuksi
								sisalto = this.kaivaSubfieldinArvo(subfieldNodet, "a");
								String lisamaare = "ONGELMA";
								lisamaare = this.kaivaSubfieldinArvo(subfieldNodet, "x");
								if (!lisamaare.equals("ONGELMA")) {
									this.kirjoitaCillaSuomiPrefLabelMusaskosiin(id, sisalto + " -- " + lisamaare, "sv");
								} else 
								this.kirjoitaCillaSuomiPrefLabelMusaskosiin(id, sisalto, "fi");
							}
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
		return this.musaskos.createResource(id);
	}
	
	// Tämä myös luo uuden käsitteen kannalta oleelliset muut määrittelyt
	public void kirjoitaLabelMusaskosiin(String id, String label, String kieli) {
		if (kieli.equals("se")) kieli = "sv";
		Property prefLabel = this.musaskos.createProperty(this.skosNS + "prefLabel");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.musaskos.createLiteral(label, kieli);
		this.musaskos.add(subj, prefLabel, obj);
		
		Property type = this.musaskos.createProperty(this.rdfNS + "type");
		Resource skosConcept = this.musaskos.createResource(this.skosNS + "Concept");
		this.musaskos.add(subj, type, skosConcept);
		
		Resource juuri = this.musaskos.createResource(this.musaNS);
		Property inScheme = this.musaskos.createProperty(this.skosNS + "inScheme");
		this.musaskos.add(subj, inScheme, juuri);
	}

	// Tätä käytetään vain cilla-altLabeleita poimittaessa, kun kirjoitetaan Cillasta MUSA-prefLabel
	public void kirjoitaCillaSuomiPrefLabelMusaskosiin(String id, String label, String kieli) {
		if (kieli.equals("se")) kieli = "sv";
		Property prefLabel = this.musaskos.createProperty(this.skosNS + "prefLabel");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.musaskos.createLiteral(label, kieli);
		this.musaskos.add(subj, prefLabel, obj);
		
		Property type = this.musaskos.createProperty(this.rdfNS + "type");
		Resource skosCillaConcept = this.musaskos.createResource(this.skosNS + "CillaConcept");
		this.musaskos.add(subj, type, skosCillaConcept);
	}
	
	public void kirjoitaAltLabelMusaskosiin(String id, String label, String kieli) {
		Property pred = this.musaskos.createProperty(this.skosNS + "altLabel");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.musaskos.createLiteral(label, kieli);
		this.musaskos.add(subj, pred, obj);
	}
	
	public void kirjoitaBroaderMusaskosiin(String id, String laajemmanTerminId) {
		Property pred = this.musaskos.createProperty(this.skosNS + "broader");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(laajemmanTerminId);
		this.musaskos.add(subj, pred, obj);
	}
	            
	public void kirjoitaNarrowerMusaskosiin(String id, String suppeammanTerminId) {
		Property pred = this.musaskos.createProperty(this.skosNS + "narrower");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(suppeammanTerminId);
		this.musaskos.add(subj, pred, obj);
	}
	
	public void kirjoitaRelatedMusaskosiin(String id, String rinnakkaisTerminId) {
		Property pred = this.musaskos.createProperty(this.skosNS + "related");
		Resource subj = this.luoKasiteresurssi(id);
		Resource obj = this.luoKasiteresurssi(rinnakkaisTerminId);
		this.musaskos.add(subj, pred, obj);
	}
	
	public void kirjoitaNoteMusaskosiin(String id, String kommentti, String kieli) {
		Property pred = this.musaskos.createProperty(this.skosNS + "note");
		Resource subj = this.luoKasiteresurssi(id);
		Literal obj = this.musaskos.createLiteral(kommentti, kieli);
		this.musaskos.add(subj, pred, obj);
	}
	
	public void luoJuuri() {
		Resource juuri = this.musaskos.createResource(this.musaNS);
		Property type = this.musaskos.createProperty(this.rdfNS + "type");
		Resource conceptScheme = this.musaskos.createResource(this.skosNS + "ConceptScheme");
		this.musaskos.add(juuri, type, conceptScheme);
	}
	
	public String muutaUriksi(String muutettava) {
		muutettava = muutettava.replace('ä', 'a');
		muutettava = muutettava.replace('ö', 'o');
		muutettava = muutettava.replace(' ', '_');
		muutettava = muutettava.toLowerCase();
		return muutettava;
	}
	
	public void poistaDummyCillaConceptitSamallaPoimienRuotsiAltLabelit() {
		Resource skosCillaConcept = this.musaskos.createResource(this.skosNS + "CillaConcept");
		Property prefLabel = this.musaskos.createProperty(this.skosNS + "prefLabel");
		Property altLabel = this.musaskos.createProperty(this.skosNS + "altLabel");
		Property note = this.musaskos.createProperty(this.skosNS + "note");
		Property type = this.musaskos.createProperty(this.rdfNS + "type");
		
		Vector<Resource> cillaDummySubjektit = new Vector<Resource>();
		StmtIterator iter = this.musaskos.listStatements((Resource)null, type, skosCillaConcept);
		while (iter.hasNext()) {
			cillaDummySubjektit.add(iter.nextStatement().getSubject());
		}
		HashMap<String, String> fiPrefLabelSvAltLabelMap = new HashMap<String, String>();
		HashMap<String, String> fiPrefLabelSvNoteMap = new HashMap<String, String>();
		Vector<Statement> poistettavat = new Vector<Statement>();
		for (Resource subj:cillaDummySubjektit) {
			String fiPrefLabel = "ONGELMA";
			String svAltLabel = "ONGELMA";
			String svNote = "ONGELMA";
			iter = this.musaskos.listStatements(subj, (Property)null, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();	
				if (stmt.getPredicate().getURI().equals(this.skosNS + "prefLabel")) {
					fiPrefLabel = ((Literal)stmt.getObject()).getLexicalForm();
				} else if (stmt.getPredicate().getURI().equals(this.skosNS + "altLabel")) {
					svAltLabel = ((Literal)stmt.getObject()).getLexicalForm();
				} else if (stmt.getPredicate().getURI().equals(this.skosNS + "note")) {
					svNote = ((Literal)stmt.getObject()).getLexicalForm();
				}
				poistettavat.add(stmt);
			}
			if ( (!fiPrefLabel.equals("ONGELMA")) && (!svAltLabel.equals("ONGELMA")) ) {
				fiPrefLabelSvAltLabelMap.put(fiPrefLabel, svAltLabel);
			}
			if ( (!fiPrefLabel.equals("ONGELMA")) && (!svNote.equals("ONGELMA")) ) {
				fiPrefLabelSvNoteMap.put(fiPrefLabel, svNote);
			}
		}
		iter = this.musaskos.listStatements((Resource)null, prefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String fiPrefLabel = ((Literal)stmt.getObject()).getLexicalForm();
				if (fiPrefLabelSvAltLabelMap.containsKey(fiPrefLabel)) {
					this.musaskos.add(stmt.getSubject(), altLabel, this.musaskos.createLiteral(fiPrefLabelSvAltLabelMap.get(fiPrefLabel), "sv"));
				}
				if (fiPrefLabelSvNoteMap.containsKey(fiPrefLabel)) {
					this.musaskos.add(stmt.getSubject(), note, this.musaskos.createLiteral(fiPrefLabelSvNoteMap.get(fiPrefLabel), "sv"));
				}
			}
		}
		
		for (Statement s:poistettavat) this.musaskos.remove(s);
	}
	
	public void testaaEtsiOngelmat() {
		StmtIterator iter = this.musaskos.listStatements();
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
	
	public void kirjoitaMusaskos(String musaskosinPolku) {
		try {
			FileOutputStream os = new FileOutputStream(musaskosinPolku);
			BufferedOutputStream bs = new BufferedOutputStream(os);
			RDFWriter kirjuri = this.musaskos.getWriter();
			kirjuri.setProperty("showXmlDeclaration", true);
			kirjuri.write(this.musaskos, bs, null);
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("SKOS-muunnettu MUSA kirjoitettiin tiedostoon " + musaskosinPolku);
	}
	
	public static void main(String[] args) {
		if (args.length != 2) {
			System.out.println("Anna kaksi parametria: [muunnettava tiedosto] [uusi tiedosto]");
		}
		MUSASKOSmuunnin mm = new MUSASKOSmuunnin();
		mm.muunna(args[0]);
		mm.poistaDummyCillaConceptitSamallaPoimienRuotsiAltLabelit();
		mm.testaaEtsiOngelmat();
		mm.kirjoitaMusaskos(args[1]);
	}
	
}
