import mysql.connector as mysql
from config.db_config import get_db_connection
from utils.logger import Logger
from utils.validators import validate_username
from .security import hash_password, verify_password, is_strong_password, record_failed_attempt, reset_attempts

logger = Logger()


def register_user(username: str, email: str, password: str):
    if not validate_username(username):
        print("Invalid username format.")
        logger.warning(f"Invalid username format: {username}")
        return False

    if not is_strong_password(password):
        print("Weak password. Use upper, lower, digit, and special character.")
        logger.warning(f"Weak password attempt for user {username}")
        return False

    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print("Username already exists.")
            logger.warning(f"Attempted registration with existing username: {username}")
            return False

        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_pw))
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


def login_user(username: str, email: str, password: str):
    try:
        conn, err = get_db_connection("quantra_db")
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
    logger.info(f"User logged out: {username}")
    print(f"{username} has logged out successfully.")

def get_user_details(user_id):
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT username, email, role, created_at 
            FROM users 
            WHERE id = {user_id}
        """)
        
        user_info = cursor.fetchone()
        if not user_info:
            logger.error(f"User ID {user_id} not found")
            return None
            
        # Get all accounts associated with user
        cursor.execute(f"""
            SELECT id, account_type, created_at 
            FROM accounts 
            WHERE user_id = {user_id}
        """)
        
        accounts = cursor.fetchall()
        
        user_details = {
            "user_info": {
                "username": user_info[0],
                "email": user_info[1],
                "role": user_info[2],
                "joined": user_info[3]
            },
            "accounts": accounts
        }
        
        return user_details
        
    except Exception as e:
        logger.error(f"Failed to get user details: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def update_user_details(user_id, updates):
    # Update user details (except password and role).
    try:
        allowed_fields = ["username", "email"]
        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not update_fields:
            logger.error("No valid fields to update")
            return False
            
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{field} = %s" for field in update_fields])
        values = list(update_fields.values())
        values.append(user_id)
        
        cursor.execute(f"""
            UPDATE users 
            SET {set_clause}
            WHERE id = %s
        """, values)
        
        conn.commit()
        logger.info(f"Updated details for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def change_password(user_id, old_password, new_password):
    # Change user password with verification.
    try:
        if not is_strong_password(new_password):
            logger.error("New password does not meet strength requirements")
            return False
            
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT password_hash 
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            logger.error(f"User {user_id} not found")
            return False
            
        if not verify_password(old_password, result[0]):
            logger.error("Current password is incorrect")
            return False
            
        new_hash = hash_password(new_password)
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s 
            WHERE id = %s
        """, (new_hash, user_id))
        
        conn.commit()
        logger.info(f"Password changed for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to change password for user {user_id}: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()
