"""
مسیریابی و رندر صفحات - نسخه کامل و نهایی با سایدبار شیشه‌ای
"""

from flask import render_template_string, session, abort
from utils.jalali_date import get_today_shamsi
from layouts.components.sidebar import get_sidebar_html
from layouts.components.navbar import get_header_html
from models.user_model import user_has_sub_access
import secrets
from markupsafe import escape 

from flask import render_template, session



from flask import render_template

# ==================== نگاشت‌های دسترسی ====================
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





def get_user_menus(role):
    # اینجا لیست منوها را به صورت لیستی از دیکشنری‌ها تعریف می‌کنیم
    # این جایگزین MODULE_MENU_MAP قدیمی شما می‌شود
    all_menus = {
        'admin': [
            {'title': 'مدیریت کاربران', 'url': '/admin/users', 'icon': '👥'},
            {'title': 'گزارشات سیستمی', 'url': '/admin/logs', 'icon': '📊'}
        ],
        'supervisor': [
            {'title': 'ثبت گزارش شیفت', 'url': '/supervisor/report', 'icon': '📝'},
            {'title': 'مشاهده پانل', 'url': '/supervisor/panel', 'icon': '💻'}
        ]
        # بقیه نقش‌ها را اینجا اضافه کنید...
    }
    return all_menus.get(role, [])


def check_module_access(module_name, user):
    """بررسی می‌کند که کاربر به یک ماژول دسترسی دارد یا خیر.
       ماژول 'security' برای همه در دسترس است (تغییر رمز عبور)."""
    if module_name == 'security':
        return True
    menu_name = MODULE_MENU_MAP.get(module_name)
    if not menu_name:
        return False
    return menu_name in user.get('menus', [])


def check_report_sub_access(sub_page, user):
    """بررسی می‌کند که کاربر به یک زیربخش خاص از گزارشات دسترسی دارد یا خیر."""
    perm_key = REPORT_SUB_PERM_MAP.get(sub_page)
    if not perm_key:
        return False
    return user_has_sub_access(user.get('AccessLevelID'), perm_key)


# ==================== رندر صفحات ماژول‌ها ====================
def get_module_html(module_name, user, sub_page=None):
    """
    دریافت HTML ماژول با مدیریت خطا و زیرصفحات
    
    Args:
        module_name: نام ماژول (supervisor, matron, ...)
        user: اطلاعات کاربر
        sub_page: زیرصفحه (shift, attendance, ...)
    
    Returns:
        str: HTML
    """
    
    # ========== سوپروایزر ==========
    if module_name == 'supervisor':
        try:
            from modules.supervisor.views import get_page
            return get_page(user, sub_page)
        except Exception as e:
            print(f"[ROUTER] Error loading supervisor: {e}")
            import traceback
            traceback.print_exc()
    
    # ========== مترون ==========
    elif module_name == 'matron':
        try:
            from modules.matron.views import get_page
            return get_page(user, sub_page)
        except Exception as e:
            print(f"[ROUTER] Error loading matron: {e}")
            import traceback
            traceback.print_exc()
    
    # ========== ریاست ==========
    elif module_name == 'riyasat':
        try:
            from modules.riyasat.views import get_page
            return get_page(user, sub_page)
        except Exception as e:
            print(f"[ROUTER] Error loading riyasat: {e}")
            import traceback
            traceback.print_exc()
    
    # ========== مسئول فنی ==========
    elif module_name == 'fanni':
        try:
            from modules.fanni.views import get_page
            return get_page(user, sub_page)
        except Exception as e:
            print(f"[ROUTER] Error loading fanni: {e}")
            import traceback
            traceback.print_exc()
    
    # ========== مدیران اجرایی ==========
    elif module_name == 'manager':
        try:
            from modules.manager.views import get_page
            return get_page(user, sub_page)
        except Exception as e:
            print(f"[ROUTER] Error loading manager: {e}")
            import traceback
            traceback.print_exc()
    
    # ========== ادمین ==========
    elif module_name == 'admin':
        try:
            from modules.admin.views import get_page
            return get_page(user, sub_page)
        except Exception as e:
            print(f"[ROUTER] Error loading admin: {e}")
            import traceback
            traceback.print_exc()
    
    # ========== امنیت ==========
    elif module_name == 'security':
        from modules.security.views import get_security_page
        return get_security_page(user)
    
    # ========== گزارشات ==========
    elif module_name == 'reports':
        from modules.reports.views import get_page
        return get_page(user, sub_page)
    
    # ========== صفحه پیش‌فرض برای ماژول‌های تعریف نشده ==========
    return f'''
    <div class="content-card fade-in">
        <div style="text-align:center; padding:60px 20px;">
            <p style="font-size:48px;">🚧</p>
            <p style="color:#94a3b8; margin-top:15px; font-size:16px;">
                این بخش در حال توسعه است
            </p>
            <p style="color:#cbd5e1; font-size:13px; margin-top:5px;">
                به زودی تکمیل خواهد شد
            </p>
        </div>
    </div>
    '''


