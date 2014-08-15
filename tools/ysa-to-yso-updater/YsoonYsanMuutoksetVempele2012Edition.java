package ysoPaivitys;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.OntModelSpec;
import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.RDFWriter;
import com.hp.hpl.jena.rdf.model.ResIterator;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.util.FileManager;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;
import common.JenaHelpers;

public class YsoonYsanMuutoksetVempele2012Edition {

	private final String skosNS = "http://www.w3.org/2004/02/skos/core#";
	private final String ysoNs = "http://www.yso.fi/onto/yso/";
	private final String kehitysNs = "http://www.yso.fi/onto/yso-kehitys/";
	private final String peilausNs = "http://www.yso.fi/onto/yso-peilaus/2007-03-02/";
	private final String ysoMetaNs = "http://www.yso.fi/onto/yso-meta/2007-03-02/";
	private final String ysaMetaNs = "http://www.yso.fi/onto/ysa-meta/";

	private Model vanhaYsa;
	private Model uusiYsa;
	private Model yso;

	private HashMap<Resource, Resource> ysaYsoVastaavuudetMap;
	private HashMap<Resource, Resource> ysoYsaVastaavuudetMap;
	private HashMap<Property, Property> ysaYsoPropertyVastaavuudetMap;

	private HashSet<Resource> uudet;
	private HashSet<Resource> poistuneet;

	private HashMap<Resource, Resource> ysaYsoUudetKasitteetMap;
	private HashMap<Resource, String> suomiLabelitRaportointiaVartenMap;
	
	private int ongelmalaskuri;

	public YsoonYsanMuutoksetVempele2012Edition(String vanhanYsanPolku, String uudenYsanPolku, String ysonPolku) {
		this.vanhaYsa = JenaHelpers.lueMalliModeliksi(vanhanYsanPolku);
		this.uusiYsa = JenaHelpers.lueMalliModeliksi(uudenYsanPolku);
		this.yso = JenaHelpers.lueMalliModeliksi(ysonPolku);
		
		this.poistaMaantieteellisetKasitteet(true);
		this.poistaMaantieteellisetKasitteet(false);

		this.taytaYsaYsoPropertyVastaavuudet();

		this.uudet = new HashSet<Resource>();
		this.poistuneet = new HashSet<Resource>();
		
		this.ysaYsoUudetKasitteetMap = new HashMap<Resource, Resource>();

		this.ongelmalaskuri = 0;
		
		this.suomiLabelitRaportointiaVartenMap = new HashMap<Resource, String>();
		this.taytaLabelMap();
	}

