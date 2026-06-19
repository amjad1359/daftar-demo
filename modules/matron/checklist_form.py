"""
تنظیمات چک‌لیست ارزیابی – مترون
نسخه Flask با AJAX، Toast و مدیریت گروه‌ها و سنجه‌ها
"""

import jdatetime
from datetime import datetime
from models.database import query, get_connection
import json
from utils.auto_log import log_crud

def get_checklist_form(user):
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    # ========== لیست گروه‌های ارزیابی ==========
    titles = query("SELECT ID_onvan_arziabi, nom_onvan FROM tbl_arzibi_onvan ORDER BY nom_onvan", fetch_all=True) or []
    title_options = '<option value="">--- انتخاب گروه ---</option>'
    for t in titles:
        title_options += f'<option value="{t["ID_onvan_arziabi"]}">{t["nom_onvan"]}</option>'

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
    .checklist-header {{
        background:linear-gradient(135deg, #6366f1, #8b5cf6); color:white; border-radius:16px; padding:25px 30px;
        margin-bottom:25px; display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(99,102,241,0.25);
    }}
    .checklist-header h2 {{ font-size:24px; }}
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
    .form-select, .form-input, .form-textarea {{
        width:100%; padding:12px 14px; border:2px solid var(--border); border-radius:8px;
        font-size:14px; font-family:inherit; transition:var(--transition); background:var(--white);
    }}
    .form-select:focus, .form-input:focus, .form-textarea:focus {{ border-color:var(--primary-light); outline:none; box-shadow:0 0 0 3px rgba(59,130,246,0.15); }}
    .form-textarea {{ min-height:80px; resize:vertical; }}

    .btn {{ display:inline-flex; align-items:center; justify-content:center; gap:6px; padding:10px 20px; border:none; border-radius:8px; font-size:14px; font-weight:600; cursor:pointer; font-family:inherit; transition:var(--transition); text-decoration:none; }}
    .btn-primary {{ background:var(--primary); color:white; }} .btn-primary:hover {{ background:var(--primary-light); }}
    .btn-success {{ background:var(--success); color:white; }} .btn-danger {{ background:var(--danger); color:white; }}
    .btn-sm {{ padding:6px 12px; font-size:12px; }} .btn-xs {{ padding:4px 8px; font-size:11px; }}

    /* کارت سنجه‌ها */
    .item-card {{
        background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:15px;
        margin-bottom:10px; transition:var(--transition);
    }}
    .item-card:hover {{ border-color:var(--primary-light); }}
    .item-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }}
    .item-name {{ font-weight:bold; color:var(--dark); }}
    .item-code {{ font-size:12px; color:var(--gray); }}
    .edit-panel {{ display:none; margin-top:15px; padding-top:15px; border-top:1px dashed var(--border); }}
    .edit-panel.show {{ display:block; }}

    .toast-container {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:10px; pointer-events:none; }}
    .toast {{ display:flex; align-items:center; gap:12px; padding:14px 22px; border-radius:12px; color:white; font-weight:600; box-shadow:0 10px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }} .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}

    /* مودال افزودن گروه */
    .modal-overlay {{ display:none; position:fixed; top:0;left:0;right:0;bottom:0; background:rgba(0,0,0,0.5); z-index:1000; justify-content:center; align-items:center; }}
    .modal-overlay.show {{ display:flex; }}
    .modal {{ background:white; border-radius:12px; padding:25px; width:90%; max-width:450px; box-shadow:0 10px 40px rgba(0,0,0,0.3); }}
    .modal h3 {{ margin-bottom:15px; }}
    .modal .row {{ margin-top:15px; }}

    @media (max-width:768px) {{
        .checklist-header {{ flex-direction:column; gap:15px; text-align:center; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>

<!-- مودال افزودن گروه جدید -->
<div class="modal-overlay" id="new-title-modal">
    <div class="modal">
        <h3>➕ تعریف گروه ارزیابی جدید</h3>
        <input type="text" id="new-title-input" class="form-input" placeholder="نام گروه ارزیابی...">
        <div class="row">
            <button class="btn btn-primary" onclick="addNewTitle()">💾 ذخیره</button>
            <button class="btn btn-sm" onclick="closeModal()">انصراف</button>
        </div>
    </div>
</div>

<div class="container fade-in">
    <div class="checklist-header">
        <h2>⚙️ مدیریت و پیکربندی چک‌لیست‌های ارزیابی</h2>
        <a href="/module/matron" class="back-btn">⬅️ بازگشت</a>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="switchTab('tab-new')">➕ تعریف سنجه جدید</button>
        <button class="tab" onclick="switchTab('tab-list')">📋 ویرایش و مدیریت لیست</button>
    </div>

    <!-- تب اول: ثبت سنجه جدید -->
    <div id="tab-new" class="tab-content active">
        <div class="card">
            <div class="row" style="margin-bottom:15px;">
                <select id="new-title-select" class="form-select" style="flex:1;" onchange="onTitleChange()">
                    {title_options}
                </select>
                <button class="btn btn-primary btn-sm" onclick="openModal()">➕ گروه جدید</button>
            </div>
            <div class="row">
                <div class="form-group" style="flex:4;">
                    <label>نام سنجه (سوال)</label>
                    <input type="text" id="new-item-name" class="form-input" placeholder="نام سنجه...">
                </div>
                <div class="form-group" style="flex:1;">
                    <label>آدرس سنجه (کد)</label>
                    <input type="text" id="new-item-addr" class="form-input" placeholder="کد...">
                </div>
            </div>
            <div class="row">
                <div class="form-group" style="flex:1;">
                    <label>حداکثر امتیاز</label>
                    <input type="number" id="new-item-score" class="form-input" value="1" step="0.25" min="0">
                </div>
                <div class="form-group" style="flex:1;">
                    <label>سطح</label>
                    <input type="text" id="new-item-level" class="form-input" value="1">
                </div>
                <div class="form-group" style="flex:1;">
                    <label>وزن سنجه</label>
                    <input type="number" id="new-item-weight" class="form-input" value="1" step="0.1" min="0">
                </div>
                <div class="form-group" style="flex:1;">
                    <label>وضعیت ایمنی</label>
                    <select id="new-item-safety" class="form-select">
                        <option value="0">ندارد</option>
                        <option value="1">دارد</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>متن راهنمای ارزیابی</label>
                <textarea id="new-item-guide" class="form-textarea" rows="2" placeholder="توضیح برای سوپروایزر..."></textarea>
            </div>
            <button class="btn btn-primary" onclick="saveNewItem()">
                <span id="save-new-text">💾 ذخیره نهایی سنجه</span>
                <span id="save-new-loading" style="display:none;">⏳ ...</span>
            </button>
        </div>
    </div>

    <!-- تب دوم: ویرایش و مدیریت لیست -->
    <div id="tab-list" class="tab-content">
        <div class="card">
            <div class="row" style="margin-bottom:15px;">
                <select id="edit-title-select" class="form-select" style="flex:1;" onchange="loadItems()">
                    {title_options}
                </select>
            </div>
            <div id="items-count" style="margin-bottom:10px; color:var(--gray);"></div>
            <div id="items-container"></div>
        </div>
    </div>
</div>

<script>
    function switchTab(tab) {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        if (tab === 'tab-new') {{
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.getElementById('tab-new').classList.add('active');
        }} else {{
            document.querySelectorAll('.tab')[1].classList.add('active');
            document.getElementById('tab-list').classList.add('active');
            loadItems();
        }}
    }}

    function showToast(msg, type) {{
        const c = document.getElementById('toast-container'), t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span><span style="cursor:pointer;margin-right:auto;" onclick="this.parentElement.remove()">✕</span>';
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    // ==================== مودال گروه جدید ====================
    function openModal() {{
        document.getElementById('new-title-modal').classList.add('show');
        document.getElementById('new-title-input').value = '';
        document.getElementById('new-title-input').focus();
    }}
    function closeModal() {{ document.getElementById('new-title-modal').classList.remove('show'); }}

    async function addNewTitle() {{
        const title = document.getElementById('new-title-input').value.trim();
        if (!title) {{ showToast('نام گروه الزامی است', 'error'); return; }}
        try {{
            const formData = new FormData();
            formData.append('title', title);
            const res = await fetch('/module/matron/checklist/add_title', {{ method:'POST', body: formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ گروه جدید ثبت شد', 'success');
                closeModal();
                // بروزرسانی dropdownها
                const newOption = '<option value="' + data.id + '" selected>' + data.title + '</option>';
                document.getElementById('new-title-select').innerHTML += newOption;
                document.getElementById('edit-title-select').innerHTML += newOption;
                document.getElementById('new-title-select').value = data.id;
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    // ==================== تب اول: ثبت سنجه جدید ====================
    async function saveNewItem() {{
        const titleId = document.getElementById('new-title-select').value;
        const name = document.getElementById('new-item-name').value.trim();
        if (!titleId) {{ showToast('گروه ارزیابی را انتخاب کنید', 'error'); return; }}
        if (!name) {{ showToast('نام سنجه الزامی است', 'error'); return; }}

        const formData = new FormData();
        formData.append('title_id', titleId);
        formData.append('name', name);
        formData.append('address', document.getElementById('new-item-addr').value);
        formData.append('score', document.getElementById('new-item-score').value);
        formData.append('level', document.getElementById('new-item-level').value);
        formData.append('weight', document.getElementById('new-item-weight').value);
        formData.append('safety', document.getElementById('new-item-safety').value);
        formData.append('guide', document.getElementById('new-item-guide').value);

        document.getElementById('save-new-text').style.display = 'none';
        document.getElementById('save-new-loading').style.display = 'inline';
        try {{
            const res = await fetch('/module/matron/checklist/save_item', {{ method:'POST', body: formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ سنجه با موفقیت ثبت شد', 'success');
                document.getElementById('new-item-name').value = '';
                document.getElementById('new-item-addr').value = '';
                document.getElementById('new-item-guide').value = '';
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
        finally {{
            document.getElementById('save-new-text').style.display = 'inline';
            document.getElementById('save-new-loading').style.display = 'none';
        }}
    }}

    // ==================== تب دوم: ویرایش لیست ====================
    async function loadItems() {{
        const titleId = document.getElementById('edit-title-select').value;
        if (!titleId) {{ document.getElementById('items-container').innerHTML = ''; return; }}
        try {{
            const res = await fetch('/module/matron/checklist/items/' + titleId);
            const data = await res.json();
            if (data.success) {{
                document.getElementById('items-count').innerText = 'تعداد سنجه‌ها: ' + data.items.length;
                renderItems(data.items);
            }}
        }} catch(e) {{ console.error(e); }}
    }}

    function renderItems(items) {{
        const container = document.getElementById('items-container');
        if (!items.length) {{ container.innerHTML = '<p style="color:var(--light-gray);">سنجه‌ای تعریف نشده است</p>'; return; }}
        let html = '';
        items.forEach(item => {{
            html += '<div class="item-card">' +
                '<div class="item-header">' +
                    '<span class="item-name">📌 ' + item.nam_item + ' (کد: ' + (item.adres_sanjeh || '-') + ')</span>' +
                    '<button class="btn btn-primary btn-xs" onclick="toggleEdit(' + item.ID_cheklist + ')">✏️ ویرایش</button>' +
                '</div>' +
                '<div class="edit-panel" id="edit-panel-' + item.ID_cheklist + '">' +
                    '<div class="row">' +
                        '<div class="form-group" style="flex:4;"><label>نام سنجه</label><input type="text" id="e-name-' + item.ID_cheklist + '" class="form-input" value="' + (item.nam_item || '') + '"></div>' +
                        '<div class="form-group" style="flex:1;"><label>آدرس/کد</label><input type="text" id="e-addr-' + item.ID_cheklist + '" class="form-input" value="' + (item.adres_sanjeh || '') + '"></div>' +
                    '</div>' +
                    '<div class="row">' +
                        '<div class="form-group" style="flex:1;"><label>حداکثر امتیاز</label><input type="number" id="e-score-' + item.ID_cheklist + '" class="form-input" value="' + item.nomreh + '" step="0.25"></div>' +
                        '<div class="form-group" style="flex:1;"><label>سطح</label><input type="text" id="e-level-' + item.ID_cheklist + '" class="form-input" value="' + (item.sath || '1') + '"></div>' +
                        '<div class="form-group" style="flex:1;"><label>وزن</label><input type="number" id="e-weight-' + item.ID_cheklist + '" class="form-input" value="' + item.vazn_sanjeh + '" step="0.1"></div>' +
                        '<div class="form-group" style="flex:1;"><label>ایمنی</label><select id="e-safety-' + item.ID_cheklist + '" class="form-select">' +
                            '<option value="0" ' + (item.imani_chek == 0 ? 'selected' : '') + '>ندارد</option>' +
                            '<option value="1" ' + (item.imani_chek == 1 ? 'selected' : '') + '>دارد</option>' +
                        '</select></div>' +
                    '</div>' +
                    '<div class="form-group"><label>راهنما</label><textarea id="e-guide-' + item.ID_cheklist + '" class="form-textarea" rows="2">' + (item.rahnamii || '') + '</textarea></div>' +
                    '<button class="btn btn-success btn-sm" onclick="updateItem(' + item.ID_cheklist + ')">💾 ذخیره تغییرات</button>' +
                '</div>' +
            '</div>';
        }});
        container.innerHTML = html;
    }}

    function toggleEdit(id) {{
        const panel = document.getElementById('edit-panel-' + id);
        panel.classList.toggle('show');
    }}

    async function updateItem(itemId) {{
        const formData = new FormData();
        formData.append('item_id', itemId);
        formData.append('name', document.getElementById('e-name-' + itemId).value);
        formData.append('address', document.getElementById('e-addr-' + itemId).value);
        formData.append('score', document.getElementById('e-score-' + itemId).value);
        formData.append('level', document.getElementById('e-level-' + itemId).value);
        formData.append('weight', document.getElementById('e-weight-' + itemId).value);
        formData.append('safety', document.getElementById('e-safety-' + itemId).value);
        formData.append('guide', document.getElementById('e-guide-' + itemId).value);

        try {{
            const res = await fetch('/module/matron/checklist/update_item', {{ method:'POST', body: formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ تغییرات ذخیره شد', 'success');
                loadItems();
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}
</script>
</body>
</html>'''
    return html


# ==================== API Functions ====================

def add_title_api(user, title):
    if not title or not title.strip():
        return {'success': False, 'message': 'نام گروه الزامی است'}
    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()
    user_id = user.get('UserID', 0)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tbl_arzibi_onvan (nom_onvan, dat_sabt, UserID, zaman_sabt)
            VALUES (%s, %s, %s, %s)
        """, (title.strip(), today, user_id, now))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        log_crud('add_title_api', user_id, key_value=new_id,
                 new_value=json.dumps({"title": title.strip()}, ensure_ascii=False))               
        return {'success': True, 'id': new_id, 'title': title.strip()}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def save_item_api(user, form_data):
    title_id = form_data.get('title_id')
    name = form_data.get('name', '').strip()
    address = form_data.get('address', '').strip()
    score = float(form_data.get('score', 1))
    level = form_data.get('level', '1')
    weight = float(form_data.get('weight', 1))
    safety = int(form_data.get('safety', 0))
    guide = form_data.get('guide', '').strip()
    kole = round(score * weight, 2)
    if not name:
        return {'success': False, 'message': 'نام سنجه الزامی است'}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = int(jdatetime.date.today().strftime("%Y%m%d"))
        now = datetime.now()
        user_id = user.get('UserID', 0)
        cursor.execute("""
            INSERT INTO tbl_arziabi_cheklist
            (id_onvan_arziabi, nam_item, nomreh, rahnamii, sath, vazn_sanjeh,
             imani_chek, adres_sanjeh, kole_emtiaz, dat_sabt, UserID, zaman_sabt)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (title_id, name, score, guide, level, weight, safety, address, kole, today, user_id, now))
        conn.commit()
        conn.close()
        log_crud('save_item_api', user_id, key_value=cursor.lastrowid,
                 new_value=json.dumps({
                     'title_id': title_id,
                     'name': name,
                     'score': score,
                     'level': level,
                     'weight': weight,
                     'safety': safety,
                     'guide': guide
                 }, ensure_ascii=False))
      
        return {'success': True, 'message': 'سنجه با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def get_items_api(title_id):
    items = query("""
        SELECT ID_cheklist, nam_item, nomreh, rahnamii, sath, vazn_sanjeh,
               imani_chek, adres_sanjeh
        FROM tbl_arziabi_cheklist
        WHERE id_onvan_arziabi = %s
        ORDER BY sath, ID_cheklist
    """, (title_id,), fetch_all=True) or []
    return {'success': True, 'items': items}


def update_item_api(user, form_data):
    user_id = user.get('UserID', 0)
    item_id = form_data.get('item_id')
    name = form_data.get('name', '').strip()
    address = form_data.get('address', '').strip()
    score = float(form_data.get('score', 1))
    level = form_data.get('level', '1')
    weight = float(form_data.get('weight', 1))
    safety = int(form_data.get('safety', 0))
    guide = form_data.get('guide', '').strip()
    kole = round(score * weight, 2)
    if not name:
        return {'success': False, 'message': 'نام سنجه الزامی است'}
    try:
        query("""
            UPDATE tbl_arziabi_cheklist SET
                nam_item=%s, nomreh=%s, rahnamii=%s, sath=%s, vazn_sanjeh=%s,
                imani_chek=%s, adres_sanjeh=%s, kole_emtiaz=%s
            WHERE ID_cheklist=%s
        """, (name, score, guide, level, weight, safety, address, kole, item_id), commit=True)
        

        old_record = query(
            "SELECT * FROM tbl_arziabi_cheklist WHERE ID_cheklist = %s",
            (item_id,), fetch_one=True
        )
        query("""UPDATE tbl_arziabi_cheklist ... """, (...), commit=True)
        
        log_crud('update_item_api', user_id, key_value=item_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str),
                 new_value=json.dumps({
                     'name': name, 'score': score, 'level': level,
                     'weight': weight, 'safety': safety, 'guide': guide,
                     'address': address
                 }, ensure_ascii=False, default=str))
        return {'success': True, 'message': 'تغییرات ذخیره شد'}       

    except Exception as e:
        return {'success': False, 'message': str(e)}