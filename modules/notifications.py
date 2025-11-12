from config.db_config import get_db_connection
from utils.logger import Logger

logger = Logger()

def get_notifications(user_id):
    """Retrieve all unread notifications/logs for a user."""
    try:
        conn, err = get_db_connection("quantra_db")
        if conn is None:
            logger.error(f"Database connection failed: {err}")
            return []
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, action as message, created_at, is_read
            FROM user_logs
            WHERE user_id = %s AND is_read = FALSE
            ORDER BY created_at DESC
        """, (user_id,))
        
        logs = cursor.fetchall()
        logger.debug(f"Retrieved {len(logs)} unread logs for user {user_id}")
        return logs
        
    except Exception as e:
        logger.error(f"Error retrieving logs for user {user_id}: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def mark_as_read(log_id, user_id=None):
    """Mark a specific log/notification as read."""
    try:
        conn, err = get_db_connection("quantra_db")
        if conn is None:
            logger.error(f"Database connection failed: {err}")
            return False
            
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("""
                UPDATE user_logs
                SET is_read = TRUE
                WHERE id = %s AND user_id = %s
            """, (log_id, user_id))
        else:
            cursor.execute("""
                UPDATE user_logs
                SET is_read = TRUE
                WHERE id = %s
            """, (log_id,))
            
        conn.commit()

        if cursor.rowcount == 0:
            logger.warning(f"No log found with ID {log_id}")
            return False
        
        logger.info(f"Log {log_id} marked as read")
        return True
        
    except Exception as e:
        logger.error(f"Error marking log as read: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def send_low_balance_alerts(threshold=1000):
    """Send alerts to users whose account balance falls below the threshold."""
    try:
        db, err = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT username, balance FROM accounts WHERE balance < %s", (threshold,))
        low_balance_users = cursor.fetchall()

        for user in low_balance_users:
            print(f"Low balance alert for {user['username']}: Balance = {user['balance']}")
    except Exception as e:
        logger.error(f"Error sending low balance alerts: {e}")
    finally:
        db.close()

def send_loan_due_alerts():
    """Send reminders to users with loan payments due within 3 days."""
    try:
        db, err = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT users.username, loans.due_date, loans.amount_due
            FROM loans
            JOIN users ON loans.user_id = users.id
            WHERE loans.due_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 3 DAY)
            AND loans.status = 'active'
        """)
        due_loans = cursor.fetchall()

        for loan in due_loans:
            print(f"Loan reminder for {loan['username']}: {loan['amount_due']} due by {loan['due_date']}")
    except Exception as e:
        logger.error(f"Error sending loan due alerts: {e}")
    finally:
        db.close()

def send_payment_due_alerts():
    """Send reminders for bills or scheduled payments due within 3 days."""
    try:
        db, err = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
+            SELECT users.username, scheduled_payments.description, scheduled_payments.due_date, scheduled_payments.amount
+            FROM scheduled_payments
+            JOIN users ON scheduled_payments.user_id = users.id
+            WHERE scheduled_payments.due_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 3 DAY)
+        """)
        due_payments = cursor.fetchall()

        for payment in due_payments:
            print(f"Payment reminder for {payment['username']}: {payment['description']} of {payment['amount']} due on {payment['due_date']}")
    except Exception as e:
        logger.error(f"Error sending payment due alerts: {e}")
    finally:
        db.close()