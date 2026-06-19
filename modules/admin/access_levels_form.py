"""
مدیریت نام سطوح دسترسی – ادمین
ثبت، ویرایش و حذف سطوح دسترسی (accesslevels)
نسخه Flask با AJAX، Toast و طراحی مدرن
"""

from models.database import query
import json
from utils.auto_log import log_crud


def get_access_levels_form(user):
    """صفحه اصلی مدیریت نام سطوح دسترسی"""

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
        --bg: #f1f5f9; --white: #fff; --radius: 14px; --transition: 0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.5s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(15px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:1100px; margin:0 auto; padding:20px; }}

    /* هدر */
    .level-header {{
        background: linear-gradient(135deg, #4338ca, #6366f1);
        color:white; border-radius:var(--radius); padding:25px 30px; margin-bottom:25px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 10px 40px rgba(67,56,202,0.3);
    }}
    .level-header h2 {{ font-size:24px; margin:0; }}
    .level-header p {{ opacity:0.85; font-size:13px; margin:5px 0 0 0; }}
    .back-btn {{
        color:white; text-decoration:none; padding:10px 18px;
        border:1.5px solid rgba(255,255,255,0.4); border-radius:10px;
        font-size:14px; font-weight:500; transition:var(--transition);
    }}
    .back-btn:hover {{ background:rgba(255,255,255,0.15); border-color:rgba(255,255,255,0.6); }}

    /* کارت‌های آمار */
    .stats-row {{
        display:grid; grid-template-columns:repeat(4,1fr); gap:15px; margin-bottom:25px;
    }}
    .stat-card {{
        background:var(--white); border-radius:12px; padding:20px;
        text-align:center; border:1px solid var(--border);
        transition:var(--transition);
    }}
    .stat-card:hover {{ transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,0.08); }}
    .stat-card .stat-value {{ font-size:28px; font-weight:bold; }}
    .stat-card .stat-label {{ font-size:12px; color:var(--gray); margin-top:4px; }}

    /* چیدمان اصلی */
    .main-grid {{
        display:grid; grid-template-columns:1fr 1.3fr; gap:25px;
        align-items:start;
    }}

    /* کارت‌ها */
    .card {{
        background:var(--white); border-radius:var(--radius); padding:25px;
        border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05);
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

    /* فرم‌ها */
    .form-group {{ margin-bottom:16px; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:6px; }}
    .form-input, .form-textarea {{
        width:100%; padding:13px 16px; border:2px solid var(--border);
        border-radius:10px; font-size:14px; font-family:inherit;
        transition:var(--transition); background:var(--white);
    }}
    .form-input:focus, .form-textarea:focus {{
        border-color:var(--primary-light); outline:none;
        box-shadow:0 0 0 3px rgba(99,102,241,0.15);
    }}
    .form-textarea {{ min-height:80px; resize:vertical; }}
    .form-input.error {{ border-color:var(--danger); background:#fef2f2; }}

    .btn {{
        display:inline-flex; align-items:center; justify-content:center; gap:6px;
        padding:12px 22px; border:none; border-radius:10px; font-size:14px;
        font-weight:600; cursor:pointer; font-family:inherit;
        transition:var(--transition); text-decoration:none; white-space:nowrap;
    }}
    .btn-primary {{
        background:linear-gradient(135deg, #4338ca, #6366f1);
        color:white; box-shadow:0 4px 15px rgba(67,56,202,0.25);
    }}
    .btn-primary:hover {{ transform:translateY(-2px); box-shadow:0 8px 25px rgba(67,56,202,0.35); }}
    .btn-outline {{
        background:white; color:var(--dark); border:2px solid var(--border);
    }}
    .btn-outline:hover {{ border-color:#6366f1; color:#4338ca; }}
    .btn-danger {{ background:var(--danger); color:white; }}
    .btn-danger:hover {{ background:#dc2626; }}
    .btn-success {{ background:var(--success); color:white; }}
    .btn-success:hover {{ background:#059669; }}
    .btn-warning {{
        background:var(--warning); color:white;
    }}
    .btn-warning:hover {{ background:#d97706; }}
    .btn-xs {{ padding:6px 12px; font-size:12px; border-radius:7px; }}

    /* لیست سطوح */
    .level-list {{ display:flex; flex-direction:column; gap:10px; max-height:600px; overflow-y:auto; }}
    .level-card {{
        background:var(--white); border:1px solid var(--border);
        border-radius:12px; padding:0; overflow:hidden;
        transition:var(--transition);
    }}
    .level-card:hover {{ border-color:#6366f1; box-shadow:0 2px 8px rgba(0,0,0,0.05); }}
    .level-card.editing {{ border-color:var(--warning); box-shadow:0 0 0 3px rgba(245,158,11,0.15); }}

    .level-card-header {{
        display:flex; align-items:center; gap:12px;
        padding:16px 20px; cursor:pointer;
        transition:var(--transition);
    }}
    .level-card-header:hover {{ background:var(--bg); }}
    
    .level-id {{
        font-family:'Courier New', monospace; font-size:14px; font-weight:bold;
        color:var(--primary); background:#eef2ff; padding:6px 14px;
        border-radius:8px; min-width:50px; text-align:center;
    }}
    .level-info {{ flex:1; }}
    .level-name {{ font-weight:bold; font-size:15px; color:var(--dark); }}
    .level-desc {{ font-size:12px; color:var(--gray); margin-top:3px; }}
    .level-badges {{ display:flex; gap:6px; align-items:center; }}
    .badge {{
        display:inline-block; padding:4px 12px; border-radius:15px;
        font-size:11px; font-weight:600;
    }}
    .badge-admin {{ background:#dbeafe; color:#1e40af; }}
    .badge-editor {{ background:#d1fae5; color:#065f46; }}
    .badge-viewer {{ background:#fef3c7; color:#92400e; }}
    .badge-users {{
        background:#fce7f3; color:#9d174d; font-size:10px;
        padding:3px 10px; border-radius:10px;
    }}

    /* پنل ویرایش */
    .edit-panel {{
        display:none; padding:20px; background:var(--bg);
        border-top:1px solid var(--border);
    }}
    .edit-panel.show {{ display:block; animation:fadeIn 0.3s ease; }}
    .edit-panel .form-row {{
        display:flex; gap:10px; align-items:flex-end;
    }}
    .edit-panel .form-row .form-group {{ flex:1; }}

    /* Toast */
    .toast-container {{
        position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000;
        display:flex; flex-direction:column; gap:10px; pointer-events:none;
    }}
    .toast {{
        display:flex; align-items:center; gap:12px; padding:16px 24px;
        border-radius:14px; color:white; font-size:14px; font-weight:600;
        box-shadow:0 10px 40px rgba(0,0,0,0.25); animation:slideDown 0.4s ease;
        pointer-events:auto; min-width:300px;
    }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }}
    .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    .toast .toast-close {{ margin-right:auto; cursor:pointer; opacity:0.7; font-size:16px; }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}

    /* دیالوگ تایید حذف */
    .modal-overlay {{
        display:none; position:fixed; top:0; left:0; right:0; bottom:0;
        background:rgba(0,0,0,0.5); z-index:500; justify-content:center;
        align-items:center;
    }}
    .modal-overlay.show {{ display:flex; }}
    .modal {{
        background:white; border-radius:16px; padding:30px; width:90%;
        max-width:450px; text-align:center; animation:fadeIn 0.3s ease;
    }}
    .modal h3 {{ margin-bottom:10px; color:var(--danger); }}
    .modal p {{ color:var(--gray); margin-bottom:20px; font-size:14px; }}
    .modal .modal-actions {{ display:flex; gap:10px; justify-content:center; }}

    .empty-state {{
        text-align:center; padding:50px 20px; color:var(--light-gray);
    }}
    .empty-state .icon {{ font-size:48px; margin-bottom:15px; }}

    @media (max-width:768px) {{
        .main-grid {{ grid-template-columns:1fr; }}
        .stats-row {{ grid-template-columns:repeat(2,1fr); }}
        .level-header {{ flex-direction:column; gap:15px; text-align:center; }}
        .level-card-header {{ flex-wrap:wrap; }}
        .edit-panel .form-row {{ flex-direction:column; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>

<!-- دیالوگ حذف -->
<div class="modal-overlay" id="delete-modal">
    <div class="modal">
        <h3>⚠️ هشدار!</h3>
        <p id="delete-message">آیا از حذف این سطح دسترسی اطمینان دارید؟</p>
        <p style="font-size:12px; color:var(--danger);" id="delete-warning"></p>
        <div class="modal-actions">
            <button class="btn btn-danger" onclick="confirmDelete()">✅ بله، حذف شود</button>
            <button class="btn btn-outline" onclick="closeModal()">❌ انصراف</button>
        </div>
    </div>
</div>

<div class="container fade-in">
    <div class="level-header">
        <div>
            <h2>🔐 مدیریت سطوح دسترسی</h2>
            <p>تعریف و مدیریت نام سطوح دسترسی در سیستم</p>
        </div>
        <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
    </div>

    <!-- کارت‌های آمار -->
    <div class="stats-row" id="stats-row">
        <div class="stat-card">
            <div class="stat-value" style="color:#3b82f6;" id="stat-total">۰</div>
            <div class="stat-label">📊 تعداد کل</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color:#10b981;" id="stat-with-desc">۰</div>
            <div class="stat-label">📝 دارای توضیحات</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color:#8b5cf6;" id="stat-with-users">۰</div>
            <div class="stat-label">👥 دارای کاربر</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color:#f59e0b;" id="stat-total-users">۰</div>
            <div class="stat-label">👤 مجموع کاربران</div>
        </div>
    </div>

    <div class="main-grid">
        <!-- ستون فرم ثبت -->
        <div class="card">
            <div class="card-header">
                <span>🆕</span> تعریف سطح دسترسی جدید
            </div>
            <div class="form-group">
                <label>نام سطح دسترسی</label>
                <input type="text" id="new-level-name" class="form-input"
                       placeholder="مثال: admin, editor, viewer...">
            </div>
            <div class="form-group">
                <label>توضیحات</label>
                <textarea id="new-level-desc" class="form-textarea"
                          placeholder="توضیحات این سطح دسترسی..."></textarea>
            </div>
            <div style="background:#f0f7ff; padding:12px; border-radius:8px; margin-bottom:16px; font-size:12px; color:#1e40af;">
                🔹 شناسه سطح دسترسی به صورت خودکار توسط دیتابیس اختصاص داده می‌شود
            </div>
            <button class="btn btn-primary" style="width:100%;" onclick="addLevel()">
                <span id="add-text">➕ ثبت سطح دسترسی</span>
                <span id="add-loading" style="display:none;">⏳ ...</span>
            </button>
        </div>

        <!-- ستون لیست -->
        <div class="card" style="padding:15px;">
            <div class="card-header">
                <span>📋</span> سطوح دسترسی تعریف شده
                <span class="badge" id="level-count">۰ سطح</span>
            </div>
            <div class="level-list" id="level-list">
                <div class="empty-state">
                    <div class="icon">📭</div>
                    <p>در حال بارگذاری...</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    let deleteTargetId = null;
    let editingId = null;

    // ==================== توابع عمومی ====================
    function showToast(msg, type) {{
        const c = document.getElementById('toast-container');
        const t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = `<span>${{type==='success'?'✅':'❌'}}</span><span>${{msg}}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    function closeModal() {{
        document.getElementById('delete-modal').classList.remove('show');
        deleteTargetId = null;
    }}

    // ==================== بارگذاری لیست ====================
    async function loadLevels() {{
        try {{
            const res = await fetch('/module/admin/access_levels/list');
            const data = await res.json();
            const list = document.getElementById('level-list');
            document.getElementById('level-count').textContent = `${{data.levels.length}} سطح`;

            // بروزرسانی آمار
            document.getElementById('stat-total').textContent = data.stats.total;
            document.getElementById('stat-with-desc').textContent = data.stats.with_description;
            document.getElementById('stat-with-users').textContent = data.stats.with_users;
            document.getElementById('stat-total-users').textContent = data.stats.total_users;

            if (!data.levels.length) {{
                list.innerHTML = '<div class="empty-state"><div class="icon">📭</div><p>هنوز سطح دسترسی‌ای ثبت نشده است</p></div>';
                return;
            }}

            // تعیین کلاس بج بر اساس نام
            function getBadgeClass(name) {{
                const n = name.toLowerCase();
                if (n.includes('admin')) return 'badge-admin';
                if (n.includes('editor') || n.includes('ویرایش')) return 'badge-editor';
                if (n.includes('viewer') || n.includes('بیننده')) return 'badge-viewer';
                return '';
            }}

            function getBadgeLabel(name) {{
                const n = name.toLowerCase();
                if (n.includes('admin')) return 'مدیر';
                if (n.includes('editor') || n.includes('ویرایش')) return 'ویرایشگر';
                if (n.includes('viewer') || n.includes('بیننده')) return 'بیننده';
                return '';
            }}

            let html = '';
            data.levels.forEach(level => {{
                const badgeClass = getBadgeClass(level.AccessLevelName);
                const badgeLabel = getBadgeLabel(level.AccessLevelName);
                const userCount = level.user_count || 0;
                const hasUsers = userCount > 0;
                const isEditing = editingId == level.AccessLevelID;
                const disabledAttr = hasUsers ? 'disabled' : '';  // اصلاح شده

                // escaping نام برای استفاده در onclick
                const safeName = level.AccessLevelName.replace(/'/g, "\\'");

                html += `<div class="level-card ${{isEditing ? 'editing' : ''}}" id="level-card-${{level.AccessLevelID}}">                                      
                    <div class="level-card-header" onclick="toggleEdit(${{level.AccessLevelID}})">
                        <span class="level-id">#${{level.AccessLevelID}}</span>
                        <div class="level-info">
                            <div class="level-name">${{level.AccessLevelName}}</div>
                            ${{level.Description ? `<div class="level-desc">${{level.Description}}</div>` : ''}}
                        </div>
                        <div class="level-badges">
                            ${{badgeClass ? `<span class="badge ${{badgeClass}}">${{badgeLabel}}</span>` : ''}}
                            ${{hasUsers ? `<span class="badge badge-users">👤 ${{userCount}}</span>` : ''}}
                        </div>
                        <div class="level-actions" onclick="event.stopPropagation()">
                            <button class="btn btn-warning btn-xs" onclick="toggleEdit(${{level.AccessLevelID}})">📝</button>
                            <button class="btn btn-danger btn-xs" ${{disabledAttr}} onclick="event.stopPropagation(); askDelete(${{level.AccessLevelID}}, '${{safeName}}')">🗑️</button>
                        </div>
                    </div>              
                    <div class="edit-panel ${{isEditing ? 'show' : ''}}" id="edit-panel-${{level.AccessLevelID}}">
                        <div class="form-row">
                            <div class="form-group">
                                <label>نام سطح دسترسی</label>
                                <input type="text" class="form-input" id="edit-name-${{level.AccessLevelID}}" value="${{level.AccessLevelName.replace(/"/g, '&quot;')}}">
                            </div>
                            <div class="form-group">
                                <label>توضیحات</label>
                                <input type="text" class="form-input" id="edit-desc-${{level.AccessLevelID}}" value="${{(level.Description || '').replace(/"/g, '&quot;')}}">
                            </div>
                            <div class="form-group" style="flex:0 0 auto;">
                                <label>&nbsp;</label>
                                <div style="display:flex; gap:6px;">
                                    <button class="btn btn-success btn-xs" onclick="saveEdit(${{level.AccessLevelID}})">💾 ذخیره</button>
                                    <button class="btn btn-outline btn-xs" onclick="cancelEdit(${{level.AccessLevelID}})">❌</button>
                                </div>
                            </div>
                        </div>
                        ${{hasUsers ? `
                        <div style="margin-top:12px; font-size:11px; color:var(--danger); text-align:left;">
                            ⚠️ این سطح به ${{userCount}} کاربر متصل است و قابل حذف نیست
                        </div>` : ''}}
                    </div>
                </div>`;
            }});
            list.innerHTML = html;
        }} catch(e) {{ console.error(e); }}
    }}

    // ==================== افزودن ====================
    async function addLevel() {{
        const name = document.getElementById('new-level-name').value.trim();

        if (!name) {{
            document.getElementById('new-level-name').classList.add('error');
            showToast('⛔ لطفاً نام سطح دسترسی را وارد کنید', 'error');
            setTimeout(() => document.getElementById('new-level-name').classList.remove('error'), 2000);
            return;
        }}

        const addText = document.getElementById('add-text');
        const addLoading = document.getElementById('add-loading');
        addText.style.display = 'none';
        addLoading.style.display = 'inline';

        try {{
            const formData = new FormData();
            formData.append('level_name', name);
            formData.append('description', document.getElementById('new-level-desc').value.trim());

            const res = await fetch('/module/admin/access_levels/save', {{ method:'POST', body:formData }});
            const data = await res.json();

            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                document.getElementById('new-level-name').value = '';
                document.getElementById('new-level-desc').value = '';
                loadLevels();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{
            showToast('⛔ خطا در ارتباط با سرور', 'error');
        }} finally {{
            addText.style.display = 'inline';
            addLoading.style.display = 'none';
        }}
    }}

    // ==================== ویرایش ====================
    function toggleEdit(id) {{
        if (editingId === id) {{
            cancelEdit(id);
        }} else {{
            if (editingId) cancelEdit(editingId);
            editingId = id;
            document.getElementById('edit-panel-' + id).classList.add('show');
            document.getElementById('level-card-' + id).classList.add('editing');
            document.getElementById('edit-name-' + id).focus();
        }}
    }}

    function cancelEdit(id) {{
        if (editingId === id) {{
            document.getElementById('edit-panel-' + id).classList.remove('show');
            document.getElementById('level-card-' + id).classList.remove('editing');
            editingId = null;
            loadLevels(); // بارگذاری مجدد برای بازگرداندن مقادیر اصلی
        }}
    }}

    async function saveEdit(id) {{
        const newName = document.getElementById('edit-name-' + id).value.trim();
        const newDesc = document.getElementById('edit-desc-' + id).value.trim();

        if (!newName) {{
            showToast('⛔ نام سطح دسترسی نمی‌تواند خالی باشد', 'error');
            return;
        }}

        try {{
            const formData = new FormData();
            formData.append('level_id', id);
            formData.append('level_name', newName);
            formData.append('description', newDesc);

            const res = await fetch('/module/admin/access_levels/update', {{ method:'POST', body:formData }});
            const data = await res.json();

            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                editingId = null;
                loadLevels();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{
            showToast('⛔ خطا در ارتباط با سرور', 'error');
        }}
    }}

    // ==================== حذف (مودال) ====================
    function askDelete(id, name) {{
        deleteTargetId = id;
        document.getElementById('delete-message').textContent = `آیا از حذف سطح دسترسی "${{name}}" با شناسه ${{id}} اطمینان دارید؟`;
        document.getElementById('delete-warning').textContent = 'این عملیات غیرقابل بازگشت است!';
        document.getElementById('delete-modal').classList.add('show');
    }}

    async function confirmDelete() {{
        if (!deleteTargetId) return;

        try {{
            const formData = new FormData();
            formData.append('level_id', deleteTargetId);
            const res = await fetch('/module/admin/access_levels/delete', {{ method:'POST', body:formData }});
            const data = await res.json();

            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                closeModal();
                if (editingId == deleteTargetId) editingId = null;
                loadLevels();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
                closeModal();
            }}
        }} catch(e) {{
            showToast('⛔ خطا در ارتباط با سرور', 'error');
            closeModal();
        }}
    }}

    // ==================== لود اولیه ====================
    document.addEventListener('DOMContentLoaded', () => {{
        loadLevels();
    }});

    // ==================== میانبر ====================
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            if (deleteTargetId) closeModal();
            if (editingId) cancelEdit(editingId);
        }}
    }});
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions
# ==========================================

def get_levels_list(user=None):
    """دریافت لیست سطوح دسترسی با آمار"""
    try:
        levels = query(
            "SELECT AccessLevelID, AccessLevelName, Description FROM accesslevels ORDER BY AccessLevelID",
            fetch_all=True
        ) or []

        # دریافت تعداد کاربران هر سطح
        users_stats = query(
            "SELECT AccessLevelID, COUNT(*) as cnt FROM users WHERE AccessLevelID IS NOT NULL GROUP BY AccessLevelID",
            fetch_all=True
        ) or []
        users_dict = {u['AccessLevelID']: u['cnt'] for u in users_stats}

        # اضافه کردن user_count به هر سطح
        total_users = 0
        with_description = 0
        with_users = 0

        for level in levels:
            uc = users_dict.get(level['AccessLevelID'], 0)
            level['user_count'] = uc
            total_users += uc
            if uc > 0:
                with_users += 1
            if level.get('Description'):
                with_description += 1

        return {
            'success': True,
            'levels': levels,
            'stats': {
                'total': len(levels),
                'with_description': with_description,
                'with_users': with_users,
                'total_users': total_users
            }
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}


def save_level(user, form_data):
    """ثبت سطح دسترسی جدید"""
    user_id = user.get('UserID', 0)
    level_name = form_data.get('level_name', '').strip()
    description = form_data.get('description', '').strip()

    if not level_name:
        return {'success': False, 'message': 'نام سطح دسترسی الزامی است'}

    try:
        existing = query(
            "SELECT AccessLevelID FROM accesslevels WHERE AccessLevelName = %s",
            params=(level_name,), fetch_one=True
        )
        if existing:
            return {'success': False, 'message': 'این نام سطح دسترسی قبلاً ثبت شده است'}

        if description:
            query(
                "INSERT INTO accesslevels (AccessLevelName, Description) VALUES (%s, %s)",
                params=(level_name, description), commit=True
            )
        else:
            query(
                "INSERT INTO accesslevels (AccessLevelName) VALUES (%s)",
                params=(level_name,), commit=True
            )

        new_id = query("SELECT MAX(AccessLevelID) as max_id FROM accesslevels", fetch_one=True)['max_id']
        log_crud('save_level', user_id, key_value=new_id,
                 new_value=json.dumps({"name": level_name, "desc": description}, ensure_ascii=False))
        return {'success': True, 'message': f'سطح دسترسی "{level_name}" با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def update_level(user, form_data):
    """بروزرسانی سطح دسترسی"""
    user_id = user.get('UserID', 0)
    level_id = form_data.get('level_id')
    level_name = form_data.get('level_name', '').strip()
    description = form_data.get('description', '').strip()

    if not level_id:
        return {'success': False, 'message': 'شناسه سطح دسترسی نامعتبر است'}
    if not level_name:
        return {'success': False, 'message': 'نام سطح دسترسی نمی‌تواند خالی باشد'}

    try:
        existing = query(
            "SELECT AccessLevelID FROM accesslevels WHERE AccessLevelName = %s AND AccessLevelID != %s",
            params=(level_name, level_id), fetch_one=True
        )
        if existing:
            return {'success': False, 'message': 'این نام سطح دسترسی قبلاً ثبت شده است'}

        old_record = query("SELECT * FROM accesslevels WHERE AccessLevelID = %s", (level_id,), fetch_one=True)
        query(
            "UPDATE accesslevels SET AccessLevelName = %s, Description = %s WHERE AccessLevelID = %s",
            params=(level_name, description, level_id), commit=True
        )
        log_crud('update_level', user_id, key_value=level_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str),
                 new_value=json.dumps({"name": level_name, "desc": description}, ensure_ascii=False))
        return {'success': True, 'message': 'تغییرات با موفقیت بروزرسانی شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def delete_level(user, form_data):
    """حذف سطح دسترسی"""
    user_id = user.get('UserID', 0)
    level_id = form_data.get('level_id')

    if not level_id:
        return {'success': False, 'message': 'شناسه سطح دسترسی نامعتبر است'}

    try:
        # بررسی استفاده در جدول users
        user_count = query(
            "SELECT COUNT(*) as cnt FROM users WHERE AccessLevelID = %s",
            params=(level_id,),
            fetch_one=True
        )
        if user_count and user_count['cnt'] > 0:
            return {'success': False, 'message': f'این سطح دسترسی به {user_count["cnt"]} کاربر متصل است و قابل حذف نیست'}

        # بررسی استفاده در جدول userlevelpermissions
        perm_count = query(
            "SELECT COUNT(*) as cnt FROM userlevelpermissions WHERE UserLevelID = %s",
            params=(level_id,),
            fetch_one=True
        )
        if perm_count and perm_count['cnt'] > 0:
            # حذف دسترسی‌های مرتبط
            query(
                "DELETE FROM userlevelpermissions WHERE UserLevelID = %s",
                params=(level_id,),
                commit=True
            )

        # خواندن رکورد قدیمی برای لاگ
        old_record = query(
            "SELECT * FROM accesslevels WHERE AccessLevelID = %s",
            (level_id,),
            fetch_one=True
        )

        # حذف سطح دسترسی
        query(
            "DELETE FROM accesslevels WHERE AccessLevelID = %s",
            params=(level_id,),
            commit=True
        )

        # ثبت لاگ حسابرسی
        log_crud('delete_level', user_id, key_value=level_id,
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str) if old_record else '')
        
        return {'success': True, 'message': 'سطح دسترسی با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}
        
        