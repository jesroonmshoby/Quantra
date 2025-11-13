import mysql.connector as mysql
from config.db_config import get_db_connection
from datetime import date
from utils.helpers import add_days
from utils.logger import Logger
from utils.helpers import format_currency    

logger = Logger()

def apply_loan_interest():
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute(f" SELECT accounts.user_id, accounts.account_type, loan_accounts.loan_amount, loan_accounts.interest_rate, loan_accounts.due_date FROM accounts, loan_accounts WHERE accounts.id = loan_accounts.account_id;")
        loans = cursor.fetchall()
        processed_count = 0

        for loan in loans:
            user_id, account_id, loan_amount, interest_rate, due_date = loan
                
            interest = loan_amount * (interest_rate / 100)
            new_loan_amount = loan_amount + interest

            cursor.execute(
                f"UPDATE loan_accounts SET loan_amount = {new_loan_amount} WHERE account_id = {account_id}",
            )
                
            processed_count += 1
                
            logger.log_action(
                user_id,
                f"Applied interest {format_currency(interest)} to Loan Account #{account_id}"
            )

        conn.commit()
            
        if processed_count > 0:
            logger.info(
                f"Applied interest to {processed_count} loans",
                context="scheduler:apply_loan_interest"
    )

        cursor.close()
        conn.close()
        return processed_count

    except mysql.Error as err:
        logger.error(
            f"Failed to apply loan interest: {err}",
            context="scheduler:apply_loan_interest"
        )
        return 0

def apply_savings_interest():
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute(f" SELECT accounts.user_id, accounts.id AS account_id, savings_accounts.balance, savings_accounts.interest_rate FROM accounts, savings_accounts WHERE accounts.id = savings_accounts.account_id;")
        accounts = cursor.fetchall()
        processed_count = 0

        for account in accounts:
            user_id, account_id, balance, interest_rate = account
            
            interest = balance * (interest_rate / 100)
            new_balance = balance + interest

            cursor.execute(
                f"UPDATE savings_accounts SET balance = {new_balance} WHERE account_id = {account_id}",
            )
            
            processed_count += 1
            
            logger.log_action(
                user_id,
                f"Applied interest {format_currency(interest)} to Savings Account #{account_id}"
            )

        conn.commit()
        
        if processed_count > 0:
            logger.info(
                f"Applied interest to {processed_count} savings accounts",
                context="scheduler:apply_savings_interest"
            )

        cursor.close()
        conn.close()
        return processed_count

    except mysql.Error as err:
        logger.error(
            f"Failed to apply savings interest: {err}",
            context="scheduler:apply_savings_interest"
        )
        return 0



def auto_pay_insurance_premiums(insurance_id):
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute(f"""SELECT 
        insurance.user_id, 
        insurance.policy_number, 
        insurance.premium_amount, 
        insurance.premium_frequency, 
        insurance.next_premium_due, 
        insurance.last_paid_date,
        accounts.id AS account_id, 
        accounts.account_type, 
        current_accounts.balance AS current_balance 
    FROM 
        insurance, 
        accounts, 
        current_accounts
    WHERE 
        insurance.id = {insurance_id}
        AND insurance.user_id = accounts.user_id
        AND accounts.id = current_accounts.account_id;""")

        row = cursor.fetchone()
        if not row:
            print(f"No insurance or associated current account found for insurance ID {insurance_id}")
            return

        user_id, policy_number, premium_amount, premium_frequency, next_premium_due, last_paid_date, account_id, account_type, current_balance = row

        if date.today().strftime("%Y-%m-%d") > next_premium_due:
            print(f"Premium for insurance ID {insurance_id} is overdue. No payment made.")
            return

        if date.today().strftime("%Y-%m-%d") == next_premium_due:
            if current_balance >= premium_amount:
                new_balance = current_balance - premium_amount

                cursor.execute(f"UPDATE current_accounts SET balance = {new_balance} WHERE account_id = {account_id}")
                
                if premium_frequency == 'monthly':
                    next_due_date = add_days(next_premium_due, 30)
                elif premium_frequency == 'quarterly':
                    next_due_date = add_days(next_premium_due, 90)
                elif premium_frequency == 'yearly':
                    next_due_date = add_days(next_premium_due, 365)
                else:
                    print(f"Unknown premium frequency '{premium_frequency}' for insurance ID {insurance_id}")
                    return

                cursor.execute(f"UPDATE insurances SET next_premium_due = '{next_due_date}', last_paid_date = '{date.today().strftime('%Y-%m-%d')}' WHERE id = {insurance_id}")
                conn.commit()
                cursor.close()
                conn.close()

                logger.log_action(user_id,
                                f"Auto-paid insurance premium {format_currency(premium_amount)} for Policy #{policy_number} from Account #{account_id}")
                logger.log_system("INFO",
                                f"Auto-paid insurance premium for policy #{policy_number} for user {user_id}", context="scheduler:auto_pay_insurance_premiums")
            else:
                print(f"Insufficient funds in account ID {account_id} to pay premium for insurance ID {insurance_id}")
                return
    except mysql.Error as err:
        logger.error(
            f"Failed to auto-pay insurance premium: {err}",
            context="scheduler:auto_pay_insurance_premiums"
        )
        return False
    
