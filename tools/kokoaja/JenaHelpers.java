import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.HashSet;

import org.apache.jena.ontology.OntModel;
import org.apache.jena.ontology.OntModelSpec;
import org.apache.jena.rdf.model.*;
import org.apache.jena.util.FileManager;
import org.apache.jena.vocabulary.*;

public class JenaHelpers {

	public static Model lueMalliModeliksi(String polku) {
		System.out.println("luetaan malli sisään.");
		Model malli = ModelFactory.createDefaultModel();
		InputStream in = FileManager.get().open(polku);
		if (in == null) {
			throw new IllegalArgumentException("File: " + polku + " not found");
		}
		if (polku.endsWith(".ttl")) malli.read(in, "", "TTL");
		else malli.read(in, "");
		try {
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("malli luettu sisään.");
		return malli;
	}
	
	public static OntModel lueMalli(String polku, boolean onTtl) {
		System.out.println("luetaan malli sisään.");
		OntModel malli = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
		InputStream in = FileManager.get().open(polku);
		if (in == null) {
			throw new IllegalArgumentException("File: " + polku + " not found");
		}
		if (onTtl) malli.read(in, "", "TTL");
		else malli.read(in, "");

		try {
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("malli luettu sisään.");
		return malli;
	}
	
	public static OntModel lueMalli(String polku) {
		if (polku.endsWith(".ttl")) {
			return JenaHelpers.lueMalli(polku, true);
		} else {
			return JenaHelpers.lueMalli(polku, false);
		}
	}
	
	public static OntModel luoMalli() {
		OntModel malli = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
		return malli;
	}
	
	public static void testaaMallinLabelienKielet(Model malli, Property labelProp) {
		HashMap<String, Integer> kieliLablienMaaraMap = new HashMap<String, Integer>();
		StmtIterator iter = malli.listStatements((Resource)null, labelProp, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			String lang = stmt.getLanguage();
			if (kieliLablienMaaraMap.containsKey(lang)) {
				Integer maara = kieliLablienMaaraMap.get(lang) + 1;
				kieliLablienMaaraMap.put(lang, maara);
			} else {
				kieliLablienMaaraMap.put(lang, 1);
			}
		}
		for (String lang:kieliLablienMaaraMap.keySet()) {
			System.out.println(lang + ": " + kieliLablienMaaraMap.get(lang));
		}
	}
	
	public static Model muunnaKielikoodittomatLabelitSuomenkielisiksi(Model malli, Property labelProp) {
		HashSet<Statement> poistettavat = new HashSet<Statement>();
		HashSet<Statement> lisattavat = new HashSet<Statement>();
		StmtIterator iter = malli.listStatements((Resource)null, labelProp, (RDFNode)null);
		while (iter.hasNext()) {
			Statement stmt = iter.nextStatement();
			if (stmt.getLanguage().equals("")) {
				poistettavat.add(stmt);
				String labelString = ((Literal)(stmt.getObject())).getLexicalForm();
				lisattavat.add(malli.createStatement(stmt.getSubject(), stmt.getPredicate(), malli.createLiteral(labelString, "fi")));
			}
		}
		for (Statement s:poistettavat) malli.remove(s);
		for (Statement s:lisattavat) malli.add(s);
		return malli;
	}
	
	public static HashMap<Resource, String> haeTietynTyyppistenResurssienLabelitMappiin(Model malli, Property labelProp, Resource tyyppi, String kieli) {
		HashSet<Resource> tietynTyyppisetResurssit = new HashSet<Resource>();
		ResIterator resIter = malli.listResourcesWithProperty(RDF.type, tyyppi);
		while (resIter.hasNext()) tietynTyyppisetResurssit.add(resIter.nextResource());
		
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
	
}
