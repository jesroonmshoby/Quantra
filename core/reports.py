from config.db_config import get_db_connection  # Already handles connection


# -------------------- ACCOUNT STATEMENT REPORT --------------------
def print_account_statement(connection, account_type):
    cursor = connection.cursor()
    account_type = account_type.lower()

    if account_type == "savings":
        cursor.execute("SELECT id, user_id, created_at FROM accounts WHERE account_type = 'savings'")
        accounts = cursor.fetchall()

        print("\n=== SAVINGS ACCOUNT STATEMENT ===")
        print(f"{'Account ID':<12} {'Username':<20} {'Balance':<15} {'Interest Rate':<15} {'Created At':<25}")
        print("-" * 90)

        for account in accounts:
            account_id = account[0]
            user_id = account[1]
            created_at = account[2]

            cursor.execute(f"SELECT username FROM users WHERE id = {user_id}")
            username = cursor.fetchone()[0]

            cursor.execute(f"SELECT balance, interest_rate FROM savings_accounts WHERE account_id = {account_id}")
            balance, interest_rate = cursor.fetchone()

            print(f"{account_id:<12} {username:<20} {balance:<15.2f} {interest_rate:<15.2f} {str(created_at):<25}")

    elif account_type == "current":
        cursor.execute("SELECT id, user_id, created_at FROM accounts WHERE account_type = 'current'")
        accounts = cursor.fetchall()

        print("\n=== CURRENT ACCOUNT STATEMENT ===")
        print(f"{'Account ID':<12} {'Username':<20} {'Balance':<15} {'Overdraft Limit':<20} {'Created At':<25}")
        print("-" * 95)

        for account in accounts:
            account_id = account[0]
            user_id = account[1]
            created_at = account[2]

            cursor.execute(f"SELECT username FROM users WHERE id = {user_id}")
            username = cursor.fetchone()[0]

            cursor.execute(f"SELECT balance, overdraft_limit FROM current_accounts WHERE account_id = {account_id}")
            balance, overdraft_limit = cursor.fetchone()

            print(f"{account_id:<12} {username:<20} {balance:<15.2f} {overdraft_limit:<20.2f} {str(created_at):<25}")

    elif account_type == "loan":
        cursor.execute("SELECT id, user_id, created_at FROM accounts WHERE account_type = 'loan'")
        accounts = cursor.fetchall()

        print("\n=== LOAN ACCOUNT STATEMENT ===")
        print(f"{'Account ID':<12} {'Username':<20} {'Loan Amount':<15} {'Interest Rate':<15} {'Due Date':<15} {'Created At':<25}")
        print("-" * 100)

        for account in accounts:
            account_id = account[0]
            user_id = account[1]
            created_at = account[2]

            cursor.execute(f"SELECT username FROM users WHERE id = {user_id}")
            username = cursor.fetchone()[0]

            cursor.execute(f"SELECT loan_amount, interest_rate, due_date FROM loan_accounts WHERE account_id = {account_id}")
            loan_amount, interest_rate, due_date = cursor.fetchone()

            print(f"{account_id:<12} {username:<20} {loan_amount:<15.2f} {interest_rate:<15.2f} {str(due_date):<15} {str(created_at):<25}")

    else:
        print("\nInvalid account type! Choose from: savings, current, or loan.")

    cursor.close()


# -------------------- PREMIUM REPORT --------------------
def print_premium_report(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, policy_number, coverage_type, coverage_amount, premium_amount, premium_frequency, next_premium_due, status FROM insurance")
    policies = cursor.fetchall()

    print("\n=== PREMIUM REPORT ===")
    print(f"{'Policy ID':<10} {'Username':<20} {'Policy No.':<15} {'Coverage Type':<20} {'Coverage Amt':<15} {'Premium':<12} {'Frequency':<12} {'Next Due':<15} {'Status':<10}")
    print("-" * 130)

    for policy in policies:
        policy_id, user_id, policy_number, coverage_type, coverage_amount, premium_amount, frequency, next_due, status = policy
        cursor.execute(f"SELECT username FROM users WHERE id = {user_id}")
        username = cursor.fetchone()[0]

        print(f"{policy_id:<10} {username:<20} {policy_number:<15} {coverage_type:<20} {coverage_amount:<15.2f} {premium_amount:<12.2f} {frequency:<12} {str(next_due):<15} {status:<10}")

    cursor.close()


# -------------------- LOAN REPORT --------------------
def print_loan_report(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT account_id, loan_amount, interest_rate, due_date FROM loan_accounts")
    loans = cursor.fetchall()

    print("\n=== LOAN REPORT ===")
    print(f"{'Username':<20} {'Account ID':<12} {'Loan Amount':<15} {'Interest Rate':<15} {'Due Date':<15}")
    print("-" * 85)

    for loan in loans:
        account_id, loan_amount, interest_rate, due_date = loan
        cursor.execute(f"SELECT user_id FROM accounts WHERE id = {account_id}")
        user_id = cursor.fetchone()[0]

        cursor.execute(f"SELECT username FROM users WHERE id = {user_id}")
        username = cursor.fetchone()[0]

        print(f"{username:<20} {account_id:<12} {loan_amount:<15.2f} {interest_rate:<15.2f} {str(due_date):<15}")

    cursor.close()


# -------------------- TRANSACTION REPORT --------------------
def print_transaction_report(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, account_id, amount, transaction_type, created_at FROM transactions")
    transactions = cursor.fetchall()

    print("\n=== TRANSACTION REPORT ===")
    print(f"{'Transaction ID':<15} {'Username':<20} {'Account ID':<12} {'Amount':<12} {'Type':<10} {'Created At':<25}")
    print("-" * 95)

    for txn in transactions:
        txn_id, user_id, account_id, amount, txn_type, created_at = txn
        cursor.execute(f"SELECT username FROM users WHERE id = {user_id}")
        username = cursor.fetchone()[0]

        print(f"{txn_id:<15} {username:<20} {account_id:<12} {amount:<12.2f} {txn_type:<10} {str(created_at):<25}")

    cursor.close()


# -------------------- USER LOG REPORT --------------------
def print_user_log_report(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, action, created_at FROM user_logs")
    logs = cursor.fetchall()

    print("\n=== USER LOG REPORT ===")
    print(f"{'Username':<20} {'Action':<50} {'Created At':<25}")
    print("-" * 95)

    for log in logs:
        user_id, action, created_at = log
        cursor.execute(f"SELECT username FROM users WHERE id = {user_id}")
        username = cursor.fetchone()[0]

        print(f"{username:<20} {action:<50} {str(created_at):<25}")

    cursor.close()


# -------------------- NOTIFICATION REPORT --------------------
def print_notification_report(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, message, category, is_read, created_at FROM notifications")
    notifications = cursor.fetchall()

    print("\n=== NOTIFICATION REPORT ===")
    print(f"{'Username':<20} {'Message':<40} {'Category':<20} {'Read':<8} {'Created At':<25}")
    print("-" * 110)

    for notification in notifications:
        user_id, message, category, is_read, created_at = notification
        cursor.execute(f"SELECT username FROM users WHERE id = {user_id}")
        username = cursor.fetchone()[0]
        read_status = "Yes" if is_read else "No"

        print(f"{username:<20} {message:<40} {category:<20} {read_status:<8} {str(created_at):<25}")

    cursor.close()
