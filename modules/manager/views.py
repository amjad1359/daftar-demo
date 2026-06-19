"""
modules/manager/views.py — نسخه آپدیت‌شده
کارت جدید «تایید برنامه شیفت» برای مدیران اجرایی که تاییدکننده هستند
"""
from models.common import get_active_shift
from models.database import query
from models.user_model import user_has_sub_access

def get_manager_dashboard(user):
    full_name = user.get('FullName', 'کاربر')
    postmodir = user.get('postmodir', 0)
    user_id   = user.get('UserID')

    dept_name = 'نامشخص'
    if postmodir:
        dept_row = query(
            "SELECT nam_modiriat FROM tbl_nam_modiriat WHERE ID_nam_modirit = %s",
            params=(postmodir,), fetch_one=True
        )
        if dept_row:
            dept_name = dept_row['nam_modiriat']

    # شمارش برنامه‌های در انتظار تایید (برای badge)
    pending_count = 0
    try:
        pc = query("""
            SELECT COUNT(*) AS cnt
            FROM tbl_shift_approvers ap
            JOIN tbl_shift_approvals prev
                ON prev.dep_id = ap.dep_id AND prev.level_no = ap.level_no - 1
            LEFT JOIN tbl_shift_approvals done
                ON done.dep_id = ap.dep_id AND done.year = prev.year
                AND done.month = prev.month AND done.level_no = ap.level_no
            WHERE ap.user_id = %s AND ap.level_no > 1 AND done.ID IS NULL
        """, (user_id,), fetch_one=True)
        pending_count = pc.get('cnt', 0) if pc else 0
    except Exception:
        pass

    badge = (' <span style="background:#ef4444;color:white;border-radius:10px;'
             'padding:1px 8px;font-size:11px;">' + str(pending_count) + '</span>') if pending_count else ''


    access_level = user.get('AccessLevelID')
    
    menu_cards = []

    # هر کارت را جداگانه بررسی می‌کنیم
    if user_has_sub_access(access_level, 'manager_reports'):
        menu_cards.append({"title": "کارتابل مدیران", "icon": "💼", "desc": "پاسخگویی به گزارشات", "url": "/module/manager/reports"})

    if user_has_sub_access(access_level, 'manager_management_reports'):
        menu_cards.append({"title": "گزارشات مدیریتی", "icon": "📊", "desc": "گزارشات و آمار", "url": "/module/manager/management_reports"})

    if user_has_sub_access(access_level, 'manager_shifts'):
        menu_cards.append({"title": "برنامه شیفت ماهیانه", "icon": "🗓️", "desc": "ثبت و ویرایش شیفت پرسنل بخش", "url": "/module/manager/shifts"})

    if user_has_sub_access(access_level, 'manager_shift_review'):
        menu_cards.append({"title": "تایید شیفت‌بندی" + badge, "icon": "✅", "desc": "تایید برنامه‌های شیفت بخش‌ها", "url": "/module/manager/shift_review", "highlight": True})

    if user_has_sub_access(access_level, 'manager_shift_comparison'):
        menu_cards.append({"title": "مقایسه شیفت و حضور", "icon": "⚖️", "desc": "مقایسه برنامه با حضور واقعی", "url": "/module/manager/shift_comparison"})

    if user_has_sub_access(access_level, 'manager_shift_edit'):
        menu_cards.append({"title": "ویرایش پیشرفته شیفت", "icon": "🔧", "desc": "ویرایش برنامه بدون محدودیت تأیید", "url": "/module/manager/shifts_edit"})



    cards_html = ''
    for card in menu_cards:
        border = 'border-color:#0f766e;background:linear-gradient(135deg,#f0fdfa,#fff);' if card.get('highlight') else ''
        cards_html += (
            '<div class="menu-card" style="' + border + '" onclick="window.location=\'' + card['url'] + '\'">'
            + '<div class="menu-card-icon">' + card['icon'] + '</div>'
            + '<div class="menu-card-title">' + card['title'] + '</div>'
            + '<div class="menu-card-desc">' + card['desc'] + '</div>'
            + '</div>'
        )

    return f'''
<div class="content-card fade-in">
    <div class="supervisor-header">
        <div>
            <h2>💼 پنل مدیران اجرایی</h2>
            <p>👤 {full_name} | 🏢 مدیریت: {dept_name}</p>
        </div>
    </div>
    <div class="menu-cards-grid">{cards_html}</div>
</div>
<style>
.fade-in{{animation:fadeIn 0.4s ease;}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
.supervisor-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;padding-bottom:20px;border-bottom:2px solid #e2e8f0;}}
.supervisor-header h2{{font-size:22px;color:var(--dark);margin:0 0 5px 0;}}
.supervisor-header p{{color:#64748b;font-size:14px;margin:0;}}
.menu-cards-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:15px;}}
.menu-card{{background:white;border:2px solid #e2e8f0;border-radius:14px;padding:25px 20px;text-align:center;cursor:pointer;transition:all 0.3s ease;}}
.menu-card:hover{{border-color:#3b82f6;transform:translateY(-3px);box-shadow:0 8px 25px rgba(59,130,246,0.15);}}
.menu-card-icon{{font-size:36px;margin-bottom:12px;}}
.menu-card-title{{font-size:15px;font-weight:bold;color:#1e293b;margin-bottom:5px;}}
.menu-card-desc{{font-size:12px;color:#94a3b8;}}
@media(max-width:576px){{
    .menu-cards-grid{{grid-template-columns:repeat(2,1fr);gap:10px;}}
    .menu-card{{padding:18px 12px;}}
    .menu-card-icon{{font-size:28px;}}
}}
</style>'''


def get_page(user, sub_page=None):
    if sub_page == 'reports':
        from modules.manager.reports_form import get_manager_reports_form
        return get_manager_reports_form(user)

    elif sub_page == 'shifts':
        from modules.manager.shifts_form import get_shifts_form
        return get_shifts_form(user)

    elif sub_page == 'shift_review':
        from modules.manager.shift_review_form import get_shift_review_page
        return get_shift_review_page(user)

    elif sub_page == 'shift_comparison':                     # ← جدید
        from modules.manager.shift_comparison_form import get_shift_comparison_page
        return get_shift_comparison_page(user)

    elif sub_page == 'shifts_edit':
        from modules.manager.shift_edit import get_shifts_edit_form
        return get_shifts_edit_form(user)

    elif sub_page == 'management_reports':
        return '''
        <div class="content-card fade-in">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
                <h2>📊 گزارشات مدیریتی</h2>
                <a href="/module/manager" style="color:#3b82f6;font-weight:bold;">⬅️ بازگشت</a>
            </div>
            <div style="text-align:center;padding:60px 20px;">
                <p style="font-size:48px;">🚧</p>
                <p style="color:#94a3b8;margin-top:15px;font-size:16px;">این بخش در حال توسعه است</p>
            </div>
        </div>'''

    return get_manager_dashboard(user)

    
    