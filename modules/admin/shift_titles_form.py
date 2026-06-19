"""
مدیریت عناوین شیفت – ادمین (نسخه کامل با مدت‌زمان)
ثبت، ویرایش و حذف عناوین شیفت با قابلیت محاسبه و ذخیره مدت‌زمان
پشتیبانی از شیفت‌های طولانی (>۲۴ ساعت)
"""

from models.database import query
import json
from utils.auto_log import log_crud
from datetime import timedelta

# ------------------------------------------------------------
#  اطمینان از وجود ستون time_duration (TIME) در جدول
# ------------------------------------------------------------
def _ensure_time_duration_column():
    try:
        col = query("SHOW COLUMNS FROM onvan_shift LIKE 'time_duration'", fetch_one=True)
        if not col:
            query("ALTER TABLE onvan_shift ADD COLUMN time_duration TIME DEFAULT NULL", commit=True)
    except Exception:
        pass

# ------------------------------------------------------------
#  تبدیل مقادیر TIME / timedelta به رشته HH:MM
# ------------------------------------------------------------
def _format_timedelta(val):
    if val is None:
        return ''
    if isinstance(val, timedelta):
        total_seconds = int(val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    s = str(val).strip()
    if s:
        if s.count(':') == 2:
            s = s[:5]          # HH:MM
        return s
    return ''


# ------------------------------------------------------------
#  صفحه HTML
# ------------------------------------------------------------
def get_shift_titles_form(user):
    _ensure_time_duration_column()

    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>مدیریت عناوین شیفت</title>
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
        --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
        --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
        --bg: #f1f5f9; --white: #fff; --radius: 12px; --transition: 0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:1200px; margin:0 auto; padding:20px; }}

    .shift-header {{
        background: linear-gradient(135deg, #0f766e, #14b8a6);
        color:white; border-radius:16px; padding:25px 30px; margin-bottom:25px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(15,118,110,0.25);
    }}
    .shift-header h2 {{ font-size:24px; margin:0; }}
    .shift-header p {{ opacity:0.85; font-size:13px; margin:5px 0 0 0; }}
    .back-btn {{
        color:white; text-decoration:none; padding:8px 16px;
        border:1px solid rgba(255,255,255,0.4); border-radius:8px;
        font-size:13px; transition:var(--transition);
    }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    .card {{
        background:var(--white); border-radius:var(--radius); padding:25px;
        border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05);
        margin-bottom:25px;
    }}
    .card-header {{
        font-size:18px; font-weight:bold; color:var(--dark);
        margin-bottom:20px; padding-bottom:15px;
        border-bottom:2px solid var(--border);
        display:flex; align-items:center; gap:8px;
    }}
    .card-header .badge {{
        background:var(--primary); color:white; font-size:12px;
        padding:4px 12px; border-radius:15px; font-weight:normal;
        margin-right:auto;
    }}

    .add-form {{
        display:flex; gap:10px; align-items:flex-end; flex-wrap:wrap;
    }}
    .add-form .form-group {{
        flex:1; min-width:100px;
    }}
    .add-form .form-group:last-child {{
        flex:0 0 auto;
    }}
    .form-group {{ margin-bottom:0; }}
    .form-group label {{ display:block; font-size:12px; font-weight:600; color:var(--gray); margin-bottom:4px; }}
    .form-input, .form-select {{
        width:100%; padding:10px 12px; border:2px solid var(--border);
        border-radius:8px; font-size:14px; font-family:inherit;
        transition:var(--transition); background:var(--white);
    }}
    .form-input:focus, .form-select:focus {{
        border-color:var(--primary-light); outline:none;
        box-shadow:0 0 0 3px rgba(59,130,246,0.15);
    }}
    .form-input.error {{ border-color:var(--danger); background:#fef2f2; }}

    .btn {{
        display:inline-flex; align-items:center; justify-content:center; gap:6px;
        padding:10px 18px; border:none; border-radius:8px; font-size:14px;
        font-weight:600; cursor:pointer; font-family:inherit;
        transition:var(--transition); text-decoration:none; white-space:nowrap;
    }}
    .btn-primary {{ background:var(--primary); color:white; }}
    .btn-primary:hover {{ background:var(--primary-light); transform:translateY(-1px); box-shadow:0 4px 12px rgba(30,58,138,0.3); }}
    .btn-outline {{ background:white; color:var(--primary); border:2px solid var(--primary); }}
    .btn-outline:hover {{ background:var(--primary); color:white; }}
    .btn-success {{ background:var(--success); color:white; }}
    .btn-success:hover {{ background:#059669; }}
    .btn-danger {{ background:var(--danger); color:white; }}
    .btn-danger:hover {{ background:#dc2626; }}
    .btn-xs {{ padding:6px 12px; font-size:12px; border-radius:6px; }}

    .shift-list {{ display:flex; flex-direction:column; gap:8px; }}
    .shift-row {{
        display:flex; align-items:center; gap:10px; padding:12px 16px;
        background:var(--bg); border:1px solid var(--border);
        border-right:5px solid var(--primary); border-radius:10px;
        transition:var(--transition); flex-wrap:wrap;
    }}
    .shift-row:hover {{
        border-color:var(--primary-light); box-shadow:0 2px 8px rgba(0,0,0,0.05);
        transform:translateX(-2px);
    }}
    .shift-row.editing {{
        border-color:var(--warning); border-right-color:var(--warning);
        background:#fffbeb; box-shadow:0 0 0 3px rgba(245,158,11,0.15);
    }}
    .shift-row .shift-id {{
        font-family:monospace; font-size:12px; color:var(--light-gray);
        background:var(--white); padding:4px 10px; border-radius:6px;
        min-width:60px; text-align:center;
    }}
    .shift-row .field {{
        display:flex; flex-direction:column; min-width:90px;
    }}
    .shift-row .field label {{
        font-size:10px; color:var(--gray); margin-bottom:2px;
    }}
    .shift-row .field span {{
        font-size:13px; font-weight:500;
    }}
    .shift-row input, .shift-row select {{
        padding:6px 8px; border:2px solid var(--border);
        border-radius:6px; font-size:13px; font-family:inherit;
        background:var(--white);
    }}
    .shift-row input:focus, .shift-row select:focus {{
        border-color:var(--warning); outline:none;
    }}
    .shift-row .color-box {{
        width:28px; height:28px; border-radius:6px; border:1px solid var(--border);
        background-color: var(--color);
    }}

    .shift-actions {{ display:flex; gap:6px; margin-right:auto; }}

    .toast-container {{
        position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000;
        display:flex; flex-direction:column; gap:10px; pointer-events:none;
    }}
    .toast {{
        display:flex; align-items:center; gap:12px; padding:14px 22px;
        border-radius:12px; color:white; font-size:14px; font-weight:600;
        box-shadow:0 10px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease;
        pointer-events:auto;
    }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }}
    .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    .toast .toast-close {{ margin-right:auto; cursor:pointer; opacity:0.7; font-size:16px; }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .empty-state {{ text-align:center; padding:50px 20px; color:var(--light-gray); }}
    .empty-state .icon {{ font-size:48px; margin-bottom:15px; }}

    @media (max-width:768px) {{
        .shift-header {{ flex-direction:column; gap:15px; text-align:center; }}
        .add-form {{ flex-direction:column; }}
        .shift-row {{ flex-direction:column; align-items:flex-start; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="shift-header">
        <div>
            <h2>⏳ مدیریت عناوین شیفت</h2>
            <p>تعریف و ویرایش عناوین اصلی شیفت‌ها (کد، زمان و رنگ)</p>
        </div>
        <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
    </div>

    <!-- فرم افزودن -->
    <div class="card">
        <div class="card-header">
            <span>➕</span> ثبت عنوان جدید
        </div>
        <div class="add-form">
            <div class="form-group">
                <label>کد شیفت *</label>
                <input type="text" id="new-shift-code" class="form-input" placeholder="مثلاً M" maxlength="50" required>
            </div>
            <div class="form-group">
                <label>عنوان شیفت *</label>
                <input type="text" id="new-shift-name" class="form-input" placeholder="مثلاً صبح" required>
            </div>
            <div class="form-group">
                <label>شروع</label>
                <input type="time" id="new-start-time" class="form-input" value="08:00" required onchange="autoCalcDuration('new-')">
            </div>
            <div class="form-group">
                <label>پایان</label>
                <input type="time" id="new-end-time" class="form-input" value="16:00" required onchange="autoCalcDuration('new-')">
            </div>
            <div class="form-group" style="min-width:110px;">
                <label>مدت (ساعت:دقیقه)</label>
                <input type="text" id="new-duration" class="form-input" value="08:00" 
                       pattern="\\d{{1,3}}:\\d{{2}}" placeholder="مثل 29:30" required
                       title="مثال: 08:00 یا 29:30">
                <small style="color:var(--gray);font-size:10px;">محاسبه خودکار / قابل ویرایش</small>
            </div>
            <div class="form-group" style="max-width:90px;">
                <label>رنگ</label>
                <input type="color" id="new-color-code" class="form-input" value="#3b82f6" style="padding:4px; height:38px;">
            </div>
            <div class="form-group">
                <label>&nbsp;</label>
                <button class="btn btn-primary" onclick="addShift()">
                    <span id="add-text">➕ ثبت</span>
                </button>
            </div>
        </div>
    </div>

    <!-- لیست شیفت‌ها -->
    <div class="card">
        <div class="card-header">
            <span>📋</span> عناوین تعریف شده
            <span class="badge" id="shift-count">۰ عنوان</span>
        </div>
        <div class="shift-list" id="shift-list">
            <div class="empty-state">
                <div class="icon">📭</div>
                <p>در حال بارگذاری...</p>
            </div>
        </div>
    </div>
</div>

<script>
    let editingShiftId = null;

    function showToast(msg, type) {{
        const c = document.getElementById('toast-container');
        const t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = `<span>${{type==='success'?'✅':'❌'}}</span><span>${{msg}}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    function formatTime(t) {{
        if (!t) return '';
        if (t.length >= 5) return t.substring(0,5);
        return t;
    }}

    // محاسبه مدت‌زمان (خروجی H:MM)
    function calcDuration(start, end) {{
        if (!start || !end) return null;
        const [sh, sm] = start.split(':').map(Number);
        const [eh, em] = end.split(':').map(Number);
        let startMin = sh * 60 + sm;
        let endMin = eh * 60 + em;
        if (endMin <= startMin) endMin += 24 * 60;   // عبور از نیمه‌شب
        const diffMin = endMin - startMin;
        const h = Math.floor(diffMin / 60);
        const m = diffMin % 60;
        return `${{h}}:${{String(m).padStart(2, '0')}}`;
    }}

    function autoCalcDuration(prefix) {{
        const startEl = document.getElementById(prefix + 'start-time');
        const endEl = document.getElementById(prefix + 'end-time');
        const durEl = document.getElementById(prefix + 'duration');
        if (!startEl || !endEl || !durEl) return;
        const start = startEl.value;
        const end = endEl.value;
        if (start && end) {{
            const dur = calcDuration(start, end);
            if (dur) durEl.value = dur;
        }}
    }}

    async function loadShifts() {{
        try {{
            const res = await fetch('/module/admin/shifts/list');
            const data = await res.json();
            const list = document.getElementById('shift-list');
            document.getElementById('shift-count').textContent = `${{data.shifts.length}} عنوان`;

            if (!data.shifts.length) {{
                list.innerHTML = '<div class="empty-state"><div class="icon">📭</div><p>هنوز عنوانی تعریف نشده است</p></div>';
                return;
            }}

            let html = '';
            data.shifts.forEach(shift => {{
                const isEditing = editingShiftId == shift.ID_onvan_shift;
                const dur = formatTime(shift.time_duration);
                html += `<div class="shift-row ${{isEditing ? 'editing' : ''}}" id="shift-row-${{shift.ID_onvan_shift}}">
                    <span class="shift-id">#${{shift.ID_onvan_shift}}</span>
                    ${{isEditing ? `
                        <input type="text" id="edit-code-${{shift.ID_onvan_shift}}" value="${{shift.shift_code || ''}}" placeholder="کد" style="width:80px;">
                        <input type="text" id="edit-name-${{shift.ID_onvan_shift}}" value="${{shift.nam_shift.replace(/"/g, '&quot;')}}" placeholder="نام" style="width:120px;">
                        <input type="time" id="edit-start-${{shift.ID_onvan_shift}}" value="${{formatTime(shift.start_time)}}" style="width:110px;" onchange="autoCalcDuration('edit-', '${{shift.ID_onvan_shift}}')">
                        <input type="time" id="edit-end-${{shift.ID_onvan_shift}}" value="${{formatTime(shift.end_time)}}" style="width:110px;" onchange="autoCalcDuration('edit-', '${{shift.ID_onvan_shift}}')">
                        <input type="text" id="edit-duration-${{shift.ID_onvan_shift}}" value="${{dur}}" 
                               pattern="\\d{{1,3}}:\\d{{2}}" style="width:110px;">
                        <input type="color" id="edit-color-${{shift.ID_onvan_shift}}" value="${{shift.color_code || '#3b82f6'}}" style="width:50px; height:32px;">
                    ` : `
                        <div class="field"><label>کد</label><span>${{shift.shift_code || '-'}}</span></div>
                        <div class="field"><label>نام</label><span>${{shift.nam_shift}}</span></div>
                        <div class="field"><label>شروع</label><span>${{formatTime(shift.start_time)}}</span></div>
                        <div class="field"><label>پایان</label><span>${{formatTime(shift.end_time)}}</span></div>
                        <div class="field"><label>مدت</label><span>${{dur || '—'}}</span></div>
                        <div class="field"><label>رنگ</label><div class="color-box" style="background-color:${{shift.color_code || '#3b82f6'}}"></div></div>
                    `}}
                    <div class="shift-actions">
                        ${{isEditing ? `
                            <button class="btn btn-success btn-xs" onclick="saveShift(${{shift.ID_onvan_shift}})">💾 ذخیره</button>
                            <button class="btn btn-outline btn-xs" onclick="cancelEdit()">❌ انصراف</button>
                        ` : `
                            <button class="btn btn-outline btn-xs" onclick="startEdit(${{shift.ID_onvan_shift}})">📝 ویرایش</button>
                            <button class="btn btn-danger btn-xs" onclick="deleteShift(${{shift.ID_onvan_shift}})">🗑️ حذف</button>
                        `}}
                    </div>
                </div>`;
            }});
            list.innerHTML = html;
        }} catch(e) {{ console.error(e); }}
    }}

    async function addShift() {{
        const code = document.getElementById('new-shift-code').value.trim();
        const name = document.getElementById('new-shift-name').value.trim();
        const start = document.getElementById('new-start-time').value;
        const end = document.getElementById('new-end-time').value;
        const duration = document.getElementById('new-duration').value.trim();
        const color = document.getElementById('new-color-code').value;

        if (!code || !name) {{
            showToast('⛔ کد و نام شیفت الزامی است', 'error');
            return;
        }}
        if (!start || !end || !duration) {{
            showToast('⛔ شروع، پایان و مدت الزامی است', 'error');
            return;
        }}
        if (!/^\\d{{1,3}}:\\d{{2}}$/.test(duration)) {{
            showToast('⛔ فرمت مدت نامعتبر است (مثل 08:00 یا 29:30)', 'error');
            return;
        }}

        const formData = new FormData();
        formData.append('shift_code', code);
        formData.append('shift_name', name);
        formData.append('start_time', start);
        formData.append('end_time', end);
        formData.append('time_duration', duration);
        formData.append('color_code', color);

        try {{
            const res = await fetch('/module/admin/shifts/save', {{ method:'POST', body:formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                document.getElementById('new-shift-code').value = '';
                document.getElementById('new-shift-name').value = '';
                document.getElementById('new-start-time').value = '08:00';
                document.getElementById('new-end-time').value = '16:00';
                document.getElementById('new-duration').value = '08:00';
                document.getElementById('new-color-code').value = '#3b82f6';
                loadShifts();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{ showToast('خطا در ارتباط', 'error'); }}
    }}

    function startEdit(id) {{
        if (editingShiftId && editingShiftId != id) cancelEdit();
        editingShiftId = id;
        loadShifts();
    }}

    function cancelEdit() {{
        editingShiftId = null;
        loadShifts();
    }}

    async function saveShift(id) {{
        const code = document.getElementById('edit-code-' + id).value.trim();
        const name = document.getElementById('edit-name-' + id).value.trim();
        const start = document.getElementById('edit-start-' + id).value;
        const end = document.getElementById('edit-end-' + id).value;
        const duration = document.getElementById('edit-duration-' + id).value.trim();
        const color = document.getElementById('edit-color-' + id).value;

        if (!code || !name) {{
            showToast('کد و نام نمی‌تواند خالی باشد', 'error');
            return;
        }}
        if (!start || !end || !duration) {{
            showToast('شروع، پایان و مدت الزامی است', 'error');
            return;
        }}
        if (!/^\\d{{1,3}}:\\d{{2}}$/.test(duration)) {{
            showToast('⛔ فرمت مدت نامعتبر است', 'error');
            return;
        }}

        const formData = new FormData();
        formData.append('shift_id', id);
        formData.append('shift_code', code);
        formData.append('shift_name', name);
        formData.append('start_time', start);
        formData.append('end_time', end);
        formData.append('time_duration', duration);
        formData.append('color_code', color);

        try {{
            const res = await fetch('/module/admin/shifts/update', {{ method:'POST', body:formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                editingShiftId = null;
                loadShifts();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    async function deleteShift(id) {{
        if (!confirm('آیا از حذف این عنوان اطمینان دارید؟')) return;
        const formData = new FormData();
        formData.append('shift_id', id);
        try {{
            const res = await fetch('/module/admin/shifts/delete', {{ method:'POST', body:formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                if (editingShiftId == id) editingShiftId = null;
                loadShifts();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    document.addEventListener('DOMContentLoaded', () => {{
        autoCalcDuration('new-');
        loadShifts();
    }});
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions
# ==========================================
def get_shifts_list():
    _ensure_time_duration_column()
    try:
        shifts = query("""
            SELECT ID_onvan_shift, nam_shift, shift_code,
                   start_time, end_time, color_code, time_duration
            FROM onvan_shift
            ORDER BY ID_onvan_shift DESC
        """, fetch_all=True) or []

        for s in shifts:
            s['start_time'] = _format_timedelta(s.get('start_time'))
            s['end_time'] = _format_timedelta(s.get('end_time'))
            s['time_duration'] = _format_timedelta(s.get('time_duration'))

        return {'success': True, 'shifts': shifts}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def save_shift(user, form_data):
    _ensure_time_duration_column()
    user_id = user.get('UserID', 0)
    code = form_data.get('shift_code', '').strip()
    name = form_data.get('shift_name', '').strip()
    start = form_data.get('start_time', '').strip()
    end = form_data.get('end_time', '').strip()
    duration = form_data.get('time_duration', '').strip()
    color = form_data.get('color_code', '').strip() or '#3b82f6'

    if not code or not name:
        return {'success': False, 'message': 'کد و نام شیفت الزامی است'}
    if not start or not end or not duration:
        return {'success': False, 'message': 'شروع، پایان و مدت الزامی است'}

    if query("SELECT ID_onvan_shift FROM onvan_shift WHERE shift_code=%s OR nam_shift=%s",
             (code, name), fetch_one=True):
        return {'success': False, 'message': 'کد یا نام شیفت تکراری است'}

    try:
        query("""
            INSERT INTO onvan_shift (nam_shift, shift_code, start_time, end_time, color_code, time_duration)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, code, start, end, color, duration), commit=True)

        new_id = query("SELECT MAX(ID_onvan_shift) as max_id FROM onvan_shift", fetch_one=True)['max_id']
        log_crud('save_shift_title', user_id, key_value=new_id,
                 new_value=json.dumps({"code": code, "name": name, "start": start,
                                       "end": end, "duration": duration, "color": color},
                                      ensure_ascii=False))
        return {'success': True, 'message': f'شیفت "{name}" با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def update_shift(user, form_data):
    _ensure_time_duration_column()
    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id')
    code = form_data.get('shift_code', '').strip()
    name = form_data.get('shift_name', '').strip()
    start = form_data.get('start_time', '').strip()
    end = form_data.get('end_time', '').strip()
    duration = form_data.get('time_duration', '').strip()
    color = form_data.get('color_code', '').strip() or '#3b82f6'

    if not shift_id:
        return {'success': False, 'message': 'شناسه شیفت نامعتبر است'}
    if not code or not name:
        return {'success': False, 'message': 'کد و نام الزامی است'}
    if not start or not end or not duration:
        return {'success': False, 'message': 'شروع، پایان و مدت الزامی است'}

    if query("""
        SELECT ID_onvan_shift FROM onvan_shift
        WHERE (shift_code=%s OR nam_shift=%s) AND ID_onvan_shift != %s
    """, (code, name, shift_id), fetch_one=True):
        return {'success': False, 'message': 'کد یا نام تکراری است'}

    old = query("SELECT * FROM onvan_shift WHERE ID_onvan_shift=%s", (shift_id,), fetch_one=True)
    if not old:
        return {'success': False, 'message': 'رکورد یافت نشد'}

    try:
        query("""
            UPDATE onvan_shift
            SET nam_shift=%s, shift_code=%s, start_time=%s, end_time=%s,
                color_code=%s, time_duration=%s
            WHERE ID_onvan_shift=%s
        """, (name, code, start, end, color, duration, shift_id), commit=True)

        log_crud('update_shift_title', user_id, key_value=shift_id,
                 old_value=json.dumps(old, ensure_ascii=False, default=str),
                 new_value=json.dumps({"code": code, "name": name, "start": start,
                                       "end": end, "duration": duration, "color": color},
                                      ensure_ascii=False))
        return {'success': True, 'message': 'تغییرات با موفقیت اعمال شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def delete_shift(user, form_data):
    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id')
    if not shift_id:
        return {'success': False, 'message': 'شناسه شیفت نامعتبر است'}

    used = query("SELECT COUNT(*) as cnt FROM shift_namt WHERE nam_shift=%s", (shift_id,), fetch_one=True)
    if used and used['cnt'] > 0:
        return {'success': False, 'message': 'این عنوان در شیفت‌های ثبت شده استفاده شده و قابل حذف نیست'}

    old = query("SELECT * FROM onvan_shift WHERE ID_onvan_shift=%s", (shift_id,), fetch_one=True)
    if not old:
        return {'success': False, 'message': 'رکورد یافت نشد'}

    try:
        query("DELETE FROM onvan_shift WHERE ID_onvan_shift=%s", (shift_id,), commit=True)
        log_crud('delete_shift_title', user_id, key_value=shift_id,
                 old_value=json.dumps(old, ensure_ascii=False, default=str))
        return {'success': True, 'message': 'عنوان با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}
        
        