"""
تقویم شمسی میلادی - توابع کمکی
"""

import jdatetime
from datetime import datetime


def get_today_shamsi():
    """دریافت تاریخ امروز شمسی"""
    return jdatetime.date.today().strftime("%Y/%m/%d")


def get_today_shamsi_formatted():
    """دریافت تاریخ امروز با فرمت خوانا"""
    now = jdatetime.datetime.now()
    weekdays = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
    months = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    return f"{weekdays[now.weekday()]} {now.day} {months[now.month-1]} {now.year}"


def shamsi_to_miladi(shamsi_date):
    """تبدیل تاریخ شمسی به میلادی"""
    try:
        parts = shamsi_date.replace('/', '-').split('-')
        if len(parts) == 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            miladi = jdatetime.date(y, m, d).togregorian()
            return miladi.strftime("%Y-%m-%d")
    except:
        pass
    return shamsi_date


def miladi_to_shamsi(miladi_date):
    """تبدیل تاریخ میلادی به شمسی"""
    try:
        if isinstance(miladi_date, str):
            miladi_date = datetime.strptime(miladi_date, "%Y-%m-%d").date()
        shamsi = jdatetime.date.fromgregorian(date=miladi_date)
        return shamsi.strftime("%Y/%m/%d")
    except:
        return str(miladi_date)


def validate_shamsi_date(date_str):
    """اعتبارسنجی تاریخ شمسی"""
    try:
        parts = str(date_str).replace('/', '-').split('-')
        if len(parts) != 3:
            return False
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        jdatetime.date(y, m, d)
        return True
    except:
        return False


def get_shamsi_days_in_month(year, month):
    """تعداد روزهای یک ماه شمسی"""
    try:
        if month < 7:
            return 31
        elif month < 12:
            return 30
        else:
            return 30 if jdatetime.date(year, 12, 30).isleap() else 29
    except:
        return 30


def get_shamsi_month_name(month):
    """نام فارسی ماه شمسی"""
    months = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    return months[month - 1] if 1 <= month <= 12 else ""


def get_persian_date_input_html(input_id="date-input", input_name="date", 
                                 default_date=None, placeholder="انتخاب تاریخ",
                                 required=True, onchange=""):
    """
    ساخت input تاریخ شمسی با امکان تایپ دستی
    
    این تابع یک input ساده می‌سازد که کاربر می‌تواند:
    ۱. تاریخ را دستی تایپ کند (YYYY/MM/DD)
    ۲. راهنمای فرمت تاریخ را ببیند
    """
    
    today = get_today_shamsi() if default_date is None else default_date
    
    html = f'''
    <div class="form-group">
        <label>📅 تاریخ</label>
        <div style="position:relative;">
            <input 
                type="text" 
                name="{input_name}" 
                id="{input_id}" 
                class="form-input shamsi-date-input" 
                value="{today}" 
                placeholder="{placeholder}"
                {'required' if required else ''}
                onchange="{onchange}"
                autocomplete="off"
                dir="ltr"
                style="text-align:left;direction:ltr;"
            >
            <span style="
                position:absolute;
                left:12px;
                top:50%;
                transform:translateY(-50%);
                pointer-events:none;
                font-size:16px;
                color:#94a3b8;
            ">📆</span>
        </div>
        <small>فرمت: YYYY/MM/DD - مثال: {today}</small>
    </div>
    '''
    
    return html


def get_persian_datepicker_script():
    """
    اسکریپت سمت کاربر برای اعتبارسنجی و فرمت خودکار تاریخ شمسی
    
    این اسکریپت کارهای زیر را انجام می‌دهد:
    ۱. هنگام تایپ، / را خودکار اضافه می‌کند
    ۲. فقط اعداد و / را قبول می‌کند
    ۳. اعتبارسنجی اولیه انجام می‌دهد
    """
    
    return '''
    <script>
        // ========== ماسک خودکار تاریخ شمسی ==========
        document.addEventListener('DOMContentLoaded', function() {
            var dateInputs = document.querySelectorAll('.shamsi-date-input');
            
            dateInputs.forEach(function(input) {
                input.addEventListener('input', function(e) {
                    var value = this.value.replace(/[^0-9]/g, '');
                    
                    // حداکثر ۸ رقم
                    if (value.length > 8) {
                        value = value.substring(0, 8);
                    }
                    
                    // اضافه کردن / خودکار
                    var formatted = '';
                    if (value.length > 0) {
                        formatted = value.substring(0, 4);
                        if (value.length > 4) {
                            formatted += '/' + value.substring(4, 6);
                        }
                        if (value.length > 6) {
                            formatted += '/' + value.substring(6, 8);
                        }
                    }
                    
                    this.value = formatted;
                });
                
                // اعتبارسنجی در خروج از فیلد
                input.addEventListener('blur', function() {
                    var value = this.value.replace(/[^0-9]/g, '');
                    if (value.length > 0 && value.length < 8) {
                        this.style.borderColor = '#f59e0b';
                        this.style.backgroundColor = '#fef3c7';
                    } else if (value.length === 8) {
                        this.style.borderColor = '#e2e8f0';
                        this.style.backgroundColor = '#fff';
                    }
                });
                
                // برگشت به حالت عادی در فوکوس
                input.addEventListener('focus', function() {
                    this.style.borderColor = '#3b82f6';
                    this.style.backgroundColor = '#fff';
                });
            });
        });
    </script>
    '''