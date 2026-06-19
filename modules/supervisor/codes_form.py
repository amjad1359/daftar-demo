"""
فرم کدهای عملیاتی بیمارمحور - سوپروایزر
نسخه بهینه‌شده با چینش فشرده و ماسک زمان
"""

import jdatetime
from datetime import datetime
from models.database import query, get_connection
import json
from utils.auto_log import log_crud

def get_codes_form(user):
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    shift = query(
        "SELECT ID_shift, tarkib FROM shift_namt ORDER BY ID_shift DESC LIMIT 1",
        fetch_one=True
    )
    if not shift:
        return '''<div class="content-card fade-in" style="text-align:center;padding:60px;">
            <h3>⚠️ شیفت فعالی یافت نشد</h3>
            <a href="/module/supervisor/shift" class="btn btn-primary">📅 ثبت شیفت</a></div>'''

    shift_id = shift['ID_shift']
    shift_name = shift['tarkib']

    # لیست بخش‌ها
    departments = query("SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh", fetch_all=True) or []
    dept_options = '<option value="">--- انتخاب بخش ---</option>'
    for d in departments:
        dept_options += f'<option value="{d["ID_nam_bakhsh"]}">{d["nam_bakhsh"]}</option>'

    # لیست انواع کد
    codes = query("SELECT ID_onvan_kod, nam_kod FROM tbl_onvan_kod ORDER BY nam_kod", fetch_all=True) or []
    code_options = '<option value="">--- انتخاب نوع کد ---</option>'
    for c in codes:
        code_options += f'<option value="{c["ID_onvan_kod"]}">{c["nam_kod"]}</option>'

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --primary:#1e3a8a; --primary-light:#3b82f6; --success:#10b981;
        --danger:#ef4444; --warning:#f59e0b; --dark:#1e293b;
        --gray:#64748b; --light-gray:#94a3b8; --border:#e2e8f0;
        --bg:#f1f5f9; --white:#fff; --radius:12px; --transition:0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'Segoe UI',Tahoma,sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0;transform:translateY(10px); }} to {{ opacity:1;transform:translateY(0); }} }}

    .container {{ max-width:1400px; margin:0 auto; padding:20px; }}

    /* ========== هدر ========== */
    .page-header {{
        background:linear-gradient(135deg, #0f766e, #14b8a6); color:white; border-radius:16px;
        padding:22px 28px; margin-bottom:22px; display:flex; justify-content:space-between;
        align-items:center; box-shadow:0 8px 30px rgba(15,118,110,0.25);
    }}
    .page-header-left h2 {{ font-size:22px; margin:0 0 5px 0; }}
    .page-header-left p {{ opacity:0.85; font-size:13px; margin:0; }}
    .page-header-right {{ display:flex; align-items:center; gap:15px; }}
    .shift-badge {{
        background:rgba(255,255,255,0.15); padding:8px 18px; border-radius:25px;
        font-size:13px; font-weight:bold; border:1px solid rgba(255,255,255,0.2);
    }}
    .back-btn {{
        color:white; text-decoration:none; padding:8px 16px;
        border:1px solid rgba(255,255,255,0.4); border-radius:8px;
        font-size:13px; transition:var(--transition);
    }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    .tabs {{ display:flex; gap:5px; margin-bottom:20px; border-bottom:2px solid var(--border); }}
    .tab {{ padding:10px 22px; font-size:13px; font-weight:600; border:none; background:none; color:var(--light-gray); cursor:pointer; border-bottom:2px solid transparent; transition:var(--transition); font-family:inherit; }}
    .tab:hover {{ color:var(--dark); }}
    .tab.active {{ color:var(--primary); border-bottom-color:var(--primary); }}
    .tab-content {{ display:none; }}
    .tab-content.active {{ display:block; animation:fadeIn 0.3s ease; }}

    .card {{ background:var(--white); border-radius:var(--radius); padding:22px; border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:20px; }}
    .card-title {{ font-size:15px; font-weight:bold; color:var(--dark); margin-bottom:16px; padding-bottom:10px; border-bottom:2px solid var(--border); display:flex; align-items:center; gap:8px; }}

    .form-group {{ margin-bottom:14px; }}
    .form-group label {{ display:block; font-size:12px; font-weight:600; color:var(--gray); margin-bottom:5px; }}
    .form-select, .form-input, .form-textarea {{
        width:100%; padding:10px 12px; border:2px solid var(--border); border-radius:8px;
        font-size:13px; font-family:inherit; transition:var(--transition); background:var(--white);
    }}
    .form-select:focus, .form-input:focus, .form-textarea:focus {{
        border-color:var(--primary-light); outline:none; box-shadow:0 0 0 3px rgba(59,130,246,0.15);
    }}
    .form-textarea {{ min-height:70px; resize:vertical; }}

    /* ========== ماسک زمان ========== */
    .time-input {{
        text-align:center; direction:ltr; letter-spacing:1px;
        font-family:'Courier New', monospace; font-size:14px; font-weight:bold;
    }}
    .time-input:focus {{ border-color:var(--primary-light); }}
    .time-input.invalid {{ border-color:var(--danger); background:#fef2f2; }}

    .row {{ display:flex; gap:8px; align-items:flex-end; flex-wrap:wrap; }}

    .btn {{
        display:inline-flex; align-items:center; justify-content:center; gap:5px;
        padding:10px 18px; border:none; border-radius:8px; font-size:13px; font-weight:600;
        cursor:pointer; font-family:inherit; transition:var(--transition); text-decoration:none;
    }}
    .btn-primary {{ background:var(--primary); color:white; }} .btn-primary:hover {{ background:var(--primary-light); }}
    .btn-success {{ background:var(--success); color:white; }} .btn-danger {{ background:var(--danger); color:white; }}
    .btn-warning {{ background:var(--warning); color:white; }} .btn-sm {{ padding:6px 12px; font-size:11px; }}
    .btn-block {{ width:100%; }}
    .btn:disabled {{ opacity:0.6; cursor:not-allowed; }}

    .team-role-row {{
        display:flex; align-items:center; gap:8px; background:var(--bg);
        border:1px solid var(--border); padding:10px; border-radius:8px; margin-bottom:6px;
    }}
    .team-role-row .role-name {{ flex:1; font-weight:bold; font-size:13px; }}
    .team-role-row select {{ flex:2; }}
    .team-role-row input {{ flex:2; }}

    .record-item {{
        background:var(--white); border:1px solid var(--border); border-radius:10px; padding:14px;
        margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;
    }}
    .record-item .r-info {{ flex:1; }} .record-item .r-title {{ font-weight:bold; font-size:13px; }}
    .record-item .r-meta {{ font-size:11px; color:var(--gray); margin-top:3px; }}
    .record-actions {{ display:flex; gap:5px; }}

    .empty-state {{ text-align:center; padding:30px; color:var(--light-gray); }}

    .toast-container {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:10px; pointer-events:none; }}
    .toast {{ display:flex; align-items:center; gap:10px; padding:12px 20px; border-radius:10px; color:white; font-size:13px; font-weight:600; box-shadow:0 8px 25px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; pointer-events:auto; }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }}
    .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}

    @media (max-width:768px) {{
        .page-header {{ flex-direction:column; gap:12px; text-align:center; }}
        .team-role-row {{ flex-direction:column; align-items:flex-start; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">

    <!-- ========== هدر ========== -->
    <div class="page-header">
        <div class="page-header-left">
            <h2>🚑 ثبت کدهای عملیاتی (بیمارمحور)</h2>
            <p>👤 {full_name} | شیفت: {shift_name}</p>
        </div>
        <div class="page-header-right">
            <div class="shift-badge">🕒 {shift_name}</div>
            <a href="/module/supervisor" class="back-btn">⬅️ بازگشت</a>
        </div>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="switchTab('form')">📝 ثبت/ویرایش</button>
        <button class="tab" onclick="switchTab('list')">📋 سوابق شیفت</button>
    </div>

    <!-- تب فرم -->
    <div id="tab-form" class="tab-content active">
        <div class="card">
            <div class="card-title"><span>📝</span> اطلاعات بیمار و کد</div>
            <form id="code-form">
                <input type="hidden" name="shift_id" value="{shift_id}">
                <input type="hidden" name="edit_id" id="edit_id" value="">

                <!-- ردیف ۱: بخش + نوع کد + نام بیمار -->
                <div class="row" style="margin-bottom:12px;">
                    <div class="form-group" style="flex:1;">
                        <label>🏥 بخش</label>
                        <select name="dept_id" id="dept_id" class="form-select" required>{dept_options}</select>
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>🛑 نوع کد</label>
                        <select name="code_id" id="code_id" class="form-select" required onchange="loadRoles()">{code_options}</select>
                    </div>
                    <div class="form-group" style="flex:1.5;">
                        <label>👤 نام بیمار *</label>
                        <input type="text" name="patient_name" id="patient_name" class="form-input" required placeholder="نام بیمار...">
                    </div>
                </div>

                <!-- ردیف ۲: جنسیت + سن(سال) + سن(ماه) + سن(روز) -->
                <div class="row" style="margin-bottom:12px;">
                    <div class="form-group" style="flex:1;">
                        <label>⚥ جنسیت</label>
                        <select name="gender" id="gender" class="form-select">
                            <option value="آقا">آقا</option><option value="خانم">خانم</option>
                            <option value="کودک">کودک</option><option value="نوزاد">نوزاد</option>
                        </select>
                    </div>
                    <div class="form-group" style="flex:0.7;">
                        <label>📅 سن (سال)</label>
                        <input type="number" name="age" id="age" class="form-input" value="0" min="0" max="120" style="text-align:center;">
                    </div>
                    <div class="form-group" style="flex:0.7;">
                        <label>ماه</label>
                        <input type="number" name="age_month" id="age_month" class="form-input" value="0" min="0" max="12" style="text-align:center;">
                    </div>
                    <div class="form-group" style="flex:0.7;">
                        <label>روز</label>
                        <input type="number" name="age_day" id="age_day" class="form-input" value="0" min="0" max="31" style="text-align:center;">
                    </div>
                </div>

                <!-- ردیف ۳: زمان شروع + زمان پایان (با ماسک) -->
                <div class="row" style="margin-bottom:12px;">
                    <div class="form-group" style="flex:1;">
                        <label>⏰ زمان شروع</label>
                        <input type="text" name="start_time" id="start_time" class="form-input time-input" placeholder="--:--" maxlength="5">
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>🏁 زمان پایان</label>
                        <input type="text" name="end_time" id="end_time" class="form-input time-input" placeholder="--:--" maxlength="5">
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>👨‍⚕️ پزشک لیدر</label>
                        <div>
                            <select id="leader_select" class="form-select" onchange="handleSmartInput('leader', this)" style="margin-bottom:4px;">
                                <option value="">--- انتخاب یا تایپ جدید ---</option>
                            </select>
                            <input type="text" id="leader_new" class="form-input" style="display:none;" placeholder="نام پزشک لیدر...">
                        </div>
                        <input type="hidden" name="leader" id="leader" value="">
                    </div>
                </div>

                <!-- ردیف ۴: تشخیص + نتیجه + سایر موارد -->
                <div class="row" style="margin-bottom:12px;">
                    <div class="form-group" style="flex:1;">
                        <label>🔍 تشخیص</label>
                        <div>
                            <select id="diagnosis_select" class="form-select" onchange="handleSmartInput('diagnosis', this)" style="margin-bottom:4px;">
                                <option value="">--- انتخاب یا تایپ جدید ---</option>
                            </select>
                            <input type="text" id="diagnosis_new" class="form-input" style="display:none;" placeholder="تشخیص پزشکی...">
                        </div>
                        <input type="hidden" name="diagnosis" id="diagnosis" value="">
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>📝 نتیجه عملیات</label>
                        <div>
                            <select id="outcome_select" class="form-select" onchange="handleSmartInput('outcome', this)" style="margin-bottom:4px;">
                                <option value="">--- انتخاب یا تایپ جدید ---</option>
                            </select>
                            <input type="text" id="outcome_new" class="form-input" style="display:none;" placeholder="نتیجه عملیات...">
                        </div>
                        <input type="hidden" name="outcome" id="outcome" value="">
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>📋 سایر موارد</label>
                        <input type="text" name="other" id="other" class="form-input" placeholder="سایر موارد...">
                    </div>
                </div>

                <!-- توضیحات تکمیلی -->
                <div class="form-group">
                    <label>📝 توضیحات تکمیلی</label>
                    <textarea name="description" id="description" class="form-textarea" rows="4" placeholder="توضیحات اضافی..."></textarea>
                </div>
            </form>
        </div>

        <!-- تیم عملیاتی -->
        <div class="card">
            <div class="card-title"><span>👥</span> تیم عملیاتی</div>
            <div id="team-roles-container">
                <p style="color:var(--light-gray);">ابتدا نوع کد را انتخاب کنید</p>
            </div>
        </div>

        <div style="margin-top:15px; display:flex; gap:10px;">
            <button type="button" class="btn btn-primary btn-block" onclick="submitCode()" id="save-btn">
                <span id="save-text">💾 ثبت نهایی</span><span id="save-loading" style="display:none;">⏳ ...</span>
            </button>
            <button type="button" class="btn btn-warning" onclick="clearForm()">🔄 جدید</button>
        </div>
    </div>

    <!-- تب لیست -->
    <div id="tab-list" class="tab-content">
        <div class="card">
            <div class="card-title"><span>📋</span> سوابق ثبت شده در این شیفت</div>
            <div id="records-list"></div>
        </div>
    </div>
</div>

<script>
    var editingId = null, teamRoles = [], personnelList = [];
    var suggestions = {{ leader: [], diagnosis: [], outcome: [] }};

    // ========== توابع عمومی ==========
    function switchTab(tab) {{
        var tabs = document.querySelectorAll('.tab');
        var contents = document.querySelectorAll('.tab-content');
        tabs.forEach(function(t) {{ t.classList.remove('active'); }});
        contents.forEach(function(c) {{ c.classList.remove('active'); }});
        if (tab === 'form') {{
            tabs[0].classList.add('active');
            document.getElementById('tab-form').classList.add('active');
        }} else {{
            tabs[1].classList.add('active');
            document.getElementById('tab-list').classList.add('active');
            fetchRecordsList();
        }}
    }}

    function showToast(msg, type) {{
        var c = document.getElementById('toast-container');
        var t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = '<span>' + (type==='success'?'OK':'ERR') + '</span><span>' + msg + '</span><span style="cursor:pointer;margin-right:auto;" onclick="this.parentElement.remove()">x</span>';
        c.appendChild(t);
        setTimeout(function() {{ if(t.parentElement) t.remove(); }}, 4000);
    }}

    // ========== ماسک زمان ==========
    function setupTimeMask(inputId) {{
        var input = document.getElementById(inputId);
        if (!input) return;

        input.addEventListener('input', function(e) {{
            var val = this.value.replace(/[^0-9]/g, '');
            if (val.length > 4) val = val.substring(0, 4);
            
            var formatted = '';
            if (val.length > 0) {{
                formatted = val.substring(0, 2);
                if (val.length > 2) {{
                    formatted += ':' + val.substring(2, 4);
                }}
            }}
            this.value = formatted;
        }});

        input.addEventListener('blur', function() {{
            var val = this.value.trim();
            if (val === '') return;
            var parts = val.split(':');
            if (parts.length === 2) {{
                var h = parseInt(parts[0]);
                var m = parseInt(parts[1]);
                if (isNaN(h) || h < 0 || h > 23 || isNaN(m) || m < 0 || m > 59) {{
                    this.classList.add('invalid');
                }} else {{
                    this.classList.remove('invalid');
                }}
            }} else {{
                this.classList.add('invalid');
            }}
        }});

        input.addEventListener('focus', function() {{
            this.classList.remove('invalid');
        }});
    }}

    // ========== Smart Input ==========
    function handleSmartInput(field, selectEl) {{
        var newInput = document.getElementById(field + '_new');
        var hidden = document.getElementById(field);
        if (selectEl.value === '__new__') {{
            newInput.style.display = 'block';
            hidden.value = '';
        }} else {{
            hidden.value = selectEl.value;
            newInput.style.display = 'none';
        }}
    }}

    function bindNewInput(field) {{
        var inp = document.getElementById(field + '_new');
        var hidden = document.getElementById(field);
        if (inp) {{
            inp.addEventListener('input', function() {{ hidden.value = inp.value; }});
        }}
    }}

    // ========== پیشنهادات ==========
    async function loadSuggestions() {{
        try {{
            var res = await fetch('/module/supervisor/codes/suggestions');
            var data = await res.json();
            if (data.success) {{
                suggestions = data.suggestions;
                populateSuggestSelects();
            }}
        }} catch(e) {{ console.error(e); }}
    }}

    function populateSuggestSelects() {{
        ['leader', 'diagnosis', 'outcome'].forEach(function(f) {{
            var sel = document.getElementById(f + '_select');
            if (!sel) return;
            var cur = sel.value;
            sel.innerHTML = '<option value="">--- انتخاب یا تایپ جدید ---</option>';
            if (suggestions[f]) {{
                suggestions[f].forEach(function(v) {{
                    sel.innerHTML += '<option value="' + v + '">' + v + '</option>';
                }});
            }}
            sel.innerHTML += '<option value="__new__">+ مورد جدید...</option>';
            if (cur && cur !== '__new__') sel.value = cur;
        }});
    }}

    // ========== پرسنل ==========
    async function loadPersonnelList() {{
        try {{
            var res = await fetch('/module/supervisor/codes/personnel');
            var data = await res.json();
            if (data.success) personnelList = data.personnel;
        }} catch(e) {{ console.error(e); }}
    }}

    // ========== نقش‌ها ==========
    async function loadRoles() {{
        var codeId = document.getElementById('code_id').value;
        var container = document.getElementById('team-roles-container');
        if (!codeId) {{
            container.innerHTML = '<p style="color:var(--light-gray);">ابتدا نوع کد را انتخاب کنید</p>';
            teamRoles = [];
            return;
        }}
        try {{
            var res = await fetch('/module/supervisor/codes/roles/' + codeId);
            var data = await res.json();
            if (data.success) {{
                teamRoles = data.roles;
                renderTeamRoles();
            }} else {{
                container.innerHTML = '<p style="color:var(--light-gray);">نقشی برای این کد تعریف نشده است</p>';
                teamRoles = [];
            }}
        }} catch(e) {{ showToast('خطا در دریافت نقش ها', 'error'); }}
    }}

    function renderTeamRoles() {{
        var container = document.getElementById('team-roles-container');
        if (!teamRoles.length) {{
            container.innerHTML = '<p style="color:var(--light-gray);">نقشی تعریف نشده</p>';
            return;
        }}
        var html = '<div class="row" style="font-weight:bold;margin-bottom:8px;padding:0 10px;"><span style="flex:1;">عنوان نقش</span><span style="flex:2;">پرسنل</span><span style="flex:2;">ملاحظات</span></div>';
        teamRoles.forEach(function(role) {{
            html += '<div class="team-role-row">';
            html += '<span class="role-name">' + role.nam_naghsh_kod + '</span>';
            html += '<select id="role_person_' + role.ID_onvan_naghsh_kod + '" class="form-select" style="flex:2;">';
            html += '<option value="">--- انتخاب ---</option>';
            personnelList.forEach(function(p) {{
                html += '<option value="' + p.ID_person + '">' + p.full_name + '</option>';
            }});
            html += '</select>';
            html += '<input type="text" id="role_desc_' + role.ID_onvan_naghsh_kod + '" class="form-input" style="flex:2;" placeholder="توضیحات">';
            html += '</div>';
        }});
        container.innerHTML = html;
    }}

    // ========== ثبت ==========
    async function submitCode() {{
        var form = document.getElementById('code-form');
        var formData = new FormData(form);

        var team = [];
        teamRoles.forEach(function(role) {{
            var pidEl = document.getElementById('role_person_' + role.ID_onvan_naghsh_kod);
            var descEl = document.getElementById('role_desc_' + role.ID_onvan_naghsh_kod);
            var pid = pidEl ? pidEl.value : '';
            var desc = descEl ? descEl.value : '';
            if (pid) {{
                team.push({{ naghsh_id: role.ID_onvan_naghsh_kod, person_id: pid, description: desc }});
            }}
        }});

        var ids = team.map(function(t) {{ return t.person_id; }});
        var uniqueIds = ids.filter(function(v, i, a) {{ return a.indexOf(v) === i; }});
        if (uniqueIds.length !== ids.length) {{
            showToast('یک نفر نمی تواند همزمان دو نقش داشته باشد', 'error');
            return;
        }}
        formData.append('team', JSON.stringify(team));

        if (!formData.get('patient_name') || !formData.get('dept_id') || !formData.get('code_id')) {{
            showToast('نام بیمار، بخش و نوع کد الزامی است', 'error');
            return;
        }}

        document.getElementById('save-text').style.display = 'none';
        document.getElementById('save-loading').style.display = 'inline';
        document.getElementById('save-btn').disabled = true;

        try {{
            var res = await fetch('/module/supervisor/codes/save', {{ method:'POST', body: formData }});
            var data = await res.json();
            if (data.success) {{
                showToast(data.message, 'success');
                editingId = data.record_id;
                document.getElementById('edit_id').value = data.record_id;
                fetchRecordsList();
            }} else {{
                showToast(data.message, 'error');
            }}
        }} catch(e) {{ showToast('خطا در ارتباط', 'error'); }}

        document.getElementById('save-text').style.display = 'inline';
        document.getElementById('save-loading').style.display = 'none';
        document.getElementById('save-btn').disabled = false;
    }}

    function clearForm() {{
        document.getElementById('code-form').reset();
        document.getElementById('edit_id').value = '';
        editingId = null;
        document.getElementById('team-roles-container').innerHTML = '<p style="color:var(--light-gray);">ابتدا نوع کد را انتخاب کنید</p>';
        teamRoles = [];
        document.getElementById('leader_new').style.display = 'none';
        document.getElementById('diagnosis_new').style.display = 'none';
        document.getElementById('outcome_new').style.display = 'none';
        document.getElementById('leader').value = '';
        document.getElementById('diagnosis').value = '';
        document.getElementById('outcome').value = '';
        document.getElementById('start_time').classList.remove('invalid');
        document.getElementById('end_time').classList.remove('invalid');
    }}

    // ========== ویرایش ==========
    async function editRecord(id) {{
        try {{
            var res = await fetch('/module/supervisor/codes/get/' + id);
            var data = await res.json();
            if (data.success) {{
                var r = data.record;
                document.getElementById('edit_id').value = r.ID_kod;
                document.getElementById('dept_id').value = r.nam_bakhsh;
                document.getElementById('code_id').value = r.onvan_kod;
                document.getElementById('patient_name').value = r.nam_biar || '';
                document.getElementById('gender').value = r.jens || 'آقا';
                document.getElementById('age').value = r.sen || 0;
                document.getElementById('age_month').value = r.sen_mah || 0;
                document.getElementById('age_day').value = r.sen_roz || 0;
                document.getElementById('start_time').value = (r.time_saat_dagig_shoro || '').substring(0,5);
                document.getElementById('end_time').value = (r.time_sat_dagigeh_paian || '').substring(0,5);
                document.getElementById('other').value = r.mavred1 || '';
                document.getElementById('description').value = r.tavzih || '';

                setSmartValue('leader', r.nam_pezshk_lider);
                setSmartValue('diagnosis', r.tashkhis_pezeshk);
                setSmartValue('outcome', r.natijeh_amlit);

                editingId = r.ID_kod;
                await loadRoles();
                var teamData = data.team || [];
                setTimeout(function() {{
                    teamData.forEach(function(member) {{
                        var pSel = document.getElementById('role_person_' + member.nam_nagsh);
                        var dInp = document.getElementById('role_desc_' + member.nam_nagsh);
                        if (pSel) pSel.value = member.id_person;
                        if (dInp) dInp.value = member.description || '';
                    }});
                }}, 300);
                switchTab('form');
                window.scrollTo(0,0);
            }} else showToast('خطا در دریافت اطلاعات', 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    function setSmartValue(field, val) {{
        var hidden = document.getElementById(field);
        var sel = document.getElementById(field + '_select');
        var newInp = document.getElementById(field + '_new');
        if (!val) {{
            hidden.value = '';
            sel.value = '';
            newInp.style.display = 'none';
            return;
        }}
        if (suggestions[field] && suggestions[field].indexOf(val) !== -1) {{
            sel.value = val;
            newInp.style.display = 'none';
            hidden.value = val;
        }} else {{
            sel.value = '__new__';
            newInp.style.display = 'block';
            newInp.value = val;
            hidden.value = val;
        }}
    }}

    async function deleteRecord(id) {{
        if (!confirm('از حذف این کد اطمینان دارید؟')) return;
        try {{
            var res = await fetch('/module/supervisor/codes/delete/' + id, {{ method:'POST' }});
            var data = await res.json();
            if (data.success) {{
                showToast('حذف شد', 'success');
                if (editingId == id) clearForm();
                fetchRecordsList();
            }} else showToast(data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    async function fetchRecordsList() {{
        try {{
            var res = await fetch('/module/supervisor/codes/list/{shift_id}');
            var data = await res.json();
            if (data.success) renderRecordsList(data.records);
        }} catch(e) {{ console.error(e); }}
    }}

    function renderRecordsList(records) {{
        var div = document.getElementById('records-list');
        if (!records.length) {{
            div.innerHTML = '<div class="empty-state"><p>رکوردی یافت نشد</p></div>';
            return;
        }}
        var html = '';
        records.forEach(function(r) {{
            var timeDisplay = (r.time_saat_dagig_shoro || '---').substring(0,5);
            html += '<div class="record-item">';
            html += '<div class="r-info">';
            html += '<div class="r-title">👤 ' + r.nam_biar + ' - ' + r.dept_name + ' | 🛑 ' + r.code_name + ' | ⏰ ' + timeDisplay + '</div>';
            html += '</div>';
            html += '<div class="record-actions">';
            html += '<button class="btn btn-sm btn-primary" onclick="editRecord(' + r.ID_kod + ')">✏️ ویرایش</button>';
            html += '<button class="btn btn-sm btn-danger" onclick="deleteRecord(' + r.ID_kod + ')">🗑️ حذف</button>';
            html += '</div>';
            html += '</div>';
        }});
        div.innerHTML = html;
    }}

    // ========== راه اندازی ==========
    document.addEventListener('DOMContentLoaded', function() {{
        loadSuggestions();
        loadPersonnelList();
        fetchRecordsList();
        bindNewInput('leader');
        bindNewInput('diagnosis');
        bindNewInput('outcome');
        setupTimeMask('start_time');
        setupTimeMask('end_time');
    }});
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions (بدون تغییر)
# ==========================================

def save_code(user, form_data):
    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id')
    edit_id = form_data.get('edit_id') or None
    dept_id = form_data.get('dept_id')
    code_id = form_data.get('code_id')
    patient_name = form_data.get('patient_name')
    gender = form_data.get('gender', 'آقا')
    age = form_data.get('age', 0)
    age_month = form_data.get('age_month', 0)
    age_day = form_data.get('age_day', 0)
    start_time = form_data.get('start_time', '')
    end_time = form_data.get('end_time', '')
    leader = form_data.get('leader', '')
    diagnosis = form_data.get('diagnosis', '')
    outcome = form_data.get('outcome', '')
    other = form_data.get('other', '')
    desc = form_data.get('description', '')
    team_json = form_data.get('team', '[]')

    try:
        team = json.loads(team_json)
    except:
        team = []

    if not patient_name or not dept_id or not code_id:
        return {'success': False, 'message': 'نام بیمار، بخش و نوع کد الزامی است'}

    person_ids = [t['person_id'] for t in team]
    if len(person_ids) != len(set(person_ids)):
        return {'success': False, 'message': 'یک نفر نمی‌تواند همزمان دو نقش داشته باشد'}

    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()

    conn = get_connection()
    cursor = conn.cursor()
    try:
        if edit_id:
            cursor.execute("""UPDATE tbl_amliat_kod SET
                nam_bakhsh=%s, onvan_kod=%s, nam_biar=%s, jens=%s, sen=%s,
                time_saat_dagig_shoro=%s, `time_sat_dagigeh_paian`=%s,
                nam_pezshk_lider=%s, tashkhis_pezeshk=%s, natijeh_amlit=%s,
                mavred1=%s, tavzih=%s, zaman_sabt=%s, sen_mah=%s, sen_roz=%s
                WHERE ID_kod=%s""",
                (dept_id, code_id, patient_name, gender, age, start_time, end_time,
                 leader, diagnosis, outcome, other, desc, now, age_month, age_day, edit_id))
            record_id = int(edit_id)
            cursor.execute("DELETE FROM tbl_naghsh_kod WHERE nam_kod=%s", (record_id,))
        else:
            cursor.execute("""INSERT INTO tbl_amliat_kod
                (dat_sabt, onvan_kod, nam_biar, jens, sen, time_saat_dagig_shoro,
                 `time_sat_dagigeh_paian`, nam_pezshk_lider, tashkhis_pezeshk,
                 natijeh_amlit, nam_bakhsh, nam_shift, mavred1, tavzih,
                 UserID, zaman_sabt, sen_mah, sen_roz)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (today, code_id, patient_name, gender, age, start_time, end_time,
                 leader, diagnosis, outcome, dept_id, shift_id, other, desc,
                 user_id, now, age_month, age_day))
            record_id = cursor.lastrowid

        for t in team:
            cursor.execute("""INSERT INTO tbl_naghsh_kod
                (dat_sabt, id_person, nam_nagsh, description, nam_kod, UserID, zaman_sabt)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (today, t['person_id'], t['naghsh_id'], t['description'], record_id, user_id, now))

        conn.commit()
       
        log_crud('save_code', user_id, key_value=record_id,
                 new_value=f"بیمار:{patient_name}, کد:{code_id}, بخش:{dept_id}, تیم:{len(team)}")
        
        return {'success': True, 'message': 'عملیات با موفقیت ثبت شد', 'record_id': record_id}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'خطا: {str(e)}'}
    finally:
        cursor.close()
        conn.close()


def get_code_record(record_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tbl_amliat_kod WHERE ID_kod=%s", (record_id,))
        rec = cursor.fetchone()
        if not rec:
            return {'success': False, 'message': 'رکورد یافت نشد'}
        cursor.execute("SELECT * FROM tbl_naghsh_kod WHERE nam_kod=%s", (record_id,))
        team = cursor.fetchall()
        for row in [rec] + team:
            for k in list(row.keys()):
                if isinstance(row[k], bytearray):
                    row[k] = row[k].decode('utf-8')
        return {'success': True, 'record': rec, 'team': team}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        cursor.close()
        conn.close()


def delete_code(user, record_id):
    user_id = user.get('UserID', 0)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tbl_naghsh_kod WHERE nam_kod=%s", (record_id,))
        cursor.execute("DELETE FROM tbl_amliat_kod WHERE ID_kod=%s", (record_id,))
        conn.commit()
        log_crud('delete_code', user_id, key_value=record_id)
        return {'success': True, 'message': 'کد و تیم مربوطه حذف شدند'}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        cursor.close()
        conn.close()




def get_codes_list(shift_id):
    records = query("""SELECT m.ID_kod, m.nam_biar, b.nam_bakhsh as dept_name,
        ok.nam_kod as code_name, m.time_saat_dagig_shoro
        FROM tbl_amliat_kod m LEFT JOIN tbl_onvan_kod ok ON m.onvan_kod = ok.ID_onvan_kod
        LEFT JOIN tbl_bakhsh b ON m.nam_bakhsh = b.ID_nam_bakhsh
        WHERE m.nam_shift = %s ORDER BY m.ID_kod DESC""",
        params=(shift_id,), fetch_all=True) or []
    return {'success': True, 'records': records}


def get_code_roles_for_form(code_id):
    if not code_id: return {'success': False, 'roles': []}
    roles = query("SELECT ID_onvan_naghsh_kod, nam_naghsh_kod FROM tbl_onvan_naghsh WHERE id_onvan_kod = %s",
        params=(code_id,), fetch_all=True) or []
    return {'success': True, 'roles': roles}


def get_personnel_for_form():
    pers = query("SELECT ID_person, CONCAT(nam, ' ', famil) as full_name FROM tbl_person WHERE isActiv=1 ORDER BY famil",
        fetch_all=True) or []
    return {'success': True, 'personnel': pers}


def get_suggestions_for_form():
    def get_distinct(column):
        rows = query(f"SELECT DISTINCT {{column}} FROM tbl_amliat_kod WHERE {{column}} IS NOT NULL AND {{column}} != ''".format(column=column), fetch_all=True) or []
        return [r[column] for r in rows]

    return {
        'success': True,
        'suggestions': {
            'leader': get_distinct('nam_pezshk_lider'),
            'diagnosis': get_distinct('tashkhis_pezeshk'),
            'outcome': get_distinct('natijeh_amlit')
        }
    }
    