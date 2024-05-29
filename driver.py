import logging
import psycopg2
from api_helper import DataHandler

def main():
    connection = psycopg2.connect(database="api_db2", user="postgres", password="Password@186", host="localhost", port="5432")
    cursor = connection.cursor()

    loader = DataHandler(connection, cursor)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    countries = ["india", "usa", "uk", "canada", "australia", "germany", "france", "italy", "spain", "japan", "china", "brazil", "russia", "south africa", "mexico", "south korea", "netherlands", "switzerland", "sweden", "belgium"]
    
    data_to_insert = {"country": countries}
    inserted_country_data = loader.insert_data(data_to_insert)

    for log_message in inserted_country_data:
        logging.info(log_message)
    
    universities_data = {}
    for country in countries:
        university_data = loader.fetch_data("http://universities.hipolabs.com/search", country)
        if university_data:
            universities_data[country] = university_data
    
    data_to_insert["university"] = universities_data
    inserted_university_data = loader.insert_data(data_to_insert)

    for log_message in inserted_university_data:
        logging.info(log_message)

    persons_data = loader.fetch_data("https://randomuser.me/api/?results=5000")
    
    if persons_data and 'results' in persons_data:
        data_to_insert["person"] = persons_data['results']
        inserted_person_data = loader.insert_data(data_to_insert)

        for log_message in inserted_person_data:
            logging.info(log_message)

    loader.close_connection()

if __name__ == "__main__":
    main()
