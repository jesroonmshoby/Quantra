from config.db_config import get_db_connection
from utils.logger import Logger
import utils.validators as validators 

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
def withdraw(user_id, account_id, amount):
    if not validators.validate_amount(amount):
        logger.error(f"Withdrawal failed for user {user_id}: Invalid amount {amount}")
        return False

    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        # check if current account exists
        cursor.execute("SELECT id FROM accounts WHERE id = %s AND user_id = %s", (account_id, user_id))
        if not cursor.fetchone():
            logger.error(f"Deposit failed for user {user_id}: Account not found")
            return False

        # Check balance
        cursor.execute("SELECT balance FROM current_accounts WHERE account_id = %s", (account_id, ))
        result = cursor.fetchone()
        if not result:
            logger.error(f"Withdrawal failed for user {user_id}: Account not found")
            return False

        balance = result[0]
        if balance < amount:
            logger.error(f"Withdrawal failed for user {user_id}: Insufficient funds")
            return False

        # Deduct balance
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