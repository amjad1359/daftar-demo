"""
کامپوننت هدر - نوار بالای صفحه
"""


from utils.jalali_date import get_today_shamsi
from models.database import query
from markupsafe import escape

from markupsafe import escape
from utils.jalali_date import get_today_shamsi
from models.database import query

def get_header_html(user):
    """
    کامپوننت هدر - نوار بالای صفحه
    نمایش لوگو، نام مرکز درمانی، تاریخ شمسی و مشخصات کاربر به صورت ایمن
    """
    
    # ۱. استخراج امن نام کاربر (جلوگیری از خطای TypeError در صورت Null بودن فیلد دیتابیس)
    full_name = 'کاربر'
    if user and isinstance(user, dict):
        user_fullname = user.get('FullName')
        if user_fullname and str(user_fullname).strip():
            full_name = str(user_fullname).strip()
            
    full_name_safe = escape(full_name) # ایمن‌سازی در برابر XSS
    today = get_today_shamsi()

    # ۲. تنظیم مقادیر پیش‌فرض مرکز (اگر اسمی در دیتابیس نبود، نام قبلی نشان داده می‌شود)
    center_name = 'سامانه دفتر پرستاری'
    sub_center_name = ''
    logo_path = None

    try:
        # دریافت لوگوی بیمارستان
        res_logo = query("SELECT setting_value FROM site_settings WHERE setting_key = 'hospital_logo'", fetch_one=True)
        if res_logo and res_logo.get('setting_value'):
            logo_path = res_logo['setting_value']
            
        # دریافت نام مرکز اصلی (تنها در صورت پر بودن جایگزین نام پیش‌فرض می‌شود)
        res_center = query("SELECT setting_value FROM site_settings WHERE setting_key = 'center_name'", fetch_one=True)
        if res_center and res_center.get('setting_value') and res_center['setting_value'].strip():
            center_name = res_center['setting_value'].strip()
            
        # دریافت نام مرکز زیرمجموعه (بیمارستان)
        res_sub = query("SELECT setting_value FROM site_settings WHERE setting_key = 'sub_center_name'", fetch_one=True)
        if res_sub and res_sub.get('setting_value') and res_sub['setting_value'].strip():
            sub_center_name = res_sub['setting_value'].strip()
    except Exception:
        pass # در صورت بروز هرگونه خطای دیتابیس، هدر با اطلاعات پیش‌فرض بدون کرش کردن بالا می‌آید

    # ۳. ترکیب ساختار نام مراکز برای خروجی نهایی
    if sub_center_name:
        display_title = f"{center_name} - {sub_center_name}"
    else:
        display_title = center_name

    # ۴. تعیین محتوای عنوان (لوگو یا ایموجی پیش‌فرض)
    if logo_path:
        title_content = f'<img src="/{logo_path}" alt="لوگو" style="height:45px; margin-left:12px; vertical-align:middle;"> {display_title}'
    else:
        title_content = f'🏥 {display_title}'

    # ۵. تولید نهایی قالب HTML با ساختار تمیز و اصلاح‌شده
    header_html = f'''
    <header class="top-header">
        <button class="hamburger-btn" onclick="toggleSidebar()">
            ☰
        </button>

        <div style="display:flex; align-items:center; gap:6px;">
            <h4 style="font-size: 1.1rem; color: #1e293b; margin: 0; display:flex; align-items:center;">
                {title_content}
            </h4>
        </div>

        <div class="header-info">
            <span class="header-date">{today}</span>
            <div class="header-user">
                <div class="header-avatar">{full_name_safe[0] if full_name_safe else '?'}</div>
                <span>{full_name_safe}</span>
            </div>
        </div>
    </header>
    '''
    return header_html