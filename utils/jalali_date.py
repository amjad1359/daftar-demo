"""
توابع تبدیل تاریخ شمسی
"""

import jdatetime
from datetime import datetime

import re

def normalize_shamsi_date(date_str):
    """
    تبدیل تاریخ شمسی با فرمت‌های مختلف به فرمت استاندارد YYYY/MM/DD
    ورودی می‌تواند: 14010101 , 1401/01/01 , 1401-01-01 , 1401/1/1
    خروجی: رشته "1401/01/01" یا None در صورت نامعتبر بودن
    """
    if not date_str:
        return None
    # حذف کاراکترهای غیر عددی
    digits = re.sub(r'\D', '', str(date_str))
    if len(digits) != 8:
        return None
    year = digits[0:4]
    month = digits[4:6]
    day = digits[6:8]
    # بررسی اعتبار با jdatetime
    try:
        jdatetime.date(int(year), int(month), int(day))
        return f"{year}/{month}/{day}"
    except:
        return None

def is_valid_shamsi_date(date_str):
    """برگرداندن True/False برای اعتبار تاریخ"""
    return normalize_shamsi_date(date_str) is not None

def shamsi_to_int(date_str):
    """تبدیل تاریخ شمسی به عدد ۸ رقمی (مثل 14010101)"""
    norm = normalize_shamsi_date(date_str)
    if norm:
        return int(norm.replace('/', ''))
    return None




def get_today_shamsi():
    """دریافت تاریخ امروز به فارسی"""
    now = jdatetime.datetime.now()
    
    # اصلاح: jdatetime.weekday() از 0=شنبه شروع میشه
    weekdays = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
    
    months = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    # jdatetime weekday: 0=شنبه, 1=یکشنبه, ...
    return f"{weekdays[now.weekday()]} {now.day} {months[now.month-1]} {now.year}"


def format_date(date_int):
    """تبدیل عدد ۸ رقمی به تاریخ شمسی"""
    if not date_int:
        return ""
    s = str(int(date_int))
    if len(s) == 8:
        return f"{s[:4]}/{s[4:6]}/{s[6:]}"
    return s


def get_today_int():
    """دریافت تاریخ امروز به صورت عدد ۸ رقمی"""
    return int(jdatetime.date.today().strftime("%Y%m%d"))


def get_current_time():
    """دریافت ساعت فعلی"""
    return jdatetime.datetime.now().strftime("%H:%M:%S")
    