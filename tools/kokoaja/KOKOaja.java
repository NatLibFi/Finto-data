package koko;

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Vector;

import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.OntModelSpec;
import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.RDFWriter;
import com.hp.hpl.jena.rdf.model.ResIterator;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.util.FileManager;
import com.hp.hpl.jena.vocabulary.DC;
import com.hp.hpl.jena.vocabulary.OWL;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;

public class KOKOaja {

	private final String skosNs = "http://www.w3.org/2004/02/skos/core#";
	private final String skosextNs = "http://purl.org/finnonto/schema/skosext#";
	private final String kokoNs ="http://www.yso.fi/onto/koko/";
	private final String kokoMetaNs ="http://www.yso.fi/onto/koko-meta/";

	private final String kokoUriValiosa = "p"; //KOKO-urin lokaaliosan kirjaintunnus ennen juoksevaa numeroa
	private final String defaultLang = "fi";

	private OntModel koko;
	private HashSet<Statement> sailotytObjPropStatementit;
	private HashSet<Vector<Statement>> sailotyt;
	private HashMap<Resource, Resource> vanhaUriKokoUriMap;
	private HashMap<Resource, String> nykyisenMallinPrefLabelMap;
	private HashMap<Resource, HashSet<Resource>> nykyisenMallinExactMatchit;
	private HashMap<String, HashMap<String, Resource>> kielitettyLabelKokoUriMap; //kieli, label, KokoURI
	private HashMap<String, HashMap<Resource, String>> kielitettyKokoUriLabelMap; //kieli, KokoURI, label

	HashMap<String, String> ontologioidenPolutNimetMap;

	private OntModel lisattavaMalli;
	private Resource lisattavanMalliOmaKasite;
	private int viimeisinKokoUrinLoppuosa;
	
	private int laskuri;

	public KOKOaja() {
		this.kielitettyLabelKokoUriMap = new HashMap<String, HashMap<String,Resource>>();
		this.kielitettyLabelKokoUriMap.put(defaultLang, new HashMap<String, Resource>());
		this.kielitettyKokoUriLabelMap = new HashMap<String, HashMap<Resource,String>>();
		this.kielitettyKokoUriLabelMap.put(defaultLang, new HashMap<Resource, String>());
		this.sailotyt = new HashSet<Vector<Statement>>();
		this.sailotytObjPropStatementit = new HashSet<Statement>();
		this.koko = this.luoAihio();
	}

	/*
	 * 1 Kaydaan ontologiat lapi yksitellen
	 *  1.1 lisataan kaikki skosConceptit, joille loytyy kokoURI
	 *    - kokoUri voi loytya joko suoraan, tai fiPrefLabelin perusteella
	 *    1.1.1 niiden kohdalla, joille ei loydy, laitetaan statementit talteen HashSettiin
	 *    1.1.2 sailotaan myos sellaiset, joiden objektille ei loydy vastinetta skos- tai koko-nimiavaruuksista
	 * 2 Luodaan uudet urit 1.1.1-kohdan kasitteille, jos niita ei vielakaan loydy
	 * 3 Laitetaan 1.1.2-kohdan statementit paikalleen
	 */
	public void kokoa(String ontologioidenPolutTxt) {
		Vector<String> ontologioidenPolutVektori = this.parsiOntologioidenPolutVektoriin(ontologioidenPolutTxt);
		for (String lisattavanOntologianPolku:ontologioidenPolutVektori) {
			if (!lisattavanOntologianPolku.startsWith("#")) {
				System.out.println("Lisataan " + lisattavanOntologianPolku + " KOKOon.");
				this.lisaaOntologiaKokoon(this.ontologioidenPolutNimetMap.get(lisattavanOntologianPolku), this.lueMalli(lisattavanOntologianPolku));
			}
		}
		this.tuotaSailotytKokoon();
		this.tuotaObjectPropertytKokoon();
		this.siivoaConceptStatusCollectioneiltaJaPoistetaanSkosConceptStatusKaikilta();
		this.poistaTeroConceptTyypitYsoConcepteilta();
		this.poistaLoopitJaYlimaaraisetBroaderSuhteet();
		this.korjaaConceptSchemet();
	}

	public OntModel luoAihio() {
		//System.out.println("Luodaan aihio");
		OntModel aihio = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
		aihio.setNsPrefix("skos", this.skosNs);
		aihio.setNsPrefix("skosext", this.skosextNs);
		aihio.setNsPrefix("koko", this.kokoNs);
		aihio.setNsPrefix("koko-meta", this.kokoMetaNs);
		//System.out.println("Aihio luotu");
		return aihio;
	}

