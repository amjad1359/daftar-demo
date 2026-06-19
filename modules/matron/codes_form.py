"""
تنظیمات کدهای عملیاتی – مترون
مدیریت عناوین کدها و نقش‌ها
"""

import jdatetime
from datetime import datetime
from models.database import query, get_connection
import json
from utils.auto_log import log_crud

def get_codes_form(user):
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    # لیست اولیه کدها (برای dropdown)
    codes_list = query("SELECT ID_onvan_kod, nam_kod FROM tbl_onvan_kod ORDER BY nam_kod", fetch_all=True) or []
    code_options = '<option value="">--- انتخاب کد ---</option>' + ''.join(
        f'<option value="{c["ID_onvan_kod"]}">{c["nam_kod"]}</option>' for c in codes_list
    )

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
    .codes-header {{
        background:linear-gradient(135deg, #b45309, #d97706); color:white; border-radius:16px; padding:25px 30px;
        margin-bottom:25px; display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(180,83,9,0.25);
    }}
    .codes-header h2 {{ font-size:24px; }}
    .back-btn {{ color:white; text-decoration:none; padding:8px 16px; border:1px solid rgba(255,255,255,0.4); border-radius:8px; }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    .tabs {{ display:flex; gap:5px; margin-bottom:25px; border-bottom:2px solid var(--border); }}
    .tab {{ padding:12px 24px; font-weight:600; border:none; background:none; color:var(--light-gray); cursor:pointer; border-bottom:2px solid transparent; transition:var(--transition); font-family:inherit; }}
    .tab:hover {{ color:var(--dark); }}
    .tab.active {{ color:var(--primary); border-bottom-color:var(--primary); }}
    .tab-content {{ display:none; }}
    .tab-content.active {{ display:block; animation:fadeIn 0.3s ease; }}

    .card {{ background:var(--white); border-radius:var(--radius); padding:25px; border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:25px; }}
    .card-title {{ font-weight:bold; color:var(--dark); margin-bottom:15px; padding-bottom:10px; border-bottom:2px solid var(--border); }}
    .row {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }}
    .form-group {{ margin-bottom:18px; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:6px; }}
    .form-select, .form-input {{
        width:100%; padding:12px 14px; border:2px solid var(--border); border-radius:8px;
        font-size:14px; font-family:inherit; transition:var(--transition); background:var(--white);
    }}
    .form-select:focus, .form-input:focus {{ border-color:var(--primary-light); outline:none; box-shadow:0 0 0 3px rgba(59,130,246,0.15); }}

    .btn {{ display:inline-flex; align-items:center; justify-content:center; gap:6px; padding:10px 20px; border:none; border-radius:8px; font-size:14px; font-weight:600; cursor:pointer; font-family:inherit; transition:var(--transition); text-decoration:none; }}
    .btn-primary {{ background:var(--primary); color:white; }} .btn-primary:hover {{ background:var(--primary-light); }}
    .btn-success {{ background:var(--success); color:white; }} .btn-danger {{ background:var(--danger); color:white; }}
    .btn-sm {{ padding:6px 12px; font-size:12px; }} .btn-xs {{ padding:4px 8px; font-size:11px; }}

    /* کدها و نقش‌ها */
    .code-block {{
        border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:10px; background:var(--white);
    }}
    .code-block .code-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }}
    .code-block .code-id {{ font-size:11px; color:var(--light-gray); }}
    .code-block .code-name-input {{ flex:1; max-width:300px; }}
    .code-block .role-tags {{ display:flex; gap:5px; flex-wrap:wrap; margin:8px 0; }}
    .role-tag {{
        display:inline-flex; align-items:center; background:#e0e7ff; color:#1e3a8a; padding:4px 10px;
        border-radius:14px; font-size:12px; border:1px solid #c7d2fe; gap:5px;
    }}
    .role-tag .role-name {{ cursor:pointer; }} .role-tag .role-delete {{ cursor:pointer; font-weight:bold; }}
    .role-tag:hover {{ background:#cdd9ff; }}

    .edit-role-panel {{ display:none; margin-top:8px; }}
    .edit-role-panel.show {{ display:flex; gap:8px; align-items:center; }}

    .toast-container {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:10px; pointer-events:none; }}
    .toast {{ display:flex; align-items:center; gap:12px; padding:14px 22px; border-radius:12px; color:white; font-weight:600; box-shadow:0 10px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }} .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}

    @media (max-width:768px) {{
        .codes-header {{ flex-direction:column; gap:15px; text-align:center; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="codes-header">
        <h2>🚑 تنظیمات کدهای عملیاتی</h2>
        <a href="/module/matron" class="back-btn">⬅️ بازگشت</a>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="switchTab('tab-manage')">🆕 تعریف و تخصیص</button>
        <button class="tab" onclick="switchTab('tab-list')">📋 لیست و مدیریت</button>
    </div>

    <!-- تب تعریف -->
    <div id="tab-manage" class="tab-content active">
        <div class="row" style="align-items:flex-start;">
            <!-- کد جدید -->
            <div class="card" style="flex:1;">
                <div class="card-title">➕ کد جدید</div>
                <div class="form-group">
                    <label>نام کد</label>
                    <input type="text" id="new-code-name" class="form-input" placeholder="مثال: Code Blue, CPR...">
                </div>
                <button class="btn btn-primary" onclick="addNewCode()">
                    <span id="save-code-text">💾 ثبت کد</span>
                    <span id="save-code-loading" style="display:none;">⏳ ...</span>
                </button>
            </div>

            <!-- نقش جدید -->
            <div class="card" style="flex:1;">
                <div class="card-title">👥 افزودن نقش به کد</div>
                <div class="form-group">
                    <label>انتخاب کد</label>
                    <select id="role-code-select" class="form-select">{code_options}</select>
                </div>
                <div class="form-group">
                    <label>عنوان نقش</label>
                    <input type="text" id="new-role-name" class="form-input" placeholder="مثال: لیدر تیم، پرستار CPR...">
                </div>
                <button class="btn btn-primary" onclick="addNewRole()">
                    <span id="save-role-text">💾 افزودن نقش</span>
                    <span id="save-role-loading" style="display:none;">⏳ ...</span>
                </button>
            </div>
        </div>
    </div>

    <!-- تب لیست -->
    <div id="tab-list" class="tab-content">
        <div class="card" style="padding:15px;">
            <div id="codes-list"></div>
        </div>
    </div>
</div>

<script>
    function switchTab(tab) {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        if (tab === 'tab-manage') {{
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.getElementById('tab-manage').classList.add('active');
        }} else {{
            document.querySelectorAll('.tab')[1].classList.add('active');
            document.getElementById('tab-list').classList.add('active');
            loadCodesList();
        }}
    }}

    function showToast(msg, type) {{
        const c = document.getElementById('toast-container'), t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span><span style="cursor:pointer;margin-right:auto;" onclick="this.parentElement.remove()">✕</span>';
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    // ==================== تعریف کد ====================
    async function addNewCode() {{
        const name = document.getElementById('new-code-name').value.trim();
        if (!name) {{ showToast('نام کد الزامی است', 'error'); return; }}
        document.getElementById('save-code-text').style.display = 'none';
        document.getElementById('save-code-loading').style.display = 'inline';
        try {{
            const res = await fetch('/module/matron/codes/add_code', {{
                method:'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'code_name=' + encodeURIComponent(name)
            }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ کد جدید ثبت شد', 'success');
                document.getElementById('new-code-name').value = '';
                // بروزرسانی dropdown نقش
                const select = document.getElementById('role-code-select');
                select.innerHTML += '<option value="' + data.id + '">' + data.name + '</option>';
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
        finally {{
            document.getElementById('save-code-text').style.display = 'inline';
            document.getElementById('save-code-loading').style.display = 'none';
        }}
    }}

    // ==================== تعریف نقش ====================
    async function addNewRole() {{
        const codeId = document.getElementById('role-code-select').value;
        const roleName = document.getElementById('new-role-name').value.trim();
        if (!codeId) {{ showToast('یک کد انتخاب کنید', 'error'); return; }}
        if (!roleName) {{ showToast('عنوان نقش الزامی است', 'error'); return; }}
        document.getElementById('save-role-text').style.display = 'none';
        document.getElementById('save-role-loading').style.display = 'inline';
        try {{
            const res = await fetch('/module/matron/codes/add_role', {{
                method:'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'code_id=' + codeId + '&role_name=' + encodeURIComponent(roleName)
            }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ نقش اضافه شد', 'success');
                document.getElementById('new-role-name').value = '';
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
        finally {{
            document.getElementById('save-role-text').style.display = 'inline';
            document.getElementById('save-role-loading').style.display = 'none';
        }}
    }}

    // ==================== لیست ====================

    async function loadCodesList() {{
        const res = await fetch('/module/matron/codes/list');
        const data = await res.json();
        const container = document.getElementById('codes-list');
        if (!data.codes || !data.codes.length) {{
            container.innerHTML = '<p style="color:var(--light-gray);">کدی تعریف نشده است</p>';
            return;
        }}
        let html = '';
        data.codes.forEach(code => {{
            // ساخت برچسب‌های نقش
            let rolesHtml = '';
            if (code.roles && code.roles.length) {{
                code.roles.forEach(r => {{
                    rolesHtml += '<span class="role-tag" id="role-' + r.ID_onvan_naghsh_kod + '">' +
                        '<span class="role-name" onclick="toggleEditRole(' + r.ID_onvan_naghsh_kod + ')">' + r.nam_naghsh_kod + '</span>' +
                        '<span class="role-delete" onclick="deleteRole(' + r.ID_onvan_naghsh_kod + ')">❌</span>' +
                    '</span>' +
                    '<div class="edit-role-panel" id="edit-role-' + r.ID_onvan_naghsh_kod + '">' +
                        '<input type="text" class="form-input" id="edit-role-name-' + r.ID_onvan_naghsh_kod + '" value="' + r.nam_naghsh_kod + '" style="max-width:200px;">' +
                        '<button class="btn btn-success btn-xs" onclick="updateRole(' + r.ID_onvan_naghsh_kod + ')">💾</button>' +
                    '</div>';
                }});
            }} else {{
                rolesHtml = '<span style="color:var(--light-gray); font-size:12px;">بدون نقش</span>';
            }}

            // ساخت دکمه حذف با disabled
            let disabledAttr = code.has_ops ? ' disabled' : '';

            html += '<div class="code-block">' +
                '<div class="code-header">' +
                    '<span class="code-id">#' + code.ID_onvan_kod + '</span>' +
                    '<input type="text" class="form-input code-name-input" id="code-name-' + code.ID_onvan_kod + '" value="' + code.nam_kod + '">' +
                    '<div>' +
                        '<button class="btn btn-primary btn-xs" onclick="updateCode(' + code.ID_onvan_kod + ')">💾</button>' +
                        '<button class="btn btn-danger btn-xs" onclick="deleteCode(' + code.ID_onvan_kod + ')"' + disabledAttr + '>🗑️</button>' +
                    '</div>' +
                '</div>' +
                '<div class="role-tags">' + rolesHtml + '</div>' +
            '</div>';
        }});
        container.innerHTML = html;
    }}
    
    async function updateCode(codeId) {{
        const newName = document.getElementById('code-name-' + codeId).value.trim();
        if (!newName) {{ showToast('نام نمی‌تواند خالی باشد', 'error'); return; }}
        try {{
            const res = await fetch('/module/matron/codes/update_code', {{
                method:'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'code_id=' + codeId + '&code_name=' + encodeURIComponent(newName)
            }});
            const data = await res.json();
            if (data.success) showToast('✅ نام کد بروزرسانی شد', 'success');
            else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    async function deleteCode(codeId) {{
        if (!confirm('از حذف این کد و تمام نقش‌هایش اطمینان دارید؟')) return;
        try {{
            const res = await fetch('/module/matron/codes/delete_code', {{
                method:'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'code_id=' + codeId
            }});
            const data = await res.json();
            if (data.success) {{ showToast('✅ کد حذف شد', 'success'); loadCodesList(); }}
            else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    function toggleEditRole(roleId) {{
        const panel = document.getElementById('edit-role-' + roleId);
        panel.classList.toggle('show');
    }}

    async function updateRole(roleId) {{
        const newName = document.getElementById('edit-role-name-' + roleId).value.trim();
        if (!newName) {{ showToast('نام نمی‌تواند خالی باشد', 'error'); return; }}
        try {{
            const res = await fetch('/module/matron/codes/update_role', {{
                method:'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'role_id=' + roleId + '&role_name=' + encodeURIComponent(newName)
            }});
            const data = await res.json();
            if (data.success) {{ showToast('✅ نقش بروزرسانی شد', 'success'); loadCodesList(); }}
            else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    async function deleteRole(roleId) {{
        if (!confirm('نقش حذف شود؟')) return;
        try {{
            const res = await fetch('/module/matron/codes/delete_role', {{
                method:'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'role_id=' + roleId
            }});
            const data = await res.json();
            if (data.success) {{ showToast('✅ نقش حذف شد', 'success'); loadCodesList(); }}
            else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    // لود اولیه
    document.addEventListener('DOMContentLoaded', () => {{
        // هیچ لود خاصی لازم نیست
    }});
</script>
</body>
</html>'''
    return html


# ==================== API Functions ====================

def add_code_api(user, code_name):
    if not code_name or not code_name.strip():
        return {'success': False, 'message': 'نام کد الزامی است'}
    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()
    user_id = user.get('UserID', 0)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tbl_onvan_kod (nam_kod, dat_sabt, UserID, zaman_sabt) VALUES (%s,%s,%s,%s)",
            (code_name.strip(), today, user_id, now)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        log_crud('add_code_api', user_id, key_value=new_id,
                 new_value=json.dumps({"name": code_name.strip()}, ensure_ascii=False))
        
        return {'success': True, 'id': new_id, 'name': code_name.strip()}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def add_role_api(user, code_id, role_name):
    user_id = user.get('UserID', 0)
    if not code_id or not role_name or not role_name.strip():
        return {'success': False, 'message': 'انتخاب کد و نام نقش الزامی است'}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tbl_onvan_naghsh (nam_naghsh_kod, id_onvan_kod) VALUES (%s, %s)",
            (role_name.strip(), int(code_id))
        )
        conn.commit()
        new_id = cursor.lastrowid   # شناسه نقش جدید
        conn.close()
        
        # لاگ
        log_crud('add_role_api', user_id, key_value=new_id,
                 new_value=json.dumps({"code_id": code_id, "role_name": role_name.strip()}, ensure_ascii=False))
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}






def list_codes_api():
    codes = query("SELECT * FROM tbl_onvan_kod ORDER BY ID_onvan_kod", fetch_all=True) or []
    roles_all = query("SELECT * FROM tbl_onvan_naghsh", fetch_all=True) or []
    # بررسی وابستگی هر کد
    for c in codes:
        c['has_ops'] = check_dependency("tbl_amliat_kod", "onvan_kod", c['ID_onvan_kod'])
        c['roles'] = [r for r in roles_all if r['id_onvan_kod'] == c['ID_onvan_kod']]
    return {'codes': codes}


def check_dependency(table, column, value):
    try:
        row = query(f"SELECT COUNT(*) as cnt FROM {{table}} WHERE {{column}} = %s".format(table=table, column=column),
                    (value,), fetch_one=True)
        return row['cnt'] > 0 if row else False
    except:
        return False

def update_code_api(user, code_id, code_name):
    user_id = user.get('UserID', 0)
    if not code_name or not code_name.strip():
        return {'success': False, 'message': 'نام کد نمی‌تواند خالی باشد'}
    try:
        old_record = query("SELECT * FROM tbl_onvan_kod WHERE ID_onvan_kod = %s", (code_id,), fetch_one=True)
        query("UPDATE tbl_onvan_kod SET nam_kod=%s WHERE ID_onvan_kod=%s", (code_name.strip(), code_id), commit=True)
        log_crud('update_code_api', user_id, key_value=code_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str),
                 new_value=json.dumps({"name": code_name.strip()}, ensure_ascii=False))
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def delete_code_api(user, code_id):
    user_id = user.get('UserID', 0)
    if check_dependency("tbl_amliat_kod", "onvan_kod", code_id):
        return {'success': False, 'message': 'این کد در عملیات‌ها استفاده شده و قابل حذف نیست'}
    try:
        old_record = query("SELECT * FROM tbl_onvan_kod WHERE ID_onvan_kod = %s", (code_id,), fetch_one=True)
        old_roles = query("SELECT * FROM tbl_onvan_naghsh WHERE id_onvan_kod = %s", (code_id,), fetch_all=True)
        query("DELETE FROM tbl_onvan_naghsh WHERE id_onvan_kod=%s", (code_id,), commit=True)
        query("DELETE FROM tbl_onvan_kod WHERE ID_onvan_kod=%s", (code_id,), commit=True)
        log_crud('delete_code_api', user_id, key_value=code_id,
                 old_value=json.dumps({"code": old_record, "roles": old_roles}, ensure_ascii=False, default=str))
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def delete_role_api(user, role_id):
    user_id = user.get('UserID', 0)
    if check_dependency("tbl_naghsh_kod", "nam_nagsh", role_id):
        return {'success': False, 'message': 'این نقش در عملیات‌ها استفاده شده و قابل حذف نیست'}
    try:
        old_record = query("SELECT * FROM tbl_onvan_naghsh WHERE ID_onvan_naghsh_kod = %s", (role_id,), fetch_one=True)
        query("DELETE FROM tbl_onvan_naghsh WHERE ID_onvan_naghsh_kod=%s", (role_id,), commit=True)
        log_crud('delete_role_api', user_id, key_value=role_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str))
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}



def update_role_api(role_id, role_name):
    user_id = user.get('UserID', 0)
    if not role_name or not role_name.strip():
        return {'success': False, 'message': 'نام نقش نمی‌تواند خالی باشد'}           
    try:
        query("UPDATE tbl_onvan_naghsh SET nam_naghsh_kod=%s WHERE ID_onvan_naghsh_kod=%s",
              (role_name.strip(), role_id), commit=True)

        old_record = query("SELECT * FROM tbl_onvan_naghsh WHERE ID_onvan_naghsh_kod = %s", (role_id,), fetch_one=True)
        query("UPDATE tbl_onvan_naghsh SET nam_naghsh_kod=%s WHERE ID_onvan_naghsh_kod=%s", (role_name.strip(), role_id), commit=True)
        log_crud('update_role_api', user_id, key_value=role_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str),
                 new_value=json.dumps({"name": role_name.strip()}, ensure_ascii=False))              
                  
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}

