import mysql.connector as mysql
from datetime import datetime
from config.db_config import get_db_connection

LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}

CURRENT_LOG_LEVEL = LOG_LEVELS["DEBUG"]

class Logger:
    def __init__(self, db_name="quantra_db"):
        self.db_name = db_name

    # User Logs
    def log_action(self, user_id, action):
        try:
            conn = get_db_connection(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO audit_logs (user_id, action) VALUES ({user_id}, {action})"
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.Error as err:
            print(f"Failed to log user action: {err}")

    # System Logs
    def log_system(self, level, message, context=None):
        if LOG_LEVELS.get(level, 0) < CURRENT_LOG_LEVEL:
            return  # skip logs below threshold

        try:
            conn = get_db_connection(self.db_name)
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                f"""
                INSERT INTO system_logs (level, message, context, created_at)
                VALUES ({level}, {message}, {context}, {timestamp})
                """
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.Error as err:
            print(f"Failed to log system event: {err}")

    # Log each level for convenience
    
    def debug(self, message, context=None):
        self.log_system("DEBUG", message, context)

    def info(self, message, context=None):
        self.log_system("INFO", message, context)

    def warning(self, message, context=None):
        self.log_system("WARNING", message, context)

    def error(self, message, context=None):
        self.log_system("ERROR", message, context)

    def critical(self, message, context=None):
        self.log_system("CRITICAL", message, context)

print("Logger module loaded.")