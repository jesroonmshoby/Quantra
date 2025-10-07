import mysql.connector as mysql
import hashlib
import time
from config import db_config
from utils.logger import Logger
logger = Logger()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str):
    return hash_password(password) == hashed

def is_strong_password(password: str):
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    if not (has_upper and has_lower and has_digit and has_special):
        return False
    return True

def lock_account(username):
    try: 
        conn = db_config.get_db_connection("quantra_db")
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET locked = TRUE WHERE username = {username}")
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.error as err:
        logger.error(f"Failed to lock account {username}: {err}")
        
def unlock_account(username):
    try:
        conn = db_config.get_db_connection("quantra_db")
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET locked = FALSE WHERE username = {username}")
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Account {username} unlocked by manager/admin.")
    except mysql.Error as err:
        logger.error(f"Failed to unlock account {username}: {err}")

max_login_attempts = 3
login_attempts = {}

def record_failed_attempt(username):
    login_attempts[username] = login_attempts.get(username, 0) + 1
    logger.warning(f"Failed login attempt {login_attempts[username]} for user {username}")
    if login_attempts[username] >= max_login_attempts:
        lock_account(username)
        print("Account temporarily locked due to too many failed logins.")
        logger.critical(f"Account {username} locked due to too many failed login attempts.")
        return True
    return False

def reset_attempts(username):
    if username in login_attempts:
        del login_attempts[username]
        logger.debug(f"Login attempts reset for '{username}'")

