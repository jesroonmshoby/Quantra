from config.db_config import get_db_connection
from utils.logger import Logger
logger = Logger()
from modules import accounts, insurance, loans, banking

def print_account_report(user_id):

    detailled_accounts = accounts.get_account_details(user_id)
    if not detailled_accounts:
        logger.error(f"Failed to retrieve account details for user ID {user_id}")
        print("No account details found.")
        return
    
    print("\nAccount Report:")
    for account in detailled_accounts:
        if account['account_type'] == 'savings':
            print(f"  Savings Account ID: {account['account_id']}")
            print(f"  Balance: {account['balance']}")
            print(f"  Created At: {account['created_at']}") 
            print(f"  Interest Rate: {account['interest_rate']}%\n")

        elif account['account_type'] == 'current':
            print(f"  Current Account ID: {account['account_id']}")
            print(f"  Created At: {account['created_at']}")
            print(f"  Balance: {account['balance']}\n")

        elif account['account_type'] == 'loan':
            print(f"  Loan Account ID: {account['account_id']}")
            print(f"  Loan Amount: {account['loan_amount']}")
            print(f"  Interest Rate: {account['interest_rate']}%")
            print(f"  Due Date: {account['due_date']}")
            print(f"  Created At: {account['created_at']}\n")

def print_insurance_report(user_id):

    insurance_policies = insurance.get_user_insurance_policies(user_id)
    if not insurance_policies:
        logger.error(f"Failed to retrieve insurance policies for user ID {user_id}")
        print("No insurance policies found.")
        return
    
    print("\nInsurance Report:")
    for policy in insurance_policies:
        print(f"  Policy ID: {policy['policy_id']}")
        print(f"  Policy Type: {policy['policy_type']}")
        print(f"  Coverage Amount: {policy['coverage_amount']}")
        print(f"  Premium Amount: {policy['premium_amount']}")
        print(f"  Premium Frequency: {policy['premium_frequency']}")
        print(f"  Status: {policy['status']}")
        print(f"  Start Date: {policy['start_date']}")
        print(f"  End Date: {policy['end_date']}")
        print(f"  Next Premium Due: {policy['next_premium_due']}\n")

def print_transaction_report(user_id, account_id):

    transactions = banking.get_transaction_history(user_id, account_id)

    if not transactions:
        logger.error(f"Failed to retrieve transactions for user ID {user_id}")
        print("No transactions found.")
        return
    
    print("\nTransaction Report:")
    for transaction in transactions:
        print(f"  Transaction ID: {transaction['id']}")
        print(f"  Amount: {transaction['amount']}")
        print(f"  Transaction Type: {transaction['transaction_type']}")
        print(f"  Date: {transaction['created_at']}\n")