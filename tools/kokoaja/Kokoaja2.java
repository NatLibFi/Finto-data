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



public class Kokoaja2 {

	private final String skosNs = "http://www.w3.org/2004/02/skos/core#";
	private final String skosextNs = "http://purl.org/finnonto/schema/skosext#";
	private final String kokoNs ="http://www.yso.fi/onto/koko/";
	private final String kokoMetaNs ="http://www.yso.fi/onto/koko-meta/";
	
	private Model koko;
	private Model onto;
	
	private HashMap<Resource, String> ontologioidenTyypitPolutMap;
	private HashMap<String, Resource> kokoFiLabelitResurssitMap;
	private HashMap<Resource, String> ontoFiResurssitLabelitMap;
	private HashMap<Resource, Resource> ontoKokoResurssivastaavuudetMap;
	private HashMap<Resource, Resource> ontoKokoResurssivastaavuudetJotkaNykyKokossaMap;
	
	private HashSet<String> sallittujenPropertyjenNimiavaruudet;
	private HashSet<Resource> mustaLista;
	
	private int viimeisinKokoUrinLoppuosa;
	
	private int labelinPerusteellaYsoonYhdistyneet;
	private int labelinPerusteellaMuuhunKuinYsoonYhdistyneet;
	
	public Kokoaja2(String uriVastaavuuksiePolku) {
		this.labelinPerusteellaYsoonYhdistyneet = 0;
		this.labelinPerusteellaMuuhunKuinYsoonYhdistyneet = 0;
		this.taytaSallittujenPropertyjenNimiavaruudet();
		this.koko = this.luoAihio();
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
		Property skosPrefLabel = this.onto.createProperty(this.skosNs + "prefLabel");
		this.ontoFiResurssitLabelitMap = this.haeTietynTyyppistenResurssienLabelitMappiin(this.onto, skosPrefLabel, ysonKasiteresurssit, "fi");
		
		// luodaan YSOConcept-tyyppiluokka
		this.luoYSOConceptTyyppiLuokkaKokoon();
		
		Property skosInScheme = this.koko.createProperty(this.skosNs + "inScheme");
		Resource ysoConceptScheme = this.koko.createResource("http://www.yso.fi/onto/yso/");
		ResIterator resIter = this.onto.listResourcesWithProperty(skosInScheme, ysoConceptScheme);
		while (resIter.hasNext()) {
			Resource ysoSubj = resIter.nextResource();
			this.lisaaResurssiKokoon(ysoSubj, ysoSubj, true);
		}
		
		// kaivetaan KOKOon vielä isReplacedBy-tyyppiset suhteet
		StmtIterator iter = this.onto.listStatements((Resource)null, DCTerms.isReplacedBy, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			this.koko.add(stmt);
		}
	}
	
