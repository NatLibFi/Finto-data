import com.mysql.jdbc.Driver;
import com.hp.hpl.jena.query.Dataset;
import com.hp.hpl.jena.query.Query;
import com.hp.hpl.jena.query.QueryExecution;
import com.hp.hpl.jena.query.QueryExecutionFactory;
import com.hp.hpl.jena.query.QueryFactory;
import com.hp.hpl.jena.query.ResultSet;
import com.hp.hpl.jena.query.ResultSetFormatter;
import com.hp.hpl.jena.sdb.SDBFactory;
import com.hp.hpl.jena.sdb.Store;
import com.hp.hpl.jena.sdb.StoreDesc;
import com.hp.hpl.jena.sdb.sql.SDBConnection;


public class HelloSDB2 {
	StoreDesc storeDesc; 
	
	public HelloSDB2() {
		storeDesc = StoreDesc.read("sdb-yso.ttl"); 
	
	}
	
	public void testQuery(String queryString) {
        Query query = QueryFactory.create(queryString) ;	
        
		SDBConnection conn = SDBFactory.createConnection("sdb-yso.ttl");
		
		Store store = SDBFactory.connectStore(conn, storeDesc);
		
		Dataset ds = SDBFactory.connectDataset(store);
		QueryExecution qe = QueryExecutionFactory.create(query, ds);
		try {
            ResultSet rs = qe.execSelect() ;
            ResultSetFormatter.out(rs) ;
        } finally { qe.close() ; }
        store.close() ;
		
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		HelloSDB2 test = new HelloSDB2();
		String countQuery = "prefix skos:  <http://www.w3.org/2004/02/skos/core#>" +
							"SELECT ?lang (COUNT(?label) as ?count)" +
							"WHERE { GRAPH <http://www.yso.fi/onto/yso> { " + 
							"?conc a skos:Concept . ?conc skos:prefLabel ?label . " +
							"FILTER (langMatches(lang(?label), ?lang)) } }" + 
							"GROUP BY ?lang VALUES (?lang) { ('fi') ('sv') ('en') }";
		test.testQuery(countQuery);

	}

}
