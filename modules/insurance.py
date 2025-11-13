from config.db_config import get_db_connection
from utils.logger import Logger
import utils.validators as validators
import core.security as security

logger = Logger()

def create_insurance(user_id, policy_type, premium_amount, coverage_amount, premium_frequency='monthly'):
    try:
        if not validators.validate_amount(premium_amount) or not validators.validate_amount(coverage_amount):
            logger.error("Invalid premium or coverage amount")
            return None

        if premium_frequency not in ['monthly', 'quarterly', 'yearly']:
            logger.error(f"Invalid premium frequency: {premium_frequency}")
            return None

        # Calculate next premium date based on frequency
        premium_intervals = {
            'monthly': 1,
            'quarterly': 3,
            'yearly': 12
        }

        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO insurance (
                user_id, 
                policy_type,
                premium_amount,
                coverage_amount,
                premium_frequency,
                status,
                start_date,
                end_date,
                next_premium_due
            ) VALUES (
                %s, %s, 
                %s, %s,
                %s,
                'active',
                CURDATE(),
                DATE_ADD(CURDATE(), INTERVAL 1 YEAR),
                DATE_ADD(CURDATE(), INTERVAL %s MONTH)
            )
        """, (
            user_id, 
            policy_type, 
            premium_amount, 
            coverage_amount,
            premium_frequency,
            premium_intervals[premium_frequency]
        ))

        result = cursor.lastrowid

        if not result:
            logger.error("Failed to create insurance policy")
            return None
            
        policy_id = result
        conn.commit()
        
        logger.info(f"Created insurance policy POL-{policy_id:06d} for user {user_id}")
        return policy_id

    except Exception as e:
        logger.error(f"Failed to create insurance policy for user {user_id}: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

def get_insurance_details(policy_id):
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT policy_number, policy_type, premium_amount, coverage_amount, 
                   premium_frequency, status, start_date, end_date, next_premium_due
            FROM insurance 
            WHERE id = %s
        """, (policy_id,))

        policy_details = cursor.fetchone()
        if not policy_details:
            logger.error(f"Insurance policy {policy_id} not found")
            return None

        return {
            "policy_number": policy_details[0],
            "policy_type": policy_details[1],
            "premium_amount": policy_details[2],
            "coverage_amount": policy_details[3],
            "premium_frequency": policy_details[4],
            "status": policy_details[5],
            "start_date": policy_details[6],
            "end_date": policy_details[7],
            "next_premium_due": policy_details[8]
        }

    except Exception as e:
        logger.error(f"Failed to get details for insurance policy {policy_id}: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

def cancel_insurance_policy(policy_id):
    try:
        conn, err = get_db_connection("quantra_db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE insurance 
            SET status = 'canceled' 
            WHERE id = %s
        """, (policy_id,))

        if cursor.rowcount == 0:
            logger.error(f"Insurance policy {policy_id} not found")
            return False

        conn.commit()
        logger.info(f"Cancelled insurance policy {policy_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to cancel insurance policy {policy_id}: {e}")
        return False

    finally:
        cursor.close()
        conn.close()