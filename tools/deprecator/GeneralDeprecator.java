import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Vector;

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
	private HashSet<Statement> epailyttavatUudetStatementit;
	private Vector<String> emailSet;
	
	public GeneralDeprecator(String deprekoitavanPolku, String deprConfinPolku) {
		this.onto = JenaHelpers.lueMalliModeliksi(deprekoitavanPolku);
		this.nonTransitiveDeprekoimisMap = new HashMap<Property, Property>();
		this.transitiveDeprekoimisMap = new HashMap<Property, Property>();
		this.deprAsObjectMap = new HashMap<Property, Property>();
		this.laskuri = 0;
		this.labelProp = null;
		this.deprekoitavienTyypit = new HashSet<Resource>();
		this.epailyttavatUudetStatementit = new HashSet<Statement>();
		this.emailSet = new Vector<String>();
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
					case "emailForAnomalies":
						this.emailSet.add(riviSplit[1]);
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
	
	private void deprekoi(String spostiFilename) {
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
		if (this.emailSet != null) this.kirjoitaSposti(spostiFilename);
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
				lisattavat.add(this.onto.createStatement(deprekoitava, deprProp, stmt.getObject()));
				StmtIterator iter2 = this.onto.listStatements((Resource)null, prop, deprekoitava);
				while (iter2.hasNext()) {
					Statement stmt2 = iter2.nextStatement();
					poistettavat.add(stmt2);
					Statement uusiStmt = this.onto.createStatement(stmt2.getSubject(), prop, stmt.getObject()); 
					lisattavat.add(uusiStmt);
					this.epailyttavatUudetStatementit.add(uusiStmt);
					if (this.deprAsObjectMap.containsKey(deprProp)) lisattavat.add(this.onto.createStatement(deprekoitava, this.deprAsObjectMap.get(deprProp), stmt2.getSubject()));
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
				if (this.deprAsObjectMap.containsKey(deprProp)) lisattavat.add(this.onto.createStatement(deprekoitava, this.deprAsObjectMap.get(deprProp), stmt.getSubject()));
				else lisattavat.add(this.onto.createStatement(deprekoitava, deprProp, stmt.getSubject()));
			}
		}
		for (Statement s:poistettavat) this.onto.remove(s);
		for (Statement s:lisattavat) this.onto.add(s);
	}
	
	private String haeLabel(Resource haettava) {
		String labelString = haettava.getURI();
		if (this.labelProp != null) {
			StmtIterator iter = this.onto.listStatements(haettava, this.labelProp, (RDFNode)null);
			while (iter.hasNext()) {
				Statement stmt = iter.nextStatement();
				if (stmt.getLanguage().equals("fi")) {
					labelString = ((Literal)(stmt.getObject())).getLexicalForm();
				}
			}
		}
		return labelString;
	}
	
	public void tulostaDeprekoidut() {
		System.out.println("Deprekoitiin seuraavat:");
		String viesti = "";
		
		Vector<String> stringVektori = new Vector<String>();
		
		for (Resource deprekoitu:this.deprekoidutSet) {
			String labelString = this.haeLabel(deprekoitu);
			stringVektori.add(labelString + "\n");
		}
		Collections.sort(stringVektori);
		
		this.laskuri = 0;
		for (String teksti:stringVektori) {
			this.laskuri++;
			viesti += this.laskuri + ". " + teksti;
		}
		System.out.println(viesti);
	}
	
	public void kirjoitaSposti(String filename) {
		String osoite = "To: ";
		for (int i = 0; i < this.emailSet.size(); i++) {
			osoite += this.emailSet.get(i);
			if (i != this.emailSet.size()-1) osoite += ", "; 
		}
		String otsikko = "Subject: General Deprecatorilla on asiaa";
		String viesti = "Seuraavat deprekoinnin muodostamat suhteet kannattanee tarkistaa:\n\n";
		HashMap<String, String> stringMap = new HashMap<String, String>();
		for (Statement s:epailyttavatUudetStatementit) {
			if (this.labelProp != null) {
				String subjLabel = this.haeLabel(s.getSubject());
				String objLabel = this.haeLabel((Resource)(s.getObject()));
				String teksti = subjLabel + "\n   " + s.getPredicate().getLocalName() + "\n   " + objLabel + "\n";
				stringMap.put(teksti, "  " + s + "\n\n");	
			} else {
				stringMap.put("Ei labelPropertya", "  " + s + "\n\n");
			}
		}
		
		Vector<String> avaimet = new Vector<String>(); 
		for (String avain:stringMap.keySet()) {
			avaimet.add(avain);
		}
		Collections.sort(avaimet);
		
		this.laskuri = 0;
		for (String teksti:avaimet) {
			this.laskuri++;
			viesti += this.laskuri + ". " + teksti;
			viesti += stringMap.get(teksti);
		}
		
		Date date = new Date();
		SimpleDateFormat sdf = new SimpleDateFormat("dd.MM.yyyy");
		String deprPvm = sdf.format(date);
		
		viesti += "Deprekoinnissa " + deprPvm + " deprekoitiin seuraavat:\n";
		
		Vector<String> stringVektori = new Vector<String>();
				
		for (Resource deprekoitu:this.deprekoidutSet) {
			String labelString = this.haeLabel(deprekoitu);
			stringVektori.add(labelString + "\n");
		}
		Collections.sort(stringVektori);
		
		this.laskuri = 0;
		for (String teksti:stringVektori) {
			this.laskuri++;
			viesti += this.laskuri + ". " + teksti;
		}
		
		BufferedWriter writer = null;
		try
		{
		    writer = new BufferedWriter( new FileWriter(filename));
		    writer.write(osoite + "\n");
		    writer.write(otsikko + "\n\n");
		    writer.write(viesti);
		}
		catch ( IOException e)
		{
		}
		finally
		{
		    try
		    {
		        if ( writer != null)
		        writer.close( );
		    }
		    catch ( IOException e)
		    {
		    }
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
	 * args[3] = email outputFile
	 */
	public static void main(String[] args) {
		GeneralDeprecator gd = new GeneralDeprecator(args[0], args[1]);
		gd.deprekoi(args[3]);
		gd.kirjoitaUusiMalli(args[2]);
	}
	
}