def get_main_styles():
    """دریافت استایل‌های اصلی برنامه"""
    return '''
    <style>
                    
            /* افزودن فونت وزیرمتن */
            @font-face {
                font-family: 'Vazirmatn';
                src: url('/static/fonts/vazirmatn/Vazirmatn-Regular.woff2') format('woff2');
                font-weight: normal;
                font-style: normal;
                font-display: swap;
            }

            @font-face {
                font-family: 'Vazirmatn';
                src: url('/static/fonts/vazirmatn/Vazirmatn-Bold.woff2') format('woff2');
                font-weight: bold;
                font-style: normal;
                font-display: swap;
            }

            /* همچنین برای وزن‌های دیگر (اختیاری) – اگر فایل‌های Medium, Black و... دارید */
            @font-face {
                font-family: 'Vazirmatn';
                src: url('/static/fonts/vazirmatn/Vazirmatn-Medium.woff2') format('woff2');
                font-weight: 500;
                font-style: normal;
                font-display: swap;
            }        
                
        :root {
            --sidebar-w: 280px;
            --header-h: 65px;
            --glass-bg: rgba(17, 25, 40, 0.75);
            --glass-border: rgba(255, 255, 255, 0.125);
            --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            --primary: #3b82f6;
            --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
             font-family: 'Vazirmatn', Tahoma, Arial, sans-serif !important;
            direction: rtl;
            background: #f1f5f9;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        a { text-decoration: none; color: inherit; }
        ul { list-style: none; }
        
        .app-wrapper {
            display: flex;
            min-height: 100vh;
        }
        
        /* ========== سایدبار شیشه‌ای ========== */
        .glass-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            width: var(--sidebar-w);
            background: transparent;
            z-index: 1000;
            overflow-y: auto;
            overflow-x: hidden;
            transition: transform var(--transition), opacity var(--transition);
            display: flex;
            flex-direction: column;
        }
        
        .glass-bg {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--glass-bg);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border-left: 1px solid var(--glass-border);
            box-shadow: var(--glass-shadow);
        }
        
        /* ========== برند ========== */
        .sidebar-brand {
            position: relative;
            z-index: 1;
            padding: 2rem 1.5rem 1.5rem;
            text-align: center;
        }
        
        .brand-icon {
            font-size: 2.5rem;
            color: #fff;
            margin-bottom: 0.5rem;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .sidebar-brand h3 {
            color: #fff;
            font-size: 1.1rem;
            margin: 0;
            font-weight: 600;
        }
        
        .brand-line {
            width: 40px;
            height: 3px;
            background: linear-gradient(to left, #3b82f6, #8b5cf6);
            margin: 0.8rem auto 0;
            border-radius: 3px;
        }
        
        /* ========== کارت کاربر ========== */
        .sidebar-user-card {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.5rem;
            margin: 0 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .user-avatar-wrapper {
            position: relative;
            flex-shrink: 0;
        }
        
        .user-avatar {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .online-indicator {
            position: absolute;
            bottom: -2px;
            right: -2px;
            width: 14px;
            height: 14px;
            background: #10b981;
            border: 2px solid rgba(17, 25, 40, 0.75);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        
        .user-name {
            color: #fff;
            font-size: 0.9rem;
            font-weight: 500;
            margin: 0;
        }
        
        .user-status {
            display: flex;
            align-items: center;
            gap: 0.3rem;
            margin-top: 2px;
        }
        
        .status-dot {
            width: 6px;
            height: 6px;
            background: #10b981;
            border-radius: 50%;
        }
        
        .user-status small {
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.75rem;
        }
        
        /* ========== منو ========== */
        .sidebar-menu {
            position: relative;
            z-index: 1;
            margin-top: 1.5rem;
            padding: 0 1rem;
            flex: 1;
        }
        
        .menu-label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            color: rgba(255, 255, 255, 0.4);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        .sidebar-nav {
            list-style: none;
            padding: 0;
            margin: 0.5rem 0;
        }
        
        .sidebar-nav-item {
            margin-bottom: 0.3rem;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: all var(--transition);
            position: relative;
            overflow: hidden;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.08);
            color: #fff;
            transform: translateX(-5px);
        }
        
        .nav-link.active {
            background: rgba(59, 130, 246, 0.15);
            color: #fff;
        }
        
        .nav-icon {
            width: 35px;
            height: 35px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            flex-shrink: 0;
            transition: all var(--transition);
        }
        
        .nav-link:hover .nav-icon {
            transform: scale(1.1);
        }
        
        .nav-text {
            font-size: 0.875rem;
            font-weight: 500;
            white-space: nowrap;
        }
        
        .nav-indicator {
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 0;
            border-radius: 3px;
            transition: height var(--transition);
        }
        
        .nav-link:hover .nav-indicator,
        .nav-link.active .nav-indicator {
            height: 20px;
        }
        
        /* ========== فوتر ========== */
        .sidebar-footer {
            position: relative;
            z-index: 1;
            padding: 1rem;
            margin-top: auto;
        }
        
        .logout-btn {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            color: rgba(239, 68, 68, 0.8);
            text-decoration: none;
            transition: all var(--transition);
        }
        
        .logout-btn:hover {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
        }
        
        /* ========== Overlay ========== */
        .sidebar-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            z-index: 999;
        }
        
        .sidebar-overlay.show {
            display: block;
        }
        
        /* ========== محتوای اصلی ========== */
        .main-content {
            margin-right: var(--sidebar-w);
            flex: 1;
            min-height: 100vh;
            padding: 1.5rem;
        }
        
        .content-area {
            margin-top: 1rem;
        }
        
        /* ========== هدر ========== */
        .top-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.5rem;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .hamburger-btn {
            display: none;
            width: 40px;
            height: 40px;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1.2rem;
            cursor: pointer;
            align-items: center;
            justify-content: center;
        }
        
        .header-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .header-date {
            font-size: 0.875rem;
            color: #64748b;
            background: #f8fafc;
            padding: 0.5rem 1rem;
            border-radius: 2rem;
        }
        
        .header-user {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
            color: #1e293b;
        }
        
        .header-avatar {
            width: 35px;
            height: 35px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 0.875rem;
        }
        
        /* ========== کارت‌های محتوا ========== */
        .content-card {
            background: white;
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* ========== رسپانسیو ========== */
        @media (max-width: 992px) {
            .glass-sidebar {
                transform: translateX(100%);
            }
            
            .glass-sidebar.open {
                transform: translateX(0);
            }
            
            .main-content {
                margin-right: 0;
            }
            
            .hamburger-btn {
                display: flex;
            }
        }
        
        @media (max-width: 576px) {
            .header-date {
                display: none;
            }
            
            .main-content {
                padding: 1rem;
            }
        }
    </style>
    '''


