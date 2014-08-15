package ysoPaivitys;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Vector;

import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.UnionClass;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.RDFList;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.vocabulary.OWL;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;
import common.JenaHelpers;

public class YSODeprecator {

	private Model yso;
	private final String ysoNs = "http://www.yso.fi/onto/yso/";
	private final String ysoMetaNs = "http://www.yso.fi/onto/yso-meta/2007-03-02/";
	private long time;

	public YSODeprecator(String ysonPolku) {
		System.out.println("luetaan YSO sis‰‰n.");
		this.yso = JenaHelpers.lueMalliModeliksi(ysonPolku);
		System.out.println("YSO luettu sis‰‰n.");
	}

	private void luoMeta() {
		Resource deprecatedConcept = this.yso.createResource(this.ysoMetaNs + "DeprecatedConcept");
		// jos meta jo olemassa, break

		StmtIterator iter = this.yso.listStatements(deprecatedConcept, (Property)null, (RDFNode)null);
		if (!iter.hasNext()) {
			// ei ollut olemassa, tehd‰‰n luokat
			Resource deprecatedClass = this.yso.createResource(this.ysoMetaNs + "DeprecatedClass");
			this.yso.add(deprecatedClass, RDF.type, OWL.Class);
			this.yso.add(deprecatedClass, RDFS.subClassOf, OWL.DeprecatedClass);
			this.yso.add(deprecatedClass, RDFS.subClassOf, this.yso.createResource(this.ysoMetaNs + "Class"));
						
			this.yso.add(deprecatedConcept, RDF.type, OWL.Class);
			this.yso.add(deprecatedConcept, RDFS.subClassOf, deprecatedClass);
			this.yso.add(deprecatedConcept, RDFS.comment, this.yso.createLiteral("K‰ytˆst‰ poistettujen k‰sitteiden luokka"));
			
			Resource deprecatedAggregateConcept = this.yso.createResource(this.ysoMetaNs + "DeprecatedAggregateConcept");
			this.yso.add(deprecatedAggregateConcept, RDF.type, OWL.Class);
			this.yso.add(deprecatedAggregateConcept, RDFS.subClassOf, deprecatedClass);
			
			Resource deprecatedGroupConcept = this.yso.createResource(this.ysoMetaNs + "DeprecatedGroupConcept");
			this.yso.add(deprecatedGroupConcept, RDF.type, OWL.Class);
			this.yso.add(deprecatedGroupConcept, RDFS.subClassOf, deprecatedClass);
			
			Resource deprYlaluokka = this.yso.createResource(this.ysoMetaNs + "deprecatedConcepts");
			this.yso.add(deprYlaluokka, RDF.type, deprecatedGroupConcept);
			this.yso.add(deprecatedConcept, RDFS.comment, this.yso.createLiteral("K‰ytˆst‰ poistettujen k‰sitteiden yl‰luokka"));

			/*
			// tehd‰‰n propertyt		TODO
			Resource[] rarray = new Resource[2];
			rarray[0] = deprecatedClass;
			rarray[1] = this.yso.createResource(this.ysoMetaNs + "Class");
			RDFList lista = this.yso.createList(rarray);
			UnionClass ysoClassJaDeprClassUnioni = this.yso.createUnionClass(null, lista);
			
			Property deprHasPart = this.yso.createProperty(this.ysoMetaNs + "deprecatedHasPart");
			this.yso.add(deprHasPart, RDF.type, OWL.ObjectProperty);
			this.yso.add(deprHasPart, RDFS.domain, deprecatedClass);
			this.yso.add(deprHasPart, RDFS.range, ysoClassJaDeprClassUnioni);
			
			Property deprPartOf = this.yso.createProperty(this.ysoMetaNs + "deprecatedPartOf");
			this.yso.add(deprPartOf, RDF.type, OWL.ObjectProperty);
			this.yso.add(deprPartOf, RDFS.domain, deprecatedClass);
			this.yso.add(deprPartOf, RDFS.range, ysoClassJaDeprClassUnioni);
			
			Property deprSubClassOf = this.yso.createProperty(this.ysoMetaNs + "deprecatedSubClassOf");
			this.yso.add(deprSubClassOf, RDF.type, OWL.ObjectProperty);
			this.yso.add(deprSubClassOf, RDFS.domain, deprecatedClass);
			this.yso.add(deprSubClassOf, RDFS.range, ysoClassJaDeprClassUnioni);
						
			Property deprSuperClassOf = this.yso.createProperty(this.ysoMetaNs + "deprecatedSuperClassOf");
			this.yso.add(deprSuperClassOf, RDF.type, OWL.ObjectProperty);
			this.yso.add(deprSuperClassOf, RDFS.domain, deprecatedClass);
			this.yso.add(deprSuperClassOf, RDFS.range, ysoClassJaDeprClassUnioni);
			
			Property deprAssociativeRelation = this.yso.createProperty(this.ysoMetaNs + "deprecatedAssociativeRelation");
			this.yso.add(deprAssociativeRelation, RDF.type, OWL.ObjectProperty);
			this.yso.add(deprAssociativeRelation, RDFS.domain, deprecatedClass);
			this.yso.add(deprAssociativeRelation, RDFS.range, ysoClassJaDeprClassUnioni);
			
			Property deprReplacedBy = this.yso.createProperty(this.ysoMetaNs + "deprecatedReplacedBy");
			this.yso.add(deprReplacedBy, RDF.type, OWL.ObjectProperty);
			this.yso.add(deprReplacedBy, RDFS.domain, deprecatedClass);
			this.yso.add(deprReplacedBy, RDFS.range, ysoClassJaDeprClassUnioni);
			
			/*
			// Lis‰t‰‰n viel‰ prefLabelien sun muiden domaineihin deprecatedConcept
			Property prefLabel = this.yso.createProperty(this.ysoMetaNs + "prefLabel");
			iter = this.yso.listStatements(prefLabel, RDFS.domain, (RDFNode)null);
			this.lisaaUnioniin(deprecatedConcept, iter.nextStatement());
			
			Property altLabel = this.yso.createProperty(this.ysoMetaNs + "altLabel");
			iter = this.yso.listStatements(altLabel, RDFS.domain, (RDFNode)null);
			this.lisaaUnioniin(deprecatedConcept, iter.nextStatement());
			
			Property oldLabel = this.yso.createProperty(this.ysoMetaNs + "oldLabel");
			iter = this.yso.listStatements(oldLabel, RDFS.domain, (RDFNode)null);
			this.lisaaUnioniin(deprecatedConcept, iter.nextStatement());
			*/
		}
		System.out.println("Meta luotu.");
	}
	
