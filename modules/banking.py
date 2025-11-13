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
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        # Verify ownership of from_account_id
        cursor.execute(
            f"SELECT id FROM accounts WHERE id = {from_account_id} AND user_id = {user_id}",
        )
        if not cursor.fetchone():
            logger.error(
                f"Transfer failed: User {user_id} does not own Account #{from_account_id}",
                context="banking:process_immediate_transfer"
            )
            return False
        
        # Verify Account isnt Loan Account For Both Accounts
        cursor.execute(
            f"SELECT account_type FROM accounts WHERE id = {from_account_id}",
        )
        account_type = cursor.fetchone()[0]
        if account_type == "loan":
            logger.error(
                f"Transfer failed: Cannot transfer from Loan Account #{from_account_id}",
                context="banking:process_immediate_transfer"
            )
            return False
        
        cursor.execute(
            f"SELECT account_type FROM accounts WHERE id = {to_account_id}",
        )
        account_type = cursor.fetchone()[0]
        if account_type == "loan":
            logger.error(
                f"Transfer failed: Cannot transfer to Loan Account #{to_account_id}",
                context="banking:process_immediate_transfer"
            )
            return False
        


        # Check sufficient funds
        cursor.execute(
            f"SELECT balance FROM current_accounts WHERE account_id = {from_account_id}",
        )
        balance = cursor.fetchone()[0]

        if balance < amount:
            logger.warning(
                f"Insufficient funds in Account #{from_account_id}",
                context="banking:process_immediate_transfer"
            )
            return False

        # Process transfer
        cursor.execute(
            f"UPDATE current_accounts SET balance = balance - {amount} WHERE account_id = {from_account_id}",
        )
        cursor.execute(
            f"UPDATE current_accounts SET balance = balance + {amount} WHERE account_id = {to_account_id}",
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(
            f"Transferred {format_currency(amount)} from Account #{from_account_id} to #{to_account_id}",
            context="banking:process_immediate_transfer"
        )
        return True

    except Exception as err:
        logger.error(
            f"Transfer failed: {err}",
            context="banking:process_immediate_transfer"
        )
        return False