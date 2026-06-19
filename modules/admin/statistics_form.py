"""
تنظیمات آمار – ادمین (نسخه کامل با نوع آیتم جریانی/موجودی)
مدیریت آیتم‌های آماری و تخصیص به بخش‌ها
"""

from models.database import query, get_connection
import json
from utils.auto_log import log_crud

def get_statistics_form(user):
    """صفحه اصلی تنظیمات آمار"""

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
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:1400px; margin:0 auto; padding:20px; }}

    .stats-header {{
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color:white; border-radius:16px; padding:25px 30px; margin-bottom:25px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(37,99,235,0.25);
    }}
    .stats-header h2 {{ font-size:24px; margin:0; }}
    .stats-header p {{ opacity:0.85; font-size:13px; margin:5px 0 0 0; }}
    .back-btn {{
        color:white; text-decoration:none; padding:8px 16px;
        border:1px solid rgba(255,255,255,0.4); border-radius:8px;
        font-size:13px; transition:var(--transition);
    }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    .tabs {{
        display:flex; gap:5px; margin-bottom:25px;
        border-bottom:2px solid var(--border); flex-wrap:wrap;
    }}
    .tab {{
        padding:14px 28px; font-size:14px; font-weight:600; border:none;
        background:none; color:var(--light-gray); cursor:pointer;
        border-bottom:2px solid transparent; transition:var(--transition);
        font-family:inherit; white-space:nowrap;
    }}
    .tab:hover {{ color:var(--dark); }}
    .tab.active {{ color:var(--primary-light); border-bottom-color:var(--primary-light); }}
    .tab-content {{ display:none; animation:fadeIn 0.3s ease; }}
    .tab-content.active {{ display:block; }}

    .card {{
        background:var(--white); border-radius:var(--radius); padding:25px;
        border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05);
        margin-bottom:25px;
    }}
    .card-header {{
        display:flex; justify-content:space-between; align-items:center;
        margin-bottom:20px; padding-bottom:15px; border-bottom:2px solid var(--border);
    }}
    .card-header h3 {{ font-size:18px; color:var(--dark); margin:0; display:flex; align-items:center; gap:8px; }}
    .card-header .badge {{
        background:var(--primary); color:white; font-size:12px;
        padding:4px 12px; border-radius:15px; font-weight:normal;
    }}

    .form-row {{ display:flex; gap:12px; align-items:flex-end; flex-wrap:wrap; margin-bottom:20px; }}
    .form-group {{ flex:1; min-width:150px; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:6px; }}
    .form-input, .form-select {{
        width:100%; padding:12px 14px; border:2px solid var(--border);
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
        padding:12px 20px; border:none; border-radius:8px; font-size:14px;
        font-weight:600; cursor:pointer; font-family:inherit;
        transition:var(--transition); text-decoration:none; white-space:nowrap;
    }}
    .btn-primary {{ background:var(--primary); color:white; }}
    .btn-primary:hover {{ background:var(--primary-light); transform:translateY(-1px); box-shadow:0 4px 12px rgba(37,99,235,0.3); }}
    .btn-success {{ background:var(--success); color:white; }}
    .btn-success:hover {{ background:#059669; }}
    .btn-danger {{ background:var(--danger); color:white; }}
    .btn-danger:hover {{ background:#dc2626; }}
    .btn-outline {{
        background:white; color:var(--primary-light); border:2px solid var(--primary-light);
    }}
    .btn-outline:hover {{ background:var(--primary-light); color:white; }}
    .btn-sm {{ padding:8px 14px; font-size:12px; }}
    .btn-xs {{ padding:5px 10px; font-size:11px; border-radius:6px; }}

    .item-list {{ display:flex; flex-direction:column; gap:8px; }}
    .item-row {{
        display:flex; align-items:center; gap:12px; padding:14px 18px;
        background:var(--bg); border:1px solid var(--border); border-radius:10px;
        transition:var(--transition);
    }}
    .item-row:hover {{ border-color:var(--primary-light); box-shadow:0 2px 8px rgba(0,0,0,0.05); }}
    .item-row .item-info {{ flex:1; display:flex; align-items:center; gap:12px; }}
    .item-row .item-name {{ font-weight:600; color:var(--dark); }}
    .item-row .item-unit {{
        font-size:12px; background:#dbeafe; color:var(--primary);
        padding:2px 10px; border-radius:12px;
    }}
    .item-row .item-type {{
        font-size:12px; padding:2px 10px; border-radius:12px;
    }}
    .item-type-flow {{ background:#d1fae5; color:#065f46; }}
    .item-type-inventory {{ background:#fee2e2; color:#991b1b; }}
    .item-row.editing {{
        border-color:var(--warning); background:#fffbeb;
        box-shadow:0 0 0 3px rgba(245,158,11,0.15);
    }}

    .dept-group {{
        border:1px solid var(--border); border-radius:10px;
        margin-bottom:15px; overflow:hidden;
    }}
    .dept-header {{
        background:var(--bg); padding:14px 18px; font-weight:bold;
        color:var(--dark); display:flex; justify-content:space-between;
        align-items:center; cursor:pointer; transition:var(--transition);
    }}
    .dept-header:hover {{ background:#e2e8f0; }}
    .dept-header .dept-count {{
        font-size:12px; color:var(--gray); font-weight:normal;
    }}
    .dept-body {{ padding:15px 18px; }}
    .config-item {{
        display:flex; align-items:center; justify-content:space-between;
        padding:10px 14px; margin-bottom:6px; background:var(--bg);
        border-radius:8px; transition:var(--transition);
    }}
    .config-item:hover {{ background:#e2e8f0; }}
    .config-item .config-name {{ font-size:14px; color:var(--dark); }}
    .config-item .config-unit {{
        font-size:11px; color:var(--gray); margin-right:8px;
    }}

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

    @media (max-width:768px) {{
        .stats-header {{ flex-direction:column; gap:15px; text-align:center; }}
        .form-row {{ flex-direction:column; }}
        .form-group {{ min-width:100%; }}
        .tabs {{ overflow-x:auto; }}
        .tab {{ padding:10px 18px; font-size:13px; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="stats-header">
        <div>
            <h2>📊 مدیریت هوشمند پیکربندی آمار</h2>
            <p>تعریف آیتم‌های آماری و تخصیص به بخش‌ها</p>
        </div>
        <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="switchTab('items')">✨ مدیریت آیتم‌های پایه</button>
        <button class="tab" onclick="switchTab('config')">🛠️ تخصیص آیتم به بخش‌ها</button>
    </div>

    <!-- تب ۱: مدیریت آیتم‌های پایه -->
    <div id="tab-items" class="tab-content active">
        <div class="card">
            <div class="card-header">
                <h3><span>📝</span> ثبت / ویرایش آیتم</h3>
                <span class="badge" id="edit-badge" style="display:none;">✏️ در حال ویرایش</span>
            </div>
            <div class="form-row">
                <div class="form-group" style="flex:2;">
                    <label>نام آیتم</label>
                    <input type="text" id="item-name" class="form-input" placeholder="مثلاً: تعداد سزارین">
                </div>
                <div class="form-group" style="flex:1;">
                    <label>واحد</label>
                    <input type="text" id="item-unit" class="form-input" placeholder="مثلاً: مورد">
                </div>
                <div class="form-group" style="flex:1;">
                    <label>نوع آیتم</label>
                    <select id="item-type" class="form-select">
                        <option value="0">📊 جریانی (پذیرش، ترخیص)</option>
                        <option value="1">⚠️ موجودی (بستری، تخت)</option>
                    </select>
                </div>
                <div class="form-group" style="flex:0 0 auto;">
                    <label>&nbsp;</label>
                    <button class="btn btn-primary" id="save-item-btn" onclick="saveItem()">
                        <span id="save-item-text">✅ ثبت جدید</span>
                        <span id="save-item-loading" style="display:none;">⏳ ...</span>
                    </button>
                </div>
                <div class="form-group" style="flex:0 0 auto;">
                    <label>&nbsp;</label>
                    <button class="btn btn-outline btn-sm" onclick="cancelEdit()" id="cancel-edit-btn" style="display:none;">
                        ❌ انصراف
                    </button>
                </div>
            </div>
            <input type="hidden" id="edit-item-id" value="">
        </div>

        <div class="card">
            <div class="card-header">
                <h3><span>📋</span> لیست آیتم‌های پایه</h3>
                <span class="badge" id="items-count">۰ آیتم</span>
            </div>
            <div class="item-list" id="items-list">
                <p style="text-align:center; color:var(--light-gray); padding:30px;">در حال بارگذاری...</p>
            </div>
        </div>
    </div>

    <!-- تب ۲: تخصیص آیتم به بخش‌ها -->
    <div id="tab-config" class="tab-content">
        <div class="card">
            <div class="card-header">
                <h3><span>➕</span> تخصیص آیتم جدید به بخش</h3>
            </div>
            <div class="form-row">
                <div class="form-group" style="flex:1;">
                    <label>انتخاب بخش</label>
                    <select id="config-dept" class="form-select">
                        <option value="">--- انتخاب بخش ---</option>
                    </select>
                </div>
                <div class="form-group" style="flex:1;">
                    <label>انتخاب آیتم</label>
                    <select id="config-item" class="form-select">
                        <option value="">--- انتخاب آیتم ---</option>
                    </select>
                </div>
                <div class="form-group" style="flex:0 0 auto;">
                    <label>&nbsp;</label>
                    <button class="btn btn-success" onclick="assignItem()">
                        <span id="assign-text">🔗 تایید اتصال</span>
                        <span id="assign-loading" style="display:none;">⏳ ...</span>
                    </button>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3><span>📂</span> پیکربندی بر اساس هر بخش</h3>
                <span class="badge" id="config-count">۰ پیکربندی</span>
            </div>
            <div id="config-list">
                <p style="text-align:center; color:var(--light-gray); padding:30px;">در حال بارگذاری...</p>
            </div>
        </div>
    </div>
</div>

<script>
    let editingItemId = null;

    function switchTab(tab) {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        if (tab === 'items') {{
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.getElementById('tab-items').classList.add('active');
            loadItems();
        }} else {{
            document.querySelectorAll('.tab')[1].classList.add('active');
            document.getElementById('tab-config').classList.add('active');
            loadConfigs();
        }}
    }}

    function showToast(msg, type) {{
        const c = document.getElementById('toast-container');
        const t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = `<span>${{type==='success'?'✅':'❌'}}</span><span>${{msg}}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    // ==================== تب ۱: مدیریت آیتم‌ها ====================
    async function loadItems() {{
        try {{
            const res = await fetch('/module/admin/statistics/items/list');
            const data = await res.json();
            const list = document.getElementById('items-list');
            document.getElementById('items-count').textContent = `${{data.items.length}} آیتم`;

            if (!data.items.length) {{
                list.innerHTML = '<p style="text-align:center; color:var(--light-gray); padding:30px;">هیچ آیتمی تعریف نشده است</p>';
                return;
            }}

            let html = '';
            data.items.forEach(item => {{
                const isEditing = editingItemId == item.ID_item;
                const typeLabel = item.is_inventory == 1 ? '⚠️ موجودی' : '📊 جریانی';
                const typeClass = item.is_inventory == 1 ? 'item-type-inventory' : 'item-type-flow';
                html += `<div class="item-row ${{isEditing ? 'editing' : ''}}" id="item-row-${{item.ID_item}}">
                    <div class="item-info">
                        <span class="item-name">${{item.item_name}}</span>
                        <span class="item-unit">${{item.unit}}</span>
                        <span class="item-type ${{typeClass}}">${{typeLabel}}</span>
                    </div>
                    <div style="display:flex; gap:6px;">
                        <button class="btn btn-outline btn-xs" onclick="editItem(${{item.ID_item}}, '${{item.item_name}}', '${{item.unit}}', ${{item.is_inventory}})">📝 ویرایش</button>
                        <button class="btn btn-danger btn-xs" onclick="deleteItem(${{item.ID_item}})">🗑️ حذف</button>
                    </div>
                </div>`;
            }});
            list.innerHTML = html;
        }} catch(e) {{ console.error(e); }}
    }}

    function editItem(id, name, unit, isInventory) {{
        editingItemId = id;
        document.getElementById('edit-item-id').value = id;
        document.getElementById('item-name').value = name;
        document.getElementById('item-unit').value = unit;
        document.getElementById('item-type').value = isInventory;
        document.getElementById('save-item-text').textContent = '💾 بروزرسانی';
        document.getElementById('edit-badge').style.display = 'inline';
        document.getElementById('cancel-edit-btn').style.display = 'inline-flex';
        document.getElementById('item-name').focus();
        loadItems();
    }}

    function cancelEdit() {{
        editingItemId = null;
        document.getElementById('edit-item-id').value = '';
        document.getElementById('item-name').value = '';
        document.getElementById('item-unit').value = '';
        document.getElementById('item-type').value = '0';
        document.getElementById('save-item-text').textContent = '✅ ثبت جدید';
        document.getElementById('edit-badge').style.display = 'none';
        document.getElementById('cancel-edit-btn').style.display = 'none';
        document.getElementById('item-name').classList.remove('error');
        document.getElementById('item-unit').classList.remove('error');
        loadItems();
    }}

    async function saveItem() {{
        const name = document.getElementById('item-name').value.trim();
        const unit = document.getElementById('item-unit').value.trim();
        const isInventory = document.getElementById('item-type').value;
        const itemId = document.getElementById('edit-item-id').value;

        let hasError = false;
        if (!name) {{
            document.getElementById('item-name').classList.add('error');
            hasError = true;
        }} else {{
            document.getElementById('item-name').classList.remove('error');
        }}
        if (!unit) {{
            document.getElementById('item-unit').classList.add('error');
            hasError = true;
        }} else {{
            document.getElementById('item-unit').classList.remove('error');
        }}
        if (hasError) {{
            showToast('⛔ لطفاً نام آیتم و واحد را وارد کنید', 'error');
            return;
        }}

        const saveText = document.getElementById('save-item-text');
        const saveLoading = document.getElementById('save-item-loading');
        saveText.style.display = 'none';
        saveLoading.style.display = 'inline';

        try {{
            const formData = new FormData();
            formData.append('item_name', name);
            formData.append('item_unit', unit);
            formData.append('is_inventory', isInventory);
            if (itemId) formData.append('item_id', itemId);

            const res = await fetch('/module/admin/statistics/items/save', {{ method:'POST', body:formData }});
            const data = await res.json();

            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                cancelEdit();
                loadItems();
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

    async function deleteItem(id) {{
        if (!confirm('آیا از حذف این آیتم اطمینان دارید؟')) return;
        try {{
            const formData = new FormData();
            formData.append('item_id', id);
            const res = await fetch('/module/admin/statistics/items/delete', {{ method:'POST', body:formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                if (editingItemId == id) cancelEdit();
                loadItems();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{ showToast('⛔ خطا در ارتباط با سرور', 'error'); }}
    }}

    // ==================== تب ۲: تخصیص‌ها ====================
    async function loadConfigs() {{
        try {{
            const [configRes, deptRes, itemRes] = await Promise.all([
                fetch('/module/admin/statistics/config/list'),
                fetch('/module/admin/statistics/depts/list'),
                fetch('/module/admin/statistics/items/list')
            ]);

            const configData = await configRes.json();
            const deptData = await deptRes.json();
            const itemData = await itemRes.json();

            const deptSelect = document.getElementById('config-dept');
            deptSelect.innerHTML = '<option value="">--- انتخاب بخش ---</option>';
            deptData.depts.forEach(d => {{
                deptSelect.innerHTML += `<option value="${{d.ID_nam_bakhsh}}">${{d.nam_bakhsh}}</option>`;
            }});

            const itemSelect = document.getElementById('config-item');
            itemSelect.innerHTML = '<option value="">--- انتخاب آیتم ---</option>';
            itemData.items.forEach(i => {{
                itemSelect.innerHTML += `<option value="${{i.ID_item}}">${{i.item_name}} (${{i.unit}})</option>`;
            }});

            const list = document.getElementById('config-list');
            document.getElementById('config-count').textContent = `${{configData.configs.length}} پیکربندی`;

            if (!configData.configs.length) {{
                list.innerHTML = '<p style="text-align:center; color:var(--light-gray); padding:30px;">هیچ پیکربندی وجود ندارد</p>';
                return;
            }}

            const grouped = {{}};
            configData.configs.forEach(c => {{
                if (!grouped[c.nam_bakhsh]) grouped[c.nam_bakhsh] = [];
                grouped[c.nam_bakhsh].push(c);
            }});

            let html = '';
            for (const [deptName, items] of Object.entries(grouped)) {{
                html += `<div class="dept-group">
                    <div class="dept-header">
                        <span>🏥 ${{deptName}}</span>
                        <span class="dept-count">${{items.length}} آیتم</span>
                    </div>
                    <div class="dept-body">`;
                items.forEach(item => {{
                    html += `<div class="config-item" id="config-row-${{item.ID_config}}">
                        <span>
                            <span class="config-name">🔹 ${{item.item_name}}</span>
                            <span class="config-unit">(${{item.unit}})</span>
                        </span>
                        <button class="btn btn-danger btn-xs" onclick="deleteConfig(${{item.ID_config}})">🗑️ حذف</button>
                    </div>`;
                }});
                html += `</div></div>`;
            }}
            list.innerHTML = html;
        }} catch(e) {{ console.error(e); }}
    }}

    async function assignItem() {{
        const deptId = document.getElementById('config-dept').value;
        const itemId = document.getElementById('config-item').value;

        if (!deptId || !itemId) {{
            showToast('⛔ لطفاً بخش و آیتم را انتخاب کنید', 'error');
            return;
        }}

        const assignText = document.getElementById('assign-text');
        const assignLoading = document.getElementById('assign-loading');
        assignText.style.display = 'none';
        assignLoading.style.display = 'inline';

        try {{
            const formData = new FormData();
            formData.append('dept_id', deptId);
            formData.append('item_id', itemId);

            const res = await fetch('/module/admin/statistics/config/assign', {{ method:'POST', body:formData }});
            const data = await res.json();

            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                document.getElementById('config-dept').value = '';
                document.getElementById('config-item').value = '';
                loadConfigs();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{
            showToast('⛔ خطا در ارتباط با سرور', 'error');
        }} finally {{
            assignText.style.display = 'inline';
            assignLoading.style.display = 'none';
        }}
    }}

    async function deleteConfig(configId) {{
        if (!confirm('آیا از حذف این تخصیص اطمینان دارید؟')) return;
        try {{
            const formData = new FormData();
            formData.append('config_id', configId);
            const res = await fetch('/module/admin/statistics/config/delete', {{ method:'POST', body:formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                const row = document.getElementById('config-row-' + configId);
                if (row) row.remove();
                loadConfigs();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{ showToast('⛔ خطا در ارتباط با سرور', 'error'); }}
    }}

    document.addEventListener('DOMContentLoaded', () => {{
        loadItems();
    }});

    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            cancelEdit();
        }}
        if (e.ctrlKey && e.key === 's') {{
            e.preventDefault();
            if (document.getElementById('tab-items').classList.contains('active')) {{
                saveItem();
            }}
        }}
    }});
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions
# ==========================================

def get_items_list():
    """دریافت لیست تمام آیتم‌های آماری"""
    try:
        items = query(
            "SELECT ID_item, item_name, unit, is_inventory FROM tbl_amar_items ORDER BY ID_item DESC",
            fetch_all=True
        ) or []
        return {'success': True, 'items': items}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def save_item(user, form_data):
    user_id = user.get('UserID', 0)
    item_id = form_data.get('item_id')
    item_name = form_data.get('item_name', '').strip()
    item_unit = form_data.get('item_unit', '').strip()
    is_inventory = form_data.get('is_inventory', '0')

    if not item_name or not item_unit:
        return {'success': False, 'message': 'نام آیتم و واحد الزامی است'}

    try:
        if item_id:
            old_record = query("SELECT * FROM tbl_amar_items WHERE ID_item = %s", (item_id,), fetch_one=True)
            query("UPDATE tbl_amar_items SET item_name=%s, unit=%s, is_inventory=%s WHERE ID_item=%s",
                  (item_name, item_unit, is_inventory, item_id), commit=True)
            log_crud('save_amar_item', user_id, key_value=item_id,
                     old_value=json.dumps(old_record, ensure_ascii=False, default=str),
                     new_value=json.dumps({"name": item_name, "unit": item_unit, "is_inventory": is_inventory}, ensure_ascii=False))
            return {'success': True, 'message': 'آیتم با موفقیت بروزرسانی شد'}
        else:
            query("INSERT INTO tbl_amar_items (item_name, unit, is_inventory) VALUES (%s, %s, %s)",
                  (item_name, item_unit, is_inventory), commit=True)
            new_id = query("SELECT MAX(ID_item) as max_id FROM tbl_amar_items", fetch_one=True)['max_id']
            log_crud('save_amar_item', user_id, key_value=new_id,
                     new_value=json.dumps({"name": item_name, "unit": item_unit, "is_inventory": is_inventory}, ensure_ascii=False))
            return {'success': True, 'message': 'آیتم جدید با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def delete_item(user, form_data):
    user_id = user.get('UserID', 0)
    item_id = form_data.get('item_id')
    if not item_id:
        return {'success': False, 'message': 'شناسه آیتم نامعتبر است'}

    try:
        config_count = query(
            "SELECT COUNT(*) as cnt FROM tbl_bakhsh_amar_config WHERE item_id = %s",
            params=(item_id,), fetch_one=True
        )
        if config_count and config_count['cnt'] > 0:
            return {'success': False, 'message': 'این آیتم در پیکربندی‌ها استفاده شده و قابل حذف نیست'}

        old_record = query("SELECT * FROM tbl_amar_items WHERE ID_item = %s", (item_id,), fetch_one=True)
        query("DELETE FROM tbl_amar_items WHERE ID_item = %s", params=(item_id,), commit=True)
        log_crud('delete_amar_item', user_id, key_value=item_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str))
        return {'success': True, 'message': 'آیتم با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def get_depts_with_amar():
    """دریافت لیست بخش‌های دارای آمار"""
    try:
        depts = query(
            "SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh WHERE amar = 1 ORDER BY nam_bakhsh",
            fetch_all=True
        ) or []
        return {'success': True, 'depts': depts}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def get_config_list():
    """دریافت لیست تمام پیکربندی‌ها"""
    try:
        configs = query("""
            SELECT c.ID_config, b.nam_bakhsh, i.item_name, i.unit
            FROM tbl_bakhsh_amar_config c
            JOIN tbl_bakhsh b ON c.bakhsh_id = b.ID_nam_bakhsh
            JOIN tbl_amar_items i ON c.item_id = i.ID_item
            ORDER BY b.nam_bakhsh, i.item_name
        """, fetch_all=True) or []
        return {'success': True, 'configs': configs}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def assign_item_to_dept(user, form_data):
    user_id = user.get('UserID', 0)
    dept_id = form_data.get('dept_id')
    item_id = form_data.get('item_id')

    if not dept_id or not item_id:
        return {'success': False, 'message': 'بخش و آیتم الزامی است'}

    try:
        existing = query(
            "SELECT ID_config FROM tbl_bakhsh_amar_config WHERE bakhsh_id = %s AND item_id = %s",
            params=(dept_id, item_id), fetch_one=True
        )
        if existing:
            return {'success': False, 'message': 'این اتصال قبلاً وجود دارد'}

        query("INSERT INTO tbl_bakhsh_amar_config (bakhsh_id, item_id) VALUES (%s, %s)",
              (dept_id, item_id), commit=True)
        new_id = query("SELECT MAX(ID_config) as max_id FROM tbl_bakhsh_amar_config", fetch_one=True)['max_id']
        log_crud('assign_amar_config', user_id, key_value=new_id,
                 new_value=json.dumps({"dept": dept_id, "item": item_id}, ensure_ascii=False))
        return {'success': True, 'message': 'اتصال با موفقیت ایجاد شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}

def delete_config(user, form_data):
    user_id = user.get('UserID', 0)
    config_id = form_data.get('config_id')
    if not config_id:
        return {'success': False, 'message': 'شناسه پیکربندی نامعتبر است'}

    try:
        old_record = query("SELECT * FROM tbl_bakhsh_amar_config WHERE ID_config = %s", (config_id,), fetch_one=True)
        query("DELETE FROM tbl_bakhsh_amar_config WHERE ID_config = %s", params=(config_id,), commit=True)
        log_crud('delete_amar_config', user_id, key_value=config_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str))
        return {'success': True, 'message': 'پیکربندی با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}
        
        
        