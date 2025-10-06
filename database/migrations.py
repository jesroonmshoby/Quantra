import mysql.connector as mysql
from config.db_config import get_db_connection
from utils.logger import Logger

logger = Logger("quantra_db")

conn, err = get_db_connection()
if conn is None:
    db_info = "no database selected"
    # Log the error
    logger.error(f"Error connecting to MySQL server for {db_info}: {err}", context = "Database Connection")
    print(f"Error connecting to MySQL server for {db_info}: {err}")

def run_migrations():
    logger.info("Migration process started", context="Migrations")
    connection = None
    cursor = None

    try:

        # Connect without specifying a database to create it if it doesn't exist
        connection = get_db_connection()
        if connection is None:
            print("Failed to connect to the database.")
            return

        cursor = connection.cursor()

        # Open and Read Schema.sql
        with open('./database/Schema.sql', 'r') as file:
            schema_sql = file.read().split(';')

        # Execute each statement in the schema file
        for query in schema_sql:
            query = query.strip()
            if query:
                cursor.execute(query)
                logger.debug(f"Executed query: {query}", context="Migrations")

        connection.commit()
        logger.info("Migration of 'Schema.sql' applied successfully", context="Migrations")
        print("Database and tables migrated successfully.")

    except mysql.Error as err:
        logger.error(f"SQL execution failed on query: {query[:50]}... Error: {err}", context="Migrations")
        print(f"Migration failed: {err}")
        return
    
    except FileNotFoundError as fe:
        logger.error(f"Schema file not found: {fe}", context="Migrations")
        print(f"Schema file not found: {fe}")
        return
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# To run the migrations when this script is only executed directly
if __name__ == "__main__":
    run_migrations()