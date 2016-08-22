import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;

import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.vocabulary.RDF;

public class GeneralDeprecator {

	private Model onto;
	private int laskuri;
	private HashMap<Property, Property> nonTransitiveDeprekoimisMap;
	private HashMap<Property, Property> transitiveDeprekoimisMap;
	private HashMap<Property, Property> deprAsObjectMap;
	private HashSet<Resource> deprekoitavienTyypit;
	private Property dateProp;
	private Property labelProp;
	private Property replacedBy;
	private Property replacedByDefault;
	private HashSet<Resource> deprekoidutSet;
	
	public GeneralDeprecator(String deprekoitavanPolku, String deprConfinPolku) {
		this.onto = JenaHelpers.lueMalliModeliksi(deprekoitavanPolku);
		this.nonTransitiveDeprekoimisMap = new HashMap<Property, Property>();
		this.transitiveDeprekoimisMap = new HashMap<Property, Property>();
		this.deprAsObjectMap = new HashMap<Property, Property>();
		this.laskuri = 0;
		this.deprekoitavienTyypit = new HashSet<Resource>();
		this.lueDeprPropertytTiedostosta(deprConfinPolku);
	}
	
	private void lueDeprPropertytTiedostosta(String tiedostonPolku) {
		try {
			FileReader fr = new FileReader(tiedostonPolku);
			BufferedReader br = new BufferedReader(fr);
			String rivi = br.readLine().trim();
			while (rivi != null) {
				rivi = rivi.trim();
				if (rivi.startsWith("#")) {}
				else {
					String[] riviSplit = rivi.split(" ");
					String lineContent = riviSplit[0].trim();
					switch (lineContent) {
					case "dateProperty":
						this.dateProp = this.onto.createProperty(riviSplit[1]);
						break;
					case "class":
						this.deprekoitavienTyypit.add(this.onto.createResource(riviSplit[1])); 
						break;
					case "transitiveProperty":
						this.transitiveDeprekoimisMap.put(this.onto.createProperty(riviSplit[1]), this.onto.createProperty(riviSplit[2]));
						if (riviSplit.length > 3) {
							if (riviSplit[3].equals("deprecatedAsObject"))
								this.deprAsObjectMap.put(this.onto.createProperty(riviSplit[2]), this.onto.createProperty(riviSplit[4]));
						}
						break;
					case "nonTransitiveProperty":
						this.nonTransitiveDeprekoimisMap.put(this.onto.createProperty(riviSplit[1]), this.onto.createProperty(riviSplit[2]));
						if (riviSplit.length > 3) {
							if (riviSplit[3].equals("deprecatedAsObject"))
								this.deprAsObjectMap.put(this.onto.createProperty(riviSplit[2]), this.onto.createProperty(riviSplit[4]));
						}
						break;
					case "labelProperty":
						this.labelProp = this.onto.createProperty(riviSplit[1]);
						break;
					case "replaceByAndDefault":
						this.replacedBy = this.onto.createProperty(riviSplit[1]);
						this.replacedByDefault = this.onto.createProperty(riviSplit[2]);
						break;
					}
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
	}
	
	private void deprekoi() {
		HashSet<Resource> deprekoitavatAll = new HashSet<Resource>();
		for (Resource deprekoitavanTyyppi:this.deprekoitavienTyypit) {
			StmtIterator iter = this.onto.listStatements((Resource)null, RDF.type, deprekoitavanTyyppi);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				deprekoitavatAll.add(stmt.getSubject());
			}
		}
		HashSet<Resource> deprekoitavat = new HashSet<Resource>(deprekoitavatAll);
		for (Resource potentiaalinenDeprekoitava:deprekoitavatAll) {
			StmtIterator iter = this.onto.listStatements(potentiaalinenDeprekoitava, this.dateProp, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				String objString = ((Literal)(stmt.getObject())).getLexicalForm();
				if (objString.contains("deprecated on ")) deprekoitavat.remove(potentiaalinenDeprekoitava);
			}
			
		}
		this.deprekoidutSet = new HashSet<Resource>(deprekoitavat);
		for (Resource deprekoitava:deprekoitavat) {
			this.laskuri++;
			this.merkitseDateJaTarkistaReplaced(deprekoitava);
			if (this.replacedBy != null) this.tarkistaReplacedBy(deprekoitava);
			this.deprekoiEiTransitiivisetPropertyt(deprekoitava);
			this.deprekoiTransitiivisetPropertyt(deprekoitava);
		}
		if (this.labelProp != null) this.tulostaDeprekoidut();
		else System.out.println("Deprekoitiin " + this.laskuri + " kasitetta.");
	}
	
	private void merkitseDateJaTarkistaReplaced(Resource deprekoitava) {
		Date date = new Date();
		SimpleDateFormat sdf = new SimpleDateFormat("dd.MM.yyyy");
		String deprPvm = sdf.format(date);
		this.onto.add(deprekoitava, this.dateProp, this.onto.createLiteral("deprecated on " + deprPvm));
	}
	
	private void tarkistaReplacedBy(Resource deprekoitava) {
		Statement lisattava = null;
		StmtIterator iter = this.onto.listStatements(deprekoitava, this.replacedBy, (RDFNode)null);
		// jos replacedByta ei loydy, lisataan default-propertyn avulla sellainen
		if (!iter.hasNext()) {
			StmtIterator iter2 = this.onto.listStatements(deprekoitava, this.replacedByDefault, (RDFNode)null);
			while (iter2.hasNext()) {
				Statement stmt2 = iter2.nextStatement();
				lisattava = this.onto.createStatement(deprekoitava, this.replacedBy, stmt2.getObject());
			}
		}
		if (lisattava != null) this.onto.add(lisattava);
	}
	
	private void deprekoiTransitiivisetPropertyt(Resource deprekoitava) {
		HashSet<Statement> poistettavat = new HashSet<Statement>();
		HashSet<Statement> lisattavat = new HashSet<Statement>();
		for (Property prop:this.transitiveDeprekoimisMap.keySet()) {
			Property deprProp = this.transitiveDeprekoimisMap.get(prop);
			StmtIterator iter = this.onto.listStatements(deprekoitava, prop, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				poistettavat.add(stmt);
				lisattavat.add(this.onto.createStatement(deprekoitava, deprProp, stmt.getSubject()));
				StmtIterator iter2 = this.onto.listStatements((Resource)null, prop, deprekoitava);
				while (iter2.hasNext()) {
					Statement stmt2 = iter2.nextStatement();
					poistettavat.add(stmt2);
					if (this.deprAsObjectMap.containsKey(prop)) lisattavat.add(this.onto.createStatement(stmt2.getSubject(), this.deprAsObjectMap.get(prop), stmt.getObject()));
					else lisattavat.add(this.onto.createStatement(stmt2.getSubject(), prop, stmt.getObject()));
				}
			}
		}
		for (Statement s:poistettavat) this.onto.remove(s);
		for (Statement s:lisattavat) this.onto.add(s);
	}
	
	private void deprekoiEiTransitiivisetPropertyt(Resource deprekoitava) {
		HashSet<Statement> poistettavat = new HashSet<Statement>();
		HashSet<Statement> lisattavat = new HashSet<Statement>();
		for (Property prop:this.nonTransitiveDeprekoimisMap.keySet()) {
			Property deprProp = this.nonTransitiveDeprekoimisMap.get(prop);
			StmtIterator iter = this.onto.listStatements(deprekoitava, prop, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				poistettavat.add(stmt);
				lisattavat.add(this.onto.createStatement(stmt.getSubject(), deprProp, stmt.getObject()));
			}
			iter = this.onto.listStatements((Resource)null, prop, deprekoitava);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				poistettavat.add(stmt);
				if (this.deprAsObjectMap.containsKey(prop)) lisattavat.add(this.onto.createStatement(stmt.getSubject(), this.deprAsObjectMap.get(prop), stmt.getObject()));
				else lisattavat.add(this.onto.createStatement(deprekoitava, deprProp, stmt.getSubject()));
			}
		}
		for (Statement s:poistettavat) this.onto.remove(s);
		for (Statement s:lisattavat) this.onto.add(s);
	}
	
	public void tulostaDeprekoidut() {
		System.out.println("Deprekoitiin seuraavat:");
		this.laskuri = 0;
		for (Resource deprekoitu:this.deprekoidutSet) {
			StmtIterator iter = this.onto.listStatements(deprekoitu, this.labelProp, (RDFNode)null);
			String labelString = "ei labelia";
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				if (stmt.getLanguage().equals("fi")) {
					labelString = ((Literal)(stmt.getObject())).getLexicalForm();
				}
			}
			this.laskuri++;
			System.out.println(this.laskuri + ". " + labelString);
		}
	}
	
	public void kirjoitaUusiMalli(String uudenPolku) {
		boolean onTtl = false;
		if (uudenPolku.endsWith(".ttl")) onTtl = true;
		JenaHelpers.kirjoitaMalli(this.onto, uudenPolku, onTtl);
	}
	
	/*
	 * args[0] = deprekoitavanPolku
	 * args[1] = deprConfinPolku
	 * args[2] = outputFile
	 */
	public static void main(String[] args) {
		GeneralDeprecator gd = new GeneralDeprecator(args[0], args[1]);
		gd.deprekoi();
		gd.kirjoitaUusiMalli(args[2]);
	}
	
}
