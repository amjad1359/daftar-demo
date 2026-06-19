"""
ماژول ادمین – داشبورد و مسیریابی
"""

# from models.common import get_active_shift


def get_admin_dashboard(user):
    """داشبورد اصلی ادمین"""

   # shift = get_active_shift()
   # shift_name = shift['tarkib'] if shift else 'نامشخص'
    full_name = user.get('FullName', 'کاربر')

    # کارت‌های منوی ادمین
    menu_cards = [
        {"title": "مدیریت کاربران", "icon": "👥", "desc": "ثبت، ویرایش و مدیریت کاربران", "url": "/module/admin/users"},
        {"title": "سطوح دسترسی", "icon": "🔐", "desc": "مدیریت مجوزها و دسترسی‌ها", "url": "/module/admin/permissions"},
        {"title": "نام مدیریت‌ها", "icon": "🏛️", "desc": "تعریف واحدهای مدیریتی", "url": "/module/admin/departments"},
        {"title": "چارت بحران", "icon": "🚨", "desc": "تنظیمات چارت بحران", "url": "/module/admin/crisis_chart"},
        {"title": "مدیریت بخش‌ها", "icon": "🏥", "desc": "افزودن/ویرایش بخش‌ها", "url": "/module/admin/wards"},
        {"title": "عناوین شیفت", "icon": "🕒", "desc": "مدیریت شیفت‌ها", "url": "/module/admin/shifts"},
        {"title": "تنظیمات آمار", "icon": "📊", "desc": "پیکربندی آیتم‌های آماری", "url": "/module/admin/statistics"},
        {"title": "عناوین شغلی", "icon": "👨‍⚕️", "desc": "مدیریت عناوین شغلی", "url": "/module/admin/jobs"},
        {"title": "تخصص پزشکان", "icon": "🩺", "desc": "مدیریت تخصص‌ها", "url": "/module/admin/specialties"},
        {"title": "تعریف سطح دسترسی", "icon": "🔑", "desc": "نام سطوح دسترسی", "url": "/module/admin/access_levels"},
        {"title": "محتوای داشبورد", "icon": "🎨", "desc": "مدیریت اسلایدر و محتوای صفحه اصلی", "url": "/module/admin/dashboard_content"},
        {"title": "لوگوی بیمارستان", "icon": "🏥", "desc": "بارگذاری و مدیریت لوگو", "url": "/module/admin/logo"},
        {"title": "رصد کاربران", "icon": "🕵️", "desc": "گزارش اقدامات کاربران در سامانه", "url": "/module/admin/audit"},
        {"title": "تاییدکننده‌های شیفت", "icon": "✅", "desc": "تنظیم سه سطح تایید برای هر بخش", "url": "/module/admin/shift_approvers"},
        
       
    ]

    cards_html = ""
    for card in menu_cards:
        cards_html += f'''
        <div class="menu-card" onclick="window.location='{card['url']}'">
            <div class="menu-card-icon">{card['icon']}</div>
            <div class="menu-card-title">{card['title']}</div>
            <div class="menu-card-desc">{card['desc']}</div>
        </div>
        '''

    html = f'''
    <div class="content-card fade-in">
        <div class="supervisor-header">
            <div>
                <h2>⚙️ پنل مدیریت سیستم (ادمین)</h2>
                <p>👤 {full_name}</p>
            </div>
           
            </div>
        </div>

        <div class="menu-cards-grid">
            {cards_html}
        </div>
    </div>

    <style>
        .fade-in {{
            animation: fadeIn 0.4s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .supervisor-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .supervisor-header h2 {{
            font-size: 22px;
            color: var(--dark);
            margin: 0 0 5px 0;
        }}

        .supervisor-header p {{
            color: #64748b;
            font-size: 14px;
            margin: 0;
        }}

        .shift-badge {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: #1e3a8a;
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 14px;
        }}

        .menu-cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}

        .menu-card {{
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 14px;
            padding: 25px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .menu-card:hover {{
            border-color: #3b82f6;
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(59,130,246,0.15);
        }}

        .menu-card-icon {{
            font-size: 36px;
            margin-bottom: 12px;
        }}

        .menu-card-title {{
            font-size: 15px;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 5px;
        }}

        .menu-card-desc {{
            font-size: 12px;
            color: #94a3b8;
        }}

        @media (max-width: 576px) {{
            .menu-cards-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }}

            .menu-card {{
                padding: 18px 12px;
            }}

            .menu-card-icon {{
                font-size: 28px;
            }}

            .shift-badge {{
                padding: 8px 14px;
                font-size: 12px;
            }}
        }}
    </style>
    '''

    return html


def get_page(user, sub_page=None):
    """مسیریابی صفحات ادمین"""

    if sub_page == 'users':
        from modules.admin.users_form import get_users_form
        return get_users_form(user)

    if sub_page == 'statistics':
        from modules.admin.statistics_form import get_statistics_form
        return get_statistics_form(user)

    if sub_page == 'specialties':
        from modules.admin.specialties_form import get_specialties_form
        return get_specialties_form(user)

    if sub_page == 'shifts':
        from modules.admin.shift_titles_form import get_shift_titles_form
        return get_shift_titles_form(user)
        
    if sub_page == 'permissions':
        from modules.admin.permissions_form import get_permissions_form
        return get_permissions_form(user)
                
    if sub_page == 'access_levels':
        from modules.admin.access_levels_form import get_access_levels_form
        return get_access_levels_form(user)            

    if sub_page == 'departments':
        from modules.admin.departments_form import get_departments_form
        return get_departments_form(user)

    if sub_page == 'wards':
        from modules.admin.wards_form import get_wards_form
        return get_wards_form(user)

    if sub_page == 'jobs':
        from modules.admin.job_titles_form import get_job_titles_form
        return get_job_titles_form(user)

    if sub_page == 'crisis_chart':
        from modules.admin.crisis_chart_form import get_crisis_chart_form
        return get_crisis_chart_form(user)

    if sub_page == 'dashboard_content':
        from modules.admin.dashboard_settings import get_dashboard_settings_form
        return get_dashboard_settings_form(user)

    if sub_page == 'logo':
        from modules.admin.logo_form import get_logo_form
        return get_logo_form(user)

    if sub_page == 'audit':
        from modules.admin.audit_log import get_audit_log_form
        return get_audit_log_form(user)
        
    if sub_page == 'shift_approval':
        from modules.admin.shift_approval_form import get_shift_approval_form
        return get_shift_approval_form(user)   
       
   
    # لیست زیرصفحه‌های در حال توسعه
    sub_pages = {
     #   'users': {'icon': '👥', 'title': 'مدیریت کاربران'},
       # 'permissions': {'icon': '🔐', 'title': 'سطوح دسترسی'},
     #   'departments': {'icon': '🏛️', 'title': 'نام مدیریت‌ها'},
       # 'crisis_chart': {'icon': '🚨', 'title': 'چارت بحران'},
    
    }

    if sub_page and sub_page in sub_pages:
        info = sub_pages[sub_page]
        return f'''
        <div class="content-card fade-in">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
                <h2>{info['icon']} {info['title']}</h2>
                <a href="/module/admin" style="color:#3b82f6;font-weight:bold;">⬅️ بازگشت</a>
            </div>
            <div style="text-align:center;padding:60px 20px;">
                <p style="font-size:48px;">🚧</p>
                <p style="color:#94a3b8;margin-top:15px;font-size:16px;">این بخش در حال توسعه است</p>
            </div>
        </div>
        '''

    # صفحه اصلی
    return get_admin_dashboard(user)
    
    