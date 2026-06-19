"""
فرم راند و اعتباربخشی – سوپروایزر
نسخه Flask با AJAX، Toast و مدیریت اسناد (نسخه بهینه‌شده)
"""

import os, json, jdatetime, time
from datetime import datetime
from werkzeug.utils import secure_filename
from models.database import query, get_connection
from utils.auto_log import log_crud

UPLOAD_DIR = "uploads/arziabi"

def get_rounds_form(user):
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')
    shift = query("SELECT ID_shift, tarkib FROM shift_namt ORDER BY ID_shift DESC LIMIT 1", fetch_one=True)
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

    # لیست گروه‌های ارزیابی
    titles = query("SELECT ID_onvan_arziabi, nom_onvan FROM tbl_arzibi_onvan ORDER BY nom_onvan", fetch_all=True) or []
    title_options = '<option value="">--- انتخاب گروه ارزیابی ---</option>'
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
    .rounds-header {{
        background:linear-gradient(135deg, #6366f1, #8b5cf6); color:white; border-radius:16px; padding:25px 30px;
        margin-bottom:25px; display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(99,102,241,0.25);
    }}
    .rounds-header h2 {{ font-size:24px; }}
    .shift-badge {{ background:rgba(255,255,255,0.2); padding:10px 20px; border-radius:30px; font-weight:bold; }}
    .back-btn {{ color:white; text-decoration:none; padding:8px 16px; border:1px solid rgba(255,255,255,0.4); border-radius:8px; transition:var(--transition); }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}
    .tabs {{ display:flex; gap:5px; margin-bottom:25px; border-bottom:2px solid var(--border); }}
    .tab {{ padding:12px 24px; font-weight:600; border:none; background:none; color:var(--light-gray); cursor:pointer; border-bottom:2px solid transparent; transition:var(--transition); font-family:inherit; }}
    .tab:hover {{ color:var(--dark); }}
    .tab.active {{ color:var(--primary); border-bottom-color:var(--primary); }}
    .tab-content {{ display:none; }}
    .tab-content.active {{ display:block; animation:fadeIn 0.3s ease; }}
    .card {{ background:var(--white); border-radius:var(--radius); padding:25px; border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:25px; }}
    .card-title {{ font-weight:bold; color:var(--dark); margin-bottom:20px; padding-bottom:12px; border-bottom:2px solid var(--border); display:flex; align-items:center; gap:8px; }}
    .form-group {{ margin-bottom:18px; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:6px; }}
    .form-select, .form-input, .form-textarea {{
        width:100%; padding:12px 14px; border:2px solid var(--border); border-radius:8px;
        font-size:14px; font-family:inherit; transition:var(--transition); background:var(--white);
    }}
    .form-select:focus, .form-input:focus, .form-textarea:focus {{ border-color:var(--primary-light); outline:none; box-shadow:0 0 0 3px rgba(59,130,246,0.15); }}
    .form-textarea {{ min-height:80px; resize:vertical; }}
    .row {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }}
    .btn {{ display:inline-flex; align-items:center; justify-content:center; gap:6px; padding:10px 20px; border:none; border-radius:8px; font-size:14px; font-weight:600; cursor:pointer; font-family:inherit; transition:var(--transition); }}
    .btn-primary {{ background:var(--primary); color:white; }} .btn-primary:hover {{ background:var(--primary-light); }}
    .btn-danger {{ background:var(--danger); color:white; }} .btn-sm {{ padding:6px 12px; font-size:12px; }}
    
    /* استایل‌های جدید برای مدیریت فایل */
    .file-upload-box {{
        margin-top: 15px;
        border: 2px dashed var(--border);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        background: #fafafa;
    }}
    .file-upload-box:hover {{
        border-color: var(--primary-light);
        background: #f0f4ff;
    }}
    .file-upload-box.dragover {{
        border-color: var(--primary);
        background: #eef2ff;
    }}
    .file-upload-box input[type=file] {{ display:none; }}
    .file-upload-icon {{ font-size: 32px; margin-bottom: 8px; }}
    .file-upload-text {{ color: var(--gray); font-size: 13px; }}
    .file-upload-hint {{ color: var(--light-gray); font-size: 11px; margin-top: 4px; }}
    
    .files-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 10px;
        margin-top: 15px;
    }}
    .file-card {{
        background: white;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: all 0.2s ease;
    }}
    .file-card:hover {{
        border-color: var(--primary-light);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .file-card-icon {{
        font-size: 24px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg);
        border-radius: 8px;
        flex-shrink: 0;
    }}
    .file-card-info {{
        flex: 1;
        min-width: 0;
    }}
    .file-card-name {{
        font-size: 12px;
        font-weight: 600;
        color: var(--dark);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .file-card-size {{
        font-size: 10px;
        color: var(--gray);
        margin-top: 2px;
    }}
    .file-card-actions {{
        display: flex;
        gap: 4px;
    }}
    .file-card .btn {{
        padding: 4px 8px;
        font-size: 11px;
    }}
    
    .record-item {{
        background:var(--white); border:1px solid var(--border); border-radius:10px; padding:15px;
        margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;
    }}
    .record-item .r-info {{ flex:1; }}
    .record-item .r-title {{ font-weight:bold; font-size:14px; }}
    .record-item .r-meta {{ font-size:12px; color:var(--gray); margin-top:4px; }}
    .record-actions {{ display:flex; gap:6px; }}
    .toast-container {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:10px; pointer-events:none; }}
    .toast {{ display:flex; align-items:center; gap:12px; padding:14px 22px; border-radius:12px; color:white; font-weight:600; box-shadow:0 10px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; pointer-events:auto; }}
    .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }} .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-30px); }} to {{ opacity:1; transform:translateY(0); }} }}
    @media (max-width:768px) {{ .rounds-header {{ flex-direction:column; gap:15px; text-align:center; }} }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">
    <div class="rounds-header">
        <div><h2>🔍 راند و اعتباربخشی</h2><p style="opacity:0.85;margin-top:5px;">شیفت: {shift_name}</p></div>
        <a href="/module/supervisor" class="back-btn">⬅️ بازگشت</a>
    </div>
    <div class="tabs">
        <button class="tab active" onclick="switchTab('form')">📝 ثبت / ویرایش</button>
        <button class="tab" onclick="switchTab('list')">📋 سوابق ثبت شده</button>
    </div>
    <div id="tab-form" class="tab-content active">
        <div class="card">
            <div class="card-title"><span>📝</span> اطلاعات ارزیابی</div>
            <form id="round-form">
                <input type="hidden" name="shift_id" value="{shift_id}">
                <input type="hidden" name="edit_id" id="edit_id" value="">
                <div class="row" style="margin-bottom:15px;">
                    <div class="form-group" style="flex:1;">
                        <label>🏥 بخش</label>
                        <select name="dept_id" id="dept_id" class="form-select" required>{dept_options}</select>
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>📌 گروه ارزیابی</label>
                        <select name="title_id" id="title_id" class="form-select" required onchange="loadChecklistItems()">{title_options}</select>
                    </div>
                </div>
                
                <!-- بخش انتخاب سنجه -->
                <div id="checklist-container">
                    <div class="form-group">
                        <label>✅ سنجه</label>
                        <select name="checklist_id" id="checklist_id" class="form-select" onchange="updateItemInfo()" disabled>
                            <option value="">ابتدا گروه ارزیابی را انتخاب کنید</option>
                        </select>
                    </div>
                </div>
                
                <!-- اطلاعات سنجه + امتیاز در یک ردیف -->
                <div class="row" style="margin-bottom:15px; display:none;" id="item-info-row">
                    <div class="form-group" style="flex:1;">
                        <label>سطح</label>
                        <input type="text" id="item_level" class="form-input" disabled>
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>وزن</label>
                        <input type="text" id="item_weight" class="form-input" disabled>
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>ایمنی</label>
                        <input type="text" id="item_safety" class="form-input" disabled>
                    </div>
                    <div class="form-group" style="flex:1.5;">
                        <label>🔴 امتیاز (حداکثر: <span id="max_score_label" style="color:#1e40af;">0</span>)</label>
                        <input type="number" name="score" id="score" class="form-input" step="0.25" min="0" value="0" style="font-weight:bold; font-size:16px; color:#1e3a8a;">
                    </div>
                </div>
                
                <!-- راهنمای سنجه -->
                <div id="guide-box" style="display:none; background:#f0f7ff; padding:12px; border-radius:8px; margin-bottom:15px; color:#1e40af;">
                    <strong>💡 راهنما:</strong> <span id="guide-text"></span>
                </div>
                
                <div class="row" style="margin-bottom:15px;">
                    <div class="form-group" style="flex:1;">
                        <label>نقاط مثبت</label>
                        <textarea name="positive_notes" id="positive_notes" class="form-textarea" rows="2" placeholder="موارد مثبت مشاهده شده..."></textarea>
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>نقاط منفی</label>
                        <textarea name="negative_notes" id="negative_notes" class="form-textarea" rows="2" placeholder="موارد منفی یا قابل بهبود..."></textarea>
                    </div>
                </div>
                <div class="form-group">
                    <label>توضیحات تکمیلی</label>
                    <input type="text" name="description" id="description" class="form-input" placeholder="توضیحات اضافی...">
                </div>
                
                <!-- آپلود فایل با طراحی جدید -->
                <div class="file-upload-box" id="file-drop-zone">
                    <div class="file-upload-icon">📁</div>
                    <div class="file-upload-text">فایل‌های خود را اینجا رها کنید یا کلیک کنید</div>
                    <div class="file-upload-hint" id="file-upload-hint">
                        فرمت‌های مجاز: PDF, Word, Excel, JPG/PNG | حداکثر 20 مگابایت هر فایل | حداکثر 10 فایل
                    </div>
                    <input type="file" id="file-upload" multiple accept=".pdf,.doc,.docx,.xlsx,.xls,.jpg,.jpeg,.png" onchange="handleFileSelect()">
                </div>
                
                <!-- لیست فایل‌های جدید انتخاب‌شده -->
                <div class="files-grid" id="new-files-grid"></div>
                
                <!-- فایل‌های موجود -->
                <div id="existing-files-section" style="margin-top:15px;"></div>
            </form>
        </div>
        <div style="display:flex; gap:10px;">
            <button class="btn btn-primary" style="flex:1;" onclick="submitRound()" id="submit-btn">
                <span id="save-text">💾 ثبت نهایی</span>
                <span id="save-loading" style="display:none;">⏳ در حال ذخیره...</span>
            </button>
            <button class="btn btn-sm" onclick="clearForm()" style="background:white; border:2px solid var(--border); color:var(--gray);">🔄 جدید</button>
        </div>
    </div>

    <div id="tab-list" class="tab-content">
        <div class="card">
            <div class="card-title"><span>📋</span> سوابق ثبت شده</div>
            <div id="records-list"></div>
        </div>
    </div>
</div>

<script>
    let editingId = null, existingFiles = [], selectedFiles = [];
    let currentMaxScore = 0, currentItemWeight = 1;
    const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB
    const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xlsx', 'xls', 'jpg', 'jpeg', 'png'];
    const MAX_FILES = 10;

    // ========== مدیریت تب‌ها ==========
    function switchTab(tab) {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        if (tab === 'form') {{
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.getElementById('tab-form').classList.add('active');
        }} else {{
            document.querySelectorAll('.tab')[1].classList.add('active');
            document.getElementById('tab-list').classList.add('active');
            fetchRecordsList();
        }}
    }}

    // ========== Toast Notification ==========
    function showToast(msg, type) {{
        const c = document.getElementById('toast-container'), t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span><span style="cursor:pointer;margin-right:auto;" onclick="this.parentElement.remove()">✕</span>';
        c.appendChild(t);
        setTimeout(() => {{ if(t.parentElement) {{ t.style.opacity='0'; setTimeout(() => t.remove(), 300); }} }}, 4000);
    }}

    // ========== مدیریت فایل (Drag & Drop) ==========
    const dropZone = document.getElementById('file-drop-zone');
    
    dropZone.addEventListener('click', () => {{
        document.getElementById('file-upload').click();
    }});
    
    dropZone.addEventListener('dragover', (e) => {{
        e.preventDefault();
        dropZone.classList.add('dragover');
    }});
    
    dropZone.addEventListener('dragleave', () => {{
        dropZone.classList.remove('dragover');
    }});
    
    dropZone.addEventListener('drop', (e) => {{
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const droppedFiles = Array.from(e.dataTransfer.files);
        processFiles(droppedFiles);
    }});

    function handleFileSelect() {{
        const input = document.getElementById('file-upload');
        const files = Array.from(input.files);
        processFiles(files);
        input.value = ''; // ریست input
    }}

    function processFiles(files) {{
        let hasError = false;
        
        files.forEach(file => {{
            // بررسی تعداد کل فایل‌ها
            if (selectedFiles.length + existingFiles.length >= MAX_FILES) {{
                showToast(`حداکثر ${{MAX_FILES}} فایل مجاز است`, 'error');
                hasError = true;
                return;
            }}
            
            // بررسی پسوند فایل
            const ext = file.name.split('.').pop().toLowerCase();
            if (!ALLOWED_EXTENSIONS.includes(ext)) {{
                showToast(`فرمت فایل "${{file.name}}" مجاز نیست`, 'error');
                hasError = true;
                return;
            }}
            
            // بررسی حجم فایل
            if (file.size > MAX_FILE_SIZE) {{
                const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
                showToast(`حجم فایل "${{file.name}}" (${{sizeMB}}MB) بیش از حد مجاز 20MB است`, 'error');
                hasError = true;
                return;
            }}
            
            // بررسی تکراری نبودن
            const isDuplicate = selectedFiles.some(f => f.name === file.name && f.size === file.size);
            if (!isDuplicate) {{
                selectedFiles.push(file);
            }}
        }});
        
        renderNewFiles();
        updateUploadHint();
    }}

    function renderNewFiles() {{
        const grid = document.getElementById('new-files-grid');
        if (!selectedFiles.length) {{
            grid.innerHTML = '';
            return;
        }}
        
        let html = '';
        selectedFiles.forEach((file, index) => {{
            const ext = file.name.split('.').pop().toLowerCase();
            const icon = getFileIcon(ext);
            const sizeKB = (file.size / 1024).toFixed(1);
            const sizeDisplay = sizeKB > 1024 ? (sizeKB / 1024).toFixed(1) + ' MB' : sizeKB + ' KB';
            
            html += `
                <div class="file-card">
                    <div class="file-card-icon">${{icon}}</div>
                    <div class="file-card-info">
                        <div class="file-card-name" title="${{file.name}}">${{file.name.substring(0, 25)}}${{file.name.length > 25 ? '...' : ''}}</div>
                        <div class="file-card-size">${{sizeDisplay}}</div>
                    </div>
                    <div class="file-card-actions">
                        <button class="btn btn-danger" onclick="removeNewFile(${{index}})" title="حذف">🗑️</button>
                    </div>
                </div>
            `;
        }});
        
        grid.innerHTML = html;
    }}

    function removeNewFile(index) {{
        selectedFiles.splice(index, 1);
        renderNewFiles();
        updateUploadHint();
    }}

    function getFileIcon(ext) {{
        const icons = {{
            'pdf': '📕',
            'doc': '📝',
            'docx': '📝',
            'xlsx': '📊',
            'xls': '📊',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️'
        }};
        return icons[ext] || '📎';
    }}

    function updateUploadHint() {{
        const totalCount = selectedFiles.length + existingFiles.length;
        const totalSize = selectedFiles.reduce((sum, f) => sum + f.size, 0);
        const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(1);
        
        document.getElementById('file-upload-hint').textContent = 
            `${{totalCount}} فایل انتخاب شده | حجم کل: ${{totalSizeMB}} MB | حداکثر 10 فایل و 20MB هر فایل`;
    }}

    // ========== لود چک‌لیست آیتم‌ها ==========
    async function loadChecklistItems() {{
        const titleId = document.getElementById('title_id').value;
        const sel = document.getElementById('checklist_id');
        sel.innerHTML = '<option value="">در حال بارگذاری...</option>';
        sel.disabled = true;
        if (!titleId) {{
            sel.innerHTML = '<option value="">ابتدا گروه ارزیابی را انتخاب کنید</option>';
            return;
        }}
        try {{
            const res = await fetch('/module/supervisor/rounds/items/' + titleId);
            const data = await res.json();
            if (data.success) {{
                const items = data.items;
                sel.innerHTML = '<option value="">--- انتخاب سنجه ---</option>';
                items.forEach(item => {{
                    sel.innerHTML += `<option value="${{item.ID_cheklist}}" data-max="${{item.nomreh}}" data-weight="${{item.vazn_sanjeh}}" data-level="${{item.sath||''}}" data-safety="${{item.imani_chek||'0'}}" data-guide="${{(item.rahnamii || '').replace(/"/g, '&quot;')}}">${{item.nam_item}} (کد: ${{item.adres_sanjeh||'-'}})</option>`;
                }});
                sel.disabled = false;
            }} else {{
                sel.innerHTML = '<option value="">خطا در دریافت آیتم‌ها</option>';
            }}
        }} catch(e) {{ showToast('خطا در دریافت چک‌لیست', 'error'); }}
    }}

    function updateItemInfo() {{
        const sel = document.getElementById('checklist_id');
        const option = sel.options[sel.selectedIndex];
        const maxScore = parseFloat(option.getAttribute('data-max')) || 0;
        const weight = parseFloat(option.getAttribute('data-weight')) || 1;
        const level = option.getAttribute('data-level') || '-';
        const safety = option.getAttribute('data-safety') === '1' ? '✅ دارد' : '❌ ندارد';
        const guide = option.getAttribute('data-guide');

        document.getElementById('max_score_label').textContent = maxScore;
        document.getElementById('score').setAttribute('max', maxScore);
        document.getElementById('item_level').value = level;
        document.getElementById('item_weight').value = weight;
        document.getElementById('item_safety').value = safety;
        
        // نمایش ردیف اطلاعات + امتیاز
        document.getElementById('item-info-row').style.display = 'flex';
        
        // نمایش راهنما
        const guideBox = document.getElementById('guide-box');
        const guideText = document.getElementById('guide-text');
        if (guide) {{
            guideText.textContent = guide;
            guideBox.style.display = 'block';
        }} else {{
            guideBox.style.display = 'none';
        }}
        
        currentMaxScore = maxScore;
        currentItemWeight = weight;
    }}

    // ========== ارسال فرم ==========
    async function submitRound() {{
        const form = document.getElementById('round-form');
        if (!form.dept_id.value || !form.title_id.value || !form.checklist_id.value) {{
            showToast('⛔ لطفاً بخش، گروه و سنجه را انتخاب کنید', 'error');
            return;
        }}
        const score = parseFloat(form.score.value);
        if (isNaN(score) || score < 0 || score > currentMaxScore) {{
            showToast(`⛔ امتیاز باید بین 0 تا ${{currentMaxScore}} باشد`, 'error');
            return;
        }}
        
        const formData = new FormData(form);
        selectedFiles.forEach(f => formData.append('files', f));
        formData.append('existing_files', JSON.stringify(existingFiles));

        const saveText = document.getElementById('save-text');
        const saveLoading = document.getElementById('save-loading');
        const submitBtn = document.getElementById('submit-btn');
        saveText.style.display = 'none';
        saveLoading.style.display = 'inline';
        submitBtn.disabled = true;
        
        try {{
            const res = await fetch('/module/supervisor/rounds/save', {{ method:'POST', body: formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                editingId = data.record_id;
                document.getElementById('edit_id').value = data.record_id;
                selectedFiles = [];
                document.getElementById('new-files-grid').innerHTML = '';
                document.getElementById('file-upload').value = '';
                loadExistingFiles(data.record_id);
                fetchRecordsList();
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }} catch(e) {{ showToast('خطا در ارتباط', 'error'); }}
        finally {{
            saveText.style.display = 'inline';
            saveLoading.style.display = 'none';
            submitBtn.disabled = false;
        }}
    }}

    // ========== مدیریت فایل‌های موجود ==========
    async function loadExistingFiles(recordId) {{
        const div = document.getElementById('existing-files-section');
        if (!existingFiles.length) {{ div.innerHTML = ''; return; }}
        
        let html = '<div style="font-weight:600; margin-bottom:10px; padding:8px 0; border-bottom:1px solid var(--border);">📎 فایل‌های پیوست شده قبلی:</div>';
        html += '<div class="files-grid">';
        existingFiles.forEach((filePath, index) => {{
            const name = filePath.split('/').pop();
            const ext = name.split('.').pop().toLowerCase();
            const icon = getFileIcon(ext);
            
            html += `
                <div class="file-card">
                    <div class="file-card-icon">${{icon}}</div>
                    <div class="file-card-info">
                        <div class="file-card-name" title="${{name}}">${{name.substring(0, 25)}}${{name.length > 25 ? '...' : ''}}</div>
                    </div>
                    <div class="file-card-actions">
                        <a href="/${{filePath}}" target="_blank" class="btn btn-sm" style="background:var(--primary-light); color:white; text-decoration:none;" download>⬇️</a>
                        <button class="btn btn-danger" onclick="deleteFile(${{recordId}}, ${{index}})" title="حذف">🗑️</button>
                    </div>
                </div>
            `;
        }});
        html += '</div>';
        div.innerHTML = html;
    }}

    async function deleteFile(recordId, fileIndex) {{
        if (!confirm('آیا از حذف این فایل اطمینان دارید؟')) return;
        try {{
            const formData = new FormData();
            formData.append('record_id', recordId);
            formData.append('file_index', fileIndex);
            const res = await fetch('/module/supervisor/rounds/delete_file', {{ method:'POST', body: formData }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ فایل حذف شد', 'success');
                existingFiles = data.files;
                loadExistingFiles(recordId);
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    // ========== پاکسازی فرم ==========
    function clearForm() {{
        document.getElementById('round-form').reset();
        document.getElementById('edit_id').value = '';
        editingId = null;
        existingFiles = [];
        selectedFiles = [];
        document.getElementById('new-files-grid').innerHTML = '';
        document.getElementById('existing-files-section').innerHTML = '';
        document.getElementById('item-info-row').style.display = 'none';
        document.getElementById('guide-box').style.display = 'none';
        document.getElementById('checklist_id').innerHTML = '<option value="">ابتدا گروه ارزیابی را انتخاب کنید</option>';
        document.getElementById('checklist_id').disabled = true;
        document.getElementById('file-upload-hint').textContent = 'فرمت‌های مجاز: PDF, Word, Excel, JPG/PNG | حداکثر 20 مگابایت هر فایل | حداکثر 10 فایل';
    }}

    // ========== ویرایش/حذف رکورد ==========
    async function editRecord(id) {{
        try {{
            const res = await fetch('/module/supervisor/rounds/get/' + id);
            const data = await res.json();
            if (data.success) {{
                const r = data.record;
                document.getElementById('edit_id').value = r.ID_arziabi_bakhsh;
                document.getElementById('dept_id').value = r.id_nam_bakhsh;
                document.getElementById('title_id').value = r.id_onvan_arziabi;
                await loadChecklistItems();
                setTimeout(() => {{
                    document.getElementById('checklist_id').value = r.id_ckeklist;
                    updateItemInfo();
                    document.getElementById('score').value = r.emtiaz;
                    document.getElementById('positive_notes').value = r.nokhat_mosbat || '';
                    document.getElementById('negative_notes').value = r.nokat_manfi || '';
                    document.getElementById('description').value = r.tozihat || '';
                }}, 500);
                editingId = r.ID_arziabi_bakhsh;
                existingFiles = r.sanad ? r.sanad.split(',').filter(f => f) : [];
                loadExistingFiles(r.ID_arziabi_bakhsh);
                switchTab('form');
                window.scrollTo(0,0);
            }} else showToast('خطا در دریافت اطلاعات', 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    async function deleteRecord(id) {{
        if (!confirm('از حذف این رکورد اطمینان دارید؟')) return;
        try {{
            const res = await fetch('/module/supervisor/rounds/delete/' + id, {{ method:'POST' }});
            const data = await res.json();
            if (data.success) {{
                showToast('✅ حذف شد', 'success');
                if (editingId == id) clearForm();
                fetchRecordsList();
            }} else showToast('⛔ ' + data.message, 'error');
        }} catch(e) {{ showToast('خطا', 'error'); }}
    }}

    // ========== لیست رکوردها ==========
    async function fetchRecordsList() {{
        try {{
            const res = await fetch('/module/supervisor/rounds/list/{shift_id}');
            const data = await res.json();
            if (data.success) renderRecordsList(data.records);
        }} catch(e) {{ console.error(e); }}
    }}

    function renderRecordsList(records) {{
        const div = document.getElementById('records-list');
        if (!records.length) {{
            div.innerHTML = '<p style="text-align:center;color:var(--light-gray);">رکوردی ثبت نشده است</p>';
            return;
        }}
        let html = '';
        records.forEach(r => {{
            html += `<div class="record-item">
                <div class="r-info">
                    <div class="r-title">🏥 ${{r.nam_bakhsh}} | 📝 ${{r.nam_item}} | ⭐ ${{r.emtiaz}}</div>
                </div>
                <div class="record-actions">
                    <button class="btn btn-sm btn-primary" onclick="editRecord(${{r.ID_arziabi_bakhsh}})">✏️ ویرایش</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteRecord(${{r.ID_arziabi_bakhsh}})">🗑️ حذف</button>
                </div>
            </div>`;
        }});
        div.innerHTML = html;
    }}

    // ========== شروع ==========
    document.addEventListener('DOMContentLoaded', () => {{
        fetchRecordsList();
        updateUploadHint();
    }});
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions (بدون تغییر)
# ==========================================

def save_round(user, form_data, files):
    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id')
    edit_id = form_data.get('edit_id') or None
    dept_id = form_data.get('dept_id')
    title_id = form_data.get('title_id')
    checklist_id = form_data.get('checklist_id')
    score = form_data.get('score', 0)
    positive = form_data.get('positive_notes', '')
    negative = form_data.get('negative_notes', '')
    description = form_data.get('description', '')
    existing_files_json = form_data.get('existing_files', '[]')

    try:
        existing_files = json.loads(existing_files_json)
    except:
        existing_files = []

    if not dept_id or not title_id or not checklist_id:
        return {'success': False, 'message': 'بخش، گروه و سنجه الزامی است'}

    # دریافت وزن از سنجه برای محاسبه nomreh_kol
    item = query("SELECT vazn_sanjeh FROM tbl_arziabi_cheklist WHERE ID_cheklist=%s", (checklist_id,), fetch_one=True)
    weight = float(item['vazn_sanjeh']) if item else 1
    total_score = round(float(score) * weight, 2)

    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()

    conn = get_connection()
    cursor = conn.cursor()
    try:
        if edit_id:
            cursor.execute("""
                UPDATE tbl_arziabi_bakhsh SET
                    emtiaz=%s, nomreh_kol=%s, id_ckeklist=%s, id_nam_bakhsh=%s,
                    id_onvan_arziabi=%s, nokat_manfi=%s, nokhat_mosbat=%s,
                    tozihat=%s
                WHERE ID_arziabi_bakhsh=%s
            """, (score, total_score, checklist_id, dept_id, title_id, negative, positive, description, edit_id))
            record_id = int(edit_id)
        else:
            # بررسی تکراری
            dup = query("SELECT COUNT(*) as cnt FROM tbl_arziabi_bakhsh WHERE id_shift=%s AND id_nam_bakhsh=%s AND id_ckeklist=%s",
                        (shift_id, dept_id, checklist_id), fetch_one=True)
            if dup and dup['cnt'] > 0:
                return {'success': False, 'message': 'این سنجه قبلاً برای این بخش در این شیفت ثبت شده است'}

            cursor.execute("""
                INSERT INTO tbl_arziabi_bakhsh
                (dat_sabt, emtiaz, nomreh_kol, id_ckeklist, id_nam_bakhsh,
                 id_onvan_arziabi, id_shift, nokat_manfi, nokhat_mosbat,
                 tozihat, UserID, zaman_sabt, sanad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '')
            """, (today, score, total_score, checklist_id, dept_id, title_id, shift_id,
                  negative, positive, description, user_id, now))
            record_id = cursor.lastrowid

        # مدیریت فایل‌ها
        saved_new = []
        if files:
            record_dir = os.path.join(UPLOAD_DIR, str(record_id))
            os.makedirs(record_dir, exist_ok=True)
            for f in files.getlist('files'):
                if f.filename:
                    fname = secure_filename(f.filename)
                    f.save(os.path.join(record_dir, fname))
                    saved_new.append(f"{UPLOAD_DIR}/{record_id}/{fname}")

        all_files = existing_files + saved_new
        sanad_str = ','.join(all_files) if all_files else ''
        cursor.execute("UPDATE tbl_arziabi_bakhsh SET sanad=%s WHERE ID_arziabi_bakhsh=%s", (sanad_str, record_id))
        conn.commit()
       
        log_crud('save_round', user_id, key_value=record_id,
                 new_value=f"بخش:{dept_id}, سنجه:{checklist_id}, امتیاز:{score}")       
        
        return {'success': True, 'message': 'راند با موفقیت ثبت شد', 'record_id': record_id}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'خطا: {str(e)}'}
    finally:
        cursor.close()
        conn.close()


def get_round_record(record_id):
    rec = query("SELECT * FROM tbl_arziabi_bakhsh WHERE ID_arziabi_bakhsh=%s", (record_id,), fetch_one=True)
    if not rec:
        return {'success': False, 'message': 'رکورد یافت نشد'}
    for k in list(rec.keys()):
        if isinstance(rec[k], bytearray):
            rec[k] = rec[k].decode('utf-8')
    return {'success': True, 'record': rec}

def delete_round(user, record_id):
    user_id = user.get('UserID', 0)
    try:
        query("DELETE FROM tbl_arziabi_bakhsh WHERE ID_arziabi_bakhsh=%s", (record_id,), commit=True)
        log_crud('delete_round', user_id, key_value=record_id)
        return {'success': True, 'message': 'رکورد حذف شد'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def delete_round_file(form_data):
    record_id = form_data.get('record_id')
    file_index = int(form_data.get('file_index', 0))
    rec = query("SELECT sanad FROM tbl_arziabi_bakhsh WHERE ID_arziabi_bakhsh=%s", (record_id,), fetch_one=True)
    if not rec or not rec['sanad']:
        return {'success': False, 'message': 'فایلی وجود ندارد'}
    files = rec['sanad'].split(',')
    if file_index < 0 or file_index >= len(files):
        return {'success': False, 'message': 'فایل نامعتبر'}
    # حذف فایل از دیسک
    try:
        os.remove(files[file_index])
    except:
        pass
    # حذف از لیست
    del files[file_index]
    new_sanad = ','.join(files) if files else ''
    query("UPDATE tbl_arziabi_bakhsh SET sanad=%s WHERE ID_arziabi_bakhsh=%s", (new_sanad, record_id), commit=True)
    return {'success': True, 'files': files}


def get_rounds_list(shift_id):
    records = query("""
        SELECT b.*, c.nam_item, d.nam_bakhsh
        FROM tbl_arziabi_bakhsh b
        JOIN tbl_arziabi_cheklist c ON b.id_ckeklist = c.ID_cheklist
        JOIN tbl_bakhsh d ON b.id_nam_bakhsh = d.ID_nam_bakhsh
        WHERE b.id_shift = %s
        ORDER BY b.ID_arziabi_bakhsh DESC
    """, params=(shift_id,), fetch_all=True) or []
    return {'success': True, 'records': records}


def get_checklist_items_api(title_id):
    items = query(
        "SELECT ID_cheklist, nam_item, nomreh, vazn_sanjeh, sath, imani_chek, rahnamii, adres_sanjeh FROM tbl_arziabi_cheklist WHERE id_onvan_arziabi = %s",
        params=(title_id,), fetch_all=True
    ) or []
    return {'success': True, 'items': items}
    