	/*
	// unioninAloittavaStatement siis tarkoittaa lausetta, jonka objektina on anonyymi noodi, 
	//   jolla on puolestaan owl:unionOf property ja sen p‰‰ss‰ anonyyminoodi, joka aloittaa first-rest-ketjun
	public void lisaaUnioniin(Resource lisattava, Statement unioninAloittavaStatement) {
		Vector<Statement> poistettavat = new Vector<Statement>();
		Vector<Resource> koosteosat = new Vector<Resource>();
		
		StmtIterator iter = this.yso.listStatements((Resource)(unioninAloittavaStatement.getObject()), OWL.unionOf, (RDFNode)null);
		Statement stmt = iter.nextStatement();
		Resource anon = (Resource)stmt.getObject();
		poistettavat.add(stmt);
		boolean jatka = true;
		while (jatka) {
			iter = this.yso.listStatements(anon, (Property)null, (RDFNode)null);
			while (iter.hasNext()) poistettavat.add(iter.nextStatement());
			
			iter = this.yso.listStatements(anon, RDF.first, (RDFNode)null);
			koosteosat.add((Resource)iter.nextStatement().getObject());
			iter = this.yso.listStatements(anon, RDF.rest, (RDFNode)null);
			stmt = iter.nextStatement();
			if (stmt.getObject().isAnon()) anon = (Resource)stmt.getObject();
			else jatka = false;
		}
		
		for (Statement s:poistettavat) {
			this.yso.remove(s);
		}
		
		koosteosat.add(lisattava);
		
		if (koosteosat.size() < 2) System.out.println("ongelma");
		Resource[] rarray = new Resource[koosteosat.size()];
		int i = 0;
		for (Resource r:koosteosat) {
			rarray[i] = r;
			i++;
		}
		RDFList lista = this.yso.createList(rarray);
		UnionClass koosteunioni = this.yso.createUnionClass(null, lista);
		this.yso.add(this.yso.createStatement(unioninAloittavaStatement.getSubject(), unioninAloittavaStatement.getPredicate(), koosteunioni));
	}
	*/
	
