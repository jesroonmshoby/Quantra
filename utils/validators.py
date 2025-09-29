from datetime import datetime   

def validate_username(username):    # Only letters, numbers, underscore and 3–20 characters
    if len(username) < 3 or len(username) > 20:
        return False
    for ch in username:
        if not (ch.isalpha() or ch.isdigit() or ch == "_"):
            return False
    return True


def validate_password(password):  # At least 8 characters, includes upper, lower, digit, special
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


def validate_amount(amount):  # Must be numeric and greater than 0
    try:
        amt = float(amount)
        return amt > 0
    except:
        return False

def validate_account_type(acc_type):    # Must be one of these
    if acc_type == "Checking" or acc_type == "Savings" or acc_type == "Investment":
        return True
    else:
        return False

def validate_interest_rate(rate):  # Numeric and between 0–100
    try:
        value = float(rate)
        if value > 0 and value <= 100:
            return True
        else:
            return False
    except:
        return False

def validate_date(date_string):  # Must be YYYY-MM-DD
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except:
        return False


def validate_policy_type(policy_type):
    if policy_type in ["Life", "Health", "Property", "Auto", "Business"]:
        return True
    else:
        return False

def validate_stock_symbol(symbol):  # 1–5 uppercase letters
    if len(symbol) < 1 or len(symbol) > 5:
        return False
    for ch in symbol:
        if not ch.isupper():
            return False
    return True
