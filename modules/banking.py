from config.db_config import get_db_connection
from utils.logger import Logger
import utils.validators as validators 
from utils.helpers import format_currency

logger = Logger()


# Deposit function
def deposit(user_id, account_id, amount):
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        if not validators.validate_amount(amount):
            logger.error(f"Deposit failed for user {user_id}: Invalid amount {amount}")
            return False
        
        # check if current account exists
        cursor.execute("SELECT id FROM accounts WHERE id = %s AND user_id = %s", (account_id, user_id))
        if not cursor.fetchone():
            logger.error(f"Deposit failed for user {user_id}: Account not found")
            return False
        
        # Update account balance
        cursor.execute(
            "UPDATE current_accounts SET balance = balance + %s WHERE account_id = %s",
            (amount, account_id)
        )

        if cursor.rowcount == 0:
            logger.error(f"Deposit failed for user {user_id}: Account not found")
            return False

        conn.commit()

        # Log transaction
        logger.log_transaction(user_id, account_id, amount, 'credit')
        logger.info(f"User {user_id} deposited {amount} into account {account_id}")
        return True

    except Exception as e:
        logger.error(f"Deposit failed for user {user_id}: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


# Withdraw function
def withdraw(user_id, account_id, amount, account_type):
    if not validators.validate_amount(amount):
        logger.error(f"Withdrawal failed for user {user_id}: Invalid amount {amount}")
        return False

    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        # check if account exists
        if account_type in ["savings", "current"]:
            cursor.execute("SELECT id FROM accounts WHERE id = %s AND user_id = %s", (account_id, user_id))
            if not cursor.fetchone():
                logger.error(f"Deposit failed for user {user_id}: Account not found")
                return False
            
        else:
            # Check if account type is valid
            if account_type not in ["savings", "current", "loan"]:
                logger.error(f"Withdrawal failed for user {user_id}: Invalid account type {account_type}")
                return False
            
            else:
                print("Withdrawals can only be made from savings or current accounts.")
                logger.error(f"Withdrawal failed for user {user_id}: Invalid account type {account_type}")
                return False
            

        # Check balance
        if account_type == "savings":
            cursor.execute("SELECT balance FROM savings_accounts WHERE account_id = %s", (account_id,))
        elif account_type == "current":
            cursor.execute("SELECT balance FROM current_accounts WHERE account_id = %s", (account_id,))
        result = cursor.fetchone()
        if not result:
            logger.error(f"Withdrawal failed for user {user_id}: Account not found")
            return False

        balance = result[0]
        if balance < amount:
            logger.error(f"Withdrawal failed for user {user_id}: Insufficient funds")
            return False

        # Deduct balance
        if account_type == "savings":
            cursor.execute(
                "UPDATE savings_accounts SET balance = balance - %s WHERE account_id = %s",
                (amount, account_id)
            )
        elif account_type == "current":
            cursor.execute(
                "UPDATE current_accounts SET balance = balance - %s WHERE account_id = %s",
                (amount, account_id)
            )
        conn.commit()

        # Log transaction
        logger.log_transaction(user_id, account_id, amount, 'debit')
        logger.info(f"User {user_id} withdrew {amount} from account {account_id}")
        return True

    except Exception as e:
        logger.error(f"Withdrawal failed for user {user_id}: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()
    
def process_immediate_transfer(user_id, from_account_id, to_account_id, amount):
    conn = None
    cursor = None
    
    try:
        if not validators.validate_amount(amount):
            logger.error(
                f"Transfer failed: Invalid amount {amount}",
                context="banking:process_immediate_transfer"
            )
            return False
        
        conn, err = get_db_connection("quantra_db")
        if err or not conn:
            logger.error(f"Database connection failed: {err}")
            return False
        
        cursor = conn.cursor(dictionary=True)

        # Verify ownership of from_account_id
        cursor.execute(
            "SELECT id, account_type FROM accounts WHERE id = %s AND user_id = %s",
            (from_account_id, user_id)
        )
        from_account = cursor.fetchone()
        
        if not from_account:
            logger.error(
                f"Transfer failed: User {user_id} does not own Account #{from_account_id}",
                context="banking:process_immediate_transfer"
            )
            return False
        
        # Verify from_account is not a loan account
        if from_account['account_type'] == "loan":
            logger.error(
                f"Transfer failed: Cannot transfer from Loan Account #{from_account_id}",
                context="banking:process_immediate_transfer"
            )
            return False
        
        # Get to_account details and verify it exists
        cursor.execute(
            "SELECT user_id, account_type FROM accounts WHERE id = %s",
            (to_account_id,)
        )
        to_account = cursor.fetchone()
        
        if not to_account:
            logger.error(
                f"Transfer failed: Destination Account #{to_account_id} not found",
                context="banking:process_immediate_transfer"
            )
            return False
        
        to_user_id = to_account['user_id']
        
        # Verify to_account is not a loan account
        if to_account['account_type'] == "loan":
            logger.error(
                f"Transfer failed: Cannot transfer to Loan Account #{to_account_id}",
                context="banking:process_immediate_transfer"
            )
            return False

        # Determine table names based on account types
        from_table = f"{from_account['account_type']}_accounts"
        to_table = f"{to_account['account_type']}_accounts"

        # Check sufficient funds
        cursor.execute(
            f"SELECT balance FROM {from_table} WHERE account_id = %s",
            (from_account_id,)
        )
        balance_result = cursor.fetchone()
        
        if not balance_result:
            logger.error(
                f"Transfer failed: Account #{from_account_id} not found in {from_table}",
                context="banking:process_immediate_transfer"
            )
            return False
        
        balance = float(balance_result['balance'])

        if balance < amount:
            logger.warning(
                f"Insufficient funds in Account #{from_account_id}. Balance: {format_currency(balance)}, Required: {format_currency(amount)}",
                context="banking:process_immediate_transfer"
            )
            return False

        # Process transfer - debit from source
        cursor.execute(
            f"UPDATE {from_table} SET balance = balance - %s WHERE account_id = %s",
            (amount, from_account_id)
        )
        
        # Credit to destination
        cursor.execute(
            f"UPDATE {to_table} SET balance = balance + %s WHERE account_id = %s",
            (amount, to_account_id)
        )

        # Log debit transaction for sender
        cursor.execute("""
            INSERT INTO transactions (user_id, account_id, amount, transaction_type)
            VALUES (%s, %s, %s, 'debit')
        """, (user_id, from_account_id, amount))
        debit_transaction_id = cursor.lastrowid

        # Log credit transaction for receiver
        cursor.execute("""
            INSERT INTO transactions (user_id, account_id, amount, transaction_type)
            VALUES (%s, %s, %s, 'credit')
        """, (to_user_id, to_account_id, amount))
        credit_transaction_id = cursor.lastrowid

        conn.commit()

        logger.info(
            f"Transferred {format_currency(amount)} from Account #{from_account_id} (User {user_id}) to Account #{to_account_id} (User {to_user_id})",
            context="banking:process_immediate_transfer"
        )
        return True

    except Exception as err:
        logger.error(
            f"Transfer failed: {err}",
            context="banking:process_immediate_transfer"
        )
        if conn:
            conn.rollback()
        return False
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_transaction_history(user_id, account_id):
    try:
        conn, err = get_db_connection("quantra_db")
        if err or not conn:
            logger.error(f"Database connection failed: {err}")
            return None
        cursor = conn.cursor(dictionary=True)

        # Verify ownership of account_id
        cursor.execute(
            "SELECT id FROM accounts WHERE id = %s AND user_id = %s",
            (account_id, user_id)
        )
        account = cursor.fetchone()
        
        if not account:
            logger.error(f"Transaction history retrieval failed: User {user_id} does not own Account #{account_id}")
            return None

        # Fetch transaction history
        cursor.execute("""
            SELECT id, amount, transaction_type, created_at 
            FROM transactions 
            WHERE account_id = %s 
            ORDER BY created_at DESC 
        """, (account_id,))
        
        transactions = cursor.fetchall()
        return transactions

    except Exception as err:
        logger.error(f"Transaction history retrieval failed for User {user_id}, Account #{account_id}: {err}")
        return None

    finally:
        cursor.close()
        conn.close()

