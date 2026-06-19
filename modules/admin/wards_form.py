"""
مدیریت بخش‌ها – ادمین (با گروه‌بندی بخش)
"""

from models.database import query
import json
from utils.auto_log import log_crud

# لیست ثابت گروه‌ها
GROUP_OPTIONS = [
    'درمانی', 'پاراکلینیکی', 'خدماتی پشتیبانی', 'اداری',
    'موقت', 'سرپایی', 'تخصصی', 'فوق تخصصی', 'سایر'
]


def _ensure_grop_column():
    """اضافه کردن ستون grop در صورت عدم وجود"""
    col = query("SHOW COLUMNS FROM tbl_bakhsh LIKE 'grop'", fetch_one=True)
    if not col:
        query("ALTER TABLE tbl_bakhsh ADD COLUMN grop VARCHAR(50) DEFAULT NULL", commit=True)


def get_wards_form(user):
    _ensure_grop_column()

    html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
        --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
        --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
        --bg: #f1f5f9; --white: #fff; --radius: 14px; --transition: 0.2s ease;
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: Tahoma, Arial, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }
    .fade-in { animation:fadeIn 0.5s ease; }
    @keyframes fadeIn { from { opacity:0; transform:translateY(15px); } to { opacity:1; transform:translateY(0); } }

    .container { max-width:1000px; margin:0 auto; padding:20px; }

    .page-header {
        background: linear-gradient(135deg, #0284c7, #0ea5e9);
        color:white; border-radius:var(--radius); padding:22px 28px; margin-bottom:22px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(2,132,199,0.25);
    }
    .page-header h2 { font-size:22px; margin:0; }
    .back-btn {
        color:white; text-decoration:none; padding:8px 16px;
        border:1.5px solid rgba(255,255,255,0.4); border-radius:8px;
        font-size:13px; transition:var(--transition);
    }
    .back-btn:hover { background:rgba(255,255,255,0.15); }

    .card {
        background:var(--white); border-radius:var(--radius); padding:22px;
        border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.04);
        margin-bottom:20px;
    }
    .card-title {
        font-size:16px; font-weight:bold; color:var(--dark);
        margin-bottom:18px; padding-bottom:12px;
        border-bottom:2px solid var(--border);
        display:flex; align-items:center; gap:8px;
    }
    .card-title .count {
        background:var(--primary); color:white; font-size:11px;
        padding:3px 12px; border-radius:12px; font-weight:normal; margin-right:auto;
    }

    .add-row { display:flex; gap:10px; align-items:flex-end; flex-wrap:wrap; }
    .add-row .field { flex:1; min-width:160px; }
    .add-row .field label { display:block; font-size:12px; font-weight:600; color:var(--gray); margin-bottom:5px; }
    .add-row .field input, .add-row .field select {
        width:100%; padding:12px 15px; border:2px solid var(--border);
        border-radius:8px; font-size:14px; font-family:inherit; transition:var(--transition);
        background:var(--white);
    }
    .add-row .field input:focus, .add-row .field select:focus {
        border-color:#0ea5e9; outline:none; box-shadow:0 0 0 3px rgba(14,165,233,0.1);
    }

    .checkbox-wrap {
        display:flex; align-items:center; gap:8px; padding:12px 15px;
        background:var(--bg); border-radius:8px; cursor:pointer;
        user-select:none; border:2px solid transparent; transition:var(--transition);
    }
    .checkbox-wrap:hover { border-color:var(--border); }
    .checkbox-wrap.checked { border-color:#0ea5e9; background:#f0f9ff; }
    .checkbox-wrap input[type="checkbox"] { width:18px; height:18px; accent-color:#0ea5e9; }
    .checkbox-wrap span { font-size:13px; font-weight:600; color:var(--dark); }

    .btn {
        display:inline-flex; align-items:center; justify-content:center; gap:5px;
        padding:12px 20px; border:none; border-radius:8px; font-size:14px;
        font-weight:600; cursor:pointer; font-family:inherit;
        transition:var(--transition); white-space:nowrap;
    }
    .btn-primary { background:#0284c7; color:white; }
    .btn-primary:hover { background:#0369a1; }
    .btn-sm { padding:6px 12px; font-size:12px; border-radius:6px; }
    .btn-xs { padding:5px 10px; font-size:11px; border-radius:5px; }
    .btn-edit { background:var(--warning); color:white; }
    .btn-edit:hover { background:#d97706; }
    .btn-save { background:var(--success); color:white; }
    .btn-save:hover { background:#059669; }
    .btn-cancel { background:white; color:var(--gray); border:2px solid var(--border); }
    .btn-cancel:hover { border-color:var(--danger); color:var(--danger); }
    .btn-del { background:var(--danger); color:white; }
    .btn-del:hover { background:#dc2626; }

    .list-item {
        display:flex; align-items:center; gap:10px; padding:12px 15px;
        background:var(--bg); border:1px solid var(--border);
        border-right:4px solid #0ea5e9; border-radius:8px; margin-bottom:7px;
        transition:var(--transition);
    }
    .list-item:hover { border-color:#0ea5e9; }
    .list-item.editing { border-color:var(--warning); border-right-color:var(--warning); background:#fffbeb; }
    .list-item .item-id {
        font-family:monospace; font-size:11px; color:var(--gray);
        background:white; padding:4px 10px; border-radius:5px; min-width:40px; text-align:center;
    }
    .list-item .item-name {
        flex:1; padding:8px 12px; border:2px solid var(--border);
        border-radius:6px; font-size:13px; font-family:inherit; background:white;
    }
    .list-item .item-name:focus { border-color:#0ea5e9; outline:none; }
    .list-item .item-actions { display:flex; gap:5px; }

    .badge-amar {
        display:inline-block; padding:3px 10px; border-radius:10px;
        font-size:10px; font-weight:600;
    }
    .badge-amar.yes { background:#d1fae5; color:#065f46; }
    .badge-amar.no { background:#fee2e2; color:#991b1b; }

    .badge-group {
        display:inline-block; padding:3px 10px; border-radius:10px;
        font-size:10px; font-weight:600; background:#e0e7ff; color:#3730a3;
    }

    .modal-overlay {
        display:none; position:fixed; top:0; left:0; right:0; bottom:0;
        background:rgba(0,0,0,0.5); z-index:500; justify-content:center; align-items:center;
    }
    .modal-overlay.show { display:flex; }
    .modal {
        background:white; border-radius:14px; padding:25px; width:90%; max-width:400px;
        text-align:center; animation:fadeIn 0.3s ease;
    }
    .modal h4 { color:var(--danger); margin-bottom:8px; }
    .modal p { color:var(--gray); font-size:13px; margin-bottom:18px; }
    .modal .modal-btns { display:flex; gap:8px; justify-content:center; }

    .toast-box {
        position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000;
        display:flex; flex-direction:column; gap:8px; pointer-events:none;
    }
    .toast {
        display:flex; align-items:center; gap:10px; padding:14px 20px;
        border-radius:12px; color:white; font-size:13px; font-weight:600;
        box-shadow:0 8px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease;
        pointer-events:auto;
    }
    .toast.ok { background:linear-gradient(135deg, #059669, #10b981); }
    .toast.err { background:linear-gradient(135deg, #dc2626, #ef4444); }
    .toast .close { margin-right:auto; cursor:pointer; opacity:0.7; }
    @keyframes slideDown { from { opacity:0; transform:translateY(-25px); } to { opacity:1; transform:translateY(0); } }

    .empty { text-align:center; padding:40px; color:var(--light-gray); }

    @media (max-width:600px) {
        .add-row { flex-direction:column; }
        .list-item { flex-wrap:wrap; }
    }
</style>
</head>
<body>
<div class="toast-box" id="toast-box"></div>

<div class="modal-overlay" id="del-modal">
    <div class="modal">
        <h4>⚠️ تأیید حذف</h4>
        <p id="del-msg">آیا از حذف این بخش اطمینان دارید؟</p>
        <div class="modal-btns">
            <button class="btn btn-del" onclick="confirmDelete()">بله، حذف شود</button>
            <button class="btn btn-cancel btn-sm" onclick="closeModal()">انصراف</button>
        </div>
    </div>
</div>

<div class="container fade-in">
    <div class="page-header">
        <h2>🏥 مدیریت و تعریف بخش‌ها</h2>
        <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
    </div>

    <!-- فرم افزودن -->
    <div class="card">
        <div class="card-title">➕ ثبت بخش جدید</div>
        <div class="add-row">
            <div class="field">
                <label>نام بخش</label>
                <input type="text" id="new-name" placeholder="نام بخش جدید را وارد کنید...">
            </div>
            <div class="field">
                <label>گروه بخش</label>
                <select id="new-group">
                    <option value="">-- انتخاب کنید --</option>
''' + ''.join(f'<option value="{g}">{g}</option>' for g in GROUP_OPTIONS) + '''
                </select>
            </div>
            <div class="field">
                <label>آمارگیری</label>
                <label class="checkbox-wrap" id="amar-wrap" onclick="toggleAmar()">
                    <input type="checkbox" id="amar-cb">
                    <span id="amar-label">نیاز به آمارگیری دارد</span>
                </label>
            </div>
            <div class="field" style="flex:0 0 auto;">
                <label>&nbsp;</label>
                <button class="btn btn-primary" onclick="addItem()">
                    <span id="add-txt">✅ ثبت بخش</span>
                    <span id="add-load" style="display:none;">⏳</span>
                </button>
            </div>
        </div>
    </div>

    <!-- لیست -->
    <div class="card">
        <div class="card-title">📋 لیست بخش‌های تعریف شده <span class="count" id="total-count">۰</span></div>
        <div id="list-container">
            <div class="empty">در حال بارگذاری...</div>
        </div>
    </div>
</div>

<script>
    const GROUP_OPTIONS = ''' + json.dumps(GROUP_OPTIONS, ensure_ascii=False) + ''';
    let editingId = null;
    let delTarget = null;

    function toast(msg, type) {
        const box = document.getElementById('toast-box');
        const t = document.createElement('div');
        t.className = 'toast ' + (type==='ok'?'ok':'err');
        t.innerHTML = `<span>${type==='ok'?'✅':'❌'}</span><span>${msg}</span><span class="close" onclick="this.parentElement.remove()">✕</span>`;
        box.appendChild(t);
        setTimeout(() => { if(t.parentElement) t.remove(); }, 3500);
    }

    function closeModal() {
        document.getElementById('del-modal').classList.remove('show');
        delTarget = null;
    }

    function toggleAmar() {
        const cb = document.getElementById('amar-cb');
        const wrap = document.getElementById('amar-wrap');
        const label = document.getElementById('amar-label');
        cb.checked = !cb.checked;
        if (cb.checked) {
            wrap.classList.add('checked');
            label.textContent = 'نیاز به آمارگیری دارد';
        } else {
            wrap.classList.remove('checked');
            label.textContent = 'بدون نیاز به آمارگیری';
        }
    }

    function groupDropdown(selected) {
        let opts = '<option value="">-- انتخاب --</option>';
        GROUP_OPTIONS.forEach(g => {
            opts += `<option value="${g}" ${g === selected ? 'selected' : ''}>${g}</option>`;
        });
        return opts;
    }

    async function loadList() {
        try {
            const r = await fetch('/module/admin/wards/list');
            const d = await r.json();
            const container = document.getElementById('list-container');
            document.getElementById('total-count').textContent = d.items.length;

            if (!d.items.length) {
                container.innerHTML = '<div class="empty">هنوز بخشی تعریف نشده است</div>';
                return;
            }

            let html = '';
            d.items.forEach(item => {
                const isEdit = editingId == item.ID_nam_bakhsh;
                const amarBadge = item.amar == 1
                    ? '<span class="badge-amar yes">📊 آمار</span>'
                    : '<span class="badge-amar no">بدون آمار</span>';
                const groupBadge = item.grop ? `<span class="badge-group">📁 ${item.grop}</span>` : '';

                html += `<div class="list-item ${isEdit ? 'editing' : ''}" id="row-${item.ID_nam_bakhsh}">
                    <span class="item-id">#${item.ID_nam_bakhsh}</span>
                    <input type="text" class="item-name" id="inp-${item.ID_nam_bakhsh}"
                           value="${item.nam_bakhsh.replace(/"/g, '&quot;')}"
                           ${!isEdit ? 'readonly' : ''}
                           onkeydown="if(event.key==='Enter' && ${isEdit}) saveEdit(${item.ID_nam_bakhsh})">
                    ${groupBadge}
                    ${amarBadge}
                    <div class="item-actions">
                        ${isEdit ? `
                            <select id="edit-group-${item.ID_nam_bakhsh}" style="padding:4px 6px;font-size:11px;border-radius:4px;border:1px solid #cbd5e1;">
                                ${groupDropdown(item.grop || '')}
                            </select>
                            <label style="display:flex;align-items:center;gap:4px;font-size:11px;margin-left:5px;">
                                <input type="checkbox" id="edit-amar-${item.ID_nam_bakhsh}" ${item.amar == 1 ? 'checked' : ''}> آمار
                            </label>
                            <button class="btn btn-save btn-xs" onclick="saveEdit(${item.ID_nam_bakhsh})">💾</button>
                            <button class="btn btn-cancel btn-xs" onclick="cancelEdit()">✕</button>
                        ` : `
                            <button class="btn btn-edit btn-xs" onclick="startEdit(${item.ID_nam_bakhsh})">📝</button>
                            <button class="btn btn-del btn-xs" onclick="askDel(${item.ID_nam_bakhsh}, '${item.nam_bakhsh.replace(/'/g, "\\'")}')">🗑️</button>
                        `}
                    </div>
                </div>`;
            });
            container.innerHTML = html;

            if (editingId) {
                const inp = document.getElementById('inp-' + editingId);
                if (inp) { inp.focus(); inp.select(); }
            }
        } catch(e) { console.error(e); }
    }

    async function addItem() {
        const name = document.getElementById('new-name').value.trim();
        const group = document.getElementById('new-group').value;
        if (!name) { toast('لطفاً نام بخش را وارد کنید', 'err'); return; }
        const isAmar = document.getElementById('amar-cb').checked ? '1' : '0';

        document.getElementById('add-txt').style.display = 'none';
        document.getElementById('add-load').style.display = 'inline';

        try {
            const fd = new FormData();
            fd.append('name', name);
            fd.append('amar', isAmar);
            fd.append('grop', group);
            const r = await fetch('/module/admin/wards/save', { method:'POST', body:fd });
            const d = await r.json();
            if (d.success) {
                toast(d.message, 'ok');
                document.getElementById('new-name').value = '';
                document.getElementById('new-group').value = '';
                document.getElementById('amar-cb').checked = false;
                document.getElementById('amar-wrap').classList.remove('checked');
                document.getElementById('amar-label').textContent = 'نیاز به آمارگیری دارد';
                loadList();
            } else {
                toast(d.message, 'err');
            }
        } catch(e) { toast('خطا در ارتباط', 'err'); }
        finally {
            document.getElementById('add-txt').style.display = 'inline';
            document.getElementById('add-load').style.display = 'none';
        }
    }

    function startEdit(id) {
        if (editingId && editingId != id) cancelEdit();
        editingId = id;
        loadList();
    }

    function cancelEdit() {
        editingId = null;
        loadList();
    }

    async function saveEdit(id) {
        const inp = document.getElementById('inp-' + id);
        const name = inp.value.trim();
        if (!name) { toast('نام نمی‌تواند خالی باشد', 'err'); inp.focus(); return; }

        const groupSel = document.getElementById('edit-group-' + id);
        const group = groupSel ? groupSel.value : '';
        const amarCb = document.getElementById('edit-amar-' + id);
        const isAmar = amarCb && amarCb.checked ? '1' : '0';

        try {
            const fd = new FormData();
            fd.append('id', id);
            fd.append('name', name);
            fd.append('amar', isAmar);
            fd.append('grop', group);
            const r = await fetch('/module/admin/wards/update', { method:'POST', body:fd });
            const d = await r.json();
            if (d.success) {
                toast(d.message, 'ok');
                editingId = null;
                loadList();
            } else {
                toast(d.message, 'err');
            }
        } catch(e) { toast('خطا در ارتباط', 'err'); }
    }

    function askDel(id, name) {
        delTarget = id;
        document.getElementById('del-msg').textContent = `آیا از حذف بخش "${name}" اطمینان دارید؟`;
        document.getElementById('del-modal').classList.add('show');
    }

    async function confirmDelete() {
        if (!delTarget) return;
        try {
            const fd = new FormData();
            fd.append('id', delTarget);
            const r = await fetch('/module/admin/wards/delete', { method:'POST', body:fd });
            const d = await r.json();
            if (d.success) {
                toast(d.message, 'ok');
                if (editingId == delTarget) editingId = null;
                loadList();
            } else {
                toast(d.message, 'err');
            }
        } catch(e) { toast('خطا در ارتباط', 'err'); }
        closeModal();
    }

    document.addEventListener('DOMContentLoaded', loadList);
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (delTarget) closeModal();
            if (editingId) cancelEdit();
        }
    });
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions
# ==========================================

def get_list():
    """دریافت لیست بخش‌ها"""
    try:
        items = query(
            "SELECT ID_nam_bakhsh, nam_bakhsh, amar, grop FROM tbl_bakhsh ORDER BY ID_nam_bakhsh DESC",
            fetch_all=True
        ) or []
        return {'success': True, 'items': items}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def save_item(user, form_data):
    user_id = user.get('UserID', 0)
    name = form_data.get('name', '').strip()
    amar = form_data.get('amar', '0')
    grop = form_data.get('grop', '').strip() or None  # ذخیره NULL در صورت خالی
    if not name:
        return {'success': False, 'message': 'لطفاً نام بخش را وارد کنید'}
    amar_val = 1 if amar == '1' else 0
    try:
        existing = query(
            "SELECT ID_nam_bakhsh FROM tbl_bakhsh WHERE nam_bakhsh = %s",
            params=(name,), fetch_one=True
        )
        if existing:
            return {'success': False, 'message': 'این نام بخش قبلاً ثبت شده است'}
        from jdatetime import date as jdate
        from datetime import datetime
        d_sh = int(jdate.today().strftime("%Y%m%d"))
        query(
            "INSERT INTO tbl_bakhsh (nam_bakhsh, dat_sabt, UserID, zaman_sabt, amar, grop) VALUES (%s, %s, 1, %s, %s, %s)",
            params=(name, d_sh, datetime.now(), amar_val, grop), commit=True
        )
        new_id = query("SELECT MAX(ID_nam_bakhsh) as max_id FROM tbl_bakhsh", fetch_one=True)['max_id']
        log_crud('save_ward', user_id, key_value=new_id,
                 new_value=json.dumps({"name": name, "amar": amar_val, "grop": grop}, ensure_ascii=False))
        return {'success': True, 'message': f'بخش "{name}" با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def update_item(user, form_data):
    user_id = user.get('UserID', 0)
    item_id = form_data.get('id')
    name = form_data.get('name', '').strip()
    amar = form_data.get('amar', '0')
    grop = form_data.get('grop', '').strip() or None
    if not item_id:
        return {'success': False, 'message': 'شناسه نامعتبر است'}
    if not name:
        return {'success': False, 'message': 'نام نمی‌تواند خالی باشد'}
    amar_val = 1 if amar == '1' else 0
    try:
        existing = query(
            "SELECT ID_nam_bakhsh FROM tbl_bakhsh WHERE nam_bakhsh = %s AND ID_nam_bakhsh != %s",
            params=(name, item_id), fetch_one=True
        )
        if existing:
            return {'success': False, 'message': 'این نام بخش قبلاً ثبت شده است'}

        old_record = query("SELECT * FROM tbl_bakhsh WHERE ID_nam_bakhsh = %s", (item_id,), fetch_one=True)
        query(
            "UPDATE tbl_bakhsh SET nam_bakhsh = %s, amar = %s, grop = %s WHERE ID_nam_bakhsh = %s",
            params=(name, amar_val, grop, item_id), commit=True
        )
        log_crud('update_ward', user_id, key_value=item_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str),
                 new_value=json.dumps({"name": name, "amar": amar_val, "grop": grop}, ensure_ascii=False))
        return {'success': True, 'message': 'تغییرات با موفقیت اعمال شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def delete_item(user, form_data):
    user_id = user.get('UserID', 0)
    item_id = form_data.get('id')
    if not item_id:
        return {'success': False, 'message': 'شناسه نامعتبر است'}
    try:
        used = query(
            "SELECT COUNT(*) as cnt FROM tbl_amliat_kod WHERE nam_bakhsh = %s",
            params=(item_id,), fetch_one=True
        )
        if used and used['cnt'] > 0:
            return {'success': False, 'message': f'این بخش در {used["cnt"]} عملیات استفاده شده و قابل حذف نیست'}

        old_record = query("SELECT * FROM tbl_bakhsh WHERE ID_nam_bakhsh = %s", (item_id,), fetch_one=True)
        query("DELETE FROM tbl_bakhsh WHERE ID_nam_bakhsh = %s", params=(item_id,), commit=True)
        log_crud('delete_ward', user_id, key_value=item_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str))
        return {'success': True, 'message': 'بخش با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}
        

        