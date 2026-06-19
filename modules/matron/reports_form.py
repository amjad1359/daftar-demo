"""
فرم کارتابل مترون – بررسی و تأیید گزارشات سوپروایزری
نسخه جدید: افزودن قابلیت «فقط برای این مدیریت» (only_thisid)
"""

import os, json, jdatetime
from datetime import datetime
from models.database import query, get_connection
from utils.auto_log import log_crud

UPLOAD_DIR = "uploads/gozaresh"


def get_matron_reports_form(user):
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    shift = query(
        "SELECT ID_shift, tarkib FROM shift_namt ORDER BY ID_shift DESC LIMIT 1",
        fetch_one=True
    )
    shift_name = shift['tarkib'] if shift else 'نامشخص'

    depts = query(
        "SELECT ID_nam_modirit, nam_modiriat FROM tbl_nam_modiriat ORDER BY nam_modiriat",
        fetch_all=True
    ) or []
    dept_options = ''.join([f'<option value="{d["ID_nam_modirit"]}">{d["nam_modiriat"]}</option>' for d in depts])

    titles = query(
        "SELECT ID_onvan_gozaresh, nam_onvan_gozaresh FROM tbl_onvan_gozaresh ORDER BY nam_onvan_gozaresh",
        fetch_all=True
    ) or []
    title_options = ''.join([f'<option value="{t["ID_onvan_gozaresh"]}">{t["nam_onvan_gozaresh"]}</option>' for t in titles])

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
    .matron-header {{
        background:linear-gradient(135deg, #0f766e, #14b8a6); color:white; border-radius:16px; padding:25px 30px;
        margin-bottom:25px; display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(15,118,110,0.25);
    }}
    .matron-header h2 {{ font-size:24px; }}
    .shift-badge {{ background:rgba(255,255,255,0.2); padding:10px 20px; border-radius:30px; font-weight:bold; }}
    .back-btn {{ color:white; text-decoration:none; padding:8px 16px; border:1px solid rgba(255,255,255,0.4); border-radius:8px; transition:var(--transition); }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}
    .card {{ background:var(--white); border-radius:var(--radius); padding:25px; border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:25px; }}
    .row {{ display:flex; gap:15px; align-items:center; flex-wrap:wrap; }}
    .form-group {{ margin-bottom:18px; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:6px; }}
    .form-select, .form-input, .form-textarea {{
        width:100%; padding:12px 14px; border:2px solid var(--border); border-radius:8px;
        font-size:14px; font-family:inherit; transition:var(--transition); background:var(--white);
    }}
    .form-select:focus, .form-input:focus, .form-textarea:focus {{ border-color:var(--primary-light); outline:none; box-shadow:0 0 0 3px rgba(59,130,246,0.15); }}
    .form-textarea {{ min-height:100px; resize:vertical; }}
    .btn {{
        display:inline-flex; align-items:center; justify-content:center; gap:6px;
        padding:10px 20px; border:none; border-radius:8px; font-size:14px; font-weight:600;
        cursor:pointer; font-family:inherit; transition:var(--transition); text-decoration:none;
    }}
    .btn-primary {{ background:var(--primary); color:white; }} .btn-primary:hover {{ background:var(--primary-light); }}
    .btn-success {{ background:var(--success); color:white; }}
    .btn-danger {{ background:var(--danger); color:white; }}
    .btn-sm {{ padding:6px 12px; font-size:12px; }}

    .report-list-table {{ width:100%; border-collapse:collapse; }}
    .report-list-table th {{ background:var(--primary); color:white; padding:12px; font-size:13px; text-align:center; }}
    .report-list-table td {{ padding:10px; text-align:center; border-bottom:1px solid var(--border); font-size:13px; }}
    .report-list-table tr:hover {{ background:#f8fafc; cursor:pointer; }}
    .report-list-table .status-approved {{ color:var(--success); font-weight:bold; }}
    .report-list-table .status-pending {{ color:var(--warning); font-weight:bold; }}
    .action-buttons {{ display:flex; gap:5px; justify-content:center; }}

    .detail-card {{ margin-top:25px; }}
    .file-list {{ margin-top:10px; }}
    .file-list a {{ margin-left:12px; font-size:13px; }}

    .pagination {{ display:flex; justify-content:center; gap:10px; margin-top:20px; }}

    .toast-container {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:10px; pointer-events:none; }}
    .toast {{ display:flex; align-items:center; gap:12px; padding:14px 22px; border-radius:12px; color:white; font-weight:600; box-shadow:0 10px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; pointer-events:auto; }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }} .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}
    @media (max-width:768px) {{ .matron-header {{ flex-direction:column; gap:15px; text-align:center; }} }}
    .checkbox-custom {{
        display: flex; align-items: center; gap: 10px;
        padding: 14px 16px; background: #f0fdf4; border-radius: 8px;
        border: 1px solid #bbf7d0; cursor: pointer; user-select: none;
    }}
    .checkbox-custom input[type="checkbox"] {{ width: 20px; height: 20px; accent-color: #0f766e; }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="matron-header">
        <div><h2>📋 کارتابل مدیر پرستاری (مترون)</h2><p style="opacity:0.85;margin-top:5px;">بررسی و تأیید گزارشات سوپروایزری | شیفت: {shift_name}</p></div>
        <a href="/module/matron" class="back-btn">⬅️ بازگشت</a>
    </div>

    <!-- بخش فیلتر و لیست -->
    <div class="card">
        <div class="row" style="margin-bottom:15px;">
            <input type="text" id="search-input" class="form-input" placeholder="جستجو در عنوان یا سوپروایزر..." oninput="fetchReportList(1)" style="flex:1;">
            <select id="status-filter" class="form-select" style="width:180px;" onchange="fetchReportList(1)">
                <option value="all">همه</option>
                <option value="منتظر بررسی">⏳ منتظر بررسی</option>
                <option value="تایید شده">✅ تایید شده</option>
            </select>
        </div>
        <div style="overflow-x:auto;">
            <table class="report-list-table" id="report-table">
                <thead>
                    <tr>
                        <th>کد</th><th>تاریخ</th><th>شیفت</th><th>سوپروایزر</th><th>واحد</th><th>عنوان</th><th>وضعیت</th><th>عملیات</th>
                    </tr>
                </thead>
                <tbody id="report-tbody"></tbody>
            </table>
        </div>
        <div id="no-records" style="text-align:center; padding:20px; color:var(--light-gray); display:none;">گزارشی یافت نشد</div>
        <div id="pagination" class="pagination"></div>
    </div>

    <!-- بخش جزئیات -->
    <div id="detail-section" class="card detail-card" style="display:none;">
        <div class="row" style="justify-content:space-between; margin-bottom:15px;">
            <h3 id="detail-title" style="margin:0;">جزئیات گزارش</h3>
            <button class="btn btn-sm" onclick="closeDetail()">✖️ بستن</button>
        </div>
        <form id="detail-form">
            <input type="hidden" id="report-id" value="">
            <div class="row" style="margin-bottom:15px;">
                <div class="form-group" style="flex:1;">
                    <label>🎯 واحد مدیریت</label>
                    <select id="edit-dept" class="form-select">{dept_options}</select>
                </div>
                <div class="form-group" style="flex:1;">
                    <label>📌 موضوع گزارش</label>
                    <select id="edit-title" class="form-select">{title_options}</select>
                </div>
            </div>
            <div class="form-group">
                <label>📄 شرح واقعه</label>
                <textarea id="edit-mohtava" class="form-textarea" rows="4"></textarea>
            </div>
            <div class="form-group">
                <label>🛠️ اقدامات اصلاحی</label>
                <textarea id="edit-eghdam" class="form-textarea" rows="3"></textarea>
            </div>
            <div class="form-group">
                <label>📎 اسناد پیوست</label>
                <div id="files-container" class="file-list"></div>
            </div>

            <!-- 🆕 چک‌باکس فقط برای این مدیریت -->
            <div class="form-group" style="margin-top:20px;">
                <label class="checkbox-custom" id="only-thisid-label">
                    <input type="checkbox" id="only-thisid">
                    <span>🔒 فقط برای این مدیریت قابل مشاهده باشد</span>
                </label>
                <small style="color:var(--gray); display:block; margin-top:6px;">
                    در صورت انتخاب، این گزارش فقط برای مدیر همان واحد مدیریت نمایش داده خواهد شد.
                </small>
            </div>

            <div style="display:flex; gap:10px; margin-top:20px;">
                <button type="button" class="btn btn-success" id="approve-btn" onclick="approveReport()">
                    <span id="approve-text">✅ تایید و ارسال به مدیریت</span>
                    <span id="approve-loading" style="display:none;">⏳ ...</span>
                </button>
                <button type="button" class="btn btn-sm" onclick="closeDetail()">بازگشت</button>
            </div>
        </form>
    </div>
</div>

<script>
    var currentPage = 1;
    var totalPages = 1;

    document.addEventListener('DOMContentLoaded', () => {{
        fetchReportList(1);
    }});

    function showToast(msg, type) {{
        const c = document.getElementById('toast-container'), t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span><span style="cursor:pointer;margin-right:auto;" onclick="this.parentElement.remove()">✕</span>';
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    async function fetchReportList(page = 1) {{
        const search = document.getElementById('search-input').value;
        const status = document.getElementById('status-filter').value;
        try {{
            const res = await fetch(`/module/matron/reports/list?search=${{encodeURIComponent(search)}}&status=${{status}}&page=${{page}}&per_page=15`);
            const data = await res.json();
            if (data.success) {{
                renderTable(data.records);
                currentPage = data.page;
                totalPages = Math.ceil(data.total / data.per_page);
                renderPagination();
            }} else {{
                showToast('خطا در دریافت لیست', 'error');
            }}
        }} catch(e) {{ console.error(e); }}
    }}

    function renderTable(records) {{
        const tbody = document.getElementById('report-tbody');
        const noRecords = document.getElementById('no-records');
        if (!records.length) {{
            tbody.innerHTML = '';
            noRecords.style.display = 'block';
            return;
        }}
        noRecords.style.display = 'none';
        let html = '';
        records.forEach(r => {{
            const statusClass = r.taid_ersal == 1 ? 'status-approved' : 'status-pending';
            const statusText = r.taid_ersal == 1 ? '✅ تایید شده' : '⏳ منتظر بررسی';
            html += `<tr>
                <td>${{r.ID_gozaresh}}</td>
                <td>${{r.dat_sabt_display}}</td>
                <td>${{r.shift_name || '-'}}</td>
                <td>${{r.FullName || '-'}}</td>
                <td>${{r.nam_modiriat || '-'}}</td>
                <td>${{r.nam_onvan_gozaresh || '-'}}</td>
                <td class="${{statusClass}}">${{statusText}}</td>
                <td class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="loadDetail(${{r.ID_gozaresh}})">${{r.taid_ersal == 1 ? '🔍 مشاهده' : '✏️ بررسی'}}</button>
                </td>
            </tr>`;
        }});
        tbody.innerHTML = html;
    }}

    function renderPagination() {{
        const container = document.getElementById('pagination');
        if (totalPages <= 1) {{
            container.innerHTML = '';
            return;
        }}
        let html = '';
        if (currentPage > 1) {{
            html += `<button class="btn btn-sm btn-primary" onclick="fetchReportList(${{currentPage - 1}})">« قبلی</button>`;
        }}
        html += `<span style="display:flex; align-items:center; font-size:13px; margin:0 10px;">صفحه ${{currentPage}} از ${{totalPages}}</span>`;
        if (currentPage < totalPages) {{
            html += `<button class="btn btn-sm btn-primary" onclick="fetchReportList(${{currentPage + 1}})">بعدی »</button>`;
        }}
        container.innerHTML = html;
    }}

    async function loadDetail(reportId) {{
        try {{
            const res = await fetch('/module/matron/reports/get/' + reportId);
            const data = await res.json();
            if (data.success) {{
                const r = data.record;
                document.getElementById('report-id').value = r.ID_gozaresh;
                document.getElementById('edit-dept').value = r.nam_modirit;
                document.getElementById('edit-title').value = r.onvan_gozaresh;
                document.getElementById('edit-mohtava').value = r.mohtava_gozaresh || '';
                document.getElementById('edit-eghdam').value = r.eghdam_eslahi_avlieh || '';

                // بازنشانی چک‌باکس فقط برای این مدیریت
                document.getElementById('only-thisid').checked = (r.only_thisid == 1);

                const filesDiv = document.getElementById('files-container');
                let filesHtml = '';
                if (r.mostanad) {{
                    const files = r.mostanad.split(',').filter(f => f);
                    files.forEach(f => {{
                        const name = f.split('/').pop();
                        filesHtml += `<a href="/${{f}}" target="_blank" class="file-link">📎 ${{name}}</a>`;
                    }});
                }} else {{
                    filesHtml = '<span style="color:var(--light-gray);">بدون پیوست</span>';
                }}
                filesDiv.innerHTML = filesHtml;

                const isApproved = r.taid_ersal == 1;
                toggleEditFields(!isApproved);
                document.getElementById('approve-btn').style.display = isApproved ? 'none' : 'inline-flex';

                document.getElementById('detail-section').style.display = 'block';
                document.getElementById('detail-title').innerText = 'گزارش شماره ' + r.ID_gozaresh;
                document.getElementById('detail-section').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }} else {{
                showToast('گزارش یافت نشد', 'error');
            }}
        }} catch(e) {{ showToast('خطا در دریافت جزئیات', 'error'); }}
    }}

    function toggleEditFields(enabled) {{
        ['edit-dept', 'edit-title', 'edit-mohtava', 'edit-eghdam'].forEach(id => {{
            document.getElementById(id).disabled = !enabled;
        }});
    }}

    function closeDetail() {{
        document.getElementById('detail-section').style.display = 'none';
    }}

    async function approveReport() {{
        const reportId = document.getElementById('report-id').value;
        const dept = document.getElementById('edit-dept').value;
        const title = document.getElementById('edit-title').value;
        const mohtava = document.getElementById('edit-mohtava').value;
        const eghdam = document.getElementById('edit-eghdam').value;
        const onlyThisid = document.getElementById('only-thisid').checked ? '1' : '0';

        const formData = new FormData();
        formData.append('report_id', reportId);
        formData.append('dept_id', dept);
        formData.append('title_id', title);
        formData.append('mohtava', mohtava);
        formData.append('eghdam', eghdam);
        formData.append('only_thisid', onlyThisid);

        document.getElementById('approve-text').style.display = 'none';
        document.getElementById('approve-loading').style.display = 'inline';

        try {{
            const res = await fetch('/module/matron/reports/approve', {{ method:'POST', body: formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ گزارش تایید و ارسال شد', 'success');
                closeDetail();
                fetchReportList(currentPage);
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{ showToast('خطا در ارتباط', 'error'); }}
        finally {{
            document.getElementById('approve-text').style.display = 'inline';
            document.getElementById('approve-loading').style.display = 'none';
        }}
    }}
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions
# ==========================================

def get_matron_reports_list(search, status, page=1, per_page=15):
    offset = (page - 1) * per_page

    sql = """
        SELECT g.ID_gozaresh, g.dat_sabt, s.tarkib AS shift_name,
               u.FullName, m.nam_modiriat, o.nam_onvan_gozaresh,
               mp.taid_ersal, mp.only_thisid
        FROM tbl_gozaresh g
        LEFT JOIN shift_namt s ON g.ID_shift = s.ID_shift
        LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
        LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
        LEFT JOIN users u ON g.UserID = u.UserID
        LEFT JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh = mp.ID_gozaresh
        WHERE g.ersal_gozaresh = 1
    """
    params = []

    count_sql = """
        SELECT COUNT(*) as total
        FROM tbl_gozaresh g
        LEFT JOIN shift_namt s ON g.ID_shift = s.ID_shift
        LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
        LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
        LEFT JOIN users u ON g.UserID = u.UserID
        LEFT JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh = mp.ID_gozaresh
        WHERE g.ersal_gozaresh = 1
    """
    count_params = []

    if search:
        sql += " AND (o.nam_onvan_gozaresh LIKE %s OR u.FullName LIKE %s)"
        p = f'%{search}%'
        params.extend([p, p])
        count_sql += " AND (o.nam_onvan_gozaresh LIKE %s OR u.FullName LIKE %s)"
        count_params.extend([p, p])

    if status == 'منتظر بررسی':
        sql += " AND (mp.taid_ersal IS NULL OR mp.taid_ersal = 0)"
        count_sql += " AND (mp.taid_ersal IS NULL OR mp.taid_ersal = 0)"
    elif status == 'تایید شده':
        sql += " AND mp.taid_ersal = 1"
        count_sql += " AND mp.taid_ersal = 1"

    sql += " ORDER BY g.CreatedDate DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    records = query(sql, params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0

    for r in records:
        d = str(r.get('dat_sabt', ''))
        if len(d) == 8:
            r['dat_sabt_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}"
        else:
            r['dat_sabt_display'] = d

    return {'success': True, 'records': records, 'total': total, 'page': page, 'per_page': per_page}


def get_matron_report_detail(report_id):
    rec = query("""
        SELECT g.*, mp.taid_ersal, mp.only_thisid
        FROM tbl_gozaresh g
        LEFT JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh = mp.ID_gozaresh
        WHERE g.ID_gozaresh = %s
    """, (report_id,), fetch_one=True)
    if not rec:
        return {'success': False, 'message': 'گزارش یافت نشد'}
    for k in list(rec.keys()):
        if isinstance(rec[k], bytearray):
            rec[k] = rec[k].decode('utf-8')
    rec['taid_ersal'] = 1 if rec.get('taid_ersal') == 1 else 0
    rec['only_thisid'] = rec.get('only_thisid', 0) or 0
    return {'success': True, 'record': rec}


def approve_matron_report(user, form_data):
    user_id = user.get('UserID', 0)
    report_id = form_data.get('report_id')
    dept_id = form_data.get('dept_id')
    title_id = form_data.get('title_id')
    mohtava = form_data.get('mohtava')
    eghdam = form_data.get('eghdam')
    only_thisid = form_data.get('only_thisid', '0')  # '1' یا '0'

    if not report_id:
        return {'success': False, 'message': 'شناسه گزارش نامعتبر'}

    now = datetime.now()
    solar_date = int(jdatetime.date.today().strftime("%Y%m%d"))
    only_flag = 1 if only_thisid == '1' else 0

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE tbl_gozaresh SET
                mohtava_gozaresh=%s, eghdam_eslahi_avlieh=%s,
                onvan_gozaresh=%s, nam_modirit=%s
            WHERE ID_gozaresh=%s
        """, (mohtava, eghdam, title_id, dept_id, report_id))

        cursor_dict = conn.cursor(dictionary=True)
        cursor_dict.execute(
            "SELECT ID_gozaresh_modir_parstati FROM tbl_gozaresh_modir_parastari WHERE ID_gozaresh=%s",
            (report_id,)
        )
        existing = cursor_dict.fetchone()
        cursor_dict.close()

        if existing:
            cursor.execute("""
                UPDATE tbl_gozaresh_modir_parastari
                SET taid_ersal=1, ersal_Date=%s, dat_sabt=%s, UserID=%s, only_thisid=%s
                WHERE ID_gozaresh=%s
            """, (now, solar_date, user_id, only_flag, report_id))
        else:
            cursor.execute("""
                INSERT INTO tbl_gozaresh_modir_parastari
                (ID_gozaresh, taid_ersal, ersal_Date, dat_sabt, UserID, only_thisid)
                VALUES (%s, 1, %s, %s, %s, %s)
            """, (report_id, now, solar_date, user_id, only_flag))

        conn.commit()
        log_crud('approve_matron_report', user_id, key_value=report_id,
                 new_value=json.dumps({"dept_id": dept_id, "title_id": title_id, "only_thisid": only_flag},
                                     ensure_ascii=False))
        return {'success': True, 'message': 'گزارش با موفقیت تأیید و ارسال شد'}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'خطا: {str(e)}'}
    finally:
        cursor.close()
        conn.close()
        
       