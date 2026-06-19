"""
سامانه جامع دفتر پرستاری
نقطه ورود اصلی برنامه
"""
from models.user_model import user_has_sub_access

from flask import Flask, session, redirect, url_for, request, render_template_string, jsonify, abort
import secrets
from core.auth import login_user, logout_user
from core.router import render_page
from utils.jalali_date import get_today_shamsi

from modules.matron.routes import matron_bp
from modules.riyasat.routes import riyasat_bp
from modules.fanni.routes import fanni_bp
from modules.manager.routes import manager_bp
from modules.admin.routes import admin_bp
from modules.reports.routes import reports_bp
from modules.security.routes import security_bp
from modules.supervisor.routes import supervisor_bp

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# ==================== تنظیمات اولیه ====================

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response



# راه‌اندازی محدودساز نرخ با شناسایی از طریق IP (برای پشت پراکسی هم میتوان کلید را عوض کرد)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["500 per hour", "100 per minute"]  # محدودیت‌های کلی ملایم برای کل سایت
)

# ---------- نگاشت نام انگلیسی ماژول به نام منوی فارسی ----------
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

# ---------- نگاشت زیربخش‌های گزارشات به کلیدهای مجوز ----------
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

def check_module_access(module_name, user):
    if module_name == 'security':
        return True
    menu_name = MODULE_MENU_MAP.get(module_name)
    if not menu_name:
        return False
    return menu_name in user.get('menus', [])

def check_report_sub_access(sub_page, user):
    perm_key = REPORT_SUB_PERM_MAP.get(sub_page)
    if not perm_key:
        return False
    return user_has_sub_access(user.get('AccessLevelID'), perm_key)




# ==================== سیستم ساده ضد CSRF (بدون کتابخانه خارجی) ====================
def generate_csrf_token():
    """تولید یک توکن تصادفی و ذخیره در نشست کاربر"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']
    
@app.before_request
def csrf_protect():
    """بررسی توکن CSRF برای درخواست‌های تغییردهنده (POST, PUT, DELETE)"""
    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        token = None
        
        # ۱. اگر درخواست شامل هدر X-CSRFToken باشد (AJAX)، از آن استفاده کن
        if 'X-CSRFToken' in request.headers:
            token = request.headers.get('X-CSRFToken')
        # ۲. در غیر این صورت (فرم معمولی)، از form data بخوان
        else:
            token = request.form.get('csrf_token')
        
        if not token or token != session.get('_csrf_token'):
            abort(400, description="CSRF token missing or incorrect")

# تزریق تابع تولید توکن به تمام قالب‌ها (Jinja2)
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token())

# ==================== مسیرهای اصلی ====================

@app.route('/static/<path:filename>')
def serve_static(filename):
    from flask import send_from_directory
    return send_from_directory('static', filename)


@app.route('/', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # <-- فقط ۱۰ تلاش در دقیقه برای هر IP
def login_page():
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            error = "⛔ لطفاً نام کاربری و رمز عبور را وارد کنید"
        else:
            user_data, login_error = login_user(username, password)
            if user_data:
                session['user'] = user_data
                return redirect(url_for('dashboard'))
            else:
                error = login_error or "⛔ نام کاربری یا رمز عبور نادرست است"

    return render_page('login', error=error)


@app.route('/dashboard')
def dashboard():
    """داشبورد اصلی"""
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    user = session['user']
    return render_page('dashboard', user=user)


@app.route('/module/<module_name>')
def module_page(module_name):
    """صفحات ماژول‌ها"""
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    user = session['user']
    # ---- کنترل دسترسی ----
    if not check_module_access(module_name, user):
        abort(403)   # دسترسی ممنوع
    # --------------------
    return render_page(module_name, user=user)


@app.route('/module/<module_name>/<sub_page>')
def module_sub_page(module_name, sub_page):
    """صفحات زیرمجموعه ماژول‌ها"""
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    user = session['user']
    # ---- کنترل دسترسی ----
    if not check_module_access(module_name, user):
        abort(403)
    if module_name == 'reports':
        if not check_report_sub_access(sub_page, user):
            abort(403)
    # --------------------
    return render_page(f'module/{module_name}/{sub_page}', user=user)

@app.route('/logout')
def logout():
    """خروج از سیستم"""
    logout_user()
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """سرو فایل‌های آپلود شده"""
    from flask import send_from_directory
    import os
    return send_from_directory('uploads', filename)

# ==================== Route  ====================

app.register_blueprint(matron_bp)
app.register_blueprint(riyasat_bp)
app.register_blueprint(fanni_bp)
app.register_blueprint(manager_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(security_bp)
app.register_blueprint(supervisor_bp)

 
# ====================  فرم ==================== 

#False

# ==================== اجرا ====================
if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════╗
    ║     🏥 سامانه جامع دفتر پرستاری          ║
    ║     http://127.0.0.1:8050                 ║
    ║     📱 http://IP:8050                     ║
    ╚══════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=8050, debug=False, threaded=True)
   
   