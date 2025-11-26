import hashlib
import sys
import os

# Add the parent directory (QUANTRA/) to sys.path
sys.path.append(os.path.dirname(os.path.abspath(r"C:\Users\hp\Documents\GitHub\Quantra")))
from config.db_config import get_db_connection


import mysql.connector as mysql
from config.db_config import get_db_connection
from modules import accounts, banking, insurance, loans, notifications
from core import auth, roles, scheduler, security, reports
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
            time.sleep(0.0035)  # Adjust speed here
            if c == correct_char:
                guessed += c
                break
    print()

def login():
    username = input("Enter your username: ").strip()
    email = input("Enter your email: ").strip()

    # Call the login_user function and capture the returned user_id
    user_id = auth.login_user(username, email)
    if user_id:
        print("Login successful!")
        return user_id
    else:
        print("Login failed. Please check your credentials.")
        return False
    
def register():
    username = input("Choose a username: ").strip()
    email = input("Enter your email: ").strip()
    password = input("Choose a password: ").strip()

    if auth.register_user(username, email, password):
        print("Registration successful! You can now log in.")
        logger.log_action(None, f"Welcome new user: {username}")
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
            user_id = login()
            if user_id:
                return user_id
            else:
                return False
        elif choice == '2':
            if not register():
                return False
            login()
            return True
        else:
            print("Invalid choice. Please enter 1 or 2.")

