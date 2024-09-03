import requests
from functools import wraps

def sparql_query(endpoint, params=None, headers=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            local_headers = headers if headers is not None else {'User-Agent': 'finto.fi-automation-to-get-yso-mappings/0.1.0'}

            if params is None:
                raise ValueError("Parametrien täytyy sisältää sparkkelin ja formaatin ..")
            local_params = params.copy()
            local_params['format'] = 'json'

            try:
                response = requests.get(endpoint, params=local_params, headers=local_headers)
                response.raise_for_status()  # HTTP-errorit 4xx and 5xx, jos niin käy
                return func(response.json(), *args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(f"HTTP-virhe: {e}")
                raise
        return wrapper
    return decorator
