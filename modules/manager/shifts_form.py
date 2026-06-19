"""
modules/manager/shifts_form.py — نسخه چندبخشی (بدون ویرایش اجباری)
پشتیبانی از tbl_user_depts برای انتخاب بخش توسط کاربر
"""

import json
import logging
import secrets
from typing import Optional

import jdatetime
from models.database import query

logger = logging.getLogger(__name__)

PERSIAN_MONTHS = [
    'فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور',
    'مهر','آبان','آذر','دی','بهمن','اسفند'
]

WEEKDAY_SHORT = ['ش','ی','د','س','چ','پ','ج']

_shift_table_initialized = False


# ══════════════════════════════════════════════════════════════════
# توابع کمکی
# ══════════════════════════════════════════════════════════════════

def get_jalali_days(year: int, month: int) -> int:
    if month <= 6:  return 31
    if month <= 11: return 30
    try:
        jdatetime.date(year, 12, 30)
        return 30
    except ValueError:
        return 29


def _safe_int(value, field_name='مقدار') -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f'مقدار نامعتبر برای فیلد «{field_name}»')


def _require_fields(form_data, *fields) -> dict:
    result = {}
    for field in fields:
        val = form_data.get(field)
        if val is None or str(val).strip() == '':
            raise ValueError(f'فیلد اجباری «{field}» ارسال نشده است')
        result[field] = val
    return result


def _get_csrf_token() -> str:
    try:
        from flask import session as _s
        if '_csrf_token' not in _s:
            _s['_csrf_token'] = secrets.token_hex(32)
        return _s['_csrf_token']
    except Exception:
        return ''


def _jalali_weekday(year: int, month: int, day: int) -> int:
    try:
        return jdatetime.date(year, month, day).weekday()
    except Exception:
        return 0


# ══════════════════════════════════════════════════════════════════
# دریافت بخش‌های کاربر از tbl_user_depts
# ══════════════════════════════════════════════════════════════════

def get_user_departments(user_id: int) -> list:
    """لیست دیکشنری‌های {id, name} برای بخش‌های مجاز کاربر"""
    rows = query("""
        SELECT d.ID_nam_bakhsh, d.nam_bakhsh
        FROM tbl_user_depts ud
        JOIN tbl_bakhsh d ON ud.dep_id = d.ID_nam_bakhsh
        WHERE ud.user_id = %s
        ORDER BY d.nam_bakhsh
    """, (user_id,), fetch_all=True) or []
    return [{'id': r['ID_nam_bakhsh'], 'name': r['nam_bakhsh']} for r in rows]


# ══════════════════════════════════════════════════════════════════
# مقداردهی جدول
# ══════════════════════════════════════════════════════════════════

def init_shift_table() -> None:
    global _shift_table_initialized
    if _shift_table_initialized:
        return
    try:
        query("""
            CREATE TABLE IF NOT EXISTS tbl_personnel_shifts (
                ID           INT AUTO_INCREMENT PRIMARY KEY,
                ID_person    INT      NOT NULL,
                shift_date   INT      NOT NULL,
                ID_onvan_shift INT    NOT NULL,
                is_extra     TINYINT  NOT NULL DEFAULT 0,
                assigned_by  INT      DEFAULT NULL,
                zaman_sabt   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_person_date (ID_person, shift_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, commit=True)
        col = query("SHOW COLUMNS FROM tbl_personnel_shifts LIKE 'is_extra'", fetch_one=True)
        if not col:
            query("ALTER TABLE tbl_personnel_shifts ADD COLUMN is_extra TINYINT NOT NULL DEFAULT 0", commit=True)
        _shift_table_initialized = True
    except Exception:
        logger.exception('خطا در init_shift_table')
        raise


def _log_audit(dep_id, person_id, shift_date, action, old_shift, new_shift, is_extra, changed_by, note=None):
    try:
        query("""
            INSERT INTO tbl_shift_audit
            (dep_id, person_id, shift_date, action, old_shift, new_shift, is_extra, changed_by, note)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (dep_id, person_id, shift_date, action, old_shift, new_shift, is_extra, changed_by, note), commit=True)
    except Exception:
        logger.warning('خطا در ثبت audit log', exc_info=True)


# ══════════════════════════════════════════════════════════════════
# وضعیت تایید
# ══════════════════════════════════════════════════════════════════

def get_approval_status(dep_id: int, year: int, month: int) -> list:
    try:
        rows = query("""
            SELECT a.level_no, a.approved_by, a.approved_at, a.note,
                   u.FullName as approver_name,
                   ap.level_label
            FROM   tbl_shift_approvals a
            LEFT JOIN users u ON u.UserID = a.approved_by
            LEFT JOIN tbl_shift_approvers ap ON ap.dep_id = a.dep_id AND ap.level_no = a.level_no
            WHERE  a.dep_id=%s AND a.year=%s AND a.month=%s
            ORDER  BY a.level_no
        """, (dep_id, year, month), fetch_all=True) or []
        return rows
    except Exception:
        return []


def get_approvers_config(dep_id: int) -> list:
    try:
        rows = query("""
            SELECT a.level_no, a.level_label, a.user_id, u.FullName
            FROM   tbl_shift_approvers a
            LEFT JOIN users u ON u.UserID = a.user_id
            WHERE  a.dep_id=%s
            ORDER  BY a.level_no
        """, (dep_id,), fetch_all=True) or []
        return rows
    except Exception:
        return []


def approve_month(user: dict, form_data) -> dict:
    try:
        dep_id   = _safe_int(form_data.get('dep_id'),   'dep_id')
        year     = _safe_int(form_data.get('year'),     'year')
        month    = _safe_int(form_data.get('month'),    'month')
        level_no = _safe_int(form_data.get('level_no'), 'level_no')
        note     = (form_data.get('note') or '').strip() or None
        user_id  = user.get('UserID')

        approver = query(
            "SELECT 1 FROM tbl_shift_approvers WHERE dep_id=%s AND level_no=%s AND user_id=%s",
            (dep_id, level_no, user_id), fetch_one=True
        )
        if not approver:
            return {'success': False, 'message': 'شما مجاز به تایید این سطح نیستید'}

        if level_no > 1:
            prev = query(
                "SELECT 1 FROM tbl_shift_approvals WHERE dep_id=%s AND year=%s AND month=%s AND level_no=%s",
                (dep_id, year, month, level_no - 1), fetch_one=True
            )
            if not prev:
                return {'success': False, 'message': f'ابتدا باید سطح {level_no-1} تایید شود'}

        query("""
            INSERT INTO tbl_shift_approvals (dep_id, year, month, level_no, approved_by, note)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE approved_by=%s, approved_at=NOW(), note=%s
        """, (dep_id, year, month, level_no, user_id, note, user_id, note), commit=True)

        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در approve_month')
        return {'success': False, 'message': 'خطای داخلی سرور'}


