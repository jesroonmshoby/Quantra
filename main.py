import mysql.connector as mysql
from config.db_config import get_db_connection
from utils.logger import Logger

logger = Logger("quantra_db")

if __name__ == "__main__":
    conn = get_db_connection()
    print("Connection successful!" if conn else "Connection failed.")
    