	private void lueDeprUritTiedostosta(String tiedostonPolku, String deprPvm) {
		// HashMapin key on deprekoitava ja arvo korvaava (jos korvaavaa ei ole, niin null)
		HashMap<Resource, Resource> deprekoitavat = new HashMap<Resource, Resource>();
		try {
			FileReader fr = new FileReader(tiedostonPolku);
			BufferedReader br = new BufferedReader(fr);
			String rivi = br.readLine().trim();
			while (rivi != null) {
				rivi = rivi.trim();
				String[] urit = rivi.split(" ");
				Resource subj = this.yso.createResource(urit[0]);
				if (urit.length > 1) {
					Resource replacingRes = this.yso.createResource(urit[1]);
					deprekoitavat.put(subj, replacingRes);
				} else {
					deprekoitavat.put(subj, null);					
				}
				rivi = br.readLine();
			}
			br.close();
			fr.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		this.deprecateResources(deprekoitavat, deprPvm);
	}
	
	public void deprecateResources(HashMap<Resource, Resource> deprekoitavat, String deprPvm) {
		this.time = System.currentTimeMillis();
		for (Resource deprekoitava:deprekoitavat.keySet()) {
			if (deprekoitavat.get(deprekoitava) == null) {
				this.deprecateAResource(deprekoitava, deprPvm);
			} else {
				this.deprecateAResource(deprekoitava, deprekoitavat.get(deprekoitava), deprPvm);
			}
		}
	}
	
	public void deprecateAResource(Resource subj, Resource replacingRes, String deprPvm) {
		this.deprecateAResource(subj, deprPvm);
		
		Property deprReplacedBy = this.yso.createProperty(this.ysoMetaNs + "deprecatedReplacedBy");
		this.yso.add(this.yso.createStatement(subj, deprReplacedBy, replacingRes));
	}
	
	public void deprecateAResource(Resource subj, String deprPvm) {
		Vector<Statement> poistettavat = new Vector<Statement>();
		Vector<Statement> lisattavat = new Vector<Statement>();

		Resource deprecatedConcept = this.yso.createResource(this.ysoMetaNs + "DeprecatedConcept");
		Resource deprecatedAggregateConcept = this.yso.createResource(this.ysoMetaNs + "DeprecatedAggregateConcept");
		Resource deprecatedGroupConcept = this.yso.createResource(this.ysoMetaNs + "DeprecatedGroupConcept");
		
		StmtIterator iter = this.yso.listStatements(subj, RDF.type, (RDFNode)null);
		Resource tyyppi = this.yso.createResource("");
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			tyyppi = (Resource)(stmt.getObject());
			poistettavat.add(stmt);
		}
		long timeElapsed = System.currentTimeMillis() - time;
		System.out.println(timeElapsed + " " + subj.getURI() + " " + tyyppi.getURI());
		if (tyyppi.getURI().equals(this.ysoMetaNs + "Concept"))		
			lisattavat.add(this.yso.createStatement(subj, RDF.type, deprecatedConcept));
		else if (tyyppi.getURI().equals(this.ysoMetaNs + "AggregateConcept"))
			lisattavat.add(this.yso.createStatement(subj, RDF.type, deprecatedAggregateConcept));
		else if (tyyppi.getURI().equals(this.ysoMetaNs + "GroupConcept"))
			lisattavat.add(this.yso.createStatement(subj, RDF.type, deprecatedGroupConcept));
		else System.out.println("Ongelma: tyyppi " + tyyppi);
		
		Property comment = this.yso.createProperty(this.ysoMetaNs + "comment");
		lisattavat.add(this.yso.createStatement(subj, comment, this.yso.createLiteral("deprecated on " + deprPvm)));
		
		Resource deprYlaluokka = this.yso.createResource(this.ysoMetaNs + "deprecatedConcepts");
		lisattavat.add(this.yso.createStatement(subj, RDFS.subClassOf, deprYlaluokka));

		Property deprHasPart = this.yso.createProperty(this.ysoMetaNs + "deprecatedHasPart");
		Property deprPartOf = this.yso.createProperty(this.ysoMetaNs + "deprecatedPartOf");
		Property partOf = this.yso.createProperty(this.ysoMetaNs + "partOf");
		
		Property deprSubClassOf = this.yso.createProperty(this.ysoMetaNs + "deprecatedSubClassOf");
		Property deprSuperClassOf = this.yso.createProperty(this.ysoMetaNs + "deprecatedSuperClassOf");
		Property deprAssociativeRelation = this.yso.createProperty(this.ysoMetaNs + "deprecatedAssociativeRelation");
		Property associativeRelation = this.yso.createProperty(this.ysoMetaNs + "associativeRelation");
		
		timeElapsed = System.currentTimeMillis() - time;
		System.out.println(timeElapsed + " tutkitaan subjekti-statementit");
		iter = this.yso.listStatements(subj, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Property prop = stmt.getPredicate();
			if (prop.equals(partOf)) {
				poistettavat.add(stmt);
				Resource obj = (Resource)(stmt.getObject());
				lisattavat.add(this.yso.createStatement(subj, deprPartOf, obj));
			} else if (prop.equals(RDFS.subClassOf)) {
				poistettavat.add(stmt);
				Resource obj = (Resource)(stmt.getObject());
				lisattavat.add(this.yso.createStatement(subj, deprSubClassOf, obj));
			} else if (prop.equals(associativeRelation)) {
				poistettavat.add(stmt);
				Resource obj = (Resource)(stmt.getObject());
				lisattavat.add(this.yso.createStatement(subj, deprAssociativeRelation, obj));
			}
		}
		
		timeElapsed = System.currentTimeMillis() - time;
		System.out.println(timeElapsed + " tutkitaan objekti-statementit");
		iter = this.yso.listStatements((Resource)null, (Property)null, subj);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Property prop = stmt.getPredicate();
			if (prop.equals(partOf)) {
				poistettavat.add(stmt);
				Resource obj = stmt.getSubject();
				lisattavat.add(this.yso.createStatement(subj, deprHasPart, obj));
			} else if (prop.equals(RDFS.subClassOf)) {
				poistettavat.add(stmt);
				Resource obj = stmt.getSubject();
				lisattavat.add(this.yso.createStatement(subj, deprSuperClassOf, obj));
			} else if (prop.equals(associativeRelation)) {
				poistettavat.add(stmt);
				Resource obj = stmt.getSubject();
				lisattavat.add(this.yso.createStatement(subj, deprAssociativeRelation, obj));
			}
		}
		/*
		iter = this.yso.listStatements(subj, partOf, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			poistettavat.add(stmt);
			Resource obj = (Resource)(stmt.getObject());
			lisattavat.add(this.yso.createStatement(subj, deprPartOf, obj));
		}
		iter = this.yso.listStatements((Resource)null, partOf, subj);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			poistettavat.add(stmt);
			Resource obj = stmt.getSubject();
			lisattavat.add(this.yso.createStatement(subj, deprHasPart, obj));
		}

		Property deprSubClassOf = this.yso.createProperty(this.ysoMetaNs + "deprecatedSubClassOf");
		Property deprSuperClassOf = this.yso.createProperty(this.ysoMetaNs + "deprecatedSuperClassOf");
		iter = this.yso.listStatements(subj, RDFS.subClassOf, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			poistettavat.add(stmt);
			Resource obj = (Resource)(stmt.getObject());
			lisattavat.add(this.yso.createStatement(subj, deprSubClassOf, obj));
		}
		iter = this.yso.listStatements((Resource)null, RDFS.subClassOf, subj);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			poistettavat.add(stmt);
			Resource obj = stmt.getSubject();
			lisattavat.add(this.yso.createStatement(subj, deprSuperClassOf, obj));
		}

		Property deprAssociativeRelation = this.yso.createProperty(this.ysoMetaNs + "deprecatedAssociativeRelation");
		Property associativeRelation = this.yso.createProperty(this.ysoMetaNs + "associativeRelation");
		iter = this.yso.listStatements(subj, associativeRelation, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			poistettavat.add(stmt);
			Resource obj = (Resource)(stmt.getObject());
			lisattavat.add(this.yso.createStatement(subj, deprAssociativeRelation, obj));
		}
		iter = this.yso.listStatements((Resource)null, associativeRelation, subj);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			poistettavat.add(stmt);
			Resource obj = stmt.getSubject();
			lisattavat.add(this.yso.createStatement(subj, deprAssociativeRelation, obj));
		}*/
		timeElapsed = System.currentTimeMillis() - time;
		System.out.println(timeElapsed + " kirjataan muutokset");
		for (Statement s:poistettavat) {
			this.yso.remove(s);
		}
		for (Statement s:lisattavat) {
			this.yso.add(s);
		}
		timeElapsed = System.currentTimeMillis() - time;
		System.out.println(timeElapsed + " valmis");
	}

	public void deprekoi(String tiedostonPolku, String deprPvm) {
		this.luoMeta();
		this.lueDeprUritTiedostosta(tiedostonPolku, deprPvm);
	}
	
	public void kirjoitaYso(String uudenYsonPolku) {
		JenaHelpers.kirjoitaMalli(this.yso, uudenYsonPolku, true);
		//System.out.println("korjattu YSO kirjoitettu tiedostoon " + uudenYsonPolku);
	}
	
	public void kirjoitaDiff(String alkuperaisenYsonPolku, String diffinPolku) {
		Model alkupYso = JenaHelpers.lueMalli(alkuperaisenYsonPolku);
		JenaHelpers.kirjoitaMalli(this.yso.difference(alkupYso), diffinPolku, true);
	}
	
	public static void main(String[] args) {
		if (args.length != 5) {
			System.out.println("argumentit: [yso] [deprekoitavat] [p‰iv‰m‰‰r‰] [uusi yso] [diff]");
		} else {
			YSODeprecator depr = new YSODeprecator(args[0]);
			depr.deprekoi(args[1], args[2]);
			depr.kirjoitaYso(args[3]);
			depr.kirjoitaDiff(args[0], args[4]);
		}
	}
}