def revoke_approval(user: dict, form_data) -> dict:
    try:
        dep_id   = _safe_int(form_data.get('dep_id'),   'dep_id')
        year     = _safe_int(form_data.get('year'),     'year')
        month    = _safe_int(form_data.get('month'),    'month')
        level_no = _safe_int(form_data.get('level_no'), 'level_no')
        user_id  = user.get('UserID')

        approver = query(
            "SELECT 1 FROM tbl_shift_approvers WHERE dep_id=%s AND level_no=%s AND user_id=%s",
            (dep_id, level_no, user_id), fetch_one=True
        )
        if not approver:
            return {'success': False, 'message': 'شما مجاز به لغو این سطح نیستید'}

        higher = query(
            "SELECT 1 FROM tbl_shift_approvals WHERE dep_id=%s AND year=%s AND month=%s AND level_no>%s",
            (dep_id, year, month, level_no), fetch_one=True
        )
        if higher:
            return {'success': False, 'message': 'ابتدا باید تاییدهای سطح بالاتر لغو شود'}

        query(
            "DELETE FROM tbl_shift_approvals WHERE dep_id=%s AND year=%s AND month=%s AND level_no=%s",
            (dep_id, year, month, level_no), commit=True
        )
        return {'success': True}
    except Exception:
        logger.exception('خطا در revoke_approval')
        return {'success': False, 'message': 'خطای داخلی سرور'}


# ══════════════════════════════════════════════════════════════════
# HTML اصلی — ویرایش (مسئول بخش)
# ══════════════════════════════════════════════════════════════════

def get_shifts_form(user: dict) -> str:
    user_id = user.get('UserID')
    init_shift_table()

    # دریافت بخش‌های مجاز کاربر
    user_depts = get_user_departments(user_id)
 
    if not user_depts:
        return ('<div style="padding:60px;text-align:center;color:#dc2626;">'
                '<h2>⛔ دسترسی محدود</h2>'
                '<p>شما به هیچ بخشی دسترسی ندارید.</p>'
                '<a href="/module/manager" style="display:inline-block;margin-top:25px;'
                'background:#0f766e;color:white;padding:12px 28px;border-radius:8px;'
                'text-decoration:none;font-weight:bold;">⬅️ بازگشت به داشبورد</a></div>') 

    # انتخاب بخش پیش‌فرض (اولین بخش) یا از session
    default_dep = user_depts[0]['id']
    try:
        from flask import session as fs
        if 'shift_dep_id' in fs and any(d['id'] == fs['shift_dep_id'] for d in user_depts):
            default_dep = fs['shift_dep_id']
    except Exception:
        pass

    dept_options = ''.join(
        f'<option value="{d["id"]}" {"selected" if d["id"] == default_dep else ""}>{d["name"]}</option>'
        for d in user_depts
    )
    dep_id = default_dep   # برای بار اول

    dept_info = query("SELECT nam_bakhsh FROM tbl_bakhsh WHERE ID_nam_bakhsh=%s", (dep_id,), fetch_one=True)
    dept_name = dept_info['nam_bakhsh'] if dept_info else 'نامشخص'

    shift_titles = query(
        "SELECT ID_onvan_shift, nam_shift, shift_code, color_code FROM onvan_shift ORDER BY ID_onvan_shift",
        fetch_all=True
    ) or []
    shift_json = json.dumps(shift_titles, ensure_ascii=False)

    approvers = get_approvers_config(dep_id)
    approvers_json = json.dumps(
        [{'level_no': a['level_no'], 'level_label': a['level_label'] or f'سطح {a["level_no"]}',
          'user_id': a['user_id'], 'FullName': a['FullName']} for a in approvers],
        ensure_ascii=False
    )

    csrf_token = _get_csrf_token()
    today = jdatetime.date.today()
    cy, cm = today.year, today.month

    year_opts = ''.join(
        f'<option value="{y}" {"selected" if y == cy else ""}>{y}</option>'
        for y in range(cy - 1, cy + 2)
    )
    month_opts = ''.join(
        f'<option value="{m}" {"selected" if m == cm else ""}>{PERSIAN_MONTHS[m-1]}</option>'
        for m in range(1, 13)
    )
    shift_sel_rows = ''.join(
        f'<option value="{s["ID_onvan_shift"]}">{s["shift_code"]}</option>'
        for s in shift_titles
    )

    return f'''<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="csrf-token" content="{csrf_token}">
<title>شیفت‌بندی – {dept_name}</title>
<style>
{_SHIFTS_CSS}
</style>
</head>
<body>
<div class="toast-box" id="toastBox"></div>

<div class="container">
<!-- ── Header ── -->
<div class="header">
    <div>
        <h2>🗓️ شیفت‌بندی — <span id="deptNameHeader">{dept_name}</span></h2>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
        <!-- انتخاب بخش -->
        <select id="deptSelector" class="no-print" onchange="onDeptChange()" style="padding:6px 10px;border-radius:6px;font-weight:bold;">
            {dept_options}
        </select>
        <button class="btn btn-purple no-print" onclick="window.print()">🖨️ چاپ</button>
        <a href="/module/manager" class="btn btn-ghost no-print">⬅️ بازگشت</a>
    </div>
</div>

<!-- ── نوار تایید ── -->
<div class="approval-bar no-print" id="approvalBar">
    <span class="bar-title">📋 وضعیت تایید:</span>
    <span id="approvalSteps" style="display:flex;gap:8px;flex-wrap:wrap;">
        <span style="color:#94a3b8;font-size:13px;">در حال بارگذاری...</span>
    </span>
</div>

<!-- ── Controls ── -->
<div class="controls no-print">
    <label>سال:</label>
    <select id="yearSel" onchange="loadGrid()">{year_opts}</select>
    <label>ماه:</label>
    <select id="monthSel" onchange="loadGrid()">{month_opts}</select>
    <span id="loadTxt" style="display:none;color:var(--primary);font-weight:bold;">⏳...</span>
</div>

<!-- عنوان چاپ -->
<div class="print-only print-title" id="printTitle"></div>

<!-- ── Grid ── -->
<div class="table-wrapper">
    <table class="shift-table">
        <thead id="gridHead"></thead>
        <tbody id="gridBody"></tbody>
    </table>
</div>

<!-- ── فوتر چاپ ── -->
<div class="print-footer print-only" id="printFooter" style="display:none;"></div>

<!-- Modal ثبت گروهی -->
<div id="bulkModal" class="modal no-print">
    <div class="modal-box">
        <h3>⚡ ثبت گروهی</h3>
        <p id="bulkName" style="color:var(--primary);font-weight:bold;margin-top:4px;"></p>
        <input type="hidden" id="bulkPid">
        <label>شیفت:</label>
        <select id="bulkShift">
            <option value="">-- انتخاب --</option>
            {shift_sel_rows}
            <option value="DELETE">🗑️ پاک کردن بازه</option>
        </select>
        <div style="display:flex;gap:12px;">
            <div style="flex:1;"><label>از روز:</label><select id="bulkStart"></select></div>
            <div style="flex:1;"><label>تا روز:</label><select id="bulkEnd"></select></div>
        </div>
        <div class="modal-actions">
            <button class="btn btn-green" onclick="submitBulk()" style="flex:1;">✅ ثبت</button>
            <button class="btn btn-gray" onclick="closeModal('bulkModal')" style="flex:1;">انصراف</button>
        </div>
    </div>
</div>

<!-- Modal تایید -->
<div id="approveModal" class="modal no-print">
    <div class="modal-box">
        <h3 id="approveTitle">✅ تایید شیفت‌بندی</h3>
        <input type="hidden" id="appLevelNo">
        <input type="hidden" id="appAction">
        <label>یادداشت (اختیاری):</label>
        <textarea id="appNote" rows="3" placeholder="توضیحات..."></textarea>
        <div class="modal-actions">
            <button class="btn btn-green" id="appSubmitBtn" onclick="submitApproval()" style="flex:1;">✅ تایید</button>
            <button class="btn btn-gray" onclick="closeModal('approveModal')" style="flex:1;">انصراف</button>
        </div>
    </div>
</div>

</div><!-- /container -->

<script>
const SHIFTS    = {shift_json};
const MY_ID     = {user_id};
const IS_READONLY = false;
// بخش‌های کاربر و بخش جاری
const USER_DEPTS = {json.dumps(user_depts, ensure_ascii=False)};
let currentDepId = {dep_id};

{_SHIFTS_JS_COMMON}
{_SHIFTS_JS_EDIT}
</script>
</body>
</html>'''


