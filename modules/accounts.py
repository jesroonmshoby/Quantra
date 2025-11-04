from config.db_config import get_db_connection
from utils.logger import Logger
import utils.validators as validators
import core.security as security

logger = Logger()

def create_account(user_id, account_type, initial_deposit=0.0, interest_rate=None, due_date=None):
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
                INSERT INTO loan_accounts (account_id, loan_amount, interest_rate, due_date)
                VALUES (%s, %s, %s, %s)
            """, (account_id, initial_deposit, interest_rate, due_date))

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

