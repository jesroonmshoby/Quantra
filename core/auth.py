import mysql.connector as mysql
from utils import validators, helpers, logger
from config.db_config import get_db_connetion
from utils.logger import Logger
from utils.validators import validate_username
from security import hash_password, verify_password, is_strong_password, record_failed_attempt, reset_attempts

logger = Logger()


def register_user(username: str, password: str):
    """Register a new user after validation and password hashing."""
    if not validate_username(username):
        print("Invalid username format.")
        logger.warning(f"Invalid username format: {username}")
        return False

    if not is_strong_password(password):
        print("Weak password. Use upper, lower, digit, and special character.")
        logger.warning(f"Weak password attempt for user {username}")
        return False

    try:
        conn = db_config.get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print("Username already exists.")
            logger.warning(f"Attempted registration with existing username: {username}")
            return False

        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        conn.commit()

        print("User registered successfully.")
        logger.info(f"New user registered: {username}")
        return True

    except mysql.Error as err:
        print("Database error during registration.")
        logger.error(f"Registration failed for {username}: {err}")
        return False

    finally:
        cursor.close()
        conn.close()


def login_user(username: str, password: str):
    """Authenticate user with password verification."""
    try:
        conn = db_config.get_db_connection("quantra_db")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            print("User not found.")
            logger.warning(f"Login failed: {username} not found.")
            return False

        if user.get("locked"):
            print("Account is locked. Contact admin.")
            logger.warning(f"Login attempt on locked account: {username}")
            return False

        if verify_password(password, user["password"]):
            print("Login successful!")
            logger.info(f"User logged in: {username}")
            reset_attempts(username)
            return True
        else:
            print("Incorrect password.")
            logger.warning(f"Incorrect password for {username}")
            record_failed_attempt(username)
            return False

    except mysql.Error as err:
        print("Database error during login.")
        logger.error(f"Login failed for {username}: {err}")
        return False

    finally:
        cursor.close()
        conn.close()


def logout_user(username: str):
    """Logout action with simple logging."""
    logger.info(f"User logged out: {username}")
    print(f"{username} has logged out successfully.")