	public void lueUriVastaavuudetTiedostosta(String polku) {
		System.out.println("Luetaan URI-vastaavuudet tiedostosta " + polku);
		int korkeinNro = 0;
		this.vanhaUriKokoUriMap = new HashMap<Resource, Resource>();
		try {
			BufferedReader br = new BufferedReader( new InputStreamReader( new FileInputStream(polku), "UTF8" ) );

			String rivi = br.readLine().trim();
			//int i = 0;
			while (rivi != null) {				
				rivi = rivi.trim();

				String[] uriTaulukko = rivi.split(" ");
				Resource vanhaRes = this.koko.createResource(uriTaulukko[0].trim());
				Resource kokoRes = this.koko.createResource(uriTaulukko[1].trim());
				this.vanhaUriKokoUriMap.put(vanhaRes, kokoRes);
				int uriNro = Integer.parseInt(kokoRes.getLocalName().substring(1));
				if (uriNro > korkeinNro) korkeinNro = uriNro;
				rivi = br.readLine();
			}
			br.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		this.viimeisinKokoUrinLoppuosa = korkeinNro;
	}

	public Vector<String> parsiOntologioidenPolutVektoriin(String ontologioidenPolutTxt) {
		this.ontologioidenPolutNimetMap = new HashMap<String, String>();
		Vector<String> polkuVektori = new Vector<String>();
		try {
			BufferedReader br = new BufferedReader( new InputStreamReader( new FileInputStream(ontologioidenPolutTxt), "UTF8" ) );

			String rivi = br.readLine().trim();
			while (rivi != null) {
				rivi = rivi.trim();
				String[] uriTaulukko = rivi.split(" ");
				polkuVektori.add(uriTaulukko[1].trim());
				this.ontologioidenPolutNimetMap.put(uriTaulukko[1].trim(), uriTaulukko[0].trim());
				rivi = br.readLine();
			}
			br.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return polkuVektori;
	}

	private void lisaaOntologiaKokoon(String ontologianTunnus, OntModel malli) {
		this.lisattavaMalli = malli;
		this.lisattavanMalliOmaKasite = this.lisattavaMalli.createResource(this.kokoMetaNs + ontologianTunnus.toUpperCase() + "Concept");
		this.koko.add(this.lisattavanMalliOmaKasite, RDF.type, OWL.Class);
		this.koko.add(this.lisattavanMalliOmaKasite, RDFS.subClassOf, this.koko.createResource(this.skosNs + "Concept"));
		this.koko.add(this.lisattavanMalliOmaKasite, RDFS.label, this.koko.createLiteral(ontologianTunnus + "-k‰site", this.defaultLang));
		this.taydennaUriVastaavuudetExactMatchienPerusteella();
		this.taytaNykyisenMallinPrefLabelMap();
		Resource skosConcept = this.koko.createResource(this.skosNs + "Concept");
		Resource skosCollection = this.koko.createResource(this.skosNs + "Collection");
		StmtIterator iter = this.lisattavaMalli.listStatements((Resource)null, RDF.type, skosConcept);
		this.lisaaOntologiaKokoonIteroija(iter);
		iter = this.lisattavaMalli.listStatements((Resource)null, RDF.type, skosCollection);
		this.lisaaOntologiaKokoonIteroija(iter);
	}

	private void lisaaOntologiaKokoonIteroija(StmtIterator iter) {
		int i = 0;
		while (iter.hasNext()) {
			i++;
			if (i%100 == 0) {
				System.out.print(".");
			}
			if (i%10000 == 0) {
				System.out.println();
			}

			Statement stmt = iter.nextStatement();
			Resource vanhaRes = stmt.getSubject();
			Resource kokoRes;
			if (this.vanhaUriKokoUriMap.containsKey(vanhaRes)) {
				kokoRes = this.vanhaUriKokoUriMap.get(vanhaRes);
				this.lisaaResurssiKokoon(vanhaRes, kokoRes);
			} else {
				kokoRes = this.tuotaKokoResurssiLabelinPerusteella(vanhaRes);
				if (kokoRes == null) {
					this.sailoResurssi(vanhaRes);
				} else {
					this.vanhaUriKokoUriMap.put(vanhaRes, kokoRes);
					this.lisaaResurssiKokoon(vanhaRes, kokoRes);
				}
			}
		}
		System.out.println();
	}
	
	private void lisaaResurssiKokoon(Resource vanhaRes, Resource kokoRes) {
		Property skosExactMatch = this.koko.createProperty(this.skosNs + "exactMatch");
		// TODO: hieman purkkaliimaratkaisu
		if (this.lisattavanMalliOmaKasite.getURI().contains("YSOConcept") || !vanhaRes.getNameSpace().contains("http://www.yso.fi/onto/yso/")) {
			this.koko.add(kokoRes, RDF.type, this.lisattavanMalliOmaKasite);
		}
		this.koko.add(kokoRes, skosExactMatch, vanhaRes);
		StmtIterator iter = this.lisattavaMalli.listStatements(vanhaRes, (Property)null, (RDFNode)null);
		//long time = System.currentTimeMillis();
		while (iter.hasNext()) {
			//System.out.println(System.currentTimeMillis()-time);
			//time = System.currentTimeMillis();
			Statement stmt = iter.nextStatement();
			this.lisaaStatementKokoon(kokoRes, stmt);
		}
	}

	private void lisaaStatementKokoon(Resource kokoRes, Statement stmt) {
		String ysaNameSpace = "http://www.yso.fi/onto/ysa/";
		String allarsNameSpace = "http://www.yso.fi/onto/allars/";
		String stametaNameSpace = "http://www.yso.fi/onto/stameta/";
		String meshNameSpace = "http://www.yso.fi/onto/mesh/";

		Property skosPrefLabel = this.koko.createProperty(this.skosNs + "prefLabel");
		Property skosAltLabel = this.koko.createProperty(this.skosNs + "altLabel");
		String predNs = stmt.getPredicate().getNameSpace();
		if (predNs.equals(this.skosNs) || predNs.equals(this.skosextNs) || predNs.equals(RDFS.getURI()) || predNs.equals(RDF.getURI())) {
			if (stmt.getObject().isURIResource()) {
				Resource vanhaObj = (Resource)(stmt.getObject());
				if (stmt.getPredicate().getURI().equals(this.skosNs + "topConceptOf")) {
					
				} else if (vanhaObj.getNameSpace().equals(this.skosNs) || vanhaObj.getLocalName().endsWith("conceptscheme") || vanhaObj.getNameSpace().equals(this.kokoMetaNs)) {
					this.koko.add(kokoRes, stmt.getPredicate(), vanhaObj);
				} else if (vanhaObj.getNameSpace().equals(ysaNameSpace) || vanhaObj.getNameSpace().equals(allarsNameSpace) || vanhaObj.getNameSpace().equals(stametaNameSpace) || vanhaObj.getNameSpace().equals(meshNameSpace)) {
					this.koko.add(kokoRes, stmt.getPredicate(), vanhaObj);
				} else if (this.vanhaUriKokoUriMap.containsKey(vanhaObj)) {
					Resource kokoObj = this.vanhaUriKokoUriMap.get(vanhaObj);
					this.koko.add(kokoRes, stmt.getPredicate(), kokoObj);
				} else {
					this.sailotytObjPropStatementit.add(stmt);
				}
			} else if (stmt.getPredicate().equals(skosPrefLabel)) {
				//System.out.print("P");
				Literal labelLiteral = (Literal)(stmt.getObject());
				if (this.laitaLabelMuistiin(kokoRes, labelLiteral)) {
					// Oli jo, tai oli resurssille, jolla ei ollut viela prefLabelia talla kielella
					this.koko.add(kokoRes, skosPrefLabel, labelLiteral);
				} else {
					// Resurssille oli jo prefLabel talla kielella -> laitetaan altLabeliksi
					this.koko.add(kokoRes, skosAltLabel, labelLiteral);
				}
			} else {
				this.koko.add(kokoRes, stmt.getPredicate(), stmt.getObject());
			}
		}
	}

	// Palauttaa true, jos labelia ei viela ollut tai se oli sama kuin olemassa ollut ja false jos labeli loytyi jo, mutta se oli eri
	private boolean laitaLabelMuistiin(Resource kokoRes, Literal labelLiteral) {
		String lang = labelLiteral.getLanguage();
		// Jos kielta ei loydy, otetaan kayttoon default
		if (lang.equals("")) lang = this.defaultLang;
		String labelString = labelLiteral.getLexicalForm();
		if (this.kielitettyLabelKokoUriMap.containsKey(lang) && this.kielitettyKokoUriLabelMap.containsKey(lang)) {
			HashMap<String, Resource> labelKokoUriMap = this.kielitettyLabelKokoUriMap.get(lang);
			HashMap<Resource, String> kokoUriLabelMap = this.kielitettyKokoUriLabelMap.get(lang);

			if (kokoUriLabelMap.containsKey(kokoRes) && kokoUriLabelMap.get(kokoRes).equals(labelLiteral.getLexicalForm())) {
				return true;
			} else if (!kokoUriLabelMap.containsKey(kokoRes) && !labelKokoUriMap.containsKey(labelLiteral.getLexicalForm())) {
				labelKokoUriMap.put(labelString, kokoRes);
				this.kielitettyLabelKokoUriMap.put(lang, labelKokoUriMap);
				kokoUriLabelMap.put(kokoRes, labelString);
				this.kielitettyKokoUriLabelMap.put(lang, kokoUriLabelMap);
				return true;
			} else if (!kokoUriLabelMap.containsKey(kokoRes) && labelKokoUriMap.containsKey(labelLiteral.getLexicalForm())) {
				labelKokoUriMap.put(labelString, kokoRes);
				this.kielitettyLabelKokoUriMap.put(lang, labelKokoUriMap);
				return true;
			} else {
				return false;
			}
		} else {
			HashMap<String, Resource> labelKokoUriMap = new HashMap<String, Resource>();
			labelKokoUriMap.put(labelString, kokoRes);
			this.kielitettyLabelKokoUriMap.put(lang, labelKokoUriMap);

			HashMap<Resource, String> kokoUriLabelMap = new HashMap<Resource, String>();
			kokoUriLabelMap.put(kokoRes, labelString);
			this.kielitettyKokoUriLabelMap.put(lang, kokoUriLabelMap);

			return true;
		}
	}

	private void sailoResurssi(Resource vanhaRes) {
		Vector<Statement> statementVector = new Vector<Statement>();
		StmtIterator iter = this.lisattavaMalli.listStatements(vanhaRes, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			statementVector.add(stmt);
		}
		if (this.lisattavanMalliOmaKasite.getURI().contains("YSOConcept") || !vanhaRes.getNameSpace().contains("http://www.yso.fi/onto/yso/")) {
			statementVector.add(this.lisattavaMalli.createStatement(vanhaRes, RDF.type, this.lisattavanMalliOmaKasite));
		}
		this.sailotyt.add(statementVector);
	}

	private void tuotaSailotytKokoon() {
		System.out.println("Tuotetaan " + this.sailotyt.size() + " sailottya kasitetta KOKOon");
		for (Vector<Statement> statementVector:this.sailotyt) {
			Resource vanhaRes = statementVector.get(0).getSubject();
			Resource kokoRes = null;
			if (this.vanhaUriKokoUriMap.containsKey(vanhaRes)) {
				kokoRes = this.vanhaUriKokoUriMap.get(vanhaRes);
			} else if (this.tuotaKokoResurssiLabelinPerusteella(vanhaRes) != null) { 
				kokoRes = this.tuotaKokoResurssiLabelinPerusteella(vanhaRes);
				this.vanhaUriKokoUriMap.put(vanhaRes, kokoRes);
			} else {
				kokoRes = this.luoSeuraavaKokoResurssi();
				this.vanhaUriKokoUriMap.put(vanhaRes, kokoRes);
				if (this.nykyisenMallinExactMatchit.containsKey(vanhaRes)) {
					HashSet<Resource> exactMatchSetti = this.nykyisenMallinExactMatchit.get(vanhaRes);
					for (Resource vastaavuus:exactMatchSetti) {
						this.vanhaUriKokoUriMap.put(vastaavuus, kokoRes);
					}
				}
			}
			for (Statement stmt:statementVector) {
				this.lisaaStatementKokoon(kokoRes, stmt);
			}
		}
	}

	private void tuotaObjectPropertytKokoon() {
		System.out.println("Tuotetaan " + this.sailotytObjPropStatementit.size() + " sailottya ObjProp-statementtia KOKOon");
		int i = 0;
		for (Statement stmt:this.sailotytObjPropStatementit) {
			Resource vanhaSubjRes = stmt.getSubject();
			Resource vanhaObjRes = (Resource)(stmt.getObject());

			if (this.vanhaUriKokoUriMap.containsKey(vanhaSubjRes) && this.vanhaUriKokoUriMap.containsKey(vanhaObjRes)) {
				Resource kokoSubjRes = this.vanhaUriKokoUriMap.get(vanhaSubjRes);
				Resource kokoObjRes = this.vanhaUriKokoUriMap.get(vanhaObjRes);
				this.koko.add(kokoSubjRes, stmt.getPredicate(), kokoObjRes);
			} else if (this.vanhaUriKokoUriMap.containsKey(vanhaSubjRes)) {
				Resource kokoSubjRes = this.vanhaUriKokoUriMap.get(vanhaSubjRes);
				this.koko.add(kokoSubjRes, stmt.getPredicate(), vanhaObjRes);
			} else if (vanhaObjRes.getURI().equals("http://www.yso.fi/onto/yso/p26114")) {
				// yson conceptSchemen virheellinen puritus, ei tarvitse tehd‰ mit‰‰n
			} else {
				// Ongelma, joka pitaisi raportoida jotenkin
				i++;
				System.out.println(i + ": ONGELMA: Ei loytynyt KOKO-URI-vastineita seuraavan statementin kasitteille: " + stmt.toString());
			}
		}
	}

	private Resource luoSeuraavaKokoResurssi() {
		this.viimeisinKokoUrinLoppuosa++;
		return this.koko.createResource(this.kokoNs + this.kokoUriValiosa + this.viimeisinKokoUrinLoppuosa);
	}

	private void taydennaUriVastaavuudetExactMatchienPerusteella() {
		this.nykyisenMallinExactMatchit = new HashMap<Resource, HashSet<Resource>>();		
		Property skosExactMatch = this.koko.createProperty(this.skosNs + "exactMatch");
		StmtIterator iter = this.lisattavaMalli.listStatements((Resource)null, skosExactMatch, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			Resource obj = (Resource)(stmt.getObject());
			if (this.vanhaUriKokoUriMap.containsKey(subj) && !this.vanhaUriKokoUriMap.containsKey(obj)) {
				this.vanhaUriKokoUriMap.put(obj, this.vanhaUriKokoUriMap.get(subj));
			} else if (!this.vanhaUriKokoUriMap.containsKey(subj) && this.vanhaUriKokoUriMap.containsKey(obj)) {
				this.vanhaUriKokoUriMap.put(subj, this.vanhaUriKokoUriMap.get(obj));
			} else if (!this.vanhaUriKokoUriMap.containsKey(subj) && !this.vanhaUriKokoUriMap.containsKey(obj)) {
				HashSet<Resource> subjSetti = new HashSet<Resource>();
				if (this.nykyisenMallinExactMatchit.containsKey(subj)) subjSetti = this.nykyisenMallinExactMatchit.get(subj);
				subjSetti.add(obj);
				this.nykyisenMallinExactMatchit.put(subj, subjSetti);
				HashSet<Resource> objSetti = new HashSet<Resource>();
				if (this.nykyisenMallinExactMatchit.containsKey(obj)) objSetti = this.nykyisenMallinExactMatchit.get(obj);
				objSetti.add(subj);
				this.nykyisenMallinExactMatchit.put(obj, objSetti);
			}
		}
	}

	private void taytaNykyisenMallinPrefLabelMap() {
		this.nykyisenMallinPrefLabelMap = new HashMap<Resource, String>();
		Property skosPrefLabel = this.koko.createProperty(this.skosNs + "prefLabel");

		StmtIterator iter = this.lisattavaMalli.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals(defaultLang)) {
				String labelString = ((Literal)(stmt.getObject())).getLexicalForm();
				this.nykyisenMallinPrefLabelMap.put(stmt.getSubject(), labelString);
			}
		}
	}

