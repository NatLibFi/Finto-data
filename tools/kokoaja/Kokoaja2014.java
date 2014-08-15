package koko;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Vector;

import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.ResIterator;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.vocabulary.DC;
import com.hp.hpl.jena.vocabulary.DCTerms;
import com.hp.hpl.jena.vocabulary.OWL;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;

import common.JenaHelpers;

public class Kokoaja2014 {

	private final String skosNs = "http://www.w3.org/2004/02/skos/core#";
	private final String skosextNs = "http://purl.org/finnonto/schema/skosext#";
	private final String kokoNs ="http://www.yso.fi/onto/koko/";
	private final String kokoMetaNs ="http://www.yso.fi/onto/koko-meta/";
	
	private Model koko;
	private Model onto;
	private Model sailotyt;
	
	private HashMap<Resource, String> ontologioidenTyypitPolutMap;
	private HashMap<String, Resource> kokoFiLabelitResurssitMap;
	private HashMap<Resource, String> ontoFiResurssitLabelitMap;
	private HashMap<Resource, Resource> ontoKokoResurssivastaavuudetMap;
	private HashMap<Resource, Resource> ontoKokoResurssivastaavuudetJotkaNykyKokossaMap;
	
	private HashSet<String> sallittujenPropertyjenNimiavaruudet;
	
	private int viimeisinKokoUrinLoppuosa;
	
	public Kokoaja2014(String uriVastaavuuksiePolku) {
		this.taytaSallittujenPropertyjenNimiavaruudet();
		this.koko = this.luoAihio();
		this.sailotyt = this.luoAihio();
		this.lueUriVastaavuudetTiedostosta(uriVastaavuuksiePolku);
		
		this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap = new HashMap<Resource, Resource>();
		this.kokoFiLabelitResurssitMap = new HashMap<String, Resource>();
	}
	
	public Model luoAihio() {
		Model aihio = ModelFactory.createDefaultModel();
		aihio.setNsPrefix("skos", this.skosNs);
		aihio.setNsPrefix("skosext", this.skosextNs);
		aihio.setNsPrefix("koko", this.kokoNs);
		aihio.setNsPrefix("koko-meta", this.kokoMetaNs);
		return aihio;
	}
	
	public void taytaSallittujenPropertyjenNimiavaruudet() {
		this.sallittujenPropertyjenNimiavaruudet = new HashSet<String>();
		this.sallittujenPropertyjenNimiavaruudet.add(this.skosNs);
		this.sallittujenPropertyjenNimiavaruudet.add(this.skosextNs);
		this.sallittujenPropertyjenNimiavaruudet.add(DC.getURI());
		this.sallittujenPropertyjenNimiavaruudet.add(OWL.getURI());
		this.sallittujenPropertyjenNimiavaruudet.add(RDF.getURI());
		this.sallittujenPropertyjenNimiavaruudet.add(RDFS.getURI());
		this.sallittujenPropertyjenNimiavaruudet.add(DCTerms.getURI());
		this.sallittujenPropertyjenNimiavaruudet.add("http://purl.org/iso25964/skos-thes#");
	}
	
