from config.db_config import get_db_connection
from utils.logger import Logger
import utils.validators as validators
import core.security as security

logger = Logger()

def create_account(user_id, account_type, initial_deposit=0.0, interest_rate=None, due_date=None):
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        if not validators.validate_amount(initial_deposit):
            logger.error(f"Invalid initial deposit amount: {initial_deposit}")
            print("Invalid initial deposit amount: {}".format(initial_deposit))
            return None

        if account_type not in ["savings", "current", "loan"]:
            logger.error(f"Invalid account type: {account_type}")
            print("Invalid account type: {}".format(account_type))
            return None
        
        if account_type == "loan":
            if not due_date:
                logger.error(f"Due date is required for loan accounts")
                print("Due date is required for loan accounts")
                return None
            if interest_rate is None:
                logger.error(f"Interest rate is required for loan accounts")
                print("Interest rate is required for loan accounts")
                return None

        # Create base account
        cursor.execute("""
            INSERT INTO accounts (user_id, account_type)
            VALUES (%s, %s)
        """, (user_id, account_type))
        
        account_id = cursor.lastrowid

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
        conn, err = get_db_connection("quantra_db")
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
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        # Check if account has zero balance
        balance = get_account_balance(account_id, account_type)
        if balance and balance != 0:
            logger.error(f"Cannot close account {account_id}: Balance must be zero")
            return False
        
        # Delete Nessecary Records from Transaction Table
        cursor.execute("""
            DELETE FROM transactions 
            WHERE account_id = %s
        """, (account_id,))

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

def get_account_details(user_id):

    try:
        # Get database connection
        conn, err = get_db_connection("quantra_db")
        if err or not conn:
            logger.error(f"Database connection failed: {err}")
            conn, cursor = None, None
            return None
        
        cursor = conn.cursor(dictionary=True)
        
        # Get all accounts for the user
        cursor.execute("""
            SELECT id, account_type, created_at
            FROM accounts
            WHERE user_id = %s
        """, (user_id,))
        
        accounts = cursor.fetchall()
        
        if not accounts:
            logger.info(f"No accounts found for user {user_id}")
            return []
        
        # Fetch specific details for each account based on type
        detailed_accounts = []
        
        for account in accounts:
            account_id = account['id']
            account_type = account['account_type']
            
            account_details = {
                'account_id': account_id,
                'account_type': account_type,
                'created_at': account['created_at']
            }
            
            # Fetch type-specific details
            if account_type == 'savings':
                cursor.execute("""
                    SELECT balance, interest_rate
                    FROM savings_accounts
                    WHERE account_id = %s
                """, (account_id,))
                savings_data = cursor.fetchone()
                
                if savings_data:
                    account_details['balance'] = float(savings_data['balance'])
                    account_details['interest_rate'] = float(savings_data['interest_rate'])
            
            elif account_type == 'current':
                cursor.execute("""
                    SELECT balance, overdraft_limit
                    FROM current_accounts
                    WHERE account_id = %s
                """, (account_id,))
                current_data = cursor.fetchone()
                
                if current_data:
                    account_details['balance'] = float(current_data['balance'])
                    account_details['overdraft_limit'] = float(current_data['overdraft_limit'])
            
            elif account_type == 'loan':
                cursor.execute("""
                    SELECT loan_amount, interest_rate, due_date
                    FROM loan_accounts
                    WHERE account_id = %s
                """, (account_id,))
                loan_data = cursor.fetchone()
                
                if loan_data:
                    account_details['loan_amount'] = float(loan_data['loan_amount'])
                    account_details['interest_rate'] = float(loan_data['interest_rate'])
                    account_details['due_date'] = loan_data['due_date']
            
            detailed_accounts.append(account_details)
        
        logger.info(f"Retrieved {len(detailed_accounts)} account(s) for user {user_id}")
        return detailed_accounts
    
    except Exception as e:
        logger.error(f"Failed to get account details for user {user_id}: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()