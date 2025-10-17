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
    
def authenticate_user(email, password):
    try:
        conn = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT id, password_hash, role, locked FROM users WHERE email = {email}")
        result = cursor.fetchone()
        if not result:
            logger.error(f"Email {email} not found.")
            return None
        user_id, stored_hashed_password, role, locked = result
        if locked:
            logger.error(f"Account with email {email} is locked.")
            return None
        if not security.verify_password(password, stored_hashed_password):
            logger.error(f"Incorrect password for email {email}.")
            return None

        cursor.close()
        conn.close()
        logger.info(f"User with email {email} authenticated successfully.")
        return {"user_id": user_id, "role": role}
    except Exception as e:
        logger.error(f"Authentication failed for email {email}: {e}")
        return None
    
def get_user_details(user_id):
    try:
        conn = get_db_connection("quantra_db")
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
            
        conn = get_db_connection("quantra_db")
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
        if not security.is_strong_password(new_password):
            logger.error("New password does not meet strength requirements")
            return False
            
        conn = get_db_connection("quantra_db")
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
            
        if not security.verify_password(old_password, result[0]):
            logger.error("Current password is incorrect")
            return False
            
        new_hash = security.hash_password(new_password)
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

    
