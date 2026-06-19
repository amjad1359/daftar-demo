"""
مدیریت ماتریس دسترسی – ادمین
شامل دو تب:
  ۱. مجوزهای ماژول‌های اصلی
  ۲. مجوزهای زیربخش‌ها (مثلاً گزارش‌های خاص)
نسخه Flask با AJAX، Toast و ماتریس تعاملی پیشرفته
"""

from models.database import query, get_connection
from models.user_model import SUB_PAGE_PERMISSIONS
from utils.auto_log import log_crud
import json

# ---------- ثابت‌های ماژول (برای هماهنگی بین UI و ذخیره‌سازی) ----------
MAIN_FORMS = [
    "👨‍⚕️ سوپروایزر",
    "📋 مدیر پرستاری",
    "👔 مدیران اجرایی",
    "🏢 ریاست",
    "🛠️ مسئول فنی",
    "⚙️ ادمین",
    "📊 گزارشات",
    "🔑 امنیت",
]


def get_permissions_form(user):
    """صفحه اصلی مدیریت ماتریس دسترسی (با دو تب)"""

    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    levels = query(
        "SELECT AccessLevelID, AccessLevelName, Description FROM accesslevels ORDER BY AccessLevelID",
        fetch_all=True
    ) or []

    if not levels:
        return '''<div class="content-card fade-in" style="text-align:center;padding:60px;">
            <div style="font-size:64px;margin-bottom:15px;">⚠️</div>
            <h3>هیچ سطح دسترسی تعریف نشده است</h3>
            <p style="color:#94a3b8;margin-bottom:25px;">لطفاً ابتدا از بخش "نام سطح دسترسی" سطوح مورد نظر را تعریف کنید</p>
            <a href="/module/admin/access_levels" class="btn btn-primary">🔑 تعریف سطح دسترسی</a>
        </div>'''

    # ---------- ۱. ماژول‌های اصلی ----------
    current_main = query(
        "SELECT UserLevelID, TableName FROM userlevelpermissions WHERE Permission = 1",
        fetch_all=True
    ) or []
    main_perm_set = set()
    for p in current_main:
        if p['TableName'] in MAIN_FORMS:
            main_perm_set.add(f"{p['UserLevelID']}|{p['TableName']}")

    main_level_headers = ''
    for level in levels:
        desc = level.get('Description', '')
        tooltip = f' title="{desc}"' if desc else ''
        main_level_headers += f'<th{tooltip}><div class="th-content"><span class="th-icon">🔹</span><span>{level["AccessLevelName"]}</span></div></th>'

    main_table_rows = ''
    for form in MAIN_FORMS:
        row_cells = ''
        for level in levels:
            has_perm = f"{level['AccessLevelID']}|{form}" in main_perm_set
            checked_attr = 'checked' if has_perm else ''
            active_class = 'active' if has_perm else ''
            row_cells += f'''
                <td class="perm-cell {active_class}" data-level="{level['AccessLevelID']}" data-form="{form}" onclick="toggleCell(this)">
                    <div class="cell-content">
                        <input type="checkbox" {checked_attr} style="display:none;">
                        <span class="status-icon">{'✅' if has_perm else '✕'}</span>
                    </div>
                </td>
            '''
        main_table_rows += f'''<tr>
            <td class="form-name-cell" title="{form}">{form}</td>
            {row_cells}
        </tr>'''

    # ---------- ۲. زیربخش‌ها ----------
    sub_forms = sorted(SUB_PAGE_PERMISSIONS.keys())
    current_sub = query(
        "SELECT UserLevelID, TableName FROM userlevelpermissions WHERE Permission = 1",
        fetch_all=True
    ) or []
    sub_perm_set = set()
    for p in current_sub:
        if p['TableName'] in sub_forms:
            sub_perm_set.add(f"{p['UserLevelID']}|{p['TableName']}")

    sub_level_headers = ''
    for level in levels:
        desc = level.get('Description', '')
        tooltip = f' title="{desc}"' if desc else ''
        sub_level_headers += f'<th{tooltip}><div class="th-content"><span class="th-icon">🔸</span><span>{level["AccessLevelName"]}</span></div></th>'

    sub_table_rows = ''
    for form_key in sub_forms:
        row_cells = ''
        for level in levels:
            has_perm = f"{level['AccessLevelID']}|{form_key}" in sub_perm_set
            checked_attr = 'checked' if has_perm else ''          # ← رفع باگ اصلی
            active_class = 'active' if has_perm else ''
            row_cells += f'''
                <td class="perm-cell {active_class}" data-level="{level['AccessLevelID']}" data-form="{form_key}" onclick="toggleCell(this)">
                    <div class="cell-content">
                        <input type="checkbox" {checked_attr} style="display:none;">
                        <span class="status-icon">{'✅' if has_perm else '✕'}</span>
                    </div>
                </td>
            '''
        sub_table_rows += f'''<tr>
            <td class="form-name-cell" title="{form_key}">{SUB_PAGE_PERMISSIONS.get(form_key, form_key)}</td>
            {row_cells}
        </tr>'''

    # ---------- ساخت HTML ----------
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
        --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
        --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
        --bg: #f1f5f9; --white: #fff; --radius: 14px; --transition: 0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.5s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(15px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:100%; margin:0 auto; padding:20px; }}

    .perm-header {{
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        color:white; border-radius:var(--radius); padding:25px 30px; margin-bottom:25px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 10px 40px rgba(30,58,138,0.3);
    }}
    .perm-header h2 {{ font-size:24px; margin:0; }}
    .perm-header p {{ opacity:0.85; font-size:13px; margin:5px 0 0 0; }}
    .back-btn {{
        color:white; text-decoration:none; padding:10px 18px;
        border:1.5px solid rgba(255,255,255,0.4); border-radius:10px;
        font-size:14px; font-weight:500; transition:var(--transition);
    }}
    .back-btn:hover {{ background:rgba(255,255,255,0.15); border-color:rgba(255,255,255,0.6); }}

    .tabs {{
        display:flex; gap:5px; margin-bottom:25px; border-bottom:2px solid var(--border);
    }}
    .tab {{
        padding:12px 24px; font-size:14px; font-weight:600; border:none;
        background:none; color:var(--light-gray); cursor:pointer;
        border-bottom:2px solid transparent; transition:var(--transition);
        font-family:inherit;
    }}
    .tab:hover {{ color:var(--dark); }}
    .tab.active {{ color:var(--primary); border-bottom-color:var(--primary); }}
    .tab-content {{ display:none; animation:fadeIn 0.3s ease; }}
    .tab-content.active {{ display:block; }}

    .toolbar {{
        display:flex; justify-content:space-between; align-items:center;
        margin-bottom:20px; gap:12px; flex-wrap:wrap;
    }}
    .btn {{
        display:inline-flex; align-items:center; justify-content:center; gap:6px;
        padding:10px 20px; border:none; border-radius:10px; font-size:13px;
        font-weight:600; cursor:pointer; font-family:inherit;
        transition:var(--transition); text-decoration:none; white-space:nowrap;
    }}
    .btn-primary {{
        background:linear-gradient(135deg, var(--primary), var(--primary-light));
        color:white; box-shadow:0 4px 15px rgba(30,58,138,0.25);
    }}
    .btn-primary:hover {{ transform:translateY(-2px); box-shadow:0 8px 25px rgba(30,58,138,0.35); }}
    .btn-primary:disabled {{ opacity:0.5; cursor:not-allowed; transform:none; }}
    .btn-outline {{
        background:white; color:var(--dark); border:2px solid var(--border);
    }}
    .btn-outline:hover {{ border-color:var(--primary-light); color:var(--primary-light); }}
    .btn-sm {{ padding:8px 14px; font-size:12px; }}

    .quick-actions {{ display:flex; gap:8px; }}

    .matrix-wrapper {{
        background:var(--white); border-radius:var(--radius);
        border:1px solid var(--border); overflow:hidden;
        box-shadow:0 2px 8px rgba(0,0,0,0.05);
    }}
    .matrix-scroll {{
        overflow-x:auto; max-height:65vh;
    }}
    .matrix-table {{
        width:100%; border-collapse:collapse; min-width:900px;
    }}
    .matrix-table thead {{
        position:sticky; top:0; z-index:20;
    }}
    .matrix-table th {{
        background:var(--primary); color:white; padding:16px 10px;
        font-size:13px; font-weight:600; text-align:center;
        white-space:nowrap;
    }}
    .matrix-table th:first-child {{
        position:sticky; right:0; z-index:21; min-width:200px;
        background:var(--primary);
    }}
    .matrix-table th .th-content {{
        display:flex; align-items:center; justify-content:center; gap:6px;
    }}

    .matrix-table td {{
        padding:0; text-align:center; border:1px solid var(--border);
        transition:all 0.15s ease;
    }}
    .matrix-table tbody tr:hover td {{
        background:#f8fafc;
    }}
    .matrix-table tbody tr:hover .form-name-cell {{
        background:#e2e8f0; font-weight:700;
    }}

    .form-name-cell {{
        background:var(--bg); font-weight:600; color:var(--dark);
        font-size:14px; padding:16px 20px !important;
        text-align:right !important; border-left:4px solid var(--primary) !important;
        position:sticky; right:0; z-index:5; white-space:nowrap;
        cursor:default;
    }}

    .perm-cell {{
        cursor:pointer; padding:8px 5px !important;
        user-select:none; position:relative; min-width:100px;
        transition:all 0.15s ease;
    }}
    .perm-cell:hover {{
        background:#eef2ff !important; transform:scale(1.02);
        box-shadow:0 0 0 2px var(--primary-light);
        z-index:2;
    }}
    .perm-cell .cell-content {{
        display:flex; align-items:center; justify-content:center;
        padding:10px; border-radius:10px; transition:var(--transition);
    }}
    .perm-cell.active .cell-content {{
        background:#d1fae5;
    }}
    .perm-cell:not(.active) .cell-content {{
        background:#fee2e2;
    }}
    .perm-cell .status-icon {{
        font-size:18px; transition:var(--transition);
    }}
    .perm-cell.active .status-icon {{ color:#059669; }}
    .perm-cell:not(.active) .status-icon {{ color:#dc2626; }}

    .legend {{
        display:flex; gap:20px; padding:15px 20px;
        background:var(--bg); border-top:1px solid var(--border);
        font-size:12px; color:var(--gray);
    }}
    .legend-item {{ display:flex; align-items:center; gap:6px; }}
    .legend-dot {{ width:12px; height:12px; border-radius:3px; }}
    .legend-dot.active {{ background:#10b981; }}
    .legend-dot.inactive {{ background:#ef4444; }}

    .toast-container {{
        position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000;
        display:flex; flex-direction:column; gap:10px; pointer-events:none;
    }}
    .toast {{
        display:flex; align-items:center; gap:12px; padding:16px 24px;
        border-radius:14px; color:white; font-size:14px; font-weight:600;
        box-shadow:0 10px 40px rgba(0,0,0,0.25); animation:slideDown 0.4s ease;
        pointer-events:auto; min-width:300px;
    }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }}
    .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    .toast .toast-close {{ margin-right:auto; cursor:pointer; opacity:0.7; font-size:16px; }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}

    @media (max-width:768px) {{
        .perm-header {{ flex-direction:column; gap:15px; text-align:center; }}
        .toolbar {{ flex-direction:column; align-items:stretch; }}
        .quick-actions {{ justify-content:center; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">

    <div class="perm-header">
        <div>
            <h2>🔐 مدیریت ماتریس دسترسی</h2>
            <p>تعیین مجوزهای ماژول‌ها و زیربخش‌ها</p>
        </div>
        <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="switchTab('main')">📋 ماژول‌های اصلی</button>
        <button class="tab" onclick="switchTab('sub')">🔸 زیربخش‌ها</button>
    </div>

    <div id="tab-main" class="tab-content active">
        <div class="toolbar">
            <div class="quick-actions">
                <button class="btn btn-outline btn-sm" onclick="selectAll('main')">✅ انتخاب همه</button>
                <button class="btn btn-outline btn-sm" onclick="deselectAll('main')">❌ لغو انتخاب همه</button>
                <button class="btn btn-outline btn-sm" onclick="invertAll('main')">🔄 معکوس کردن</button>
            </div>
            <button class="btn btn-primary" onclick="savePermissions('main')" id="save-main-btn">
                <span id="save-main-text">💾 ذخیره تغییرات</span>
                <span id="save-main-loading" style="display:none;">⏳ در حال ذخیره...</span>
            </button>
        </div>

        <div class="matrix-wrapper">
            <div class="matrix-scroll">
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th>📋 فرم / ماژول</th>
                            {main_level_headers}
                        </tr>
                    </thead>
                    <tbody>
                        {main_table_rows}
                    </tbody>
                </table>
            </div>
            <div class="legend">
                <div class="legend-item"><span class="legend-dot active"></span> دسترسی فعال</div>
                <div class="legend-item"><span class="legend-dot inactive"></span> دسترسی غیرفعال</div>
                <div class="legend-item" style="margin-right:auto;">برای ذخیره تغییرات، دکمه "ذخیره" را بزنید</div>
            </div>
        </div>
    </div>

    <div id="tab-sub" class="tab-content">
        <div class="toolbar">
            <div class="quick-actions">
                <button class="btn btn-outline btn-sm" onclick="selectAll('sub')">✅ انتخاب همه</button>
                <button class="btn btn-outline btn-sm" onclick="deselectAll('sub')">❌ لغو انتخاب همه</button>
                <button class="btn btn-outline btn-sm" onclick="invertAll('sub')">🔄 معکوس کردن</button>
            </div>
            <button class="btn btn-primary" onclick="savePermissions('sub')" id="save-sub-btn">
                <span id="save-sub-text">💾 ذخیره تغییرات</span>
                <span id="save-sub-loading" style="display:none;">⏳ در حال ذخیره...</span>
            </button>
        </div>

        <div class="matrix-wrapper">
            <div class="matrix-scroll">
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th>🔸 زیربخش</th>
                            {sub_level_headers}
                        </tr>
                    </thead>
                    <tbody>
                        {sub_table_rows}
                    </tbody>
                </table>
            </div>
            <div class="legend">
                <div class="legend-item"><span class="legend-dot active"></span> دسترسی فعال</div>
                <div class="legend-item"><span class="legend-dot inactive"></span> دسترسی غیرفعال</div>
                <div class="legend-item" style="margin-right:auto;">برای ذخیره تغییرات، دکمه "ذخیره" را بزنید</div>
            </div>
        </div>
    </div>
</div>

<script>
    function switchTab(tab) {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        if (tab === 'main') {{
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.getElementById('tab-main').classList.add('active');
        }} else {{
            document.querySelectorAll('.tab')[1].classList.add('active');
            document.getElementById('tab-sub').classList.add('active');
        }}
    }}

    function showToast(msg, type) {{
        const c = document.getElementById('toast-container');
        const t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = `<span>${{type==='success'?'✅':'❌'}}</span><span>${{msg}}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    // تغییر سلول با همگام‌سازی checkbox مخفی
    function toggleCell(cell) {{
        const checkbox = cell.querySelector('input[type="checkbox"]');
        if (!checkbox) return;
        checkbox.checked = !checkbox.checked;
        cell.classList.toggle('active', checkbox.checked);
        const icon = cell.querySelector('.status-icon');
        icon.textContent = checkbox.checked ? '✅' : '✕';
    }}

    function selectAll(section) {{
        const selector = section === 'main' ? '#tab-main .perm-cell' : '#tab-sub .perm-cell';
        document.querySelectorAll(selector).forEach(cell => {{
            const checkbox = cell.querySelector('input[type="checkbox"]');
            if (checkbox && !checkbox.checked) {{
                checkbox.checked = true;
                cell.classList.add('active');
                cell.querySelector('.status-icon').textContent = '✅';
            }}
        }});
    }}

    function deselectAll(section) {{
        const selector = section === 'main' ? '#tab-main .perm-cell' : '#tab-sub .perm-cell';
        document.querySelectorAll(selector).forEach(cell => {{
            const checkbox = cell.querySelector('input[type="checkbox"]');
            if (checkbox && checkbox.checked) {{
                checkbox.checked = false;
                cell.classList.remove('active');
                cell.querySelector('.status-icon').textContent = '✕';
            }}
        }});
    }}

    function invertAll(section) {{
        const selector = section === 'main' ? '#tab-main .perm-cell' : '#tab-sub .perm-cell';
        document.querySelectorAll(selector).forEach(cell => {{
            toggleCell(cell);
        }});
    }}

    async function savePermissions(section) {{
        const containerId = section === 'main' ? 'tab-main' : 'tab-sub';
        const permissions = [];

        document.querySelectorAll(`#${{containerId}} .perm-cell`).forEach(cell => {{
            const checkbox = cell.querySelector('input[type="checkbox"]');
            if (checkbox && checkbox.checked) {{
                permissions.push({{
                    level_id: parseInt(cell.dataset.level),
                    form_name: cell.dataset.form
                }});
            }}
        }});

        // هشدار برای حذف کامل
        if (permissions.length === 0) {{
            const msg = section === 'main' 
                ? '⚠️ هیچ مجوزی انتخاب نشده است. با ذخیره، تمام دسترسی‌های ماژول‌های اصلی حذف خواهند شد. ادامه می‌دهید؟'
                : '⚠️ هیچ مجوزی انتخاب نشده است. با ذخیره، تمام دسترسی‌های زیربخش‌ها حذف خواهند شد. ادامه می‌دهید؟';
            if (!confirm(msg)) {{
                return;
            }}
        }}

        const url = section === 'main' ? '/module/admin/permissions/save' : '/module/admin/sub_permissions/save';
        const btnId = section === 'main' ? 'save-main-btn' : 'save-sub-btn';
        const textId = section === 'main' ? 'save-main-text' : 'save-sub-text';
        const loadingId = section === 'main' ? 'save-main-loading' : 'save-sub-loading';

        document.getElementById(textId).style.display = 'none';
        document.getElementById(loadingId).style.display = 'inline';
        document.getElementById(btnId).disabled = true;

        try {{
            const res = await fetch(url, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{permissions}})
            }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{
            showToast('⛔ خطا در ارتباط با سرور', 'error');
        }} finally {{
            document.getElementById(textId).style.display = 'inline';
            document.getElementById(loadingId).style.display = 'none';
            document.getElementById(btnId).disabled = false;
        }}
    }}

    document.addEventListener('keydown', function(e) {{
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {{
            e.preventDefault();
            const activeTab = document.querySelector('.tab.active');
            if (activeTab && activeTab.innerText.includes('اصلی')) {{
                savePermissions('main');
            }} else {{
                savePermissions('sub');
            }}
        }}
    }});
</script>
</body>
</html>'''
    return html


# =====================================================================
# API Functions
# =====================================================================

def save_permissions(user, data):
    """ذخیره ماتریس دسترسی ماژول‌های اصلی"""
    user_id = user.get('UserID', 0) if user else 0
    try:
        permissions = data.get('permissions', [])
        if not isinstance(permissions, list):
            return {'success': False, 'message': 'فرمت داده‌ها نامعتبر است'}

        # اعتبارسنجی نام فرم‌ها
        for perm in permissions:
            if perm.get('form_name') not in MAIN_FORMS:
                return {'success': False, 'message': f'نام فرم نامعتبر: {perm.get("form_name")}'}

        conn = get_connection()
        if not conn:
            return {'success': False, 'message': 'خطا در اتصال به دیتابیس'}

        conn.autocommit = False
        cursor = conn.cursor()

        try:
            # ----- مرحله‌ی ۱: گرفتن وضعیت قدیم برای لاگ -----
            placeholders = ','.join(['%s'] * len(MAIN_FORMS))
            cursor.execute(
                f"SELECT UserLevelID, TableName FROM userlevelpermissions WHERE TableName IN ({placeholders}) AND Permission = 1",
                MAIN_FORMS
            )
            old_records = cursor.fetchall()

            # ----- مرحله‌ی ۲: حذف تمام مجوزهای قبلی -----
            cursor.execute(
                f"DELETE FROM userlevelpermissions WHERE TableName IN ({placeholders})",
                MAIN_FORMS
            )

            # ----- مرحله‌ی ۳: درج مجوزهای جدید -----
            insert_count = 0
            for perm in permissions:
                cursor.execute(
                    "INSERT INTO userlevelpermissions (UserLevelID, TableName, Permission, dastrasi) VALUES (%s, %s, 1, 1)",
                    (int(perm['level_id']), perm['form_name'])
                )
                insert_count += 1

            conn.commit()

            # ----- مرحله‌ی ۴: لاگ حسابرسی -----
            log_crud(
                'save_permissions',
                user_id,
                key_value=None,
                old_value=json.dumps(old_records, default=str, ensure_ascii=False),
                new_value=json.dumps(permissions, ensure_ascii=False)
            )

            if permissions:
                msg = f'دسترسی‌ها با موفقیت بروزرسانی شدند ({insert_count} مورد ذخیره شد)'
            else:
                msg = 'تمام مجوزهای ماژول‌های اصلی حذف شدند.'
            return {
                'success': True,
                'message': msg,
                'active_count': insert_count
            }
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'خطا در ذخیره‌سازی: {str(e)}'}
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def save_sub_permissions(user, data):
    """ذخیره دسترسی‌های زیربخش‌ها"""
    user_id = user.get('UserID', 0) if user else 0
    try:
        permissions = data.get('permissions', [])
        if not isinstance(permissions, list):
            return {'success': False, 'message': 'داده‌ها نامعتبر هستند'}

        sub_keys = list(SUB_PAGE_PERMISSIONS.keys())
        if not sub_keys:
            return {'success': False, 'message': 'زیربخشی تعریف نشده است'}

        for perm in permissions:
            if perm.get('form_name') not in sub_keys:
                return {'success': False, 'message': f'زیربخش نامعتبر: {perm.get("form_name")}'}

        conn = get_connection()
        if not conn:
            return {'success': False, 'message': 'خطا در اتصال به دیتابیس'}

        conn.autocommit = False
        cursor = conn.cursor()

        try:
            # ----- وضعیت قدیم -----
            placeholders = ','.join(['%s'] * len(sub_keys))
            cursor.execute(
                f"SELECT UserLevelID, TableName FROM userlevelpermissions WHERE TableName IN ({placeholders}) AND Permission = 1",
                sub_keys
            )
            old_records = cursor.fetchall()

            # ----- حذف -----
            cursor.execute(
                f"DELETE FROM userlevelpermissions WHERE TableName IN ({placeholders})",
                sub_keys
            )

            # ----- درج -----
            insert_count = 0
            for perm in permissions:
                cursor.execute(
                    "INSERT INTO userlevelpermissions (UserLevelID, TableName, Permission, dastrasi) VALUES (%s, %s, 1, 1)",
                    (int(perm['level_id']), perm['form_name'])
                )
                insert_count += 1

            conn.commit()

            # ----- لاگ -----
            log_crud(
                'save_sub_permissions',
                user_id,
                key_value=None,
                old_value=json.dumps(old_records, default=str, ensure_ascii=False),
                new_value=json.dumps(permissions, ensure_ascii=False)
            )

            if permissions:
                msg = f'زیرمجوزها با موفقیت ذخیره شدند ({insert_count} مورد)'
            else:
                msg = 'تمام مجوزهای زیربخش‌ها حذف شدند.'
            return {'success': True, 'message': msg}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'خطا: {str(e)}'}
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}