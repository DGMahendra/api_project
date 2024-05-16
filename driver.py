
from api_helper import APIFetch

def main():
    countries = ["india", "usa", "uk", "canada", "australia", "germany", "france", "italy", "spain", "japan", "china", "brazil", "russia", "south africa", "mexico", "south korea", "netherlands", "switzerland", "sweden", "belgium"]
    loader1=APIFetch()
    for country in countries:

        answer=loader1.fetch_data("http://universities.hipolabs.com/search?country",country)
        print(country,answer)
    loader2=APIFetch()
    for _ in range(50): 
       person=loader2.fetch_data("https://randomuser.me/api/",None)
       print(person)
if __name__=="__main__":
    main()
