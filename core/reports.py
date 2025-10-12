# reports.py
from dbconfig import get_db_connection  # Importing DB connection function
from datetime import datetime

# ---------- USER REPORT ----------
def print_user_report(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, created_at FROM users")
    data = cursor.fetchall()

    print("\n=== USER REPORT ===")
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Created At':<20}")
    print("-" * 80)

    for row in data:
        id, username, email, created_at = row
        print(f"{id:<5} {username:<20} {email:<30} {created_at:<20}")

    print("-" * 80)
    cursor.close()


# ---------- ACCOUNT REPORT ----------
def print_account_report(conn):
    cursor = conn.cursor()
    query = """
        SELECT a.id, u.username, a.account_type, a.balance, a.created_at
        FROM accounts a
        JOIN users u ON a.user_id = u.id
    """
    cursor.execute(query)
    data = cursor.fetchall()

    print("\n=== ACCOUNT REPORT ===")
    print(f"{'ID':<5} {'Username':<15} {'Type':<10} {'Balance':<15} {'Created At':<20}")
    print("-" * 75)

    for row in data:
        id, username, acc_type, balance, created_at = row
        print(f"{id:<5} {username:<15} {acc_type:<10} {balance:<15.2f} {created_at:<20}")

    print("-" * 75)
    cursor.close()


# ---------- INSURANCE REPORT ----------
def print_insurance_report(conn):
    cursor = conn.cursor()
    query = """
        SELECT i.id, u.username, i.policy_number, i.coverage_type, i.coverage_amount,
               i.status, i.start_date, i.end_date
        FROM insurance i
        JOIN users u ON i.user_id = u.id
    """
    cursor.execute(query)
    data = cursor.fetchall()

    print("\n=== INSURANCE REPORT ===")
    print(f"{'ID':<5} {'Username':<15} {'Policy No':<15} {'Type':<15} "
          f"{'Amount':<12} {'Status':<10} {'Start':<12} {'End':<12}")
    print("-" * 100)

    for row in data:
        id, username, policy_no, cov_type, cov_amt, status, start, end = row
        print(f"{id:<5} {username:<15} {policy_no:<15} {cov_type:<15} "
              f"{cov_amt:<12.2f} {status:<10} {start:<12} {end:<12}")

    print("-" * 100)
    cursor.close()


# ---------- TRANSACTION REPORT ----------
def print_transaction_report(conn):
    cursor = conn.cursor()
    query = """
        SELECT t.id, u.username, a.account_type, t.amount, t.transaction_type, t.created_at
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN accounts a ON t.account_id = a.id
    """
    cursor.execute(query)
    data = cursor.fetchall()

    print("\n=== TRANSACTION REPORT ===")
    print(f"{'ID':<5} {'Username':<15} {'Acc Type':<10} {'Amount':<12} "
          f"{'Type':<10} {'Date':<20}")
    print("-" * 80)

    for row in data:
        id, username, acc_type, amount, trans_type, created_at = row
        print(f"{id:<5} {username:<15} {acc_type:<10} {amount:<12.2f} "
              f"{trans_type:<10} {created_at:<20}")

    print("-" * 80)
    cursor.close()


# ---------- MAIN ----------
def main():
    conn = get_db_connection("quantra_db")  # Use imported connection
    if conn is None:
        print("Error: Unable to connect to database.")
        return

    print("\nConnected to Quantra Database Successfully!")

    print_user_report(conn)
    print_account_report(conn)
    print_insurance_report(conn)
    print_transaction_report(conn)

    conn.close()
    print("\nAll reports printed successfully!")


# ---------- RUN ----------
if __name__ == "__main__":
    main()
