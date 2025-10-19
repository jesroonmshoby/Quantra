# reports.py
from config.db_config import get_db_connection

# ---------- ACCOUNT STATEMENT REPORT ----------
def print_account_statement(conn, account_type):
    cursor = conn.cursor()
    account_type = account_type.lower()

    if account_type == "savings":
        query = """
            SELECT a.id, u.username, s.balance, s.interest_rate, a.created_at
            FROM accounts a
            JOIN users u ON a.user_id = u.id
            JOIN savings_accounts s ON a.id = s.account_id
            WHERE a.account_type = 'savings'
        """
        cursor.execute(query)
        data = cursor.fetchall()

        print("\n=== SAVINGS ACCOUNT STATEMENT ===")
        print(f"{'ID':<5} {'Username':<15} {'Balance':<12} {'Interest Rate':<15} {'Created At':<20}")
        print("-" * 70)
        for row in data:
            id, username, balance, interest, created_at = row
            print(f"{id:<5} {username:<15} {balance:<12.2f} {interest:<15.2f} {created_at:<20}")

    elif account_type == "current":
        query = """
            SELECT a.id, u.username, c.balance, c.overdraft_limit, a.created_at
            FROM accounts a
            JOIN users u ON a.user_id = u.id
            JOIN current_accounts c ON a.id = c.account_id
            WHERE a.account_type = 'current'
        """
        cursor.execute(query)
        data = cursor.fetchall()

        print("\n=== CURRENT ACCOUNT STATEMENT ===")
        print(f"{'ID':<5} {'Username':<15} {'Balance':<12} {'Overdraft Limit':<18} {'Created At':<20}")
        print("-" * 75)
        for row in data:
            id, username, balance, overdraft, created_at = row
            print(f"{id:<5} {username:<15} {balance:<12.2f} {overdraft:<18.2f} {created_at:<20}")

    elif account_type == "loan":
        query = """
            SELECT a.id, u.username, l.loan_amount, l.interest_rate, l.due_date, a.created_at
            FROM accounts a
            JOIN users u ON a.user_id = u.id
            JOIN loan_accounts l ON a.id = l.account_id
            WHERE a.account_type = 'loan'
        """
        cursor.execute(query)
        data = cursor.fetchall()

        print("\n=== LOAN ACCOUNT STATEMENT ===")
        print(f"{'ID':<5} {'Username':<15} {'Loan Amount':<15} {'Interest Rate':<15} {'Due Date':<12} {'Created At':<20}")
        print("-" * 85)
        for row in data:
            id, username, loan_amount, interest, due_date, created_at = row
            print(f"{id:<5} {username:<15} {loan_amount:<15.2f} {interest:<15.2f} {due_date:<12} {created_at:<20}")

    else:
        print("\nInvalid account type! Choose from: savings, current, or loan.")

    print("-" * 85)
    cursor.close()


# ---------- PREMIUM REPORT ----------
def print_premium_report(conn):
    cursor = conn.cursor()
    query = """
        SELECT 
            i.id, u.username, i.policy_number, i.coverage_type, 
            i.coverage_amount, i.premium_amount, i.premium_frequency, 
            i.next_premium_due, i.status
        FROM insurance i
        JOIN users u ON i.user_id = u.id
    """
    cursor.execute(query)
    data = cursor.fetchall()

    print("\n=== PREMIUM REPORT ===")
    print(f"{'ID':<5} {'Username':<15} {'Policy No.':<15} {'Coverage':<15} {'Premium':<10} {'Freq':<10} {'Next Due':<12} {'Status':<10}")
    print("-" * 95)
    for row in data:
        id, username, policy, coverage, coverage_amt, premium, freq, due, status = row
        print(f"{id:<5} {username:<15} {policy:<15} {coverage:<15} {premium:<10.2f} {freq:<10} {due:<12} {status:<10}")
    print("-" * 95)
    cursor.close()


# ---------- LOAN REPORT ----------
def print_loan_report(conn):
    cursor = conn.cursor()
    query = """
        SELECT 
            u.username, l.account_id, l.loan_amount, l.interest_rate, l.due_date
        FROM loan_accounts l
        JOIN accounts a ON l.account_id = a.id
        JOIN users u ON a.user_id = u.id
    """
    cursor.execute(query)
    data = cursor.fetchall()

    print("\n=== LOAN REPORT ===")
    print(f"{'Username':<15} {'Account ID':<12} {'Loan Amount':<15} {'Interest Rate':<15} {'Due Date':<12}")
    print("-" * 75)
    for row in data:
        username, acc_id, loan_amount, rate, due = row
        print(f"{username:<15} {acc_id:<12} {loan_amount:<15.2f} {rate:<15.2f} {due:<12}")
    print("-" * 75)
    cursor.close()


# ---------- TRANSACTION REPORT ----------
def print_transaction_report(conn):
    cursor = conn.cursor()
    query = """
        SELECT 
            t.id, u.username, t.account_id, t.amount, t.transaction_type, t.created_at
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC
    """
    cursor.execute(query)
    data = cursor.fetchall()

    print("\n=== TRANSACTION REPORT ===")
    print(f"{'Txn ID':<8} {'Username':<15} {'Account ID':<12} {'Amount':<12} {'Type':<10} {'Created At':<20}")
    print("-" * 80)
    for row in data:
        txn_id, username, acc_id, amount, txn_type, created = row
        print(f"{txn_id:<8} {username:<15} {acc_id:<12} {amount:<12.2f} {txn_type:<10} {created:<20}")
    print("-" * 80)
    cursor.close()


# ---------- USER LOG REPORT ----------
def print_user_log_report(conn):
    cursor = conn.cursor()
    query = """
        SELECT u.username, l.action, l.created_at
        FROM user_logs l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC
    """
    cursor.execute(query)
    data = cursor.fetchall()

    print("\n=== USER LOG REPORT ===")
    print(f"{'Username':<15} {'Action':<40} {'Created At':<20}")
    print("-" * 75)
    for row in data:
        username, action, created_at = row
        print(f"{username:<15} {action:<40} {created_at:<20}")
    print("-" * 75)
    cursor.close()
