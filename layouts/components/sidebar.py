"""
کامپوننت سایدبار شیشه‌ای - نسخه مدرن با Glassmorphism
"""
from markupsafe import escape

def get_sidebar_html(user):
    """تولید HTML سایدبار شیشه‌ای"""
    
    full_name = user.get('FullName', 'کاربر')
    full_name_safe = escape(full_name)  # ← ایمن‌سازی
    menus = user.get('menus', [])
    
    # نگاشت نام منو به آیکون و route
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
    
    # ساخت آیتم‌های منو
    menu_items = ""
    for menu_name in menus:
        if menu_name not in menu_map:
            continue   # صرف‌نظر از زیرمجوزهایی که منوی اصلی نیستند
        
        config = menu_map.get(menu_name, {"icon": "fa-circle", "route": "#", "color": "#94a3b8"})
        menu_items += f'''
        <li class="sidebar-nav-item">
            <a href="{config['route']}" class="nav-link" data-tooltip="{menu_name}">
                <span class="nav-icon" style="background: {config['color']}20; color: {config['color']};">
                    <i class="fas {config['icon']}"></i>
                </span>
                <span class="nav-text">{menu_name}</span>
                <span class="nav-indicator" style="background: {config['color']};"></span>
            </a>
        </li>
        '''
    
    # HTML کامل سایدبار
    sidebar_html = f'''
    <!-- Font Awesome برای آیکون‌ها -->
   
    <link rel="stylesheet" href="/static/libs/css/all.min.css">
    
    <aside class="sidebar glass-sidebar" id="sidebar">
        <!-- لایه شیشه‌ای پس‌زمینه -->
        <div class="glass-bg"></div>
        
        <!-- برند -->
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
        
        <!-- فوتر -->
        <div class="sidebar-footer">
            <a href="/logout" class="logout-btn">
                <i class="fas fa-sign-out-alt"></i>
                <span>خروج از حساب</span>
            </a>
        </div>
    </aside>
    
    <!-- Overlay برای موبایل -->
    <div class="sidebar-overlay" id="overlay"></div>
    '''
    
    return sidebar_html