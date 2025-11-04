import core.security as security
import core.roles as roles
import utils.validators as validators
from config.db_config import get_db_connection

from modules.accounts import create_account
from utils.logger import Logger

logger = Logger()

def apply_for_loan(user_id, amount, interest_rate, due_date):
    logger.info(f"Processing loan application for user {user_id} for amount {amount}.")
    
    loan_account_id = create_account(
        user_id=user_id,
        account_type='loan',
        initial_deposit=amount,
        interest_rate=interest_rate,
        due_date=due_date
    )
    
    if loan_account_id:
        logger.info(f"Loan application successful for user {user_id}. Loan account ID: {loan_account_id}")
    else:
        logger.error(f"Loan application failed for user {user_id}.")
        
    return loan_account_id


