"""
مدیریت ورود و خروج کاربران
"""

from models.user_model import authenticate, get_user_menus
from utils.audit import log_action


def _safe_str(value):
    """
    تبدیل bytearray یا هر نوع دیگه به string
    این تابع مشکل JSON serialization رو حل می‌کنه
    """
    if value is None:
        return ""
    if isinstance(value, bytearray):
        return value.decode('utf-8', errors='ignore')
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    return str(value)
    
def login_user(username, password):
    """
    ورود کاربر
    Returns:
        (user_data, None) : در صورت موفقیت
        (None, error_msg)  : در صورت شکست
    """
    user, error = authenticate(username, password)

    if user:
        menus = get_user_menus(user['AccessLevelID'])
        user_data = {
            'UserID': int(user['UserID']),
            'Username': _safe_str(user['Username']),
            'FullName': _safe_str(user['FullName']),
            'AccessLevelID': int(user['AccessLevelID']),
            'postmodir': int(user.get('postmodir', 0)),
            'dep_id': int(user.get('dep_id', 0)),
            'menus': [str(m) for m in menus] if menus else []
        }
        log_action("Login", user_id=user_data['UserID'], status="Success")
        return user_data, None
    else:
        log_action("Login Attempt", status="Failed", error_msg=error or "Invalid credentials")
        return None, error
        
def logout_user():
    """خروج کاربر"""
    from flask import session
    if 'user' in session:
        user_id = session['user'].get('UserID')
        log_action("Logout", user_id=user_id, status="Success")