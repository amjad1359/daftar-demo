"""
ماژول مدیر پرستاری (مترون) - صفحه اصلی (با کنترل دسترسی)
"""

from models.user_model import user_has_sub_access


def get_matron_dashboard(user):
    """دریافت HTML داشبورد مترون با فیلتر دسترسی"""

    full_name = user.get('FullName', 'کاربر')
    access_level = user.get('AccessLevelID')

    all_cards = [
        {"key": "matron_reports",   "title": "گزارشات سوپروایزر", "icon": "📋", "desc": "بررسی و تأیید گزارشات", "url": "/module/matron/reports"},
        {"key": "matron_personnel", "title": "مدیریت پرسنل",      "icon": "👥", "desc": "ثبت و ویرایش اطلاعات پرسنل", "url": "/module/matron/personnel"},
        {"key": "matron_checklist", "title": "تنظیمات چک‌لیست",  "icon": "⚙️", "desc": "مدیریت ارزیابی‌ها", "url": "/module/matron/checklist"},
        {"key": "matron_codes",     "title": "کدهای عملیاتی",     "icon": "🚑", "desc": "تعریف کدها و نقش‌ها", "url": "/module/matron/codes"},
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
                <h2>📋 پنل مدیر پرستاری (مترون)</h2>
                <p>👤 {full_name}</p>
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
        }}
    </style>
    '''

    return html


def get_page(user, sub_page=None):
    """دریافت صفحه مترون"""
    if sub_page == 'reports':
        from modules.matron.reports_form import get_matron_reports_form
        return get_matron_reports_form(user)

    if sub_page == 'personnel':
        from modules.matron.personnel_form import get_personnel_form
        return get_personnel_form(user)
        
    if sub_page == 'checklist':
        from modules.matron.checklist_form import get_checklist_form
        return get_checklist_form(user)

    if sub_page == 'codes':
        from modules.matron.codes_form import get_codes_form
        return get_codes_form(user)

    return get_matron_dashboard(user)
    
    