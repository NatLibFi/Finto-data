package JenaTesting1;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.rdf.model.Statement;
import org.apache.jena.rdf.model.StmtIterator;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFWriter;
import org.apache.jena.riot.RIOT;


public class SimplifiedRemoveTriplesUntilTheLimitIsReached {

	public static void main (String[] args) {
		final File file1 = new File("/home/mijuahon/codes/Finto-data/vocabularies/maotao/maotao-skos.ttl");
		final File file3 = new File(("/home/mijuahon/codes/RDFTools/ykl-2021-11-17/MaoTaoModified.ttl"));
		List<Resource> maoConceptsToKeepSafe = new ArrayList<Resource>();
		List<Resource> ysoConceptsToKeepSafe = new ArrayList<Resource>();
		Model m1 = ModelFactory.createDefaultModel();
		m1.read(file1.toString());
		checkIfFileExists(file1);
		StmtIterator it1ForMao =  m1.listStatements();
		StmtIterator it2ForMao =  m1.listStatements();
		StmtIterator it3ForMao =  m1.listStatements();
		List<Statement> shakenIt1ForMao = new ArrayList<>(it1ForMao.toList());
		List<Statement> allTheRemovables = new ArrayList<>(it3ForMao.toList());
		
		/// Säädä tätä
		int savedConceptsLimitForMao = 500;
//		int savedConceptsLimitForMao = 1000;
		
		for (int i = 0; i < shakenIt1ForMao.size(); i++) {
			if (savedConceptsLimitForMao > 0) {
				if (shakenIt1ForMao.get(i).getSubject().toString().contains("/onto/mao/p") &&
						shakenIt1ForMao.get(i).getObject().toString().contains("/onto/yso/p")) {
					maoConceptsToKeepSafe.add(shakenIt1ForMao.get(i).getSubject());
					if (shakenIt1ForMao.get(i).getObject().isResource()) {
						ysoConceptsToKeepSafe.add(shakenIt1ForMao.get(i).getObject().asResource());
						savedConceptsLimitForMao -= 1;
					}
				}
			}
		}

		while (it2ForMao.hasNext()) {
			Statement stmt = it2ForMao.next();
			Resource subj = stmt.getSubject();
			if (maoConceptsToKeepSafe.contains(subj) ||
					ysoConceptsToKeepSafe.contains(subj)) {
				allTheRemovables.remove(stmt);
			}
		}			
			
		try {
			m1.remove(allTheRemovables);
		} catch (Exception e) {
			System.out.println(e);
		}
		
		System.out.printf("maoConceptsToKeepSafe %s %n", maoConceptsToKeepSafe.size());
		System.out.printf("ysoConceptsToKeepSafe %s %n", ysoConceptsToKeepSafe.size());
		System.out.printf("allTheRemovables %s %n", allTheRemovables.size()); //645534 48401 9926
//		maoConceptsToKeepSafe 10505 
//		ysoConceptsToKeepSafe 10505 
//		allTheRemovables 645534 
				
		RDFWriter.create()
		.set(RIOT.symTurtleDirectiveStyle, "sparql")
		.lang(Lang.TTL)
		.source(m1)
		.output(file3.toString());	
				
	}
	
	private static void checkIfFileExists(File file) {
		try {
			 if (!file.exists())
			    throw new FileNotFoundException();
			}
			catch(FileNotFoundException e) {
			   System.out.println("Syöttämääsi tiedostoa ei löytynyt");
			}
	}
}
