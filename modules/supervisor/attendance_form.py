"""
modules/supervisor/attendance_form.py — نسخه نهایی (بدون active_shift_name)
فرم ثبت حضور و غیاب با ریزشیفت بر اساس ID_onvan_shift
"""

from models.database import query
import jdatetime
from datetime import datetime
import json
from utils.auto_log import log_crud


def _ensure_rizshift_int():
    """تبدیل ستون rizshift از VARCHAR به INT (در صورت نیاز)"""
    try:
        col = query("SHOW COLUMNS FROM tbl_hozor LIKE 'rizshift'", fetch_one=True)
        if col and 'varchar' in str(col.get('Type', '')).lower():
            query("UPDATE tbl_hozor SET rizshift = NULL WHERE rizshift IS NOT NULL AND rizshift REGEXP '[^0-9]'", commit=True)
            query("ALTER TABLE tbl_hozor MODIFY COLUMN rizshift INT DEFAULT NULL", commit=True)
    except Exception:
        pass


def get_attendance_form(user, message=None, error=None):
    """فرم ثبت حضور و غیاب پرسنل"""

    _ensure_rizshift_int()

    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    # ========== شیفت فعال ==========
    active_shift = query(
        "SELECT ID_shift, tarkib, nam_shift FROM shift_namt ORDER BY ID_shift DESC LIMIT 1",
        fetch_one=True
    )
    if not active_shift:
        return '''
        <div class="content-card fade-in">
            <div style="text-align:center;padding:60px;">
                <div style="font-size:64px;">⚠️</div>
                <h3>شیفت فعالی یافت نشد</h3>
                <p style="color:#94a3b8;">لطفاً ابتدا یک شیفت ثبت کنید</p>
                <a href="/module/supervisor/shift" class="btn btn-primary">📅 ثبت شیفت</a>
            </div>
        </div>'''

    shift_id = active_shift['ID_shift']
    shift_name = active_shift['tarkib'] or '---'

    # nam_shift در shift_namt حالا ID_onvan_shift است → مستقیماً به عنوان پیش‌فرض ریزشیفت
    default_rizshift_id = active_shift.get('nam_shift', '')

    # ========== بخش‌ها ==========
    departments = query(
        "SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh",
        fetch_all=True
    ) or []

    # ========== لیست شیفت‌ها برای dropdown ==========
    shift_list = query(
        "SELECT ID_onvan_shift, shift_code FROM onvan_shift ORDER BY shift_code",
        fetch_all=True
    ) or []

    # ========== بخش‌های ثبت‌شده در این شیفت ==========
    registered = query("""
        SELECT DISTINCT b.nam_bakhsh, h.nam_bakhsh AS bakhsh_id
        FROM tbl_hozor h
        JOIN tbl_bakhsh b ON h.nam_bakhsh = b.ID_nam_bakhsh
        WHERE h.nam_shift = %s
    """, params=(shift_id,), fetch_all=True)
    registered_count = len(registered) if registered else 0

    # ========== گزینه‌های بخش ==========
    dept_options = '<option value="">--- انتخاب بخش ---</option>'
    for d in departments:
        dept_options += f'<option value="{d["ID_nam_bakhsh"]}">{d["nam_bakhsh"]}</option>'

    # ========== گزینه‌های ریزشیفت (value = ID_onvan_shift، نمایش = shift_code) ==========
    shift_options = '<option value="">---</option>'
    for s in shift_list:
        shift_options += f'<option value="{s["ID_onvan_shift"]}">{s["shift_code"]}</option>'

    # ========== JSON داده‌ها ==========
    dept_data_json = _build_departments_json(departments, shift_id)

    # ========== آمار ==========
    present_count = query(
        "SELECT COUNT(*) as cnt FROM tbl_hozor WHERE nam_shift = %s AND ispresent = 1",
        params=(shift_id,), fetch_one=True
    )['cnt']
    absent_count = query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND ghaibat = 1",
        params=(shift_id,), fetch_one=True
    )['cnt']
    total_depts = len(departments)

    # ========== HTML ==========
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>حضور و غیاب</title>
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981; --danger: #ef4444;
        --warning: #f59e0b; --dark: #1e293b; --gray: #64748b; --light-gray: #94a3b8;
        --border: #e2e8f0; --bg-light: #f8fafc; --radius: 12px; --transition: 0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; background: #f1f5f9; color: var(--dark); }}
    .fade-in {{ animation: fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .content-card {{ max-width: 1400px; margin: 0 auto; }}

    .att-header {{
        background: linear-gradient(135deg, #0f766e, #14b8a6);
        color: white; padding: 25px 30px; border-radius: 16px;
        margin-bottom: 25px; display: flex; justify-content: space-between;
        align-items: center; box-shadow: 0 8px 30px rgba(15,118,110,0.25);
    }}
    .att-header h2 {{ font-size:22px; margin:0 0 5px 0; }}
    .att-header p {{ opacity:0.85; font-size:13px; margin:0; }}
    .shift-badge {{
        background: rgba(255,255,255,0.15); padding: 10px 20px;
        border-radius: 30px; font-size: 14px; font-weight: bold;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .back-btn {{
        color: white; text-decoration: none; padding: 8px 16px;
        border: 1px solid rgba(255,255,255,0.3); border-radius: 8px;
        font-size: 13px; transition: var(--transition);
    }}
    .back-btn:hover {{ background: rgba(255,255,255,0.15); }}

    .kpi-row {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;
    }}
    .kpi-card {{
        background: white; border-radius: 14px; padding: 20px; text-align: center;
        border: 1px solid var(--border); transition: var(--transition);
    }}
    .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }}
    .kpi-value {{ font-size: 28px; font-weight: bold; }}
    .kpi-label {{ font-size: 12px; color: var(--gray); margin-top: 4px; }}

    .main-grid {{
        display: grid; grid-template-columns: 260px 1fr; gap: 25px;
    }}

    .side-panel {{
        background: white; border-radius: 14px; padding: 20px;
        border: 1px solid var(--border);
    }}
    .side-title {{
        font-size: 15px; font-weight: bold; color: var(--dark);
        margin-bottom: 15px; padding-bottom: 12px;
        border-bottom: 2px solid var(--border);
        display: flex; align-items: center; gap: 8px;
    }}
    .side-count {{
        background: var(--primary); color: white; font-size: 11px;
        padding: 2px 10px; border-radius: 15px;
    }}
    .dept-item {{
        display: flex; align-items: center; gap: 10px;
        padding: 10px 12px; margin-bottom: 5px; border-radius: 8px;
        cursor: pointer; transition: var(--transition);
        font-size: 13px; border: 1px solid transparent;
    }}
    .dept-item:hover {{
        background: #dbeafe; border-color: var(--primary-light);
    }}
    .dept-badge {{
        margin-right: auto; background: #d1fae5; color: #065f46;
        font-size: 10px; padding: 2px 8px; border-radius: 10px;
    }}
    .empty-side {{
        text-align: center; color: var(--light-gray); font-size: 13px; padding: 20px;
    }}

    .form-panel {{
        background: white; border-radius: 14px; padding: 25px;
        border: 1px solid var(--border);
    }}
    .form-title {{
        font-size: 16px; font-weight: bold; color: var(--dark);
        margin-bottom: 20px; padding-bottom: 12px;
        border-bottom: 2px solid var(--border);
    }}
    .form-select {{
        width: 100%; padding: 12px 14px; border: 2px solid var(--border);
        border-radius: 10px; font-size: 14px; font-family: Tahoma;
        background: white; margin-bottom: 20px; transition: var(--transition);
    }}
    .form-select:focus {{ border-color: var(--primary-light); outline: none; }}

    .person-grid {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
        margin-bottom: 20px;
    }}
    .person-card {{
        background: var(--bg-light); border: 2px solid var(--border);
        border-radius: 10px; padding: 12px; cursor: pointer;
        transition: var(--transition); text-align: center;
        user-select: none;
    }}
    .person-card:hover {{ border-color: var(--primary-light); }}
    .person-card.selected {{
        border-color: var(--success); background: #d1fae5;
    }}
    .person-card .person-name {{
        font-size: 13px; font-weight: bold; color: var(--dark);
    }}
    .person-card .person-code {{
        font-size: 10px; color: var(--light-gray); margin-top: 3px;
    }}
    .person-card .person-shift {{
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px dashed var(--border);
    }}
    .person-card .person-shift select {{
        width: 100%;
        padding: 5px 8px;
        border: 1px solid var(--border);
        border-radius: 6px;
        font-size: 11px;
        font-family: Tahoma;
        background: white;
        transition: var(--transition);
    }}
    .person-card .person-shift select:focus {{
        border-color: var(--primary-light);
        outline: none;
    }}

    .btn {{
        display: inline-flex; align-items: center; justify-content: center; gap: 6px;
        padding: 12px 24px; border: none; border-radius: 10px;
        font-size: 14px; font-weight: 600; cursor: pointer;
        font-family: Tahoma; transition: var(--transition); text-decoration: none;
    }}
    .btn-primary {{
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        color: white; box-shadow: 0 4px 15px rgba(30,58,138,0.2);
    }}
    .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(30,58,138,0.3); }}
    .btn-secondary {{
        background: var(--bg-light); color: var(--gray); border: 2px solid var(--border);
    }}
    .btn-actions {{
        display: flex; gap: 10px; margin-top: 20px; padding-top: 20px;
        border-top: 1px solid var(--border);
    }}
    .btn-actions.hidden {{ display: none; }}

    .select-all-btn {{
        font-size: 12px; padding: 6px 12px; background: #dbeafe;
        color: var(--primary); border: none; border-radius: 6px;
        cursor: pointer; margin-bottom: 10px; font-family: Tahoma;
    }}

    .empty-personnel {{
        text-align: center; padding: 40px; color: var(--light-gray);
    }}

    .toast-container {{
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        z-index: 10000; display: flex; flex-direction: column-reverse; gap: 10px;
        pointer-events: none;
    }}
    .toast {{
        display: flex; align-items: center; gap: 12px;
        padding: 14px 22px; border-radius: 12px; color: white;
        font-size: 14px; font-weight: 600;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: slideUp 0.4s ease; pointer-events: auto;
    }}
    .toast.success {{ background: linear-gradient(135deg, #059669, #10b981); }}
    .toast.error {{ background: linear-gradient(135deg, #dc2626, #ef4444); }}
    .toast .toast-close {{
        margin-right: auto; cursor: pointer; opacity: 0.7; font-size: 16px;
    }}
    @keyframes slideUp {{
        from {{ opacity:0; transform:translateY(30px); }}
        to {{ opacity:1; transform:translateY(0); }}
    }}

    @media (max-width: 992px) {{
        .main-grid {{ grid-template-columns: 1fr; }}
        .person-grid {{ grid-template-columns: repeat(3, 1fr); }}
        .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 576px) {{
        .person-grid {{ grid-template-columns: repeat(2, 1fr); }}
        .att-header {{ flex-direction: column; gap: 15px; text-align: center; }}
    }}
</style>
</head>
<body>

<div class="toast-container" id="toast-container"></div>
<div class="content-card fade-in">

    <div class="att-header">
        <div>
            <h2>👥 سامانه هوشمند حضور و غیاب</h2>
            <p>ثبت وضعیت حضور پرسنل در شیفت جاری</p>
        </div>
        <div style="display:flex;align-items:center;gap:15px;">
            <span class="shift-badge">🕒 شیفت: {shift_name}</span>
            <a href="/module/supervisor" class="back-btn">⬅️ بازگشت</a>
        </div>
    </div>

    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-icon">🏥</div>
            <div class="kpi-value" style="color:#3b82f6;">{total_depts}</div>
            <div class="kpi-label">کل بخش‌ها</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">✅</div>
            <div class="kpi-value" style="color:#10b981;">{present_count}</div>
            <div class="kpi-label">حاضرین</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">❌</div>
            <div class="kpi-value" style="color:#ef4444;">{absent_count}</div>
            <div class="kpi-label">غایبین</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">📋</div>
            <div class="kpi-value" style="color:#0f766e;">{registered_count}</div>
            <div class="kpi-label">بخش ثبت شده</div>
        </div>
    </div>

    <div class="main-grid">

        <div class="side-panel">
            <div class="side-title">
                📁 بخش‌های ثبت شده
                <span class="side-count">{registered_count}</span>
            </div>
            {_build_registered_list_html(registered, shift_id)}
        </div>

        <div class="form-panel">
            <div class="form-title">🏥 ثبت حضور پرسنل</div>

            <form id="attendance-form">
                <input type="hidden" name="shift_id" value="{shift_id}">

                <select name="dept_id" id="dept-select" class="form-select" onchange="loadPersonnel()">
                    {dept_options}
                </select>

                <div id="personnel-container">
                    <div class="empty-personnel">
                        <div style="font-size:48px;">👥</div>
                        <p>لطفاً یک بخش را انتخاب کنید</p>
                    </div>
                </div>

                <div class="btn-actions hidden" id="btn-actions">
                    <button type="submit" class="btn btn-primary" id="save-btn">
                        <span id="save-text">💾 ثبت نهایی</span>
                        <span id="save-loading" style="display:none;">⏳ ...</span>
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="resetForm()">
                        ❌ انصراف
                    </button>
                </div>
            </form>
        </div>

    </div>

</div>

<script>
    var deptData = {dept_data_json};
    var allShiftOptions = `{shift_options}`;
    var defaultRizShiftId = "{default_rizshift_id or ''}";

    function showToast(msg, type) {{
        var c = document.getElementById('toast-container');
        var t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>';
        c.appendChild(t);
        setTimeout(function(){{ if(t.parentElement){{ t.style.opacity='0'; setTimeout(function(){{t.remove()}},300); }} }}, 4000);
    }}

    function loadPersonnel() {{
        var deptId = document.getElementById('dept-select').value;
        var container = document.getElementById('personnel-container');
        var actions = document.getElementById('btn-actions');

        if (!deptId || !deptData[deptId]) {{
            container.innerHTML = '<div class="empty-personnel"><div style="font-size:48px;">👥</div><p>لطفاً یک بخش را انتخاب کنید</p></div>';
            actions.classList.add('hidden');
            return;
        }}

        var personnel = deptData[deptId].personnel || [];
        var presentIds = deptData[deptId].present_ids || [];
        var rizShifts = deptData[deptId].riz_shifts || {{}};

        if (personnel.length === 0) {{
            container.innerHTML = '<div class="empty-personnel"><p>پرسنلی در این بخش یافت نشد</p></div>';
            actions.classList.add('hidden');
            return;
        }}

        var html = '<button type="button" class="select-all-btn" onclick="selectAll()">✅ انتخاب همه</button>';
        html += '<button type="button" class="select-all-btn" style="margin-right:5px;" onclick="deselectAll()">❌ حذف همه</button>';
        html += '<div class="person-grid">';

        personnel.forEach(function(p) {{
            var isChecked = presentIds.indexOf(parseInt(p.ID_person)) !== -1;
            html += '<div class="person-card' + (isChecked ? ' selected' : '') + '" onclick="togglePerson(this, ' + p.ID_person + ')" data-id="' + p.ID_person + '">';
            html += '<div class="person-name">' + p.nam + ' ' + p.famil + '</div>';
            html += '<div class="person-code">' + (p.kod_meli || '') + '</div>';
            html += '<div class="person-shift" onclick="event.stopPropagation();">';
            html += '<select name="rizshift_' + p.ID_person + '" class="rizshift-select" data-person-id="' + p.ID_person + '">';
            html += allShiftOptions;
            html += '</select>';
            html += '</div>';
            html += '<input type="hidden" name="person_' + p.ID_person + '" value="' + (isChecked ? '1' : '0') + '" id="input-' + p.ID_person + '">';
            html += '</div>';
        }});

        html += '</div>';
        container.innerHTML = html;

        // تنظیم مقادیر پیش‌فرض ریزشیفت
        personnel.forEach(function(p) {{
            var sel = document.querySelector('select[name="rizshift_' + p.ID_person + '"]');
            if (sel) {{
                sel.value = rizShifts[p.ID_person] || defaultRizShiftId;
            }}
        }});

        actions.classList.remove('hidden');
    }}

    function togglePerson(card, personId) {{
        card.classList.toggle('selected');
        var input = document.getElementById('input-' + personId);
        if (card.classList.contains('selected')) {{
            input.value = '1';
        }} else {{
            input.value = '0';
        }}
    }}

    function selectAll() {{
        document.querySelectorAll('.person-card').forEach(function(c) {{
            if (!c.classList.contains('selected')) {{
                c.classList.add('selected');
                var id = c.getAttribute('data-id');
                document.getElementById('input-' + id).value = '1';
            }}
        }});
    }}

    function deselectAll() {{
        document.querySelectorAll('.person-card').forEach(function(c) {{
            c.classList.remove('selected');
            var id = c.getAttribute('data-id');
            document.getElementById('input-' + id).value = '0';
        }});
    }}

    document.getElementById('attendance-form').addEventListener('submit', function(e) {{
        e.preventDefault();

        var deptId = document.getElementById('dept-select').value;
        if (!deptId) {{ showToast('بخش را انتخاب کنید', 'error'); return; }}

        var formData = new FormData(this);

        document.getElementById('save-text').style.display = 'none';
        document.getElementById('save-loading').style.display = 'inline';

        fetch('/module/supervisor/attendance/save', {{ method:'POST', body:formData }})
        .then(r => r.json())
        .then(data => {{
            document.getElementById('save-text').style.display = 'inline';
            document.getElementById('save-loading').style.display = 'none';

            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                if (data.present_ids) {{
                    deptData[deptId].present_ids = data.present_ids;
                    deptData[deptId].riz_shifts = data.riz_shifts || {{}};
                }}
                setTimeout(function() {{ location.reload(); }}, 1200);
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }})
        .catch(function() {{
            document.getElementById('save-text').style.display = 'inline';
            document.getElementById('save-loading').style.display = 'none';
            showToast('خطا در ارتباط', 'error');
        }});
    }});

    function resetForm() {{
        document.getElementById('dept-select').value = '';
        loadPersonnel();
    }}
</script>
</body>
</html>'''

    return html


def _build_departments_json(departments, shift_id):
    """ساخت JSON بخش‌ها با پرسنل، وضعیت حضور و ریزشیفت (ID_onvan_shift)"""
    data = {}
    for dept in departments:
        dept_id = dept['ID_nam_bakhsh']

        personnel = query("""
            SELECT p.ID_person, p.nam, p.famil, p.kod_meli
            FROM tbl_person p
            JOIN tbl_sazema_person s ON p.ID_person = s.nam_person
            WHERE s.nam_bakhsh = %s AND p.isActiv = 1
            AND (s.payani_sazmandehi = 0 OR s.payani_sazmandehi IS NULL)
            ORDER BY p.famil, p.nam
        """, params=(dept_id,), fetch_all=True)

        present_rows = query("""
            SELECT id_person, rizshift
            FROM tbl_hozor
            WHERE nam_shift = %s AND nam_bakhsh = %s AND ispresent = 1
        """, params=(shift_id, dept_id), fetch_all=True)

        present_ids = [p['id_person'] for p in present_rows] if present_rows else []
        riz_shifts = {}
        for row in (present_rows or []):
            val = row['rizshift']
            if val is not None and val != '':
                riz_shifts[str(row['id_person'])] = str(val)

        data[str(dept_id)] = {
            'name': dept['nam_bakhsh'],
            'personnel': personnel if personnel else [],
            'present_ids': present_ids,
            'riz_shifts': riz_shifts
        }

    return json.dumps(data, ensure_ascii=False)


def _build_registered_list_html(registered, shift_id):
    if not registered:
        return '<div class="empty-side">هنوز بخشی ثبت نشده</div>'

    html = ''
    for r in registered:
        html += f'''
        <div class="dept-item" onclick="document.getElementById('dept-select').value='{r["bakhsh_id"]}';loadPersonnel();">
            <span>📝</span>
            <span>{r["nam_bakhsh"]}</span>
            <span class="dept-badge">ثبت شده</span>
        </div>
        '''
    return html


def save_attendance(user, form_data):
    """ذخیره وضعیت حضور پرسنل با ریزشیفت ID_onvan_shift"""

    _ensure_rizshift_int()

    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id', '')
    dept_id = form_data.get('dept_id', '')

    if not dept_id:
        return {'success': False, 'message': 'بخش انتخاب نشده'}

    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    present_ids = []
    riz_shift_dict = {}

    try:
        # حذف رکوردهای قبلی این بخش در این شیفت
        query(
            "DELETE FROM tbl_hozor WHERE nam_shift = %s AND nam_bakhsh = %s",
            params=(shift_id, dept_id),
            commit=True
        )

        # ثبت جدید
        for key, value in form_data.items():
            if key.startswith('person_'):
                person_id = key.replace('person_', '')
                is_present = int(value) if value else 0

                rizshift = form_data.get(f'rizshift_{person_id}')
                rizshift = int(rizshift) if rizshift and rizshift.isdigit() else None

                query("""
                    INSERT INTO tbl_hozor (id_person, ispresent, nam_bakhsh, nam_shift, rizshift, dat_sabt, zaman_sabt, UserID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, params=(person_id, is_present, dept_id, shift_id, rizshift, today, now, user_id), commit=True)

                if is_present == 1:
                    present_ids.append(int(person_id))
                if rizshift is not None:
                    riz_shift_dict[str(person_id)] = rizshift

        dept_info = query(
            "SELECT nam_bakhsh FROM tbl_bakhsh WHERE ID_nam_bakhsh = %s",
            params=(dept_id,), fetch_one=True
        )
        dept_name = dept_info['nam_bakhsh'] if dept_info else ''

        log_crud('save_attendance', user_id, key_value=dept_id,
                 new_value=f"شیفت:{shift_id}, بخش:{dept_id}, تعداد حاضر:{len(present_ids)}")

        return {
            'success': True,
            'message': f'حضور پرسنل بخش {dept_name} ثبت شد',
            'present_ids': present_ids,
            'riz_shifts': riz_shift_dict
        }

    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}
        
        