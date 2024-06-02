
import time
import logging
import psycopg2
import requests
from psycopg2 import Error
import json

def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds to complete.")
        return result
    return wrapper

class DataHandler:
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
                        self._insert_generic("country", {"name": country}, "name")
                elif table_name == "university":
                    for country, universities in data.items():
                        country_id = self._insert_generic("country", {"name": country}, "name")
                        for university in universities:
                            university_data = {
                                "name": university['name'],
                                "alpha_two_code": university.get('alpha_two_code'),
                                "state_province": university.get('state-province'),
                                "domains": json.dumps(university.get('domains')),
                                "web_pages": json.dumps(university.get('web_pages')),
                                "country_id": country_id
                            }
                            self._insert_generic("university", university_data, ["name", "country_id"])
                elif table_name == "person":
                    for person_data in data:
                        flattened_data = self._flatten_person_data(person_data)
                        # Check if the username already exists
                        existing_username = self._check_existing_username(flattened_data['username'])
                        if existing_username:
                            logging.warning(f"Skipping insertion for user with existing username: {flattened_data['username']}")
                            continue
                        location_id = self._insert_generic("location", flattened_data['location'], ["street", "city", "state", "country", "postcode"])
                        if location_id:
                            flattened_data['location_id'] = location_id
                            self._remove_keys(flattened_data, ["location"])
                            self._insert_generic("users", flattened_data, "email")
            yield "Data insertion completed."
        except Error as e:
            self.connection.rollback()  # Rollback the transaction
            logging.error(f"Error while inserting data: {e}")
            yield f"Error occurred: {e}"
        except psycopg2.InterfaceError as e:
            logging.error(f"InterfaceError occurred: {e}")

    def _check_existing_username(self, username):
        query = "SELECT COUNT(*) FROM users WHERE username = %s"
        self.cursor.execute(query, (username,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def _insert_generic(self, table_name, data, unique_columns):
        try:
            columns = data.keys()
            values = tuple(data.values())
            placeholders = ', '.join(['%s'] * len(values))
            unique_columns = [unique_columns] if isinstance(unique_columns, str) else unique_columns
            conflict_clause = ', '.join(unique_columns)
            update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns])
            query = f"""
                INSERT INTO {table_name} ({', '.join(columns)}) 
                VALUES ({placeholders}) 
                ON CONFLICT ({conflict_clause}) 
                DO UPDATE SET {update_clause} 
                RETURNING {table_name}_id
            """
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
        location = person_data['location']
        flattened = {
            "gender": person_data['gender'],
            "title": person_data['name']['title'],
            "first_name": person_data['name']['first'],
            "last_name": person_data['name']['last'],
            "email": person_data['email'],
            "username": person_data['login']['username'],
            "password": person_data['login']['password'],
            "date_of_birth": person_data['dob']['date'],
            "registered_date": person_data['registered']['date'],
            "phone": person_data['phone'],
            "cell": person_data['cell'],
            "nationality": person_data['nat'],
            "picture_large": person_data['picture']['large'],
            "picture_medium": person_data['picture']['medium'],
            "picture_thumbnail": person_data['picture']['thumbnail'],
            "location": {
                "street": location['street']['name'],
                "city": location['city'],
                "state": location['state'],
                "country": location['country'],
                "postcode": location['postcode'],
                "latitude": location['coordinates']['latitude'],
                "longitude": location['coordinates']['longitude'],
                "timezone_offset": location['timezone']['offset'],
                "timezone_description": location['timezone']['description']
            }
        }
        return flattened

    def _remove_keys(self, data_dict, keys):
        for key in keys:
            if key in data_dict:
                del data_dict[key]
