# sparql_decorator.py
import requests
from functools import wraps

def sparql_query(endpoint, params=None, headers=None, limit=1000):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_headers = headers if headers is not None else {'User-Agent': 'finto.fi-automation-to-get-yso-mappings/0.1.0'}
            
            if params is None:
                raise ValueError("Parametrien täytyy sisältää sparkkelin ja formaatin ..")
            
            offset = 0
            all_results = []
            
            while True:
                local_params = params.copy()
                local_params['format'] = 'json'

                paginated_query = f"{local_params['query']} LIMIT {limit} OFFSET {offset}"
                local_params['query'] = paginated_query

                try:
                    response = requests.get(endpoint, params=local_params, headers=local_headers)
                    response.raise_for_status()  # HTTP errors / 4xx ja 5xx
                    data = response.json()
                    
                    results = data['results']['bindings']
                    if not results:
                        break  # Pysähtyy kun tuloksia on tarpeeksi

                    all_results.extend(results)
                    
                    offset += limit

                except requests.exceptions.RequestException as e:
                    print(f"HTTP-virhe: {e}")
                    raise

            # Valmis setti dekoraatiofunktiolle
            return func({'results': {'bindings': all_results}}, *args, **kwargs)
        
        return wrapper
    return decorator
