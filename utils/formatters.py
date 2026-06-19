"""
توابع فرمت کردن داده‌ها برای نمایش
"""

import jdatetime


def format_date(date_int):
    """تبدیل عدد ۸ رقمی به تاریخ شمسی"""
    if not date_int:
        return "---"
    s = str(int(date_int))
    if len(s) == 8:
        return f"{s[:4]}/{s[4:6]}/{s[6:]}"
    return str(date_int)


def format_time(time_val):
    """فرمت کردن زمان"""
    if not time_val:
        return "---"
    return str(time_val)[:5]


def get_person_fullname(row):
    """نام کامل پرسنل"""
    nam = row.get('nam', '')
    famil = row.get('famil', '')
    return f"{nam} {famil}".strip()


def safe_int(value, default=0):
    """تبدیل امن به عدد"""
    try:
        return int(value) if value is not None else default
    except:
        return default
        
def format_date_display(date_val):
    """
    تبدیل عدد ۸ رقمی شمسی به رشتهٔ YYYY/MM/DD بدون نقص.
    مثال: 14010101 -> '1401/01/01'
    اگر ورودی None باشد یا خالی، '---' برمی‌گرداند.
    """
    if date_val is None or str(date_val).strip() == '':
        return '---'
    try:
        # تبدیل به عدد و سپس رشته ۸ رقمی با صفرهای سمت چپ
        num = int(date_val)
        s = str(num).zfill(8)
    except (ValueError, TypeError):
        return str(date_val)
    if len(s) != 8:
        return str(date_val)
    return f"{s[:4]}/{s[4:6]}/{s[6:]}"
    