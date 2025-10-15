from config.db_config import get_db_connection
from utils.logger import Logger
import utils.validators as validators
import core.security as security

logger = Logger()

def create_user(username, email, password):
    # Manager and Admin roles should be created directly in the database by authorized personnel using SQL commands
    try:
        if not validators.validate_username(username):
            logger.error("Invalid username format.")
            return None
        if not validators.validate_email(email):
            logger.error("Invalid email format.")
            return None
        if not security.is_strong_password(password):
            logger.error("Password does not meet strength requirements.")
            return None

        
        conn = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT id FROM users WHERE email = {email}")
        if cursor.fetchone():
            logger.error(f"Email {email} already exists.")
            return None

        hashed_password = security.hash_password(password)

        cursor.execute(f"""
            INSERT INTO users (username, email, password, role, locked)
            VALUES ({username}, {email}, {hashed_password}, 'User', FALSE)
            RETURNING id
        """)
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"User {username} created with ID {user_id}.")
        return user_id
    except Exception as e:
        logger.error(f"Failed to create user {username}: {e}")
        return None
    

    
