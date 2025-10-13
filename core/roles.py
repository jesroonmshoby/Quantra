ROLE_PERMISSIONS = {
    "User": [
        "banking_view", "banking_transact",
        "loan_apply", "loan_payment",
        "insurance_apply", "insurance_claim",
        "report_personal"
    ],

    "Manager": [
        "banking_view", "banking_transact",
        "loan_apply", "loan_approve", "loan_payment",
        "insurance_apply", "insurance_approve", "insurance_claim",
        "report_personal", "report_all_users", "view_audit_logs",
    ],

    "Admin": [
        "all"   # Full access
    ]
}

def validate_role(role):
    return role in ROLE_PERMISSIONS

def has_permission(role, permission):
    if not validate_role(role):
        return False
    if "all" in ROLE_PERMISSIONS[role]:
        return True
    return permission in ROLE_PERMISSIONS[role]

def get_permissions(role):
    return ROLE_PERMISSIONS.get(role, [])

def is_admin(role):
    return role == "Admin"

def is_manager(role):
    return role == "Manager"

def list_roles():
    return list(ROLE_PERMISSIONS.keys())

def get_role_level(role):
    levels = {
        "User": 1,
        "Manager": 2,
        "Admin": 3
    }
    return levels.get(role, 0)

