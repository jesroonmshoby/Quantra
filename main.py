import mysql.connector as mysql
from config.db_config import get_db_connection
from modules import accounts, banking, insurance, loans, notifications
from core import auth, reports, roles, scheduler, security
from utils import helpers, logger, validators
from database.migrations import run_migrations
import time
import string

# Initialize logger
logger = logger.Logger()

def display_loading_screen():
    loading_message = "Initializing Quantra Banking System"
    print(loading_message, end="", flush=True)
    for i in range(5):
        print(".", end="", flush=True)
        time.sleep(0.5)
    print("\nInitialization Complete!\n")

    # Wait for 2 seconds before clearing the screen
    time.sleep(2)
    helpers.clear_screen()


def print_letter_progress(word):
    guessed = ""
    for index, correct_char in enumerate(word):
        for c in string.printable:  # or use any set of characters you want
            print(guessed + c, end='\r', flush=True)
            time.sleep(0.006)  # Adjust speed here
            if c == correct_char:
                guessed += c
                break
    print()

def login():
    username = input("Enter your username: ").strip()
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()

    if auth.login_user(username, email, password):
        print("Login successful!")
        return True
    else:
        print("Login failed. Please check your credentials.")
        return False
    
def register():
    username = input("Choose a username: ").strip()
    email = input("Enter your email: ").strip()
    password = input("Choose a password: ").strip()

    if auth.register_user(username, email, password):
        print("Registration successful! You can now log in.")
        return True
    else:
        print("Registration failed. Please try again.")
        return False
    
def authorize():
    while True:
        print("1. Login")
        print("2. Register")
        choice = input("Enter your choice (1 or 2): ").strip()

        if choice == '1':
            if login():
                return True
            else:
                return False
        elif choice == '2':
            if not register():
                return False
            login()
        else:
            print("Invalid choice. Please enter 1 or 2.")

def menu():
    print("Home Menu:")
    options = [
        "User Management",
        "Accounts",
        "Banking",
        "Insurance",
        "Notifications",
        "Reports",
        "Exit"
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

def get_user_choice():
    while True:
        try:
            menu()
            choice = int(input("Enter your choice (1-11): "))
            if choice.isdigit() and 1 <= choice <= 11:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 11.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def account_menu():
    print("Account Menu:")
    options = [
        "Create Account",
        "Delete Account"
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

def user_management_menu():
    print("User Management Menu:")
    options = [
        "View User Details",
        "Update User Information",
        "Change User Password",
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-3): "))
            if choice.isdigit() and 1 <= choice <= 3:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def accounts_management_menu():
    print("Accounts Management Menu:")
    options = [
        "Create Account",
        "Delete Account",
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-2): ")).strip()
            if choice.isdigit() and 1 <= choice <= 2:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 2.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def banking_management_menu():
    print("Banking Management Menu:")
    options = [
        "Deposit",
        "Withdraw",
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-2): "))
            if choice.isdigit() and 1 <= choice <= 2:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def insurance_menu():
    print("Insurance Menu:")
    options = [
        "View Insurance Details",
        "Create Insurance Policy",
        "Cancel Insurance Policy",
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-3): ")).strip()
            if choice.isdigit() and 1 <= choice <= 3:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():

    # Connect to the database
    conn = get_db_connection()

    # Check if the connection was successful
    if conn is not None:
        print("Connection successful!")
    else:
        print("Connection failed.")

    # Run the migrations
    run_migrations()

    # Display loading screen
    display_loading_screen()

    print_letter_progress("Quantra Banking System")

    # Authorize user
    if not authorize():
        print("Authorization failed. Exiting application.")
        return

    # Main Loop
    while True:
        choice = get_user_choice()

        if choice == 1:
            user_choice = user_management_menu()

            if user_choice == 1:
                user_id = int(input("Enter User ID to view details: "))
                details = auth.get_user_details(user_id)
                if details:
                    print(details)
                else:
                    print("User not found.")

            elif user_choice == 2:
                user_id = int(input("Enter User ID to update: ").strip())
                updates = {}
                new_email = input("Enter new email (leave blank to skip): ").strip()
                if new_email:
                    updates['email'] = new_email
                new_username = input("Enter new username (leave blank to skip): ").strip()
                if new_username:
                    updates['username'] = new_username
                if auth.update_user_info(user_id, updates):
                    print("User information updated successfully.")
                else:
                    print("Failed to update user information.")

            elif user_choice == 3:
                user_id = int(input("Enter User ID to change password: ").strip())
                old_password = input("Enter old password: ").strip()
                new_password = input("Enter new password: ").strip()
                if auth.change_user_password(user_id, old_password, new_password):
                    print("Password changed successfully.")
                else:
                    print("Failed to change password.")

        elif choice == 2:
            user_choice = accounts_management_menu()

            if user_choice == 1:
                account_data = {}
                account_data['account_type'] = input("Enter Account Type: ").strip()

                if account_data['account_type']=='savings' or account_data['account_type']=='checking':
                    account_data['initial_deposit'] = float(input("Enter Initial Deposit: ").strip())
                    if accounts.create_account(account_data):
                        print("Account created successfully.")
                    else:
                        print("Failed to create account.")
                elif account_data['account_type']=='loan':
                    loans.apply_for_loan()
                else:
                    print("Invalid account type. Please choose 'savings', 'checking', or 'loan'.")

            elif user_choice == 2:
                account_id = int(input("Enter user ID to delete: ").strip())
                if accounts.delete_account(account_id):
                    print("Account deleted successfully.")
                else:
                    print("Failed to delete account.")



        elif choice == 3:
            user_choice = banking_management_menu()
            user_id = int(input("Enter User ID: ").strip())
            account_id = int(input("Enter Account ID: ").strip())
            amount = float(input("Enter amount: ").strip())

            if user_choice == 1:
                if banking.deposit(user_id, account_id, amount):
                    print("Deposit successful.")
                else:
                    print("Deposit failed.")

            elif user_choice == 2:
                if banking.withdraw(user_id, account_id, amount):
                    print("Withdrawal successful.")
                else:
                    print("Withdrawal failed.")

        elif choice == 4:
            user_choice = insurance_menu()

            if user_choice == 1:
                policy_id = int(input("Enter Policy ID to view details: ").strip())
                details = insurance.get_policy_details(policy_id)
                if details:
                    print(details)
                else:
                    print("Policy not found.")

            elif user_choice == 2:
                user_id = int(input("Enter User ID to create policy for: ").strip())
                policy_data = {}
                policy_data['type'] = input("Enter policy type: ").strip()
                policy_data['amount'] = float(input("Enter policy amount: ").strip())
                if insurance.create_policy(user_id, policy_data):
                    print("Policy created successfully.")
                else:
                    print("Failed to create policy.")

            elif user_choice == 3:
                policy_id = int(input("Enter Policy ID to cancel: ").strip())
                if insurance.cancel_policy(policy_id):
                    print("Policy canceled successfully.")
                else:
                    print("Failed to cancel policy.")

        elif choice == 5: