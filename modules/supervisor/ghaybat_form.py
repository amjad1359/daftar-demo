"""
فرم ثبت غیبت، تاخیر، تعجیل و پاس ساعتی - سوپروایزر (ویرایش نهایی)
ذخیره‌سازی rizshift بر اساس ID_onvan_shift
"""

from models.database import query
import jdatetime
from datetime import datetime
import json
from utils.auto_log import log_crud


def _ensure_rizshift_int():
    """تبدیل ستون rizshift در tbl_ghaybat از VARCHAR به INT (در صورت وجود)"""
    try:
        col = query("SHOW COLUMNS FROM tbl_ghaybat LIKE 'rizshift'", fetch_one=True)
        if col and 'varchar' in str(col.get('Type', '')).lower():
            query("UPDATE tbl_ghaybat SET rizshift = NULL WHERE rizshift IS NOT NULL AND rizshift REGEXP '[^0-9]'", commit=True)
            query("ALTER TABLE tbl_ghaybat MODIFY COLUMN rizshift INT DEFAULT NULL", commit=True)
    except Exception:
        pass


def get_ghaybat_form(user):
    """صفحه اصلی ثبت غیبت، تاخیر، تعجیل و پاس ساعتی"""

    _ensure_rizshift_int()

    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    # ========== شیفت فعال ==========
    active_shift = query(
        "SELECT ID_shift, tarkib, nam_shift FROM shift_namt ORDER BY ID_shift DESC LIMIT 1",
        fetch_one=True
    )
    if not active_shift:
        return '''
        <div class="content-card fade-in">
            <div style="text-align:center;padding:60px;">
                <div style="font-size:64px;">⚠️</div>
                <h3>شیفت فعالی یافت نشد</h3>
                <p style="color:#94a3b8;">لطفاً ابتدا یک شیفت ثبت کنید</p>
                <a href="/module/supervisor/shift" class="btn btn-primary">📅 ثبت شیفت</a>
            </div>
        </div>'''

    shift_id = active_shift['ID_shift']
    shift_name = active_shift['tarkib'] or active_shift.get('nam_shift', '---')

    # nam_shift در shift_namt حالا ID_onvan_shift است
    default_rizshift_id = active_shift.get('nam_shift', '')

    # ========== بخش‌ها ==========
    departments = query(
        "SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh",
        fetch_all=True
    ) or []

    # ========== لیست شیفت‌ها برای dropdown ==========
    shift_list = query(
        "SELECT ID_onvan_shift, shift_code FROM onvan_shift ORDER BY shift_code",
        fetch_all=True
    ) or []

    # ========== گزینه‌های ریزشیفت (value = ID_onvan_shift، نمایش = shift_code) ==========
    shift_options = '<option value="">---</option>'
    for s in shift_list:
        shift_options += f'<option value="{s["ID_onvan_shift"]}">{s["shift_code"]}</option>'

    # ========== JSON پرسنل هر بخش ==========
    dept_personnel_json = _build_personnel_json(departments)

    # ========== آمار ==========
    present_count = query(
        "SELECT COUNT(*) as cnt FROM tbl_hozor WHERE nam_shift = %s AND ispresent = 1",
        params=(shift_id,), fetch_one=True
    )['cnt'] if query(
        "SELECT COUNT(*) as cnt FROM tbl_hozor WHERE nam_shift = %s AND ispresent = 1",
        params=(shift_id,), fetch_one=True
    )['cnt'] else 0

    ghaibat_count = query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND ghaibat = 1",
        params=(shift_id,), fetch_one=True
    )['cnt'] if query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND ghaibat = 1",
        params=(shift_id,), fetch_one=True
    ) else 0

    takhir_count = query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND takhir_saati = 1",
        params=(shift_id,), fetch_one=True
    )['cnt'] if query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND takhir_saati = 1",
        params=(shift_id,), fetch_one=True
    ) else 0

    taajil_count = query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND taajil_khoroj = 1",
        params=(shift_id,), fetch_one=True
    )['cnt'] if query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND taajil_khoroj = 1",
        params=(shift_id,), fetch_one=True
    ) else 0

    pas_count = query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND pas_saati = 1",
        params=(shift_id,), fetch_one=True
    )['cnt'] if query(
        "SELECT COUNT(*) as cnt FROM tbl_ghaybat WHERE nam_shift = %s AND pas_saati = 1",
        params=(shift_id,), fetch_one=True
    ) else 0

    # ========== گزینه‌های بخش ==========
    dept_options = '<option value="">--- انتخاب بخش ---</option>'
    for d in departments:
        dept_options += f'<option value="{d["ID_nam_bakhsh"]}">{d["nam_bakhsh"]}</option>'

    # ========== HTML ==========
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981; --danger: #ef4444;
        --warning: #f59e0b; --dark: #1e293b; --gray: #64748b; --light-gray: #94a3b8;
        --border: #e2e8f0; --bg-light: #f8fafc; --radius: 12px; --transition: 0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; background: #f1f5f9; color: var(--dark); }}
    .fade-in {{ animation: fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .content-card {{ max-width: 1400px; margin: 0 auto; }}

    .gh-header {{
        background: linear-gradient(135deg, #b91c1c, #dc2626);
        color: white; padding: 25px 30px; border-radius: 16px;
        margin-bottom: 25px; display: flex; justify-content: space-between;
        align-items: center; box-shadow: 0 8px 30px rgba(185,28,28,0.25);
    }}
    .gh-header h2 {{ font-size:22px; margin:0 0 5px 0; }}
    .gh-header p {{ opacity:0.85; font-size:13px; margin:0; }}
    .shift-badge {{
        background: rgba(255,255,255,0.15); padding: 10px 20px;
        border-radius: 30px; font-size: 14px; font-weight: bold;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .back-btn {{
        color: white; text-decoration: none; padding: 8px 16px;
        border: 1px solid rgba(255,255,255,0.3); border-radius: 8px;
        font-size: 13px; transition: var(--transition);
    }}
    .back-btn:hover {{ background: rgba(255,255,255,0.15); }}

    .kpi-row {{
        display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 25px;
    }}
    .kpi-card {{
        background: white; border-radius: 14px; padding: 20px; text-align: center;
        border: 1px solid var(--border); transition: var(--transition);
    }}
    .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }}
    .kpi-value {{ font-size: 28px; font-weight: bold; }}
    .kpi-label {{ font-size: 12px; color: var(--gray); margin-top: 4px; }}

    .tabs {{ display: flex; gap: 5px; margin-bottom: 25px; border-bottom: 2px solid var(--border); }}
    .tab {{ padding: 12px 24px; font-size: 14px; font-weight: 600; border: none; background: none;
        color: var(--light-gray); cursor: pointer; border-bottom: 2px solid transparent;
        margin-bottom: -2px; transition: var(--transition); font-family: Tahoma; }}
    .tab:hover {{ color: var(--dark); }}
    .tab.active {{ color: var(--primary-light); border-bottom-color: var(--primary-light); }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}

    .main-grid {{ display: grid; grid-template-columns: 1fr 1.5fr; gap: 25px; }}

    .form-panel {{
        background: white; border-radius: 14px; padding: 25px;
        border: 1px solid var(--border);
    }}
    .form-title {{
        font-size: 16px; font-weight: bold; color: var(--dark);
        margin-bottom: 20px; padding-bottom: 12px;
        border-bottom: 2px solid var(--border);
    }}

    .form-group {{ margin-bottom: 18px; }}
    .form-group label {{
        display: block; font-size: 13px; font-weight: 600;
        color: var(--gray); margin-bottom: 6px;
    }}
    .form-select {{
        width: 100%; padding: 12px 14px; border: 2px solid var(--border);
        border-radius: 10px; font-size: 14px; font-family: Tahoma;
        background: white; transition: var(--transition);
    }}
    .form-select:focus {{ border-color: var(--primary-light); outline: none; }}

    .checkbox-group {{
        display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;
    }}
    .checkbox-item {{
        display: flex; align-items: center; gap: 8px;
        padding: 10px 14px; border: 2px solid var(--border);
        border-radius: 10px; cursor: pointer; transition: var(--transition);
        font-size: 13px; color: var(--dark);
    }}
    .checkbox-item:hover {{ border-color: var(--primary-light); }}
    .checkbox-item input[type="checkbox"] {{
        width: 18px; height: 18px; accent-color: var(--primary);
    }}

    .form-input {{
        width: 100%; padding: 12px 14px; border: 2px solid var(--border);
        border-radius: 10px; font-size: 14px; font-family: Tahoma; transition: var(--transition);
    }}
    .form-input:focus {{ border-color: var(--primary-light); outline: none; }}

    .btn {{
        display: inline-flex; align-items: center; justify-content: center; gap: 6px;
        padding: 12px 24px; border: none; border-radius: 10px;
        font-size: 14px; font-weight: 600; cursor: pointer;
        font-family: Tahoma; transition: var(--transition); text-decoration: none;
    }}
    .btn-primary {{
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        color: white; box-shadow: 0 4px 15px rgba(30,58,138,0.2);
    }}
    .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(30,58,138,0.3); }}
    .btn-danger {{ background: var(--danger); color: white; }}
    .btn-danger:hover {{ background: #dc2626; }}
    .btn-sm {{ padding: 6px 12px; font-size: 12px; border-radius: 8px; }}
    .btn-xs {{ padding: 4px 10px; font-size: 11px; border-radius: 6px; }}

    .list-panel {{
        background: white; border-radius: 14px; padding: 25px;
        border: 1px solid var(--border); max-height: 600px; overflow-y: auto;
    }}

    .record-item {{
        background: var(--bg-light); border: 1px solid var(--border);
        border-radius: 10px; padding: 15px; margin-bottom: 10px;
        transition: var(--transition);
    }}
    .record-item:hover {{ border-color: var(--primary-light); }}
    .record-item .r-header {{
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 8px;
    }}
    .r-person {{ font-weight: bold; font-size: 14px; color: var(--dark); }}
    .r-dept {{
        font-size: 12px; color: var(--primary-light);
        background: #dbeafe; padding: 3px 10px; border-radius: 15px;
    }}
    .r-statuses {{
        display: flex; gap: 8px; flex-wrap: wrap;
        margin: 10px 0;
    }}
    .status-badge {{
        padding: 3px 10px; border-radius: 15px;
        font-size: 11px; font-weight: 600;
    }}
    .badge-ghaibat {{ background: #fee2e2; color: #991b1b; }}
    .badge-takhir {{ background: #fef3c7; color: #92400e; }}
    .badge-taajil {{ background: #fce7f3; color: #9d174d; }}
    .badge-pas {{ background: #dbeafe; color: #1e40af; }}

    .r-desc {{ font-size: 12px; color: var(--gray); margin-top: 8px; }}
    .r-shift {{ font-size: 12px; color: var(--primary); margin-top: 4px; }}
    .r-actions {{ display: flex; gap: 5px; margin-top: 8px; justify-content: flex-end; }}

    .empty-list {{ text-align: center; padding: 40px 20px; color: var(--light-gray); }}

    .toast-container {{
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        z-index: 10000; display: flex; flex-direction: column-reverse; gap: 10px;
        pointer-events: none;
    }}
    .toast {{
        display: flex; align-items: center; gap: 12px;
        padding: 14px 22px; border-radius: 12px; color: white;
        font-size: 14px; font-weight: 600;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: slideUp 0.4s ease;
        pointer-events: auto;
    }}
    .toast.success {{ background: linear-gradient(135deg, #059669, #10b981); }}
    .toast.error {{ background: linear-gradient(135deg, #dc2626, #ef4444); }}
    .toast .toast-close {{
        margin-right: auto; cursor: pointer; opacity: 0.7; font-size: 16px;
    }}

    @keyframes slideUp {{
        from {{ opacity:0; transform:translateY(30px); }}
        to {{ opacity:1; transform:translateY(0); }}
    }}

    @media (max-width: 992px) {{
        .main-grid {{ grid-template-columns: 1fr; }}
        .kpi-row {{ grid-template-columns: repeat(3, 1fr); }}
    }}
    @media (max-width: 576px) {{
        .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
        .checkbox-group {{ grid-template-columns: 1fr; }}
        .gh-header {{ flex-direction: column; gap: 15px; text-align: center; }}
    }}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="content-card fade-in">
    <div class="gh-header">
        <div>
            <h2>❌ ثبت غیبت، تاخیر، تعجیل و پاس ساعتی</h2>
            <p>مدیریت وضعیت‌های غیبت و انضباطی پرسنل در شیفت جاری</p>
        </div>
        <div style="display:flex;align-items:center;gap:15px;">
            <span class="shift-badge">🕒 شیفت: {shift_name}</span>
            <a href="/module/supervisor" class="back-btn">⬅️ بازگشت</a>
        </div>
    </div>

    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-value" style="color:#3b82f6;">{present_count}</div>
            <div class="kpi-label">✅ حاضرین</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color:#ef4444;">{ghaibat_count}</div>
            <div class="kpi-label">🚫 غیبت</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color:#f59e0b;">{takhir_count}</div>
            <div class="kpi-label">⏰ تاخیر</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color:#ec4899;">{taajil_count}</div>
            <div class="kpi-label">🏃 تعجیل</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color:#8b5cf6;">{pas_count}</div>
            <div class="kpi-label">🎫 پاس ساعتی</div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="switchTab('register')">📝 ثبت مورد جدید</button>
        <button class="tab" onclick="switchTab('list')">📋 لیست ثبت شده‌ها</button>
    </div>

    <div id="tab-register" class="tab-content active">
        <div class="main-grid">
            <div class="form-panel">
                <div class="form-title">➕ ثبت وضعیت</div>
                <form id="ghaybat-form">
                    <input type="hidden" name="shift_id" value="{shift_id}">

                    <div class="form-group">
                        <label>🏥 بخش</label>
                        <select name="dept_id" id="dept-select" class="form-select" onchange="loadPersonnel()">
                            {dept_options}
                        </select>
                    </div>

                    <div class="form-group">
                        <label>👤 پرسنل</label>
                        <select name="person_id" id="person-select" class="form-select" disabled>
                            <option value="">ابتدا بخش را انتخاب کنید</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>🕒 شیفت جزئی (ریزشیفت)</label>
                        <select name="rizshift" id="rizshift-select" class="form-select">
                            {shift_options}
                        </select>
                    </div>

                    <div class="form-group">
                        <label>📌 وضعیت‌ها (حداقل یکی انتخاب شود)</label>
                        <div class="checkbox-group">
                            <label class="checkbox-item">
                                <input type="checkbox" name="ghaibat" value="1"> غیبت
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" name="takhir" value="1"> تاخیر
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" name="taajil" value="1"> تعجیل
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" name="pas" value="1"> پاس ساعتی
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>📝 توضیحات</label>
                        <input type="text" name="description" class="form-input" placeholder="توضیحات تکمیلی...">
                    </div>

                    <button type="submit" class="btn btn-primary" style="width:100%;" id="save-btn">
                        <span id="save-text">💾 ثبت نهایی</span>
                        <span id="save-loading" style="display:none;">⏳ ...</span>
                    </button>
                </form>
            </div>

            <div class="form-panel" style="height:fit-content;">
                <div class="form-title">💡 نکات مهم</div>
                <ul style="list-style:none;padding:0;font-size:13px;color:var(--gray);line-height:2;">
                    <li>✅ می‌توانید چند وضعیت را همزمان انتخاب کنید.</li>
                    <li>✅ هر پرسنل در هر شیفت فقط یک بار ثبت می‌شود.</li>
                    <li>✅ برای ویرایش، رکورد را حذف و دوباره ثبت کنید.</li>
                    <li>✅ شیفت جزئی (ریزشیفت) به‌صورت پیش‌فرض برابر با شیفت فعال تنظیم می‌شود.</li>
                </ul>
            </div>
        </div>
    </div>

    <div id="tab-list" class="tab-content">
        {_build_records_html(shift_id)}
    </div>
</div>

<script>
    var deptPersonnel = {dept_personnel_json};
    var defaultRizShiftId = "{default_rizshift_id or ''}";

    function showToast(msg, type) {{
        var c = document.getElementById('toast-container');
        var t = document.createElement('div');
        t.className = 'toast ' + (type||'info');
        t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>';
        c.appendChild(t);
        setTimeout(function(){{ if(t.parentElement){{ t.style.opacity='0'; setTimeout(function(){{t.remove()}},300); }} }}, 4000);
    }}

    function switchTab(tabName) {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        if (tabName === 'register') {{
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.getElementById('tab-register').classList.add('active');
        }} else {{
            document.querySelectorAll('.tab')[1].classList.add('active');
            document.getElementById('tab-list').classList.add('active');
        }}
    }}

    function loadPersonnel() {{
        var deptId = document.getElementById('dept-select').value;
        var personSelect = document.getElementById('person-select');
        var rizshiftSelect = document.getElementById('rizshift-select');
        
        personSelect.innerHTML = '<option value="">--- انتخاب پرسنل ---</option>';
        personSelect.disabled = true;
        
        // مقدار پیش‌فرض ریزشیفت = شیفت فعال
        if (rizshiftSelect) {{
            rizshiftSelect.value = defaultRizShiftId;
        }}
        
        if (!deptId || !deptPersonnel[deptId]) return;
        var personnel = deptPersonnel[deptId];
        if (personnel.length === 0) {{
            personSelect.innerHTML = '<option value="">پرسنلی در این بخش یافت نشد</option>';
            return;
        }}
        personnel.forEach(function(p) {{
            var option = document.createElement('option');
            option.value = p.ID_person;
            option.textContent = p.full_name;
            personSelect.appendChild(option);
        }});
        personSelect.disabled = false;
    }}

    document.getElementById('ghaybat-form').addEventListener('submit', function(e) {{
        e.preventDefault();
        var deptId = document.getElementById('dept-select').value;
        var personId = document.getElementById('person-select').value;
        if (!deptId) {{ showToast('⛔ بخش انتخاب نشده', 'error'); return; }}
        if (!personId) {{ showToast('⛔ پرسنل انتخاب نشده', 'error'); return; }}

        var anyChecked = Array.from(document.querySelectorAll('input[type="checkbox"]')).some(cb => cb.checked);
        if (!anyChecked) {{ showToast('⛔ حداقل یک وضعیت انتخاب کنید', 'error'); return; }}

        var formData = new FormData(this);
        document.getElementById('save-text').style.display = 'none';
        document.getElementById('save-loading').style.display = 'inline';
        document.getElementById('save-btn').disabled = true;

        fetch('/module/supervisor/ghaybat/save', {{
            method: 'POST',
            body: formData
        }})
        .then(r => r.json())
        .then(data => {{
            document.getElementById('save-text').style.display = 'inline';
            document.getElementById('save-loading').style.display = 'none';
            document.getElementById('save-btn').disabled = false;
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                setTimeout(function(){{ location.reload(); }}, 1200);
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }})
        .catch(function() {{
            document.getElementById('save-text').style.display = 'inline';
            document.getElementById('save-loading').style.display = 'none';
            document.getElementById('save-btn').disabled = false;
            showToast('⛔ خطا در ارتباط', 'error');
        }});
    }});

    function deleteItem(itemId) {{
        if (!confirm('آیا از حذف این مورد اطمینان دارید؟')) return;
        var formData = new FormData();
        formData.append('ghaibat_id', itemId);
        fetch('/module/supervisor/ghaybat/delete', {{
            method: 'POST',
            body: formData
        }})
        .then(r => r.json())
        .then(data => {{
            if (data.success) {{
                showToast('✅ ' + data.message, 'success');
                setTimeout(function(){{ location.reload(); }}, 800);
            }} else {{
                showToast('⛔ ' + data.message, 'error');
            }}
        }});
    }}
</script>
</body>
</html>'''
    return html


def _build_personnel_json(departments):
    data = {}
    for dept in departments:
        dept_id = dept['ID_nam_bakhsh']
        personnel = query("""
            SELECT p.ID_person, CONCAT(p.nam, ' ', p.famil) as full_name
            FROM tbl_person p
            JOIN tbl_sazema_person s ON p.ID_person = s.nam_person
            WHERE s.nam_bakhsh = %s AND p.isActiv = 1
            AND (s.payani_sazmandehi = 0 OR s.payani_sazmandehi IS NULL)
            ORDER BY p.famil, p.nam
        """, params=(dept_id,), fetch_all=True)
        data[str(dept_id)] = personnel if personnel else []
    return json.dumps(data, ensure_ascii=False)


def _build_records_html(shift_id):
    records = query("""
        SELECT g.ID_ghaibat, g.ghaibat, g.takhir_saati, g.taajil_khoroj, g.pas_saati,
               g.tozihat, g.rizshift, o.shift_code,
               CONCAT(p.nam, ' ', p.famil) as full_name, b.nam_bakhsh
        FROM tbl_ghaybat g
        JOIN tbl_person p ON g.nam_person = p.ID_person
        JOIN tbl_bakhsh b ON g.nam_bakhsh = b.ID_nam_bakhsh
        LEFT JOIN onvan_shift o ON g.rizshift = o.ID_onvan_shift
        WHERE g.nam_shift = %s
        ORDER BY g.ID_ghaibat DESC
    """, params=(shift_id,), fetch_all=True)

    if not records:
        return '<div class="empty-list"><div style="font-size:40px;">📭</div><p>هنوز موردی ثبت نشده است</p></div>'

    html = '<div class="list-panel">'
    for r in records:
        statuses = []
        if r['ghaibat'] == 1: statuses.append('<span class="status-badge badge-ghaibat">غیبت</span>')
        if r['takhir_saati'] == 1: statuses.append('<span class="status-badge badge-takhir">تاخیر</span>')
        if r['taajil_khoroj'] == 1: statuses.append('<span class="status-badge badge-taajil">تعجیل</span>')
        if r['pas_saati'] == 1: statuses.append('<span class="status-badge badge-pas">پاس ساعتی</span>')
        status_html = ' '.join(statuses)

        riz_code = r.get('shift_code', '')
        rizshift_display = f'🕒 شیفت جزئی: {riz_code}' if riz_code else ''

        html += f'''
        <div class="record-item">
            <div class="r-header">
                <span class="r-person">{r['full_name']}</span>
                <span class="r-dept">🏥 {r['nam_bakhsh']}</span>
            </div>
            <div class="r-statuses">{status_html}</div>
            {f'<div class="r-desc">📝 {r["tozihat"]}</div>' if r['tozihat'] else ''}
            {f'<div class="r-shift">{rizshift_display}</div>' if rizshift_display else ''}
            <div class="r-actions">
                <button class="btn btn-danger btn-sm" onclick="deleteItem({r['ID_ghaibat']})">🗑️ حذف</button>
            </div>
        </div>'''
    html += '</div>'
    return html


def save_ghaybat(user, form_data):
    _ensure_rizshift_int()

    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id', '')
    dept_id = form_data.get('dept_id', '')
    person_id = form_data.get('person_id', '')
    ghaibat = 1 if form_data.get('ghaibat') == '1' else 0
    takhir = 1 if form_data.get('takhir') == '1' else 0
    taajil = 1 if form_data.get('taajil') == '1' else 0
    pas = 1 if form_data.get('pas') == '1' else 0
    desc = form_data.get('description', '')
    rizshift = form_data.get('rizshift')
    if rizshift == '':
        rizshift = None
    else:
        try:
            rizshift = int(rizshift)
        except (ValueError, TypeError):
            rizshift = None

    if not dept_id or not person_id:
        return {'success': False, 'message': 'بخش و پرسنل الزامی است'}
    if not any([ghaibat, takhir, taajil, pas]):
        return {'success': False, 'message': 'حداقل یک وضعیت انتخاب شود'}

    existing = query(
        "SELECT ID_ghaibat FROM tbl_ghaybat WHERE nam_person = %s AND nam_shift = %s",
        params=(person_id, shift_id), fetch_one=True
    )
    if existing:
        return {'success': False, 'message': 'این پرسنل قبلاً در این شیفت ثبت شده است'}

    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()

    try:
        query("""
            INSERT INTO tbl_ghaybat
            (nam_person, nam_bakhsh, nam_shift, ghaibat, takhir_saati, taajil_khoroj,
             pas_saati, tozihat, rizshift, dat_sabt, zaman_sabt, UserID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (person_id, dept_id, shift_id, ghaibat, takhir, taajil, pas, desc, rizshift, today, now, user_id), commit=True)
        log_crud('save_ghaybat', user_id, key_value=None,
                 new_value=f"پرسنل:{person_id}, بخش:{dept_id}, ریزشیفت:{rizshift}")
        return {'success': True, 'message': 'رکورد با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


def delete_ghaybat(user, form_data):
    user_id = user.get('UserID', 0)
    ghaibat_id = form_data.get('ghaibat_id', '')
    if not ghaibat_id:
        return {'success': False, 'message': 'شناسه نامعتبر'}
    try:
        query("DELETE FROM tbl_ghaybat WHERE ID_ghaibat = %s", params=(ghaibat_id,), commit=True)
        log_crud('delete_ghaybat', user_id, key_value=ghaibat_id)
        return {'success': True, 'message': 'رکورد حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}
        