def get_sidebar_html(user):
    """دریافت HTML سایدبار شیشه‌ای (fallback در صورت نبود فایل کامپوننت)"""
    try:
        from layouts.components.sidebar import get_sidebar_html as sidebar_func
        return sidebar_func(user)
    except (ImportError, AttributeError):
        return _build_sidebar_fallback(user)


def _build_sidebar_fallback(user):
    """ساخت سایدبار به صورت مستقیم (fallback)"""
    full_name = user.get('FullName', 'کاربر')
    full_name_safe = escape(full_name)
    menus = user.get('menus', [])
    
    menu_map = {
        "👨‍⚕️ سوپروایزر": {"icon": "fa-stethoscope", "route": "/module/supervisor", "color": "#3b82f6"},
        "📋 مدیر پرستاری": {"icon": "fa-clipboard-list", "route": "/module/matron", "color": "#8b5cf6"},
        "👔 مدیران اجرایی": {"icon": "fa-users", "route": "/module/manager", "color": "#10b981"},
        "🏢 ریاست": {"icon": "fa-building", "route": "/module/riyasat", "color": "#f59e0b"},
        "🛠️ مسئول فنی": {"icon": "fa-tools", "route": "/module/fanni", "color": "#ef4444"},
        "⚙️ ادمین": {"icon": "fa-cogs", "route": "/module/admin", "color": "#6366f1"},
        "📊 گزارشات": {"icon": "fa-chart-bar", "route": "/module/reports", "color": "#14b8a6"},
        "🔑 امنیت": {"icon": "fa-lock", "route": "/module/security", "color": "#f97316"},
    }
    
    menu_items = ""
    for menu_name in menus:
        config = menu_map.get(menu_name, {"icon": "fa-circle", "route": "#", "color": "#94a3b8"})
        menu_items += f'''
        <li class="sidebar-nav-item">
            <a href="{config['route']}" class="nav-link">
                <span class="nav-icon" style="background: {config['color']}20; color: {config['color']};">
                    <i class="fas {config['icon']}"></i>
                </span>
                <span class="nav-text">{menu_name}</span>
                <span class="nav-indicator" style="background: {config['color']};"></span>
            </a>
        </li>
        '''
    
    return f'''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <aside class="sidebar glass-sidebar" id="sidebar">
        <div class="glass-bg"></div>
        
        <div class="sidebar-brand">
            <div class="brand-icon">
                <i class="fas fa-hospital"></i>
            </div>
            <h3>دفتر پرستاری</h3>
            <div class="brand-line"></div>
        </div>
        
        <!-- منو -->        
        <div class="sidebar-menu">
            <div class="menu-label">
                <i class="fas fa-compass"></i>
                <span>منوی اصلی</span>
            </div>
            
            <ul class="sidebar-nav">
                <li class="sidebar-nav-item">
                    <a href="/dashboard" class="nav-link active">
                        <span class="nav-icon" style="background: #3b82f620; color: #3b82f6;">
                            <i class="fas fa-home"></i>
                        </span>
                        <span class="nav-text">داشبورد</span>
                        <span class="nav-indicator" style="background: #3b82f6;"></span>
                    </a>
                </li>
                {menu_items}
            </ul>
        </div>
        
        <div class="sidebar-footer">
            <a href="/logout" class="logout-btn">
                <i class="fas fa-sign-out-alt"></i>
                <span>خروج از حساب</span>
            </a>
        </div>
    </aside>
    
    <div class="sidebar-overlay" id="overlay"></div>
    '''


