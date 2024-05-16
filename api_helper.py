import requests
import logging
from psycopg2 import Error
class APIFetch:
    def __init__(self) -> None:
        pass
    def fetch_data(self,url,country:None):
        try:
            if country is not None:
                url=url+f"country={country}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()        
        except Error as e:
            logging.error(f"Failed to fetch data for {url}",e)
    
           