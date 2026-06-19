"""
ماژول گزارشات – داشبورد اصلی
نمایش کارت‌های منو برای دسترسی به انواع گزارشات
"""

from models.user_model import SUB_PAGE_PERMISSIONS, user_has_sub_access


def get_reports_dashboard(user):
    full_name = user.get('FullName', 'کاربر')
    level_id = user.get('AccessLevelID')

    # کارت‌ها با کلید دسترسی
    report_cards = [
        {"title": "گردش‌کار گزارشات", "icon": "🔄", "desc": "مشاهده روند بررسی و وضعیت گزارشات", "url": "/module/reports/workflow", "color": "#3b82f6", "perm_key": "reports_workflow"},
        {"title": "آمار پایان شیفت", "icon": "⏰", "desc": "گزارش آماری پایان شیفت به تفکیک بخش", "url": "/module/reports/stats", "color": "#10b981", "perm_key": "reports_stats"},
        {"title": "حضور و غیاب پرسنل", "icon": "👥", "desc": "گزارش تردد، غیبت و تأخیر پرسنل", "url": "/module/reports/attendance", "color": "#8b5cf6", "perm_key": "reports_attendance"},
        {"title": "بررسی راندها", "icon": "🏥", "desc": "گزارش راند و اعتباربخشی بخش‌ها", "url": "/module/reports/rounds", "color": "#f59e0b", "perm_key": "reports_rounds"},
        {"title": "گزارش کدها و عملیات", "icon": "🚨", "desc": "کدهای عملیاتی بیمارمحور (CPR و...)", "url": "/module/reports/codes", "color": "#ef4444", "perm_key": "reports_codes"},
        {"title": "گزارش بحران‌ها", "icon": "🔥", "desc": "بحران‌ها و کدهای عمومی", "url": "/module/reports/crisis", "color": "#f97316", "perm_key": "reports_crisis"},
        {"title": "گزارش هموویژولانس", "icon": "🩸", "desc": "مصرف خون و فرآورده‌های خونی", "url": "/module/reports/blood", "color": "#dc2626", "perm_key": "reports_blood"},
        {"title": "گزارش آنکالی پزشکان", "icon": "🩺", "desc": "وضعیت پاسخگویی پزشکان آنکال", "url": "/module/reports/ankal", "color": "#0891b2", "perm_key": "reports_ankal"},
    ]

    # فقط کارت‌هایی که کاربر مجوز دارد
    allowed_cards = [card for card in report_cards if user_has_sub_access(level_id, card['perm_key'])]

    if not allowed_cards:
        return '''<div class="content-card fade-in" style="text-align:center;padding:60px;">
            <h3>⛔ شما به هیچ گزارشی دسترسی ندارید</h3>
        </div>'''

    cards_html = ''
    for card in allowed_cards:
        cards_html += f'''
        <a href="{card['url']}" class="report-card" style="--card-color: {card['color']};">
            <div class="report-card-icon" style="background: {card['color']}15;">{card['icon']}</div>
            <div class="report-card-content">
                <div class="report-card-title">{card['title']}</div>
                <div class="report-card-desc">{card['desc']}</div>
            </div>
            <div class="report-card-arrow">←</div>
        </a>
        '''

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --primary: #1e3a8a; --dark: #1e293b; --gray: #64748b;
        --light-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9;
        --white: #fff; --radius: 16px; --transition: 0.25s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.5s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(15px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:1200px; margin:0 auto; padding:20px; }}

    .page-header {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color:white; border-radius:var(--radius); padding:28px 32px; margin-bottom:30px;
        text-align:center; box-shadow:0 10px 40px rgba(30,58,138,0.25);
    }}
    .page-header .icon {{ font-size:52px; margin-bottom:12px; }}
    .page-header h2 {{ font-size:24px; margin:0 0 6px 0; }}
    .page-header .subtitle {{ opacity:0.85; font-size:14px; }}
    .page-header .user-info {{
        margin-top:12px; font-size:12px; opacity:0.7;
    }}

    .cards-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
    }}

    .report-card {{
        display: flex;
        align-items: center;
        gap: 16px;
        background: var(--white);
        border: 2px solid var(--border);
        border-radius: 14px;
        padding: 20px;
        text-decoration: none;
        color: inherit;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }}
    .report-card::before {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 5px;
        height: 100%;
        background: var(--card-color, #3b82f6);
        border-radius: 0 14px 14px 0;
    }}
    .report-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-color: var(--card-color, #3b82f6);
    }}
    .report-card:active {{
        transform: translateY(-1px);
    }}

    .report-card-icon {{
        width: 56px;
        height: 56px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        flex-shrink: 0;
    }}
    .report-card-content {{
        flex: 1;
        min-width: 0;
    }}
    .report-card-title {{
        font-size: 15px;
        font-weight: 700;
        color: var(--dark);
        margin-bottom: 4px;
    }}
    .report-card-desc {{
        font-size: 11px;
        color: var(--gray);
        line-height: 1.5;
    }}
    .report-card-arrow {{
        font-size: 18px;
        color: var(--light-gray);
        transition: var(--transition);
        flex-shrink: 0;
    }}
    .report-card:hover .report-card-arrow {{
        color: var(--card-color, #3b82f6);
        transform: translateX(-5px);
    }}

    @media (max-width: 600px) {{
        .container {{ padding:12px; }}
        .cards-grid {{
            grid-template-columns: 1fr;
        }}
        .report-card {{
            padding: 16px;
        }}
        .report-card-icon {{
            width: 44px;
            height: 44px;
            font-size: 22px;
            border-radius: 10px;
        }}
        .report-card-title {{
            font-size: 13px;
        }}
    }}
</style>
</head>
<body>
<div class="container fade-in">
    <div class="page-header">
        
        <h2>سامانه جامع گزارشات مدیریتی 📊</h2>
        <p class="subtitle">انتخاب و مشاهده انواع گزارشات و آمارهای سیستم</p>
       
    </div>

    <div class="cards-grid">
        {cards_html}
    </div>
</div>
</body>
</html>'''
    return html


def get_page(user, sub_page=None):
  
    if sub_page:
        perm_key_map = {
            'ankal': 'reports_ankal',
            'blood': 'reports_blood',
            'codes': 'reports_codes',
            'crisis': 'reports_crisis',
            'attendance': 'reports_attendance',
            'workflow': 'reports_workflow',
            'rounds': 'reports_rounds',
            'stats': 'reports_stats',
        }
        perm_key = perm_key_map.get(sub_page)
        if perm_key and not user_has_sub_access(user.get('AccessLevelID'), perm_key):
            return '<div class="content-card fade-in" style="text-align:center;padding:60px;"><h3>⛔ دسترسی غیرمجاز</h3><p>شما مجاز به مشاهده این گزارش نیستید</p></div>'
 
    if sub_page is None:
        return get_reports_dashboard(user)

    if sub_page == 'ankal':
        from modules.reports.ankal_report import get_ankal_report
        return get_ankal_report(user)

    if sub_page == 'blood':
        from modules.reports.blood_report import get_blood_report
        return get_blood_report(user)
            
    if sub_page == 'codes':
        from modules.reports.codes_report import get_codes_report
        return get_codes_report(user)

    if sub_page == 'crisis':
        from modules.reports.crisis_report import get_crisis_report
        return get_crisis_report(user)

    if sub_page == 'attendance':
        from modules.reports.attendance_report import get_attendance_report
        return get_attendance_report(user)

    if sub_page == 'workflow':
        from modules.reports.workflow_report import get_workflow_report
        return get_workflow_report(user)

    if sub_page == 'rounds':
        from modules.reports.rounds_report import get_rounds_report
        return get_rounds_report(user)

    if sub_page == 'stats':
        from modules.reports.stats_report import get_stats_report
        return get_stats_report(user)






    # هر گزارش در آینده اینجا اضافه می‌شود
    sub_pages = {
    #    'workflow': {'icon': '🔄', 'title': 'گردش‌کار گزارشات'},
    #    'stats': {'icon': '⏰', 'title': 'آمار پایان شیفت'},
    #    'attendance': {'icon': '👥', 'title': 'حضور و غیاب پرسنل'},
     #   'rounds': {'icon': '🏥', 'title': 'بررسی راندها'},
     #   'codes': {'icon': '🚨', 'title': 'گزارش کدها و عملیات'},
      #  'crisis': {'icon': '🔥', 'title': 'گزارش بحران‌ها'},
     #   'blood': {'icon': '🩸', 'title': 'گزارش هموویژولانس'},
      #  'ankal': {'icon': '🩺', 'title': 'گزارش آنکالی پزشکان'},
    }

    if sub_page in sub_pages:
        info = sub_pages[sub_page]
        return f'''
        <div class="content-card fade-in">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
                <h2>{info['icon']} {info['title']}</h2>
                <a href="/module/reports" style="color:#3b82f6;font-weight:bold;text-decoration:none;">⬅️ بازگشت به لیست گزارشات</a>
            </div>
            <div style="text-align:center;padding:80px 20px;">
                <p style="font-size:56px;">🚧</p>
                <p style="color:#94a3b8;margin-top:15px;font-size:16px;">این گزارش در نسخه بعدی اضافه خواهد شد</p>
            </div>
        </div>
        '''

    return get_reports_dashboard(user)
    
    
    