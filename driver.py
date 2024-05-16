
from api_helper import APIFetch
# class PersonDataFetcher():

#     def fetch_data(self):
#         for _ in range(5000): 
#             response = requests.get("https://randomuser.me/api/")
#             if response.status_code == 200:
#                 persons = response.json()['results']
#                 print(persons)
#             else:
#                 logging.error("Failed to fetch data for persons")

def main():
    # countries = ["india", "usa", "uk", "canada", "australia", "germany", "france", "italy", "spain", "japan", "china", "brazil", "russia", "south africa", "mexico", "south korea", "netherlands", "switzerland", "sweden", "belgium"]
    # loader1=APIFetch()
    # for country in countries:
    #     url=f"http://universities.hipolabs.com/search?country={country}"
    #     loader1.fetch_data(url,country)
    loader2=APIFetch()
    loader2.fetch_data("https://randomuser.me/api/",None)
if __name__=="__main__":
    main()
