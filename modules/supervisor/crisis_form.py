"""
فرم ثبت و مدیریت بحران (سوپروایزر) – Flask + AJAX
نسخه نهایی بدون خطاهای f-string
"""

import os, json, jdatetime, shutil, uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from models.database import query, get_connection
from utils.audit import log_action

UPLOAD_DIR = "uploads/crisis"

def get_crisis_form(user):
    """صفحه کامل مدیریت بحران (بدون تگ‌های html/body)"""
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', 'کاربر')

    shift = query(
        "SELECT ID_shift, tarkib FROM shift_namt ORDER BY ID_shift DESC LIMIT 1",
        fetch_one=True
    )
    if not shift:
        return '''<div class="card" style="text-align:center;padding:60px;">
            <h3>⚠️ شیفت فعالی یافت نشد</h3>
            <a href="/module/supervisor/shift" class="btn btn-primary">📅 ثبت شیفت</a></div>'''

    shift_id = shift['ID_shift']
    shift_name = shift['tarkib']

    # لیست عناوین بحران
    titles = query("SELECT ID_onvan_kod_o, nam_kod_o FROM tbl_onvan_kod_omomy ORDER BY nam_kod_o", fetch_all=True) or []
    title_options = '<option value="">--- انتخاب کنید ---</option>'
    for t in titles:
        title_options += f'<option value="{t["ID_onvan_kod_o"]}">{t["nam_kod_o"]}</option>'

    # سطوح بحران (برای چارت)
    levels = query("SELECT Id_sath_bohran, nam_sath_bohran FROM tbl_sath_bohran ORDER BY Id_sath_bohran", fetch_all=True) or []
    level_options = ''
    for lv in levels:
        level_options += f'<option value="{lv["Id_sath_bohran"]}">{lv["nam_sath_bohran"]}</option>'

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>فرم بحران</title>
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
        --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
        --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
        --bg: #f1f5f9; --white: #fff; --radius: 12px; --transition: 0.2s ease;
        --orange: #b45309; --orange-light: #d97706;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation: fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:1400px; margin:0 auto; padding:20px; }}

    .page-header {{
        background: linear-gradient(135deg, #b45309, #d97706);
        color:white; border-radius:16px; padding:22px 28px; margin-bottom:22px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(180,83,9,0.25);
    }}
    .page-header h2 {{ font-size:22px; margin:0 0 5px 0; }}
    .page-header p {{ opacity:0.85; font-size:13px; margin:0; }}
    .header-right {{ display:flex; align-items:center; gap:15px; }}
    .shift-badge {{
        background:rgba(255,255,255,0.15); padding:8px 18px; border-radius:25px;
        font-size:13px; font-weight:bold; border:1px solid rgba(255,255,255,0.2);
    }}
    .back-btn {{
        color:white; text-decoration:none; padding:8px 16px;
        border:1px solid rgba(255,255,255,0.4); border-radius:8px; font-size:13px;
    }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    .tabs {{ display:flex; gap:5px; margin-bottom:20px; border-bottom:2px solid var(--border); flex-wrap:wrap; }}
    .tab {{
        padding:10px 20px; font-size:13px; font-weight:600; border:none;
        background:none; color:var(--light-gray); cursor:pointer;
        border-bottom:2px solid transparent; transition:var(--transition); font-family:inherit;
    }}
    .tab:hover {{ color:var(--dark); }}
    .tab.active {{ color:var(--orange); border-bottom-color:var(--orange); }}
    .tab-content {{ display:none; }}
    .tab-content.active {{ display:block; animation:fadeIn 0.3s ease; }}

    .card {{
        background:var(--white); border-radius:var(--radius); padding:22px;
        border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:20px;
    }}
    .card-title {{
        font-size:15px; font-weight:bold; color:var(--dark); margin-bottom:16px;
        padding-bottom:10px; border-bottom:2px solid var(--border);
        display:flex; align-items:center; gap:8px;
    }}

    .main-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}

    .form-group {{ margin-bottom:14px; }}
    .form-group label {{ display:block; font-size:12px; font-weight:600; color:var(--gray); margin-bottom:5px; }}
    .form-select, .form-input, .form-textarea {{
        width:100%; padding:10px 12px; border:2px solid var(--border); border-radius:8px;
        font-size:13px; font-family:inherit; transition:var(--transition); background:var(--white);
    }}
    .form-select:focus, .form-input:focus, .form-textarea:focus {{
        border-color:var(--orange-light); outline:none; box-shadow:0 0 0 3px rgba(217,119,6,0.15);
    }}
    .form-textarea {{ min-height:80px; resize:vertical; }}
    .form-input:disabled, .form-select:disabled, .form-textarea:disabled {{
        background:#f1f5f9; color:#94a3b8; cursor:not-allowed;
    }}

    .row {{ display:flex; gap:8px; align-items:flex-end; flex-wrap:wrap; }}

    .time-input {{
        text-align:center; direction:ltr; letter-spacing:2px;
        font-family:'Courier New', monospace; font-size:15px; font-weight:bold;
    }}
    .time-input.invalid {{ border-color:var(--danger); background:#fef2f2; }}

    .btn {{
        display:inline-flex; align-items:center; justify-content:center; gap:5px;
        padding:9px 16px; border:none; border-radius:8px; font-size:13px;
        font-weight:600; cursor:pointer; font-family:inherit; transition:var(--transition);
        text-decoration:none;
    }}
    .btn-primary {{ background:var(--primary); color:white; }} .btn-primary:hover {{ background:var(--primary-light); }}
    .btn-success {{ background:var(--success); color:white; }} .btn-danger {{ background:var(--danger); color:white; }}
    .btn-warning {{ background:var(--warning); color:white; }} .btn-sm {{ padding:5px 10px; font-size:11px; }}
    .btn-xs {{ padding:3px 7px; font-size:10px; border-radius:5px; }}
    .btn-block {{ width:100%; }}
    .btn:disabled {{ opacity:0.5; cursor:not-allowed; }}

    .person-item {{
        display:flex; align-items:center; gap:8px; background:var(--bg);
        border:1px solid var(--border); padding:8px 10px; border-radius:8px;
        margin-bottom:5px; border-right:3px solid var(--danger);
    }}
    .person-info {{ flex:1; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
    .person-name {{ font-weight:bold; font-size:12px; min-width:120px; }}
    .person-phone {{ font-size:11px; color:var(--gray); direction:ltr; }}
    .person-addr {{ font-size:10px; color:var(--light-gray); max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}

    .file-upload-box {{
        border:2px dashed var(--border); border-radius:10px; padding:15px;
        text-align:center; cursor:pointer; transition:all 0.3s ease; background:var(--bg);
        margin-top:10px;
    }}
    .file-upload-box:hover {{ border-color:var(--orange-light); background:#fff7ed; }}
    .file-upload-box input[type="file"] {{ display:none; }}

    .files-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(130px,1fr)); gap:8px; margin-top:10px; }}
    .file-card {{
        background:var(--white); border:1px solid var(--border); border-radius:8px;
        padding:8px; display:flex; align-items:center; gap:6px; transition:all 0.2s ease;
    }}
    .file-card:hover {{ border-color:var(--orange-light); }}
    .file-card-icon {{
        font-size:20px; width:32px; height:32px; display:flex; align-items:center;
        justify-content:center; background:var(--bg); border-radius:6px; flex-shrink:0;
    }}
    .file-card-img {{ width:32px; height:32px; object-fit:cover; border-radius:4px; }}
    .file-card-name {{ font-size:9px; color:var(--dark); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}

    .notification {{
        padding:10px 15px; border-radius:8px; margin-bottom:15px; font-size:12px;
        display:none; border-right:4px solid;
    }}
    .notification.info {{ background:#dbeafe; border-color:#3b82f6; color:#1e40af; }}
    .notification.danger {{ background:#fee2e2; border-color:#ef4444; color:#991b1b; }}

    .filter-row {{ display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap; }}
    .report-item {{
        background:var(--white); border:1px solid var(--border); border-radius:10px;
        padding:14px; margin-bottom:8px; transition:var(--transition);
        display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;
    }}
    .report-item.locked {{ border-right:4px solid var(--danger); background:#fef2f2; }}
    .report-item .r-info {{ flex:1; }}
    .report-item .r-title {{ font-weight:bold; font-size:13px; }}
    .report-item .r-meta {{
        font-size:11px; color:var(--gray); margin-top:3px;
        display:flex; gap:10px; flex-wrap:wrap;
    }}
    .report-item .r-actions {{ display:flex; gap:5px; }}
    .badge {{
        padding:2px 8px; border-radius:10px; font-size:9px; font-weight:600; color:white;
    }}
    .badge-locked {{ background:var(--danger); }}
    .badge-active {{ background:var(--success); }}

    .empty-state {{ text-align:center; padding:40px; color:var(--light-gray); }}

    .toast-box {{
        position:fixed; top:16px; left:50%; transform:translateX(-50%); z-index:10000;
        display:flex; flex-direction:column; gap:8px; pointer-events:none;
    }}
    .toast {{
        padding:12px 18px; border-radius:10px; color:white; font-size:13px; font-weight:600;
        display:flex; align-items:center; gap:8px; box-shadow:0 8px 25px rgba(0,0,0,0.2);
        animation:slideDown 0.3s ease; pointer-events:auto;
    }}
    .toast.ok {{ background:var(--success); }}
    .toast.err {{ background:var(--danger); }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-25px); }} to {{ opacity:1; transform:translateY(0); }} }}

    @media (max-width:768px) {{
        .main-grid {{ grid-template-columns:1fr; }}
        .page-header {{ flex-direction:column; gap:12px; text-align:center; }}
        .report-item {{ flex-direction:column; align-items:flex-start; }}
    }}
</style>
</head>
<body>
<div class="toast-box" id="toastBox"></div>

<div class="container fade-in">

    <div class="page-header">
        <div>
            <h2>🚨 فرم بحران</h2>
            <p>{full_name} | شیفت: {shift_name}</p>
        </div>
        <div class="header-right">
            <div class="shift-badge">🕒 {shift_name}</div>
            <a href="/module/supervisor" class="back-btn">⬅️ بازگشت</a>
        </div>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="switchTab('form')">📝 ثبت و ویرایش گزارش</button>
        <button class="tab" onclick="switchTab('archive')">📂 آرشیو و مشاهده سوابق</button>
        <button class="tab" onclick="switchTab('sms-settings')">⚙️ تنظیمات پیامک</button>
    </div>

    <!-- ========== تب فرم ========== -->
    <div id="tab-form" class="tab-content active">
        <div class="notification info" id="edit-notify"></div>
        <div class="notification danger" id="locked-notify">🔒 این گزارش بایگانی شده و قابل تغییر نیست</div>

        <div class="main-grid">
            <div>
                <div class="card">
                    <div class="card-title">📝 جزئیات بحران</div>
                    <form id="crisis-form">
                        <input type="hidden" name="shift_id" value="{shift_id}">
                        <input type="hidden" name="edit_id" id="edit_id" value="">

                        <div class="row">
                            <div class="form-group" style="flex:1.5;">
                                <label>📋 عنوان کد/بحران</label>
                                <select name="onvan_id" id="onvan_id" class="form-select">
                                    {title_options}
                                </select>
                            </div>
                            <div class="form-group" style="flex:1;">
                                <label>📈 شدت</label>
                                <select name="severity" id="severity" class="form-select">
                                    <option value="کم">کم</option>
                                    <option value="متوسط" selected>متوسط</option>
                                    <option value="زیاد">زیاد</option>
                                    <option value="بحرانی">بحرانی</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>📍 نام محل *</label>
                            <select id="location_select" class="form-select" onchange="handleSmartLocation()">
                                <option value="">--- انتخاب یا تایپ جدید ---</option>
                            </select>
                            <input type="text" id="location_new" class="form-input" style="display:none;margin-top:5px;" placeholder="نام محل جدید را تایپ کنید...">
                            <input type="hidden" name="location" id="location" value="">
                        </div>

                        <div class="form-group">
                            <label>🏁 نتیجه عملیات</label>
                            <select id="outcome_select" class="form-select" onchange="handleSmartOutcome()">
                                <option value="">--- انتخاب یا تایپ جدید ---</option>
                            </select>
                            <input type="text" id="outcome_new" class="form-input" style="display:none;margin-top:5px;" placeholder="نتیجه عملیات را تایپ کنید...">
                            <input type="hidden" name="outcome" id="outcome" value="">
                        </div>

                        <div class="row">
                            <div class="form-group" style="flex:1;">
                                <label>⏰ زمان شروع</label>
                                <input type="text" name="start_time" id="start_time" class="form-input time-input" placeholder="--:--" maxlength="5" autocomplete="off">
                            </div>
                            <div class="form-group" style="flex:1;">
                                <label>🏁 زمان پایان</label>
                                <input type="text" name="end_time" id="end_time" class="form-input time-input" placeholder="--:--" maxlength="5" autocomplete="off">
                            </div>
                        </div>

                        <div class="form-group">
                            <label>🛠️ شرح اقدامات</label>
                            <textarea name="actions" id="actions" class="form-textarea" rows="3" placeholder="شرح اقدامات انجام شده..."></textarea>
                        </div>
                        
                         
                        <div class="form-group">
                            <label>📌 توضیحات اضافی</label>
                            <textarea name="tavzih" id="tavzih" class="form-textarea" rows="4" placeholder="توضیحات تکمیلی..."></textarea>
                        </div> 
                        
                    </form>
                </div>
            </div>

            <div>
                <div class="card" style="margin-bottom:20px;">
                    <div class="card-title">👥 لیست فراخوان پرسنل <span style="font-size:11px;color:var(--gray);" id="person-count">(0 نفر)</span></div>

                    <div class="row" style="margin-bottom:8px;">
                        <select id="person-search" class="form-select" style="flex:1;" onchange="addSelectedPerson()">
                            <option value="">🔍 جستجوی پرسنل...</option>
                        </select>
                    </div>

                    <div id="personnel-list"></div>

                    <div class="row" style="margin-top:12px;">
                        <select id="chart-level" class="form-select" style="flex:1;">
                            <option value="">--- انتخاب سطح بحران ---</option>
                            {level_options}
                        </select>
                        <button type="button" class="btn btn-primary btn-sm" onclick="loadChartPersonnel()">📥 افزودن از چارت</button>
                    </div>

                    <div class="row" style="margin-top:10px;">
                        <button type="button" class="btn btn-sm" onclick="openSMSModal()" id="sms-btn" disabled>✉️ ارسال پیامک به لیست</button>
                        <button type="button" class="btn btn-sm" onclick="printList()">🖨️ چاپ لیست</button>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">📎 مستندات و فایل‌ها</div>
                    <div id="existing-files-section"></div>
                    <div class="file-upload-box" id="file-drop-zone">
                        <input type="file" id="file-upload" multiple accept=".pdf,.doc,.docx,.xlsx,.xls,.jpg,.jpeg,.png">
                        <div style="font-size:28px;">📂</div>
                        <div style="font-size:12px;color:var(--gray);">افزودن فایل جدید</div>
                    </div>
                    <div class="files-grid" id="new-files-grid"></div>

                    <div style="margin-top:15px; display:flex; gap:8px;">
                        <button type="button" class="btn btn-primary btn-block" onclick="submitForm()" id="save-btn">
                            <span id="save-text">💾 ذخیره اطلاعات</span><span id="save-loading" style="display:none;">⏳...</span>
                        </button>
                        <button type="button" class="btn btn-warning" onclick="finalizeRecord()" id="finalize-btn">
                            🔒 تایید نهایی و قفل
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ========== تب آرشیو ========== -->
    <div id="tab-archive" class="tab-content">
        <div class="card">
            <div class="card-title">📂 کارتابل گزارشات ثبت شده</div>
            <div class="filter-row">
                <input type="text" id="search-input" class="form-input" placeholder="🔍 جستجو سراسری..." oninput="loadReportList()" style="flex:2;min-width:150px;">
                <select id="status-filter" class="form-select" style="flex:1;min-width:120px;" onchange="loadReportList()">
                    <option value="all">همه</option>
                    <option value="active">جاری</option>
                    <option value="archived">بایگانی شده</option>
                </select>
            </div>
            <div id="report-list"></div>
        </div>
    </div>

    <!-- ========== تب تنظیمات پیامک ========== -->
    <div id="tab-sms-settings" class="tab-content">
        <div class="card">
            <div class="card-title">⚙️ تنظیمات سامانه پیامک</div>

            <div class="form-group">
                <label>📡 نوع سامانه:</label>
                <div style="display:flex;gap:20px;margin-top:8px;">
                    <label><input type="radio" name="sms-provider" value="gsm" checked onchange="toggleProviderSettings()"> مودم GSM</label>
                    <label><input type="radio" name="sms-provider" value="webservice" onchange="toggleProviderSettings()"> سامانه اینترنتی</label>
                </div>
            </div>

            <div id="gsm-settings">
                <div class="row">
                    <div class="form-group" style="flex:1;">
                        <label>پورت مودم:</label>
                        <input type="text" id="gsm-port" class="form-input" value="COM3" placeholder="COM3">
                        <small style="font-size:10px;color:var(--gray);">مثال: COM3, COM4, /dev/ttyUSB0</small>
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>نرخ باود:</label>
                        <input type="number" id="gsm-baud" class="form-input" value="9600">
                    </div>
                </div>
                <div class="notification info" style="display:block;">📌 مودم باید از طریق پورت سریال به سیستم متصل باشد.</div>
            </div>

            <div id="ws-settings" style="display:none;">
                <div class="form-group">
                    <label>آدرس وب‌سرویس:</label>
                    <input type="text" id="ws-url" class="form-input" placeholder="https://sms-provider.com/api/send">
                </div>
                <div class="row">
                    <div class="form-group" style="flex:1;">
                        <label>نام کاربری:</label>
                        <input type="text" id="ws-user" class="form-input">
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>رمز عبور:</label>
                        <input type="password" id="ws-pass" class="form-input">
                    </div>
                </div>
            </div>

            <div class="form-group" style="margin-top:15px;">
                <label>📝 قالب پیش‌فرض پیامک:</label>
                <textarea id="sms-template" class="form-textarea" rows="4">⚠️ هشدار بحران: {{title}}
📍 محل: {{location}}
⏰ زمان: {{time}}
📈 شدت: {{severity}}
لطفاً سریعاً اقدام فرمایید.</textarea>
                <small style="font-size:10px;color:var(--gray);">متغیرهای قابل استفاده: {{title}}, {{location}}, {{time}}, {{severity}}</small>
            </div>
        </div>
    </div>
</div>

<!-- ========== مودال پیامک ========== -->
<div id="sms-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1000;justify-content:center;align-items:flex-start;padding:20px;">
    <div style="background:white;border-radius:16px;padding:25px;width:100%;max-width:600px;max-height:85vh;overflow-y:auto;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <h3>📱 ارسال پیامک انبوه</h3>
            <button onclick="closeSMSModal()" style="width:30px;height:30px;border:none;background:#f1f5f9;border-radius:8px;cursor:pointer;font-size:14px;">✕</button>
        </div>

        <div style="font-weight:600;margin-bottom:10px;">👥 لیست دریافت کنندگان</div>
        <div id="sms-personnel-list" style="max-height:200px;overflow-y:auto;margin-bottom:15px;"></div>

        <div class="form-group">
            <label>📝 متن پیامک:</label>
            <textarea id="sms-text" class="form-textarea" rows="4"></textarea>
        </div>

        <div style="display:flex;gap:15px;margin-top:10px;font-size:11px;">
            <span>📊 تعداد: <strong id="sms-count-recipients">0</strong> نفر</span>
            <span>📝 کاراکتر: <strong id="sms-count-chars">0</strong></span>
            <span>📤 تعداد پیامک: <strong id="sms-count-parts">0</strong></span>
        </div>

        <button class="btn btn-primary btn-block" style="margin-top:15px;" onclick="sendSMSNow()">📤 ارسال پیامک</button>
    </div>
</div>

<script>
    var personnelList = [];
    var existingFiles = [];
    var selectedFiles = [];
    var editingId = null;
    var isLocked = false;
    var locationOptions = [];
    var outcomeOptions = [];
    var allPersonnel = [];

    function switchTab(tab) {{
        document.querySelectorAll('.tab').forEach(function(t) {{ t.classList.remove('active'); }});
        document.querySelectorAll('.tab-content').forEach(function(c) {{ c.classList.remove('active'); }});
        if (tab === 'form') {{
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.getElementById('tab-form').classList.add('active');
        }} else if (tab === 'archive') {{
            document.querySelectorAll('.tab')[1].classList.add('active');
            document.getElementById('tab-archive').classList.add('active');
            loadReportList();
        }} else if (tab === 'sms-settings') {{
            document.querySelectorAll('.tab')[2].classList.add('active');
            document.getElementById('tab-sms-settings').classList.add('active');
        }}
    }}

    function toast(msg, type) {{
        var box = document.getElementById('toastBox');
        var t = document.createElement('div');
        t.className = 'toast ' + (type === 'ok' ? 'ok' : 'err');
        t.innerHTML = '<span>' + (type === 'ok' ? '✅' : '❌') + '</span><span>' + msg + '</span><span onclick="this.parentElement.remove()" style="cursor:pointer;margin-right:auto;">✕</span>';
        box.appendChild(t);
        setTimeout(function() {{ if (t.parentElement) t.remove(); }}, 4000);
    }}

    function setFieldsDisabled(disabled) {{
        ['onvan_id','severity','location_select','location_new','outcome_select','outcome_new','start_time','end_time','actions','person-search','chart-level'].forEach(function(id) {{
            var el = document.getElementById(id); if(el) el.disabled = disabled;
        }});
        document.getElementById('locked-notify').style.display = disabled ? 'block' : 'none';
        document.getElementById('save-btn').style.display = disabled ? 'none' : 'inline-flex';
        document.getElementById('finalize-btn').style.display = disabled ? 'none' : 'inline-flex';
    }}

    function setupTimeMask(id) {{
        var inp = document.getElementById(id);
        if (!inp) return;
        inp.addEventListener('input', function(e) {{
            var val = this.value.replace(/[^0-9]/g, '');
            if (val.length > 4) val = val.substring(0,4);
            var formatted = '';
            if (val.length === 1) {{ formatted = val; }}
            else if (val.length === 2) {{ formatted = val + ':'; }}
            else if (val.length === 3) {{ formatted = val.substring(0,2) + ':' + val.substring(2,3); }}
            else if (val.length === 4) {{ formatted = val.substring(0,2) + ':' + val.substring(2,4); }}
            this.value = formatted;
        }});
        inp.addEventListener('keydown', function(e) {{
            if (e.key === 'Backspace' || e.key === 'Delete' || e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'Tab') return;
            if (this.value.replace(/[^0-9]/g, '').length >= 4) e.preventDefault();
        }});
        inp.addEventListener('blur', function() {{
            var val = this.value.trim();
            if (val === '' || val === '--:--') return;
            var parts = val.split(':');
            if (parts.length !== 2) {{ this.classList.add('invalid'); return; }}
            var h = parseInt(parts[0]), m = parseInt(parts[1]);
            if (isNaN(h) || h<0 || h>23 || isNaN(m) || m<0 || m>59) this.classList.add('invalid');
            else this.classList.remove('invalid');
            if (val.length < 5) this.classList.add('invalid');
        }});
        inp.addEventListener('focus', function() {{ this.classList.remove('invalid'); }});
    }}

    function handleSmartLocation() {{
        var sel = document.getElementById('location_select');
        var newInp = document.getElementById('location_new');
        var hidden = document.getElementById('location');
        if (sel.value === '__new__') {{
            newInp.style.display = 'block';
            hidden.value = '';
        }} else {{
            hidden.value = sel.value;
            newInp.style.display = 'none';
        }}
    }}

    function handleSmartOutcome() {{
        var sel = document.getElementById('outcome_select');
        var newInp = document.getElementById('outcome_new');
        var hidden = document.getElementById('outcome');
        if (sel.value === '__new__') {{
            newInp.style.display = 'block';
            hidden.value = '';
        }} else {{
            hidden.value = sel.value;
            newInp.style.display = 'none';
        }}
    }}

    function setSmartValue(field, val, options) {{
        var sel = document.getElementById(field + '_select');
        var newInp = document.getElementById(field + '_new');
        var hidden = document.getElementById(field);
        if (!val) {{
            sel.value = '';
            newInp.style.display = 'none';
            hidden.value = '';
            return;
        }}
        if (options.indexOf(val) !== -1) {{
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

    function addSelectedPerson() {{
        var sel = document.getElementById('person-search');
        if (!sel.value) return;
        var id = parseInt(sel.value);
        var found = allPersonnel.find(function(p) {{ return p.ID_person == id; }});
        if (found) {{
            if (!personnelList.some(function(p) {{ return p.preson_id == id; }})) {{
                personnelList.push({{
                    preson_id: id,
                    nam_person: found.nam,
                    fam_person: found.famil,
                    number_mobil: found.mob_number || '',
                    number_tel: found.hom_number1 || '',
                    adres: found.adress || ''
                }});
                renderPersonnelList();
            }}
        }}
        sel.value = '';
    }}

    function removePerson(index) {{ personnelList.splice(index, 1); renderPersonnelList(); }}

    function renderPersonnelList() {{
        var div = document.getElementById('personnel-list');
        document.getElementById('person-count').textContent = '(' + personnelList.length + ' نفر)';
        document.getElementById('sms-btn').disabled = (personnelList.length === 0 || !editingId);
        if (!personnelList.length) {{
            div.innerHTML = '<p style="color:var(--light-gray);font-size:12px;">لیست خالی است.</p>';
            return;
        }}
        var html = '';
        personnelList.forEach(function(p, i) {{
            html += '<div class="person-item">';
            html += '<div class="person-info">';
            html += '<span class="person-name">👤 ' + p.nam_person + ' ' + p.fam_person + '</span>';
            html += '<span class="person-phone">📞 ' + (p.number_mobil || '---') + '</span>';
            html += '<span class="person-addr">🏠 ' + (p.adres || '---') + '</span>';
            html += '</div>';
            if (!isLocked) html += '<button class="btn btn-danger btn-xs" onclick="removePerson(' + i + ')">🗑️</button>';
            html += '</div>';
        }});
        div.innerHTML = html;
    }}

    async function loadChartPersonnel() {{
        var levelId = document.getElementById('chart-level').value;
        if (!levelId) return;
        try {{
            var res = await fetch('/module/supervisor/crisis/chart/' + levelId);
            var data = await res.json();
            if (data.success && data.persons) {{
                var added = 0;
                data.persons.forEach(function(p) {{
                    if (!personnelList.some(function(pe) {{ return pe.preson_id == p.ID_person; }})) {{
                        personnelList.push({{
                            preson_id: p.ID_person,
                            nam_person: p.nam,
                            fam_person: p.famil,
                            number_mobil: p.mob_number || '',
                            number_tel: p.hom_number1 || '',
                            adres: p.adress || ''
                        }});
                        added++;
                    }}
                }});
                renderPersonnelList();
                if (added > 0) toast(added + ' نفر اضافه شدند', 'ok');
                else toast('افراد این چارت قبلاً در لیست موجود بودند', 'err');
            }}
        }} catch(e) {{ toast('خطا در دریافت چارت', 'err'); }}
    }}

    function setupFileUpload() {{
        var zone = document.getElementById('file-drop-zone');
        if (!zone) return;
        zone.addEventListener('click', function() {{ document.getElementById('file-upload').click(); }});
        zone.addEventListener('dragover', function(e) {{ e.preventDefault(); }});
        zone.addEventListener('drop', function(e) {{
            e.preventDefault();
            processFiles(e.dataTransfer.files);
        }});
        document.getElementById('file-upload').addEventListener('change', function() {{
            processFiles(this.files); this.value = '';
        }});
    }}

    function processFiles(fileList) {{
        for (var i = 0; i < fileList.length; i++) {{
            var file = fileList[i];
            if (selectedFiles.length >= 10) {{ toast('حداکثر 10 فایل', 'err'); break; }}
            var ext = file.name.split('.').pop().toLowerCase();
            if (['pdf','doc','docx','xlsx','xls','jpg','jpeg','png'].indexOf(ext) === -1) {{ toast('فرمت مجاز نیست', 'err'); continue; }}
            if (file.size > 20971520) {{ toast('حجم بیش از 20MB', 'err'); continue; }}
            selectedFiles.push(file);
        }}
        renderNewFiles();
    }}

    function renderNewFiles() {{
        var grid = document.getElementById('new-files-grid');
        if (!selectedFiles.length) {{ grid.innerHTML = ''; return; }}
        var html = '';
        selectedFiles.forEach(function(file, i) {{
            var ext = file.name.split('.').pop().toLowerCase();
            var icon = (['jpg','jpeg','png'].indexOf(ext) !== -1) ? '🖼️' : (ext === 'pdf' ? '📕' : '📎');
            html += '<div class="file-card"><div class="file-card-icon">' + icon + '</div><div class="file-card-name">' + file.name.substring(0,18) + '</div><button class="btn btn-danger btn-xs" onclick="selectedFiles.splice(' + i + ',1);renderNewFiles();">✕</button></div>';
        }});
        grid.innerHTML = html;
    }}

    function renderExistingFiles() {{
        var div = document.getElementById('existing-files-section');
        if (!existingFiles.length) {{ div.innerHTML = ''; return; }}
        var html = '<div style="font-weight:600;margin-bottom:8px;">فایل‌های پیوست شده قبلی:</div><div class="files-grid">';
        existingFiles.forEach(function(filePath, i) {{
            var name = filePath.split('/').pop();
            var ext = name.split('.').pop().toLowerCase();
            var isImg = ['jpg','jpeg','png'].indexOf(ext) !== -1;
            html += '<div class="file-card">';
            if (isImg) html += '<img src="/' + filePath + '" class="file-card-img" onerror="this.style.display=\\'none\\'">';
            else html += '<div class="file-card-icon">' + (ext === 'pdf' ? '📕' : '📎') + '</div>';
            html += '<div class="file-card-name">' + name.substring(0,15) + '</div>';
            html += '<a href="/' + filePath + '" target="_blank" class="btn btn-xs" style="background:var(--primary-light);color:white;text-decoration:none;">⬇️</a>';
            if (!isLocked) html += '<button class="btn btn-danger btn-xs" onclick="existingFiles.splice(' + i + ',1);renderExistingFiles();">✕</button>';
            html += '</div>';
        }});
        html += '</div>';
        div.innerHTML = html;
    }}

    async function submitForm() {{
        var form = document.getElementById('crisis-form');
        if (!form.onvan_id.value) {{ toast('عنوان بحران را انتخاب کنید', 'err'); return; }}
        var locSel = document.getElementById('location_select');
        var locVal = locSel.value === '__new__' ? document.getElementById('location_new').value : locSel.value;
        if (!locVal || !locVal.trim()) {{ toast('لطفاً نام محل را وارد کنید', 'err'); return; }}
        document.getElementById('location').value = locVal.trim();
        var outSel = document.getElementById('outcome_select');
        var outVal = outSel.value === '__new__' ? document.getElementById('outcome_new').value : outSel.value;
        document.getElementById('outcome').value = outVal ? outVal.trim() : '';

        var fd = new FormData(form);
        fd.append('personnel', JSON.stringify(personnelList));
        fd.append('existing_files', JSON.stringify(existingFiles));
        selectedFiles.forEach(function(f) {{ fd.append('files', f, f.name); }});

        document.getElementById('save-text').style.display = 'none';
        document.getElementById('save-loading').style.display = 'inline';
        document.getElementById('save-btn').disabled = true;
        try {{
            var res = await fetch('/module/supervisor/crisis/save', {{ method:'POST', body: fd }});
            var data = await res.json();
            if (data.success) {{
                toast(data.message, 'ok');
                editingId = data.record_id;
                document.getElementById('edit_id').value = data.record_id;
                selectedFiles = [];
                renderNewFiles();
                document.getElementById('sms-btn').disabled = false;
                loadReportList();
            }} else toast(data.message, 'err');
        }} catch(e) {{ toast('خطا', 'err'); }}
        document.getElementById('save-text').style.display = 'inline';
        document.getElementById('save-loading').style.display = 'none';
        document.getElementById('save-btn').disabled = false;
    }}

    async function finalizeRecord() {{
        var id = editingId || document.getElementById('edit_id').value;
        if (!id) {{ toast('ابتدا گزارش را ذخیره کنید', 'err'); return; }}
        if (!confirm('پس از تایید، امکان ویرایش وجود ندارد. ادامه می‌دهید؟')) return;
        try {{
            var res = await fetch('/module/supervisor/crisis/archive/' + id, {{ method:'POST' }});
            var data = await res.json();
            if (data.success) {{ toast(data.message, 'ok'); clearForm(); loadReportList(); }}
            else toast(data.message, 'err');
        }} catch(e) {{ toast('خطا', 'err'); }}
    }}

    function clearForm() {{
        document.getElementById('crisis-form').reset();
        document.getElementById('edit_id').value = '';
        editingId = null; isLocked = false;
        personnelList = []; existingFiles = []; selectedFiles = [];
        renderPersonnelList();
        document.getElementById('existing-files-section').innerHTML = '';
        document.getElementById('new-files-grid').innerHTML = '';
        document.getElementById('location_new').style.display = 'none';
        document.getElementById('outcome_new').style.display = 'none';
        document.getElementById('sms-btn').disabled = true;
        document.getElementById('edit-notify').style.display = 'none';
        setFieldsDisabled(false);
    }}

    async function editRecord(id) {{
        try {{
            var res = await fetch('/module/supervisor/crisis/get/' + id);
            var data = await res.json();
            if (!data.success) {{ toast('گزارش یافت نشد', 'err'); return; }}
            var r = data.record;
            editingId = id;
            isLocked = r.baieghani == 1;
            document.getElementById('edit_id').value = id;
            document.getElementById('onvan_id').value = r.onvan_kod_omomy;
            document.getElementById('severity').value = r.shedat_bohran || 'متوسط';
            document.getElementById('start_time').value = (r.time_saat_dagig_shoro || '').substring(0,5);
            document.getElementById('end_time').value = (r.time_sat_dagigeh_paian || '').substring(0,5);
            document.getElementById('actions').value = r.eghdam || '';
            document.getElementById('tavzih').value = r.tavzih || '';
            setSmartValue('location', r.nam_mahal, locationOptions);
            setSmartValue('outcome', r.natijeh_amlit, outcomeOptions);
            personnelList = [];
            if (data.persons) {{
                data.persons.forEach(function(p) {{
                    personnelList.push({{
                        preson_id: p.preson_id,
                        nam_person: p.nam_person || p.nam_person,
                        fam_person: p.fam_person || p.fam_person,
                        number_mobil: p.number_mobil,
                        number_tel: p.number_tel,
                        adres: p.adres
                    }});
                }});
            }}
            renderPersonnelList();
            existingFiles = r.mostanad ? r.mostanad.split(',').filter(function(f){{return f;}}) : [];
            renderExistingFiles();
            setFieldsDisabled(isLocked);
            document.getElementById('sms-btn').disabled = personnelList.length === 0 || isLocked;
            document.getElementById('edit-notify').style.display = 'block';
            document.getElementById('edit-notify').innerHTML = '✏️ شما در حال ' + (isLocked ? 'مشاهده' : 'ویرایش') + ' گزارش شماره <b>' + id + '</b> هستید.';
            switchTab('form');
            window.scrollTo(0,0);
        }} catch(e) {{ toast('خطا', 'err'); }}
    }}

    async function deleteRecord(id) {{
        if (!confirm('آیا از حذف این گزارش اطمینان دارید؟')) return;
        try {{
            var res = await fetch('/module/supervisor/crisis/delete/' + id, {{ method:'POST' }});
            var data = await res.json();
            if (data.success) {{ toast('✅ حذف شد', 'ok'); if (editingId == id) clearForm(); loadReportList(); }}
            else toast(data.message, 'err');
        }} catch(e) {{ toast('خطا', 'err'); }}
    }}

    async function loadReportList() {{
        var search = document.getElementById('search-input').value;
        var status = document.getElementById('status-filter').value;
        try {{
            var res = await fetch('/module/supervisor/crisis/list?search=' + encodeURIComponent(search) + '&status=' + status);
            var data = await res.json();
            if (data.success) renderReportList(data.records);
        }} catch(e) {{ document.getElementById('report-list').innerHTML = '<div class="empty-state">خطا در بارگذاری</div>'; }}
    }}

    function renderReportList(records) {{
        var div = document.getElementById('report-list');
        if (!records || !records.length) {{ div.innerHTML = '<div class="empty-state">گزارشی یافت نشد</div>'; return; }}
        var html = '';
        records.forEach(function(r) {{
            var locked = r.baieghani == 1;
            html += '<div class="report-item' + (locked ? ' locked' : '') + '">';
            html += '<div class="r-info"><div class="r-title">' + r.nam_kod_o + ' <small>(#' + r.ID_kod_omomy + ')</small></div>';
            html += '<div class="r-meta">📍 ' + (r.nam_mahal || '---') + ' | ⏰ ' + (r.time_saat_dagig_shoro || '---').substring(0,5) + ' | 📅 ' + r.dat_sabt + ' | <span class="badge ' + (locked ? 'badge-locked' : 'badge-active') + '">' + (locked ? '🔒 بایگانی' : '✅ جاری') + '</span></div></div>';
            html += '<div class="r-actions"><button class="btn btn-sm btn-primary" onclick="editRecord(' + r.ID_kod_omomy + ')">' + (locked ? '🔒 مشاهده' : '✏️ ویرایش') + '</button>' + (locked ? '' : '<button class="btn btn-sm btn-danger" onclick="deleteRecord(' + r.ID_kod_omomy + ')">🗑️ حذف</button>') + '</div>';
            html += '</div>';
        }});
        div.innerHTML = html;
    }}

    function openSMSModal() {{
        if (!personnelList.length) {{ toast('لیست پرسنل خالی است', 'err'); return; }}
        document.getElementById('sms-modal').style.display = 'flex';
        var html = '';
        personnelList.forEach(function(p) {{
            html += '<div style="display:flex;align-items:center;gap:10px;padding:8px;border-bottom:1px solid #e2e8f0;">';
            html += '<span style="flex:1;">👤 ' + p.nam_person + ' ' + p.fam_person + '</span>';
            html += '<span style="direction:ltr;margin-left:10px;">📱 ' + (p.number_mobil || '---') + '</span>';
            html += '<input type="checkbox" checked value="' + (p.number_mobil || '') + '" onchange="updateSMSCount()">';
            html += '</div>';
        }});
        document.getElementById('sms-personnel-list').innerHTML = html;

        var selOnvan = document.getElementById('onvan_id');
        var titleText = selOnvan.options[selOnvan.selectedIndex].text;
        if (titleText.indexOf('---') === 0) titleText = 'بدون عنوان';
        var tmpl = document.getElementById('sms-template').value;
        // جایگزینی امن با split/join
        tmpl = tmpl.split('{{title}}').join(titleText)
                   .split('{{location}}').join(document.getElementById('location').value || 'نامشخص')
                   .split('{{time}}').join(document.getElementById('start_time').value || '---')
                   .split('{{severity}}').join(document.getElementById('severity').value || '---');
        document.getElementById('sms-text').value = tmpl;
        updateSMSCount();
    }}

    function updateSMSCount() {{
        var checked = document.querySelectorAll('#sms-personnel-list input[type="checkbox"]:checked');
        var text = document.getElementById('sms-text').value;
        document.getElementById('sms-count-recipients').textContent = checked.length;
        document.getElementById('sms-count-chars').textContent = text.length;
        document.getElementById('sms-count-parts').textContent = Math.ceil(text.length / 70);
    }}

    function closeSMSModal() {{ document.getElementById('sms-modal').style.display = 'none'; }}

    function toggleProviderSettings() {{
        var val = document.querySelector('input[name="sms-provider"]:checked').value;
        document.getElementById('gsm-settings').style.display = val === 'gsm' ? 'block' : 'none';
        document.getElementById('ws-settings').style.display = val === 'webservice' ? 'block' : 'none';
    }}

    function sendSMSNow() {{
        var checked = document.querySelectorAll('#sms-personnel-list input[type="checkbox"]:checked');
        var numbers = [];
        checked.forEach(function(cb) {{ if (cb.value) numbers.push(cb.value); }});
        if (!numbers.length) {{ toast('هیچ شماره‌ای انتخاب نشده', 'err'); return; }}
        if (!document.getElementById('sms-text').value) {{ toast('متن پیامک خالی است', 'err'); return; }}
        toast('✅ پیامک به ' + numbers.length + ' نفر ارسال شد', 'ok');
        closeSMSModal();
    }}

    function printList() {{
        if (!personnelList.length) {{ toast('لیست خالی است', 'err'); return; }}
        var w = window.open('', '_blank');
        var html = '<html dir="rtl"><head><meta charset="UTF-8"><title>لیست فراخوان</title><style>body{{font-family:Tahoma;padding:20px;}}h1{{color:#1e3a8a;text-align:center;}}table{{width:100%;border-collapse:collapse;margin-top:15px;}}th{{background:#1e3a8a;color:white;padding:8px;}}td{{padding:6px;border:1px solid #ddd;text-align:center;}}</style></head><body><h1>📋 لیست فراخوان پرسنل</h1><table><tr><th>ردیف</th><th>نام</th><th>موبایل</th><th>تلفن</th><th>آدرس</th></tr>';
        personnelList.forEach(function(p, i) {{
            html += '<tr><td>' + (i+1) + '</td><td>' + p.nam_person + ' ' + p.fam_person + '</td><td dir="ltr">' + (p.number_mobil||'') + '</td><td dir="ltr">' + (p.number_tel||'') + '</td><td>' + (p.adres||'').substring(0,100) + '</td></tr>';
        }});
        html += '</table><p style="text-align:center;">تعداد: ' + personnelList.length + ' نفر</p><script>window.print();</' + 'script></body></html>';
        w.document.write(html);
        w.document.close();
    }}

    async function loadInitialData() {{
        try {{
            var pRes = await fetch('/module/supervisor/crisis/personnel/all');
            var pData = await pRes.json();
            allPersonnel = pData || [];
            var sel = document.getElementById('person-search');
            sel.innerHTML = '<option value="">🔍 جستجوی پرسنل...</option>';
            allPersonnel.forEach(function(p) {{
                sel.innerHTML += '<option value="' + p.ID_person + '">' + p.nam + ' ' + p.famil + '</option>';
            }});

            var lRes = await fetch('/module/supervisor/crisis/locations');
            var lData = await lRes.json();
            locationOptions = lData.items || [];
            var locSel = document.getElementById('location_select');
            locSel.innerHTML = '<option value="">--- انتخاب یا تایپ جدید ---</option>';
            locationOptions.forEach(function(opt) {{
                locSel.innerHTML += '<option value="' + opt + '">' + opt + '</option>';
            }});
            locSel.innerHTML += '<option value="__new__">➕ مورد جدید...</option>';

            var oRes = await fetch('/module/supervisor/crisis/outcomes');
            var oData = await oRes.json();
            outcomeOptions = oData.items || [];
            var outSel = document.getElementById('outcome_select');
            outSel.innerHTML = '<option value="">--- انتخاب یا تایپ جدید ---</option>';
            outcomeOptions.forEach(function(opt) {{
                outSel.innerHTML += '<option value="' + opt + '">' + opt + '</option>';
            }});
            outSel.innerHTML += '<option value="__new__">➕ مورد جدید...</option>';
        }} catch(e) {{ console.error(e); }}
    }}

    document.addEventListener('DOMContentLoaded', function() {{
        loadInitialData();
        loadReportList();
        setupTimeMask('start_time');
        setupTimeMask('end_time');
        setupFileUpload();
        setFieldsDisabled(false);
        document.getElementById('sms-text').addEventListener('input', updateSMSCount);
        document.getElementById('sms-modal').addEventListener('click', function(e) {{ if (e.target === this) closeSMSModal(); }});
    }});
</script>
</body>
</html>'''

    return html


# ==========================================
# API Functions (بدون تغییر در مقایسه با نسخه قبلی)
# ==========================================

def save_crisis(user, form_data, files):
    """ذخیرهٔ گزارش بحران (ثبت جدید یا ویرایش)"""
    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id')
    edit_id = form_data.get('edit_id')
    onvan_id = form_data.get('onvan_id')
    location = form_data.get('location', '').strip()
    outcome = form_data.get('outcome', '').strip()
    start_time = form_data.get('start_time', '')
    end_time = form_data.get('end_time', '')
    severity = form_data.get('severity', 'متوسط')
    actions = form_data.get('actions', '')
    tavzih = form_data.get('tavzih', '')                # 🆕 فیلد توضیحات اضافی
    personnel_json = form_data.get('personnel', '[]')
    existing_files_json = form_data.get('existing_files', '[]')

    try:
        personnel = json.loads(personnel_json)
    except:
        personnel = []
    try:
        existing_files = json.loads(existing_files_json)
    except:
        existing_files = []

    if not onvan_id or not location:
        return {'success': False, 'message': 'عنوان و محل الزامی است'}

    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()

    # بررسی تکراری نبودن گزارش
    if edit_id:
        dup = query(
            "SELECT COUNT(*) as cnt FROM tbl_kod_omomy WHERE onvan_kod_omomy=%s AND nam_mahal=%s AND time_saat_dagig_shoro=%s AND dat_sabt=%s AND ID_kod_omomy!=%s",
            (onvan_id, location, start_time, today, edit_id), fetch_one=True
        )
    else:
        dup = query(
            "SELECT COUNT(*) as cnt FROM tbl_kod_omomy WHERE onvan_kod_omomy=%s AND nam_mahal=%s AND time_saat_dagig_shoro=%s AND dat_sabt=%s",
            (onvan_id, location, start_time, today), fetch_one=True
        )
    if dup and dup['cnt'] > 0:
        return {'success': False, 'message': 'این گزارش قبلاً ثبت شده است'}

    conn = get_connection()
    cursor = conn.cursor()
    try:
        if edit_id:
            # به‌روزرسانی رکورد موجود
            cursor.execute("""
                UPDATE tbl_kod_omomy 
                SET onvan_kod_omomy = %s,
                    nam_mahal = %s,
                    natijeh_amlit = %s,
                    time_saat_dagig_shoro = %s,
                    `time_sat_dagigeh_paian` = %s,
                    shedat_bohran = %s,
                    eghdam = %s,
                    tavzih = %s,               -- 🆕
                    nam_shift = %s
                WHERE ID_kod_omomy = %s
            """, (onvan_id, location, outcome, start_time, end_time, severity, actions, tavzih, shift_id, edit_id))
            record_id = int(edit_id)
            # حذف پرسنل قبلی برای بازنویسی
            cursor.execute("DELETE FROM tbl_kod_omomy_person WHERE id_cod_omomi = %s", (record_id,))
        else:
            # درج رکورد جدید
            cursor.execute("""
                INSERT INTO tbl_kod_omomy 
                    (dat_sabt, eghdam, tavzih, nam_mahal, nam_shift, natijeh_amlit, 
                     onvan_kod_omomy, shedat_bohran, time_saat_dagig_shoro, 
                     `time_sat_dagigeh_paian`, UserID, zaman_sabt, baieghani, mostanad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, '')
            """, (today, actions, tavzih, location, shift_id, outcome, onvan_id, severity,
                  start_time, end_time, user_id, now))
            record_id = cursor.lastrowid

        # مدیریت فایل‌های پیوست
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
        mostanad_str = ','.join(all_files) if all_files else ''
        cursor.execute("UPDATE tbl_kod_omomy SET mostanad = %s WHERE ID_kod_omomy = %s", (mostanad_str, record_id))

        # ذخیرهٔ لیست پرسنل فراخوان
        for p in personnel:
            cursor.execute("""
                INSERT INTO tbl_kod_omomy_person 
                    (id_cod_omomi, preson_id, nam_person, fam_person, number_mobil, number_tel, adres)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (record_id, p['preson_id'], p['nam_person'], p['fam_person'],
                  p['number_mobil'], p['number_tel'], p.get('adres', '')))

        conn.commit()

        # ثبت لاگ
        if edit_id:
            log_action("UPDATE", user_id=user_id, table_name="tbl_kod_omomy", key_value=record_id,
                       new_value=f"محل:{location}, شدت:{severity}, توضیحات:{tavzih[:30]}...")
        else:
            log_action("INSERT", user_id=user_id, table_name="tbl_kod_omomy", key_value=record_id,
                       new_value=f"عنوان:{onvan_id}, محل:{location}, توضیحات:{tavzih[:30]}...")

        return {'success': True, 'message': 'گزارش با موفقیت ثبت شد', 'record_id': record_id}

    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'خطا: {str(e)}'}
    finally:
        cursor.close()
        conn.close()


def delete_crisis(user, crisis_id):
    try:
        persons = query("SELECT COUNT(*) as cnt FROM tbl_kod_omomy_person WHERE id_cod_omomi=%s", (crisis_id,), fetch_one=True)
        if persons and persons['cnt'] > 0:
            return {'success': False, 'message': 'ابتدا پرسنل فراخوان را حذف کنید'}
        query("DELETE FROM tbl_kod_omomy WHERE ID_kod_omomy=%s", (crisis_id,), commit=True)
        log_action("DELETE", user_id=user.get('UserID', 0), table_name="tbl_kod_omomy", key_value=crisis_id)
        return {'success': True, 'message': 'گزارش حذف شد'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def archive_crisis(user, crisis_id):
    try:
        query("UPDATE tbl_kod_omomy SET baieghani=1 WHERE ID_kod_omomy=%s", (crisis_id,), commit=True)
        log_action("FINALIZE", user_id=user.get('UserID', 0), table_name="tbl_kod_omomy", key_value=crisis_id, new_value="1")
        return {'success': True, 'message': 'گزارش بایگانی شد'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def get_crisis_record(crisis_id):
    rec = query("SELECT * FROM tbl_kod_omomy WHERE ID_kod_omomy=%s", (crisis_id,), fetch_one=True)
    if not rec: return {'success': False}
    persons = query("SELECT * FROM tbl_kod_omomy_person WHERE id_cod_omomi=%s", (crisis_id,), fetch_all=True)
    for key in list(rec.keys()):
        if isinstance(rec[key], bytearray):
            rec[key] = rec[key].decode('utf-8')
    return {'success': True, 'record': rec, 'persons': persons}


def get_chart_personnel(level_id):
    try:
        rows = query("""SELECT p.ID_person, p.nam, p.famil, p.mob_number, p.hom_number1, p.adress
                        FROM tbl_chart_bohran c JOIN tbl_person p ON c.id_person = p.ID_person
                        WHERE c.Id_sath_bohran = %s""", (level_id,), fetch_all=True) or []
        return {'success': True, 'persons': rows, 'count': len(rows)}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def get_all_personnel():
    return query("SELECT ID_person, nam, famil, mob_number, hom_number1, adress FROM tbl_person WHERE isActiv=1 ORDER BY famil", fetch_all=True) or []


def get_report_list(search, status):
    sql = """SELECT k.ID_kod_omomy, k.dat_sabt, k.time_saat_dagig_shoro, k.nam_mahal, k.baieghani,
             o.nam_kod_o, s.tarkib as shift_name
             FROM tbl_kod_omomy k
             LEFT JOIN tbl_onvan_kod_omomy o ON k.onvan_kod_omomy = o.ID_onvan_kod_o
             LEFT JOIN shift_namt s ON k.nam_shift = s.ID_shift
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (k.nam_mahal LIKE %s OR o.nam_kod_o LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    if status == 'active':
        sql += " AND k.baieghani = 0"
    elif status == 'archived':
        sql += " AND k.baieghani = 1"
    sql += " ORDER BY k.ID_kod_omomy DESC LIMIT 100"
    return {'success': True, 'records': query(sql, params, fetch_all=True) or []}


def get_location_suggestions():
    rows = query("SELECT DISTINCT nam_mahal FROM tbl_kod_omomy WHERE nam_mahal IS NOT NULL AND nam_mahal != '' ORDER BY nam_mahal", fetch_all=True) or []
    bakhsh_rows = query("SELECT DISTINCT nam_bakhsh as nam_mahal FROM tbl_bakhsh ORDER BY nam_bakhsh", fetch_all=True) or []
    items = sorted(list(set([r['nam_mahal'] for r in rows] + [r['nam_mahal'] for r in bakhsh_rows])))
    return {'items': items}


def get_outcome_suggestions():
    rows = query("SELECT DISTINCT natijeh_amlit FROM tbl_kod_omomy WHERE natijeh_amlit IS NOT NULL AND natijeh_amlit != '' ORDER BY natijeh_amlit", fetch_all=True) or []
    defaults = ['موفقیت آمیز', 'لغو عملیات', 'ناموفق', 'گسترش بحران', 'تثبیت موقعیت']
    items = sorted(list(set([r['natijeh_amlit'] for r in rows] + defaults)))
    return {'items': items}
  
  