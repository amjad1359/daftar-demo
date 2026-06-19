from functools import wraps
from flask import session, jsonify, abort
from models.user_model import user_has_sub_access

MODULE_MENU_MAP = {
    'supervisor': '👨‍⚕️ سوپروایزر',
    'matron': '📋 مدیر پرستاری',
    'manager': '👔 مدیران اجرایی',
    'riyasat': '🏢 ریاست',
    'fanni': '🛠️ مسئول فنی',
    'admin': '⚙️ ادمین',
    'reports': '📊 گزارشات',
    'security': '🔑 امنیت',
}

REPORT_SUB_PERM_MAP = {
    'ankal': 'reports_ankal',
    'blood': 'reports_blood',
    'codes': 'reports_codes',
    'crisis': 'reports_crisis',
    'attendance': 'reports_attendance',
    'workflow': 'reports_workflow',
    'rounds': 'reports_rounds',
    'stats': 'reports_stats',
}

def require_module_access(module_name):
    """دکوراتور برای بررسی دسترسی کاربر به یک ماژول"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return jsonify({'success': False, 'message': 'لطفاً وارد شوید'}), 401
            
            user = session['user']
            if module_name == 'security':
                return f(*args, **kwargs)
            
            menu_name = MODULE_MENU_MAP.get(module_name)
            if not menu_name or menu_name not in user.get('menus', []):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_report_access(sub_page):
    """دکوراتور برای بررسی دسترسی به زیربخش گزارشات"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return jsonify({'success': False, 'message': 'لطفاً وارد شوید'}), 401
            
            user = session['user']
            perm_key = REPORT_SUB_PERM_MAP.get(sub_page)
            if not perm_key or not user_has_sub_access(user.get('AccessLevelID'), perm_key):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
    