	public void lueUriVastaavuudetTiedostosta(String polku) {
		System.out.println("Luetaan URI-vastaavuudet tiedostosta " + polku);
		int korkeinNro = 0;
		this.ontoKokoResurssivastaavuudetMap = new HashMap<Resource, Resource>();
		try {
			BufferedReader br = new BufferedReader( new InputStreamReader( new FileInputStream(polku), "UTF8" ) );
			String rivi = br.readLine().trim();
			while (rivi != null) {				
				rivi = rivi.trim();
				String[] uriTaulukko = rivi.split(" ");
				Resource ontoRes = this.koko.createResource(uriTaulukko[0].trim());
				Resource kokoRes = this.koko.createResource(uriTaulukko[1].trim());
				this.ontoKokoResurssivastaavuudetMap.put(ontoRes, kokoRes);
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
	
	public void lueYso(String ysonPolku) {
		this.onto = JenaHelpers.lueMalliModeliksi(ysonPolku); 
		Resource skosConcept = this.onto.createResource(this.skosNs + "Concept");
		
		// kaivetaan HashSettiin kaikki erikoisontologian oman tyyppiset kasitteet
		HashSet<Resource> ysonKasiteresurssit = this.haeTietynTyyppisetResurssit(this.onto, skosConcept);

		// kaivetaan HashMappiin kaikki YSOn fiLabelit
		// HUOM: eivat ole viela kokoResursseja vaan viela suoraan YSOsta
		Property skosPrefLabel = this.onto.createProperty(this.skosNs + "prefLabel");
		this.ontoFiResurssitLabelitMap = this.haeTietynTyyppistenResurssienLabelitMappiin(this.onto, skosPrefLabel, ysonKasiteresurssit, "fi");
		
		ResIterator resIter = this.onto.listResourcesWithProperty(RDF.type, skosConcept);
		while (resIter.hasNext()) {
			Resource ysoSubj = resIter.nextResource();
			Resource kokoSubj;
			if (this.ontoKokoResurssivastaavuudetMap.containsKey(ysoSubj)) {
				kokoSubj = this.ontoKokoResurssivastaavuudetMap.get(ysoSubj);
			} else {
				kokoSubj = this.luoUusiKokoResurssi();
			}
			this.lisaaResurssiKokoon(ysoSubj, kokoSubj);
		}
	}
	
	private HashSet<Resource> haeTietynTyyppisetResurssit(Model malli, Resource tyyppi) {
		HashSet<Resource> tietynTyyppisetResurssit = new HashSet<Resource>();
		StmtIterator iter = malli.listStatements((Resource)null, RDF.type, tyyppi);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			tietynTyyppisetResurssit.add(stmt.getSubject());
		}
		return tietynTyyppisetResurssit;
	}
	
	private HashMap<Resource, String> haeTietynTyyppistenResurssienLabelitMappiin(Model malli, Property labelProp, HashSet<Resource> tietynTyyppisetResurssit, String kieli) {
		HashMap<Resource, String> resurssitLabelitMap = new HashMap<Resource, String>();
		StmtIterator iter = malli.listStatements((Resource)null, labelProp, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals(kieli)) {
				Resource subj = stmt.getSubject();
				if (tietynTyyppisetResurssit.contains(subj)) {
					String labelString = ((Literal)(stmt.getObject())).getLexicalForm();
					resurssitLabelitMap.put(subj, labelString);
				}
			}
		}
		return resurssitLabelitMap;
	}
	
	private void lisaaResurssiKokoon(Resource ontoSubj, Resource kokoSubj) {
		this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.put(ontoSubj, kokoSubj);
		this.ontoKokoResurssivastaavuudetMap.put(ontoSubj, kokoSubj);
		this.kokoFiLabelitResurssitMap.put(this.ontoFiResurssitLabelitMap.get(ontoSubj), kokoSubj);
		Property skosExactMatch = this.onto.createProperty(this.skosNs + "exactMatch");
		this.koko.add(kokoSubj, skosExactMatch, ontoSubj);
		StmtIterator iter = this.onto.listStatements(ontoSubj, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (this.sallittujenPropertyjenNimiavaruudet.contains(stmt.getPredicate().getNameSpace()))
				this.koko.add(kokoSubj, stmt.getPredicate(), stmt.getObject());
		}
	}
	
	public void lueOnto(String ontonPolku, Resource ontoTyyppi) {
		System.out.println("Luetaan " + ontonPolku);
		this.onto = JenaHelpers.lueMalliModeliksi(ontonPolku);
		
		StmtIterator iter = this.onto.listStatements(ontoTyyppi, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			this.koko.add(stmt);
		}
		
		// kaivetaan HashSettiin kaikki erikoisontologian oman tyyppiset kasitteet
		HashSet<Resource> ontonOntoTyyppisetResurssit = this.haeTietynTyyppisetResurssit(this.onto, ontoTyyppi);
		System.out.println("Lisataan KOKOon " + ontonOntoTyyppisetResurssit.size() + " " + ontoTyyppi.getURI() + " -tyyppista resurssia.");
		
		// kaivetaan HashMappiin kaikki erikoisontologian suorat skos:exactMatchit
		HashMap<Resource, Resource> ontonExactMatchitMap = new HashMap<Resource, Resource>();
		Property skosExactMatch = this.onto.createProperty(this.skosNs + "exactMatch");
		iter = this.onto.listStatements((Resource)null, skosExactMatch, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			if (ontonOntoTyyppisetResurssit.contains(subj)) {
				ontonExactMatchitMap.put(subj, (Resource)(stmt.getObject()));
			}
		}
		
		// kaivetaan HashMappiin kaikki erikoisontologian fiLabelit
		// HUOM: eivat ole viela kokoResursseja vaan viela suoraan erikoisOntosta
		Property skosPrefLabel = this.onto.createProperty(this.skosNs + "prefLabel");
		this.ontoFiResurssitLabelitMap = this.haeTietynTyyppistenResurssienLabelitMappiin(this.onto, skosPrefLabel, ontonOntoTyyppisetResurssit, "fi");
		
		ResIterator resIter = this.onto.listResourcesWithProperty(RDF.type, ontoTyyppi);
		while (resIter.hasNext()) {
			Resource ontoSubj = resIter.nextResource();
			Resource kokoSubj = null;
			boolean potentiaalinenSailottava = false;
			
			// Tutkitaan mika on resurssa vastaava resurssi kokossa tai jos moista ei ole, paatetaan sailotaanko vai ei
			if (this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.containsKey(ontoSubj)) {
				kokoSubj = ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(ontoSubj);
			} else if (ontonExactMatchitMap.containsKey(ontoSubj)) {
				Resource exactMatchinKohde = ontonExactMatchitMap.get(ontoSubj);
				if (this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.containsKey(exactMatchinKohde)) {
					kokoSubj = this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(exactMatchinKohde);
				} else {
					potentiaalinenSailottava = true;
				}
			}
			if (kokoSubj == null && this.ontoFiResurssitLabelitMap.containsKey(ontoSubj)) {
				String ontoLabel = ontoFiResurssitLabelitMap.get(ontoSubj);
				if (this.kokoFiLabelitResurssitMap.containsKey(ontoLabel)) {
					kokoSubj = this.kokoFiLabelitResurssitMap.get(ontoLabel);
				}
			}
			
			// laitetaan kasite ja siihen liittyvat triplet KOKOon tai sailotaan ne
			if (kokoSubj != null) this.lisaaResurssiKokoon(ontoSubj, kokoSubj);
			else if (!potentiaalinenSailottava) {
				if (this.ontoKokoResurssivastaavuudetMap.containsKey(ontoSubj)) {
					kokoSubj = this.ontoKokoResurssivastaavuudetMap.get(ontoSubj);
				} else {
					kokoSubj = this.luoUusiKokoResurssi();
				}
				this.lisaaResurssiKokoon(ontoSubj, kokoSubj);
			}
			else this.sailoKasite(ontoSubj);
		}
	}
	
	public Resource luoUusiKokoResurssi() {
		this.viimeisinKokoUrinLoppuosa++;
		Resource uusiResurssi = this.koko.createResource(this.kokoNs + "p" + this.viimeisinKokoUrinLoppuosa);
		return uusiResurssi;
	}
	
	public void sailoKasite(Resource sailottavaSubj) {
		StmtIterator iter = this.onto.listStatements(sailottavaSubj, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			this.sailotyt.add(stmt);
		}
	}
	
	public void hoidaSailotyt() {
		HashSet<Resource> resurssitSet = new HashSet<Resource>();
		ResIterator resIter = this.sailotyt.listResourcesWithProperty(RDF.type);
		while (resIter.hasNext()) {
			Resource res = resIter.nextResource();
			resurssitSet.add(res);
		}
		
		HashMap<Resource, Resource> ontonExactMatchitMap = new HashMap<Resource, Resource>();
		Property skosExactMatch = this.onto.createProperty(this.skosNs + "exactMatch");
		StmtIterator iter = this.onto.listStatements((Resource)null, skosExactMatch, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			ontonExactMatchitMap.put(subj, (Resource)(stmt.getObject()));
		}
		
		Property skosPrefLabel = this.onto.createProperty(this.skosNs + "prefLabel");
		this.ontoFiResurssitLabelitMap = this.haeTietynTyyppistenResurssienLabelitMappiin(this.onto, skosPrefLabel, resurssitSet, "fi");
		
		for (Resource ontoSubj:resurssitSet) {
			Resource kokoSubj = null;

			// Tutkitaan mika on resurssia vastaava resurssi kokossa
			if (this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.containsKey(ontoSubj)) {
				kokoSubj = ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(ontoSubj);
			} else if (ontonExactMatchitMap.containsKey(ontoSubj)) {
				Resource exactMatchinKohde = ontonExactMatchitMap.get(ontoSubj);
				if (this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.containsKey(exactMatchinKohde)) {
					kokoSubj = this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(exactMatchinKohde);
				}
			}
			if (kokoSubj == null && this.ontoFiResurssitLabelitMap.containsKey(ontoSubj)) {
				String ontoLabel = ontoFiResurssitLabelitMap.get(ontoSubj);
				if (this.kokoFiLabelitResurssitMap.containsKey(ontoLabel)) {
					kokoSubj = this.kokoFiLabelitResurssitMap.get(ontoLabel);
				}
			}
			
			// laitetaan kasite ja siihen liittyvat triplet KOKOon
			if (kokoSubj != null) this.lisaaResurssiKokoon(ontoSubj, kokoSubj);
			else {
				if (this.ontoKokoResurssivastaavuudetMap.containsKey(ontoSubj)) {
					kokoSubj = this.ontoKokoResurssivastaavuudetMap.get(ontoSubj);
				} else {
					kokoSubj = this.luoUusiKokoResurssi();
				}
				this.lisaaResurssiKokoon(ontoSubj, kokoSubj);
			}
		}
	}
	
	public void parsiErikoisontologioidenPolutVektoriin(String ontologioidenPolutJaTyypitTxt) {
		this.ontologioidenTyypitPolutMap = new HashMap<Resource, String>();
		Vector<String> polkuVektori = new Vector<String>();
		try {
			BufferedReader br = new BufferedReader( new InputStreamReader( new FileInputStream(ontologioidenPolutJaTyypitTxt), "UTF8" ) );

			String rivi = br.readLine().trim();
			while (rivi != null) {
				rivi = rivi.trim();
				if (!rivi.startsWith("#")) { 
					String[] uriTaulukko = rivi.split(" ");
					polkuVektori.add(uriTaulukko[1].trim());
					this.ontologioidenTyypitPolutMap.put(this.koko.createResource(uriTaulukko[0].trim()), uriTaulukko[1].trim());
				}
				rivi = br.readLine();
			}
			br.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void korjaaLopuksiObjectit() {
		System.out.println("Korjataan KOKOn objektit.");		
		HashSet<Statement> poistettavat = new HashSet<Statement>();
		HashSet<Statement> lisattavat = new HashSet<Statement>();
		StmtIterator iter = this.koko.listStatements();
		Property skosExactMatch = this.koko.createProperty(this.skosNs + "exactMatch");
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (!stmt.getPredicate().equals(skosExactMatch)) {
				RDFNode obj = stmt.getObject();
				if (obj.isURIResource()) {
					if (this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.containsKey(obj)) {
						Resource uusiObj = this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(obj);
						poistettavat.add(stmt);
						lisattavat.add(this.koko.createStatement(stmt.getSubject(), stmt.getPredicate(), uusiObj));
					}
				}
			}
		}
		for (Statement stmt:poistettavat) this.koko.remove(stmt);
		for (Statement stmt:lisattavat) this.koko.add(stmt);
	}
	
	public void lisaaExactMatchitAiemmassaKokossaOlleisiin(String aiemmanKokonpolku) {
		System.out.println("Lisataan linkit aiemmassa KOKOssa olleisiin kasitteisiin.");		
		int i = 0;
		Model aiempiKoko = JenaHelpers.lueMalliModeliksi(aiemmanKokonpolku);
		Property skosPrefLabel = aiempiKoko.createProperty(this.skosNs + "prefLabel");
		aiempiKoko = JenaHelpers.muunnaKielikoodittomatLabelitSuomenkielisiksi(aiempiKoko, skosPrefLabel);
		HashSet<Resource> nykyKokonResurssit = new HashSet<Resource>();
		Resource skosConcept = this.koko.createResource(this.skosNs + "Concept");
		ResIterator resIter = this.koko.listResourcesWithProperty(RDF.type, skosConcept);
		while (resIter.hasNext()) {
			Resource subj = resIter.nextResource();
			nykyKokonResurssit.add(subj);
		}
		
		HashSet<Resource> aiemmassaKokossaOlleetMuttaNykyKokostaPuuttuvatResurssit = new HashSet<Resource>();
		resIter = aiempiKoko.listResourcesWithProperty(RDF.type, skosConcept);
		while (resIter.hasNext()) {
			Resource subj = resIter.nextResource();
			if (!nykyKokonResurssit.contains(subj)) {
				aiemmassaKokossaOlleetMuttaNykyKokostaPuuttuvatResurssit.add(subj);
			}
		}
		
		System.out.println(aiemmassaKokossaOlleetMuttaNykyKokostaPuuttuvatResurssit.size());
		HashMap<Resource, String> aiemmanKokonNykyKokostaPuuttuvienFiLabelitMap = this.haeTietynTyyppistenResurssienLabelitMappiin(aiempiKoko, skosPrefLabel, aiemmassaKokossaOlleetMuttaNykyKokostaPuuttuvatResurssit, "fi");
		System.out.println(aiemmanKokonNykyKokostaPuuttuvienFiLabelitMap.size());
		
		Property skosExactMatch = this.koko.createProperty(skosNs + "exactMatch");
		for (Resource subj:aiemmassaKokossaOlleetMuttaNykyKokostaPuuttuvatResurssit) {
			boolean loytyiVastine = false;
			HashSet<Resource> subjinAiemmassaKokossaOlevatExactMatchit = new HashSet<Resource>();
			StmtIterator iter = aiempiKoko.listStatements(subj, skosExactMatch, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				Resource obj = (Resource)(stmt.getObject());
				subjinAiemmassaKokossaOlevatExactMatchit.add(obj);
			}
			iter = aiempiKoko.listStatements(subj, DCTerms.isReplacedBy, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				Resource obj = (Resource)(stmt.getObject());
				subjinAiemmassaKokossaOlevatExactMatchit.add(obj);
			}
			for (Resource obj:subjinAiemmassaKokossaOlevatExactMatchit) {
				if (nykyKokonResurssit.contains(obj)) {
					loytyiVastine = true;
					this.koko.add(subj, DCTerms.isReplacedBy, obj);
				}
			}
			if (!loytyiVastine) {
				for (Resource obj:subjinAiemmassaKokossaOlevatExactMatchit) {
					if (this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.containsKey(obj)) {
						loytyiVastine = true;
						this.koko.add(subj, DCTerms.isReplacedBy, this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(obj));
					}
				}
			}
			if (!loytyiVastine) {
				if (aiemmanKokonNykyKokostaPuuttuvienFiLabelitMap.containsKey(subj)) {
					String labelString = aiemmanKokonNykyKokostaPuuttuvienFiLabelitMap.get(subj);
					if (this.kokoFiLabelitResurssitMap.containsKey(labelString)) {
						loytyiVastine = true;
						this.koko.add(subj, DCTerms.isReplacedBy, this.kokoFiLabelitResurssitMap.get(labelString));
					}
				}
			}
			if (!loytyiVastine) {
				i++;
				if (aiemmanKokonNykyKokostaPuuttuvienFiLabelitMap.containsKey(subj)) {
					System.out.println(i + ". ongelma: Edellisessä KOKOssa oli käsite, jolle ei löytynyt vastinetta uuteen KOKOon: " + aiemmanKokonNykyKokostaPuuttuvienFiLabelitMap.get(subj) + " -- " + subj.getURI());
				} else {
					System.out.println(i + ". ongelma: Edellisessä KOKOssa oli käsite, jolle ei löytynyt vastinetta uuteen KOKOon: " + subj.getURI());
				}
			}
		}
		//JenaHelpers.testaaMallinLabelienKielet(aiempiKoko, skosPrefLabel);
	}
	
	public void kirjoitaUudetUriVastaavuudet(String tiedostonPolku) {
		try {
			FileWriter fstream = new FileWriter(tiedostonPolku);
			BufferedWriter out = new BufferedWriter(fstream);
			for (Resource vanhaUriRes:this.ontoKokoResurssivastaavuudetMap.keySet()) {
				String vanhaUriString = vanhaUriRes.getURI();
				String kokoUriString = this.ontoKokoResurssivastaavuudetMap.get(vanhaUriRes).getURI();
				out.write(vanhaUriString + " " + kokoUriString + "\n");
			}
			out.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		System.out.println("Uudet KOKO-URI-vastaavuudet kirjoitettu tiedostoon " + tiedostonPolku);
	}
	
	public void kokoa(String ysonPolku, String erikoisontologiaTxtnPolku, String edellisenKokonPolku, String uusienUrivastaavuuksienPolku) {
		this.lueYso(ysonPolku);
		this.parsiErikoisontologioidenPolutVektoriin(erikoisontologiaTxtnPolku);
		for (Resource ontonTyyppi:this.ontologioidenTyypitPolutMap.keySet()) {
			String polku = this.ontologioidenTyypitPolutMap.get(ontonTyyppi);
			this.lueOnto(polku, ontonTyyppi);
		}
		this.hoidaSailotyt();
		this.korjaaLopuksiObjectit();
		this.lisaaExactMatchitAiemmassaKokossaOlleisiin(edellisenKokonPolku);
		this.kirjoitaUudetUriVastaavuudet(uusienUrivastaavuuksienPolku);
	}
	
	public void kirjoitaKoko(String kokonPolku) {
		JenaHelpers.kirjoitaMalli(this.koko, kokonPolku, true);
	}
	
	/*
	 * args[0] = vanhatUrit-KokoUrit-vastaavuudettiedosto
	 * args[1] = yson polku
	 * args[2] = kokon erikoisontologioiden polut ja tyypit
	 * args[3] = uusi vanhatUrit-KokoUrit-vastaavuudettiedosto
	 * args[4] = vanha KOKO
	 * args[5] = uusi KOKO
	 */
	public static void main(String[] args) {
		Kokoaja2014 kokoaja = new Kokoaja2014(args[0]);
		kokoaja.kokoa(args[1], args[2], args[4], args[3]);
		kokoaja.kirjoitaKoko(args[5]);
	}
}
