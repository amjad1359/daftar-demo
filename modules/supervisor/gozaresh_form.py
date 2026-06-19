"""
فرم گزارش سوپروایزر – نسخه نهایی با صفحه‌بندی
رفع مشکل آپلود فایل در حالت ویرایش + پیمایش در کارتابل
"""

import os, json, jdatetime, shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from models.database import query, get_connection

UPLOAD_DIR = "uploads/gozaresh"


def get_gozaresh_form(user):
    """صفحه اصلی فرم گزارش سوپروایزر"""
    
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')
    
    # دریافت شیفت فعال
    shift = query("SELECT ID_shift, tarkib, dat_sabt FROM shift_namt ORDER BY ID_shift DESC LIMIT 1", fetch_one=True)
    
    if not shift:
        return '''<div class="card" style="text-align:center;padding:60px;">
            <div style="font-size:64px;">⚠️</div>
            <h3>شیفت فعالی یافت نشد</h3>
            <a href="/module/supervisor/shift" class="btn btn-primary">📅 ثبت شیفت</a></div>'''
    
    shift_id = shift['ID_shift']
    shift_name = shift['tarkib']
    
    # تاریخ شیفت
    shift_date = str(shift.get('dat_sabt', ''))
    if len(shift_date) == 8:
        shift_date_display = f"{shift_date[:4]}/{shift_date[4:6]}/{shift_date[6:]}"
    else:
        shift_date_display = jdatetime.date.today().strftime("%Y/%m/%d")
    
    # لود dropdown ها
    titles = query("SELECT ID_onvan_gozaresh, nam_onvan_gozaresh FROM tbl_onvan_gozaresh ORDER BY nam_onvan_gozaresh", fetch_all=True) or []
    title_options = '<option value="">--- انتخاب عنوان ---</option>'
    for t in titles:
        title_options += f'<option value="{t["ID_onvan_gozaresh"]}">{t["nam_onvan_gozaresh"]}</option>'

    depts = query("SELECT ID_nam_modirit, nam_modiriat FROM tbl_nam_modiriat ORDER BY nam_modiriat", fetch_all=True) or []
    dept_options = '<option value="">--- انتخاب واحد ---</option>'
    for d in depts:
        dept_options += f'<option value="{d["ID_nam_modirit"]}">{d["nam_modiriat"]}</option>'

    html = f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>گزارش سوپروایزر | {shift_name}</title>