	private void luoYSOConceptTyyppiLuokkaKokoon() {
		String ysoMetaNs = "http://www.yso.fi/onto/yso-meta/";
		Resource skosConcept = this.onto.createResource(this.skosNs + "Concept");
		
		Resource ysoConcept = this.koko.createResource(ysoMetaNs + "Concept");
		Literal fiLabel = this.koko.createLiteral("YSO-käsite", "fi");
		Literal enLabel = this.koko.createLiteral("YSO Concept", "en");
		Literal svLabel = this.koko.createLiteral("Allfo-begrepp", "sv");
		this.koko.add(ysoConcept, RDF.type, OWL.Class);
		this.koko.add(ysoConcept, RDFS.label, fiLabel);
		this.koko.add(ysoConcept, RDFS.label, enLabel);
		this.koko.add(ysoConcept, RDFS.label, svLabel);
		this.koko.add(ysoConcept, RDFS.subClassOf, skosConcept);
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
	
	/*
	 *  primaryLabelSource on true YSOlle, jolloin YSOn prefLabelit otetaan sellaisinaan ja muille false
	 *  jolloin prefLabeleista tulee skosext:candidateLabeleita
	 */
	private void lisaaResurssiKokoon(Resource ontoSubj, Resource kokoSubj, boolean primaryLabelSource) {
		Property skosExactMatch = this.onto.createProperty(this.skosNs + "exactMatch");
		Property skosPrefLabel = this.onto.createProperty(skosNs + "prefLabel");
		Property skosextCandidateLabel = this.onto.createProperty(skosextNs + "candidateLabel");
		
		HashSet<Property> propertytJoitaEiHalutaKokoon = new HashSet<Property>();
		propertytJoitaEiHalutaKokoon.add(this.onto.createProperty(this.skosNs + "inScheme"));
		propertytJoitaEiHalutaKokoon.add(this.onto.createProperty(this.skosNs + "topConceptOf"));
		propertytJoitaEiHalutaKokoon.add(this.onto.createProperty(this.skosNs + "narrower"));
		
		this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.put(ontoSubj, kokoSubj);
		this.kokoFiLabelitResurssitMap.put(this.ontoFiResurssitLabelitMap.get(ontoSubj), kokoSubj);
		this.koko.add(kokoSubj, skosExactMatch, ontoSubj);
		StmtIterator iter = this.onto.listStatements(ontoSubj, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (!(stmt.getObject().isURIResource() && this.mustaLista.contains(stmt.getObject()))) {
				if (this.sallittujenPropertyjenNimiavaruudet.contains(stmt.getPredicate().getNameSpace()))
					if (stmt.getPredicate().equals(skosPrefLabel)) {
						if (primaryLabelSource) {
							this.koko.add(kokoSubj, stmt.getPredicate(), stmt.getObject());
						} else {
							this.koko.add(kokoSubj, skosextCandidateLabel, stmt.getObject());
						}
					} else if (!propertytJoitaEiHalutaKokoon.contains(stmt.getPredicate())) {
						this.koko.add(kokoSubj, stmt.getPredicate(), stmt.getObject());
					}
			}
		}
	}
	
	public void lueOnto(String ontonPolku, Resource ontoTyyppi) {
		System.out.println("Luetaan " + ontonPolku);
		this.onto = JenaHelpers.lueMalliModeliksi(ontonPolku);
		
		int kasiteltavanOntologianLabelinPerusteellaRomautetutKasitteet = 0;
		
		StmtIterator iter = this.onto.listStatements(ontoTyyppi, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			this.koko.add(stmt);
		}
		
		// kaivetaan HashSettiin kaikki erikoisontologian oman tyyppiset kasitteet
		HashSet<Resource> ontonOntoTyyppisetResurssit = this.haeTietynTyyppisetResurssit(this.onto, ontoTyyppi);
		System.out.println("Lisataan KOKOon " + ontonOntoTyyppisetResurssit.size() + " " + ontoTyyppi.getURI() + " -tyyppista resurssia.");
		
		// kaivetaan HashMappiin kaikki erikoisontologian suorat skos:exactMatchit
		HashMap<Resource, HashSet<Resource>> ontonExactMatchitMap = new HashMap<Resource, HashSet<Resource>>();
		Property skosExactMatch = this.onto.createProperty(this.skosNs + "exactMatch");
		iter = this.onto.listStatements((Resource)null, skosExactMatch, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			Resource subj = stmt.getSubject();
			if (!this.mustaLista.contains(subj)) {
				if (ontonOntoTyyppisetResurssit.contains(subj)) {
					HashSet<Resource> matchitSet = new HashSet<Resource>();
					if (ontonExactMatchitMap.containsKey(subj)) {
						matchitSet = ontonExactMatchitMap.get(subj);
					}
					matchitSet.add((Resource)(stmt.getObject()));
					ontonExactMatchitMap.put(subj, matchitSet);
				}
			}
		}

		// kaivetaan HashMappiin kaikki erikoisontologian fiLabelit
		Property skosPrefLabel = this.onto.createProperty(this.skosNs + "prefLabel");
		this.ontoFiResurssitLabelitMap = this.haeTietynTyyppistenResurssienLabelitMappiin(this.onto, skosPrefLabel, ontonOntoTyyppisetResurssit, "fi");

		ResIterator resIter = this.onto.listResourcesWithProperty(RDF.type, ontoTyyppi);
		while (resIter.hasNext()) {
			Resource ontoSubj = resIter.nextResource();
			if (!this.mustaLista.contains(ontoSubj)) {
				Resource kokoSubj = null;

				// Tutkitaan mika on resurssia vastaava resurssi kokossa tai jos moista ei ole, paatetaan sailotaanko vai ei
				if (this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.containsKey(ontoSubj)) {
					kokoSubj = ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(ontoSubj);
				} else if (ontonExactMatchitMap.containsKey(ontoSubj)) {
					for (Resource matchRes:ontonExactMatchitMap.get(ontoSubj)) {
						if (this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.containsKey(matchRes)) {
							kokoSubj = this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(matchRes);
						}
					}
				}
				
				if (kokoSubj == null && this.ontoFiResurssitLabelitMap.containsKey(ontoSubj)) {
					String ontoLabel = ontoFiResurssitLabelitMap.get(ontoSubj);
					if (this.kokoFiLabelitResurssitMap.containsKey(ontoLabel)) {
						kokoSubj = this.kokoFiLabelitResurssitMap.get(ontoLabel);
						kasiteltavanOntologianLabelinPerusteellaRomautetutKasitteet++;
						if (kokoSubj.getNameSpace().equals("http://www.yso.fi/onto/yso/")) {
							this.labelinPerusteellaYsoonYhdistyneet++;
							//System.out.println(kasiteltavanOntologianLabelinPerusteellaRomautetutKasitteet + ";ye;" + this.labelinPerusteellaYsoonYhdistyneet + ";" + kokoSubj.getURI() + ";" + ontoSubj.getURI() + ";" + ontoLabel);
						} else {
							this.labelinPerusteellaMuuhunKuinYsoonYhdistyneet++;
							//System.out.println(kasiteltavanOntologianLabelinPerusteellaRomautetutKasitteet + ";ee;" + this.labelinPerusteellaMuuhunKuinYsoonYhdistyneet+ ";" + kokoSubj.getURI() + ";" + ontoSubj.getURI() + ";" + ontoLabel);
						}
					}
				}
				if (kokoSubj == null) kokoSubj = ontoSubj;
				
				// laitetaan kasite ja siihen liittyvat triplet KOKOon					
				this.lisaaResurssiKokoon(ontoSubj, kokoSubj, false);
				if (ontonExactMatchitMap.containsKey(ontoSubj)) {
					for (Resource matchRes:ontonExactMatchitMap.get(ontoSubj)) {
						this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.put(matchRes, kokoSubj);
					}
				}
			}
		}
		// kaivetaan KOKOon vielä isReplacedBy-tyyppiset suhteet
		iter = this.onto.listStatements((Resource)null, DCTerms.isReplacedBy, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			this.koko.add(stmt);
		}
	}
	
	public Resource luoUusiKokoResurssi() {
		this.viimeisinKokoUrinLoppuosa++;
		Resource uusiResurssi = this.koko.createResource(this.kokoNs + "p" + this.viimeisinKokoUrinLoppuosa);
		return uusiResurssi;
	}
			
	public void muutaUritKokoUreiksi() {
		HashSet<Resource> kokonSubjektit = new HashSet<Resource>();
		HashSet<Resource> kokossaOlevatKokoUritTaiOikeamminResurssit = new HashSet<Resource>();
		Resource skosConcept = this.koko.createResource(this.skosNs + "Concept");
		ResIterator resIter = this.koko.listResourcesWithProperty(RDF.type, skosConcept);
		while (resIter.hasNext()) {
			Resource subj = resIter.nextResource();
			kokonSubjektit.add(subj);
		}
		StmtIterator iter = this.koko.listStatements((Resource)null, DCTerms.isReplacedBy, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			kokonSubjektit.add(stmt.getSubject());
		}
		Property skosExactMatch = this.onto.createProperty(this.skosNs + "exactMatch");
		for (Resource subj:kokonSubjektit) {
			HashSet<Resource> ontoSubjSet = new HashSet<Resource>();
			ontoSubjSet.add(subj);
			iter = this.koko.listStatements(subj, skosExactMatch, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				ontoSubjSet.add((Resource)(stmt.getObject()));
			}
			Resource kokoSubj = null;
			for (Resource ontoSubj:ontoSubjSet) {
				if (kokoSubj == null && this.ontoKokoResurssivastaavuudetMap.containsKey(ontoSubj)) {
					if (kokossaOlevatKokoUritTaiOikeamminResurssit.contains(this.ontoKokoResurssivastaavuudetMap.get(ontoSubj))) {
						kokoSubj = this.luoUusiKokoResurssi();
					} else {
						kokoSubj = this.ontoKokoResurssivastaavuudetMap.get(ontoSubj);
					}
				} else if (kokoSubj != null && this.ontoKokoResurssivastaavuudetMap.containsKey(ontoSubj) && !kokoSubj.equals(this.ontoKokoResurssivastaavuudetMap.get(ontoSubj))) {
					this.koko.add(this.ontoKokoResurssivastaavuudetMap.get(ontoSubj), DCTerms.isReplacedBy, kokoSubj);
				}
			}
			if (kokoSubj == null) {
				kokoSubj = this.luoUusiKokoResurssi();
			}
			kokossaOlevatKokoUritTaiOikeamminResurssit.add(kokoSubj);
			for (Resource ontoSubj:ontoSubjSet) {
				this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.put(ontoSubj, kokoSubj);
				this.ontoKokoResurssivastaavuudetMap.put(ontoSubj, kokoSubj);
			}
			this.muutaKokoSubj(subj, kokoSubj);
		}
	}
		
	private void muutaKokoSubj(Resource vanhaSubj, Resource uusiSubj) {
		HashSet<Statement> poistettavat = new HashSet<Statement>();
		HashSet<Statement> lisattavat = new HashSet<Statement>();
		StmtIterator iter = this.koko.listStatements(vanhaSubj, (Property)null, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			poistettavat.add(stmt);
			lisattavat.add(this.koko.createStatement(uusiSubj, stmt.getPredicate(), stmt.getObject()));
		}
		for (Statement s:poistettavat) this.koko.remove(s);
		for (Statement s:lisattavat) this.koko.add(s);
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
			if (!(stmt.getPredicate().equals(skosExactMatch))) {
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
	
	public void tulostaMuutoksetEdelliseenVerrattuna(String aiemmanKokonpolku) {
		System.out.println("Tulostetaan prefLabel-muutokset edelliseen KOKOon verrattuna.");		
		int i = 0;
		Model aiempiKoko = JenaHelpers.lueMalliModeliksi(aiemmanKokonpolku);
		Property skosPrefLabel = aiempiKoko.createProperty(this.skosNs + "prefLabel");
		aiempiKoko = JenaHelpers.muunnaKielikoodittomatLabelitSuomenkielisiksi(aiempiKoko, skosPrefLabel);
		
		HashMap<Resource, String> nykyKokonPrefLabelitMap = new HashMap<Resource, String>();
		StmtIterator iter = this.koko.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String fiLabelString = ((Literal)stmt.getObject()).getLexicalForm();
				nykyKokonPrefLabelitMap.put(stmt.getSubject(), fiLabelString);
			}
		}
		iter = aiempiKoko.listStatements((Resource)null, skosPrefLabel, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("fi")) {
				String fiLabelString = ((Literal)stmt.getObject()).getLexicalForm();
				if (nykyKokonPrefLabelitMap.containsKey(stmt.getSubject())) {
					String nykyFiLabelString = nykyKokonPrefLabelitMap.get(stmt.getSubject());
					String nykyFiLabelStringIlmanSulkutarkenteita = nykyFiLabelString;
					if (nykyFiLabelString.contains("(")) nykyFiLabelStringIlmanSulkutarkenteita = nykyFiLabelString.substring(0, nykyFiLabelString.indexOf("(")).trim();
					String fiLabelStringIlmanSulkutarkenteita = fiLabelString;
					if (fiLabelString.contains("(")) fiLabelStringIlmanSulkutarkenteita = fiLabelString.substring(0, fiLabelString.indexOf("(")).trim();
					if (!(nykyFiLabelStringIlmanSulkutarkenteita.equals(fiLabelStringIlmanSulkutarkenteita))) {
						i++;
						System.out.println(i + ". " + stmt.getSubject().getURI() + " -- " + fiLabelString + " => " + nykyFiLabelString);
					}
				}
			}
		}
		Resource skosConcept = this.koko.createResource(this.skosNs + "Concept");
		HashSet<Resource> uudenKokonResurssit = new HashSet<Resource>();
		ResIterator resIter = this.koko.listSubjectsWithProperty(RDF.type, skosConcept);
		while (resIter.hasNext()) {
			uudenKokonResurssit.add(resIter.nextResource());
		}
		resIter = aiempiKoko.listSubjectsWithProperty(RDF.type, skosConcept);
		while (resIter.hasNext()) {
			uudenKokonResurssit.remove(resIter.nextResource());
		}
		System.out.println("Uudessa KOKOssa on " + uudenKokonResurssit.size() + " uutta käsitettä.");
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
						this.koko.add(subj, DCTerms.isReplacedBy, this.ontoKokoResurssivastaavuudetJotkaNykyKokossaMap.get(this.kokoFiLabelitResurssitMap.get(labelString)));
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
		// Poistetaan itseensä osoittavat replacedByt, sekä ne, jotka tulisivat nyky-KOKOssa ihan varsinaisina käsitteinä olevista
		HashSet<Statement> poistettavat = new HashSet<Statement>();
		StmtIterator iter = this.koko.listStatements((Resource)null, DCTerms.isReplacedBy, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getSubject().equals(stmt.getObject())) poistettavat.add(stmt);
			else {
				StmtIterator iter2 = this.koko.listStatements(stmt.getSubject(), RDF.type, (RDFNode)null);
				if (iter2.hasNext()) poistettavat.add(stmt);
			}
		}
		for (Statement s:poistettavat) this.koko.remove(s);
		
