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

def create_account(user_id, account_type, initial_deposit=0.0, interest_rate=None):
    try:
        if not validators.validate_amount(initial_deposit):
            logger.error(f"Invalid initial deposit amount: {initial_deposit}")
            return None

        if account_type not in ["savings", "current", "loan"]:
            logger.error(f"Invalid account type: {account_type}")
            return None

        conn = get_db_connection("quantra_db")
        cursor = conn.cursor()

        # Create base account
        cursor.execute("""
            INSERT INTO accounts (user_id, account_type)
            VALUES (%s, %s)
            RETURNING id
        """, (user_id, account_type))
        
        account_id = cursor.fetchone()[0]

        # Create specific account type
        if account_type == "savings":
            cursor.execute("""
                INSERT INTO savings_accounts (account_id, balance, interest_rate)
                VALUES (%s, %s, %s) 
            """, (account_id, initial_deposit, interest_rate))

        elif account_type == "current":
            cursor.execute("""
                INSERT INTO current_accounts (account_id, balance)
                VALUES (%s, %s)
            """, (account_id, initial_deposit))

        elif account_type == "loan":
            cursor.execute("""
                INSERT INTO loan_accounts (account_id, loan_amount, interest_rate)
                VALUES (%s, %s, %s)
            """, (account_id, initial_deposit, interest_rate))

        conn.commit()
        logger.info(f"Created {account_type} account (ID: {account_id}) for user {user_id}")
        return account_id

    except Exception as e:
        logger.error(f"Failed to create {account_type} account for user {user_id}: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

def get_account_balance(account_id, account_type):
    try:
        conn = get_db_connection("quantra_db")
        cursor = conn.cursor()

        if account_type == "loan":
            cursor.execute("""
                SELECT loan_amount FROM loan_accounts 
                WHERE account_id = %s
            """, (account_id,))
        else:
            cursor.execute(f"""
                SELECT balance FROM {account_type}_accounts 
                WHERE account_id = %s
            """, (account_id,))

        result = cursor.fetchone()
        if not result:
            logger.error(f"Account {account_id} not found")
            return None

        return result[0]

    except Exception as e:
        logger.error(f"Failed to get balance for account {account_id}: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

def close_account(account_id, account_type):
    try:
        conn = get_db_connection("quantra_db")
        cursor = conn.cursor()

        # Check if account has zero balance
        balance = get_account_balance(account_id, account_type)
        if balance and balance != 0:
            logger.error(f"Cannot close account {account_id}: Balance must be zero")
            return False

        # Deletes Account
        cursor.execute("""
            DELETE FROM accounts 
            WHERE id = %s
        """, (account_id,))

        conn.commit()
        logger.info(f"Closed {account_type} account {account_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to close account {account_id}: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def create_insurance(user_id, policy_type, premium_amount, coverage_amount, premium_frequency='monthly'):
    try:
        if not validators.validate_amount(premium_amount) or not validators.validate_amount(coverage_amount):
            logger.error("Invalid premium or coverage amount")
            return None

        if premium_frequency not in ['monthly', 'quarterly', 'yearly']:
            logger.error(f"Invalid premium frequency: {premium_frequency}")
            return None

        # Calculate next premium date based on frequency
        premium_intervals = {
            'monthly': 1,
            'quarterly': 3,
            'yearly': 12
        }

        conn = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO insurance (
                user_id, 
                policy_type,
                policy_number,
                premium_amount,
                coverage_amount,
                premium_frequency,
                status,
                start_date,
                end_date,
                next_premium_due
            ) VALUES (
                %s, %s, 
                CONCAT('POL-', LPAD(LAST_INSERT_ID(), 6, '0')),
                %s, %s,
                %s,
                'active',
                CURDATE(),
                DATE_ADD(CURDATE(), INTERVAL 1 YEAR),
                DATE_ADD(CURDATE(), INTERVAL %s MONTH)
            )
            RETURNING id, policy_number
        """, (
            user_id, 
            policy_type, 
            premium_amount, 
            coverage_amount,
            premium_frequency,
            premium_intervals[premium_frequency]
        ))
        
        result = cursor.fetchone()
        if not result:
            logger.error("Failed to create insurance policy")
            return None
            
        policy_id, policy_number = result
        conn.commit()
        
        logger.info(f"Created insurance policy {policy_number} for user {user_id}")
        return policy_id

    except Exception as e:
        logger.error(f"Failed to create insurance policy for user {user_id}: {e}")
        return None

    finally:
        cursor.close()
        conn.close()