	public OntModel lueMalli(String polku) {
		OntModel malli = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
		InputStream in = FileManager.get().open(polku);
		if (in == null) {
			throw new IllegalArgumentException("File: " + polku + " not found");
		}
		malli.read(in, "");

		try {
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return malli;
	}

	private void taytaYsaYsoPropertyVastaavuudet() {
		this.ysaYsoPropertyVastaavuudetMap = new HashMap<Property, Property>();
		this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(this.skosNS + "prefLabel"), this.yso.createProperty(this.ysoMetaNs + "prefLabel"));
		this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(this.skosNS + "altLabel"), this.yso.createProperty(this.ysoMetaNs + "oldLabel"));
		this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(this.skosNS + "exactMatch"), this.yso.createProperty(this.peilausNs + "definedConcept"));
		this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(this.skosNS + "broader"), RDFS.subClassOf);
		this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(this.skosNS + "related"), this.yso.createProperty(this.ysoMetaNs + "associativeRelation"));
		this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(this.skosNS + "note"), this.yso.createProperty(ysoMetaNs + "ysaComment"));
		//this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(this.ysaMetaNs + "hiddenNote"), this.yso.createProperty());
		this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(this.ysaMetaNs + "source"), this.yso.createProperty(ysoMetaNs + "ysaSource"));
		//this.ysaYsoPropertyVastaavuudetMap.put(this.uusiYsa.createProperty(), this.yso.createProperty());
	}

	private void taytaLabelMap() {
		Property skosPrefLabel = this.uusiYsa.createProperty(this.skosNS + "prefLabel");
		StmtIterator iter = this.uusiYsa.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String label = ((Literal)stmt.getObject()).getLexicalForm();
				this.suomiLabelitRaportointiaVartenMap.put(stmt.getSubject(), label);
			}
		}
		Property ysoPrefLabel = this.yso.createProperty(this.ysoMetaNs + "prefLabel");
		iter = this.yso.listStatements((Resource)null, ysoPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String label = ((Literal)stmt.getObject()).getLexicalForm();
				this.suomiLabelitRaportointiaVartenMap.put(stmt.getSubject(), label);
			}
		}
	}
	
	public String annaLabelResurssinPerusteella(Resource resurssi) {
		String label = "ei loytynyt labelia";
		if (this.suomiLabelitRaportointiaVartenMap.containsKey(resurssi)) {
			label = this.suomiLabelitRaportointiaVartenMap.get(resurssi);
		}
		return label;
	}
	
	public void poistaMaantieteellisetKasitteet(boolean uudestaEikaVanhastaYsasta) {
		Property skosHiddenNote = this.uusiYsa.createProperty(this.ysaMetaNs + "hiddenNote");
		HashSet<Resource> maantieteellisetKasitteet = new HashSet<Resource>();
		StmtIterator iter;
		if (uudestaEikaVanhastaYsasta) {
			iter = this.uusiYsa.listStatements((Resource)null, skosHiddenNote, (RDFNode)null);
		} else {
			iter = this.vanhaYsa.listStatements((Resource)null, skosHiddenNote, (RDFNode)null);
		}
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			String hiddenNoteString = ((Literal)(stmt.getObject())).getLexicalForm();
			if (hiddenNoteString.equals("151")) {
				maantieteellisetKasitteet.add(stmt.getSubject());
			}
		}
		HashSet<Statement> poistettavat = new HashSet<Statement>();
		for (Resource r:maantieteellisetKasitteet) {
			if (uudestaEikaVanhastaYsasta) {
				iter = this.uusiYsa.listStatements(r, (Property)null, (RDFNode)null);
				while (iter.hasNext()) {
					Statement stmt = iter.nextStatement();
					poistettavat.add(stmt);
				}
				iter = this.uusiYsa.listStatements((Resource)null, (Property)null, r);
				while (iter.hasNext()) {
					Statement stmt = iter.nextStatement();
					poistettavat.add(stmt);
				}
			} else {
				iter = this.vanhaYsa.listStatements(r, (Property)null, (RDFNode)null);
				while (iter.hasNext()) {
					Statement stmt = iter.nextStatement();
					poistettavat.add(stmt);
				}
				iter = this.vanhaYsa.listStatements((Resource)null, (Property)null, r);
				while (iter.hasNext()) {
					Statement stmt = iter.nextStatement();
					poistettavat.add(stmt);
				}
			}
		}
		for (Statement s:poistettavat) {
			if (uudestaEikaVanhastaYsasta) {
				this.uusiYsa.remove(s);
			} else {
				this.vanhaYsa.remove(s);
			}
		}
	}
	
	public void siivoaYsonKehitysYlaluokatDummyjenPerusteella() {
		Resource uudet = this.yso.createResource(this.kehitysNs + "uudet");
		Resource uudetDummy = this.yso.createResource(this.kehitysNs + "uudetDummy");

		Resource muuttuneet = this.yso.createResource(this.kehitysNs + "muuttuneet");
		Resource muuttuneetDummy = this.yso.createResource(this.kehitysNs + "muuttuneetDummy");

		Resource vanhentuneet = this.yso.createResource(this.kehitysNs + "vanhentuneet");
		Resource vanhentuneetDummy = this.yso.createResource(this.kehitysNs + "vanhentuneetDummy");

		HashSet<Resource> setti = new HashSet<Resource>();
		HashSet<Resource> dummySetti = new HashSet<Resource>();
		Resource ylaluokka = uudet;
		Resource dummyYlaluokka = uudetDummy;
		StmtIterator iter = this.yso.listStatements((Resource) null, RDFS.subClassOf, ylaluokka);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			setti.add(stmt.getSubject());
		}
		iter = this.yso.listStatements((Resource) null, RDFS.subClassOf, dummyYlaluokka);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			dummySetti.add(stmt.getSubject());
		}
		for (Resource r:setti) {
			if (!dummySetti.contains(r)) {
				this.yso.remove(this.yso.createStatement(r, RDFS.subClassOf, ylaluokka));
			}
		}

		setti = new HashSet<Resource>();
		dummySetti = new HashSet<Resource>();
		ylaluokka = muuttuneet;
		dummyYlaluokka = muuttuneetDummy;
		iter = this.yso.listStatements((Resource) null, RDFS.subClassOf, ylaluokka);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			setti.add(stmt.getSubject());
		}
		iter = this.yso.listStatements((Resource) null, RDFS.subClassOf, dummyYlaluokka);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			dummySetti.add(stmt.getSubject());
		}
		for (Resource r:setti) {
			if (!dummySetti.contains(r)) {
				this.yso.remove(this.yso.createStatement(r, RDFS.subClassOf, ylaluokka));
			}
		}

		setti = new HashSet<Resource>();
		dummySetti = new HashSet<Resource>();
		ylaluokka = vanhentuneet;
		dummyYlaluokka = vanhentuneetDummy;
		iter = this.yso.listStatements((Resource) null, RDFS.subClassOf, ylaluokka);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			setti.add(stmt.getSubject());
		}
		iter = this.yso.listStatements((Resource) null, RDFS.subClassOf, dummyYlaluokka);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			dummySetti.add(stmt.getSubject());
		}
		for (Resource r:setti) {
			if (!dummySetti.contains(r)) {
				this.yso.remove(this.yso.createStatement(r, RDFS.subClassOf, ylaluokka));
			}
		}
	}

	public void taytaYsoYsaVastaavuudet() {
		this.ysaYsoVastaavuudetMap = new HashMap<Resource, Resource>();
		this.ysoYsaVastaavuudetMap = new HashMap<Resource, Resource>();

		Property definedConcept = this.yso.createProperty(this.peilausNs + "definedConcept");
		StmtIterator iter = this.yso.listStatements((Resource)null, definedConcept, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (((Resource)stmt.getObject()).getURI().contains("http://www.yso.fi/onto/ysa/")) {
				Resource ysaSubj = (Resource)(stmt.getObject());
				Resource ysoSubj = stmt.getSubject();
				this.ysaYsoVastaavuudetMap.put(ysaSubj, ysoSubj);
				this.ysoYsaVastaavuudetMap.put(ysoSubj, ysaSubj);
			}
		}
	}

	public void taytaYsaYsoVastaavuudetAllarsinMukaan() {
		// uusiYsa on nyt uusiAllars, koska hoidaLopuksiVielaRuotsi-metodi muuttaa sen
		this.ysaYsoVastaavuudetMap = new HashMap<Resource, Resource>();
		Property definedConcept = this.yso.createProperty(this.peilausNs + "definedConcept");
		StmtIterator iter = this.yso.listStatements((Resource)null, definedConcept, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource obj = (Resource)(stmt.getObject());
			if (obj.getURI().contains("allars")) {
				this.ysaYsoVastaavuudetMap.put(obj, stmt.getSubject());
			}
		}
		/*
		HashMap<Resource, Resource> ysaAllarsVastaavuudetMap = new HashMap<Resource, Resource>();
		
		Property skosExactMatch = this.uusiYsa.createProperty(this.skosNS + "exactMatch");
		StmtIterator iter = this.yso.listStatements((Resource)null, skosExactMatch, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			ysaAllarsVastaavuudetMap.put((Resource)(stmt.getObject()), stmt.getSubject());
		}
		HashSet<Resource> nykkelisetti = new HashSet<Resource>(this.ysaYsoVastaavuudetMap.keySet());
		for (Resource ysaSubj:nykkelisetti) {
			if (ysaAllarsVastaavuudetMap.containsKey(ysaSubj)) {
				this.ysaYsoVastaavuudetMap.put(ysaSubj, ysaAllarsVastaavuudetMap.get(ysaSubj));
			} else {
				this.ysaYsoVastaavuudetMap.remove(ysaSubj);
			}
		}*/
	}
	
	public void etsiUudetJaPoistuneet() {
		HashSet<Resource> vanhanYsanSubjektit = new HashSet<Resource>();
		ResIterator resIter = this.vanhaYsa.listSubjects();
		while (resIter.hasNext()) {
			vanhanYsanSubjektit.add(resIter.nextResource());
		}
		HashSet<Resource> uudenYsanSubjektit = new HashSet<Resource>();
		resIter = this.uusiYsa.listSubjects();
		while (resIter.hasNext()) {
			uudenYsanSubjektit.add(resIter.nextResource());
		}

		for (Resource uudesta:uudenYsanSubjektit) {
			if (!vanhanYsanSubjektit.contains(uudesta)) {
				this.uudet.add(uudesta);
			}
		}

		// Täydennetään ysaYsoVastaavuudetMapit
		for (Resource uusi:this.uudet) {
			Resource subj = this.yso.createResource(this.ysoNs + uusi.getLocalName());
			this.ysaYsoVastaavuudetMap.put(uusi, subj);
			this.ysoYsaVastaavuudetMap.put(subj, uusi);
		}
		// Luodaan uudet käsitteet Ysoon
		for (Resource uusi:this.uudet) {
			Resource subj = this.yso.createResource(this.ysoNs + uusi.getLocalName());
			this.luoUusiKasiteYsoon(uusi, subj);
		}

		// Laitetaan poistuneet käsittelylistalle
		for (Resource vanhasta:vanhanYsanSubjektit) {
			if (!uudenYsanSubjektit.contains(vanhasta)) {
				this.poistuneet.add(vanhasta);
			}
		}

		Resource vanhentuneet = this.yso.createResource(this.kehitysNs + "vanhentuneet");
		Resource vanhentuneetDummy = this.yso.createResource(this.kehitysNs + "vanhentuneetDummy");
		for (Resource ysaSubj:this.poistuneet) {
			if (this.ysaYsoVastaavuudetMap.containsKey(ysaSubj)) {
				Resource ysoSubj = ysaYsoVastaavuudetMap.get(ysaSubj);
				this.yso.add(ysoSubj, RDFS.subClassOf, vanhentuneet);
				this.yso.add(ysoSubj, RDFS.subClassOf, vanhentuneetDummy);
			} else {
				this.ongelmalaskuri++;
				System.out.println(this.ongelmalaskuri + ". Ongelma: Ysosta ei löytynyt Ysasta poistunutta käsitettä " + ysaSubj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaSubj) + ")");
			}
		}
	}

	public void luoUusiKasiteYsoon(Resource ysaSubjekti, Resource ysoSubjekti) {
		HashSet<Property> sivuutettavatPropertyt = new HashSet<Property>();
		sivuutettavatPropertyt.add(this.uusiYsa.createProperty(this.skosNS + "inScheme"));
		sivuutettavatPropertyt.add(this.uusiYsa.createProperty(this.ysaMetaNs + "hiddenNote"));

		Property skosNarrower = this.uusiYsa.createProperty(this.skosNS + "narrower");
		Property skosExactMatch = this.uusiYsa.createProperty(this.skosNS + "exactMatch");
		Property definedConcept = this.yso.createProperty(this.peilausNs + "definedConcept");

		Resource uudet = this.yso.createResource(this.kehitysNs + "uudet");
		Resource uudetDummy = this.yso.createResource(this.kehitysNs + "uudetDummy");
		StmtIterator iter = this.uusiYsa.listStatements(ysaSubjekti, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getPredicate().equals(RDF.type)) {
				Resource ysoConcept = this.yso.createResource(this.ysoMetaNs + "Concept");
				this.yso.add(ysoSubjekti, RDF.type, ysoConcept);
				this.yso.add(ysoSubjekti, definedConcept, ysaSubjekti);
				this.yso.add(ysoSubjekti, RDFS.subClassOf, uudet);
				this.yso.add(ysoSubjekti, RDFS.subClassOf, uudetDummy);
				this.ysaYsoUudetKasitteetMap.put(ysaSubjekti, ysoSubjekti);
			} else if (stmt.getObject().isURIResource()) {
				if (stmt.getPredicate().equals(skosExactMatch)) {
					this.yso.add(ysoSubjekti, definedConcept, stmt.getObject());
				} else {
					Resource obj = (Resource)stmt.getObject();
					if (this.ysaYsoVastaavuudetMap.containsKey(obj)) {
						if (this.ysaYsoPropertyVastaavuudetMap.containsKey(stmt.getPredicate())) {
							Property pred = this.ysaYsoPropertyVastaavuudetMap.get(stmt.getPredicate());
							Resource ysoObj = this.ysaYsoVastaavuudetMap.get(obj);
							this.yso.add(ysoSubjekti, pred, ysoObj);
						} else if (stmt.getPredicate().equals(skosNarrower)) {
							Resource ysoObj = this.ysaYsoVastaavuudetMap.get(obj);
							this.yso.add(ysoObj, RDFS.subClassOf, ysoSubjekti);
						} else if (!sivuutettavatPropertyt.contains(stmt.getPredicate())) {
							this.ongelmalaskuri++;
							System.out.println(this.ongelmalaskuri + ". Ongelma: Ei löytynyt vastaavuutta YSAn propertylle " + stmt.getPredicate().getURI());
						}
					} else {
						this.ongelmalaskuri++;
						System.out.println(this.ongelmalaskuri + ". Ongelma: Uuden käsitteen suhteelle ei löytynyt objektia (" + ysaSubjekti.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaSubjekti) + ") " + stmt.getPredicate().getURI() + " " + obj.getURI() + " (" + this.annaLabelResurssinPerusteella(obj) + ")");
					}
				}
			} else { //objekti on literaali
				if (this.ysaYsoPropertyVastaavuudetMap.containsKey(stmt.getPredicate())) {
					Property pred = this.ysaYsoPropertyVastaavuudetMap.get(stmt.getPredicate());
					this.yso.add(ysoSubjekti, pred, stmt.getObject());
				} else if (!sivuutettavatPropertyt.contains(stmt.getPredicate())) {
					this.ongelmalaskuri++;
					System.out.println(this.ongelmalaskuri + ". Ongelma: Ei löytynyt vastaavuutta YSAn propertylle " + stmt.getPredicate().getURI());
				}
			}
		}
	}

	public void etsiMuuttuneet() {
		// associativeRelation-muutokset
		Property skosRelated = this.uusiYsa.createProperty(this.skosNS + "related");
		Property uusiAssociativeRelation = this.yso.createProperty(this.kehitysNs + "uusiAssociativeRelation");
		Property poistunutAssociativeRelation = this.yso.createProperty(this.kehitysNs + "poistunutAssociativeRelation");

		this.kirjoitaMuuttuneet(skosRelated, uusiAssociativeRelation, true);
		this.kirjoitaMuuttuneet(skosRelated, poistunutAssociativeRelation, false);

		// subClassOf-muutokset
		Property skosBroader = this.uusiYsa.createProperty(this.skosNS + "broader");
		Property uusiSubClassOfSuhde = this.yso.createProperty(this.kehitysNs + "uusiSubClassOfSuhde");
		Property poistunutSubClassOfSuhde = this.yso.createProperty(this.kehitysNs + "poistunutSubClassOfSuhde");

		this.kirjoitaMuuttuneet(skosBroader, uusiSubClassOfSuhde, true);
		this.kirjoitaMuuttuneet(skosBroader, poistunutSubClassOfSuhde, false);

		Property skosNarrower = this.uusiYsa.createProperty(this.skosNS + "narrower");
		this.kirjoitaMuuttuneetNarrowerSuhteet(skosNarrower);

		// label-muutokset
		Property skosPrefLabel = this.uusiYsa.createProperty(this.skosNS + "prefLabel");
		Property uusiPrefLabel = this.yso.createProperty(this.kehitysNs + "uusiPrefLabel");
		Property poistunutPrefLabel = this.yso.createProperty(this.kehitysNs + "poistunutPrefLabel");
		this.kirjoitaMuuttuneetDatatypePropertyt(skosPrefLabel, uusiPrefLabel, "fi", true);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosPrefLabel, uusiPrefLabel, "sv", true);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosPrefLabel, uusiPrefLabel, "en", true);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosPrefLabel, poistunutPrefLabel, "fi", false);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosPrefLabel, poistunutPrefLabel, "sv", false);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosPrefLabel, poistunutPrefLabel, "en", false);

		Property skosAltLabel = this.uusiYsa.createProperty(this.skosNS + "altLabel");
		Property uusiOldLabel = this.yso.createProperty(this.kehitysNs + "uusiOldLabel");
		Property poistunutOldLabel = this.yso.createProperty(this.kehitysNs + "poistunutOldLabel");
		this.kirjoitaMuuttuneetDatatypePropertyt(skosAltLabel, uusiOldLabel, "fi", true);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosAltLabel, uusiOldLabel, "sv", true);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosAltLabel, uusiOldLabel, "en", true);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosAltLabel, poistunutOldLabel, "fi", false);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosAltLabel, poistunutOldLabel, "sv", false);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosAltLabel, poistunutOldLabel, "en", false);
	}

	private void kirjoitaMuuttuneetNarrowerSuhteet(Property skosNarrower) {
		Resource muuttuneet = this.yso.createResource(this.kehitysNs + "muuttuneet");
		Resource muuttuneetDummy = this.yso.createResource(this.kehitysNs + "muuttuneetDummy");

		Property uusiSubClassOfSuhde = this.yso.createProperty(this.kehitysNs + "uusiSubClassOfSuhde");
		Property poistunutSubClassOfSuhde = this.yso.createProperty(this.kehitysNs + "poistunutSubClassOfSuhde");

		HashMap<Resource, HashSet<Resource>> uudetSuhteet = this.haeUudetSuhteet(skosNarrower);
		if (uudetSuhteet.size() > 0) {
			for (Resource ysaSubj:uudetSuhteet.keySet()) {
				if (this.ysaYsoVastaavuudetMap.containsKey(ysaSubj)) {
					Resource ysoObj = this.ysaYsoVastaavuudetMap.get(ysaSubj);
					for (Resource ysaObj:uudetSuhteet.get(ysaSubj)) {
						if (this.ysaYsoVastaavuudetMap.containsKey(ysaObj)) {
							Resource ysoSubj = this.ysaYsoVastaavuudetMap.get(ysaObj);
							this.yso.add(ysoSubj, RDFS.subClassOf, muuttuneet);
							this.yso.add(ysoSubj, RDFS.subClassOf, muuttuneetDummy);
							this.yso.add(ysoSubj, uusiSubClassOfSuhde, ysoObj);
						} else {
							this.ongelmalaskuri++;
							System.out.println(this.ongelmalaskuri + ". Ongelma: -=" + ysaObj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaObj) + ") =- " + uusiSubClassOfSuhde.getURI() + " " + ysoObj.getURI() + " (" + annaLabelResurssinPerusteella(ysoObj) + ")");
						}
					}
				} else {
					this.ongelmalaskuri++;
					System.out.println(this.ongelmalaskuri + ". Ongelma: xyz " + uusiSubClassOfSuhde.getURI() + " -=" + ysaSubj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaSubj) + ")=-");
				}
			}
		}

		HashMap<Resource, HashSet<Resource>> poistuneetSuhteet = this.haeVanhentuneetSuhteet(skosNarrower);
		if (poistuneetSuhteet.size() > 0) {
			for (Resource ysaSubj:poistuneetSuhteet.keySet()) {
				if (this.ysaYsoVastaavuudetMap.containsKey(ysaSubj)) {
					Resource ysoObj = this.ysaYsoVastaavuudetMap.get(ysaSubj);
					for (Resource ysaObj:poistuneetSuhteet.get(ysaSubj)) {
						if (this.ysaYsoVastaavuudetMap.containsKey(ysaObj)) {
							Resource ysoSubj = this.ysaYsoVastaavuudetMap.get(ysaObj);
							this.yso.add(ysoSubj, RDFS.subClassOf, muuttuneet);
							this.yso.add(ysoSubj, RDFS.subClassOf, muuttuneetDummy);
							this.yso.add(ysoSubj, poistunutSubClassOfSuhde, ysoObj);
						} else {
							this.ongelmalaskuri++;
							System.out.println(this.ongelmalaskuri + ". Ongelma: -=" + ysaObj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaObj) + ")=- " + poistunutSubClassOfSuhde.getURI() + " " + ysoObj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysoObj) + ")");
						}
					}
				} else {
					this.ongelmalaskuri++;
					System.out.println(this.ongelmalaskuri + ". Ongelma: xyz " + poistunutSubClassOfSuhde.getURI() + " -=" + ysaSubj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaSubj) + ")=-");
				}
			}
		}
	}

	private void kirjoitaMuuttuneet(Property ysaSuhde, Property ysoSuhde, boolean lisatytEikaPoistuneet) {
		Resource muuttuneet = this.yso.createResource(this.kehitysNs + "muuttuneet");
		Resource muuttuneetDummy = this.yso.createResource(this.kehitysNs + "muuttuneetDummy");
		HashMap<Resource, HashSet<Resource>> muuttuneetSuhteet;
		if (lisatytEikaPoistuneet) {
			muuttuneetSuhteet = this.haeUudetSuhteet(ysaSuhde);
		} else {
			muuttuneetSuhteet = this.haeVanhentuneetSuhteet(ysaSuhde);
		}
		if (muuttuneetSuhteet.size() > 0) {
			for (Resource ysaSubj:muuttuneetSuhteet.keySet()) {
				if (this.ysaYsoVastaavuudetMap.containsKey(ysaSubj)) {
					Resource ysoSubj = this.ysaYsoVastaavuudetMap.get(ysaSubj);
					this.yso.add(ysoSubj, RDFS.subClassOf, muuttuneet);
					this.yso.add(ysoSubj, RDFS.subClassOf, muuttuneetDummy);
					for (Resource ysaObj:muuttuneetSuhteet.get(ysaSubj)) {
						if (this.ysaYsoVastaavuudetMap.containsKey(ysaObj)) {
							Resource ysoObj = this.ysaYsoVastaavuudetMap.get(ysaObj);
							this.yso.add(ysoSubj, ysoSuhde, ysoObj);
						} else {
							this.ongelmalaskuri++;
							System.out.println(this.ongelmalaskuri + ". Ongelma: -=" + ysaObj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaObj) + ")=- " + ysoSuhde.getURI() + " " + ysoSubj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysoSubj) + ")");
						}
					}
				} else {
					this.ongelmalaskuri++;
					System.out.println(this.ongelmalaskuri + ". Ongelma: xyz " + ysoSuhde.getURI() + " -=" + ysaSubj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaSubj) + ")=-");
				}
			}
		}
	}

	// Jos lang on null, niin käsitellään kaiken kieliset (mukaanlukien ne, joilla kielimäärettä ei ole)
	private void kirjoitaMuuttuneetDatatypePropertyt(Property ysaSuhde, Property ysoSuhde, String lang, boolean lisatytEikaPoistuneet) {
		Resource muuttuneet = this.yso.createResource(this.kehitysNs + "muuttuneet");
		Resource muuttuneetDummy = this.yso.createResource(this.kehitysNs + "muuttuneetDummy");
		HashMap<Resource, HashSet<String>> muuttuneetLabelit;
		if (lisatytEikaPoistuneet) {
			muuttuneetLabelit = this.haeUudetLabelit(ysaSuhde, lang);
		} else {
			muuttuneetLabelit = this.haeVanhentuneetLabelit(ysaSuhde, lang);
		}
		if (muuttuneetLabelit.size() > 0) {
			for (Resource ysaSubj:muuttuneetLabelit.keySet()) {
				if (this.ysaYsoVastaavuudetMap.containsKey(ysaSubj)) {
					Resource ysoSubj = this.ysaYsoVastaavuudetMap.get(ysaSubj);
					this.yso.add(ysoSubj, RDFS.subClassOf, muuttuneet);
					this.yso.add(ysoSubj, RDFS.subClassOf, muuttuneetDummy);
					for (String labelString:muuttuneetLabelit.get(ysaSubj)) {
						Literal ysoObjLiteral;
						if (lang != null) {
							ysoObjLiteral = this.yso.createLiteral(labelString, lang);
						} else {
							ysoObjLiteral = this.yso.createLiteral(labelString);
						}
						this.yso.add(ysoSubj, ysoSuhde, ysoObjLiteral);
					}
				} else {
					this.ongelmalaskuri++;
					System.out.println(this.ongelmalaskuri + ". Ongelma: -=" + ysaSubj.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaSubj) + ")=- " + ysoSuhde.getURI() + " (" + muuttuneetLabelit.get(ysaSubj).toString() + ")");
				}
			}
		}
	}

	public HashMap<Resource, HashSet<Resource>> haeUudetSuhteet(Property suhde) {
		return this.haeSuhteidenMuutokset(suhde, false);
	}

	public HashMap<Resource, HashSet<Resource>> haeVanhentuneetSuhteet(Property suhde) {
		return this.haeSuhteidenMuutokset(suhde, true);
	}

	private HashMap<Resource, HashSet<String>> haeUudetLabelit(Property suhde, String lang) {
		return this.haeLabeleidenMuutokset(suhde, lang, false);
	}

	private HashMap<Resource, HashSet<String>> haeVanhentuneetLabelit(Property suhde, String lang) {
		return this.haeLabeleidenMuutokset(suhde, lang, true);
	}

	private HashMap<Resource, HashSet<Resource>> haeSuhteidenMuutokset(Property suhde, boolean haetaanPoistuneetEikaUudetSuhteet) {
		HashMap<Resource, HashSet<Resource>> uudenSuhteet = new HashMap<Resource, HashSet<Resource>>();
		HashMap<Resource, HashSet<Resource>> vanhanSuhteet = new HashMap<Resource, HashSet<Resource>>();
		HashMap<Resource, HashSet<Resource>> erot = new HashMap<Resource, HashSet<Resource>>();

		StmtIterator iter = this.uusiYsa.listStatements((Resource)null, suhde, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			Resource obj = (Resource)(stmt.getObject());
			uudenSuhteet = this.lisaaResurssiResurssiSetMappiin(subj, obj, uudenSuhteet);
		}
		iter = this.vanhaYsa.listStatements((Resource)null, suhde, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			Resource obj = (Resource)(stmt.getObject());
			vanhanSuhteet = this.lisaaResurssiResurssiSetMappiin(subj, obj, uudenSuhteet);
		}
		if (!haetaanPoistuneetEikaUudetSuhteet) {
			for (Resource vanhaSubj:vanhanSuhteet.keySet()) {
				HashSet<Resource> vanhaObjSetti = vanhanSuhteet.get(vanhaSubj);
				if (uudenSuhteet.containsKey(vanhaSubj)) {
					HashSet<Resource> uusiObjSetti = uudenSuhteet.get(vanhaSubj);
					HashSet<Resource> eroSetti = uusiObjSetti;
					eroSetti.removeAll(vanhaObjSetti);
					if (eroSetti.size() > 0) erot.put(vanhaSubj, eroSetti);
				} // uusissa ei ollut vastaavaa subjektia, jos edellä oleva if ei laukea
			}
		} else { // haetaankin poistuneet suhteet
			for (Resource uusiSubj:uudenSuhteet.keySet()) {
				HashSet<Resource> uusiObjSetti = uudenSuhteet.get(uusiSubj);
				if (vanhanSuhteet.containsKey(uusiSubj)) {
					HashSet<Resource> vanhaObjSetti = vanhanSuhteet.get(uusiSubj);
					HashSet<Resource> eroSetti = vanhaObjSetti;
					eroSetti.removeAll(uusiObjSetti);
					if (eroSetti.size() > 0) erot.put(uusiSubj, eroSetti);
				}
			}
		}
		return erot;
	}

	private HashMap<Resource, HashSet<String>> haeLabeleidenMuutokset(Property suhde, String lang, boolean haetaanPoistuneetEikaUudetSuhteet) {
		HashMap<Resource, HashSet<String>> uudenLabelit = new HashMap<Resource, HashSet<String>>();
		HashMap<Resource, HashSet<String>> vanhanLabelit = new HashMap<Resource, HashSet<String>>();
		HashMap<Resource, HashSet<String>> erot = new HashMap<Resource, HashSet<String>>();

		StmtIterator iter = this.uusiYsa.listStatements((Resource)null, suhde, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (lang == null) {
				String r = ((Literal)(stmt.getObject())).getLexicalForm();
				uudenLabelit = this.lisaaResurssiResurssiStringSetMappiin(stmt.getSubject(), r, uudenLabelit);
			} else if (stmt.getLanguage().equals(lang)) {
				String r = ((Literal)(stmt.getObject())).getLexicalForm();
				uudenLabelit = this.lisaaResurssiResurssiStringSetMappiin(stmt.getSubject(), r, uudenLabelit);
			}
		}
		iter = this.vanhaYsa.listStatements((Resource)null, suhde, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (lang == null) {
				String r = ((Literal)(stmt.getObject())).getLexicalForm();
				uudenLabelit = this.lisaaResurssiResurssiStringSetMappiin(stmt.getSubject(), r, uudenLabelit);
			} else if (stmt.getLanguage().equals(lang)) {
				String r = ((Literal)(stmt.getObject())).getLexicalForm();
				vanhanLabelit = this.lisaaResurssiResurssiStringSetMappiin(stmt.getSubject(), r, vanhanLabelit);
			}
		}
		if (!haetaanPoistuneetEikaUudetSuhteet) {
			for (Resource vanhaSubj:vanhanLabelit.keySet()) {
				HashSet<String> vanhaLabelSetti = vanhanLabelit.get(vanhaSubj);
				if (uudenLabelit.containsKey(vanhaSubj)) {
					HashSet<String> uusiLabelSetti = uudenLabelit.get(vanhaSubj);
					HashSet<String> eroSetti = uusiLabelSetti;
					eroSetti.removeAll(vanhaLabelSetti);
					if (eroSetti.size() > 0) erot.put(vanhaSubj, eroSetti);
				} // uusissa ei ollut vastaavaa subjektia, jos edellä oleva if ei laukea
			}
		} else {
			for (Resource uusiSubj:uudenLabelit.keySet()) {
				HashSet<String> uusiLabelSetti = uudenLabelit.get(uusiSubj);
				if (vanhanLabelit.containsKey(uusiSubj)) {
					HashSet<String> vanhaLabelSetti = vanhanLabelit.get(uusiSubj);
					HashSet<String> eroSetti = vanhaLabelSetti;
					eroSetti.removeAll(uusiLabelSetti);
					if (eroSetti.size() > 0) erot.put(uusiSubj, eroSetti);
				}
			}
		}

		return erot;
	}

	private HashMap<Resource, HashSet<Resource>> lisaaResurssiResurssiSetMappiin (Resource key, Resource value, HashMap<Resource, HashSet<Resource>> map) {
		if (map.containsKey(key)) {
			map.get(key).add(value);
		} else {
			HashSet<Resource> setti = new HashSet<Resource>();
			setti.add(value);
			map.put(key, setti);
		}
		return map;
	}

	private HashMap<Resource, HashSet<String>> lisaaResurssiResurssiStringSetMappiin (Resource key, String value, HashMap<Resource, HashSet<String>> map) {
		if (map.containsKey(key)) {
			map.get(key).add(value);
		} else {
			HashSet<String> setti = new HashSet<String>();
			setti.add(value);
			map.put(key, setti);
		}
		return map;
	}

	public void hoidaLopuksiVielaRuotsi(String vanhanAllarsinPolku, String uudenAllarsinPolku) {
		//System.out.println("Hoidetaan ruotsi");
		this.vanhaYsa = this.lueMalli(vanhanAllarsinPolku);
		this.uusiYsa = this.lueMalli(uudenAllarsinPolku);
		this.taytaYsaYsoVastaavuudetAllarsinMukaan();
		
		Property skosPrefLabel = this.uusiYsa.createProperty(this.skosNS + "prefLabel");
		Property uusiPrefLabel = this.yso.createProperty(this.kehitysNs + "uusiPrefLabel");
		Property poistunutPrefLabel = this.yso.createProperty(this.kehitysNs + "poistunutPrefLabel");
		this.kirjoitaMuuttuneetDatatypePropertyt(skosPrefLabel, uusiPrefLabel, "sv", true);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosPrefLabel, poistunutPrefLabel, "sv", false);
		
		Property skosAltLabel = this.uusiYsa.createProperty(this.skosNS + "altLabel");
		Property uusiOldLabel = this.yso.createProperty(this.kehitysNs + "uusiOldLabel");
		Property poistunutOldLabel = this.yso.createProperty(this.kehitysNs + "poistunutOldLabel");
		this.kirjoitaMuuttuneetDatatypePropertyt(skosAltLabel, uusiOldLabel, "sv", true);
		this.kirjoitaMuuttuneetDatatypePropertyt(skosAltLabel, poistunutOldLabel, "sv", false);
		
		this.kirjoitaRuotsiLabelit();
		this.kirjoitaProtegeLabelit();
	}

	private void kirjoitaRuotsiLabelit() {
		// this.ysa on allars
		Property skosExactMatch = this.uusiYsa.createProperty(this.skosNS + "exactMatch");
		Property skosPrefLabel = this.uusiYsa.createProperty(this.skosNS + "prefLabel");
		Property ysoPrefLabel = this.yso.createProperty(this.ysoMetaNs + "prefLabel");
		
		HashMap<Resource, Resource> ysaAllarsUusienKasitteidenVastaavuudet = new HashMap<Resource, Resource>();
		StmtIterator iter = this.uusiYsa.listStatements((Resource)null, skosExactMatch, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			ysaAllarsUusienKasitteidenVastaavuudet.put((Resource)(stmt.getObject()), stmt.getSubject());
		}
		
		HashMap<Resource, String> allarsLabelMap = new HashMap<Resource, String>();
		iter = this.uusiYsa.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("sv")) {
				String labelString = ((Literal)(stmt.getObject())).getLexicalForm();
				allarsLabelMap.put(stmt.getSubject(), labelString);
			}
		}
		
		for (Resource ysaSubjekti:this.ysaYsoUudetKasitteetMap.keySet()) {
			Resource ysoSubjekti = this.ysaYsoUudetKasitteetMap.get(ysaSubjekti);
			if (ysaAllarsUusienKasitteidenVastaavuudet.containsKey(ysaSubjekti)) {
				Resource allarsSubjekti = ysaAllarsUusienKasitteidenVastaavuudet.get(ysaSubjekti);
				Literal svPrefLabelLiteral = this.yso.createLiteral(allarsLabelMap.get(allarsSubjekti), "sv");
				this.yso.add(ysoSubjekti, ysoPrefLabel, svPrefLabelLiteral);
			} else {
				this.ongelmalaskuri++;
				System.out.println(this.ongelmalaskuri + ". Ongelma: Ei löytynyt ruotsinkielistä prefLabelia uudelle käsitteelle " + ysaSubjekti.getURI() + " (" + this.annaLabelResurssinPerusteella(ysaSubjekti) + ") " + " == " + ysoSubjekti.getURI() + " (" + this.annaLabelResurssinPerusteella(ysoSubjekti) + ")");
			}
		}
	}
	
	public void kirjoitaProtegeLabelit() {
		Property ysoPrefLabel = this.yso.createProperty(this.ysoMetaNs + "prefLabel");
		Property protegeLabelFi = this.yso.createProperty(this.kehitysNs + "protegeLabelFi");
		Property protegeLabelSv = this.yso.createProperty(this.kehitysNs + "protegeLabelSv");
		
		HashMap<Resource, String> ysoLabelMapFi = new HashMap<Resource, String>();
		HashMap<Resource, String> ysoLabelMapSv = new HashMap<Resource, String>();
		StmtIterator iter = this.yso.listStatements((Resource)null, ysoPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String labelString = ((Literal)(stmt.getObject())).getLexicalForm();
				ysoLabelMapFi.put(stmt.getSubject(), labelString);
			} else if (stmt.getLanguage().equals("sv")) {
				String labelString = ((Literal)(stmt.getObject())).getLexicalForm();
				ysoLabelMapSv.put(stmt.getSubject(), labelString);
			}
		}
		
		for (Resource ysaSubjekti:this.ysaYsoUudetKasitteetMap.keySet()) {
			Resource ysoSubjekti = this.ysaYsoUudetKasitteetMap.get(ysaSubjekti);
			if (ysoLabelMapFi.containsKey(ysoSubjekti)) {
				Literal fiLabelLiteral = this.yso.createLiteral(ysoLabelMapFi.get(ysoSubjekti));
				this.yso.add(ysoSubjekti, protegeLabelFi, fiLabelLiteral);
			} else {
				this.ongelmalaskuri++;
				System.out.println(this.ongelmalaskuri + ". Ongelma: Uudella käsitteellä ei ole suomenkielistä prefLabelia: " + ysoSubjekti.getURI() + " (" + this.annaLabelResurssinPerusteella(ysoSubjekti) + ")");
			}
			if (ysoLabelMapSv.containsKey(ysoSubjekti)) {
				Literal svLabelLiteral = this.yso.createLiteral(ysoLabelMapSv.get(ysoSubjekti));
				this.yso.add(ysoSubjekti, protegeLabelSv, svLabelLiteral);
			}/* else {
				this.ongelmalaskuri++;
				System.out.println(this.ongelmalaskuri + ". Ongelma: Uudella käsitteellä ei ole ruotsinkielistä prefLabelia: " + ysoSubjekti.getURI());
			}*/
		}
	}
	
	public void tulostaStatsit() {
		Resource uudet = this.yso.createResource(this.kehitysNs + "uudet");
		Resource muuttuneet = this.yso.createResource(this.kehitysNs + "muuttuneet");
		Resource vanhentuneet = this.yso.createResource(this.kehitysNs + "vanhentuneet");
		
		StmtIterator iter = this.yso.listStatements((Resource)null, RDFS.subClassOf, uudet);
		int maara = 0;
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			maara++;
		}
		System.out.println("Uusia käsitteitä: " + maara);
		
		iter = this.yso.listStatements((Resource)null, RDFS.subClassOf, vanhentuneet);
		maara = 0;
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			maara++;
		}
		System.out.println("Vanhentuneita käsitteitä: " + maara);
		
		iter = this.yso.listStatements((Resource)null, RDFS.subClassOf, muuttuneet);
		maara = 0;
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			maara++;
		}
		System.out.println("Muuttuneita käsitteitä: " + maara);
	}
	
	public void kirjoitaUusiYso(String uudenYsonPolku) {
		try {
			FileOutputStream os = new FileOutputStream(uudenYsonPolku);
			BufferedOutputStream bs = new BufferedOutputStream(os);
			RDFWriter kirjuri = this.yso.getWriter();
			kirjuri.setProperty("showXmlDeclaration", true);
			kirjuri.write(this.yso, bs, null);
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("päivitetty YSO kirjoitettu tiedostoon " + uudenYsonPolku);
	}

	public static void main(String[] args) {
		/*
		 * args:
		 * 0 = vanha YSA
		 * 1 = uusi YSA
		 * 2 = nykyinen YSO
		 * 3 = tuleva YSO
		 * 4 = vanha Allars
		 * 5 = uusi Allars
		 */
		YsoonYsanMuutoksetVempele2012Edition yymv2012e = new YsoonYsanMuutoksetVempele2012Edition(args[0], args[1], args[2]);
		yymv2012e.siivoaYsonKehitysYlaluokatDummyjenPerusteella();
		yymv2012e.taytaYsoYsaVastaavuudet();
		yymv2012e.etsiUudetJaPoistuneet();
		yymv2012e.etsiMuuttuneet();
		yymv2012e.hoidaLopuksiVielaRuotsi(args[4], args[5]);
		yymv2012e.tulostaStatsit();
		yymv2012e.kirjoitaUusiYso(args[3]);
	}

}