"""
فرم تنظیم شیفت - سوپروایزر (ویرایش برای ذخیره ID_onvan_shift)
"""

from models.database import query
import jdatetime
from datetime import datetime
import json
import math
from utils.auto_log import log_crud

# نگاشت نام شیفت به عدد یک‌رقمی برای کد شیفت
SHIFT_NUMBER_MAP = {
    'صبح': 1,
    'صبح و عصر': 2,
    'عصر': 3,
    'فول': 4,
    'عصر و شب': 5,
    'شب': 6
}

def get_shift_form(user, message=None, error=None, edit_mode=False, edit_data=None):
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', 'کاربر')

    # ========== دریافت عناوین شیفت ==========
    titles_result = query(
        "SELECT ID_onvan_shift, nam_shift FROM onvan_shift ORDER BY nam_shift",
        fetch_all=True
    )
    if not titles_result:
        titles_result = [
            {'ID_onvan_shift': 1, 'nam_shift': 'صبح'},
            {'ID_onvan_shift': 2, 'nam_shift': 'صبح و عصر'},
            {'ID_onvan_shift': 3, 'nam_shift': 'عصر'},
            {'ID_onvan_shift': 4, 'nam_shift': 'فول'},
            {'ID_onvan_shift': 5, 'nam_shift': 'عصر و شب'},
            {'ID_onvan_shift': 6, 'nam_shift': 'شب'},
        ]

    now = jdatetime.datetime.now()
    today_shamsi = now.strftime("%Y/%m/%d")
    current_weekday = now.weekday()

    days_list = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]

    default_date = today_shamsi
    default_day_idx = current_weekday
    default_shift_id_onvan = ""   # ID_onvan_shift پیش‌فرض
    default_shift_id = ""
    default_occasion = ""
    form_title = "➕ ثبت شیفت جدید"
    submit_label = "💾 ذخیره نهایی شیفت"
    form_action = "/module/supervisor/shift/save"

    if edit_mode and edit_data:
        form_title = "✏️ ویرایش شیفت"
        submit_label = "💾 بروزرسانی تغییرات"
        form_action = f"/module/supervisor/shift/edit/{edit_data.get('ID_shift', '')}"

        d = str(edit_data.get('dat_sabt', ''))
        if len(d) == 8:
            default_date = f"{d[:4]}/{d[4:6]}/{d[6:]}"
        roz = edit_data.get('roz_hafteh', '')
        if roz in days_list:
            default_day_idx = days_list.index(roz)
        # حالا nam_shift در جدول یک عدد است (ID_onvan_shift)
        default_shift_id_onvan = str(edit_data.get('nam_shift', ''))
        default_shift_id = str(edit_data.get('ID_shift', ''))
        default_occasion = edit_data.get('monasebat', '')

    # ========== ساخت گزینه‌های select ==========
    day_options_html = ''
    for i, day in enumerate(days_list):
        selected = 'selected' if i == default_day_idx else ''
        day_options_html += f'<option value="{day}" {selected}>{day}</option>'

    shift_options_html = '<option value="">-- انتخاب کنید --</option>'
    for t in titles_result:
        sid = t['ID_onvan_shift']
        name = t['nam_shift']
        num = SHIFT_NUMBER_MAP.get(name, sid)   # اگر نام در مپ نبود از id خودش استفاده می‌کنیم
        selected = 'selected' if str(sid) == default_shift_id_onvan else ''
        shift_options_html += f'<option value="{sid}" data-shift-number="{num}" {selected}>{name}</option>'

    # ========== نگاشت برای جاوااسکریپت ==========
    shift_number_map_json = json.dumps({str(t['ID_onvan_shift']): SHIFT_NUMBER_MAP.get(t['nam_shift'], t['ID_onvan_shift']) for t in titles_result}, ensure_ascii=False)

    # ========== لیست شیفت‌ها (placeholder) ==========
    list_html = get_shift_list_html(user)

    # ========== HTML ==========
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --primary: #1e3a8a;
                --primary-light: #3b82f6;
                --success: #10b981;
                --danger: #ef4444;
                --warning: #f59e0b;
                --dark: #1e293b;
                --gray: #64748b;
                --light-gray: #94a3b8;
                --border: #e2e8f0;
                --bg-light: #f8fafc;
                --radius: 12px;
                --transition: 0.2s ease;
            }}

            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; background: #f1f5f9; color: var(--dark); }}

            .fade-in {{ animation: fadeIn 0.4s ease; }}
            @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

            .content-card {{ max-width: 1400px; margin: 0 auto; }}

            .page-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                padding-bottom: 20px;
                border-bottom: 2px solid var(--border);
            }}
            .page-header-left h2 {{ margin: 0 0 5px 0; color: var(--dark); font-size: 22px; font-weight: bold; }}
            .page-header-left p {{ color: var(--light-gray); font-size: 13px; margin: 0; }}
            .back-btn {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                color: var(--primary-light);
                font-weight: bold;
                font-size: 14px;
                text-decoration: none;
                padding: 10px 18px;
                border: 2px solid var(--primary-light);
                border-radius: 10px;
                transition: var(--transition);
            }}
            .back-btn:hover {{ background: var(--primary-light); color: white; }}

            .tabs {{ display: flex; gap: 5px; margin-bottom: 25px; border-bottom: 2px solid var(--border); }}
            .tab {{
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                background: none;
                color: var(--light-gray);
                cursor: pointer;
                border-bottom: 2px solid transparent;
                margin-bottom: -2px;
                transition: var(--transition);
                font-family: Tahoma, Arial, sans-serif;
            }}
            .tab:hover {{ color: var(--dark); }}
            .tab.active {{ color: var(--primary-light); border-bottom-color: var(--primary-light); }}
            .tab-content {{ display: none; }}
            .tab-content.active {{ display: block; }}

            .form-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 20px; }}
            .form-column {{ background: var(--bg-light); padding: 25px; border-radius: 14px; border: 1px solid var(--border); }}
            .form-column-title {{ font-size: 16px; font-weight: bold; color: var(--dark); margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }}

            .form-group {{ margin-bottom: 18px; }}
            .form-group:last-child {{ margin-bottom: 0; }}
            .form-group label {{ display: block; font-size: 13px; font-weight: 600; color: var(--gray); margin-bottom: 6px; }}
            .form-group small {{ display: block; font-size: 11px; color: var(--light-gray); margin-top: 4px; }}

            .form-input {{
                width: 100%;
                padding: 11px 14px;
                border: 2px solid var(--border);
                border-radius: 10px;
                font-size: 14px;
                background: #fff;
                transition: var(--transition);
                font-family: Tahoma, Arial, sans-serif;
                color: var(--dark);
            }}
            .form-input:focus {{ border-color: var(--primary-light); outline: none; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }}
            .form-input:disabled {{ background: #f1f5f9; color: var(--gray); cursor: not-allowed; }}

            .input-with-button {{ display: flex; gap: 8px; }}
            .input-with-button .form-input {{ flex: 1; }}

            .btn-generate {{
                display: inline-flex;
                align-items: center;
                gap: 5px;
                padding: 11px 16px;
                background: white;
                color: var(--primary-light);
                border: 2px solid var(--primary-light);
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                white-space: nowrap;
                transition: var(--transition);
                font-family: Tahoma, Arial, sans-serif;
            }}
            .btn-generate:hover {{ background: var(--primary-light); color: white; }}

            .btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 12px 24px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: var(--transition);
                font-family: Tahoma, Arial, sans-serif;
                text-decoration: none;
            }}
            .btn-lg {{ padding: 14px 28px; font-size: 16px; }}
            .btn-sm {{ padding: 6px 12px; font-size: 12px; border-radius: 8px; }}

            .btn-primary {{
                background: linear-gradient(135deg, var(--primary), var(--primary-light));
                color: white;
            }}
            .btn-primary:hover {{ transform: translateY(-1px); box-shadow: 0 6px 20px rgba(30, 58, 138, 0.3); }}
            .btn-secondary {{ background: var(--bg-light); color: var(--gray); border: 2px solid var(--border); }}
            .btn-edit {{ background: var(--warning); color: white; }}
            .btn-edit:hover {{ background: #d97706; }}
            .btn-delete {{ background: var(--danger); color: white; }}
            .btn-delete:hover {{ background: #dc2626; }}
            .btn-cancel {{ background: white; color: var(--gray); border: 2px solid var(--border); }}
            .btn-cancel:hover {{ background: #fee2e2; color: var(--danger); border-color: var(--danger); }}

            .form-actions {{ display: flex; gap: 12px; margin-top: 25px; }}

            .tarkib-box {{
                display: none;
                background: #f0f9ff;
                border: 2px solid #3b82f6;
                padding: 14px 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                font-size: 15px;
                color: #1e40af;
            }}
            .tarkib-box.show {{ display: block; }}

            .alert {{
                padding: 14px 18px;
                border-radius: 10px;
                margin-bottom: 20px;
                font-size: 14px;
                animation: fadeIn 0.3s ease;
            }}
            .alert-success {{ background: #d1fae5; color: #065f46; border-right: 4px solid var(--success); }}
            .alert-error {{ background: #fee2e2; color: #991b1b; border-right: 4px solid var(--danger); }}

            .table-container {{ overflow-x: auto; border-radius: 12px; border: 1px solid var(--border); }}
            .data-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
            .data-table thead th {{
                background: var(--primary);
                color: white;
                padding: 14px 12px;
                text-align: center;
                font-weight: 600;
                font-size: 12px;
                white-space: nowrap;
                position: sticky;
                top: 0;
                z-index: 1;
            }}
            .data-table tbody td {{ padding: 12px; text-align: center; border-bottom: 1px solid var(--border); color: var(--dark); }}
            .data-table tbody tr:hover {{ background: var(--bg-light); }}
            .table-actions {{ display: flex; gap: 6px; justify-content: center; }}
            .table-footer {{ text-align: center; color: var(--light-gray); font-size: 12px; margin-top: 12px; }}
            .pagination {{ display: flex; justify-content: center; align-items: center; gap: 8px; margin-top: 15px; flex-wrap: wrap; }}
            .pagination button {{
                padding: 6px 12px;
                border: 1px solid var(--border);
                border-radius: 6px;
                background: var(--bg-light);
                color: var(--dark);
                cursor: pointer;
                font-family: Tahoma, Arial, sans-serif;
                font-size: 12px;
                transition: var(--transition);
            }}
            .pagination button:hover:not(:disabled) {{ background: var(--primary-light); color: white; border-color: var(--primary-light); }}
            .pagination button:disabled {{ opacity: 0.5; cursor: not-allowed; }}
            .pagination span {{ font-size: 12px; color: var(--gray); }}

            .empty-state {{ text-align: center; padding: 50px 20px; color: var(--light-gray); }}
            .empty-state .icon {{ font-size: 48px; margin-bottom: 15px; }}

            /* مودال ویرایش */
            .edit-modal-overlay {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(4px);
                z-index: 10000;
                justify-content: center;
                align-items: center;
                animation: fadeIn 0.3s ease;
            }}
            .edit-modal-overlay.show {{ display: flex; }}
            .edit-modal {{
                background: white;
                border-radius: 16px;
                padding: 30px;
                width: 90%;
                max-width: 750px;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: slideUp 0.3s ease;
            }}
            @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            .edit-modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid var(--border); }}
            .edit-modal-header h3 {{ margin: 0; color: var(--dark); font-size: 20px; display: flex; align-items: center; gap: 8px; }}
            .edit-modal-close {{
                width: 36px;
                height: 36px;
                border-radius: 8px;
                border: 2px solid var(--border);
                background: white;
                color: var(--gray);
                cursor: pointer;
                font-size: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: var(--transition);
            }}
            .edit-modal-close:hover {{ background: #fee2e2; color: var(--danger); border-color: var(--danger); }}
            .edit-modal-footer {{ display: flex; gap: 10px; justify-content: flex-end; padding-top: 15px; border-top: 1px solid var(--border); }}

            .toast-container {{
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 99999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
            }}
            .toast {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 24px;
                border-radius: 12px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                animation: toastIn 0.4s ease;
                pointer-events: auto;
                min-width: 300px;
            }}
            .toast.success {{ background: linear-gradient(135deg, #059669, #10b981); }}
            .toast.error {{ background: linear-gradient(135deg, #dc2626, #ef4444); }}
            @keyframes toastIn {{ from {{ opacity: 0; transform: translateY(-30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes toastOut {{ from {{ opacity: 1; transform: translateY(0); }} to {{ opacity: 0; transform: translateY(-30px); }} }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

            @media (max-width: 768px) {{
                .form-grid {{ grid-template-columns: 1fr; gap: 15px; }}
                .page-header {{ flex-direction: column; gap: 15px; text-align: center; }}
                .form-actions {{ flex-direction: column; }}
                .form-actions .btn {{ width: 100%; }}
                .tabs {{ overflow-x: auto; }}
                .tab {{ white-space: nowrap; padding: 10px 16px; }}
                .edit-modal {{ padding: 20px; width: 95%; }}
            }}
        </style>
    </head>
    <body>
        <div class="toast-container" id="toastContainer"></div>

        <div class="content-card fade-in">
            <div class="page-header">
                <div class="page-header-left">
                    <h2>📅 تنظیم و مدیریت شیفت‌ها</h2>
                    <p>{form_title}</p>
                </div>
                <a href="/module/supervisor" class="back-btn">⬅️ بازگشت به منو</a>
            </div>

            <div class="tabs">
                <button class="tab active" onclick="switchTab('register')">✨ {'ویرایش' if edit_mode else 'ثبت'} شیفت</button>
                <button class="tab" onclick="switchTab('list')">📋 لیست شیفت‌ها</button>
            </div>

            <div id="tab-register" class="tab-content active">
                <form id="shift-form" action="/module/supervisor/shift/save" method="POST" onsubmit="return submitShiftForm(event)">
                    <div class="form-grid">
                        <div class="form-column">
                            <div class="form-column-title">📋 اطلاعات پایه</div>
                            <div class="form-group">
                                <label>📅 تاریخ ثبت</label>
                                <input type="text" name="date" id="date-input" class="form-input date-mask"
                                       value="{default_date}" placeholder="مثال: {today_shamsi}" required
                                       oninput="generateShiftCode()">
                                <small>فرمت شمسی: YYYY/MM/DD</small>
                            </div>
                            <div class="form-group">
                                <label>📆 روز هفته</label>
                                <select name="day" class="form-input" onchange="generateShiftCode()">
                                    {day_options_html}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>👤 سوپروایزر</label>
                                <input type="text" class="form-input" value="{full_name}" disabled>
                            </div>
                            <div class="form-group">
                                <label>📝 مناسبت‌های امروز</label>
                                <input type="text" name="occasion" class="form-input" value="{default_occasion}" placeholder="اختیاری">
                            </div>
                        </div>

                        <div class="form-column">
                            <div class="form-column-title">🔢 اطلاعات شیفت</div>
                            <div class="form-group">
                                <label>🕒 نام شیفت</label>
                                <select name="shift_type" id="shift-select" class="form-input" onchange="generateShiftCode()">
                                    {shift_options_html}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>🔢 کد شیفت (۹ رقم عددی)</label>
                                <div class="input-with-button">
                                    <input type="text" name="shift_id" id="shift-id-input" class="form-input"
                                           value="{default_shift_id}" placeholder="مثال: 140401011" maxlength="9" required
                                           {'readonly' if edit_mode else ''}>
                                    {'' if edit_mode else '<button type="button" class="btn-generate" onclick="generateShiftCode()">🎯 تولید کد</button>'}
                                </div>
                                <small>{'کد شیفت در حالت ویرایش قابل تغییر نیست' if edit_mode else 'می‌توانید دستی وارد کنید یا از دکمه تولید کد استفاده کنید'}</small>
                            </div>

                            <div id="tarkib-preview" class="tarkib-box">
                                <strong>📌 ترکیب شیفت:</strong>
                                <span id="tarkib-text"></span>
                            </div>

                            <div class="form-group">
                                <label>💡 راهنمای کد شیفت</label>
                                <small style="line-height:2;">
                                   کد شیفت = ۸ رقم تاریخ + ۱ رقم شماره شیفت<br>
                                   شماره‌ها بر اساس نگاشت ثابت: صبح(۱) | صبح و عصر(۲) | عصر(۳) | فول(۴) | عصر و شب(۵) | شب(۶)
                                </small>
                            </div>
                        </div>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary btn-lg" id="save-shift-btn">
                            {submit_label}
                        </button>
                        {'<a href="/module/supervisor/shift" class="btn btn-cancel btn-lg">❌ انصراف از ویرایش</a>' if edit_mode else '<button type="button" class="btn btn-secondary btn-lg" onclick="resetShiftForm()">🔄 پاک کردن فرم</button>'}
                    </div>
                </form>
            </div>

            <div id="tab-list" class="tab-content">
                {list_html}
            </div>
        </div>

        <!-- مودال ویرایش -->
        <div class="edit-modal-overlay" id="editModal" onclick="if(event.target===this)closeEditModal()">
            <div class="edit-modal">
                <div class="edit-modal-header">
                    <h3>✏️ ویرایش شیفت</h3>
                    <button class="edit-modal-close" onclick="closeEditModal()">✕</button>
                </div>
                <div class="edit-modal-body">
                    <form id="edit-shift-form" onsubmit="return false;">
                        <input type="hidden" id="edit-shift-id-old" value="">
                        <div class="form-grid">
                            <div class="form-column">
                                <div class="form-column-title">📋 اطلاعات پایه</div>
                                <div class="form-group">
                                    <label>📅 تاریخ ثبت</label>
                                    <input type="text" id="edit-date" class="form-input date-mask"
                                           placeholder="YYYY/MM/DD" required oninput="updateEditTarkib()">
                                </div>
                                <div class="form-group">
                                    <label>📆 روز هفته</label>
                                    <select id="edit-day" class="form-input" onchange="updateEditTarkib()">
                                        {day_options_html}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>👤 سوپروایزر</label>
                                    <input type="text" class="form-input" value="{full_name}" disabled>
                                </div>
                                <div class="form-group">
                                    <label>📝 مناسبت‌های امروز</label>
                                    <input type="text" id="edit-occasion" class="form-input" placeholder="اختیاری">
                                </div>
                            </div>
                            <div class="form-column">
                                <div class="form-column-title">🔢 اطلاعات شیفت</div>
                                <div class="form-group">
                                    <label>🕒 نام شیفت</label>
                                    <select id="edit-shift-type" class="form-input" onchange="updateEditTarkib()">
                                        {shift_options_html}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>🔢 کد شیفت (۹ رقم عددی)</label>
                                    <input type="text" id="edit-shift-code" class="form-input"
                                           placeholder="مثال: 140401011" maxlength="9" required oninput="updateEditTarkib()">
                                </div>
                                <div id="edit-tarkib-preview" class="tarkib-box show">
                                    <strong>📌 ترکیب شیفت:</strong>
                                    <span id="edit-tarkib-text"></span>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="edit-modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeEditModal()">❌ انصراف</button>
                    <button type="button" class="btn btn-primary" onclick="submitEditShift()" id="edit-save-btn">
                        <span id="edit-save-text">💾 بروزرسانی تغییرات</span>
                        <span id="edit-save-spinner" style="display: none;">⏳ در حال ذخیره...</span>
                    </button>
                </div>
            </div>
        </div>

        <script>
            var shiftNumberMap = {shift_number_map_json};
            var deleteTargetId = null;

            function showToast(message, type) {{
                var container = document.getElementById('toastContainer');
                var toast = document.createElement('div');
                toast.className = 'toast ' + (type || 'info');
                toast.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + message + '</span><span style="cursor:pointer;margin-right:auto;opacity:0.7;" onclick="this.parentElement.remove()">✕</span>';
                container.appendChild(toast);
                setTimeout(function() {{
                    if (toast.parentElement) {{
                        toast.style.animation = 'toastOut 0.3s ease forwards';
                        setTimeout(function() {{ toast.remove(); }}, 300);
                    }}
                }}, 4000);
            }}

            function switchTab(tabName) {{
                document.querySelectorAll('.tab').forEach(function(t, idx) {{
                    t.classList.toggle('active', (tabName === 'register' && idx === 0) || (tabName === 'list' && idx === 1));
                }});
                document.getElementById('tab-register').classList.toggle('active', tabName === 'register');
                document.getElementById('tab-list').classList.toggle('active', tabName === 'list');
                if (tabName === 'list') loadShiftList(1);
            }}

            function generateShiftCode() {{
                var dateInput = document.getElementById('date-input');
                var shiftSelect = document.getElementById('shift-select');
                var codeInput = document.getElementById('shift-id-input');
                var tarkibBox = document.getElementById('tarkib-preview');
                var tarkibText = document.getElementById('tarkib-text');
                var daySelect = document.querySelector('select[name="day"]');

                if (codeInput.hasAttribute('readonly')) return;

                var date = dateInput.value.replace(/[\\/\\-]/g, '');
                var selectedOption = shiftSelect.options[shiftSelect.selectedIndex];
                var shiftName = selectedOption.text;

                if (date.length === 8 && shiftSelect.value) {{
                    var shiftId = shiftSelect.value;
                    var shiftNum = shiftNumberMap[shiftId] || shiftId;
                    if (String(shiftNum).length > 1) {{
                        // اگر شماره بیش از یک رقم باشد، کد طولانی‌تر می‌شود؛ بهتر است خطا نشان دهیم
                        showToast('شماره شیفت باید یک رقمی باشد', 'error');
                        return;
                    }}
                    var code = date + shiftNum;
                    codeInput.value = code;

                    var day = daySelect.value;
                    var formattedDate = date.substring(0,4) + '/' + date.substring(4,6) + '/' + date.substring(6,8);
                    var tarkib = day + ' ' + formattedDate + ' ' + shiftName;
                    tarkibText.textContent = tarkib;
                    tarkibBox.classList.add('show');
                }} else {{
                    tarkibBox.classList.remove('show');
                }}
            }}

            function resetShiftForm() {{
                document.getElementById('shift-form').reset();
                document.getElementById('tarkib-preview').classList.remove('show');
                document.getElementById('shift-id-input').value = '';
            }}

            function validateShiftForm() {{
                var dateInput = document.getElementById('date-input');
                var shiftIdInput = document.getElementById('shift-id-input');
                var shiftSelect = document.getElementById('shift-select');

                var date = dateInput.value.replace(/[\\/\\-]/g, '');
                if (date.length !== 8 || isNaN(date)) {{
                    showToast('⛔ لطفاً تاریخ را به صورت صحیح وارد کنید (۸ رقم)', 'error');
                    dateInput.focus();
                    return false;
                }}

                var shiftId = shiftIdInput.value.trim();
                if (shiftId.length !== 9 || isNaN(shiftId)) {{
                    showToast('⛔ کد شیفت باید دقیقاً ۹ رقم عددی باشد', 'error');
                    shiftIdInput.focus();
                    return false;
                }}

                if (!shiftSelect.value) {{
                    showToast('⛔ لطفاً نام شیفت را انتخاب کنید', 'error');
                    shiftSelect.focus();
                    return false;
                }}

                // اعتبارسنجی تاریخ شمسی
                var dateVal = dateInput.value.trim();
                if (dateVal) {{
                    var check = validateShamsiDate(dateVal);
                    if (!check.valid) {{
                        showToast('⛔ ' + check.message, 'error');
                        dateInput.focus();
                        return false;
                    }}
                }}

                return true;
            }}

            async function submitShiftForm(event) {{
                event.preventDefault();
                if (!validateShiftForm()) return false;
                const form = document.getElementById('shift-form');
                const formData = new FormData(form);
                const btn = document.getElementById('save-shift-btn');
                const originalText = btn.innerHTML;
                btn.disabled = true;
                btn.innerHTML = '⏳ در حال ذخیره...';

                try {{
                    const resp = await fetch(form.action, {{
                        method: 'POST',
                        body: formData
                    }});
                    const data = await resp.json();
                    if (data.success) {{
                        showToast(data.message, 'success');
                        form.reset();
                        document.getElementById('tarkib-preview').classList.remove('show');
                        if (document.getElementById('tab-list').classList.contains('active')) {{
                            loadShiftList(1);
                        }}
                    }} else {{
                        showToast(data.message, 'error');
                    }}
                }} catch (err) {{
                    showToast('خطا در ارتباط با سرور', 'error');
                }} finally {{
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                }}
            }}

            async function deleteShiftAjax(shiftId) {{
                if (!confirm('آیا از حذف این شیفت اطمینان دارید؟')) return;
                try {{
                    const resp = await fetch('/module/supervisor/shift/delete/' + shiftId, {{ method: 'POST' }});
                    const data = await resp.json();
                    if (data.success) {{
                        showToast(data.message, 'success');
                        loadShiftList(currentShiftPage);
                    }} else {{
                        showToast(data.message, 'error');
                    }}
                }} catch(e) {{
                    showToast('خطا در ارتباط با سرور', 'error');
                }}
            }}

            function openEditModal(data) {{
                document.getElementById('edit-shift-id-old').value = data.id;
                document.getElementById('edit-date').value = data.date;
                document.getElementById('edit-day').value = data.day;
                document.getElementById('edit-shift-type').value = data.shift_type_id;   // حالا ID_onvan_shift
                document.getElementById('edit-occasion').value = data.occasion || '';
                document.getElementById('edit-shift-code').value = data.id;

                updateEditTarkib();
                document.getElementById('editModal').classList.add('show');
            }}

            function closeEditModal() {{
                document.getElementById('editModal').classList.remove('show');
            }}

            function updateEditTarkib() {{
                var date = document.getElementById('edit-date').value;
                var day = document.getElementById('edit-day').value;
                var shiftSelect = document.getElementById('edit-shift-type');
                var shiftName = shiftSelect.options[shiftSelect.selectedIndex].text;

                var tarkibText = document.getElementById('edit-tarkib-text');
                var tarkibBox = document.getElementById('edit-tarkib-preview');

                if (date && day && shiftSelect.value) {{
                    tarkibText.textContent = day + ' ' + date + ' ' + shiftName;
                    tarkibBox.classList.add('show');
                }} else {{
                    tarkibBox.classList.remove('show');
                }}
            }}

            function submitEditShift() {{
                var date = document.getElementById('edit-date').value.trim();
                var day = document.getElementById('edit-day').value;
                var shiftType = document.getElementById('edit-shift-type').value;   // ID_onvan_shift
                var occasion = document.getElementById('edit-occasion').value;
                var newShiftCode = document.getElementById('edit-shift-code').value.trim();
                var oldShiftId = document.getElementById('edit-shift-id-old').value;

                var dateNum = date.replace(/[\\/\\-]/g, '');
                if (dateNum.length !== 8 || isNaN(dateNum)) {{
                    showToast('⛔ لطفاً تاریخ را به صورت صحیح وارد کنید (۸ رقم)', 'error');
                    return;
                }}

                if (!shiftType) {{
                    showToast('⛔ لطفاً نام شیفت را انتخاب کنید', 'error');
                    return;
                }}

                if (!day) {{
                    showToast('⛔ لطفاً روز هفته را انتخاب کنید', 'error');
                    return;
                }}

                if (newShiftCode.length !== 9 || isNaN(newShiftCode)) {{
                    showToast('⛔ کد شیفت باید دقیقاً ۹ رقم عددی باشد', 'error');
                    return;
                }}

                // اعتبارسنجی تاریخ شمسی
                var editDate = document.getElementById('edit-date').value.trim();
                if (editDate) {{
                    var check = validateShamsiDate(editDate);
                    if (!check.valid) {{
                        showToast('⛔ ' + check.message, 'error');
                        return;
                    }}
                }}

                var saveText = document.getElementById('edit-save-text');
                var saveSpinner = document.getElementById('edit-save-spinner');
                var saveBtn = document.getElementById('edit-save-btn');
                saveText.style.display = 'none';
                saveSpinner.style.display = 'inline-flex';
                saveBtn.disabled = true;

                var formData = new FormData();
                formData.append('date', date);
                formData.append('day', day);
                formData.append('shift_type', shiftType);
                formData.append('occasion', occasion);
                formData.append('new_shift_id', newShiftCode);

                fetch('/module/supervisor/shift/edit/' + oldShiftId, {{
                    method: 'POST',
                    body: formData,
                    headers: {{
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    }}
                }})
                .then(function(response) {{ return response.json(); }})
                .then(function(data) {{
                    saveText.style.display = 'inline';
                    saveSpinner.style.display = 'none';
                    saveBtn.disabled = false;
                    if (data.success) {{
                        showToast('✅ ' + data.message, 'success');
                        closeEditModal();
                        loadShiftList(currentShiftPage);
                    }} else {{
                        showToast('⛔ ' + data.message, 'error');
                    }}
                }})
                .catch(function() {{
                    saveText.style.display = 'inline';
                    saveSpinner.style.display = 'none';
                    saveBtn.disabled = false;
                    showToast('⛔ خطا در ارتباط با سرور', 'error');
                }});
            }}

            // ========== صفحه‌بندی لیست شیفت‌ها ==========
            var currentShiftPage = 1;

            async function loadShiftList(page) {{
                currentShiftPage = page;
                const container = document.getElementById('shift-list-container');
                container.innerHTML = '<div class="empty-state"><p>در حال بارگذاری...</p></div>';
                try {{
                    const resp = await fetch('/module/supervisor/shift/list?page=' + page + '&per_page=15');
                    const data = await resp.json();
                    if (data.success) {{
                        renderShiftTable(data.shifts);
                        renderPagination(data.page, data.total_pages);
                    }} else {{
                        container.innerHTML = '<div class="empty-state"><p>خطا در دریافت لیست</p></div>';
                    }}
                }} catch(e) {{
                    container.innerHTML = '<div class="empty-state"><p>خطا در ارتباط با سرور</p></div>';
                }}
            }}

            function renderShiftTable(shifts) {{
                const container = document.getElementById('shift-list-container');
                if (!shifts.length) {{
                    container.innerHTML = '<div class="empty-state"><div class="icon">📭</div><p>هنوز هیچ شیفتی ثبت نشده است</p></div>';
                    return;
                }}

                let html = '<div class="table-container"><table class="data-table"><thead><tr><th>کد شیفت</th><th>تاریخ</th><th>روز</th><th>عنوان</th><th>سوپروایزر</th><th>ترکیب</th><th>عملیات</th></tr></thead><tbody>';

                shifts.forEach(function(s) {{
                    const dateDisplay = String(s.dat_sabt).length === 8 ? String(s.dat_sabt).substring(0,4) + '/' + String(s.dat_sabt).substring(4,6) + '/' + String(s.dat_sabt).substring(6,8) : s.dat_sabt;
                    const shiftDataJson = JSON.stringify({{
                        id: String(s.ID_shift),
                        date: dateDisplay,
                        day: s.roz_hafteh || '',
                        shift_type_id: s.shift_type_id || '',
                        occasion: s.monasebat || ''
                    }});

                    html += '<tr>' +
                        '<td><strong>' + s.ID_shift + '</strong></td>' +
                        '<td>' + dateDisplay + '</td>' +
                        '<td>' + (s.roz_hafteh || '-') + '</td>' +
                        '<td>' + (s.nam_shift || '-') + '</td>' +
                        '<td>' + (s.nam_super || '-') + '</td>' +
                        '<td>' + (s.tarkib || '-') + '</td>' +
                        '<td><div class="table-actions">' +
                            '<button class="btn btn-edit btn-sm" onclick=\\'openEditModal(' + shiftDataJson + ')\\'>✏️</button>' +
                            '<button class="btn btn-delete btn-sm" onclick="deleteShiftAjax(\\'' + s.ID_shift + '\\')">🗑️</button>' +
                        '</div></td>' +
                    '</tr>';
                }});

                html += '</tbody></table></div>';
                html += '<div class="table-footer">📊 تعداد کل شیفت‌های ثبت شده: <strong>' + shifts.length + '</strong> مورد</div>';
                container.innerHTML = html;
            }}

            function renderPagination(currentPage, totalPages) {{
                const container = document.getElementById('pagination-container');
                if (totalPages <= 1) {{
                    container.innerHTML = '';
                    return;
                }}
                let html = '';
                if (currentPage > 1) {{
                    html += '<button onclick="loadShiftList(' + (currentPage - 1) + ')">« قبلی</button>';
                }}
                html += '<span>صفحه ' + currentPage + ' از ' + totalPages + '</span>';
                if (currentPage < totalPages) {{
                    html += '<button onclick="loadShiftList(' + (currentPage + 1) + ')">بعدی »</button>';
                }}
                container.innerHTML = html;
            }}

            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') closeEditModal();
            }});

            document.addEventListener('DOMContentLoaded', function() {{
                var codeInput = document.getElementById('shift-id-input');
                if (codeInput.value.length === 9) {{
                    generateShiftCode();
                }}
                document.getElementById('date-input').focus();
            }});

            // ماسک و اعتبارسنجی تاریخ شمسی
            document.addEventListener('DOMContentLoaded', function() {{
                document.querySelectorAll('.date-mask').forEach(function(inp) {{
                    inp.addEventListener('input', function(e) {{
                        var val = this.value.replace(/[^0-9]/g, '');
                        if (val.length > 8) val = val.substring(0,8);
                        var formatted = '';
                        if (val.length > 0) {{
                            formatted = val.substring(0,4);
                            if (val.length > 4) formatted += '/' + val.substring(4,6);
                            if (val.length > 6) formatted += '/' + val.substring(6,8);
                        }}
                        this.value = formatted;
                    }});
                    inp.addEventListener('blur', function() {{
                        var val = this.value.trim();
                        if (val === '') return;
                        var result = validateShamsiDate(val);
                        if (!result.valid) {{
                            this.style.borderColor = 'var(--danger)';
                            showToast('⚠️ ' + result.message, 'error');
                        }} else {{
                            this.style.borderColor = 'var(--border)';
                        }}
                    }});
                    inp.addEventListener('focus', function() {{
                        this.style.borderColor = 'var(--border)';
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    '''
    return html


def get_shift_list_html(user):
    return '''
    <div id="shift-list-container" style="min-height: 200px;">
        <div class="empty-state">
            <p>برای مشاهده لیست، روی تب "لیست شیفت‌ها" کلیک کنید.</p>
        </div>
    </div>
    <div id="pagination-container" class="pagination"></div>
    '''


def get_shift_list_api(user, page=1, per_page=15):
    user_id = user.get('UserID', 0)
    offset = (page - 1) * per_page

    total_row = query("SELECT COUNT(*) as cnt FROM shift_namt WHERE UserID = %s",
                      params=(user_id,), fetch_one=True)
    total = total_row['cnt'] if total_row else 0

    shifts = query(
        """SELECT s.ID_shift, s.dat_sabt, s.tarkib, s.roz_hafteh, s.nam_super, s.monasebat,
                  o.nam_shift as shift_name, s.nam_shift as shift_type_id
           FROM shift_namt s
           LEFT JOIN onvan_shift o ON s.nam_shift = o.ID_onvan_shift
           WHERE s.UserID = %s
           ORDER BY s.ID_shift DESC
           LIMIT %s OFFSET %s""",
        params=(user_id, per_page, offset),
        fetch_all=True
    ) or []

    # اصلاح نام‌ها برای سمت کلاینت
    for s in shifts:
        s['nam_shift'] = s['shift_name'] or str(s['shift_type_id'])
        for key in list(s.keys()):
            if isinstance(s[key], (bytearray, bytes)):
                s[key] = s[key].decode('utf-8', errors='ignore')

    total_pages = math.ceil(total / per_page) if total > 0 else 1

    return {
        'success': True,
        'shifts': shifts,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }


def save_shift(user, form_data):
    date = form_data.get('date', '').replace('/', '').replace('-', '').strip()
    day = form_data.get('day', '').strip()
    shift_type = form_data.get('shift_type', '').strip()   # حالا این ID_onvan_shift است
    shift_id = form_data.get('shift_id', '').strip()
    occasion = form_data.get('occasion', '').strip()
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    if len(date) != 8 or not date.isdigit():
        return {'success': False, 'message': "⛔ تاریخ باید ۸ رقم عددی باشد"}
    if len(shift_id) != 9 or not shift_id.isdigit():
        return {'success': False, 'message': "⛔ کد شیفت باید ۹ رقم عددی باشد"}
    if not shift_type:
        return {'success': False, 'message': "⛔ لطفاً نام شیفت را انتخاب کنید"}
    if not day:
        return {'success': False, 'message': "⛔ لطفاً روز هفته را انتخاب کنید"}

    # بررسی تکراری نبودن کد شیفت
    existing = query("SELECT ID_shift FROM shift_namt WHERE ID_shift = %s",
                     params=(shift_id,), fetch_one=True)
    if existing:
        return {'success': False, 'message': f"⛔ کد شیفت {shift_id} قبلاً ثبت شده است"}

    # دریافت نام شیفت برای ترکیب
    shift_name_row = query("SELECT nam_shift FROM onvan_shift WHERE ID_onvan_shift = %s",
                           params=(shift_type,), fetch_one=True)
    shift_name = shift_name_row['nam_shift'] if shift_name_row else str(shift_type)

    tarkib = f"{day} {date[:4]}/{date[4:6]}/{date[6:]} {shift_name}"

    try:
        query(
            """INSERT INTO shift_namt
               (ID_shift, dat_sabt, roz_hafteh, nam_super, nam_shift, tarkib, monasebat, UserID, CreatedDate)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            params=(shift_id, date, day, full_name, int(shift_type), tarkib, occasion, user_id, datetime.now()),
            commit=True
        )
        log_crud('save_shift', user_id, key_value=shift_id,
                 new_value=f"تاریخ:{date}, روز:{day}, شیفت:{shift_name}")
        return {'success': True, 'message': "✅ شیفت با موفقیت ثبت شد"}
    except Exception as e:
        if 'Duplicate entry' in str(e) or 'duplicate key' in str(e).lower():
            return {'success': False, 'message': f"⛔ کد شیفت {shift_id} قبلاً ثبت شده است"}
        log_crud('save_shift', user_id, status="Failed", error_msg=str(e))
        return {'success': False, 'message': f"⛔ خطا در ذخیره‌سازی: {str(e)}"}


def get_shift_for_edit(shift_id, user_id):
    return query(
        "SELECT * FROM shift_namt WHERE ID_shift = %s AND UserID = %s",
        params=(shift_id, user_id),
        fetch_one=True
    )


def update_shift(shift_id, user_id, form_data):
    date = form_data.get('date', '').replace('/', '').replace('-', '').strip()
    day = form_data.get('day', '').strip()
    shift_type = form_data.get('shift_type', '').strip()   # ID_onvan_shift
    occasion = form_data.get('occasion', '').strip()
    new_shift_id = form_data.get('new_shift_id', '').strip()

    if len(date) != 8 or not date.isdigit():
        return {'success': False, 'message': "⛔ تاریخ باید ۸ رقم عددی باشد"}
    if not shift_type:
        return {'success': False, 'message': "⛔ لطفاً نام شیفت را انتخاب کنید"}

    if new_shift_id and new_shift_id != str(shift_id):
        if len(new_shift_id) != 9 or not new_shift_id.isdigit():
            return {'success': False, 'message': "⛔ کد شیفت جدید باید ۹ رقم عددی باشد"}
        existing = query("SELECT ID_shift FROM shift_namt WHERE ID_shift = %s",
                         params=(new_shift_id,), fetch_one=True)
        if existing:
            return {'success': False, 'message': f"⛔ کد شیفت {new_shift_id} قبلاً ثبت شده است"}
        target_id = new_shift_id
    else:
        target_id = shift_id

    shift_name_row = query("SELECT nam_shift FROM onvan_shift WHERE ID_onvan_shift = %s",
                           params=(shift_type,), fetch_one=True)
    shift_name = shift_name_row['nam_shift'] if shift_name_row else str(shift_type)

    tarkib = f"{day} {date[:4]}/{date[4:6]}/{date[6:]} {shift_name}"

    try:
        if target_id != str(shift_id):
            full_name = query("SELECT FullName FROM users WHERE UserID = %s",
                              params=(user_id,), fetch_one=True)['FullName']
            query("DELETE FROM shift_namt WHERE ID_shift = %s AND UserID = %s",
                  params=(shift_id, user_id), commit=True)
            query(
                """INSERT INTO shift_namt
                   (ID_shift, dat_sabt, roz_hafteh, nam_super, nam_shift, tarkib, monasebat, UserID, CreatedDate)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                params=(target_id, date, day, full_name, int(shift_type), tarkib, occasion, user_id, datetime.now()),
                commit=True
            )
        else:
            query(
                """UPDATE shift_namt
                   SET dat_sabt = %s, roz_hafteh = %s, nam_shift = %s, tarkib = %s, monasebat = %s
                   WHERE ID_shift = %s AND UserID = %s""",
                params=(date, day, int(shift_type), tarkib, occasion, shift_id, user_id),
                commit=True
            )
        log_crud('update_shift', user_id, key_value=shift_id,
                 new_value=f"تاریخ:{date}, روز:{day}, شیفت:{shift_name}")
        return {'success': True, 'message': "✅ شیفت با موفقیت بروزرسانی شد"}
    except Exception as e:
        log_crud('update_shift', user_id, status="Failed", error_msg=str(e))
        return {'success': False, 'message': f"⛔ خطا در بروزرسانی: {str(e)}"}


def delete_shift(shift_id, user_id):
    shift = query(
        "SELECT * FROM shift_namt WHERE ID_shift = %s AND UserID = %s",
        params=(shift_id, user_id),
        fetch_one=True
    )
    if not shift:
        return {'success': False, 'message': "⛔ شیفت مورد نظر یافت نشد یا متعلق به شما نیست"}

    dependencies = {
        "tbl_ankal": "nam_shift",
        "tbl_hozor": "nam_shift",
        "tbl_gozaresh": "ID_shift",
        "tbl_amar_data": "nam_shift",
        "tbl_ghaybat": "nam_shift",
    }
    for table, column in dependencies.items():
        try:
            result = query(f"SELECT COUNT(*) as cnt FROM {table} WHERE {column} = %s",
                           params=(shift_id,), fetch_one=True)
            if result and result.get('cnt', 0) > 0:
                return {'success': False, 'message': f"⛔ این شیفت در {table} اطلاعات ثبت شده دارد و قابل حذف نیست"}
        except:
            pass

    try:
        query("DELETE FROM shift_namt WHERE ID_shift = %s AND UserID = %s",
              params=(shift_id, user_id), commit=True)
        log_crud('delete_shift', user_id, key_value=shift_id, status="Success")
        return {'success': True, 'message': "✅ شیفت با موفقیت حذف شد"}
    except Exception as e:
        log_crud('delete_shift', user_id, key_value=shift_id, status="Failed", error_msg=str(e))
        return {'success': False, 'message': f"⛔ خطا در حذف: {str(e)}"}
        
        
        