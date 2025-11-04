import core.security as security
import core.roles as roles
import utils.validators as validators
from config.db_config import get_db_connection
import utils.logger as logger

from modules.accounts import create_account
from utils.logger import Logger

logger = Logger()

def apply_for_loan(user_id, amount, interest_rate, due_date, purpose=None):
    """
    Applies for a loan by creating a loan account.

    Args:
        user_id (int): The ID of the user applying for the loan.
        amount (float): The loan amount.
        interest_rate (float): The interest rate for the loan.
        due_date (str): The due date for the loan in 'YYYY-MM-DD' format.
        purpose (str, optional): The purpose of the loan. Defaults to None.

    Returns:
        int: The account ID of the newly created loan account, or None if it fails.
    """
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
        if purpose:
            # In the future, you might want to store the loan purpose in a separate table.
            logger.info(f"Loan purpose: {purpose}")
    else:
        logger.error(f"Loan application failed for user {user_id}.")
        
    return loan_account_id
