"""
مدل کاربران - تمام کوئری‌های مربوط به users
سازگار با تمام نسخه‌های Werkzeug و MySQL Connector
"""

from models.database import query
from werkzeug.security import check_password_hash, generate_password_hash


def _ensure_str(value):
    """
    تبدیل مقدار به رشته (str) صرف‌نظر از نوع ورودی.
    این تابع مشکل ناسازگاری bytes/str در نسخه‌های مختلف Werkzeug و MySQL Connector را حل می‌کند.
    """
    if value is None:
        return ''
    if isinstance(value, bytes):
        return value.decode('utf-8')
    if isinstance(value, bytearray):
        return value.decode('utf-8')
    if isinstance(value, memoryview):
        return value.tobytes().decode('utf-8')
    return str(value)


def authenticate(username, password):
    """
    احراز هویت کاربر
    Returns:
        (user_dict, None) : در صورت موفقیت
        (None, error_message) : در صورت شکست
    """
    from models.database import get_connection
    import mysql.connector

    # 1. تست اتصال به دیتابیس
    conn = get_connection()
    if not conn:
        return None, "⛔ خطا در اتصال به پایگاه داده. لطفاً بعداً تلاش کنید."

    # 2. واکشی کاربر با دستور مستقیم
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT UserID, Username, PasswordHash, FullName, AccessLevelID, IsActive, postmodir
               FROM users WHERE Username = %s""",
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()
    except mysql.connector.Error as e:
        print(f"[AUTH] Database error: {e}")
        return None, "⛔ خطا در اتصال به پایگاه داده. لطفاً بعداً تلاش کنید."
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # 3. کاربر وجود ندارد یا غیرفعال است
    if not user or user.get('IsActive') != 1:
        return None, "⛔ نام کاربری یا رمز عبور نادرست است"

    # 4. تبدیل PasswordHash به رشته (حل مشکل bytes/str در Werkzeug ≥ 3.0)
    stored = _ensure_str(user.get('PasswordHash', ''))

    # 5. بررسی رمز عبور با Werkzeug
    try:
        if check_password_hash(stored, password):
            return user, None
    except (TypeError, ValueError, AttributeError):
        # در صورت بروز هرگونه خطای غیرمنتظره در بررسی هش
        pass

    # 6. fallback برای رمزهای plaintext قدیمی (در صورت وجود)
    stored_plain = _ensure_str(user.get('PasswordHash', ''))
    if stored_plain and stored_plain == password:
        # ارتقاء به هش امن
        try:
            new_hash = generate_password_hash(password)
            query(
                "UPDATE users SET PasswordHash = %s WHERE UserID = %s",
                (new_hash, user['UserID']),
                commit=True
            )
        except Exception:
            pass
        return user, None

    return None, "⛔ نام کاربری یا رمز عبور نادرست است"


def get_user_menus(access_level_id):
    """
    دریافت منوهای مجاز برای یک سطح دسترسی
    
    Returns:
        list: لیست نام منوها
    """
    sql = """
        SELECT TableName 
        FROM userlevelpermissions 
        WHERE UserLevelID = %s AND Permission = 1
    """
    results = query(sql, params=(access_level_id,), fetch_all=True)
    
    if results:
        return [_ensure_str(r.get('TableName', '')) for r in results]
    return []


def get_user_by_id(user_id):
    """دریافت اطلاعات کاربر با ID"""
    sql = "SELECT * FROM users WHERE UserID = %s"
    user = query(sql, params=(user_id,), fetch_one=True)
    
    if user:
        # تبدیل تمام مقادیر باینری به str
        clean_user = {}
        for key, value in user.items():
            clean_user[key] = _ensure_str(value) if isinstance(value, (bytes, bytearray, memoryview)) else value
        return clean_user
    return None


# ========= ثابت‌ها و توابع زیربخش =========

SUB_PAGE_PERMISSIONS = {
    # گزارشات
    'reports_ankal': 'گزارش آنکال',
    'reports_blood': 'گزارش خون',
    'reports_codes': 'گزارش کدها',
    'reports_crisis': 'گزارش بحران',
    'reports_attendance': 'گزارش حضور و غیاب',
    'reports_workflow': 'گزارش گردش کار',
    'reports_rounds': 'گزارش راندها',
    'reports_stats': 'گزارش آمار',

    # 🆕 کارت‌های پنل مدیران اجرایی
    'manager_reports':          '📋 کارتابل مدیران',
    'manager_management_reports': '📊 گزارشات مدیریتی',
    'manager_shifts':           '🗓️ برنامه شیفت ماهیانه',
    'manager_shift_review':     '✅ تایید شیفت‌بندی',
    'manager_shift_comparison': '⚖️ مقایسه شیفت و حضور',
    'manager_shift_edit':       '🔧 ویرایش پیشرفته شیفت',

    # 🆕 کارت‌های پنل مترون
    'matron_reports':   '📋 گزارشات سوپروایزر (مترون)',
    'matron_personnel': '👥 مدیریت پرسنل (مترون)',
    'matron_checklist': '⚙️ تنظیمات چک‌لیست (مترون)',
    'matron_codes':     '🚑 کدهای عملیاتی (مترون)',
    
    # 🆕 کارت‌های پنل سوپروایزر
    'supervisor_shift':      '📅 تنظیم شیفت (سوپروایزر)',
    'supervisor_attendance': '👥 حاضرین (سوپروایزر)',
    'supervisor_gozaresh':   '📝 گزارشات (سوپروایزر)',
    'supervisor_rounds':     '🔍 راند (سوپروایزر)',
    'supervisor_ankal':      '📞 آنکال (سوپروایزر)',
    'supervisor_amar':       '📊 آمار (سوپروایزر)',
    'supervisor_ghaybat':    '❌ غیبت (سوپروایزر)',
    'supervisor_blood':      '🩸 خون (سوپروایزر)',
    'supervisor_codes':      '🚑 کدها (سوپروایزر)',
    'supervisor_crisis':     '🚨 بحران (سوپروایزر)',
    
    # در آینده برای ماژول‌های دیگر اینجا اضافه کنید
}


def user_has_sub_access(access_level_id, sub_perm_key):
    """بررسی مجوز دسترسی به یک زیربخش خاص"""
    sql = "SELECT 1 FROM userlevelpermissions WHERE UserLevelID = %s AND TableName = %s AND Permission = 1"
    return query(sql, (access_level_id, sub_perm_key), fetch_one=True) is not None
    
    