def check_insurance_expiry():
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        # Find active policies that have expired
        cursor.execute(f"""
            UPDATE insurance 
            SET status = 'expired'
            WHERE status = 'active' 
            AND end_date < CURDATE()
        """)
        
        expired_count = cursor.rowcount
        conn.commit()

        # Log the operation
        if expired_count > 0:
            logger.info(
                f"Updated {expired_count} expired insurance policies",
                context="scheduler:check_insurance_expiry"
            )

        cursor.close()
        conn.close()
        return expired_count

    except mysql.Error as err:
        logger.error(
            f"Failed to check insurance expiry: {err}",
            context="scheduler:check_insurance_expiry"
        )
        return 0
    
def process_immediate_transfer(from_account_id, to_account_id, amount):
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

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

    except mysql.Error as err:
        logger.error(
            f"Transfer failed: {err}",
            context="banking:process_immediate_transfer"
        )
        return False
    
def check_upcoming_deadlines(warning_days=3):
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                accounts.user_id,
                loan_accounts.account_id,
                loan_accounts.loan_amount,
                loan_accounts.due_date,
                DATEDIFF(loan_accounts.due_date, CURDATE()) as days_remaining
            FROM loan_accounts, accounts WHERE loan_accounts.account_id = accounts.id
            AND loan_accounts.status = 'active'
            AND loan_accounts.due_date > CURDATE()
            AND loan_accounts.due_date <= DATE_ADD(CURDATE(), INTERVAL {warning_days} DAY)
        """)
        
        loan_warnings = cursor.fetchall()

        cursor.execute(f"""
            SELECT 
                accounts.user_id,
                insurances.policy_number,
                insurances.premium_amount,
                insurances.next_premium_due,
                DATEDIFF(insurances.next_premium_due, CURDATE()) as days_remaining
            FROM insurances, accounts WHERE insurances.account_id = accounts.id
            AND insurances.status = 'active'
            AND insurances.next_premium_due > CURDATE()
            AND insurances.next_premium_due <= DATE_ADD(CURDATE(), INTERVAL {warning_days} DAY)
        """)

        insurance_warnings = cursor.fetchall()

        for warning in loan_warnings:
            user_id, account_id, loan_amount, due_date, days_remaining = warning
            logger.log_action(
                user_id,
                f"Loan Account #{account_id} has an upcoming payment of {format_currency(loan_amount)} due on {due_date} ({days_remaining} days remaining)"
            )
            logger.warning(
                f"Loan payment of {format_currency(loan_amount)} for Account #{account_id} "
                f"is due in {days_remaining} days (Due: {due_date})",
                context="scheduler:check_upcoming_deadlines"
            )

        for warning in insurance_warnings:
            user_id, policy_number, premium_amount, next_premium_due, days_remaining = warning
            logger.log_action(
                user_id,
                f"Insurance Policy #{policy_number} has an upcoming premium of {format_currency(premium_amount)} due on {next_premium_due} ({days_remaining} days remaining)"
            )
            logger.warning(
                f"Insurance premium of {format_currency(premium_amount)} for Policy #{policy_number} "
                f"is due in {days_remaining} days (Due: {due_date})",
                context="scheduler:check_upcoming_deadlines"
            )

        cursor.close()
        conn.close()

    except mysql.Error as err:
        logger.error(
            f"Failed to check upcoming deadlines: {err}",
            context="scheduler:check_upcoming_deadlines"
        )

def run_daily_tasks():
    try:
        logger.info("Starting daily maintenance tasks.", 
                   context="scheduler:run_daily_tasks")

        # Check insurance expiry
        expired_count = check_insurance_expiry()

        # Apply monthly interests
        if date.today().day == 1:
            savings_interest_count = apply_loan_interest()
            loan_interest_count = apply_savings_interest()

        # Check for upcoming deadlines
        check_upcoming_deadlines(warning_days=3)


        # Process insurance premiums due today
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM insurance WHERE next_premium_due = CURDATE()")
        due_premiums = cursor.fetchall()
        for (insurance_id,) in due_premiums:
            auto_pay_insurance_premiums(insurance_id)
        cursor.close()
        conn.close()

        logger.info("Daily maintenance tasks completed successfully.", 
                   context="scheduler:run_daily_tasks")
        
        return {
            "expired_policies": expired_count,
            "loan_interest_applied": loan_interest_count,
            "savings_interest_applied": savings_interest_count
        }


    except Exception as err:
        logger.error(
            f"Failed to run daily tasks: {err}",
            context="scheduler:run_daily_tasks"
        )
        return False