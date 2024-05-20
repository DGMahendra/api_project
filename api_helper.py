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
        if self.connection is not None and  self.connection.closed == 0:
            self.connection.close()

    @log_time
    def insert_data(self, data_to_insert):
        try:
            for table_name, data in data_to_insert.items():
                if table_name == "country":
                    for country in data:
                        self._insert_generic("country", {"country_name": country})
                elif table_name == "university":
                    for country, universities in data.items():
                        country_id = self._insert_generic("country", {"country_name": country})
                        for university in universities:
                            university_data = {
                                "university_name": university['name'],
                                "country_id": country_id
                            }
                            self._insert_generic("university", university_data)
                elif table_name == "person":
                    for person_data in data:
                        flattened_data = self._flatten_person_data(person_data)
                        country = flattened_data['country']
                        country_id = self._insert_generic("country", {"country_name": country})
                        flattened_data['country_id'] = country_id
                        del flattened_data['country']
                        self._insert_generic("person", flattened_data)
            yield "Data insertion completed."
        except Error as e:
            self.connection.rollback()  # Rollback the transaction
            logging.error(f"Error while inserting data: {e}")
            yield f"Error occurred: {e}"
        except psycopg2.InterfaceError as e:
            logging.error(f"InterfaceError occurred: {e}")

    def _insert_generic(self, table_name, data):
        try:
            columns = data.keys()
            values = tuple(data.values())
            placeholders = ', '.join(['%s'] * len(values))
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING RETURNING {table_name}_id"
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            self.connection.commit()
            if result:
                return result[0]
            else:
                select_query = f"SELECT {table_name}_id FROM {table_name} WHERE " + " AND ".join([f"{col} = %s" for col in columns])
                self.cursor.execute(select_query, values)
                return self.cursor.fetchone()[0]
        except Error as e:
            self.connection.rollback()
            logging.error(f"Error while inserting into {table_name}: {e}")
            return None

    def _flatten_person_data(self, person_data):
        flattened = {
            "first_name": person_data['name']['first'],
            "last_name": person_data['name']['last'],
            "email": person_data['email'],
            "gender": person_data['gender'],
            "country": person_data['location']['country']
        }
        return flattened
