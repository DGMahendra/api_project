import time
import logging
import psycopg2
import requests
from psycopg2 import Error

def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time} seconds to complete.")
        return result
    return wrapper

class APIFetch:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    @log_time
    def fetch_data(self, url, country=None):
        try:
            if country is not None:
                url = url + f"?country={country}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to fetch data for {url}: {e}")
            return None

    def close_connection(self):
        if self.cursor is not None and not self.cursor.closed:
            self.cursor.close()
        if self.connection is not None and self.connection.closed == 0:
            self.connection.close()

    @log_time
    def insert_data(self, data_to_insert):
        try:
            for table_name, data in data_to_insert.items():
                if table_name == "country":
                    for country in data:
                        self._insert_country(country)
                elif table_name == "university":
                    for country, universities in data.items():
                        country_id = self._insert_country(country)
                        for university in universities:
                            university_name = university['name']
                            self._insert_university(university_name, country_id)
                elif table_name == "person":
                    for person_data in data:
                        country = person_data['location']['country']
                        country_id = self._insert_country(country)
                        self._insert_person(person_data, country_id)
            yield "Data insertion completed."
        except Error as e:
            self.connection.rollback()  # Rollback the transaction
            logging.error(f"Error while inserting data: {e}")
            yield f"Error occurred: {e}"
        except psycopg2.InterfaceError as e:
            logging.error(f"InterfaceError occurred: {e}")

    def _insert_country(self, country_name):
        try:
            query = "INSERT INTO country (country_name) VALUES (%s) ON CONFLICT (country_name) DO NOTHING RETURNING country_id"
            self.cursor.execute(query, (country_name,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                query = "SELECT country_id FROM country WHERE country_name = %s"
                self.cursor.execute(query, (country_name,))
                return self.cursor.fetchone()[0]
        except Error as e:
            self.connection.rollback()
            logging.error(f"Error while inserting country: {e}")
            return None

    def _insert_university(self, university_name, country_id):
        try:
            query = "INSERT INTO university (university_name, country_id) VALUES (%s, %s) ON CONFLICT DO NOTHING"
            self.cursor.execute(query, (university_name, country_id))
            self.connection.commit()
            logging.info(f"Inserted university: {university_name}")
        except Error as e:
            self.connection.rollback()
            logging.error(f"Error while inserting university: {e}")

    def _insert_person(self, person_data, country_id):
        try:
            query = """
            INSERT INTO person (first_name, last_name, email, gender, country_id)
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
            """
            self.cursor.execute(query, (
                person_data['name']['first'],
                person_data['name']['last'],
                person_data['email'],
                person_data['gender'],
                country_id
            ))
            self.connection.commit()
            logging.info(f"Inserted person: {person_data['name']['first']} {person_data['name']['last']}")
        except Error as e:
            self.connection.rollback()
            logging.error(f"Error while inserting person: {e}")