def render_page(page_name, **kwargs):
    try:
        if page_name == 'login':
            from layouts.login_layout import LOGIN_HTML, get_hospital_logo
            logo_path = get_hospital_logo()
            kwargs['logo_url'] = f"/{logo_path}" if logo_path else None
            token = session.get('_csrf_token')
            if not token:
                token = secrets.token_hex(32)
                session['_csrf_token'] = token
            kwargs['csrf_token'] = token
            return render_template_string(LOGIN_HTML, **kwargs)        
         
        user = kwargs.get('user', {})
        if user and 'FullName' in user:
            user['FullName'] = escape(user['FullName'])
        date = get_today_shamsi()
        return build_dashboard_html(user, date, page_name)
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] {error_detail}")
        return f"""
        <div style="padding:50px;text-align:center;font-family:Tahoma;">
            <h1 style="color:red;">⚠️ خطای سیستمی</h1>
            <pre style="direction:ltr;text-align:left;background:#f5f5f5;padding:20px;border-radius:10px;overflow:auto;">{error_detail}</pre>
        </div>
        """


def build_dashboard_html(user, date, page_name='dashboard'):
    sidebar_html = get_sidebar_html(user)
    header_html = get_header_html(user)
    
    if page_name == 'dashboard':
        from layouts.dashboard_layout import get_dashboard_html
        page_content = get_dashboard_html()
    elif page_name.startswith('module/'):
        parts = page_name.replace('module/', '').split('/')
        module_name = parts[0]
        sub_page = parts[1] if len(parts) > 1 else None
        page_content = get_module_html(module_name, user, sub_page)
    else:
        page_content = get_module_html(page_name, user)

    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_hex(32)
        session['_csrf_token'] = token

    html = f'''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>دفتر پرستاری</title>
        {get_main_styles()}
        <meta name="csrf-token" content="{token}">
    </head>
    <body>
        <div class="app-wrapper">
            {sidebar_html}
            <main class="main-content">
                {header_html}
                <div class="content-area fade-in">
                    {page_content}
                </div>
            </main>
        </div>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const tokenMeta = document.querySelector('meta[name="csrf-token"]');
                if (!tokenMeta) return;
                const csrfToken = tokenMeta.content;

                document.querySelectorAll('form[method="post"], form[method="POST"]').forEach(form => {{
                    if (!form.querySelector('input[name="csrf_token"]')) {{
                        const input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = 'csrf_token';
                        input.value = csrfToken;
                        form.appendChild(input);
                    }}
                }});

                const originalFetch = window.fetch;
                window.fetch = function(input, init) {{
                    init = init || {{}};
                    if (init.headers && typeof init.headers.get !== 'function') {{
                        init.headers = new Headers(init.headers);
                    }} else if (!init.headers) {{
                        init.headers = new Headers();
                    }}
                    if (!init.headers.get('X-CSRFToken')) {{
                        init.headers.set('X-CSRFToken', csrfToken);
                    }}
                    return originalFetch.call(this, input, init);
                }};
            }});
            
            function toggleSidebar() {{
                document.getElementById('sidebar').classList.toggle('open');
                document.getElementById('overlay').classList.toggle('show');
            }}
            
            function closeSidebar() {{
                document.getElementById('sidebar').classList.remove('open');
                document.getElementById('overlay').classList.remove('show');
            }}
            
            document.getElementById('overlay').addEventListener('click', closeSidebar);
            
            document.querySelectorAll('.nav-link').forEach(function(link) {{
                link.addEventListener('click', function() {{
                    if (window.innerWidth <= 992) {{
                        closeSidebar();
                    }}
                }});
            }});
            
            const currentPath = window.location.pathname;
            document.querySelectorAll('.nav-link').forEach(function(link) {{
                if (link.getAttribute('href') === currentPath) {{
                    link.classList.add('active');
                }}
            }});
            
                        
            // ========== اعتبارسنجی تاریخ شمسی (YYYY/MM/DD) ==========
            function validateShamsiDate(dateStr) {{
                if (!dateStr || dateStr.trim() === '') {{
                    return {{ valid: false, message: 'تاریخ نمی‌تواند خالی باشد' }};
                }}
                var parts = dateStr.split('/');
                if (parts.length !== 3) {{
                    return {{ valid: false, message: 'فرمت تاریخ باید YYYY/MM/DD باشد' }};
                }}
                var y = parseInt(parts[0]), m = parseInt(parts[1]), d = parseInt(parts[2]);
                if (isNaN(y) || isNaN(m) || isNaN(d)) {{
                    return {{ valid: false, message: 'سال/ماه/روز باید عددی باشند' }};
                }}
                if (y < 1300 || y > 1500) {{
                    return {{ valid: false, message: 'سال باید بین ۱۳۰۰ تا ۱۵۰۰ باشد' }};
                }}
                if (m < 1 || m > 12) {{
                    return {{ valid: false, message: 'ماه باید بین ۱ تا ۱۲ باشد' }};
                }}
                if (d < 1 || d > 31) {{
                    return {{ valid: false, message: 'روز باید بین ۱ تا ۳۱ باشد' }};
                }}
                var daysInMonth = (m <= 6) ? 31 : (m <= 11) ? 30 : (isLeapShamsi(y) ? 30 : 29);
                if (d > daysInMonth) {{
                    return {{ valid: false, message: 'این ماه حداکثر ' + daysInMonth + ' روز دارد' }};
                }}
                return {{ valid: true }};
            }}
            function isLeapShamsi(year) {{
                var y = year - 474;
                return ((y % 2820 === 2819) || ((y % 128 === 0) && (y % 2820 !== 0)) || ((y % 33 === 31) && (y % 132 !== 127)));
            }}            
                        
            
        </script>
    </body>
    </html>
    '''
    return html
    