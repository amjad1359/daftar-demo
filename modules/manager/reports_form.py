"""
modules/manager/reports_form.py — نسخه نهایی و کامل
کارتابل مدیران اجرایی با پشتیبانی از:
- گزارش‌های خصوصی (only_thisid) و نمایش آیکون قفل
- فیلتر بر اساس واحد، وضعیت پاسخ و جستجو
- پاسخ‌دهی بر اساس مجوز چندواحدی (tbl_user_units)
- KPI، صفحه‌بندی، تاریخ شمسی
"""

import json
import jdatetime
from datetime import datetime
from models.database import query
from utils.auto_log import log_crud


def get_manager_reports_form(user):
    """
    صفحه HTML کارتابل مدیران اجرایی
    """
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')
    # postmodir دیگر تنها معیار نیست، ولی برای سازگاری نگه داشته می‌شود
    postmodir = user.get('postmodir', 0)

    # عنوان‌های پاسخ‌های قبلی (برای انتخاب سریع)
    prev_titles = query(
        "SELECT DISTINCT pasokh_onvan FROM tbl_pasokh_modir_javab "
        "WHERE pasokh_onvan IS NOT NULL AND pasokh_onvan != ''",
        fetch_all=True
    ) or []
    titles_options = '<option value="">--- انتخاب سریع ---</option>'
    for t in prev_titles:
        titles_options += f'<option value="{t["pasokh_onvan"]}">{t["pasokh_onvan"]}</option>'

    html = f'''<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>کارتابل مدیران اجرایی</title>
<style>
    :root {{ --primary:#1e3a8a; --primary-light:#3b82f6; --success:#10b981; --danger:#ef4444; --warning:#f59e0b; --dark:#1e293b; --gray:#64748b; --light-gray:#94a3b8; --border:#e2e8f0; --bg:#f1f5f9; --white:#fff; --radius:12px; --transition:0.2s ease; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'Segoe UI',Tahoma,sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0;transform:translateY(10px); }} to {{ opacity:1;transform:translateY(0); }} }}

    .container {{ max-width:1400px; margin:0 auto; padding:20px; }}
    .manager-header {{
        background:linear-gradient(135deg, #2c3e50, #3498db); color:white; border-radius:16px; padding:25px 30px;
        margin-bottom:25px; display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(44,62,80,0.25);
    }}
    .manager-header h2 {{ font-size:24px; }}
    .back-btn {{ color:white; text-decoration:none; padding:8px 16px; border:1px solid rgba(255,255,255,0.4); border-radius:8px; }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    .card {{ background:var(--white); border-radius:var(--radius); padding:25px; border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:25px; }}
    .row {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }}
    .form-group {{ margin-bottom:18px; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:6px; }}
    .form-select, .form-input, .form-textarea {{
        width:100%; padding:12px 14px; border:2px solid var(--border); border-radius:8px;
        font-size:14px; font-family:inherit; transition:var(--transition); background:var(--white);
    }}
    .form-select:focus, .form-input:focus, .form-textarea:focus {{ border-color:var(--primary-light); outline:none; box-shadow:0 0 0 3px rgba(59,130,246,0.15); }}
    .form-textarea {{ min-height:100px; resize:vertical; }}

    .btn {{ display:inline-flex; align-items:center; justify-content:center; gap:6px; padding:10px 20px; border:none; border-radius:8px; font-size:14px; font-weight:600; cursor:pointer; font-family:inherit; transition:var(--transition); text-decoration:none; }}
    .btn-primary {{ background:var(--primary); color:white; }} .btn-primary:hover {{ background:var(--primary-light); }}
    .btn-success {{ background:var(--success); color:white; }} .btn-sm {{ padding:6px 12px; font-size:12px; }}

    .report-table {{ width:100%; border-collapse:collapse; }}
    .report-table th {{ background:var(--primary); color:white; padding:12px; font-size:13px; text-align:center; }}
    .report-table td {{ padding:10px; text-align:center; border-bottom:1px solid var(--border); font-size:13px; }}
    .report-table tr:hover {{ background:#f8fafc; cursor:pointer; }}
    .status-badge {{ display:inline-block; padding:4px 14px; border-radius:14px; font-size:12px; font-weight:600; }}
    .status-pending {{ background:#fff3cd; color:#856404; }}
    .status-done {{ background:#d4edda; color:#155724; }}
    .lock-icon {{ color: #92400e; margin-left: 4px; font-size: 14px; vertical-align: middle; }}

    .detail-section {{ display:none; }}
    .detail-section.show {{ display:block; }}

    .kpi-row {{ display:grid; grid-template-columns:repeat(3,1fr); gap:15px; margin-bottom:25px; }}
    .kpi-card {{ background:white; border-radius:10px; padding:20px; text-align:center; border:1px solid var(--border); }}
    .kpi-value {{ font-size:28px; font-weight:bold; color:var(--primary); }}
    .kpi-label {{ font-size:13px; color:var(--gray); margin-top:5px; }}

    .pagination {{ display:flex; justify-content:center; gap:10px; margin-top:20px; }}

    .toast-container {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:10px; pointer-events:none; }}
    .toast {{ display:flex; align-items:center; gap:12px; padding:14px 22px; border-radius:12px; color:white; font-weight:600; box-shadow:0 10px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }} .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}

    @media (max-width:768px) {{
        .manager-header {{ flex-direction:column; gap:15px; text-align:center; }}
        .kpi-row {{ grid-template-columns:1fr; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="manager-header">
        <h2>💼 کارتابل مدیران اجرایی</h2>
        <a href="/module/manager" class="back-btn">⬅️ بازگشت</a>
    </div>

    <!-- KPI -->
    <div class="kpi-row" id="kpi-row">
        <div class="kpi-card"><div class="kpi-value" id="kpi-total">0</div><div class="kpi-label">📋 کل گزارشات</div></div>
        <div class="kpi-card"><div class="kpi-value" id="kpi-pending">0</div><div class="kpi-label">⏳ منتظر پاسخ</div></div>
        <div class="kpi-card"><div class="kpi-value" id="kpi-done">0</div><div class="kpi-label">✅ پاسخ داده شده</div></div>
    </div>

    <!-- فیلترها -->
    <div class="card">
        <div class="row" style="margin-bottom:15px;">
            <input type="text" id="search-input" class="form-input" placeholder="جستجو..." oninput="fetchList(1)" style="flex:2;">
            <select id="unit-filter" class="form-select" onchange="fetchList(1)" style="flex:1;">
                <option value="all">همه واحدها</option>
            </select>
            <select id="status-filter" class="form-select" style="width:180px;" onchange="fetchList(1)">
                <option value="all">همه</option><option value="pending">⏳ منتظر پاسخ</option><option value="done">✅ پاسخ داده شده</option>
            </select>
        </div>
        <div style="overflow-x:auto;">
            <table class="report-table" id="report-table">
                <thead><tr>
                    <th>کد</th><th>تاریخ</th><th>شیفت</th><th>سوپروایزر</th><th>واحد</th><th>عنوان</th><th>وضعیت</th><th>عملیات</th>
                </tr></thead>
                <tbody id="report-tbody"></tbody>
            </table>
        </div>
        <div id="no-records" style="text-align:center;padding:20px;color:var(--light-gray);display:none;">گزارشی یافت نشد</div>
        <div id="pagination" class="pagination"></div>
    </div>

    <!-- جزئیات -->
    <div class="card detail-section" id="detail-section">
        <div class="row" style="justify-content:space-between;margin-bottom:15px;">
            <h3 id="detail-title">جزئیات گزارش</h3>
            <button class="btn btn-sm" onclick="closeDetail()">✖️ بستن</button>
        </div>
        <div id="detail-content"></div>
    </div>
</div>

<script>
    var currentPage = 1;
    var totalPages = 1;
    // برای سازگاری با کدهای قدیمی
    const userPostmodir = {postmodir};

    function showToast(msg, type) {{
        const c = document.getElementById('toast-container'), t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span><span style="cursor:pointer;margin-right:auto;" onclick="this.parentElement.remove()">✕</span>';
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    async function fetchList(page = 1) {{
        const search = document.getElementById('search-input').value;
        const status = document.getElementById('status-filter').value;
        const unit = document.getElementById('unit-filter').value;
        try {{
            const res = await fetch('/module/manager/reports/list?search=' + encodeURIComponent(search) + '&status=' + status + '&unit=' + unit + '&page=' + page + '&per_page=15');
            const data = await res.json();
            if (!data.success) {{ showToast(data.message, 'error'); return; }}
            const tbody = document.getElementById('report-tbody');
            const noRecords = document.getElementById('no-records');
            if (!data.records || !data.records.length) {{
                tbody.innerHTML = '';
                noRecords.style.display = 'block';
                updateKpi(0,0,0);
                document.getElementById('pagination').innerHTML = '';
                return;
            }}
            noRecords.style.display = 'none';
            populateUnitDropdown(data.units || []);
            let pending = 0, done = 0;
            let html = '';
            data.records.forEach(r => {{
                const isDone = r.has_response;
                if (isDone) done++; else pending++;
                const statusText = isDone ? '✅ پاسخ داده شده' : '⏳ منتظر پاسخ';
                const statusClass = isDone ? 'status-done' : 'status-pending';
                const lockIcon = (r.only_thisid == 1) ? ' <span class="lock-icon" title="محدود به همین مدیریت">🔒</span>' : '';
                html += '<tr onclick="loadDetail(' + r.ID_gozaresh + ')">' +
                    '<td>' + r.ID_gozaresh + '</td>' +
                    '<td>' + (r.dat_sabt_display || '') + '</td>' +
                    '<td>' + (r.shift_name || '') + '</td>' +
                    '<td>' + (r.FullName || '') + '</td>' +
                    '<td>' + (r.nam_modiriat || '') + '</td>' +
                    '<td>' + (r.nam_onvan_gozaresh || '') + '</td>' +
                    '<td><span class="status-badge ' + statusClass + '">' + statusText + '</span>' + lockIcon + '</td>' +
                    '<td><button class="btn btn-primary btn-sm" onclick="event.stopPropagation();loadDetail(' + r.ID_gozaresh + ')">' + (isDone ? '🔍 مشاهده' : '✏️ پاسخ') + '</button></td>' +
                '</tr>';
            }});
            tbody.innerHTML = html;
            updateKpi(data.total, pending, done);

            currentPage = data.page;
            totalPages = Math.ceil(data.total / data.per_page);
            renderPagination();
        }} catch(e) {{ showToast('خطا در شبکه', 'error'); }}
    }}

    function renderPagination() {{
        const container = document.getElementById('pagination');
        if (totalPages <= 1) {{
            container.innerHTML = '';
            return;
        }}
        let html = '';
        if (currentPage > 1) {{
            html += '<button class="btn btn-sm btn-primary" onclick="fetchList(' + (currentPage - 1) + ')">« قبلی</button>';
        }}
        html += '<span style="display:flex; align-items:center; font-size:13px; margin:0 10px;">صفحه ' + currentPage + ' از ' + totalPages + '</span>';
        if (currentPage < totalPages) {{
            html += '<button class="btn btn-sm btn-primary" onclick="fetchList(' + (currentPage + 1) + ')">بعدی »</button>';
        }}
        container.innerHTML = html;
    }}

    function populateUnitDropdown(units) {{
        const sel = document.getElementById('unit-filter');
        const currentVal = sel.value;
        sel.innerHTML = '<option value="all">همه واحدها</option>';
        units.forEach(u => {{
            sel.innerHTML += '<option value="' + u + '">' + u + '</option>';
        }});
        if (units.includes(currentVal)) sel.value = currentVal;
        else sel.value = 'all';
    }}

    function updateKpi(total, pending, done) {{
        document.getElementById('kpi-total').innerText = total;
        document.getElementById('kpi-pending').innerText = pending;
        document.getElementById('kpi-done').innerText = done;
    }}

    async function loadDetail(reportId) {{
        try {{
            const res = await fetch('/module/manager/reports/get/' + reportId);
            const data = await res.json();
            if (!data.success) {{ showToast(data.message, 'error'); return; }}
            const r = data.record;
            let html = '<div class="row"><div class="form-group" style="flex:1;"><label>تاریخ</label><input class="form-input" value="' + (r.dat_sabt_display || '') + '" disabled></div>' +
                '<div class="form-group" style="flex:1;"><label>شیفت</label><input class="form-input" value="' + (r.shift_name || '') + '" disabled></div></div>' +
                '<div class="row"><div class="form-group" style="flex:1;"><label>واحد</label><input class="form-input" value="' + (r.nam_modiriat || '') + '" disabled></div>' +
                '<div class="form-group" style="flex:1;"><label>سوپروایزر</label><input class="form-input" value="' + (r.FullName || '') + '" disabled></div></div>' +
                '<div class="form-group"><label>📄 شرح واقعه</label><textarea class="form-textarea" rows="3" disabled>' + (r.mohtava_gozaresh || '') + '</textarea></div>' +
                '<div class="form-group"><label>🛠️ اقدام اصلاحی</label><textarea class="form-textarea" rows="2" disabled>' + (r.eghdam_eslahi_avlieh || '') + '</textarea></div>';

            if (r.mostanad) {{
                const files = r.mostanad.split(',').filter(f => f);
                html += '<div class="form-group"><label>📎 اسناد پیوست</label><div>';
                files.forEach(f => {{ html += '<a href="/' + f + '" target="_blank" style="margin-left:10px;">📄 ' + f.split('/').pop() + '</a>'; }});
                html += '</div></div>';
            }}

            // نمایش پاسخ‌های قبلی (همه)
            if (data.prior_responses && data.prior_responses.length) {{
                html += '<div class="form-group"><label>💬 پاسخ‌های ثبت شده</label>';
                data.prior_responses.forEach(resp => {{
                    html += '<div class="card" style="padding:10px;margin-bottom:8px; border-right: 3px solid #3b82f6;"><strong>' + resp.FullName + ' – ' + resp.pasokh_onvan + '</strong><br><small>' + resp.javab_sharh_kamel + '</small></div>';
                }});
                html += '</div>';
            }}

            // کاربر قبلاً پاسخ داده است → فقط نمایش می‌دهیم و فیلدها را قفل می‌کنیم
            if (data.current_response) {{
                html += '<div class="form-group" style="background:#d4edda;padding:12px;border-radius:8px;color:#155724;">✅ شما قبلاً به این گزارش پاسخ داده‌اید. پاسخ شما در میان پاسخ‌های ثبت شده قابل مشاهده است.</div>';
            }}
            // کاربر هنوز پاسخ نداده و مجاز است
            else if (data.can_respond) {{
                html += '<div class="form-group"><label>🏷️ عنوان پاسخ</label>' +
                    '<div class="row"><select id="title-select" class="form-select" style="flex:1;">{titles_options}</select>' +
                    '<input type="text" id="title-input" class="form-input" placeholder="عنوان جدید..." style="flex:2;"></div></div>' +
                    '<div class="form-group"><label>📝 شرح کامل جوابیه</label><textarea id="reply-content" class="form-textarea" rows="4" placeholder="متن پاسخ..."></textarea></div>' +
                    '<button class="btn btn-primary" id="submit-response-btn" onclick="saveResponse(' + reportId + ')">✅ ثبت پاسخ</button>';
            }}
            // مجاز نیست
            else {{
                html += '<div class="form-group" style="background:#f8d7da;padding:12px;border-radius:8px;color:#721c24;">⛔ شما مجوز پاسخگویی به این گزارش را ندارید.</div>';
            }}

            document.getElementById('detail-content').innerHTML = html;
            document.getElementById('detail-section').classList.add('show');
            document.getElementById('detail-title').innerText = 'گزارش شماره ' + reportId;
            document.getElementById('detail-section').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    async function saveResponse(reportId) {{
        const title = document.getElementById('title-input').value.trim();
        const content = document.getElementById('reply-content').value.trim();
        if (!title || !content) {{ showToast('عنوان و متن پاسخ الزامی است', 'error'); return; }}
        try {{
            const formData = new FormData();
            formData.append('report_id', reportId);
            formData.append('title', title);
            formData.append('content', content);
            const res = await fetch('/module/manager/reports/respond', {{ method:'POST', body:formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ پاسخ ثبت شد', 'success');
                closeDetail();
                loadDetail(reportId);
                fetchList(currentPage);
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    function closeDetail() {{
        document.getElementById('detail-section').classList.remove('show');
    }}

    document.addEventListener('change', function(e) {{
        if (e.target.id === 'title-select') {{
            document.getElementById('title-input').value = e.target.value;
        }}
    }});

    document.addEventListener('DOMContentLoaded', () => fetchList(1));
</script>
</body>
</html>'''
    return html


