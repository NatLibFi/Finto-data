import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Vector;

import com.opencsv.CSVReader;

public class HeroParser {

	public static void main(String[] args) throws IOException {
		new HeroParser(args[0]);
	}

	public HeroParser(String fileName) throws IOException {
		HashMap<Integer, Hero> heroMap = new HashMap<Integer, Hero>();
		CSVReader csvReader = new CSVReader(new FileReader(fileName));
		BufferedWriter writer = new BufferedWriter(new FileWriter("hero.ttl"));
		Iterator<String[]> iter = csvReader.iterator();
		iter.next();

		while (iter.hasNext()) {
			String[] line = iter.next();
			String idField = line[1].trim();
			if (!idField.equals("")) {
				Integer id = new Integer( idField );
				String lineString = "";
				for (int i=2; i<line.length; i++)
					lineString += line[i] + " ";
				lineString = lineString.trim();
				//korjataan kieliattribuutit literaaleille
				lineString = lineString.replace(" @", "@")+"\n";
				//korjataan hyperlinkit
				lineString = lineString.replace("\"\"", "\\\"");

				//korjataan väärinmuodostetut hero-linkit
				if (!lineString.contains("@prefix") && !(lineString.equals("hero:")))
					lineString = lineString.replace("hero:", "hero:p").replace("hero:pp", "hero:p");

				//generoidaan aloitus- ja lopetuslausekkeet vasta kirjoittamisen yhteydessä
				if (!lineString.startsWith("hero:") && !(lineString.startsWith("hero-meta:"))) {
					if (heroMap.get(id) != null) {
						//generoidaan aloitus- ja lopetuslausekkeet vasta kirjoittamisen yhteydessä
						if (!lineString.trim().equals(".")) {
							Hero hero = heroMap.get(id);		
							hero.data.add(lineString);
							heroMap.put(id, hero);
						}

					} else {
						Hero hero = new Hero();
						if (!lineString.trim().equals(".")) {
							hero.data.addElement(lineString);
						}
						heroMap.put(id, hero);
					}
				}
			} else {
				//boiler plate
				int id = 0;
				Hero hero;
				if (heroMap.get(id) != null) {
					hero = heroMap.get(id);
				} else {
					hero = new Hero();
					heroMap.put(id, hero);
				}

				String lineString = "";
				for (int i=2; i<line.length; i++)
					lineString += line[i] + " ";
				lineString = lineString.trim();
				
				//jätetään käännösluonnokset pois
				if (!lineString.startsWith("dc:description  \"(käännös")) {	
					//korjataan kieliattribuutit literaaleille
					lineString = lineString.replace(" @", "@")+"\n";
					//korjataan hyperlinkit
					lineString = lineString.replace("\"\"", "\\\"");

					//generoidaan aloitus- ja lopetuslausekkeet vasta kirjoittamisen yhteydessä
					if (!lineString.startsWith("hero:") || !(lineString.startsWith("hero-meta:"))) {
						hero.data.add(lineString);
						heroMap.put(id, heroMap.get(id));
					}
				}
			}
		}
		csvReader.close();

		for (Integer i :heroMap.keySet()) {
			Hero hero = heroMap.get(i);

			String stringRep = "";
			for (String datum : hero.data)
				stringRep += datum;

			if ( (!stringRep.contains("rdf:type")) && i.intValue() > 0 ) {
				stringRep = "rdf:type skos:Concept ;\n" + stringRep;
			}
			if (i.intValue() > 0)
				stringRep = "hero:p"+i.intValue() + "\n" + stringRep + ".\n\n";
			writer.write(stringRep);
		}

		writer.flush();
		writer.close();
	}

	class Hero {
		Vector<String> data;

		public Hero() {
			this.data = new Vector<String>();
		}
	}
}