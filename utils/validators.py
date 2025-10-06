# utils/validators.py
from datetime import datetime

# ---------- USERS ----------
def validate_username(username):
    if len(username) < 3 or len(username) > 30:
        return False
    for ch in username:
        if not (ch.isalpha() or ch.isdigit() or ch == "_"):
            return False
    return True

def validate_email(email):
    if "@" in email and "." in email:
        return True
    else:
        return False

def validate_password(password):
    if len(password) < 8:
        return False
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    for ch in password:
        if ch.isupper():
            has_upper = True
        elif ch.islower():
            has_lower = True
        elif ch.isdigit():
            has_digit = True
        else:
            has_special = True
    if has_upper and has_lower and has_digit and has_special:
        return True
    else:
        return False


# ---------- ACCOUNTS ----------
def validate_account_type(acc_type):
    if acc_type in ["savings", "current", "loan"]:
        return True
    else:
        return False

def validate_balance(balance):
    try:
        value = float(balance)
        if value >= 0:
            return True
        else:
            return False
    except:
        return False


# ---------- SAVINGS / LOAN ----------
def validate_interest_rate(rate):
    try:
        value = float(rate)
        if value > 0 and value <= 100:
            return True
        else:
            return False
    except:
        return False

def validate_loan_amount(amount):
    try:
        value = float(amount)
        if value > 0:
            return True
        else:
            return False
    except:
        return False

def validate_due_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except:
        return False


# ---------- TRANSACTIONS ----------
def validate_transaction_type(txn_type):
    if txn_type in ["credit", "debit"]:
        return True
    else:
        return False

def validate_amount(amount):
    try:
        value = float(amount)
        if value > 0:
            return True
        else:
            return False
    except:
        return False


# ---------- INSURANCE ----------
def validate_status(status):
    if status in ["active", "expired", "cancelled"]:
        return True
    else:
        return False

def validate_policy_number(policy_number):
    if len(policy_number) == 0 or len(policy_number) > 20:
        return False
    for ch in policy_number:
        if not (ch.isalnum() or ch == "-"):
            return False
    return True

def validate_coverage_type(coverage_type):
    if coverage_type.strip() == "":
        return False
    else:
        return True

def validate_coverage_amount(amount):
    try:
        value = float(amount)
        if value > 0:
            return True
        else:
            return False
    except:
        return False

def validate_start_end_dates(start_date, end_date):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if start < end:
            return True
        else:
            return False
    except:
        return False