	// palauttaa null, jos kokossa ei ole samaa suomenkielista prefLablia
	private Resource tuotaKokoResurssiLabelinPerusteella(Resource vanhaRes) {
		Resource kokoRes = null;

		if (this.nykyisenMallinPrefLabelMap.containsKey(vanhaRes)) {
			HashMap<String, Resource> labelKokoUrimap = this.kielitettyLabelKokoUriMap.get(this.defaultLang);
			if (labelKokoUrimap.containsKey(this.nykyisenMallinPrefLabelMap.get(vanhaRes))) {
				kokoRes = labelKokoUrimap.get(this.nykyisenMallinPrefLabelMap.get(vanhaRes));
			}
		}

		return kokoRes;
	}

	public void siivoaConceptStatusCollectioneiltaJaPoistetaanSkosConceptStatusKaikilta() {
		Resource skosCollection = this.koko.createResource(this.skosNs + "Collection");
		Resource skosConcept = this.koko.createResource(this.skosNs + "Concept");
		LinkedList<Statement> poistettavat = new LinkedList<Statement>();
		StmtIterator iter = this.koko.listStatements((Resource)null, RDF.type, skosCollection);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			StmtIterator iter2 = this.koko.listStatements(stmt.getSubject(), RDF.type, (RDFNode)null);
			while (iter2.hasNext()) {
				Statement stmt2 = iter2.nextStatement();
				if (!stmt2.equals(stmt)) poistettavat.add(stmt2);
			}
		}
		this.koko.remove(poistettavat);
		HashSet<Statement> poistettavatSet = new HashSet<Statement>();
		iter = this.koko.listStatements((Resource)null, RDF.type, skosConcept);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			StmtIterator iter2 = this.koko.listStatements(stmt.getSubject(), RDF.type, (RDFNode)null);
			while (iter2.hasNext()) {
				Statement stmt2 = iter2.nextStatement();
				if (!stmt2.equals(stmt)) poistettavatSet.add(stmt);
			}
		}
		for (Statement s:poistettavatSet) this.koko.remove(s);
	}
	
	// Jos kasitteella A on broader suhde kasitteen B lapseen, silla ei voi olla broader suhdetta B:hen, poista myos broderit collectioneilta ja collectioneihin
	public void poistaLoopitJaYlimaaraisetBroaderSuhteet() {
		Property skosBroaderGeneric = this.koko.createProperty(this.skosextNs + "broaderGeneric");
		Property skosPartitive = this.koko.createProperty(this.skosextNs + "broaderPartitive");
		Property skosBroader = this.koko.createProperty(this.skosNs + "broader");
		
		this.removeBroaderitCollectioneilta(skosBroaderGeneric);
		this.removeBroaderitCollectioneilta(skosPartitive);
		this.removeBroaderitCollectioneilta(skosBroader);
		
		HashMap<Resource, HashSet<Resource>> suoratLapsetMap = this.getSuoraLapsetMap(skosBroader);
		//HashMap<Resource, HashSet<Resource>> suoratLapsetMap = this.getSuoraLapsetMap(skosBroaderGeneric);
		this.removeCycles(suoratLapsetMap, skosBroader);
		this.removeYlimaaraisetBroaderit(suoratLapsetMap, skosBroader);
		//this.removeCycles(suoratLapsetMap, skosBroaderGeneric);
		//this.removeYlimaaraisetBroaderit(suoratLapsetMap, skosBroaderGeneric);
		
		suoratLapsetMap = this.getSuoraLapsetMap(skosPartitive);
		this.removeCycles(suoratLapsetMap, skosPartitive);
		this.removeYlimaaraisetBroaderit(suoratLapsetMap, skosPartitive);
	}
	
	public void removeBroaderitCollectioneilta(Property broaderProp) {
		LinkedList<Statement> poistettavat = new LinkedList<Statement>();
		Resource skosCollection = this.koko.createResource(this.skosNs + "Collection");
		StmtIterator iter = this.koko.listStatements((Resource)null, RDF.type, skosCollection);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			StmtIterator iter2 = this.koko.listStatements((Resource)null, broaderProp, stmt.getSubject());
			while (iter2.hasNext()) {
				Statement stmt2 = iter2.nextStatement();
				poistettavat.add(stmt2);
			}
			iter2 = this.koko.listStatements(stmt.getSubject(), broaderProp, (RDFNode)null);
			while (iter2.hasNext()) {
				Statement stmt2 = iter2.nextStatement();
				poistettavat.add(stmt2);
			}
		}
		this.koko.remove(poistettavat);
	}
	
	public HashMap<Resource, HashSet<Resource>> getSuoraLapsetMap(Property lapsiProp) {
		HashMap<Resource, HashSet<Resource>> suoratLapsetMap = new HashMap<Resource, HashSet<Resource>>();
		
		StmtIterator iter = this.koko.listStatements((Resource)null, lapsiProp, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			Resource obj = (Resource)(stmt.getObject());
			HashSet<Resource> lapsetSet = new HashSet<Resource>();
			if (suoratLapsetMap.containsKey(obj)) {
				lapsetSet = suoratLapsetMap.get(obj);
			}
			lapsetSet.add(subj);
			suoratLapsetMap.put(obj, lapsetSet);
		}
		return suoratLapsetMap;
	}
	
	public void removeYlimaaraisetBroaderit(HashMap<Resource, HashSet<Resource>> suoratLapsetMap, Property broaderProp) {
		this.laskuri = 0;
		for (Resource subj:suoratLapsetMap.keySet()) {
			HashSet<Resource> paatellytLapsetSet = new HashSet<Resource>();
			Vector<Resource> paatellytLapsetVektori = new Vector<Resource>();
			HashSet<Resource> lapsetSet = suoratLapsetMap.get(subj);
			for (Resource suoraLapsi:lapsetSet) {
				if (suoratLapsetMap.containsKey(suoraLapsi)) {
					HashSet<Resource> lapsenLapsetSet = suoratLapsetMap.get(suoraLapsi);
					for (Resource lapsenlapsi:lapsenLapsetSet) {
						if (!paatellytLapsetSet.contains(lapsenlapsi)) {
							paatellytLapsetSet.add(lapsenlapsi);
							paatellytLapsetVektori.add(lapsenlapsi);
						}
					}
				}
			}
			for (int i = 0; i < paatellytLapsetVektori.size(); i++) {
				Resource paateltyLapsi = paatellytLapsetVektori.get(i);
				if (suoratLapsetMap.containsKey(paateltyLapsi)) {
					HashSet<Resource> lisaLapsetSet = suoratLapsetMap.get(paateltyLapsi);
					for (Resource lisaLapsi:lisaLapsetSet) {
						if (!paatellytLapsetSet.contains(lisaLapsi)) {
							paatellytLapsetSet.add(lisaLapsi);
							paatellytLapsetVektori.add(lisaLapsi);
						}
					}
				}
			}
			paatellytLapsetSet.retainAll(lapsetSet);
			for (Resource poistettava:paatellytLapsetSet) {
				this.koko.remove(poistettava, broaderProp, subj);
				this.laskuri++;
			}
		}
		System.out.println("Poistettu " + this.laskuri + " ylim‰‰r‰ist‰ " + broaderProp.getLocalName() + " -suhdetta.");
	}
	
	public void removeCycles(HashMap<Resource, HashSet<Resource>> suoratLapsetMap, Property sykliProp) {
		this.laskuri = 0;
		HashSet<Resource> juuret = new HashSet<Resource>();
		HashSet<Resource> eiJuuret = new HashSet<Resource>();
		for (Resource subj:suoratLapsetMap.keySet()) {
			HashSet<Resource> lapset = suoratLapsetMap.get(subj);
			eiJuuret.addAll(lapset);
			juuret.add(subj);
		}
		juuret.removeAll(eiJuuret);
		for (Resource juuri:juuret) {
			//if (sykliProp.equals(this.koko.createProperty(this.skosextNs + "broaderGeneric"))) System.out.println("Juuri (mahdollinen ripustumattoman k‰sitteen ongelma): " + juuri.getURI());
			if (sykliProp.equals(this.koko.createProperty(this.skosNs + "broader"))) System.out.println("Juuri (mahdollinen ripustumattoman k‰sitteen ongelma): " + juuri.getURI());
			this.cycleRemoval(suoratLapsetMap, new HashMap<Resource, Integer>(), juuri, juuri, sykliProp);
		}
		System.out.println("Poistettu " + this.laskuri + " " + sykliProp.getLocalName() + " -sykli‰.");
	}
	
	public void cycleRemoval(HashMap<Resource, HashSet<Resource>> suoratLapsetMap, HashMap<Resource, Integer> kaydyt, Resource nykyinen, Resource edellinen, Property sykliProp) {
		if (!(kaydyt.containsKey(nykyinen))) {
			kaydyt.put(nykyinen, 1);
			if (suoratLapsetMap.containsKey(nykyinen)) {
				HashSet<Resource> kaytavat = suoratLapsetMap.get(nykyinen);
				for (Resource kaytava:kaytavat) {
					this.cycleRemoval(suoratLapsetMap, kaydyt, kaytava, nykyinen, sykliProp);
				}
			}
		} else if (kaydyt.get(nykyinen).equals(1)) {
			this.koko.remove(nykyinen, sykliProp, edellinen);
			this.laskuri++;
			//System.out.println(this.laskuri + ". sykli: " + nykyinen.getURI() + " " + edellinen.getURI());
		} else if (kaydyt.get(nykyinen).equals(2)) {
			
		}
		kaydyt.put(nykyinen, 2);
	}
	
	public void poistaTeroConceptTyypitYsoConcepteilta() {
		HashSet<Resource> resurssitJoillaOnTeroConcept = new HashSet<Resource>();
		Resource teroConcept = this.koko.createResource(this.kokoMetaNs + "TEROConcept");
		StmtIterator iter = this.koko.listStatements((Resource)null, RDF.type, teroConcept);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			resurssitJoillaOnTeroConcept.add(stmt.getSubject());
		}
		
		HashSet<Resource> resurssitJoillaOnYsoConcept = new HashSet<Resource>();
		Resource ysoConcept = this.koko.createResource(this.kokoMetaNs + "YSOConcept");
		iter = this.koko.listStatements((Resource)null, RDF.type, ysoConcept);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			resurssitJoillaOnYsoConcept.add(stmt.getSubject());
		}
		
		HashSet<String> sailytettavienExactMatchienNimiavaruudet = new HashSet<String>();
		sailytettavienExactMatchienNimiavaruudet.add("http://www.yso.fi/onto/mesh/");
		sailytettavienExactMatchienNimiavaruudet.add("http://www.yso.fi/onto/stameta/");
		sailytettavienExactMatchienNimiavaruudet.add("http://www.yso.fi/onto/hpmulti/");
		sailytettavienExactMatchienNimiavaruudet.add("http://www.yso.fi/onto/ttl/");
		
		resurssitJoillaOnTeroConcept.retainAll(resurssitJoillaOnYsoConcept);
		Property skosExactMatch = this.koko.createProperty(this.skosNs + "exactMatch");
		int i = 0;
		for (Resource subj:resurssitJoillaOnTeroConcept) {
			boolean poista = true;
			iter = this.koko.listStatements(subj, skosExactMatch, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				String objNs = ((Resource)(stmt.getObject())).getNameSpace();
				if (sailytettavienExactMatchienNimiavaruudet.contains(objNs)) poista = false;
			}
			if (poista) {
				i++;
				this.koko.remove(subj, RDF.type, teroConcept);
			}
		}
		System.out.println("Poistettu " + i + " ylim‰‰r‰ist‰ TEROConcept-tyyppim‰‰rityst‰.");
	}
	
	public void korjaaConceptSchemet() {
		Property inScheme = this.koko.createProperty(this.skosNs + "inScheme");
		
		// luo meta TODO
		//Resource kokoScheme = this.koko.createResource(this.kokoMetaNs + "ConceptScheme");
		Resource kokoScheme = this.koko.createResource(this.kokoNs);
		Resource kokoAggregateScheme = this.koko.createResource(this.kokoNs + "AggregateConceptScheme");
		
		Resource skosConceptScheme = this.koko.createResource(this.skosNs + "ConceptScheme");
		Property skosHasTopConcept = this.koko.createProperty(this.skosNs + "hasTopConcept");
				
		String dateString = new SimpleDateFormat("yyyy-MM-dd").format(Calendar.getInstance().getTime());
		
		this.koko.add(kokoScheme, RDF.type, skosConceptScheme);
		this.koko.add(kokoScheme, RDFS.label, this.koko.createLiteral("The Finnish Collaborative Holistic Ontology (KOKO)", "en"));
		this.koko.add(kokoScheme, RDFS.label, this.koko.createLiteral("KOKO-ontologia", "fi"));
		this.koko.add(kokoScheme, skosHasTopConcept, this.koko.createResource("http://www.yso.fi/onto/koko/p25994"));
		this.koko.add(kokoScheme, DC.date, dateString);
		
		this.koko.add(kokoAggregateScheme, RDF.type, skosConceptScheme);
		this.koko.add(kokoAggregateScheme, RDFS.label, this.koko.createLiteral("Aggregate Concepts of KOKO", "en"));
		this.koko.add(kokoAggregateScheme, RDFS.label, this.koko.createLiteral("KOKO-ontologian koostek‰sitteet", "fi"));
		this.koko.add(kokoAggregateScheme, DC.date, dateString);
		
		// muuta inSchemet
		Vector<Statement> lisattavat = new Vector<Statement>();
		Vector<Statement> poistettavat = new Vector<Statement>();
		
		ResIterator resIter = this.koko.listSubjects();
		while (resIter.hasNext()) {
			Resource subj = resIter.nextResource();
			boolean onAggregateScheme = false;
			StmtIterator iter = this.koko.listStatements(subj, inScheme, (RDFNode)null); 
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				Resource obj = (Resource)(stmt.getObject());
				if (obj.getURI().contains("aggregate")) onAggregateScheme = true;
				poistettavat.add(stmt);
			}
			if (onAggregateScheme) {
				lisattavat.add(this.koko.createStatement(subj, inScheme, kokoAggregateScheme));
				lisattavat.add(this.koko.createStatement(kokoAggregateScheme, skosHasTopConcept, subj));
			} else {
				lisattavat.add(this.koko.createStatement(subj, inScheme, kokoScheme));
			}
		}
		
		this.koko.remove(poistettavat);
		this.koko.add(lisattavat);
		this.koko.remove(kokoScheme, inScheme, kokoScheme);
		this.koko.remove(kokoAggregateScheme, inScheme, kokoScheme);
	}
	
	public void hautaaVanhentuneetKasitteet(String vanhanKokonPolku) {
		this.luoHautausmaaMeta();
		HashSet<Resource> nykyKokonResurssit = new HashSet<Resource>();
		ResIterator resIter = this.koko.listSubjects();
		while (resIter.hasNext()) {
			nykyKokonResurssit.add(resIter.nextResource());
		}
		
		OntModel vanhaKoko = this.lueMalli(vanhanKokonPolku);
		
	}
	
	public void luoHautausmaaMeta() {
		
	}
	
	public OntModel lueMalli(String polku) {
		OntModel malli = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
		InputStream in = FileManager.get().open(polku);
		if (in == null) {
			throw new IllegalArgumentException("File: " + polku + " not found");
		}
		if (polku.endsWith("ttl")) {
			malli.read(in, "", "TTL");
		} else {
			malli.read(in, "");
		}
		try {
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return malli;
	}

	public void kirjoitaMalli(String kokonPolku) {
		try {
			FileOutputStream os = new FileOutputStream(kokonPolku);
			BufferedOutputStream bs = new BufferedOutputStream(os);
			RDFWriter kirjuri = this.koko.getWriter("TTL");
			kirjuri.setProperty("showXmlDeclaration", true);
			//kirjuri.setProperty("xmlbase", "http://yso.fi/mao");

			kirjuri.write(this.koko, bs, null);
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("KOKO kirjoitettu tiedostoon " + kokonPolku);
	}

	public void populoiHashMapVanhanKokonPohjalta(String vanhanKokonPolku) {
		this.vanhaUriKokoUriMap = new HashMap<Resource, Resource>();
		OntModel vanhaKoko = this.lueMalli(vanhanKokonPolku);

		//Property skosExactMatch = vanhaKoko.createProperty(this.skosNs + "exactMatch");
		//StmtIterator iter = vanhaKoko.listStatements((Resource)null, skosExactMatch, (RDFNode)null);
		StmtIterator iter = vanhaKoko.listStatements((Resource)null, OWL.equivalentClass, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource vanhaRes = (Resource)(stmt.getObject());
			Resource kokoRes = stmt.getSubject();
			this.vanhaUriKokoUriMap.put(vanhaRes, kokoRes);
		}
	} 

	public void tulostaViimeisinKokoUrinNumeroVanhastaKokosta(String vanhanKokonPolku) {
		OntModel vanhaKoko = this.lueMalli(vanhanKokonPolku);
		ResIterator resIter = vanhaKoko.listSubjects();
		int isoin = 0;
		while (resIter.hasNext()) {
			Resource subj = resIter.nextResource();
			if (subj.isURIResource()) {
				if (subj.getNameSpace().equals(this.kokoNs)) {
					int uriNro = Integer.parseInt(subj.getLocalName().substring(1));
					if (uriNro > isoin) isoin = uriNro;
				}
			}
		}
		System.out.println("Suurin URI-numero on: " + isoin);
	}

	public void kirjoitaUriVastaavuusMap(String tiedostonPolku) {
		try {
			FileWriter fstream = new FileWriter(tiedostonPolku);
			BufferedWriter out = new BufferedWriter(fstream);
			for (Resource vanhaUriRes:this.vanhaUriKokoUriMap.keySet()) {
				String vanhaUriString = vanhaUriRes.getURI();
				String kokoUriString = this.vanhaUriKokoUriMap.get(vanhaUriRes).getURI();
				out.write(vanhaUriString + " " + kokoUriString + "\n");
			}
			out.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		System.out.println("Uudet KOKO-URI-vastaavuudet kirjoitettu tiedostoon " + tiedostonPolku);
	}

	public static void main(String[] args) {
		/*
		 * args[0] = vanhatUrit-KokoUrit-vastaavuudettiedosto
		 * args[1] = kokon osaontologioiden polut
		 * args[2] = uusi vanhatUrit-KokoUrit-vastaavuudettiedosto
		 * args[3] = uusi KOKO
		 * args[4] = vanha KOKO hautuumaata varten
		 */

		KOKOaja kokoaja = new KOKOaja();
		kokoaja.lueUriVastaavuudetTiedostosta(args[0]);
		kokoaja.kokoa(args[1]);
		//kokoaja.hautaaVanhentuneetKasitteet(args[4]);
		kokoaja.kirjoitaUriVastaavuusMap(args[2]);
		kokoaja.kirjoitaMalli(args[3]);

		/***************************************************/
		// Ensikaynnistys, ei tarvitse toivottavasti toistaa:
		/*
		KOKOaja kok = new KOKOaja();
		kok.tulostaViimeisinKokoUrinNumeroVanhastaKokosta("C:/Users/mfroster/Desktop/Eclips~1/matskua/koko/koko-vanha-PURIFIED-YSO-PURIFIED.rdf");
		kok.populoiHashMapVanhanKokonPohjalta("C:/Users/mfroster/Desktop/Eclips~1/matskua/koko/koko-vanha-PURIFIED-YSO-PURIFIED.rdf");
		kok.kirjoitaUriVastaavuusMap("C:/Users/mfroster/Desktop/Eclips~1/matskua/koko/kokoUriVastaavuudet.txt");
		 */
	}

}
