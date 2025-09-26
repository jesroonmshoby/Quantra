import mysql.connector as mysql

DB_HOST = "localhost"                  
DB_USER = "root"
DB_PASSWORD = "Akshay@2008"

def get_db_connection(db_name):
    try:
        connection = mysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=db_name
        )
        return connection
    except mysql.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None