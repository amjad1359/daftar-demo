"""
ماژول سوپروایزر - صفحه اصلی (با کنترل دسترسی)
"""

from models.common import get_active_shift
from models.user_model import user_has_sub_access


def get_supervisor_dashboard(user):
    """دریافت HTML داشبورد سوپروایزر با فیلتر دسترسی"""

    shift = get_active_shift()
    shift_name = shift['tarkib'] if shift else 'نامشخص'
    full_name = user.get('FullName', 'کاربر')
    access_level = user.get('AccessLevelID')

    # کارت‌های منو (هر کدام یک کلید دسترسی دارند)
    all_cards = [
        {"key": "supervisor_shift",      "title": "تنظیم شیفت", "icon": "📅", "desc": "ثبت و مدیریت شیفت‌ها", "url": "/module/supervisor/shift"},
        {"key": "supervisor_attendance", "title": "حاضرین",     "icon": "👥", "desc": "ثبت حضور و غیاب پرسنل", "url": "/module/supervisor/attendance"},
        {"key": "supervisor_gozaresh",   "title": "گزارشات",   "icon": "📝", "desc": "ثبت گزارش سوپروایزر", "url": "/module/supervisor/gozaresh"},
        {"key": "supervisor_rounds",     "title": "راند",       "icon": "🔍", "desc": "ثبت راند و اعتباربخشی", "url": "/module/supervisor/rounds"},
        {"key": "supervisor_ankal",      "title": "آنکال",      "icon": "📞", "desc": "ثبت آنکالی پزشکان", "url": "/module/supervisor/ankal"},
        {"key": "supervisor_amar",       "title": "آمار",       "icon": "📊", "desc": "آمار پایان شیفت", "url": "/module/supervisor/amar"},
        {"key": "supervisor_ghaybat",    "title": "غیبت",       "icon": "❌", "desc": "ثبت غیبت و تاخیر", "url": "/module/supervisor/ghaybat"},
        {"key": "supervisor_blood",      "title": "خون",        "icon": "🩸", "desc": "ثبت تزریق خون", "url": "/module/supervisor/blood"},
        {"key": "supervisor_codes",      "title": "کدها",       "icon": "🚑", "desc": "کدهای عملیاتی", "url": "/module/supervisor/codes"},
        {"key": "supervisor_crisis",     "title": "بحران",      "icon": "🚨", "desc": "ثبت بحران", "url": "/module/supervisor/crisis"},
    ]

    cards_html = ""
    for card in all_cards:
        if user_has_sub_access(access_level, card["key"]):
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
                <h2>🩺 پنل سوپروایزر</h2>
                <p>👤 {full_name}</p>
            </div>
            <div class="shift-badge">
                <span>🕒</span>
                <span>شیفت: {shift_name}</span>
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
    """دریافت صفحه سوپروایزر"""

    if sub_page == 'shift':
        from modules.supervisor.shift_form import get_shift_form
        return get_shift_form(user)

    if sub_page == 'amar':
        from modules.supervisor.amar_form import get_amar_form
        return get_amar_form(user)

    if sub_page == 'ankal':
        from modules.supervisor.ankal_form import get_ankal_form
        return get_ankal_form(user)

    if sub_page == 'attendance':
        from modules.supervisor.attendance_form import get_attendance_form
        return get_attendance_form(user)

    if sub_page == 'ghaybat':
        from modules.supervisor.ghaybat_form import get_ghaybat_form
        return get_ghaybat_form(user)

    if sub_page == 'blood':
        from modules.supervisor.blood_form import get_blood_form
        return get_blood_form(user)

    if sub_page == 'crisis':
        from modules.supervisor.crisis_form import get_crisis_form
        return get_crisis_form(user)

    if sub_page == 'gozaresh':
        from modules.supervisor.gozaresh_form import get_gozaresh_form
        return get_gozaresh_form(user)

    if sub_page == 'codes':
        from modules.supervisor.codes_form import get_codes_form
        return get_codes_form(user)

    if sub_page == 'rounds':
        from modules.supervisor.rounds_form import get_rounds_form
        return get_rounds_form(user)

    return get_supervisor_dashboard(user)
    
    