def menu():
    print("\nHome Menu:")
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
            choice = int(input("Enter your choice (1-7): "))
            if 1 <= choice <= 7:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def user_management_menu():
    print("User Management Menu:")
    options = [
        "View User Details",
        "Update User Information",
        "Change User Password",
        "Exit to Main Menu"
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-4): "))
            if 1 <= choice <= 4:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def accounts_management_menu():
    print("Accounts Management Menu:")
    options = [
        "Create Account",
        "Delete Account",
        "Exit to Main Menu"
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-3): ").strip())
            if 1 <= choice <= 3:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def banking_management_menu():
    print("Banking Management Menu:")
    options = [
        "Deposit",
        "Withdraw",
        "Transfer",
        "Exit to Main Menu"
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-4): "))
            if 1 <= choice <= 4:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def insurance_menu():
    print("Insurance Menu:")
    options = [
        "View Insurance Details",
        "Create Insurance Policy",
        "Cancel Insurance Policy",
        "Exit to Main Menu"
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-4): ").strip())
            if 1 <= choice <= 4:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def reports_menu():
    print("Reports Menu:")
    options = [
        "Generate Account Report",
        "Generate Transaction Report",
        "Generate Insurance Report",
        "Exit to Main Menu"
    ]
    for index, item in enumerate(options):
        print(f"{index + 1}. - {item}")

    while True:
        try:
            choice = int(input("Enter your choice (1-4): ").strip())
            if 1 <= choice <= 4:
                return int(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def notifications_menu(user_id):
    print("\nNOTIFICATIONS:")
    notification = notifications.get_notifications(user_id)
    
    if not notification:
        print("No notifications available.")
        return None
    
    print("\nYour Notifications:")
    for note in notification:
        status = "✓ Read" if note['is_read'] else "✗ Unread"
        print(f"ID: {note['id']} | {status} | {note['message']} | {note['created_at']}")
    
    print("\n1. Mark Notification as Read")
    print("0. Back to Main Menu")

    while True:
        try:
            choice = int(input("Enter your choice (0-1): ").strip())
            if choice == 0:
                return 0
            elif choice == 1:
                return 1  
            else:
                print("Invalid choice. Please enter 0 or 1.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

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
    time.sleep(0.6)

    # Authorize user
    user_id = authorize()
    if not user_id:
        print("Authorization failed. Exiting application.")
        return
    
    time.sleep(1)
    helpers.clear_screen()
    

    # Main Loop
    while True:
        choice = get_user_choice()

        if choice == 1:
            helpers.clear_screen()
            user_choice = user_management_menu()


            if user_choice == 1:
                user_info, account_details, insurance_details = auth.get_user_details(user_id)

                if account_details and insurance_details:

                    # Print User Summary
                    print("\nUser Summary:")
                    print(f" Username: {user_info['username']}")
                    print(f" Email: {user_info['email']}")
                    print(f" Role: {user_info['role']}")
                    print(f" Joined: {user_info['created_at']}\n")

                    # Print Account Details
                    print("\nAccount Details:")
                    for acc in account_details:
                        print(f"  - Account ID: {acc['id']}")
                        print(f"  - Account Type: {acc['account_type']}")
                        print(f"  - Created At: {acc['created_at']}\n")

                    # Print Insurance Details
                    print("\nInsurance Policies:")
                    for ins in insurance_details:
                        print(f"  - Policy ID: {ins['id']}")
                        print(f"  - Policy Type: {ins['policy_type']}")
                        print(f"  - Coverage Amount: {ins['coverage_amount']}")
                        print(f"  - Status: {ins['status']}")
                        print(f"  - Created At: {ins['created_at']}\n")

                elif account_details is None or insurance_details is None:
                    # Print User Summary
                    print("\nUser Summary:")
                    print(f" Username: {user_info['username']}")
                    print(f" Email: {user_info['email']}")
                    print(f" Role: {user_info['role']}")
                    print(f" Joined: {user_info['created_at']}\n")

                    if account_details is None:
                        print("No Accounts found for this user.\n")
                    else:
                        # Print Account Details
                        print("\nAccount Details:")
                        for acc in account_details:
                            print(f"  - Account ID: {acc['id']}")
                            print(f"  - Account Type: {acc['account_type']}")
                            print(f"  - Created At: {acc['created_at']}\n")

                    if insurance_details is None:
                        print("No Insurance Policies found for this user.")
                    else:
                        # Print Insurance Details
                        print("\nInsurance Policies:")
                        for ins in insurance_details:
                            print(f"  - Policy ID: {ins['id']}")
                            print(f"  - Policy Type: {ins['policy_type']}")
                            print(f"  - Coverage Amount: {ins['coverage_amount']}")
                            print(f"  - Status: {ins['status']}")
                            print(f"  - Created At: {ins['created_at']}\n")

                elif user_info is None:
                    print("User not found.")

            elif user_choice == 2:
                updates = {}
                new_email = input("Enter new email (leave blank to skip): ").strip()
                if new_email:
                    updates['email'] = new_email
                new_username = input("Enter new username (leave blank to skip): ").strip()
                if new_username:
                    updates['username'] = new_username
                if auth.update_user_details(user_id, updates):
                    print("User information updated successfully.")
                    logger.log_action(user_id, "Updated user information")
                else:
                    print("Failed to update user information.")

            elif user_choice == 3:
                old_password = input("Enter old password: ").strip()
                new_password = input("Enter new password: ").strip()
                if auth.change_password(user_id, old_password, new_password):
                    print("Password changed successfully.")
                    logger.log_action(user_id, "Changed user password")
                else:
                    print("Failed to change password.")
            
            elif user_choice == 4:
                helpers.clear_screen()
                continue  # Exit to main menu

        elif choice == 2:
            helpers.clear_screen()
            user_choice = accounts_management_menu()

            if user_choice == 1:
                account_data = {}
                account_data['account_type'] = input("Enter Account Type(savings, current, loan): ").strip().lower()

                if account_data['account_type']=='savings' or account_data['account_type']=='current':
                    account_data['initial_deposit'] = float(input("Enter Initial Deposit: ").strip())
                    if account_data["account_type"] == "savings":
                        account_data['interest_rate'] = float(input("Enter Interest Rate (as percentage): ").strip())
                    if accounts.create_account(user_id, account_data['account_type'], account_data['initial_deposit'], interest_rate= (account_data.get('interest_rate') if account_data['account_type']=='savings' else None)):
                        print("Account created successfully.")
                        logger.log_action(user_id, f"Created {account_data['account_type']} account")
                    else:
                        print(f"Failed to create {account_data['account_type']} account.")

                elif account_data['account_type']=='loan':

                    account_data['initial_deposit'] = float(input("Enter Loan Amount: ").strip())
                    account_data['interest_rate'] = float(input("Enter Interest Rate (as percentage): ").strip())
                    account_data['due_date'] = input("Enter Due Date (YYYY-MM-DD): ").strip()

                    if loans.apply_for_loan(user_id, account_data['initial_deposit'], account_data['interest_rate'], account_data['due_date']):
                        print("Loan account created successfully.")
                        logger.log_action(user_id, "Loan account created")

                    else:
                        print("Failed to create loan account.")
                    
                else:
                    print("Invalid account type. Please choose 'savings', 'current', or 'loan'.")

            elif user_choice == 2:
                account_id = int(input("Enter Account ID to delete: ").strip())
                account_type = input("Enter Account Type (savings/current/loan): ").strip().lower()
                if accounts.close_account(account_id, account_type):
                    print("Account deleted successfully.")
                    logger.log_action(user_id, f"Deleted {account_type} account with ID {account_id}")
                else:
                    print("Failed to delete account.")

            elif user_choice == 3:
                helpers.clear_screen()
                continue  # Exit to main menu

        elif choice == 3:
            helpers.clear_screen()
            user_choice = banking_management_menu()

            if user_choice == 1:
                account_id = int(input("Enter Account ID: ").strip())
                amount = float(input("Enter amount: ").strip())

                if banking.deposit(user_id, account_id, amount):
                    print("Deposit successful.")
                    logger.log_action(user_id, f"Deposited {amount} into account {account_id}")
                else:
                    print("Deposit failed.")

            elif user_choice == 2:
                account_id = int(input("Enter Account ID: ").strip())
                amount = float(input("Enter amount: ").strip())
                account_type = input("Enter Account Type (savings/current): ").strip().lower()
                if banking.withdraw(user_id, account_id, amount, account_type):
                    print("Withdrawal successful.")
                    logger.log_action(user_id, f"Withdrew {amount} from account {account_id}")
                else:
                    print("Withdrawal failed.")

            elif user_choice == 3:
                account_id = int(input("Enter Source Account ID: ").strip())
                target_account_id = int(input("Enter Target Account ID: ").strip())
                amount = float(input("Enter amount: ").strip())
                if banking.process_immediate_transfer(user_id, account_id, target_account_id, amount):
                    print("Transfer successful.")
                    logger.log_action(user_id, f"Transferred {amount} from account {account_id} to account {target_account_id}")
                else:
                    print("Transfer failed.")

            elif user_choice == 4:
                helpers.clear_screen()
                continue  # Exit to main menu

        elif choice == 4:
            helpers.clear_screen()
            user_choice = insurance_menu()
            

            if user_choice == 1:
                policy_id = int(input("Enter Policy ID to view details: ").strip())
                details = insurance.get_insurance_details(policy_id)
                if details:
                    print("\nInsurance Policy Details:")
                    print(f" Policy Type: {details['policy_type']}")
                    print(f" Premium Amount: {details['premium_amount']}")
                    print(f" Coverage Amount: {details['coverage_amount']}")
                    print(f" Premium Frequency: {details['premium_frequency']}")
                    print(f" Status: {details['status']}")
                    print(f" Start Date: {details['start_date']}")
                    print(f" End Date: {details['end_date']}")
                    print(f" Next Premium Due: {details['next_premium_due']}\n")
                else:
                    print("Policy not found.")

            elif user_choice == 2:
                policy_data = {}
                policy_data['type'] = input("Enter policy type: ").strip()
                policy_data['coverage_amount'] = float(input("Enter coverage amount: ").strip())
                policy_data['premium_amount'] = float(input("Enter premium amount: ").strip())
                policy_data['duration'] = int(input("Enter policy duration (in years): ").strip())
                policy_data['premium_frequency'] = input("Enter premium frequency (monthly/quarterly/yearly): ").strip().lower()
                if insurance.create_insurance(user_id, policy_data['type'], policy_data['premium_amount'], policy_data['coverage_amount'], policy_data['duration'], policy_data['premium_frequency']):
                    print("Policy created successfully.")
                    logger.log_action(user_id, "Created new insurance policy")
                else:
                    print("Failed to create policy.")

            elif user_choice == 3:
                policy_id = int(input("Enter Policy ID to cancel: ").strip())
                if insurance.cancel_insurance_policy(policy_id):
                    print("Policy canceled successfully.")
                    logger.log_action(user_id, f"Canceled insurance policy with ID {policy_id}")
                else:
                    print("Failed to cancel policy.")

            elif user_choice == 4:
                helpers.clear_screen()
                continue  # Exit to main menu

        elif choice == 5:
            helpers.clear_screen()
            while True:
                user_choice = notifications_menu(user_id)  # Unpack both values
                
                if user_choice == 1:
                    notification_id = int(input("\nEnter Notification ID to mark as read: ").strip())
                    if notifications.mark_as_read(notification_id, user_id):  # Pass user_id
                        print("✓ Notification marked as read.")
                    else:
                        print("✗ Failed to mark notification as read.")

                elif user_choice == 0:
                    helpers.clear_screen()
                    break  # Back to main menu

                elif user_choice is None:
                    time.sleep(1.5)
                    helpers.clear_screen()
                    break  # No notifications, back to main menu

        elif choice == 6:
            helpers.clear_screen()
            user_choice = reports_menu()

            if user_choice == 1:
                reports.print_account_report(user_id)

            elif user_choice == 2:
                account_id = int(input("Enter Account ID: ").strip())
                reports.print_transaction_report(user_id, account_id)

            elif user_choice == 3:
                reports.print_insurance_report(user_id)

            elif user_choice == 4:
                helpers.clear_screen()
                continue

        elif choice == 7:
            helpers.clear_screen()
            print_letter_progress("Exiting application. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

        # Run Scheduler in Background
        scheduler.run_daily_tasks()

if __name__ == "__main__":
    main()
