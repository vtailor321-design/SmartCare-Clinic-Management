import mysql.connector
from mysql.connector import Error
from config.database import DB_CONFIG
import logging

# Simple logging setup for DB errors
logging.basicConfig(filename='db_errors.log', level=logging.ERROR, 
                    format='%(asctime)s - %(message)s')

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG

    def get_connection(self):
        """Establishes and returns a MySQL connection."""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            return None

    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Executes a query and handles commit/rollback automatically."""
        conn = self.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            if fetch_one:
                result = cursor.fetchone()
                return result
                
            conn.commit()
            return cursor.lastrowid
            
        except Error as e:
            logging.error(f"Database Error: {e} | Query: {query}")
            conn.rollback()
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