# ══════════════════════════════════════════════════════════
# API Functions
# ══════════════════════════════════════════════════════════

def get_manager_reports_list(user, search, status, unit, page=1, per_page=15):
    """
    دریافت لیست گزارش‌های ارسال‌شده به مدیران اجرایی.
    - گزارش‌های دارای only_thisid=1 فقط در صورتی نمایش داده می‌شوند که
      مدیر از طریق tbl_user_units به واحد همان گزارش دسترسی داشته باشد.
    """
    user_id = user.get('UserID', 0)
    offset = (page - 1) * per_page

    # شرط محدودیت only_thisid: عمومی باشد، یا مدیر به واحد آن دسترسی داشته باشد
    restriction = """
        AND (
            mp.only_thisid = 0
            OR EXISTS (
                SELECT 1 FROM tbl_user_units uu
                WHERE uu.user_id = %s AND uu.unit_id = g.nam_modirit
            )
        )
    """

    sql = f"""
        SELECT g.ID_gozaresh, g.dat_sabt, s.tarkib AS shift_name,
               u.FullName, m.nam_modiriat, o.nam_onvan_gozaresh,
               (CASE WHEN pj.ID_javab_modir IS NOT NULL THEN 1 ELSE 0 END) AS has_response,
               mp.only_thisid
        FROM tbl_gozaresh g
        JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh = mp.ID_gozaresh
        LEFT JOIN shift_namt s ON g.ID_shift = s.ID_shift
        LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
        LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
        LEFT JOIN users u ON g.UserID = u.UserID
        LEFT JOIN tbl_pasokh_modir_javab pj ON g.ID_gozaresh = pj.kod_gozaresh
        WHERE mp.taid_ersal = 1
        {restriction}
    """
    params = [user_id]

    count_sql = f"""
        SELECT COUNT(*) as total
        FROM tbl_gozaresh g
        JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh = mp.ID_gozaresh
        LEFT JOIN shift_namt s ON g.ID_shift = s.ID_shift
        LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
        LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
        LEFT JOIN users u ON g.UserID = u.UserID
        LEFT JOIN tbl_pasokh_modir_javab pj ON g.ID_gozaresh = pj.kod_gozaresh
        WHERE mp.taid_ersal = 1
        {restriction}
    """
    count_params = [user_id]

    if unit and unit != 'all':
        sql += " AND m.nam_modiriat = %s"
        params.append(unit)
        count_sql += " AND m.nam_modiriat = %s"
        count_params.append(unit)

    if search:
        sql += " AND (o.nam_onvan_gozaresh LIKE %s OR u.FullName LIKE %s OR g.ID_gozaresh LIKE %s)"
        s = f'%{search}%'
        params.extend([s, s, s])
        count_sql += " AND (o.nam_onvan_gozaresh LIKE %s OR u.FullName LIKE %s OR g.ID_gozaresh LIKE %s)"
        count_params.extend([s, s, s])

    if status == 'pending':
        sql += " AND pj.ID_javab_modir IS NULL"
        count_sql += " AND pj.ID_javab_modir IS NULL"
    elif status == 'done':
        sql += " AND pj.ID_javab_modir IS NOT NULL"
        count_sql += " AND pj.ID_javab_modir IS NOT NULL"

    sql += " ORDER BY g.ID_gozaresh DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    records = query(sql, params, fetch_all=True) or []
    total_res = query(count_sql, count_params, fetch_one=True)
    total = total_res['total'] if total_res else 0

    # لیست واحدها برای دراپ‌داون
    units_rows = query(
        "SELECT DISTINCT nam_modiriat FROM tbl_nam_modiriat ORDER BY nam_modiriat",
        fetch_all=True
    ) or []
    unit_list = [u['nam_modiriat'] for u in units_rows]

    for r in records:
        d = str(r.get('dat_sabt', ''))
        r['dat_sabt_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d
        r['only_thisid'] = r.get('only_thisid', 0) or 0

    return {'success': True, 'records': records, 'units': unit_list, 'total': total,
            'page': page, 'per_page': per_page}


def get_manager_report_detail(user, report_id):
    """
    جزئیات یک گزارش به همراه وضعیت پاسخ‌دهی و مجوز دسترسی
    (با استفاده از tbl_user_units برای احراز صلاحیت پاسخ‌گویی)
    """
    user_id = int(user.get('UserID', 0))

    rec = query("""
        SELECT g.*, s.tarkib AS shift_name, u.FullName, m.nam_modiriat,
               o.nam_onvan_gozaresh
        FROM tbl_gozaresh g
        LEFT JOIN shift_namt s ON g.ID_shift = s.ID_shift
        LEFT JOIN users u ON g.UserID = u.UserID
        LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
        LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
        WHERE g.ID_gozaresh = %s
    """, (report_id,), fetch_one=True)

    if not rec:
        return {'success': False, 'message': 'گزارش یافت نشد'}

    for k in list(rec.keys()):
        if isinstance(rec[k], bytearray):
            rec[k] = rec[k].decode('utf-8')
    d = str(rec.get('dat_sabt', ''))
    rec['dat_sabt_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d

    # بررسی مجوز پاسخگویی (بر اساس tbl_user_units)
    unit_id = rec.get('nam_modirit')   # شناسه واحد
    can_respond = False
    if unit_id:
        access = query(
            "SELECT 1 FROM tbl_user_units WHERE user_id = %s AND unit_id = %s",
            (user_id, unit_id), fetch_one=True
        )
        if access:
            can_respond = True

    # دریافت تمام پاسخ‌های قبلی
    prior_responses = query("""
        SELECT p.*, u.FullName
        FROM tbl_pasokh_modir_javab p
        LEFT JOIN users u ON p.UserID = u.UserID
        WHERE p.kod_gozaresh = %s
        ORDER BY p.dat_sabt DESC
    """, (report_id,), fetch_all=True) or []

    current_response = None
    for resp in prior_responses:
        for k in list(resp.keys()):
            if isinstance(resp[k], bytearray):
                resp[k] = resp[k].decode('utf-8')
        if str(resp.get('UserID')) == str(user_id):
            current_response = resp

    if current_response:
        can_respond = False

    return {
        'success': True,
        'record': rec,
        'prior_responses': prior_responses,
        'current_response': current_response,
        'can_respond': can_respond
    }


def save_manager_response(user, form_data):
    """
    ثبت پاسخ مدیر اجرایی به یک گزارش
    """
    user_id = user.get('UserID', 0)
    report_id = form_data.get('report_id')
    title = form_data.get('title', '').strip()
    content = form_data.get('content', '').strip()

    if not title or not content:
        return {'success': False, 'message': 'عنوان و متن پاسخ الزامی است'}

    # بررسی مجوز (مجددا) از طریق tbl_user_units
    check_access = query("""
        SELECT 1 FROM tbl_gozaresh g
        INNER JOIN tbl_user_units uu ON g.nam_modirit = uu.unit_id
        WHERE g.ID_gozaresh = %s AND uu.user_id = %s
    """, (report_id, user_id), fetch_one=True)

    if not check_access:
        return {'success': False, 'message': 'شما مجوز پاسخگویی به این گزارش را ندارید'}

    # جلوگیری از پاسخ تکراری
    existing = query(
        "SELECT ID_javab_modir FROM tbl_pasokh_modir_javab WHERE kod_gozaresh = %s AND UserID = %s",
        (report_id, user_id), fetch_one=True
    )
    if existing:
        return {'success': False, 'message': 'شما قبلاً به این گزارش پاسخ داده‌اید'}

    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()
    try:
        query("""
            INSERT INTO tbl_pasokh_modir_javab
            (kod_gozaresh, pasokh_onvan, javab_sharh_kamel, dat_sabt, zaman_open, dat_payan, payan_kar, UserID)
            VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
        """, (report_id, title, content, today, now, now, user_id), commit=True)
        log_crud('save_manager_response', user_id, key_value=report_id,
                 new_value=f"پاسخ به گزارش {report_id}: {title}")
        return {'success': True, 'message': 'پاسخ با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
        
        
