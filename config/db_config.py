import mysql.connector as mysql
from utils.logger import Logger
logger = Logger()

DB_HOST = "localhost"                  
DB_USER = "root"
DB_PASSWORD = "Akshay@2008"

def get_db_connection(db_name = None):
    try:
        connection = mysql.connect(
            host = DB_HOST,
            user = DB_USER,
            password = DB_PASSWORD,
            database = db_name
        )
        return connection
    except mysql.Error as err:
        db_info = db_name if db_name else "no database selected"
        # Log the error
        logger.error(f"Error connecting to MySQL server for {db_info}: {err}", context = "Database Connection")
        print(f"Error connecting to MySQL server for {db_info}: {err}")
        return None