# ══════════════════════════════════════════════════════════════════
# HTML فقط‌خواندنی (برای مدیران اجرایی) - با انتخاب بخش
# ══════════════════════════════════════════════════════════════════

def get_shifts_readonly(dep_id: int, year: int, month: int, user_depts: list = None) -> str:
    """
    صفحه‌ای که فقط برنامه را نمایش می‌دهد — بدون هیچ امکان ویرایشی.
    اگر user_depts داده شود، انتخاب‌گر بخش نمایش داده می‌شود.
    """
    dept_info = query("SELECT nam_bakhsh FROM tbl_bakhsh WHERE ID_nam_bakhsh=%s", (dep_id,), fetch_one=True)
    dept_name = dept_info['nam_bakhsh'] if dept_info else 'نامشخص'

    shift_titles = query(
        "SELECT ID_onvan_shift, nam_shift, shift_code, color_code FROM onvan_shift ORDER BY ID_onvan_shift",
        fetch_all=True
    ) or []
    shift_json = json.dumps(shift_titles, ensure_ascii=False)

    approvers = get_approvers_config(dep_id)
    approvers_json = json.dumps(
        [{'level_no': a['level_no'], 'level_label': a['level_label'] or f'سطح {a["level_no"]}',
          'user_id': a['user_id'], 'FullName': a['FullName']} for a in approvers],
        ensure_ascii=False
    )

    month_name = PERSIAN_MONTHS[month - 1] if 1 <= month <= 12 else str(month)

    # انتخاب‌گر بخش (اگر لیست داده شود)
    dept_selector_html = ''
    if user_depts and len(user_depts) > 1:
        opts = ''.join(
            f'<option value="{d["id"]}" {"selected" if d["id"] == dep_id else ""}>{d["name"]}</option>'
            for d in user_depts
        )
        dept_selector_html = f'''
        <select id="deptSelector" onchange="onDeptChange()" style="padding:6px 10px;border-radius:6px;font-weight:bold;">
            {opts}
        </select>
        '''
    user_depts_json = json.dumps(user_depts if user_depts else [], ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>برنامه شیفت – {dept_name} – {year} {month_name}</title>
<style>
{_SHIFTS_CSS}
/* حالت فقط‌خواندنی: مخفی کردن همه کنترل‌های ویرایش */
.no-print-ro, .inline-add, .btn-plus, .extra-sel, .rm-btn, .action-icon {{ display:none!important; }}
.shift-select {{ pointer-events:none; appearance:none; background:transparent;
  border:none; font-weight:bold; text-align:center; font-size:11px; cursor:default; }}
</style>
</head>
<body>
<div class="toast-box" id="toastBox"></div>
<div class="container">

<div class="header">
    <div>
        <h2>📋 برنامه شیفت — <span id="deptNameHeader">{dept_name}</span></h2>
        <p style="font-size:12px;opacity:.85;margin-top:3px;">{year} — {month_name} | حالت فقط‌خواندنی</p>
    </div>
    <div style="display:flex;gap:8px;align-items:center;">
        {dept_selector_html}
        <button class="btn btn-purple no-print" onclick="window.print()">🖨️ چاپ</button>
        <button class="btn btn-ghost no-print" onclick="window.close()">✕ بستن</button>
    </div>
</div>

<!-- نوار تایید -->
<div class="approval-bar no-print" id="approvalBar">
    <span class="bar-title">📋 وضعیت تایید:</span>
    <span id="approvalSteps">در حال بارگذاری...</span>
</div>

<!-- عنوان چاپ -->
<div class="print-only print-title">برنامه شیفت ماهیانه — {dept_name} — {year} {month_name}</div>

<div class="table-wrapper">
    <table class="shift-table">
        <thead id="gridHead"></thead>
        <tbody id="gridBody"></tbody>
    </table>
</div>

<!-- فوتر چاپ -->
<div class="print-footer print-only" id="printFooter" style="display:none;"></div>

</div>

<script>
const SHIFTS    = {shift_json};
const MY_ID     = 0;
const IS_READONLY = true;
const FIXED_YEAR  = {year};
const FIXED_MONTH = {month};
const USER_DEPTS  = {user_depts_json};
let currentDepId  = {dep_id};

{_SHIFTS_JS_COMMON}
{_SHIFTS_JS_READONLY}
</script>
</body>
</html>'''


# ══════════════════════════════════════════════════════════════════
# CSS مشترک
# ══════════════════════════════════════════════════════════════════

_SHIFTS_CSS = """
:root{--primary:#0f766e;--success:#10b981;--danger:#ef4444;--warning:#f59e0b;
  --border:#cbd5e1;--bg:#f8fafc;--text:#1e293b;--radius:8px;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:Tahoma,'Segoe UI',sans-serif;direction:rtl;}

.container{padding:14px;max-width:100%;}
.header{background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;
  padding:16px 20px;border-radius:12px;
  display:flex;justify-content:space-between;align-items:center;
  margin-bottom:12px;gap:10px;flex-wrap:wrap;}
.header h2{font-size:15px;}

/* نوار تایید */
.approval-bar{background:white;border:1px solid var(--border);border-radius:var(--radius);
  padding:12px 16px;margin-bottom:12px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;}
.approval-bar .bar-title{font-weight:bold;font-size:13px;margin-left:8px;color:#374151;flex-shrink:0;}
.ap-step{display:flex;align-items:center;gap:7px;padding:6px 12px;border-radius:20px;
  font-size:12px;font-weight:600;border:2px solid;cursor:default;transition:.2s;}
.ap-step.done{background:#d1fae5;color:#065f46;border-color:#6ee7b7;}
.ap-step.pending{background:#f1f5f9;color:#94a3b8;border-color:#e2e8f0;}
.ap-step.can-approve{background:#eff6ff;color:#1d4ed8;border-color:#93c5fd;cursor:pointer;animation:pulse 2s infinite;}
.ap-step.can-revoke{background:#fef3c7;color:#92400e;border-color:#fcd34d;cursor:pointer;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(59,130,246,.3);}50%{box-shadow:0 0 0 6px rgba(59,130,246,0);}}

.controls{background:white;padding:10px 14px;border-radius:var(--radius);
  display:flex;gap:10px;align-items:center;margin-bottom:10px;
  border:1px solid var(--border);flex-wrap:wrap;}
.controls label{font-weight:bold;font-size:13px;white-space:nowrap;}
.controls select{padding:6px 10px;border:1px solid var(--border);border-radius:6px;font-size:13px;min-width:90px;}

/* دکمه‌ها */
.btn{padding:7px 14px;border-radius:var(--radius);border:none;cursor:pointer;
  font-weight:bold;color:white;font-size:13px;transition:filter .15s;display:inline-flex;align-items:center;gap:5px;}
.btn:hover{filter:brightness(.9);}
.btn-blue{background:#3b82f6;} .btn-green{background:var(--success);}
.btn-gray{background:#64748b;} .btn-ghost{background:rgba(255,255,255,.18);color:white;border:1px solid rgba(255,255,255,.4);}
.btn-purple{background:#7c3aed;}

/* جدول */
.table-wrapper{overflow-x:auto;background:white;border:1px solid var(--border);
  border-radius:var(--radius);max-height:68vh;}
.shift-table{width:100%;border-collapse:collapse;font-size:12px;}
.shift-table th,.shift-table td{border:1px solid var(--border);padding:4px 3px;text-align:center;min-width:54px;vertical-align:top;}
.shift-table th{background:#f1f5f9;position:sticky;top:0;z-index:2;padding:6px 3px;white-space:nowrap;}
.shift-table th .day-num{font-size:13px;font-weight:bold;line-height:1.2;}
.shift-table th .day-wd{font-size:10px;color:#64748b;font-weight:normal;}
.shift-table th.friday .day-num{color:#dc2626;} .shift-table th.friday .day-wd{color:#fca5a5;}
.shift-table th.thursday .day-num{color:#9333ea;}
.shift-table td:first-child{position:sticky;right:0;background:#f8fafc;font-weight:bold;
  text-align:right;padding-right:10px;min-width:175px;z-index:1;border-left:2px solid var(--border);white-space:nowrap;}

.cell-wrap{display:flex;flex-direction:column;align-items:stretch;gap:3px;width:100%;}
.shift-select{width:100%;height:26px;border:1px solid #e2e8f0;border-radius:4px;
  background:#fff;text-align:center;font-weight:bold;cursor:pointer;font-size:11px;}
.extras-box{display:flex;flex-direction:column;gap:2px;}
.extra-badge{background:#be185d;color:white;padding:2px 5px;border-radius:4px;font-size:10px;
  font-weight:bold;display:flex;align-items:center;justify-content:space-between;gap:3px;}
.rm-btn{cursor:pointer;color:#fda4af;font-size:13px;line-height:1;}
.rm-btn:hover{color:#fff;}
.btn-plus{background:#f1f5f9;border:1px dashed #94a3b8;border-radius:4px;
  font-size:11px;cursor:pointer;padding:1px 6px;width:100%;font-weight:bold;color:#475569;}
.btn-plus:hover{background:#e2e8f0;color:var(--primary);}
.extra-sel{width:100%;font-size:10px;height:22px;border:1px solid #14b8a6;border-radius:4px;background:#f0fdfa;}

/* Toast */
.toast-box{position:fixed;top:14px;left:50%;transform:translateX(-50%);z-index:10000;
  display:flex;flex-direction:column;gap:8px;min-width:260px;}
.toast{padding:10px 18px;border-radius:10px;color:white;font-weight:600;font-size:13px;
  box-shadow:0 6px 18px rgba(0,0,0,.18);animation:tsd .25s ease;}
.toast.s{background:linear-gradient(135deg,#059669,#10b981);}
.toast.e{background:linear-gradient(135deg,#dc2626,#ef4444);}
@keyframes tsd{from{opacity:0;transform:translateY(-12px);}to{opacity:1;transform:translateY(0);}}

/* Modal */
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:200;align-items:center;justify-content:center;}
.modal.open{display:flex;}
.modal-box{background:white;padding:22px;border-radius:14px;width:95%;max-width:440px;box-shadow:0 20px 50px rgba(0,0,0,.2);}
.modal-box h3{margin-bottom:4px;}
.modal-box label{display:block;margin-top:12px;margin-bottom:4px;font-weight:bold;font-size:13px;}
.modal-box select,.modal-box textarea{width:100%;padding:9px;border:1px solid var(--border);border-radius:6px;font-size:13px;}
.modal-box textarea{resize:vertical;font-family:inherit;}
.modal-actions{margin-top:18px;display:flex;gap:10px;}

/* ── چاپ — عناصر فقط در چاپ ── */
.print-only{display:none;}
.print-title{font-size:14px;font-weight:bold;text-align:center;padding:6px 0 8px;color:#0f766e;border-bottom:2px solid #0f766e;margin-bottom:8px;}

/* فوتر چاپ */
.print-footer{margin-top:14px;border-top:3px solid #0f766e;padding-top:12px;page-break-inside:avoid;}
.print-footer-heading{font-size:13px;font-weight:bold;color:#0f766e;margin-bottom:10px;text-align:center;}
.pf-grid{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;}
.pf-cell{flex:1;min-width:120px;max-width:180px;border:1px solid #e2e8f0;border-radius:8px;padding:10px;text-align:center;}
.pf-cell.signed{background:#f0fdf4;border-color:#6ee7b7;}
.pf-cell.unsigned{background:#f8fafc;}
.pf-level{font-size:11px;color:#64748b;margin-bottom:4px;font-weight:600;}
.pf-name{font-size:13px;font-weight:bold;color:#0f172a;}
.pf-date{font-size:11px;color:#0f766e;margin-top:3px;direction:ltr;}
.pf-sig{margin-top:14px;border-top:1px dashed #cbd5e1;padding-top:8px;font-size:11px;color:#94a3b8;}

@media print {
  @page { size: A4 landscape; margin: 8mm 6mm; }

  .no-print { display: none !important; }
  .print-only { display: block !important; }

  body { background: white !important; font-size: 10px; }
  .container { padding: 0 !important; }

  .table-wrapper {
    max-height: none !important;
    border: none !important;
    overflow: visible !important;
  }
  .shift-table {
    font-size: 8.5px !important;
    width: 100% !important;
    table-layout: fixed;
  }
  .shift-table th,
  .shift-table td {
    min-width: 0 !important;
    padding: 2px 1px !important;
    word-break: break-all;
  }

    .shift-table th {
        position: static !important;
    }
    .shift-table td:first-child {
        position: static !important;
    }

  
  /* ستون نام پرسنل عریض‌تر */
  .shift-table td:first-child,
  .shift-table th:first-child {
    min-width: 90px !important;
    width: 90px !important;
    font-size: 8px !important;
    white-space: normal !important;
  }
  /* ستون‌های روز باریک */
  .shift-table th:not(:first-child),
  .shift-table td:not(:first-child) {
    width: calc((100% - 90px) / 31) !important;
  }
  .shift-select {
    display: none !important;
  }
  /* نمایش شیفت با رنگ به جای dropdown */
  .cell-print-val {
    display: block !important;
    font-size: 8px;
    font-weight: bold;
    border-radius: 2px;
    padding: 1px 2px;
    text-align: center;
  }
  .inline-add, .btn-plus, .extra-sel, .rm-btn, .action-icon { display: none !important; }
  .extra-badge { font-size: 7px !important; padding: 1px 2px !important; }

  /* صفحه‌بندی */
  thead { display: table-header-group; }
  tfoot { display: table-footer-group; }
  tr { page-break-inside: avoid; }

  /* فوتر چاپ */
  #printFooter { display: block !important; }
  .print-footer { page-break-inside: avoid; }
    
  
}
"""


# ══════════════════════════════════════════════════════════════════
# JavaScript مشترک (با اضافه شدن مدیریت بخش)
# ══════════════════════════════════════════════════════════════════

_SHIFTS_JS_COMMON = r"""
const shiftMap = new Map(SHIFTS.map(s => [String(s.ID_onvan_shift), s]));
const getColor = id => shiftMap.get(String(id))?.color_code ?? '#fff';
const getCode  = id => shiftMap.get(String(id))?.shift_code  ?? '?';
const WD_SHORT = ['ش','ی','د','س','چ','پ','ج'];
const PM = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'];

function _shamsiWeekday(jy, jm, jd) {
    const [gy, gm, gd] = _j2g(jy, jm, jd);
    const jsDay = new Date(gy, gm - 1, gd).getDay();
    return [1,2,3,4,5,6,0][jsDay];
}
function _j2g(jy, jm, jd) {
    let jy2=jy-979, jm2=jm-1, jd2=jd-1;
    let n=365*jy2+(~~(jy2/33))*8+~~(((jy2%33)+3)/4);
    for(let i=0;i<jm2;i++) n+=[31,31,31,31,31,31,30,30,30,30,30,29][i];
    n+=jd2;
    let g=n+79, gy=1600+400*~~(g/146097); g%=146097;
    let leap=true;
    if(g>=36525){g--;gy+=100*~~(g/36524);g%=36524;if(g>=365)g++;else leap=false;}
    gy+=4*~~(g/1461); g%=1461;
    if(g>=366){leap=false;g--;gy+=~~(g/365);g%=365;}
    const dm=[31,leap?29:28,31,30,31,30,31,31,30,31,30,31];
    let gm=0,gd_=0;
    for(let i=0;i<12;i++){if(g<dm[i]){gm=i+1;gd_=g+1;break;}g-=dm[i];}
    return [gy,gm,gd_];
}

function csrf() { return document.querySelector('meta[name="csrf-token"]')?.content ?? ''; }

async function api(url, data) {
    const p = new URLSearchParams(data), t = csrf();
    if (t && !p.has('csrf_token')) p.append('csrf_token', t);
    const r = await fetch(url, {method:'POST', body:p.toString(), credentials:'include',
        headers:{'Content-Type':'application/x-www-form-urlencoded','X-CSRFToken':t,'X-Requested-With':'XMLHttpRequest'}});
    if (!r.ok) throw new Error('خطای سرور ' + r.status);
    const d = await r.json();
    if (!d.success) throw new Error(d.message ?? 'خطای ناشناخته');
    return d;
}

function toast(msg, type='s') {
    const b = document.getElementById('toastBox');
    const e = Object.assign(document.createElement('div'), {className:`toast ${type}`, textContent:msg});
    b.appendChild(e); setTimeout(() => e.remove(), 4000);
}
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

function setLoading(s) { document.getElementById('loadTxt') && (document.getElementById('loadTxt').style.display = s ? 'inline' : 'none'); }
function populateDays(id, max) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = Array.from({length:max}, (_,i) => `<option value="${i+1}">${i+1}</option>`).join('');
}
function buildShiftOpts(sel='') {
    return SHIFTS.map(s => `<option value="${s.ID_onvan_shift}" ${String(s.ID_onvan_shift)===String(sel)?'selected':''}>${s.shift_code}</option>`).join('');
}

/* تغییر بخش */

function onDeptChange() {
    const sel = document.getElementById('deptSelector');
    if (!sel) return;
    currentDepId = parseInt(sel.value);

    fetch('/module/manager/shifts/set_dep', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrf() },
        body: new URLSearchParams({ dep_id: currentDepId, csrf_token: csrf() })
    }).catch(() => {});

    const name = sel.options[sel.selectedIndex].text;
    document.getElementById('deptNameHeader').textContent = name;

    // به‌روزرسانی فوری نوار تأیید و سپس شبکه
    const year  = +document.getElementById('yearSel').value;
    const month = +document.getElementById('monthSel').value;
    loadApprovalBar(year, month).then(() => loadGrid());
}

/* نوار تایید */
async function loadApprovalBar(year, month) {
    try {
        const r = await fetch(`/module/manager/shifts/approval_status?dep_id=${currentDepId}&year=${year}&month=${month}`);
        const d = await r.json();
        if (!d.success) return;
        const approvals = d.approvals || [];
        const done = new Set(approvals.map(a => a.level_no));
        const approvers = await fetch(`/module/manager/shifts/approvers?dep_id=${currentDepId}`).then(r=>r.json()).then(d=>d.approvers||[]);
        const myLevels = new Set(approvers.filter(a => a.user_id === MY_ID).map(a => a.level_no));
        const stepsEl = document.getElementById('approvalSteps');
        if (!approvers.length) {
            stepsEl.innerHTML = '<span style="color:#94a3b8;font-size:12px;">تاییدکننده‌ای تعریف نشده</span>';
            return;
        }
        stepsEl.innerHTML = approvers.map(a => {
            const isDone   = done.has(a.level_no);
            const canAct   = myLevels.has(a.level_no);
            const prevDone = a.level_no === 1 || done.has(a.level_no - 1);
            const info     = isDone ? (approvals.find(x => x.level_no === a.level_no)) : null;
            let cls = 'pending', title = '';
            if (isDone) {
                cls   = canAct && !IS_READONLY ? 'can-revoke' : 'done';
                title = info ? `تایید شده توسط ${info.approver_name} در ${info.approved_at?.slice(0,10)}` : 'تایید شده';
            } else if (canAct && prevDone && !IS_READONLY) {
                cls = 'can-approve';
            }
            const clickable = !IS_READONLY && canAct && (isDone || prevDone);
            const action = isDone ? 'revoke' : 'approve';
            const approverInfo = info ? ` — ${info.approver_name}` : '';
            return `<span class="ap-step ${cls}"
                ${clickable ? `onclick="openApproveModal(${a.level_no},'${action}')"` : ''}
                title="${title}">
                ${isDone ? '✅' : '⬜'} ${a.level_label || 'سطح ' + a.level_no}${approverInfo}
                ${isDone && canAct && !IS_READONLY ? ' <small>(لغو)</small>' : ''}
            </span>`;
        }).join('');

        buildPrintFooter(approvals, year, month, approvers);
    } catch(e) {
        console.warn('approval bar error', e);
    }
}

function buildPrintFooter(approvals, year, month, approvers) {
    const footer = document.getElementById('printFooter');
    if (!footer) return;
    const mn = PM[month - 1] || month;
    let cells = '';
    if (approvers && approvers.length) {
        approvers.forEach(a => {
            const ap   = approvals.find(x => x.level_no === a.level_no);
            const lbl  = a.level_label || ('سطح ' + a.level_no);
            const name = ap ? ap.approver_name : a.FullName;
            const dt   = ap && ap.approved_at ? ap.approved_at.slice(0, 16) : '';
            const cls  = ap ? 'signed' : 'unsigned';
            cells += `
              <div class="pf-cell ${cls}">
                <div class="pf-level">${lbl}</div>
                <div class="pf-name">${name}</div>
                ${dt ? `<div class="pf-date">🕐 ${dt}</div>` : ''}
                <div class="pf-sig">${ap ? '✅ تایید شده' : 'مهر و امضا'}</div>
              </div>`;
        });
    } else {
        cells = '<div class="pf-cell unsigned"><div class="pf-level">تاییدکننده‌ای تعریف نشده</div></div>';
    }
    const deptTitle = document.querySelector('.header h2')?.textContent || '';
    footer.innerHTML = `
        <div class="print-footer-heading">✅ وضعیت تایید — ${deptTitle} — ${year} ${mn}</div>
        <div class="pf-grid">${cells}</div>`;
    footer.style.display = 'block';
}

/* Approval modal (فقط در حالت ویرایش) */
function openApproveModal(levelNo, action) {
    if (IS_READONLY) return;
    document.getElementById('appLevelNo').value = levelNo;
    document.getElementById('appAction').value  = action;
    document.getElementById('appNote').value    = '';
    const approvers = async () => {
        const r = await fetch(`/module/manager/shifts/approvers?dep_id=${currentDepId}`);
        return (await r.json()).approvers || [];
    };
    approvers().then(list => {
        const a = list.find(x => x.level_no === levelNo);
        const lbl = a ? (a.level_label || 'سطح ' + levelNo) : ('سطح ' + levelNo);
        document.getElementById('approveTitle').textContent = action === 'approve' ? `✅ تایید — ${lbl}` : `↩️ لغو تایید — ${lbl}`;
        document.getElementById('appSubmitBtn').textContent = action === 'approve' ? '✅ تایید' : '↩️ لغو تایید';
    });
    openModal('approveModal');
}

async function submitApproval() {
    const levelNo = document.getElementById('appLevelNo').value;
    const action  = document.getElementById('appAction').value;
    const note    = document.getElementById('appNote').value;
    const year    = +(document.getElementById('yearSel')?.value || FIXED_YEAR);
    const month   = +(document.getElementById('monthSel')?.value || FIXED_MONTH);
    const url     = action === 'approve' ? '/module/manager/shifts/approve' : '/module/manager/shifts/revoke';
    try {
        await api(url, {dep_id:currentDepId, year, month, level_no:levelNo, note});
        closeModal('approveModal');
        loadApprovalBar(year, month);
        toast(action === 'approve' ? '✅ تایید ثبت شد' : '↩️ تایید لغو شد');
    } catch(e) { toast('⛔ ' + e.message, 'e'); }
}
"""


# ══════════════════════════════════════════════════════════════════
# JavaScript حالت ویرایش (مسئول بخش) — به‌روزرسانی با currentDepId
# ══════════════════════════════════════════════════════════════════

_SHIFTS_JS_EDIT = r"""
document.querySelectorAll('.modal').forEach(m => m.addEventListener('click', e => {
    if (e.target === m) closeModal(m.id);
}));

async function loadGrid() {
    setLoading(true);
    const year  = +document.getElementById('yearSel').value;
    const month = +document.getElementById('monthSel').value;
    try {
        const [pd, ad] = await Promise.all([
            fetch(`/module/manager/shifts/personnel?dep_id=${currentDepId}`).then(r => r.json()),
            fetch(`/module/manager/shifts/assignments?dep_id=${currentDepId}&year=${year}&month=${month}`).then(r => r.json())
        ]);
        if (!pd.success) throw new Error(pd.message);
        if (!ad.success) throw new Error(ad.message);

        const personnel = pd.personnel ?? [];
        const assigns   = ad.assignments ?? {};
        const extras    = ad.extras ?? {};
        const days      = ad.month_days ?? 30;

        populateDays('bulkStart', days);
        populateDays('bulkEnd', days);

        const deptName = document.getElementById('deptSelector')?.selectedOptions[0]?.text || '';
        const ptEl = document.getElementById('printTitle');
        if (ptEl) ptEl.textContent = `برنامه شیفت ماهیانه — ${deptName} — ${year} ${PM[month-1]||month}`;

        /* هدر */
        const hCells = Array.from({length:days}, (_, i) => {
            const d  = i + 1;
            const wd = _shamsiWeekday(year, month, d);
            const cls = wd===6?'friday':wd===5?'thursday':'';
            return `<th class="${cls}"><div class="day-num">${d}</div><div class="day-wd">${WD_SHORT[wd]}</div></th>`;
        }).join('');
        document.getElementById('gridHead').innerHTML = `<tr><th>پرسنل / روز</th>${hCells}</tr>`;

        /* ردیف‌ها */
        const rows = personnel.map(p => {
            const pid  = p.ID_person;
            const name = `${p.nam} ${p.famil}`;
            const cells = Array.from({length:days}, (_, i) => {
                const d    = i + 1;
                const date = `${year}${String(month).padStart(2,'0')}${String(d).padStart(2,'0')}`;
                const key  = `${pid}_${date}`;
                const mainId = assigns[key] ?? '';
                const dayEx  = extras[key]  ?? [];
                const bg     = mainId ? getColor(mainId) : (_shamsiWeekday(year,month,d)===6?'#fff5f5':'#fff');
                const exBadges = dayEx.map(ex =>
                    `<div class="extra-badge"><span>${getCode(ex)}</span>
                     <span class="rm-btn" onclick="removeExtra(${pid},'${date}',${ex},this)">×</span></div>`
                ).join('');
                return `<td style="background:${bg};" id="td_${key}">
                    <div class="cell-wrap">
                        <select class="shift-select" data-pid="${pid}" data-date="${date}" onchange="saveMain(this)">
                            <option value="">-</option>${buildShiftOpts(mainId)}
                        </select>
                        ${mainId ? `<span class="cell-print-val" style="background:${getColor(mainId)};color:#fff;display:none;">${getCode(mainId)}</span>` : `<span class="cell-print-val" style="display:none;">—</span>`}
                        <div class="extras-box" id="ex_${key}">${exBadges}</div>
                        <div class="inline-add">
                            <button class="btn-plus" id="bp_${key}" onclick="toggleAddEx('${key}')">＋</button>
                            <select class="extra-sel" id="es_${key}" style="display:none;"
                                onchange="saveExtra(${pid},'${date}',this)">
                                <option value="">+ انتخاب</option>${buildShiftOpts()}
                            </select>
                        </div>
                    </div>
                </td>`;
            }).join('');
            return `<tr><td>👤 ${name}
                <span class="action-icon" style="cursor:pointer;background:#e0f2fe;border-radius:4px;padding:1px 5px;font-size:12px;margin-right:6px;"
                      onclick="openBulkModal(${pid},'${name}')" title="ثبت گروهی">⚡</span>
            </td>${cells}</tr>`;
        }).join('');
        document.getElementById('gridBody').innerHTML = rows;

        loadApprovalBar(year, month);
    } catch(e) {
        toast('⛔ ' + e.message, 'e');
    } finally { setLoading(false); }
}

async function saveMain(sel) {
    const pid = sel.dataset.pid, date = sel.dataset.date, shiftId = sel.value;
    const td  = sel.closest('td');
    try {
        await api('/module/manager/shifts/save', {person_id:pid, shift_date:date, shift_id:shiftId, dep_id:currentDepId});
        td.style.background = shiftId ? getColor(shiftId) : '#fff';
        toast('✔️ ذخیره شد');
    } catch(e) { toast('⛔ ' + e.message, 'e'); loadGrid(); }
}

function toggleAddEx(key) {
    document.getElementById(`bp_${key}`).style.display = 'none';
    const s = document.getElementById(`es_${key}`);
    s.style.display = 'block'; s.focus();
}
async function saveExtra(pid, date, sel) {
    const shiftId = sel.value, key = `${pid}_${date}`;
    sel.style.display = 'none';
    document.getElementById(`bp_${key}`).style.display = 'block';
    if (!shiftId) return;
    try {
        await api('/module/manager/shifts/extra', {person_id:pid, shift_date:date, shift_id:shiftId, dep_id:currentDepId});
        const badge = document.createElement('div');
        badge.className = 'extra-badge';
        badge.innerHTML = `<span>${getCode(shiftId)}</span><span class="rm-btn" onclick="removeExtra(${pid},'${date}',${shiftId},this)">×</span>`;
        document.getElementById(`ex_${key}`).appendChild(badge);
        toast('➕ شیفت اضافی ثبت شد');
    } catch(e) { toast('⛔ ' + e.message, 'e'); }
    finally { sel.value = ''; }
}
async function removeExtra(pid, date, shiftId, el) {
    event.stopPropagation();
    if (!confirm('حذف شود؟')) return;
    try {
        await api('/module/manager/shifts/extra/delete', {person_id:pid, shift_date:date, shift_id:shiftId, dep_id:currentDepId});
        el.closest('.extra-badge').remove();
        toast('🗑️ حذف شد');
    } catch(e) { toast('⛔ ' + e.message, 'e'); }
}

function openBulkModal(pid, name) {
    document.getElementById('bulkPid').value   = pid;
    document.getElementById('bulkName').textContent = name;
    document.getElementById('bulkShift').value = '';
    openModal('bulkModal');
}
async function submitBulk() {
    const shiftId = document.getElementById('bulkShift').value;
    const start   = +document.getElementById('bulkStart').value;
    const end     = +document.getElementById('bulkEnd').value;
    if (!shiftId) { toast('⚠️ شیفت انتخاب کنید', 'e'); return; }
    if (start > end) { toast('⚠️ روز شروع باید کمتر باشد', 'e'); return; }
    try {
        await api('/module/manager/shifts/bulk_save', {
            person_id: document.getElementById('bulkPid').value,
            shift_id: shiftId, start_day: start, end_day: end,
            year: document.getElementById('yearSel').value,
            month: document.getElementById('monthSel').value,
            dep_id: currentDepId
        });
        closeModal('bulkModal');
        await loadGrid();
        toast('✅ ثبت گروهی انجام شد');
    } catch(e) { toast('⛔ ' + e.message, 'e'); }
}

document.addEventListener('DOMContentLoaded', loadGrid);
"""


# ══════════════════════════════════════════════════════════════════
# JavaScript حالت فقط‌خواندنی — با currentDepId
# ══════════════════════════════════════════════════════════════════

_SHIFTS_JS_READONLY = r"""
async function loadGridReadonly() {
    const year  = FIXED_YEAR;
    const month = FIXED_MONTH;
    try {
        const [pd, ad] = await Promise.all([
            fetch(`/module/manager/shifts/personnel_by_dep?dep_id=${currentDepId}`).then(r => r.json()),
            fetch(`/module/manager/shifts/assignments?dep_id=${currentDepId}&year=${year}&month=${month}`).then(r => r.json())
        ]);
        if (!pd.success) throw new Error(pd.message);
        if (!ad.success) throw new Error(ad.message);

        const personnel = pd.personnel ?? [];
        const assigns   = ad.assignments ?? {};
        const extras    = ad.extras ?? {};
        const days      = ad.month_days ?? 30;

        /* هدر */
        const hCells = Array.from({length:days}, (_, i) => {
            const d  = i + 1;
            const wd = _shamsiWeekday(year, month, d);
            const cls = wd===6?'friday':wd===5?'thursday':'';
            return `<th class="${cls}"><div class="day-num">${d}</div><div class="day-wd">${WD_SHORT[wd]}</div></th>`;
        }).join('');
        document.getElementById('gridHead').innerHTML = `<tr><th>پرسنل / روز</th>${hCells}</tr>`;

        /* ردیف‌ها (فقط خواندنی) */
        const rows = personnel.map(p => {
            const pid  = p.ID_person;
            const name = `${p.nam} ${p.famil}`;
            const cells = Array.from({length:days}, (_, i) => {
                const d    = i + 1;
                const date = `${year}${String(month).padStart(2,'0')}${String(d).padStart(2,'0')}`;
                const key  = `${pid}_${date}`;
                const mainId = assigns[key] ?? '';
                const dayEx  = extras[key]  ?? [];
                const s      = mainId ? shiftMap.get(String(mainId)) : null;
                const bg     = s ? s.color_code : (_shamsiWeekday(year,month,d)===6?'#fff5f5':'#fff');
                let inner = '';
                if (s) {
                    inner += `<div style="background:${s.color_code||'#e2e8f0'};color:#fff;padding:2px 4px;
                        border-radius:3px;font-size:10px;font-weight:bold;">${s.shift_code}</div>`;
                }
                dayEx.forEach(ex => {
                    const es = shiftMap.get(String(ex));
                    if (es) inner += `<div style="background:#be185d;color:white;padding:1px 4px;
                        border-radius:3px;font-size:9px;font-weight:bold;">${es.shift_code}</div>`;
                });
                return `<td style="background:${bg};">
                    <div style="display:flex;flex-direction:column;gap:2px;align-items:stretch;">${inner}</div>
                </td>`;
            }).join('');
            return `<tr><td>👤 ${name}</td>${cells}</tr>`;
        }).join('');
        document.getElementById('gridBody').innerHTML = rows;

        loadApprovalBar(year, month);
    } catch(e) {
        toast('⛔ ' + e.message, 'e');
    }
}

function onDeptChange() {
    const sel = document.getElementById('deptSelector');
    if (!sel) return;
    currentDepId = parseInt(sel.value);
    document.getElementById('deptNameHeader').textContent = sel.options[sel.selectedIndex].text;
    loadGridReadonly();
}

document.addEventListener('DOMContentLoaded', loadGridReadonly);
"""


# ══════════════════════════════════════════════════════════════════
# توابع API (بازنویسی شده با پارامتر dep_id)
# ══════════════════════════════════════════════════════════════════

def get_department_personnel(dep_id: int) -> dict:
    """دریافت پرسنل یک بخش مشخص"""
    return _get_personnel_by_dep(dep_id)


def _get_personnel_by_dep(dep_id: int) -> dict:
    rows = query("""
        SELECT DISTINCT p.ID_person, p.nam, p.famil
        FROM   tbl_person p
        JOIN   tbl_sazema_person s ON p.ID_person = s.nam_person
        WHERE  s.nam_bakhsh=%s AND s.payani_sazmandehi=0 AND p.isActiv=1
        ORDER  BY p.famil, p.nam
    """, (dep_id,), fetch_all=True) or []
    return {'success': True, 'personnel': rows}


def get_assignments(year: Optional[int], month: Optional[int], dep_id: int) -> dict:
    if not year or not month:
        return {'success': False, 'message': 'سال و ماه الزامی هستند'}
    try:
        year  = _safe_int(year,  'سال')
        month = _safe_int(month, 'ماه')

        pr = _get_personnel_by_dep(dep_id)
        if not pr['success']:
            return pr
        pids = [r['ID_person'] for r in pr['personnel']]
        days = get_jalali_days(year, month)
        if not pids:
            return {'success': True, 'assignments': {}, 'extras': {}, 'month_days': days}
        s_date = int(f"{year}{month:02d}01")
        e_date = int(f"{year}{month:02d}{days:02d}")
        ph     = ','.join(['%s'] * len(pids))
        rows   = query(f"""
            SELECT ID_person, shift_date, ID_onvan_shift, is_extra
            FROM   tbl_personnel_shifts
            WHERE  ID_person IN ({ph}) AND shift_date BETWEEN %s AND %s
        """, (*pids, s_date, e_date), fetch_all=True) or []
        assigns, extras = {}, {}
        for r in rows:
            key = f"{r['ID_person']}_{r['shift_date']}"
            if r['is_extra']:
                extras.setdefault(key, []).append(r['ID_onvan_shift'])
            else:
                assigns[key] = r['ID_onvan_shift']
        return {'success': True, 'assignments': assigns, 'extras': extras, 'month_days': days}
    except Exception:
        logger.exception('خطا در get_assignments')
        return {'success': False, 'message': 'خطای داخلی سرور'}


def save_assignment(user: dict, form_data, force_edit=False) -> dict:
    try:
        f    = _require_fields(form_data, 'person_id', 'shift_date', 'dep_id')
        pid  = _safe_int(f['person_id'],  'person_id')
        date = _safe_int(f['shift_date'], 'shift_date')
        dep_id = _safe_int(f['dep_id'], 'dep_id')
        sid  = form_data.get('shift_id') or None
        uid  = user.get('UserID')

        year_  = int(str(date)[:4])
        month_ = int(str(date)[4:6])
        if not force_edit:
            locked = query(
                "SELECT 1 FROM tbl_shift_approvals WHERE dep_id=%s AND year=%s AND month=%s AND level_no=1",
                (dep_id, year_, month_), fetch_one=True
            )
            if locked:
                return {'success': False, 'message': 'برنامه تایید شده است و قابل ویرایش نیست. ابتدا تایید را لغو کنید.'}

        if sid:
            sid  = _safe_int(sid, 'shift_id')
            old  = query("SELECT ID_onvan_shift FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date=%s AND is_extra=0",
                         (pid, date), fetch_one=True)
            old_v = old['ID_onvan_shift'] if old else None
            if old:
                query("UPDATE tbl_personnel_shifts SET ID_onvan_shift=%s,assigned_by=%s,zaman_sabt=NOW() WHERE ID_person=%s AND shift_date=%s AND is_extra=0",
                      (sid, uid, pid, date), commit=True)
            else:
                query("INSERT INTO tbl_personnel_shifts (ID_person,shift_date,ID_onvan_shift,is_extra,assigned_by,zaman_sabt) VALUES (%s,%s,%s,0,%s,NOW())",
                      (pid, date, sid, uid), commit=True)
            _log_audit(dep_id, pid, date, 'UPDATE' if old else 'INSERT', old_v, sid, 0, uid)
        else:
            old = query("SELECT ID_onvan_shift FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date=%s AND is_extra=0",
                        (pid, date), fetch_one=True)
            if old:
                _log_audit(dep_id, pid, date, 'DELETE', old['ID_onvan_shift'], None, 0, uid)
            query("DELETE FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date=%s AND is_extra=0",
                  (pid, date), commit=True)
        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در save_assignment')
        return {'success': False, 'message': 'خطای داخلی سرور'}


def bulk_save_assignments(user: dict, form_data, force_edit=False) -> dict:
    try:
        f = _require_fields(form_data, 'person_id','year','month','start_day','end_day','dep_id')
        pid   = _safe_int(f['person_id'], 'person_id')
        year  = _safe_int(f['year'],      'year')
        month = _safe_int(f['month'],     'month')
        sd    = _safe_int(f['start_day'], 'start_day')
        ed    = _safe_int(f['end_day'],   'end_day')
        dep_id = _safe_int(f['dep_id'],   'dep_id')
        sid   = form_data.get('shift_id') or None
        uid   = user.get('UserID')

        if not force_edit:
            locked = query(
                "SELECT 1 FROM tbl_shift_approvals WHERE dep_id=%s AND year=%s AND month=%s AND level_no=1",
                (dep_id, year, month), fetch_one=True
            )
            if locked:
                return {'success': False, 'message': 'برنامه تایید شده است. ابتدا تایید را لغو کنید.'}

        if sd > ed:
            return {'success': False, 'message': 'روز شروع باید کوچکتر باشد'}
        maxd  = get_jalali_days(year, month)
        sd, ed = max(1, min(sd, maxd)), max(1, min(ed, maxd))
        dates = [int(f"{year}{month:02d}{d:02d}") for d in range(sd, ed + 1)]
        if not dates:
            return {'success': True}
        ph = ','.join(['%s'] * len(dates))
        query(f"DELETE FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date IN ({ph}) AND is_extra=0",
              (pid, *dates), commit=True)
        if sid and sid != 'DELETE':
            sid = _safe_int(sid, 'shift_id')
            vals = ','.join(['(%s,%s,%s,0,%s,NOW())'] * len(dates))
            params = []
            for d in dates:
                params.extend([pid, d, sid, uid])
                _log_audit(dep_id, pid, d, 'INSERT', None, sid, 0, uid, 'bulk')
            query(f"INSERT INTO tbl_personnel_shifts (ID_person,shift_date,ID_onvan_shift,is_extra,assigned_by,zaman_sabt) VALUES {vals}",
                  params, commit=True)
        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در bulk_save_assignments')
        return {'success': False, 'message': 'خطای داخلی سرور'}


def handle_extra_shifts(user: dict, request, force_edit=False) -> dict:
    try:
        f   = _require_fields(request.form, 'person_id','shift_date','shift_id','dep_id')
        pid = _safe_int(f['person_id'],  'person_id')
        date= _safe_int(f['shift_date'], 'shift_date')
        sid = _safe_int(f['shift_id'],   'shift_id')
        dep_id = _safe_int(f['dep_id'],   'dep_id')
        uid = user.get('UserID')

        date_str = str(date)
        year_  = int(date_str[:4])
        month_ = int(date_str[4:6])
        if not force_edit:
            locked = query(
                "SELECT 1 FROM tbl_shift_approvals WHERE dep_id=%s AND year=%s AND month=%s AND level_no=1",
                (dep_id, year_, month_), fetch_one=True
            )
            if locked:
                return {'success': False, 'message': 'برنامه تأیید شده است و شیفت اضافی قابل ویرایش نیست.'}

        query("INSERT INTO tbl_personnel_shifts (ID_person,shift_date,ID_onvan_shift,is_extra,assigned_by,zaman_sabt) VALUES (%s,%s,%s,1,%s,NOW())",
              (pid, date, sid, uid), commit=True)
        _log_audit(dep_id, pid, date, 'INSERT', None, sid, 1, uid)
        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در handle_extra_shifts')
        return {'success': False, 'message': 'خطای داخلی سرور'}


def delete_extra_shift(user: dict, form_data, force_edit=False) -> dict:
    try:
        f   = _require_fields(form_data, 'person_id','shift_date','shift_id','dep_id')
        pid = _safe_int(f['person_id'],  'person_id')
        date= _safe_int(f['shift_date'], 'shift_date')
        sid = _safe_int(f['shift_id'],   'shift_id')
        dep_id = _safe_int(f['dep_id'],   'dep_id')
        uid = user.get('UserID')

        date_str = str(date)
        year_  = int(date_str[:4])
        month_ = int(date_str[4:6])
        if not force_edit:
            locked = query(
                "SELECT 1 FROM tbl_shift_approvals WHERE dep_id=%s AND year=%s AND month=%s AND level_no=1",
                (dep_id, year_, month_), fetch_one=True
            )
            if locked:
                return {'success': False, 'message': 'برنامه تأیید شده است و شیفت اضافی قابل حذف نیست.'}

        query("DELETE FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date=%s AND ID_onvan_shift=%s AND is_extra=1 LIMIT 1",
              (pid, date, sid), commit=True)
        _log_audit(dep_id, pid, date, 'DELETE', sid, None, 1, uid)
        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در delete_extra_shift')
        return {'success': False, 'message': 'خطای داخلی سرور'}
