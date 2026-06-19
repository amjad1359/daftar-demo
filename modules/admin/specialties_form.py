"""
مدیریت تخصص پزشکان – ادمین
ثبت، ویرایش و حذف عناوین تخصص با قابلیت آنکال
نسخه Flask با AJAX، Toast و طراحی مدرن
"""

from models.database import query
import json
from utils.auto_log import log_crud

def get_specialties_form(user):
    """صفحه اصلی مدیریت تخصص پزشکان"""

    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
        --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
        --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
        --bg: #f1f5f9; --white: #fff; --radius: 12px; --transition: 0.2s ease;
        --purple: #8b5cf6; --purple-light: #a78bfa;
        --ankal-red: #ff6b6b; --ankal-teal: #4ecdc4;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:1200px; margin:0 auto; padding:20px; }}

    /* هدر */
    .spec-header {{
        background: linear-gradient(135deg, #7c3aed, #8b5cf6);
        color:white; border-radius:16px; padding:25px 30px; margin-bottom:25px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(124,58,237,0.25);
    }}
    .spec-header h2 {{ font-size:24px; margin:0; }}
    .spec-header p {{ opacity:0.85; font-size:13px; margin:5px 0 0 0; }}
    .back-btn {{
        color:white; text-decoration:none; padding:8px 16px;
        border:1px solid rgba(255,255,255,0.4); border-radius:8px;
        font-size:13px; transition:var(--transition);
    }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    /* چیدمان اصلی */
    .main-grid {{
        display:grid; grid-template-columns:1fr 1.2fr; gap:25px;
        align-items:start;
    }}

    /* کارت‌ها */
    .card {{
        background:var(--white); border-radius:var(--radius); padding:25px;
        border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05);
    }}
    .card-header {{
        font-size:18px; font-weight:bold; color:var(--dark);
        margin-bottom:20px; padding-bottom:12px;
        border-bottom:2px solid var(--border);
        display:flex; align-items:center; gap:8px;
    }}
    .card-header .badge {{
        background:var(--purple); color:white; font-size:12px;
        padding:4px 12px; border-radius:15px; font-weight:normal;
        margin-right:auto;
    }}

    /* فرم‌ها */
    .form-group {{ margin-bottom:18px; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:6px; }}
    .form-input {{
        width:100%; padding:12px 14px; border:2px solid var(--border);
        border-radius:8px; font-size:14px; font-family:inherit;
        transition:var(--transition); background:var(--white);
    }}
    .form-input:focus {{
        border-color:var(--purple); outline:none;
        box-shadow:0 0 0 3px rgba(139,92,246,0.15);
    }}
    .form-input.error {{ border-color:var(--danger); background:#fef2f2; }}

    /* چک‌باکس آنکال */
    .ankal-toggle {{
        display:flex; align-items:center; gap:12px; padding:15px 18px;
        background:var(--bg); border-radius:10px; cursor:pointer;
        transition:var(--transition); user-select:none;
        border:2px solid transparent;
    }}
    .ankal-toggle:hover {{ border-color:var(--border); }}
    .ankal-toggle.active {{
        border-color:var(--ankal-red); background:#fff5f5;
    }}
    .ankal-toggle:not(.active) {{
        border-color:var(--ankal-teal); background:#f0fdfa;
    }}
    .ankal-toggle-icon {{
        width:48px; height:48px; border-radius:12px;
        display:flex; align-items:center; justify-content:center;
        font-size:24px; flex-shrink:0;
    }}
    .ankal-toggle.active .ankal-toggle-icon {{
        background:var(--ankal-red); color:white;
    }}
    .ankal-toggle:not(.active) .ankal-toggle-icon {{
        background:var(--ankal-teal); color:white;
    }}
    .ankal-toggle-info {{ flex:1; }}
    .ankal-toggle-info .title {{ font-weight:bold; font-size:14px; color:var(--dark); }}
    .ankal-toggle-info .desc {{
        font-size:11px; color:var(--gray); margin-top:3px;
    }}

    /* دکمه‌ها */
    .btn {{
        display:inline-flex; align-items:center; justify-content:center; gap:6px;
        padding:12px 20px; border:none; border-radius:8px; font-size:14px;
        font-weight:600; cursor:pointer; font-family:inherit;
        transition:var(--transition); text-decoration:none; white-space:nowrap;
    }}
    .btn-primary {{
        background:linear-gradient(135deg, #7c3aed, #8b5cf6); color:white;
    }}
    .btn-primary:hover {{ transform:translateY(-1px); box-shadow:0 4px 12px rgba(124,58,237,0.3); }}
    .btn-outline {{
        background:white; color:var(--purple); border:2px solid var(--purple);
    }}
    .btn-outline:hover {{ background:var(--purple); color:white; }}
    .btn-danger {{ background:var(--danger); color:white; }}
    .btn-danger:hover {{ background:#dc2626; }}
    .btn-xs {{ padding:5px 10px; font-size:11px; border-radius:6px; }}

    .form-actions {{
        display:flex; gap:10px; margin-top:20px;
    }}

    /* کارت‌های تخصص */
    .spec-list {{ display:flex; flex-direction:column; gap:10px; max-height:600px; overflow-y:auto; }}
    .spec-card {{
        background:var(--white); border:1px solid var(--border);
        border-right:4px solid var(--purple); border-radius:10px;
        padding:15px 18px; transition:var(--transition);
        display:flex; align-items:center; justify-content:space-between;
    }}
    .spec-card:hover {{
        border-color:var(--purple-light); box-shadow:0 2px 8px rgba(0,0,0,0.05);
        transform:translateX(-3px);
    }}
    .spec-card .spec-info {{ flex:1; }}
    .spec-card .spec-name {{ font-weight:bold; font-size:15px; color:var(--dark); }}
    .spec-card .spec-meta {{
        font-size:11px; color:var(--gray); margin-top:4px;
        display:flex; align-items:center; gap:10px;
    }}
    .spec-card .spec-code {{
        background:var(--bg); padding:2px 8px; border-radius:8px;
        font-family:monospace;
    }}
    .spec-card .spec-actions {{ display:flex; gap:6px; }}

    /* بج‌ها */
    .badge-ankal {{
        display:inline-block; padding:3px 10px; border-radius:12px;
        font-size:11px; font-weight:600;
    }}
    .badge-ankal.yes {{
        background:#fee2e2; color:#991b1b;
    }}
    .badge-ankal.no {{
        background:#d1fae5; color:#065f46;
    }}

    /* Toast */
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

    /* رسپانسیو */
    @media (max-width:768px) {{
        .main-grid {{ grid-template-columns:1fr; }}
        .spec-header {{ flex-direction:column; gap:15px; text-align:center; }}
        .spec-card {{ flex-direction:column; align-items:flex-start; gap:10px; }}
        .spec-card .spec-actions {{ width:100%; justify-content:flex-end; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="spec-header">
        <div>
            <h2>🩺 مدیریت عناوین تخصص پزشکان</h2>
            <p>تعریف و مدیریت تخصص‌ها با قابلیت تعیین وضعیت آنکال</p>
        </div>
        <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
    </div>

    <div class="main-grid">
        <!-- ستون فرم -->
        <div class="card">
            <div class="card-header">
                <span>📝</span> اطلاعات تخصص
                <span class="badge" id="edit-badge" style="display:none;">✏️ در حال ویرایش</span>
            </div>

            <div class="form-group">
                <label>عنوان تخصص</label>
                <input type="text" id="spec-name" class="form-input"
                       placeholder="مثلاً: متخصص قلب، جراح عمومی، پاتولوژیست...">
            </div>

            <div class="form-group">
                <label>وضعیت آنکال</label>
                <div class="ankal-toggle" id="ankal-toggle" onclick="toggleAnkal()">
                    <div class="ankal-toggle-icon" id="ankal-icon">🏥</div>
                    <div class="ankal-toggle-info">
                        <div class="title" id="ankal-title">نیاز به آنکال دارد</div>
                        <div class="desc">اگر این تخصص نیاز به حضور آنکال دارد، این گزینه را فعال کنید</div>
                    </div>
                </div>
            </div>

            <input type="hidden" id="edit-spec-id" value="">
            <input type="hidden" id="is-ankal" value="0">

            <div class="form-actions">
                <button class="btn btn-primary" style="flex:2;" onclick="saveSpecialty()">
                    <span id="save-text">✅ ثبت تخصص جدید</span>
                    <span id="save-loading" style="display:none;">⏳ ...</span>
                </button>
                <button class="btn btn-outline" style="flex:1;" id="cancel-btn" onclick="cancelEdit()" style="display:none;">
                    ❌ انصراف
                </button>
            </div>
        </div>

        <!-- ستون لیست -->
        <div class="card">
            <div class="card-header">
                <span>📋</span> تخصص‌های ثبت شده
                <span class="badge" id="spec-count">۰ تخصص</span>
            </div>
            <div class="spec-list" id="spec-list">
                <p style="text-align:center; color:var(--light-gray); padding:30px;">در حال بارگذاری...</p>
            </div>
        </div>
    </div>
</div>

<script>
    let editingId = null;
    let isAnkal = false;

    // ==================== توابع عمومی ====================
    function showToast(msg, type) {{
        const c = document.getElementById('toast-container');
        const t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = `<span>${{type==='success'?'✅':'❌'}}</span><span>${{msg}}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    // ==================== مدیریت آنکال ====================
    function toggleAnkal() {{
        isAnkal = !isAnkal;
        document.getElementById('is-ankal').value = isAnkal ? '1' : '0';
        const toggle = document.getElementById('ankal-toggle');
        const icon = document.getElementById('ankal-icon');
        const title = document.getElementById('ankal-title');

        if (isAnkal) {{
            toggle.classList.add('active');
            icon.textContent = '📞✅';
            title.textContent = 'نیاز به آنکال دارد';
        }} else {{
            toggle.classList.remove('active');
            icon.textContent = '❌';
            title.textContent = 'بدون نیاز به آنکال';
        }}
    }}

    function setAnkalState(state) {{
        isAnkal = state;
        document.getElementById('is-ankal').value = state ? '1' : '0';
        const toggle = document.getElementById('ankal-toggle');
        const icon = document.getElementById('ankal-icon');
        const title = document.getElementById('ankal-title');

        if (state) {{
            toggle.classList.add('active');
            icon.textContent = '📞✅';
            title.textContent = 'نیاز به آنکال دارد';
        }} else {{
            toggle.classList.remove('active');
            icon.textContent = '❌';
            title.textContent = 'بدون نیاز به آنکال';
        }}
    }}

    // ==================== بارگذاری لیست ====================
    async function loadSpecialties() {{
        try {{
            const res = await fetch('/module/admin/specialties/list');
            const data = await res.json();
            const list = document.getElementById('spec-list');
            document.getElementById('spec-count').textContent = `${{data.specialties.length}} تخصص`;

            if (!data.specialties.length) {{
                list.innerHTML = '<p style="text-align:center; color:var(--light-gray); padding:30px;">هنوز تخصصی تعریف نشده است</p>';
                return;
            }}

            let html = '';
            data.specialties.forEach(spec => {{
                const ankalBadge = spec.IS_Ankal
                    ? '<span class="badge-ankal yes">📞✅ آنکال</span>'
                    : '<span class="badge-ankal no">❌ غیرآنکال</span>';

                html += `<div class="spec-card" id="spec-row-${{spec.ID_onvan_takhasos}}">
                    <div class="spec-info">
                        <div class="spec-name">${{spec.nam_takhasos}} ${{ankalBadge}}</div>
                        <div class="spec-meta">
                            <span class="spec-code">🆔 کد: ${{spec.ID_onvan_takhasos}}</span>
                            <span>📅 ${{spec.dat_sabt || '---'}}</span>
                        </div>
                    </div>
                    <div class="spec-actions">
                        <button class="btn btn-outline btn-xs" onclick="editSpecialty(${{spec.ID_onvan_takhasos}}, '${{spec.nam_takhasos.replace(/'/g, "\\'")}}', ${{spec.IS_Ankal ? 'true' : 'false'}})">
                            📝 ویرایش
                        </button>
                        <button class="btn btn-danger btn-xs" onclick="deleteSpecialty(${{spec.ID_onvan_takhasos}})">
                            🗑️ حذف
                        </button>
                    </div>
                </div>`;
            }});
            list.innerHTML = html;
        }} catch(e) {{ console.error(e); }}
    }}

    // ==================== ویرایش ====================
    function editSpecialty(id, name, ankal) {{
        editingId = id;
        document.getElementById('edit-spec-id').value = id;
        document.getElementById('spec-name').value = name;
        setAnkalState(ankal);
        document.getElementById('save-text').textContent = '💾 بروزرسانی';
        document.getElementById('edit-badge').style.display = 'inline';
        document.getElementById('cancel-btn').style.display = 'inline-flex';
        document.getElementById('spec-name').focus();
    }}

    function cancelEdit() {{
        editingId = null;
        document.getElementById('edit-spec-id').value = '';
        document.getElementById('spec-name').value = '';
        setAnkalState(false);
        document.getElementById('save-text').textContent = '✅ ثبت تخصص جدید';
        document.getElementById('edit-badge').style.display = 'none';
        document.getElementById('cancel-btn').style.display = 'none';
        document.getElementById('spec-name').classList.remove('error');
    }}

    // ==================== ذخیره ====================
    async function saveSpecialty() {{
        const name = document.getElementById('spec-name').value.trim();

        if (!name) {{
            document.getElementById('spec-name').classList.add('error');
            showToast('⛔ لطفاً عنوان تخصص را وارد کنید', 'error');
            return;
        }}
        document.getElementById('spec-name').classList.remove('error');

        const saveText = document.getElementById('save-text');
        const saveLoading = document.getElementById('save-loading');
        saveText.style.display = 'none';
        saveLoading.style.display = 'inline';

        try {{
            const formData = new FormData();
            formData.append('spec_name', name);
            formData.append('is_ankal', isAnkal ? '1' : '0');
            if (editingId) formData.append('spec_id', editingId);

            const res = await fetch('/module/admin/specialties/save', {{ method:'POST', body:formData }});
            const data = await res.json();

            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                cancelEdit();
                loadSpecialties();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{
            showToast('⛔ خطا در ارتباط با سرور', 'error');
        }} finally {{
            saveText.style.display = 'inline';
            saveLoading.style.display = 'none';
        }}
    }}

    // ==================== حذف ====================
    async function deleteSpecialty(id) {{
        if (!confirm('آیا از حذف این تخصص اطمینان دارید؟\\n\\n⚠️ این عملیات قابل بازگشت نیست!')) return;

        try {{
            const formData = new FormData();
            formData.append('spec_id', id);
            const res = await fetch('/module/admin/specialties/delete', {{ method:'POST', body:formData }});
            const data = await res.json();

            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                if (editingId == id) cancelEdit();
                loadSpecialties();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{
            showToast('⛔ خطا در ارتباط با سرور', 'error');
        }}
    }}

    // ==================== لود اولیه ====================
    document.addEventListener('DOMContentLoaded', () => {{
        loadSpecialties();
        setAnkalState(false);
    }});

    // ==================== میانبر کیبورد ====================
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            cancelEdit();
        }}
        if (e.ctrlKey && e.key === 'Enter') {{
            e.preventDefault();
            saveSpecialty();
        }}
    }});
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions
# ==========================================

def get_specialties_list():
    """دریافت لیست تمام تخصص‌ها"""
    try:
        specialties = query(
            "SELECT ID_onvan_takhasos, nam_takhasos, IS_Ankal, dat_sabt FROM tbl_onvan_takhasos ORDER BY ID_onvan_takhasos DESC",
            fetch_all=True
        ) or []
        # فرمت تاریخ برای نمایش
        for s in specialties:
            d = str(s.get('dat_sabt', ''))
            if len(d) == 8:
                s['dat_sabt'] = f"{d[:4]}/{d[4:6]}/{d[6:]}"
        return {'success': True, 'specialties': specialties}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def save_specialty(user, form_data):
    user_id = user.get('UserID', 0)
    spec_id = form_data.get('spec_id')
    spec_name = form_data.get('spec_name', '').strip()
    is_ankal = form_data.get('is_ankal', '0')
    is_ankal_val = 1 if is_ankal == '1' else 0

    if not spec_name:
        return {'success': False, 'message': 'عنوان تخصص الزامی است'}

    try:
        if spec_id:
            # بروزرسانی
            existing = query(
                "SELECT ID_onvan_takhasos FROM tbl_onvan_takhasos WHERE nam_takhasos = %s AND ID_onvan_takhasos != %s",
                params=(spec_name, spec_id), fetch_one=True
            )
            if existing:
                return {'success': False, 'message': 'این عنوان تخصص قبلاً ثبت شده است'}

            old_record = query(
                "SELECT * FROM tbl_onvan_takhasos WHERE ID_onvan_takhasos = %s",
                (spec_id,), fetch_one=True
            )
            query(
                "UPDATE tbl_onvan_takhasos SET nam_takhasos=%s, IS_Ankal=%s WHERE ID_onvan_takhasos=%s",
                params=(spec_name, is_ankal_val, spec_id), commit=True
            )

            log_crud('update_specialty', user_id, key_value=spec_id,
                     old_value=json.dumps(old_record, ensure_ascii=False, default=str),
                     new_value=json.dumps({"name": spec_name, "ankal": is_ankal_val}, ensure_ascii=False))
            return {'success': True, 'message': 'تخصص با موفقیت ویرایش شد'}
        else:
            # ثبت جدید
            existing = query(
                "SELECT ID_onvan_takhasos FROM tbl_onvan_takhasos WHERE nam_takhasos = %s",
                params=(spec_name,), fetch_one=True
            )
            if existing:
                return {'success': False, 'message': 'این عنوان تخصص قبلاً ثبت شده است'}

            from jdatetime import date as jdate
            from datetime import datetime
            d_sh = int(jdate.today().strftime("%Y%m%d"))
            now = datetime.now()
            query(
                "INSERT INTO tbl_onvan_takhasos (nam_takhasos, dat_sabt, UserID, zaman_sabt, IS_Ankal) VALUES (%s, %s, 1, %s, %s)",
                params=(spec_name, d_sh, now, is_ankal_val), commit=True
            )
            new_id = query("SELECT MAX(ID_onvan_takhasos) as max_id FROM tbl_onvan_takhasos", fetch_one=True)['max_id']

            log_crud('save_specialty', user_id, key_value=new_id,
                     new_value=json.dumps({"name": spec_name, "ankal": is_ankal_val}, ensure_ascii=False))
            return {'success': True, 'message': 'تخصص جدید با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}



def delete_specialty(user, form_data):
    user_id = user.get('UserID', 0)
    spec_id = form_data.get('spec_id')

    if not spec_id:
        return {'success': False, 'message': 'شناسه تخصص نامعتبر است'}

    try:
        doctors_count = query(
            "SELECT COUNT(*) as cnt FROM tbl_person WHERE specialty_id = %s",
            params=(spec_id,), fetch_one=True
        )
        if doctors_count and doctors_count['cnt'] > 0:
            return {'success': False, 'message': f'این تخصص به {doctors_count["cnt"]} پزشک متصل است و قابل حذف نیست'}

        ankal_count = query(
            "SELECT COUNT(*) as cnt FROM tbl_ankal WHERE nam_takhasos = %s",
            params=(spec_id,), fetch_one=True
        )
        if ankal_count and ankal_count['cnt'] > 0:
            return {'success': False, 'message': f'این تخصص در {ankal_count["cnt"]} رکورد آنکال استفاده شده و قابل حذف نیست'}

        old_record = query(
            "SELECT * FROM tbl_onvan_takhasos WHERE ID_onvan_takhasos = %s",
            (spec_id,), fetch_one=True
        )
        query("DELETE FROM tbl_onvan_takhasos WHERE ID_onvan_takhasos = %s", params=(spec_id,), commit=True)

        log_crud('delete_specialty', user_id, key_value=spec_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str))
        return {'success': True, 'message': 'تخصص با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}
        
        