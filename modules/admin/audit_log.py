"""
رصد کاربران – پایش اقدامات (audittrail)
نسخه کامل با فیلترهای پیشرفته و صفحه‌بندی AJAX
"""

import jdatetime
from datetime import datetime as dt
from datetime import timedelta
from models.database import query
import json

def get_audit_log_form(user):
    """صفحه اصلی رصد کاربران"""

    today_j = jdatetime.date.today()
    one_month_ago = today_j - timedelta(days=30)
    today_shamsi = today_j.strftime("%Y/%m/%d")
    month_ago_shamsi = one_month_ago.strftime("%Y/%m/%d")

    # لیست‌های drop-down از داده‌های موجود
    actions_list = query("SELECT DISTINCT `Action` FROM audittrail WHERE `Action` IS NOT NULL AND `Action` != '' ORDER BY `Action`", fetch_all=True) or []
    action_opts = '<option value="">همه</option>'
    for a in actions_list:
        action_opts += f'<option value="{a["Action"]}">{a["Action"]}</option>'

    tables_list = query("SELECT DISTINCT `Table` FROM audittrail WHERE `Table` IS NOT NULL AND `Table` != '' ORDER BY `Table`", fetch_all=True) or []
    table_opts = '<option value="">همه</option>'
    for t in tables_list:
        table_opts += f'<option value="{t["Table"]}">{t["Table"]}</option>'

    # ================== HTML ==================
    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
        --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
        --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
        --bg: #f1f5f9; --white: #fff; --radius: 12px; --transition: 0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:1400px; margin:0 auto; padding:20px; }}

    .page-header {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color:white; border-radius:var(--radius); padding:22px 28px; margin-bottom:22px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(30,58,138,0.25);
    }}
    .page-header h2 {{ font-size:22px; }}
    .back-btn {{ color:white; text-decoration:none; padding:8px 16px; border:1px solid rgba(255,255,255,0.4); border-radius:8px; font-size:13px; transition:var(--transition); }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    .stats-row {{ display:grid; grid-template-columns:repeat(4,1fr); gap:15px; margin-bottom:20px; }}
    .stat-card {{ background:var(--white); border-radius:10px; padding:18px; text-align:center; border:1px solid var(--border); }}
    .stat-value {{ font-size:26px; font-weight:bold; }}
    .stat-label {{ font-size:12px; color:var(--gray); margin-top:4px; }}

    .filters {{
        background:var(--white); border-radius:var(--radius); padding:14px; border:1px solid var(--border);
        margin-bottom:15px;
    }}
    .f-row {{ display:flex; gap:8px; flex-wrap:wrap; align-items:flex-end; }}
    .f-grp {{ flex:1; min-width:100px; }}
    .f-grp label {{ display:block; font-size:10px; font-weight:600; color:var(--gray); margin-bottom:3px; }}
    .f-grp input, .f-grp select {{
        width:100%; padding:7px 9px; border:2px solid var(--border); border-radius:6px;
        font-size:12px; font-family:inherit;
    }}
    .btn {{
        padding:7px 15px; border:none; border-radius:6px; font-size:12px; font-weight:600;
        cursor:pointer; font-family:inherit; transition:var(--transition); white-space:nowrap;
        display:inline-flex; align-items:center; gap:5px;
    }}
    .btn-primary {{ background:var(--primary); color:white; }}
    .btn-primary:hover {{ background:var(--primary-light); }}
    .btn-sm {{ padding:5px 10px; font-size:10px; }}

    .table-wrap {{ background:var(--white); border-radius:var(--radius); border:1px solid var(--border); overflow:hidden; }}
    .table-scroll {{ overflow-x:auto; max-height:55vh; }}
    table {{ width:100%; border-collapse:collapse; font-size:11px; }}
    th {{ background:var(--primary); color:white; padding:9px 6px; text-align:center; position:sticky; top:0; }}
    td {{ padding:7px 6px; text-align:center; border-bottom:1px solid var(--border); }}

    .badge {{ padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; color:white; }}
    .badge-success {{ background:var(--success); }}
    .badge-danger {{ background:var(--danger); }}
    .badge-warning {{ background:var(--warning); }}

    .pagination {{ display:flex; justify-content:center; gap:8px; margin-top:15px; }}

    .toast-container {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:10px; }}
    .toast {{ padding:12px 18px; border-radius:10px; color:white; font-size:13px; font-weight:600; box-shadow:0 8px 25px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; }}
    .toast.success {{ background:var(--success); }}
    .toast.error {{ background:var(--danger); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-25px); }} to {{ opacity:1; transform:translateY(0); }} }}

    @media (max-width:768px) {{
        .stats-row {{ grid-template-columns:repeat(2,1fr); }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="page-header">
        <h2>🕵️‍♂️ رصد اقدامات کاربران</h2>
        <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
    </div>

    <div class="stats-row" id="stats-row">
        <div class="stat-card"><div class="stat-value" style="color:#1e3a8a;" id="stat-total">0</div><div class="stat-label">📋 کل رخدادها</div></div>
        <div class="stat-card"><div class="stat-value" style="color:#10b981;" id="stat-success">0</div><div class="stat-label">✅ موفق</div></div>
        <div class="stat-card"><div class="stat-value" style="color:#ef4444;" id="stat-failed">0</div><div class="stat-label">❌ ناموفق</div></div>
        <div class="stat-card"><div class="stat-value" style="color:#f59e0b;" id="stat-users">0</div><div class="stat-label">👤 کاربران یکتا</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ (شمسی)</label><input type="text" id="f-from" value="{month_ago_shamsi}" placeholder="1400/01/01"></div>
            <div class="f-grp"><label>تا تاریخ (شمسی)</label><input type="text" id="f-to" value="{today_shamsi}" placeholder="1400/01/01"></div>
            <div class="f-grp"><label>کاربر</label><input type="text" id="f-user" placeholder="نام یا کد ملی"></div>
            <div class="f-grp"><label>عملیات</label><select id="f-action">{action_opts}</select></div>
            <div class="f-grp"><label>جدول</label><select id="f-table">{table_opts}</select></div>
            <div class="f-grp"><label>وضعیت</label><select id="f-status"><option value="">همه</option><option value="Success">موفق</option><option value="Failed">ناموفق</option></select></div>
        </div>
        <div class="f-row" style="margin-top:8px;">
            <div class="f-grp" style="flex:3;"><label>جستجوی سراسری</label><input type="text" id="f-search" placeholder="در مقادیر قدیم/جدید و خطا جستجو کنید..."></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-primary" onclick="fetchData(1)">🔍 اعمال فیلتر</button></div>
        </div>
    </div>

    <div class="table-wrap">
        <div class="table-scroll">
            <table>
                <thead>
                    <tr>
                        <th>کد</th><th>تاریخ/ساعت</th><th>کاربر</th><th>IP</th><th>عملیات</th><th>جدول</th><th>کلید</th><th>مقدار قدیم</th><th>مقدار جدید</th><th>وضعیت</th><th>خطا</th>
                    </tr>
                </thead>
                <tbody id="table-body"></tbody>
            </table>
        </div>
    </div>
    <div id="pagination" class="pagination"></div>
</div>

<script>
    let currentPage = 1;
    let totalPages = 1;

    function toast(msg, type) {{
        const c = document.getElementById('toast-container');
        const t = document.createElement('div');
        t.className = 'toast ' + (type==='success'?'success':'error');
        t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span>';
        c.appendChild(t);
        setTimeout(() => t.remove(), 4000);
    }}

    async function fetchData(page = 1) {{
        const params = new URLSearchParams({{
            from: (document.getElementById('f-from').value || '').trim(),
            to: (document.getElementById('f-to').value || '').trim(),
            user: document.getElementById('f-user').value,
            action: document.getElementById('f-action').value,
            table: document.getElementById('f-table').value,
            status: document.getElementById('f-status').value,
            search: document.getElementById('f-search').value,
            page: page,
            per_page: 20
        }});
        try {{
            const resp = await fetch('/module/admin/audit/data?' + params.toString());
            const data = await resp.json();
            if (data.success) {{
                renderTable(data.records);
                document.getElementById('stat-total').textContent = data.total;
                document.getElementById('stat-success').textContent = data.success_count;
                document.getElementById('stat-failed').textContent = data.failed_count;
                document.getElementById('stat-users').textContent = data.unique_users;
                currentPage = data.page;
                totalPages = Math.ceil(data.total / data.per_page) || 1;
                renderPagination();
            }} else {{
                toast(data.message || 'خطا در دریافت داده', 'error');
            }}
        }} catch(e) {{
            toast('خطا در ارتباط با سرور', 'error');
        }}
    }}

        
    function renderTable(records) {{
        const tbody = document.getElementById('table-body');
        if (!records.length) {{
            tbody.innerHTML = '<tr><td colspan="11" style="padding:30px;">داده‌ای یافت نشد</td></tr>';
            return;
        }}
        let html = '';
        records.forEach(r => {{
            const statusText = r.Status || '---';
            const statusBadge = statusText === 'Success' 
                ? '<span class="badge badge-success">موفق</span>' 
                : (statusText === 'Failed' || statusText === 'Error' 
                    ? '<span class="badge badge-danger">ناموفق</span>' 
                    : '<span class="badge badge-warning">' + statusText + '</span>');
                                
            const maxLen = 400;
            const oldVal = r.OldValue ? (r.OldValue.length > maxLen ? r.OldValue.substring(0, maxLen) + '...' : r.OldValue) : '-';
            const newVal = r.NewValue ? (r.NewValue.length > maxLen ? r.NewValue.substring(0, maxLen) + '...' : r.NewValue) : '-';                   
            const ip = r.IPAddress || '-';
            html += '<tr>' +
                '<td>' + r.Id + '</td>' +
                '<td>' + (r.DateTimeDisplay || '') + '</td>' +
                '<td>' + (r.UserDisplay || '') + '</td>' +
                '<td>' + ip + '</td>' +
                '<td>' + (r.Action || '') + '</td>' +
                '<td>' + (r.Table || '-') + '</td>' +
                '<td>' + (r.KeyValue || '-') + '</td>' +
                '<td>' + oldVal + '</td>' +
                '<td>' + newVal + '</td>' +
                '<td>' + statusBadge + '</td>' +
                '<td>' + (r.ErrorMessage || '-') + '</td>' +
            '</tr>';
        }});
        tbody.innerHTML = html;
    }}    
  
    function renderPagination() {{
        const container = document.getElementById('pagination');
        if (totalPages <= 1) {{ container.innerHTML = ''; return; }}
        let html = '';
        if (currentPage > 1) {{
            html += '<button class="btn btn-sm btn-primary" onclick="fetchData(' + (currentPage - 1) + ')">« قبلی</button>';
        }}
        html += '<span style="display:flex; align-items:center; font-size:13px; margin:0 10px;">صفحه ' + currentPage + ' از ' + totalPages + '</span>';
        if (currentPage < totalPages) {{
            html += '<button class="btn btn-sm btn-primary" onclick="fetchData(' + (currentPage + 1) + ')">بعدی »</button>';
        }}
        container.innerHTML = html;
    }}

    document.addEventListener('DOMContentLoaded', () => fetchData(1));
</script>
</body>
</html>'''
    return html


def get_audit_data(request_args):
    """API برای دریافت داده‌های جدول audittrail با فیلتر و صفحه‌بندی"""
    from_date_shamsi = request_args.get('from', '').strip()
    to_date_shamsi = request_args.get('to', '').strip()
    user_search = request_args.get('user', '').strip()
    action = request_args.get('action', '').strip()
    table_name = request_args.get('table', '').strip()
    status = request_args.get('status', '').strip()
    search = request_args.get('search', '').strip()
    page = int(request_args.get('page', 1))
    per_page = int(request_args.get('per_page', 20))

    # ========== تبدیل تاریخ شمسی به میلادی برای فیلتر ==========
    miladi_from = miladi_to = None
    if from_date_shamsi:
        try:
            parts = list(map(int, from_date_shamsi.replace('/', '-').split('-')))
            jd = jdatetime.date(parts[0], parts[1], parts[2])
            miladi_from = jd.togregorian()
        except:
            pass
    if to_date_shamsi:
        try:
            parts = list(map(int, to_date_shamsi.replace('/', '-').split('-')))
            jd = jdatetime.date(parts[0], parts[1], parts[2])
            miladi_to = jd.togregorian() + timedelta(days=1)  # تا پایان روز
        except:
            pass

    # ========== ساخت کوئری اصلی ==========
    sql = """
        SELECT a.Id, a.DateTime, a.Script, a.User, a.IPAddress, a.UserAgent,
               a.Action, a.`Table`, a.Field, a.KeyValue, a.OldValue, a.NewValue,
               a.Status, a.ErrorMessage, a.SessionID
        FROM audittrail a
        WHERE 1=1
    """
    params = []

    if miladi_from:
        sql += " AND a.DateTime >= %s"
        params.append(miladi_from)
    if miladi_to:
        sql += " AND a.DateTime < %s"
        params.append(miladi_to)

    if user_search:
        # جستجو در ستون User (مثل "UserID:123") از طریق JOIN با users
        sql += """ AND (
            a.User LIKE %s
            OR (SUBSTRING_INDEX(a.User, ':', -1) REGEXP '^[0-9]+$'
                AND CAST(SUBSTRING_INDEX(a.User, ':', -1) AS UNSIGNED) IN
                (SELECT UserID FROM users WHERE FullName LIKE %s OR Username LIKE %s))
        )"""
        params.extend([f'%{user_search}%', f'%{user_search}%', f'%{user_search}%'])

    if action:
        sql += " AND a.Action = %s"
        params.append(action)

    if table_name:
        sql += " AND a.`Table` = %s"
        params.append(table_name)

    if status:
        sql += " AND a.Status = %s"
        params.append(status)

    if search:
        sql += " AND (a.OldValue LIKE %s OR a.NewValue LIKE %s OR a.ErrorMessage LIKE %s)"
        like = f'%{search}%'
        params.extend([like, like, like])

    # تعداد کل (بدون صفحه‌بندی)
    count_sql = f"SELECT COUNT(*) as total FROM ({sql}) AS tmp"
    count_params = params.copy()
    total_row = query(count_sql, count_params, fetch_one=True)
    total_records = total_row['total'] if total_row else 0

    # محاسبه آمار کلی (مستقل از صفحه‌بندی)
    success_count = query(
        "SELECT COUNT(*) as cnt FROM audittrail WHERE Status='Success' AND 1=1",
        fetch_one=True
    )
    failed_count = query(
        "SELECT COUNT(*) as cnt FROM audittrail WHERE Status='Failed'",
        fetch_one=True
    )
    unique_users = query(
        "SELECT COUNT(DISTINCT User) as cnt FROM audittrail",
        fetch_one=True
    )

    # اعمال صفحه‌بندی
    offset = (page - 1) * per_page
    sql += " ORDER BY a.Id DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    records = query(sql, params, fetch_all=True) or []

    # فرمت نمایش تاریخ و نام کاربر
    for r in records:
        if r.get('DateTime'):
            try:
                dt_val = r['DateTime'] if isinstance(r['DateTime'], dt) else dt.fromisoformat(str(r['DateTime']))
                jdt_val = jdatetime.datetime.fromgregorian(datetime=dt_val)
                r['DateTimeDisplay'] = jdt_val.strftime("%Y/%m/%d %H:%M")
            except:
                r['DateTimeDisplay'] = str(r.get('DateTime', ''))
        else:
            r['DateTimeDisplay'] = '-'

        # سعی در نمایش نام واقعی کاربر
        raw_user = r.get('User', '')
        user_display = raw_user
        if raw_user.startswith('UserID:'):
            uid = raw_user.split(':')[-1].strip()
            if uid.isdigit():
                user_info = query("SELECT FullName FROM users WHERE UserID=%s", (int(uid),), fetch_one=True)
                if user_info:
                    user_display = user_info['FullName']
                else:
                    user_display = raw_user
        r['UserDisplay'] = user_display

    return {
        'success': True,
        'records': records,
        'total': total_records,
        'page': page,
        'per_page': per_page,
        'success_count': success_count['cnt'] if success_count else 0,
        'failed_count': failed_count['cnt'] if failed_count else 0,
        'unique_users': unique_users['cnt'] if unique_users else 0,
    }
    
    
