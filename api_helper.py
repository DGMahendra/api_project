import requests
import logging

class APIFetch:
    def __init__(self) -> None:
        pass
    def fetch_data(self,url,country:None):
        if country is not None:
            print("Data of Country and Univerities:")
            response = requests.get(url)
            if response.status_code == 200:
                universities = response.json()
                print(country,universities)
            else:
                logging.error(f"Failed to fetch data for {country}")
        else:
            print("data of persons:")
            for _ in range(50): 
                response = requests.get("https://randomuser.me/api/")
                if response.status_code == 200:
                    persons = response.json()['results']
                print(persons)
            else:
                logging.error("Failed to fetch data for persons")

def main():
    countries=[]