<style>
    :root {{
        --primary: #6366f1; --primary-dark: #4f46e5; --primary-light: #818cf8;
        --success: #10b981; --success-light: #d1fae5; --danger: #ef4444;
        --danger-light: #fee2e2; --warning: #f59e0b; --warning-light: #fef3c7;
        --info: #3b82f6; --info-light: #dbeafe; --dark: #1e293b;
        --gray: #64748b; --gray-light: #94a3b8; --border: #e2e8f0;
        --bg: #f8fafc; --bg-dark: #f1f5f9; --surface: #ffffff;
        --radius-sm: 8px; --radius: 12px; --radius-lg: 16px;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1);
        --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial, sans-serif; background:transparent; color:var(--dark); line-height:1.6; }}

    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}
    @keyframes spin {{ to {{ transform:rotate(360deg); }} }}

    .page-header {{
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white; border-radius: var(--radius-lg); padding: 25px 30px;
        margin-bottom: 25px; display: flex; justify-content: space-between;
        align-items: center; box-shadow: 0 8px 30px rgba(79, 70, 229, 0.25);
    }}
    .page-header-left h2 {{ font-size: 22px; margin: 0 0 5px 0; font-weight: 700; }}
    .page-header-left p {{ opacity: 0.85; font-size: 13px; margin: 0; }}
    .page-header-right {{ display: flex; align-items: center; gap: 15px; }}
    .shift-badge {{
        background: rgba(255,255,255,0.15); border-radius: 30px; padding: 10px 20px;
        font-size: 14px; font-weight: bold; border: 1px solid rgba(255,255,255,0.2);
    }}
    .back-btn {{
        color: white; text-decoration: none; padding: 8px 16px;
        border: 1.5px solid rgba(255,255,255,0.4); border-radius: 10px;
        font-size: 13px; font-weight: 600; transition: var(--transition);
    }}
    .back-btn:hover {{ background: rgba(255,255,255,0.15); }}

    .card {{ background:var(--surface); border-radius:var(--radius-lg); padding:20px; border:1px solid var(--border); box-shadow:var(--shadow-sm); margin-bottom:16px; }}
    .card-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding-bottom:12px; border-bottom:2px solid var(--border); }}
    .card-title {{ font-size:16px; font-weight:700; color:var(--dark); display:flex; align-items:center; gap:8px; }}
    .card-badge {{ font-size:10px; padding:3px 10px; border-radius:15px; font-weight:600; background:var(--info-light); color:var(--info); }}

    .tabs {{ display:flex; gap:4px; margin-bottom:16px; border-bottom:2px solid var(--border); }}
    .tab {{ padding:10px 20px; font-size:13px; font-weight:600; border:none; background:none; color:var(--gray-light); cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-2px; transition:var(--transition); font-family:inherit; }}
    .tab:hover {{ color:var(--dark); }}
    .tab.active {{ color:var(--primary); border-bottom-color:var(--primary); }}
    .tab-content {{ display:none; animation:fadeIn 0.3s ease; }}
    .tab-content.active {{ display:block; }}

    .main-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
    @media (max-width:900px) {{ .main-grid {{ grid-template-columns:1fr; }} }}

    .form-group {{ margin-bottom:14px; }}
    .form-label {{ display:block; font-size:12px; font-weight:600; color:var(--gray); margin-bottom:5px; }}
    .form-select, .form-input, .form-textarea {{ width:100%; padding:10px 13px; border:2px solid var(--border); border-radius:var(--radius-sm); font-size:13px; font-family:inherit; transition:var(--transition); background:var(--surface); color:var(--dark); }}
    .form-select:focus, .form-input:focus, .form-textarea:focus {{ border-color:var(--primary-light); outline:none; box-shadow:0 0 0 3px rgba(99,102,241,0.1); }}
    .form-textarea {{ min-height:90px; resize:vertical; }}
    .form-row {{ display:flex; gap:8px; align-items:flex-end; flex-wrap:wrap; }}
    .form-input.error {{ border-color: var(--danger); background: #fef2f2; }}

    .btn {{ display:inline-flex; align-items:center; justify-content:center; gap:5px; padding:10px 18px; border:none; border-radius:var(--radius-sm); font-size:13px; font-weight:600; cursor:pointer; transition:var(--transition); font-family:inherit; white-space:nowrap; text-decoration:none; }}
    .btn-primary {{ background:var(--primary); color:white; }} .btn-primary:hover {{ background:var(--primary-dark); }}
    .btn-success {{ background:var(--success); color:white; }} .btn-success:hover {{ background:#059669; }}
    .btn-warning {{ background:var(--warning); color:white; }} .btn-warning:hover {{ background:#d97706; }}
    .btn-danger {{ background:var(--danger); color:white; }} .btn-danger:hover {{ background:#dc2626; }}
    .btn-ghost {{ background:transparent; color:var(--gray); border:2px solid var(--border); }}
    .btn-ghost:hover {{ border-color:var(--primary-light); color:var(--primary); }}
    .btn-sm {{ padding:6px 12px; font-size:11px; }}
    .btn-block {{ width:100%; }}
    .btn:disabled {{ opacity: 0.6; cursor: not-allowed; }}

    .file-upload-box {{
        border: 2px dashed var(--border); border-radius: var(--radius); padding: 20px;
        text-align: center; cursor: pointer; transition: all 0.3s ease; background: var(--bg);
    }}
    .file-upload-box:hover {{ border-color: var(--primary-light); background: #eef2ff; }}
    .file-upload-box.dragover {{ border-color: var(--primary); background: #e0e7ff; }}
    .file-upload-box input[type="file"] {{ display:none; }}
    .file-upload-icon {{ font-size: 36px; margin-bottom: 8px; }}
    .file-upload-text {{ color: var(--gray); font-size: 13px; }}
    .file-upload-hint {{ color: var(--gray-light); font-size: 11px; margin-top: 5px; }}

    .files-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(170px,1fr)); gap:8px; margin-top:12px; }}
    .file-card {{
        background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-sm);
        padding:10px; display:flex; align-items:center; gap:10px; transition:all 0.2s ease;
    }}
    .file-card:hover {{ border-color:var(--primary-light); }}
    .file-card-icon {{ font-size:24px; width:40px; height:40px; display:flex; align-items:center; justify-content:center; background:var(--bg-dark); border-radius:8px; flex-shrink:0; }}
    .file-card-info {{ flex:1; min-width:0; }}
    .file-card-name {{ font-size:11px; font-weight:600; color:var(--dark); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .file-card-size {{ font-size:9px; color:var(--gray); margin-top:2px; }}
    .file-card-del {{
        width:20px; height:20px; border-radius:50%; background:var(--danger); color:white;
        border:none; cursor:pointer; font-size:8px; display:flex; align-items:center;
        justify-content:center; opacity:0; transition:all 0.2s; flex-shrink:0;
    }}
    .file-card:hover .file-card-del {{ opacity:1; }}

    .report-list {{ max-height:450px; overflow-y:auto; }}
    .report-item {{ background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-sm); padding:14px; margin-bottom:8px; border-right:4px solid transparent; transition:var(--transition); }}
    .report-item:hover {{ border-color:var(--primary-light); }}
    .report-item.draft {{ border-right-color:var(--warning); }}
    .report-item.sent {{ border-right-color:var(--success); }}
    .report-title {{ font-size:13px; font-weight:600; }}
    .report-id {{ font-size:10px; color:var(--gray-light); font-family:monospace; }}
    .report-meta {{ font-size:10px; color:var(--gray); margin:4px 0; display:flex; gap:10px; flex-wrap:wrap; }}
    .report-actions {{ display:flex; gap:4px; justify-content:flex-end; margin-top:8px; }}
    .status-badge {{ font-size:9px; padding:2px 8px; border-radius:8px; font-weight:600; }}
    .status-draft {{ background:var(--warning-light); color:#92400e; }}
    .status-sent {{ background:var(--success-light); color:#065f46; }}

    .search-box {{ position:relative; margin-bottom:10px; }}
    .search-box input {{ width:100%; padding:9px 12px 9px 35px; border:2px solid var(--border); border-radius:var(--radius-sm); font-size:12px; background:var(--bg); }}
    .search-icon {{ position:absolute; left:10px; top:50%; transform:translateY(-50%); font-size:14px; color:var(--gray-light); }}
    .filter-btns {{ display:flex; gap:4px; margin-bottom:10px; }}
    .filter-btn {{ padding:5px 12px; border-radius:15px; font-size:10px; font-weight:600; border:2px solid var(--border); background:var(--surface); color:var(--gray); cursor:pointer; transition:var(--transition); font-family:inherit; }}
    .filter-btn.active {{ background:var(--primary); color:white; border-color:var(--primary); }}

    .modal-overlay {{ position:fixed; inset:0; background:rgba(15,23,42,0.6); z-index:1000; display:flex; justify-content:center; align-items:flex-start; padding:20px; opacity:0; visibility:hidden; transition:all 0.3s; }}
    .modal-overlay.show {{ opacity:1; visibility:visible; }}
    .modal-content-wrapper {{
        background:var(--surface); border-radius:var(--radius-lg); padding:20px;
        width:100%; max-width:650px; max-height:85vh;
        display:flex; flex-direction:column; overflow:hidden;
        box-shadow:var(--shadow-xl); transform:translateY(-15px); transition:all 0.3s;
    }}
    .modal-overlay.show .modal-content-wrapper {{ transform:translateY(0); }}
    .modal-header {{ display:flex; justify-content:space-between; align-items:center; padding-bottom:10px; border-bottom:2px solid var(--border); flex-shrink:0; }}
    .modal-title {{ font-size:16px; font-weight:700; }}
    .modal-close {{ width:30px; height:30px; border-radius:8px; border:none; background:var(--bg-dark); color:var(--gray); cursor:pointer; font-size:14px; display:flex; align-items:center; justify-content:center; }}
    .modal-close:hover {{ background:var(--danger-light); color:var(--danger); }}
    
    .modal-scroll-body {{
        flex:1; overflow-y:auto; padding:15px 0;
        max-height: calc(85vh - 120px);
    }}
    
    .report-text-section {{
        max-height: 200px;
        overflow-y: auto;
        background: #f8fafc;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid var(--border);
    }}
    
    .files-section {{
        margin-top: 10px;
        padding: 12px;
        background: #f0fdf4;
        border-radius: 8px;
        border: 1px solid #bbf7d0;
    }}
    .files-section-title {{
        font-weight: 700;
        color: #065f46;
        margin-bottom: 8px;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .modal-footer {{ display:flex; gap:6px; padding-top:10px; border-top:1px solid var(--border); justify-content:flex-end; flex-shrink:0; }}

    .toast-box {{ position:fixed; top:16px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:6px; pointer-events:none; max-width:400px; width:calc(100%-32px); }}
    .toast {{ padding:12px 16px; border-radius:10px; color:white; font-size:13px; font-weight:600; display:flex; align-items:center; gap:8px; box-shadow:var(--shadow-xl); pointer-events:auto; animation:fadeIn 0.3s ease; }}
    .toast.ok {{ background:var(--success); }}
    .toast.err {{ background:var(--danger); }}
    .toast .tclose {{ cursor:pointer; opacity:0.7; font-size:14px; margin-right:auto; }}

    .empty {{ text-align:center; padding:40px; color:var(--gray-light); }}
    .spinner {{ width:16px; height:16px; border:2px solid rgba(255,255,255,0.3); border-top-color:white; border-radius:50%; animation:spin 0.6s linear infinite; display:inline-block; }}

    .info-row {{
        background: #f0f7ff;
        border-right: 4px solid #3b82f6;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 12px;
        color: #1e40af;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .pagination {{ display:flex; justify-content:center; gap:10px; margin-top:15px; }}
</style>
</head>
<body>

<div class="toast-box" id="toastBox"></div>

<!-- ========== مودال مشاهده ========== -->
<div class="modal-overlay" id="viewModal">
    <div class="modal-content-wrapper">
        <div class="modal-header">
            <h3 class="modal-title">مشاهده گزارش</h3>
            <button class="modal-close" onclick="closeViewModal()">✕</button>
        </div>
        <div class="modal-scroll-body" id="viewContent"></div>
    </div>
</div>

<!-- ========== مودال ویرایش ========== -->
<div class="modal-overlay" id="editModal">
    <div class="modal-content-wrapper">
        <div class="modal-header">
            <h3 class="modal-title">ویرایش گزارش</h3>
            <button class="modal-close" onclick="closeEditModal()">✕</button>
        </div>
        <div class="modal-scroll-body">
            <form id="editForm">
                <input type="hidden" id="editReportId">
                <div class="form-row">
                    <div class="form-group"><label class="form-label">واحد مدیریت</label><select id="editDeptId" class="form-select">{dept_options}</select></div>
                    <div class="form-group"><label class="form-label">موضوع</label><select id="editOnvanId" class="form-select">{title_options}</select></div>
                </div>
                <div class="form-group"><label class="form-label">شرح واقعه</label><textarea id="editMohtava" class="form-textarea" rows="3"></textarea></div>
                <div class="form-group"><label class="form-label">اقدامات اصلاحی</label><textarea id="editEghdam" class="form-textarea" rows="2"></textarea></div>
                <div class="form-group">
                    <label class="form-label">فایل ها</label>
                    <div id="editOldFiles"></div>
                    <div class="file-upload-box" id="editFileDropZone">
                        <input type="file" id="editFileInput" multiple accept=".pdf,.doc,.docx,.xlsx,.xls,.jpg,.jpeg,.png">
                        <div class="file-upload-icon">📁</div>
                        <div class="file-upload-text">افزودن فایل جدید</div>
                    </div>
                    <div class="files-grid" id="editNewFilesGrid"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-ghost btn-sm" onclick="closeEditModal()">انصراف</button>
                    <button type="button" class="btn btn-warning btn-sm" onclick="saveEdit('draft')">پیش نویس</button>
                    <button type="button" class="btn btn-success btn-sm" onclick="saveEdit('final')">ارسال</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- ========== هدر ========== -->
<div class="page-header">
    <div class="page-header-left">
        <h2>ثبت گزارش سوپروایزر</h2>
        <p>{full_name} | {shift_date_display}</p>
    </div>
    <div class="page-header-right">
        <div class="shift-badge">شیفت: {shift_name}</div>
        <a href="/module/supervisor" class="back-btn">بازگشت به منو</a>
    </div>
</div>

<!-- تب ها -->
<div class="tabs">
    <button class="tab active" onclick="switchTab('register')">ثبت گزارش</button>
    <button class="tab" onclick="switchTab('list')">کارتابل</button>
</div>

<!-- تب ثبت -->
<div id="tab-register" class="tab-content active">
    <div class="card">
        <div class="card-header">
            <div class="card-title">ثبت گزارش جدید</div>
        </div>
        <form id="reportForm">
            <div class="main-grid">
                <div>
                    <div class="form-group"><label class="form-label">واحد مدیریت *</label><select id="deptId" class="form-select">{dept_options}</select></div>
                    <div class="form-group">
                        <label class="form-label">موضوع *</label>
                        <div class="form-row">
                            <select id="onvanId" class="form-select" style="flex:1;">{title_options}</select>
                            <button type="button" class="btn btn-sm btn-primary" onclick="toggleNewTitle()">+</button>
                        </div>
                        <div id="newTitleBox" style="display:none;margin-top:5px;" class="form-row">
                            <input type="text" id="newTitleInput" class="form-input" placeholder="عنوان جدید...">
                            <button type="button" class="btn btn-sm btn-success" onclick="addNewTitle()">ثبت</button>
                        </div>
                    </div>
                    <div class="form-group"><label class="form-label">شرح واقعه *</label><textarea id="mohtava" class="form-textarea" rows="4" placeholder="شرح کامل واقعه..."></textarea></div>
                    <div class="form-group"><label class="form-label">اقدامات اصلاحی</label><textarea id="eghdam" class="form-textarea" rows="2" placeholder="اقدامات انجام شده..."></textarea></div>
                </div>
                <div>
                    <div class="form-group">
                        <label class="form-label">مستندات</label>
                        <div class="file-upload-box" id="fileDropZone">
                            <input type="file" id="fileInput" multiple accept=".pdf,.doc,.docx,.xlsx,.xls,.jpg,.jpeg,.png">
                            <div class="file-upload-icon">📂</div>
                            <div class="file-upload-text">فایل ها را اینجا رها کنید</div>
                            <div class="file-upload-hint">حداکثر 15 فایل | 20MB هر فایل</div>
                        </div>
                        <div class="files-grid" id="fileThumbsGrid"></div>
                        <div style="margin-top:8px;font-size:11px;color:var(--gray-light);">
                            <span id="fileCount">0</span> فایل | <span id="totalSize">0</span> MB
                        </div>
                    </div>
                    <div style="margin-top:12px;display:flex;flex-direction:column;gap:6px;">
                        <button type="button" class="btn btn-success btn-block" onclick="submitForm('final')" id="finalBtn">
                            <span id="finalText">ارسال نهایی</span><span id="finalSpinner" class="spinner" style="display:none;"></span>
                        </button>
                        <button type="button" class="btn btn-warning btn-block" onclick="submitForm('draft')" id="draftBtn">
                            <span id="draftText">ذخیره پیش نویس</span><span id="draftSpinner" class="spinner" style="display:none;"></span>
                        </button>
                    </div>
                </div>
            </div>
        </form>
    </div>
</div>

<!-- تب کارتابل -->
<div id="tab-list" class="tab-content">
    <div class="card">
        <div class="card-header"><div class="card-title">کارتابل گزارشات <span class="card-badge" id="reportCount">0</span></div></div>
        <div class="search-box"><span class="search-icon">🔍</span><input type="text" id="searchInput" placeholder="جستجو..." oninput="loadReports(1)"></div>
        <div class="filter-btns">
            <button class="filter-btn active" onclick="setFilter('all')">همه</button>
            <button class="filter-btn" onclick="setFilter('پیش نویس')">پیش نویس</button>
            <button class="filter-btn" onclick="setFilter('ارسال شده')">ارسال شده</button>
        </div>
        <div id="reportList"><div class="empty"><p>در حال بارگذاری...</p></div></div>
        <div id="pagination" class="pagination"></div>
    </div>
</div>

<script>
    var selectedFiles = [];
    var editOldFiles = [];
    var editNewFiles = [];
    var currentFilter = 'all';
    var editingId = null;
    var currentPage = 1;
    var totalPages = 1;
    
    var MAX_FILE_SIZE = 20 * 1024 * 1024;
    var MAX_FILES = 15;
    var ALLOWED_TYPES = ['pdf', 'doc', 'docx', 'xlsx', 'xls', 'jpg', 'jpeg', 'png'];

    function toast(msg, type) {{
        var box = document.getElementById('toastBox');
        var t = document.createElement('div');
        t.className = 'toast ' + (type==='ok'?'ok':'err');
        t.innerHTML = '<span>' + (type==='ok'?'OK':'ERR') + '</span><span>' + msg + '</span><span class="tclose" onclick="this.parentElement.remove()">x</span>';
        box.appendChild(t);
        setTimeout(function() {{ if(t.parentElement) t.remove(); }}, 4000);
    }}

    function getFileIcon(ext) {{
        var icons = {{'pdf':'PDF','doc':'DOC','docx':'DOC','xlsx':'XLS','xls':'XLS','jpg':'IMG','jpeg':'IMG','png':'IMG'}};
        return icons[ext] || 'FILE';
    }}

    function renderFilesGrid(gridId, files, showDelete, removeCallback) {{
        var grid = document.getElementById(gridId);
        if (!grid) return;
        if (!files.length) {{ grid.innerHTML = ''; return; }}
        
        var html = '';
        files.forEach(function(file, index) {{
            var ext = file.name.split('.').pop().toLowerCase();
            var icon = getFileIcon(ext);
            var sizeKB = file.size / 1024;
            var sizeDisplay = sizeKB > 1024 ? (sizeKB/1024).toFixed(1)+' MB' : sizeKB.toFixed(1)+' KB';
            
            html += '<div class="file-card">';
            html += '<div class="file-card-icon">'+icon+'</div>';
            html += '<div class="file-card-info">';
            html += '<div class="file-card-name" title="'+file.name+'">'+file.name.substring(0,25)+(file.name.length>25?'...':'')+'</div>';
            html += '<div class="file-card-size">'+sizeDisplay+'</div>';
            html += '</div>';
            if (showDelete) {{
                html += '<button class="file-card-del" style="opacity:1;" onclick="'+removeCallback+'('+index+')">x</button>';
            }}
            html += '</div>';
        }});
        grid.innerHTML = html;
    }}

    function removeNewFile(index) {{
        selectedFiles.splice(index, 1);
        renderFilesGrid('fileThumbsGrid', selectedFiles, true, 'removeNewFile');
        updateFileInfo();
    }}

    function removeEditFile(index) {{
        editNewFiles.splice(index, 1);
        renderFilesGrid('editNewFilesGrid', editNewFiles, true, 'removeEditFile');
    }}

    function processFiles(fileList, filesArray, gridId, removeCallback) {{
        for (var i = 0; i < fileList.length; i++) {{
            var file = fileList[i];
            
            if (filesArray.length >= MAX_FILES) {{
                toast('حداکثر '+MAX_FILES+' فایل مجاز است', 'err');
                break;
            }}
            
            var ext = file.name.split('.').pop().toLowerCase();
            if (ALLOWED_TYPES.indexOf(ext) === -1) {{
                toast('فرمت "'+file.name+'" مجاز نیست', 'err');
                continue;
            }}
            
            if (file.size > MAX_FILE_SIZE) {{
                var mb = (file.size/(1024*1024)).toFixed(1);
                toast('حجم "'+file.name+'" ('+mb+'MB) بیش از حد مجاز است', 'err');
                continue;
            }}
            
            var dup = filesArray.some(function(f) {{ return f.name===file.name && f.size===file.size; }});
            if (!dup) {{
                filesArray.push(file);
            }}
        }}
        
        renderFilesGrid(gridId, filesArray, true, removeCallback);
        if (filesArray === selectedFiles) updateFileInfo();
    }}

    function updateFileInfo() {{
        document.getElementById('fileCount').textContent = selectedFiles.length;
        var total = (selectedFiles.reduce(function(s,f){{return s+f.size;}},0)/(1024*1024)).toFixed(2);
        document.getElementById('totalSize').textContent = total;
    }}

    function setupDropZone(dropZoneId, inputId, filesArray, gridId, removeCallback) {{
        var zone = document.getElementById(dropZoneId);
        if (!zone) return;
        
        zone.addEventListener('click', function() {{
            document.getElementById(inputId).click();
        }});
        
        zone.addEventListener('dragover', function(e) {{
            e.preventDefault();
            zone.classList.add('dragover');
        }});
        
        zone.addEventListener('dragleave', function() {{
            zone.classList.remove('dragover');
        }});
        
        zone.addEventListener('drop', function(e) {{
            e.preventDefault();
            zone.classList.remove('dragover');
            processFiles(e.dataTransfer.files, filesArray, gridId, removeCallback);
        }});
        
        document.getElementById(inputId).addEventListener('change', function() {{
            if (this.files && this.files.length > 0) {{
                processFiles(this.files, filesArray, gridId, removeCallback);
                this.value = '';
            }}
        }});
    }}

    function switchTab(tab) {{
        document.querySelectorAll('.tab').forEach(function(t,i) {{
            t.classList.toggle('active', (tab==='register'&&i===0)||(tab==='list'&&i===1));
        }});
        document.getElementById('tab-register').classList.toggle('active', tab==='register');
        document.getElementById('tab-list').classList.toggle('active', tab==='list');
        if (tab==='list') loadReports(1);
    }}

    function toggleNewTitle() {{
        var box = document.getElementById('newTitleBox');
        box.style.display = box.style.display==='none'?'flex':'none';
    }}

    async function addNewTitle() {{
        var title = document.getElementById('newTitleInput').value.trim();
        if (!title) {{ toast('عنوان را وارد کنید', 'err'); return; }}
        
        try {{
            var fd = new FormData(); fd.append('title', title);
            var r = await fetch('/module/supervisor/gozaresh/add_title', {{method:'POST', body:fd}});
            var d = await r.json();
            
            if (d.success) {{
                toast('عنوان اضافه شد', 'ok');
                var opt = '<option value="'+d.id+'" selected>'+d.title+'</option>';
                ['onvanId','editOnvanId'].forEach(function(id) {{
                    var el = document.getElementById(id);
                    if (el) el.innerHTML += opt;
                }});
                document.getElementById('newTitleInput').value = '';
                document.getElementById('newTitleBox').style.display = 'none';
            }} else {{
                toast(d.message, 'err');
            }}
        }} catch(e) {{
            toast('خطا در ارتباط با سرور', 'err');
        }}
    }}

    function resetFullForm() {{
        var form = document.getElementById('reportForm');
        form.reset();
        
        selectedFiles = [];
        
        var fileGrid = document.getElementById('fileThumbsGrid');
        if (fileGrid) fileGrid.innerHTML = '';
        
        var oldFileInput = document.getElementById('fileInput');
        if (oldFileInput) {{
            var newFileInput = document.createElement('input');
            newFileInput.type = 'file';
            newFileInput.id = 'fileInput';
            newFileInput.multiple = true;
            newFileInput.accept = '.pdf,.doc,.docx,.xlsx,.xls,.jpg,.jpeg,.png';
            newFileInput.style.display = 'none';
            
            oldFileInput.parentNode.replaceChild(newFileInput, oldFileInput);
            
            newFileInput.addEventListener('change', function() {{
                if (this.files && this.files.length > 0) {{
                    processFiles(this.files, selectedFiles, 'fileThumbsGrid', 'removeNewFile');
                    this.value = '';
                }}
            }});
        }}
        
        var mohtava = document.getElementById('mohtava');
        if (mohtava) mohtava.classList.remove('error');
        
        document.getElementById('fileCount').textContent = '0';
        document.getElementById('totalSize').textContent = '0';
        
        document.getElementById('newTitleBox').style.display = 'none';
        
        var dropZone = document.getElementById('fileDropZone');
        if (dropZone) dropZone.classList.remove('dragover');
        
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    async function submitForm(type) {{
        var dept = document.getElementById('deptId').value;
        var onvan = document.getElementById('onvanId').value;
        var mohtava = document.getElementById('mohtava').value.trim();
        
        if (!dept || !onvan || !mohtava) {{
            toast('فیلدهای ستاره دار را پر کنید', 'err');
            if (!mohtava) document.getElementById('mohtava').classList.add('error');
            return;
        }}
        
        document.getElementById('mohtava').classList.remove('error');
        
        var textId = type==='final'?'finalText':'draftText';
        var spinId = type==='final'?'finalSpinner':'draftSpinner';
        var btnId = type==='final'?'finalBtn':'draftBtn';
        
        document.getElementById(textId).style.display = 'none';
        document.getElementById(spinId).style.display = 'inline-block';
        document.getElementById(btnId).disabled = true;

        var fd = new FormData();
        fd.append('shift_id', '{shift_id}');
        fd.append('date', '{shift_date_display}');
        fd.append('dept_id', dept);
        fd.append('onvan_id', onvan);
        fd.append('mohtava', mohtava);
        fd.append('eghdam', document.getElementById('eghdam').value);
        fd.append('type', type);
        fd.append('existing_files', '[]');
        
        selectedFiles.forEach(function(f) {{
            fd.append('files', f, f.name);
        }});

        try {{
            var r = await fetch('/module/supervisor/gozaresh/save', {{method:'POST', body:fd}});
            var d = await r.json();
            
            if (d.success) {{
                toast(d.message + ' OK', 'ok');
                resetFullForm();
                loadReports(1);
            }} else {{
                toast(d.message, 'err');
            }}
        }} catch(e) {{
            toast('خطا در ارتباط با سرور', 'err');
        }}
        
        document.getElementById(textId).style.display = 'inline';
        document.getElementById(spinId).style.display = 'none';
        document.getElementById(btnId).disabled = false;
    }}

    async function loadReports(page = 1) {{
        var search = document.getElementById('searchInput').value;
        var status = currentFilter === 'all' ? 'all' : currentFilter;
        
        try {{
            var r = await fetch('/module/supervisor/gozaresh/list?search='+encodeURIComponent(search)+'&status='+status+'&page='+page+'&per_page=15');
            var d = await r.json();
            
            var container = document.getElementById('reportList');
            document.getElementById('reportCount').textContent = d.total + ' گزارش';
            totalPages = Math.ceil(d.total / d.per_page);
            currentPage = d.page;
            
            if (!d.records || d.records.length === 0) {{
                container.innerHTML = '<div class="empty"><p>گزارشی یافت نشد</p></div>';
                document.getElementById('pagination').innerHTML = '';
                return;
            }}
            
            var html = '';
            d.records.forEach(function(r) {{
                var isDraft = r.statuse === 'پیش نویس';
                html += '<div class="report-item '+(isDraft?'draft':'sent')+'">';
                html += '<div style="display:flex;justify-content:space-between;align-items:center;">';
                html += '<span class="report-title">'+(r.nam_onvan_gozaresh||'')+'</span>';
                html += '<span class="report-id">#'+r.ID_gozaresh+'</span>';
                html += '</div>';
                html += '<div class="report-meta">';
                html += '<span>'+(r.nam_modiriat||'')+'</span>';
                html += '<span>'+(r.dat_sabt||'')+'</span>';
                html += '<span class="status-badge '+(isDraft?'status-draft':'status-sent')+'">'+r.statuse+'</span>';
                html += '</div>';
                html += '<div class="report-actions">';
                if (isDraft) {{
                    html += '<button class="btn btn-sm btn-primary" onclick="openEdit('+r.ID_gozaresh+')">ویرایش</button>';
                }} else {{
                    html += '<button class="btn btn-sm btn-ghost" onclick="openView('+r.ID_gozaresh+')">مشاهده</button>';
                }}
                html += '<button class="btn btn-sm btn-danger" onclick="deleteReport('+r.ID_gozaresh+')">حذف</button>';
                html += '</div></div>';
            }});
            container.innerHTML = html;
            
            // بروزرسانی صفحه‌بندی
            var pagHtml = '';
            if (currentPage > 1) {{
                pagHtml += '<button class="btn btn-sm btn-primary" onclick="loadReports('+(currentPage-1)+')">« قبلی</button>';
            }}
            pagHtml += '<span style="display:flex; align-items:center; font-size:13px;">صفحه '+currentPage+' از '+totalPages+'</span>';
            if (currentPage < totalPages) {{
                pagHtml += '<button class="btn btn-sm btn-primary" onclick="loadReports('+(currentPage+1)+')">بعدی »</button>';
            }}
            document.getElementById('pagination').innerHTML = pagHtml;
            
        }} catch(e) {{
            document.getElementById('reportList').innerHTML = '<div class="empty"><p>خطا در بارگذاری</p></div>';
        }}
    }}

    function setFilter(f) {{
        currentFilter = f;
        document.querySelectorAll('.filter-btn').forEach(function(b) {{
            b.classList.toggle('active', b.textContent.trim().includes(f==='all'?'همه':f));
        }});
        loadReports(1);
    }}

    async function openView(id) {{
        try {{
            var r = await fetch('/module/supervisor/gozaresh/get/'+id);
            var d = await r.json();
            if (!d.success) {{ toast('گزارش یافت نشد', 'err'); return; }}
            
            var rec = d.record;
            var html = '';
            
            html += '<div style="background:#f8fafc;padding:10px;border-radius:8px;margin-bottom:10px;display:flex;flex-wrap:wrap;gap:15px;font-size:12px;">';
            html += '<span><strong>واحد:</strong> '+(rec.nam_modiriat||'---')+'</span>';
            html += '<span><strong>موضوع:</strong> '+(rec.nam_onvan_gozaresh||'---')+'</span>';
            html += '<span><strong>تاریخ:</strong> '+(rec.dat_sabt_display||'---')+'</span>';
            html += '</div>';
            
            html += '<div class="report-text-section">';
            html += '<strong style="display:block;margin-bottom:5px;">شرح واقعه:</strong>';
            html += '<p style="white-space:pre-wrap;margin-top:5px;font-size:12px;line-height:1.8;">'+(rec.mohtava_gozaresh||'---')+'</p>';
            html += '</div>';
            
            if (rec.eghdam_eslahi_avlieh) {{
                html += '<div class="report-text-section" style="max-height:120px;margin-top:8px;">';
                html += '<strong style="display:block;margin-bottom:5px;">اقدام اصلاحی:</strong>';
                html += '<p style="white-space:pre-wrap;margin-top:5px;font-size:12px;">'+rec.eghdam_eslahi_avlieh+'</p>';
                html += '</div>';
            }}
            
            if (rec.mostanad) {{
                var files = rec.mostanad.split(',').filter(function(f){{return f;}});
                html += '<div class="files-section">';
                html += '<div class="files-section-title">فایل های پیوست شده ('+files.length+' فایل)</div>';
                html += '<div class="files-grid" style="max-height:250px;overflow-y:auto;">';
                files.forEach(function(f) {{
                    var name = f.split('/').pop();
                    var ext = name.split('.').pop().toLowerCase();
                    html += '<div class="file-card">';
                    html += '<div class="file-card-icon">'+getFileIcon(ext)+'</div>';
                    html += '<div class="file-card-info"><div class="file-card-name" title="'+name+'">'+name.substring(0,20)+'</div></div>';
                    html += '<a href="/'+f+'" target="_blank" class="btn btn-sm" style="background:var(--primary-light);color:white;text-decoration:none;flex-shrink:0;">دانلود</a>';
                    html += '</div>';
                }});
                html += '</div></div>';
            }} else {{
                html += '<div class="files-section" style="background:#f8fafc;border-color:#e2e8f0;">';
                html += '<div class="files-section-title" style="color:#64748b;">بدون فایل پیوست</div>';
                html += '</div>';
            }}
            
            document.getElementById('viewContent').innerHTML = html;
            document.getElementById('viewModal').classList.add('show');
        }} catch(e) {{ toast('خطا', 'err'); }}
    }}

    function closeViewModal() {{ document.getElementById('viewModal').classList.remove('show'); }}

    // ========== ویرایش ==========
    async function openEdit(id) {{
        try {{
            var r = await fetch('/module/supervisor/gozaresh/get/'+id);
            var d = await r.json();
            if (!d.success) {{ toast('گزارش یافت نشد', 'err'); return; }}
            
            var rec = d.record;
            editingId = rec.ID_gozaresh;
            document.getElementById('editReportId').value = rec.ID_gozaresh;
            document.getElementById('editDeptId').value = rec.nam_modirit;
            document.getElementById('editOnvanId').value = rec.onvan_gozaresh;
            document.getElementById('editMohtava').value = rec.mohtava_gozaresh || '';
            document.getElementById('editEghdam').value = rec.eghdam_eslahi_avlieh || '';
            
            editOldFiles = rec.mostanad ? rec.mostanad.split(',').filter(function(f){{return f;}}) : [];
            editNewFiles = [];
            
            renderOldFiles();
            document.getElementById('editNewFilesGrid').innerHTML = '';
            
            var oldEditInput = document.getElementById('editFileInput');
            if (oldEditInput) {{
                var newEditInput = document.createElement('input');
                newEditInput.type = 'file';
                newEditInput.id = 'editFileInput';
                newEditInput.multiple = true;
                newEditInput.accept = '.pdf,.doc,.docx,.xlsx,.xls,.jpg,.jpeg,.png';
                newEditInput.style.display = 'none';
                
                oldEditInput.parentNode.replaceChild(newEditInput, oldEditInput);
                
                newEditInput.addEventListener('change', function() {{
                    if (this.files && this.files.length > 0) {{
                        processFiles(this.files, editNewFiles, 'editNewFilesGrid', 'removeEditFile');
                        this.value = '';
                    }}
                }});
            }}
            
            document.getElementById('editModal').classList.add('show');
        }} catch(e) {{ toast('خطا', 'err'); }}
    }}

    function closeEditModal() {{ 
        document.getElementById('editModal').classList.remove('show'); 
        editingId = null; 
        editOldFiles = [];
        editNewFiles = [];
    }}

    function renderOldFiles() {{
        var container = document.getElementById('editOldFiles');
        if (!editOldFiles.length) {{ container.innerHTML = ''; return; }}
        
        var html = '<div style="font-weight:600;margin-bottom:8px;">فایل های قبلی:</div><div class="files-grid">';
        editOldFiles.forEach(function(f, i) {{
            var name = f.split('/').pop();
            var ext = name.split('.').pop().toLowerCase();
            html += '<div class="file-card">';
            html += '<div class="file-card-icon">'+getFileIcon(ext)+'</div>';
            html += '<div class="file-card-info"><div class="file-card-name">'+name.substring(0,20)+'</div></div>';
            html += '<a href="/'+f+'" target="_blank" class="btn btn-sm" style="background:var(--primary-light);color:white;text-decoration:none;">دانلود</a>';
            html += '<button class="file-card-del" style="opacity:1;" onclick="editOldFiles.splice('+i+',1);renderOldFiles();">x</button>';
            html += '</div>';
        }});
        html += '</div>';
        container.innerHTML = html;
    }}

    async function saveEdit(type) {{
        if (!editingId) return;
        
        var fd = new FormData();
        fd.append('edit_id', editingId);
        fd.append('dept_id', document.getElementById('editDeptId').value);
        fd.append('onvan_id', document.getElementById('editOnvanId').value);
        fd.append('mohtava', document.getElementById('editMohtava').value);
        fd.append('eghdam', document.getElementById('editEghdam').value);
        fd.append('type', type);
        fd.append('existing_files', JSON.stringify(editOldFiles));
        fd.append('shift_id', '{shift_id}');
        fd.append('date', '{shift_date_display}');
        
        editNewFiles.forEach(function(f) {{
            fd.append('files', f, f.name);
        }});

        try {{
            var r = await fetch('/module/supervisor/gozaresh/save', {{method:'POST', body:fd}});
            var d = await r.json();
            if (d.success) {{ 
                toast(d.message, 'ok'); 
                closeEditModal(); 
                loadReports(currentPage); 
            }}
            else toast(d.message, 'err');
        }} catch(e) {{ toast('خطا', 'err'); }}
    }}

    async function deleteReport(id) {{
        if (!confirm('آیا از حذف این گزارش اطمینان دارید؟')) return;
        
        try {{
            var r = await fetch('/module/supervisor/gozaresh/delete/'+id, {{method:'POST'}});
            var d = await r.json();
            if (d.success) {{ 
                toast(d.message, 'ok'); 
                if (editingId==id) closeEditModal(); 
                loadReports(currentPage); 
            }}
            else toast(d.message, 'err');
        }} catch(e) {{ toast('خطا', 'err'); }}
    }}

    document.addEventListener('DOMContentLoaded', function() {{
        loadReports(1);
        setupDropZone('fileDropZone', 'fileInput', selectedFiles, 'fileThumbsGrid', 'removeNewFile');
        setupDropZone('editFileDropZone', 'editFileInput', editNewFiles, 'editNewFilesGrid', 'removeEditFile');
    }});
    
    document.getElementById('viewModal').addEventListener('click', function(e) {{
        if (e.target === this) closeViewModal();
    }});
    document.getElementById('editModal').addEventListener('click', function(e) {{
        if (e.target === this) closeEditModal();
    }});
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{ closeEditModal(); closeViewModal(); }}
    }});
</script>
</body>
</html>'''
    return html


# ==========================================
# API Functions
# ==========================================

def save_report(user, form_data, files):
    """ذخیره گزارش با پشتیبانی کامل از آپلود فایل"""
    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id')
    edit_id = form_data.get('edit_id') or None
    dept_id = form_data.get('dept_id')
    onvan_id = form_data.get('onvan_id')
    date_str = form_data.get('date', '')
    mohtava = form_data.get('mohtava', '')
    eghdam = form_data.get('eghdam', '')
    report_type = form_data.get('type', 'draft')
    existing_files_json = form_data.get('existing_files', '[]')
    
    try:
        existing_files = json.loads(existing_files_json)
    except:
        existing_files = []

    if not mohtava or not onvan_id or not dept_id:
        return {'success': False, 'message': 'شرح واقعه، موضوع و واحد مدیریت الزامی است'}

    try:
        date_clean = date_str.replace('/', '')
        dat_sabt = int(date_clean) if len(date_clean) == 8 else int(jdatetime.date.today().strftime("%Y%m%d"))
    except:
        dat_sabt = int(jdatetime.date.today().strftime("%Y%m%d"))

    now = datetime.now()
    is_final = report_type == 'final'
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if edit_id:
            cursor.execute("""UPDATE tbl_gozaresh SET mohtava_gozaresh=%s, eghdam_eslahi_avlieh=%s,
                onvan_gozaresh=%s, nam_modirit=%s, dat_sabt=%s,
                ersal_gozaresh=%s, statuse=%s, Date_ersal=%s
                WHERE ID_gozaresh=%s""",
                (mohtava, eghdam, onvan_id, dept_id, dat_sabt,
                 1 if is_final else 0, "ارسال شده" if is_final else "پیش نویس",
                 now if is_final else None, edit_id))
            record_id = int(edit_id)
        else:
            cursor.execute("""INSERT INTO tbl_gozaresh
                (CreatedDate, dat_sabt, Date_ersal, mohtava_gozaresh, eghdam_eslahi_avlieh,
                 onvan_gozaresh, nam_modirit, taid_aval, ersal_gozaresh, statuse,
                 ID_shift, UserID, mostanad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s, %s, %s, %s, '')""",
                (now, dat_sabt, now if is_final else None, mohtava, eghdam, onvan_id, dept_id,
                 1 if is_final else 0, "ارسال شده" if is_final else "پیش نویس", shift_id, user_id))
            record_id = cursor.lastrowid

        saved_new = []
        if files:
            record_dir = os.path.join(UPLOAD_DIR, str(record_id))
            os.makedirs(record_dir, exist_ok=True)
            uploaded = files.getlist('files')
            for f in uploaded:
                if f and f.filename:
                    try:
                        fname = secure_filename(f.filename) or f"file_{datetime.now().strftime('%H%M%S%f')}.tmp"
                        filepath = os.path.join(record_dir, fname)
                        f.save(filepath)
                        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                            saved_new.append(f"{UPLOAD_DIR}/{record_id}/{fname}")
                    except Exception as e:
                        print(f"[ERROR] File save failed: {e}")
                        continue
        
        all_files = existing_files + saved_new
        mostanad_str = ','.join(all_files) if all_files else ''
        cursor.execute("UPDATE tbl_gozaresh SET mostanad=%s WHERE ID_gozaresh=%s", (mostanad_str, record_id))
        conn.commit()
        return {'success': True, 'message': 'گزارش با موفقیت ثبت شد', 'record_id': record_id, 'files_count': len(saved_new)}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'خطا: {str(e)}'}
    finally:
        cursor.close()
        conn.close()


def get_report(record_id):
    """دریافت اطلاعات یک گزارش"""
    rec = query("SELECT g.*, m.nam_modiriat, o.nam_onvan_gozaresh FROM tbl_gozaresh g LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit=m.ID_nam_modirit LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh=o.ID_onvan_gozaresh WHERE g.ID_gozaresh=%s", (record_id,), fetch_one=True)
    if not rec:
        return {'success': False, 'message': 'گزارش یافت نشد'}
    d = str(rec.get('dat_sabt', ''))
    rec['dat_sabt_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d
    for k in list(rec.keys()):
        if isinstance(rec[k], bytearray):
            rec[k] = rec[k].decode('utf-8')
    return {'success': True, 'record': rec}


def delete_report(user, record_id):
    """حذف گزارش"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) as cnt FROM tbl_pasokh_modir_javab WHERE kod_gozaresh=%s", (record_id,))
        if cursor.fetchone()[0] > 0:
            return {'success': False, 'message': 'این گزارش دارای پاسخ مدیر است و قابل حذف نیست'}
        cursor.execute("SELECT COUNT(*) as cnt FROM tbl_gozaresh_modir_parastari WHERE ID_gozaresh=%s", (record_id,))
        if cursor.fetchone()[0] > 0:
            return {'success': False, 'message': 'گزارش در کارتابل مدیر پرستاری ثبت شده است'}
        cursor.execute("DELETE FROM tbl_gozaresh WHERE ID_gozaresh=%s", (record_id,))
        conn.commit()
        shutil.rmtree(os.path.join(UPLOAD_DIR, str(record_id)), ignore_errors=True)
        return {'success': True, 'message': 'گزارش حذف شد'}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        cursor.close()
        conn.close()


def add_new_title(title):
    """افزودن عنوان جدید"""
    if not title or not title.strip():
        return {'success': False, 'message': 'عنوان نمی تواند خالی باشد'}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tbl_onvan_gozaresh (nam_onvan_gozaresh) VALUES (%s)", (title.strip(),))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return {'success': True, 'id': new_id, 'title': title.strip()}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def get_report_list(user, search, status, page=1, per_page=15):
    """دریافت لیست گزارشات با صفحه‌بندی"""
    user_id = user.get('UserID', 0)
    offset = (page - 1) * per_page

    sql = """SELECT g.ID_gozaresh, g.dat_sabt, g.statuse, o.nam_onvan_gozaresh, m.nam_modiriat
             FROM tbl_gozaresh g LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh=o.ID_onvan_gozaresh
             LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit=m.ID_nam_modirit WHERE g.UserID=%s"""
    params = [user_id]

    count_sql = "SELECT COUNT(*) as total FROM tbl_gozaresh g LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh=o.ID_onvan_gozaresh LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit=m.ID_nam_modirit WHERE g.UserID=%s"
    count_params = [user_id]

    if search:
        sql += " AND (o.nam_onvan_gozaresh LIKE %s OR m.nam_modiriat LIKE %s OR g.ID_gozaresh LIKE %s)"
        params.extend([f'%{search}%']*3)
        count_sql += " AND (o.nam_onvan_gozaresh LIKE %s OR m.nam_modiriat LIKE %s OR g.ID_gozaresh LIKE %s)"
        count_params.extend([f'%{search}%']*3)

    if status != 'all':
        sql += " AND g.statuse = %s"
        params.append(status)
        count_sql += " AND g.statuse = %s"
        count_params.append(status)

    sql += " ORDER BY g.CreatedDate DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    records = query(sql, params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0

    for r in records:
        d = str(r.get('dat_sabt', ''))
        r['dat_sabt'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d

    return {'success': True, 'records': records, 'total': total, 'page': page, 'per_page': per_page}
    
    
