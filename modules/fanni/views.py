"""
ماژول مسئول فنی - داشبورد و مسیریابی
"""

from models.common import get_active_shift


def get_fanni_dashboard(user):
    """داشبورد اصلی مسئول فنی"""

   # shift = get_active_shift()
  #  shift_name = shift['tarkib'] if shift else 'نامشخص'
    full_name = user.get('FullName', 'کاربر')

    # کارت‌های منو
    menu_cards = [
        {"title": "کارتابل فنی", "icon": "📋", "desc": "بررسی و ثبت نظر فنی", "url": "/module/fanni/reports"},
         {"title": "گزارشات مدیریتی", "icon": "📊", "desc": "گزارشات و آمار", "url": "/module/riyasat/management_reports"},
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
                <h2>🛠️ پنل مسئول فنی</h2>
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
    """مسیریابی صفحات مسئول فنی"""

    # ========== کارتابل فنی ==========
    if sub_page == 'reports':
        from modules.fanni.reports_form import get_fanni_reports_form
        return get_fanni_reports_form(user)

    # ========== زیرصفحه‌های دیگر (placeholder) ==========
    sub_pages = {}

    if sub_page and sub_page in sub_pages:
        info = sub_pages[sub_page]
        return f'''
        <div class="content-card fade-in">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
                <h2>{info['icon']} {info['title']}</h2>
                <a href="/module/fanni" style="color:#3b82f6;font-weight:bold;">⬅️ بازگشت</a>
            </div>
            <div style="text-align:center;padding:60px 20px;">
                <p style="font-size:48px;">🚧</p>
                <p style="color:#94a3b8;margin-top:15px;font-size:16px;">این بخش در حال توسعه است</p>
            </div>
        </div>
        '''

    # ========== صفحه اصلی ==========
    return get_fanni_dashboard(user)