		//JenaHelpers.testaaMallinLabelienKielet(aiempiKoko, skosPrefLabel);
	}
	
	public void lueMustaLista(String mustanListanPolku) {
		this.mustaLista = new HashSet<Resource>();
		try {
			BufferedReader br = new BufferedReader( new InputStreamReader( new FileInputStream(mustanListanPolku), "UTF8" ) );

			String rivi = br.readLine().trim();
			while (rivi != null) {
				rivi = rivi.trim();
				this.mustaLista.add(this.koko.createResource(rivi));
				rivi = br.readLine();
			}
			br.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
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
	
	public void kokoa(String ysonPolku, String erikoisontologiaTxtnPolku, String edellisenKokonPolku, String uusienUrivastaavuuksienPolku, String mustanListanPolku) {
		this.lueMustaLista(mustanListanPolku);
		this.lueYso(ysonPolku);
		this.parsiErikoisontologioidenPolutVektoriin(erikoisontologiaTxtnPolku);
		for (Resource ontonTyyppi:this.ontologioidenTyypitPolutMap.keySet()) {
			String polku = this.ontologioidenTyypitPolutMap.get(ontonTyyppi);
			this.lueOnto(polku, ontonTyyppi);
		}
		this.muutaUritKokoUreiksi();
		this.korjaaLopuksiObjectit();
		this.lisaaExactMatchitAiemmassaKokossaOlleisiin(edellisenKokonPolku);
		this.tulostaMuutoksetEdelliseenVerrattuna(edellisenKokonPolku);
		this.kirjoitaUudetUriVastaavuudet(uusienUrivastaavuuksienPolku);
		System.out.println("Labelin perusteella romautettiin " + this.labelinPerusteellaYsoonYhdistyneet + " käsitettä YSOn ja erikoisontologian välillä ja " + this.labelinPerusteellaMuuhunKuinYsoonYhdistyneet + " käsitettä erikoisontologioiden välillä.");
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
	 * agrs[6] = musta lista (kasitteet, joita ei haluta KOKOon)
	 */
	public static void main(String[] args) {
		Kokoaja2 kokoaja = new Kokoaja2(args[0]);
		kokoaja.kokoa(args[1], args[2], args[4], args[3], args[6]);
		kokoaja.kirjoitaKoko(args[5]);
	}
}
