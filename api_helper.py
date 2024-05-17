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
        except Error as e:
            logging.error(f"Failed to fetch data for {url}: {e}")

    def close_connection(self):
        if self.cursor is not None and not self.cursor.closed:
            self.cursor.close()
        if self.connection is not None and self.connection.closed == 0:
            self.connection.close()

    @log_time
    def insert_data(self, data_to_insert):
        try:
            inserted_data = []
            for table_name, data_list in data_to_insert.items():
                for data in data_list:
                    if table_name == 'country':
                        country_id = self.insert_country(data['country'])
                        inserted_data.append((country_id, table_name))
                    else:
                        placeholders = ', '.join(['%s'] * len(data))
                        columns = ', '.join(data.keys())
                        values = tuple(data.values())
                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                        self.cursor.execute(query, values)
                        self.connection.commit()
                        inserted_data.append((None, table_name))
            return inserted_data
        except Error as e:
            self.connection.rollback()  # Rollback the transaction
            logging.error(f"Error while inserting data: {e}")
            return [("Error occurred", None)]
        except psycopg2.InterfaceError as e:
            logging.error(f"InterfaceError occurred: {e}")
            return [("InterfaceError occurred", None)]
        finally:
            if self.cursor is not None and not self.cursor.closed:
                self.cursor.close()     # Close the cursor if it's not already closed
            if self.connection is not None and self.connection.closed == 0:
                self.connection.close() # Close the connection if it's not already closed
    @log_time
    def insert_country(self, country_name):
        try:
            query = "INSERT INTO country (country_name) VALUES (%s) ON CONFLICT DO NOTHING RETURNING country_id"
            self.cursor.execute(query, (country_name,))
            country_id = self.cursor.fetchone()[0]
            return country_id
        except Error as e:
            logging.error("Error while inserting country", e)
            return None

    