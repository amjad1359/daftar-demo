"""
کارتابل مسئول فنی – بررسی و ثبت نظر فنی
نسخه Flask با AJAX، Toast و صفحه‌بندی
"""

import jdatetime
from datetime import datetime
from models.database import query, get_connection

UPLOAD_DIR = "uploads/gozaresh"


def get_fanni_reports_form(user):
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{ --primary:#1e3a8a; --primary-light:#3b82f6; --success:#10b981; --danger:#ef4444; --warning:#f59e0b; --dark:#1e293b; --gray:#64748b; --light-gray:#94a3b8; --border:#e2e8f0; --bg:#f1f5f9; --white:#fff; --radius:12px; --transition:0.2s ease; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'Segoe UI',Tahoma,sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0;transform:translateY(10px); }} to {{ opacity:1;transform:translateY(0); }} }}

    .container {{ max-width:1400px; margin:0 auto; padding:20px; }}
    .fanni-header {{
        background:linear-gradient(135deg, #2c3e50, #3498db); color:white; border-radius:16px; padding:25px 30px;
        margin-bottom:25px; display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(44,62,80,0.25);
    }}
    .fanni-header h2 {{ font-size:24px; }}
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
    .status-tag {{ padding:3px 12px; border-radius:14px; font-size:12px; font-weight:bold; }}
    .status-pending {{ background:#fff3cd; color:#856404; }}
    .status-done {{ background:#d4edda; color:#155724; }}

    .detail-section {{ display:none; }}
    .detail-section.show {{ display:block; }}

    .pagination {{ display:flex; justify-content:center; gap:10px; margin-top:20px; }}

    .toast-container {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:10px; pointer-events:none; }}
    .toast {{ display:flex; align-items:center; gap:12px; padding:14px 22px; border-radius:12px; color:white; font-weight:600; box-shadow:0 10px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }} .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}

    @media (max-width:768px) {{
        .fanni-header {{ flex-direction:column; gap:15px; text-align:center; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="fanni-header">
        <h2>⚙️ کارتابل مسئول فنی</h2>
        <a href="/module/fanni" class="back-btn">⬅️ بازگشت</a>
    </div>

    <!-- فیلتر و لیست -->
    <div class="card">
        <div class="row" style="margin-bottom:15px;">
            <input type="text" id="search-input" class="form-input" placeholder="جستجو..." oninput="fetchList(1)" style="flex:1;">
            <select id="status-filter" class="form-select" style="width:180px;" onchange="fetchList(1)">
                <option value="all">همه</option>
                <option value="pending">⏳ منتظر</option>
                <option value="done">✅ ثبت شده</option>
            </select>
        </div>
        <div style="overflow-x:auto;">
            <table class="report-table" id="report-table">
                <thead>
                    <tr><th>کد</th><th>تاریخ</th><th>شیفت</th><th>سوپروایزر</th><th>واحد</th><th>عنوان</th><th>وضعیت</th><th>عملیات</th></tr>
                </thead>
                <tbody id="report-tbody"></tbody>
            </table>
        </div>
        <div id="no-records" style="text-align:center;padding:20px;color:var(--light-gray); display:none;">گزارشی یافت نشد</div>
        <div id="pagination" class="pagination"></div>
    </div>

    <!-- بخش جزئیات -->
    <div class="card detail-section" id="detail-section">
        <div class="row" style="justify-content:space-between; margin-bottom:15px;">
            <h3 id="detail-title" style="margin:0;">جزئیات گزارش</h3>
            <button class="btn btn-sm" onclick="closeDetail()">✖️ بستن</button>
        </div>
        <div id="detail-content"></div>
    </div>
</div>

<script>
    var currentPage = 1;
    var totalPages = 1;

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
        try {{
            const res = await fetch('/module/fanni/reports/list?search=' + encodeURIComponent(search) + '&status=' + status + '&page=' + page + '&per_page=15');
            const data = await res.json();
            const tbody = document.getElementById('report-tbody');
            const noRecords = document.getElementById('no-records');
            if (!data.records || !data.records.length) {{
                tbody.innerHTML = '';
                noRecords.style.display = 'block';
                document.getElementById('pagination').innerHTML = '';
                return;
            }}
            noRecords.style.display = 'none';
            let html = '';
            data.records.forEach(r => {{
                const statusText = r.has_opinion ? '✅ ثبت شده' : '⏳ منتظر';
                const statusClass = r.has_opinion ? 'status-done' : 'status-pending';
                html += '<tr onclick="loadDetail(' + r.ID_gozaresh + ')">' +
                    '<td>' + r.ID_gozaresh + '</td>' +
                    '<td>' + (r.dat_sabt_display || '') + '</td>' +
                    '<td>' + (r.shift_name || '') + '</td>' +
                    '<td>' + (r.FullName || '') + '</td>' +
                    '<td>' + (r.nam_modiriat || '') + '</td>' +
                    '<td>' + (r.nam_onvan_gozaresh || '') + '</td>' +
                    '<td><span class="status-tag ' + statusClass + '">' + statusText + '</span></td>' +
                    '<td><button class="btn btn-primary btn-sm" onclick="event.stopPropagation();loadDetail(' + r.ID_gozaresh + ')">' + (r.has_opinion ? '🔍 مشاهده' : '✏️ نظر') + '</button></td>' +
                '</tr>';
            }});
            tbody.innerHTML = html;

            currentPage = data.page;
            totalPages = Math.ceil(data.total / data.per_page);
            renderPagination();
        }} catch(e) {{ console.error(e); }}
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

    async function loadDetail(reportId) {{
        try {{
            const res = await fetch('/module/fanni/reports/get/' + reportId);
            const data = await res.json();
            if (data.success) {{
                const r = data.record;
                let html = '<div class="row"><div class="form-group" style="flex:1;"><label>تاریخ</label><input class="form-input" value="' + (r.dat_sabt_display || '') + '" disabled></div>' +
                    '<div class="form-group" style="flex:1;"><label>شیفت</label><input class="form-input" value="' + (r.shift_name || '') + '" disabled></div></div>' +
                    '<div class="row"><div class="form-group" style="flex:1;"><label>واحد</label><input class="form-input" value="' + (r.nam_modiriat || '') + '" disabled></div>' +
                    '<div class="form-group" style="flex:1;"><label>سوپروایزر</label><input class="form-input" value="' + (r.FullName || '') + '" disabled></div></div>' +
                    '<div class="form-group"><label>شرح واقعه</label><textarea class="form-textarea" rows="3" disabled>' + (r.mohtava_gozaresh || '') + '</textarea></div>' +
                    '<div class="form-group"><label>اقدام اصلاحی</label><textarea class="form-textarea" rows="2" disabled>' + (r.eghdam_eslahi_avlieh || '') + '</textarea></div>';

                if (r.mostanad) {{
                    const files = r.mostanad.split(',').filter(f => f);
                    html += '<div class="form-group"><label>اسناد پیوست</label><div>';
                    files.forEach(f => {{
                        const name = f.split('/').pop();
                        html += '<a href="/' + f + '" target="_blank" style="margin-left:10px;">📎 ' + name + '</a>';
                    }});
                    html += '</div></div>';
                }}

                if (r.manager_response) {{
                    html += '<div class="form-group"><label>پاسخ مدیر</label><div class="form-input" style="background:#f9f9f9;">' + r.manager_response + '</div></div>';
                }}

                if (r.has_opinion) {{
                    html += '<div class="form-group"><label>نظر فنی</label><textarea class="form-textarea" rows="3" disabled>' + (r.nazar_msol_fanni || '') + '</textarea></div>';
                }} else {{
                    html += '<div class="form-group"><label>نظر فنی</label><textarea id="opinion-text" class="form-textarea" rows="3" placeholder="نظر فنی خود را بنویسید..."></textarea></div>';
                    html += '<button class="btn btn-primary" onclick="saveOpinion(' + reportId + ')">✅ ثبت نظر فنی</button>';
                }}

                document.getElementById('detail-content').innerHTML = html;
                document.getElementById('detail-section').classList.add('show');
                document.getElementById('detail-title').innerText = 'گزارش شماره ' + reportId;
                document.getElementById('detail-section').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }} else {{
                showToast('گزارش یافت نشد', 'error');
            }}
        }} catch(e) {{ showToast('خطا در دریافت جزئیات', 'error'); }}
    }}

    async function saveOpinion(reportId) {{
        const opinion = document.getElementById('opinion-text').value.trim();
        if (!opinion) {{ showToast('متن نظر الزامی است', 'error'); return; }}
        try {{
            const formData = new FormData();
            formData.append('report_id', reportId);
            formData.append('opinion_text', opinion);
            const res = await fetch('/module/fanni/reports/opinion', {{ method:'POST', body: formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ نظر ثبت شد', 'success');
                loadDetail(reportId);
                fetchList(currentPage); // بازگشت به همین صفحه
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    function closeDetail() {{
        document.getElementById('detail-section').classList.remove('show');
    }}

    document.addEventListener('DOMContentLoaded', () => fetchList(1));
</script>
</body>
</html>'''
    return html


# ==================== API Functions ====================

def get_fanni_reports_list(search, status, page=1, per_page=15):
    offset = (page - 1) * per_page

    sql = """
        SELECT g.ID_gozaresh, g.dat_sabt, s.tarkib AS shift_name,
               u.FullName, m.nam_modiriat, o.nam_onvan_gozaresh,
               (CASE WHEN f.ID_nazar_fanni IS NOT NULL THEN 1 ELSE 0 END) AS has_opinion,
               g.mohtava_gozaresh, g.eghdam_eslahi_avlieh, g.mostanad
        FROM tbl_gozaresh g
        JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh = mp.ID_gozaresh
        LEFT JOIN shift_namt s ON g.ID_shift = s.ID_shift
        LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
        LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
        LEFT JOIN users u ON g.UserID = u.UserID
        LEFT JOIN tbl_nazar_fanni f ON g.ID_gozaresh = f.kod_gozaresh
        WHERE mp.taid_ersal = 1
    """
    params = []

    count_sql = """
        SELECT COUNT(*) as total
        FROM tbl_gozaresh g
        JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh = mp.ID_gozaresh
        LEFT JOIN shift_namt s ON g.ID_shift = s.ID_shift
        LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
        LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
        LEFT JOIN users u ON g.UserID = u.UserID
        LEFT JOIN tbl_nazar_fanni f ON g.ID_gozaresh = f.kod_gozaresh
        WHERE mp.taid_ersal = 1
    """
    count_params = []

    if search:
        sql += " AND (o.nam_onvan_gozaresh LIKE %s OR u.FullName LIKE %s OR g.ID_gozaresh LIKE %s)"
        s = f'%{search}%'
        params.extend([s, s, s])
        count_sql += " AND (o.nam_onvan_gozaresh LIKE %s OR u.FullName LIKE %s OR g.ID_gozaresh LIKE %s)"
        count_params.extend([s, s, s])

    if status == 'pending':
        sql += " AND f.ID_nazar_fanni IS NULL"
        count_sql += " AND f.ID_nazar_fanni IS NULL"
    elif status == 'done':
        sql += " AND f.ID_nazar_fanni IS NOT NULL"
        count_sql += " AND f.ID_nazar_fanni IS NOT NULL"

    sql += " ORDER BY g.ID_gozaresh DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    records = query(sql, params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0

    for r in records:
        d = str(r.get('dat_sabt', ''))
        r['dat_sabt_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d
    return {'success': True, 'records': records, 'total': total, 'page': page, 'per_page': per_page}


def get_fanni_report_detail(report_id):
    rec = query("""
        SELECT g.*, s.tarkib AS shift_name, u.FullName, m.nam_modiriat, o.nam_onvan_gozaresh,
               f.nazar_msol_fanni, (CASE WHEN f.ID_nazar_fanni IS NOT NULL THEN 1 ELSE 0 END) AS has_opinion,
               pj.javab_sharh_kamel AS manager_response
        FROM tbl_gozaresh g
        LEFT JOIN shift_namt s ON g.ID_shift = s.ID_shift
        LEFT JOIN users u ON g.UserID = u.UserID
        LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
        LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
        LEFT JOIN tbl_nazar_fanni f ON g.ID_gozaresh = f.kod_gozaresh
        LEFT JOIN tbl_pasokh_modir_javab pj ON g.ID_gozaresh = pj.kod_gozaresh
        WHERE g.ID_gozaresh = %s
    """, (report_id,), fetch_one=True)
    if not rec:
        return {'success': False}
    for k in list(rec.keys()):
        if isinstance(rec[k], bytearray):
            rec[k] = rec[k].decode('utf-8')
    d = str(rec.get('dat_sabt', ''))
    rec['dat_sabt_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d
    return {'success': True, 'record': rec}


def save_fanni_opinion(user, form_data):
    user_id = user.get('UserID', 0)
    report_id = form_data.get('report_id')
    opinion = form_data.get('opinion_text', '').strip()
    if not opinion:
        return {'success': False, 'message': 'متن نظر الزامی است'}
    existing = query("SELECT ID_nazar_fanni FROM tbl_nazar_fanni WHERE kod_gozaresh = %s", (report_id,), fetch_one=True)
    if existing:
        return {'success': False, 'message': 'نظر فنی قبلاً ثبت شده است'}
    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()
    try:
        query("""
            INSERT INTO tbl_nazar_fanni
            (kod_gozaresh, nazar_msol_fanni, taiid_nazar, dat_sabt, dat_payan, UserID)
            VALUES (%s, %s, 1, %s, %s, %s)
        """, (report_id, opinion, today, now, user_id), commit=True)
        return {'success': True, 'message': 'نظر فنی با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
        
        
