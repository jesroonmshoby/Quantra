import mysql.connector as mysql
from config.db_config import get_db_connection

def run_migrations():
    try:

        # Connect without specifying a database to create it if it doesn't exist
        connection = get_db_connection()
        if connection is None:
            print("Failed to connect to the database.")
            return

        cursor = connection.cursor()

        # Open and Read Schema.sql
        with open('database/Schema.sql', 'r') as file:
            schema_sql = file.read().split(';')

        # Execute each statement in the schema file
        for query in schema_sql:
            query = query.strip()
            if query:
                cursor.execute(query)

        connection.commit()
        print("✅ Database and tables migrated successfully.")

    except mysql.Error as err:
        print(f"❌ Migration failed: {err}")
        return
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# To run the migrations when this script is only executed directly
if __name__ == "__main__":
    run_migrations()