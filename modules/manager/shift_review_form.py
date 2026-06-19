"""
modules/manager/shift_review_form.py — نسخه v4 (نمایش امضای تأییدکنندگان)
  ✅ حذف سطح ۱ از لیست تأیید مدیران اجرایی
  ✅ دکمه تأیید در modal
  ✅ چاپ حرفه‌ای
  ✅ **نمایش تصویر امضای دیجیتال تأییدکننده در فوتر چاپ**
"""
import logging, secrets, base64, os
import jdatetime
from models.database import query
from modules.admin.users_form import get_user_signature   # import helper

logger = logging.getLogger(__name__)

PERSIAN_MONTHS = [
    'فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور',
    'مهر','آبان','آذر','دی','بهمن','اسفند'
]

# ══════════════════════════════════════════════════════════
# توابع داده
# ══════════════════════════════════════════════════════════

def get_pending_approvals(user_id: int) -> dict:
    rows = query("""
        SELECT
            ap.dep_id, b.nam_bakhsh, ap.level_no, ap.level_label,
            prev.year, prev.month,
            prev.approved_at  AS prev_approved_at,
            prev_u.FullName   AS prev_approver_name,
            prev_ap.level_label AS prev_level_label
        FROM tbl_shift_approvers ap
        LEFT JOIN tbl_bakhsh b ON b.ID_nam_bakhsh = ap.dep_id
        JOIN tbl_shift_approvals prev
            ON prev.dep_id   = ap.dep_id
           AND prev.level_no = ap.level_no - 1
        LEFT JOIN users prev_u ON prev_u.UserID = prev.approved_by
        LEFT JOIN tbl_shift_approvers prev_ap
            ON prev_ap.dep_id = ap.dep_id AND prev_ap.level_no = prev.level_no
        LEFT JOIN tbl_shift_approvals done
            ON done.dep_id   = ap.dep_id
           AND done.year      = prev.year
           AND done.month     = prev.month
           AND done.level_no  = ap.level_no
        WHERE ap.user_id  = %s
          AND ap.level_no > 1
          AND done.ID IS NULL
        ORDER BY prev.year DESC, prev.month DESC, b.nam_bakhsh
    """, (user_id,), fetch_all=True) or []
    return {'success': True, 'pending': rows}


def get_approved_by_user(user_id: int) -> dict:
    rows = query("""
        SELECT
            a.dep_id, b.nam_bakhsh, a.level_no,
            ap.level_label,
            a.year, a.month, a.approved_at, a.note
        FROM tbl_shift_approvals a
        LEFT JOIN tbl_bakhsh b ON b.ID_nam_bakhsh = a.dep_id
        LEFT JOIN tbl_shift_approvers ap
            ON ap.dep_id = a.dep_id AND ap.level_no = a.level_no
        WHERE a.approved_by = %s
          AND a.level_no > 1
        ORDER BY a.approved_at DESC
        LIMIT 200
    """, (user_id,), fetch_all=True) or []
    return {'success': True, 'approved': rows}


def get_shift_data_for_view(dep_id: int, year: int, month: int) -> dict:
    """داده کامل برنامه + تمام سطوح تأیید + امضاهای تصویری."""
    try:
        dept = query("SELECT nam_bakhsh FROM tbl_bakhsh WHERE ID_nam_bakhsh=%s", (dep_id,), fetch_one=True)
        dept_name = dept['nam_bakhsh'] if dept else 'نامشخص'

        personnel = query("""
            SELECT DISTINCT p.ID_person, p.nam, p.famil
            FROM   tbl_person p
            JOIN   tbl_sazema_person s ON p.ID_person = s.nam_person
            WHERE  s.nam_bakhsh=%s AND s.payani_sazmandehi=0 AND p.isActiv=1
            ORDER  BY p.famil, p.nam
        """, (dep_id,), fetch_all=True) or []

        shifts = query("SELECT ID_onvan_shift, nam_shift, shift_code, color_code FROM onvan_shift ORDER BY ID_onvan_shift", fetch_all=True) or []

        if month <= 6: days = 31
        elif month <= 11: days = 30
        else:
            try:
                jdatetime.date(year, 12, 30)
                days = 30
            except ValueError:
                days = 29

        pids = [p['ID_person'] for p in personnel]
        assigns, extras = {}, {}
        if pids:
            s_date = int(f"{year}{month:02d}01")
            e_date = int(f"{year}{month:02d}{days:02d}")
            ph = ','.join(['%s'] * len(pids))
            rows = query(f"""
                SELECT ID_person, shift_date, ID_onvan_shift, is_extra
                FROM   tbl_personnel_shifts
                WHERE  ID_person IN ({ph}) AND shift_date BETWEEN %s AND %s
            """, (*pids, s_date, e_date), fetch_all=True) or []
            for r in rows:
                key = f"{r['ID_person']}_{r['shift_date']}"
                if r['is_extra']:
                    extras.setdefault(key, []).append(r['ID_onvan_shift'])
                else:
                    assigns[key] = r['ID_onvan_shift']

        # همه سطوح تأیید (شامل سطح ۱)
        approvals = query("""
            SELECT a.level_no, a.approved_by, a.approved_at, a.note,
                   u.FullName as approver_name,
                   u.emza_path,
                   ap.level_label
            FROM   tbl_shift_approvals a
            LEFT JOIN users u ON u.UserID = a.approved_by
            LEFT JOIN tbl_shift_approvers ap
                ON ap.dep_id = a.dep_id AND ap.level_no = a.level_no
            WHERE  a.dep_id=%s AND a.year=%s AND a.month=%s
            ORDER  BY a.level_no
        """, (dep_id, year, month), fetch_all=True) or []

        # تنظیمات تأییدکننده‌ها
        approvers_cfg = query("""
            SELECT ap.level_no, ap.level_label, u.FullName, u.UserID
            FROM   tbl_shift_approvers ap
            LEFT JOIN users u ON u.UserID = ap.user_id
            WHERE  ap.dep_id=%s
            ORDER  BY ap.level_no
        """, (dep_id,), fetch_all=True) or []

        # 🆕 جمع‌آوری امضاهای دیجیتال تأییدکنندگان
        signatures = {}
        for ap in approvals:
            uid = ap.get('approved_by')
            if uid and uid not in signatures:
                sig = get_user_signature(uid)
                if sig['success']:
                    signatures[uid] = sig['data']   # data:image/...;base64,...

        return {
            'success': True,
            'dept_name': dept_name,
            'personnel': personnel,
            'shifts': shifts,
            'assigns': assigns,
            'extras': extras,
            'days': days,
            'approvals': approvals,
            'approvers_cfg': approvers_cfg,
            'signatures': signatures,              # ← امضاها
        }
    except Exception:
        logger.exception('خطا در get_shift_data_for_view')
        return {'success': False, 'message': 'خطای داخلی سرور'}


def get_shift_view_data(user_id: int, dep_id: int, year: int, month: int) -> dict:
    has_access = query(
        "SELECT level_no FROM tbl_shift_approvers WHERE dep_id=%s AND user_id=%s",
        (dep_id, user_id), fetch_one=True
    )
    if not has_access:
        return {'success': False, 'message': 'دسترسی مجاز نیست'}
    data = get_shift_data_for_view(dep_id, year, month)
    if data.get('success'):
        data['my_level_no'] = has_access['level_no']
    return data


def do_approve(user: dict, form_data) -> dict:
    try:
        dep_id   = int(form_data.get('dep_id', 0))
        year     = int(form_data.get('year', 0))
        month    = int(form_data.get('month', 0))
        level_no = int(form_data.get('level_no', 0))
        note     = (form_data.get('note') or '').strip() or None
        user_id  = user.get('UserID')
        if not all([dep_id, year, month, level_no]):
            return {'success': False, 'message': 'اطلاعات ناقص است'}
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
                return {'success': False, 'message': 'سطح قبلی هنوز تایید نشده است'}
        query("""
            INSERT INTO tbl_shift_approvals (dep_id,year,month,level_no,approved_by,note)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE approved_by=%s, approved_at=NOW(), note=%s
        """, (dep_id, year, month, level_no, user_id, note, user_id, note), commit=True)
        return {'success': True}
    except Exception:
        logger.exception('خطا در do_approve')
        return {'success': False, 'message': 'خطای داخلی سرور'}


def do_revoke(user: dict, form_data) -> dict:
    try:
        dep_id   = int(form_data.get('dep_id', 0))
        year     = int(form_data.get('year', 0))
        month    = int(form_data.get('month', 0))
        level_no = int(form_data.get('level_no', 0))
        user_id  = user.get('UserID')
        if not all([dep_id, year, month, level_no]):
            return {'success': False, 'message': 'اطلاعات ناقص است'}
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
            return {'success': False, 'message': 'ابتدا باید تأییدهای سطح بالاتر لغو شود'}
        query(
            "DELETE FROM tbl_shift_approvals WHERE dep_id=%s AND year=%s AND month=%s AND level_no=%s",
            (dep_id, year, month, level_no), commit=True
        )
        return {'success': True}
    except Exception:
        logger.exception('خطا در do_revoke')
        return {'success': False, 'message': 'خطای داخلی سرور'}


# ══════════════════════════════════════════════════════════
# HTML
# ══════════════════════════════════════════════════════════

def get_shift_review_page(user: dict) -> str:
    from flask import session as _s
    if '_csrf_token' not in _s:
        _s['_csrf_token'] = secrets.token_hex(32)
    tok = _s['_csrf_token']

    full_name = user.get('FullName', '')
    today     = jdatetime.date.today()
    cy, cm    = today.year, today.month

    yopts = ''.join(f'<option value="{y}"{" selected" if y==cy else ""}>{y}</option>' for y in range(cy-1, cy+2))
    mopts = '<option value="">همه ماه‌ها</option>'
    for m in range(1, 13):
        mopts += f'<option value="{m}"{" selected" if m==cm else ""}>{PERSIAN_MONTHS[m-1]}</option>'

    return f'''<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="csrf-token" content="{tok}">
<title>تأیید برنامه شیفت‌بندی</title>
<style>{_CSS}</style>
</head>
<body>
<div class="toast-box" id="toastBox"></div>
<div class="container">
  <div class="header">
    <div><h2>✅ تأیید برنامه شیفت‌بندی</h2><p>👤 {full_name}</p></div>
    <a href="/module/manager" class="back-btn">⬅️ بازگشت</a>
  </div>
  <div class="filter-bar">
    <label>سال:</label><select id="fYear" onchange="loadAll()">{yopts}</select>
    <label>ماه:</label><select id="fMonth" onchange="loadAll()">{mopts}</select>
  </div>
  <div class="tabs">
    <div class="tab active" data-tab="pending" onclick="showTab('pending')">
      در انتظار تأیید <span class="tab-badge" id="pendingCount" style="display:none;"></span>
    </div>
    <div class="tab" data-tab="approved" onclick="showTab('approved')">تأیید شده‌ها</div>
  </div>
  <div class="tab-pane active" id="pane-pending"><div id="pendingList"></div></div>
  <div class="tab-pane" id="pane-approved"><div id="approvedList"></div></div>
</div>

<!-- Modal تأیید/لغو -->
<div class="modal" id="confirmModal">
  <div class="mbox">
    <h3 id="mTitle">تأیید</h3>
    <div class="minfo" id="mInfo"></div>
    <input type="hidden" id="mDepId">
    <input type="hidden" id="mYear">
    <input type="hidden" id="mMonth">
    <input type="hidden" id="mLevel">
    <input type="hidden" id="mAction">
    <label>یادداشت (اختیاری)</label>
    <textarea id="mNote" rows="3" placeholder="توضیحات..."></textarea>
    <div class="mact">
      <button class="btn btn-green" id="mBtn" onclick="submitAction()">✅ ثبت تأیید</button>
      <button class="btn btn-gray" onclick="closeConfirm()">انصراف</button>
    </div>
  </div>
</div>

<!-- Modal مشاهده برنامه -->
<div class="modal" id="viewModal">
  <div class="view-mbox" id="viewMbox">
    <div class="view-header">
      <div>
        <h3 id="vTitle">برنامه شیفت</h3>
        <p id="vSubtitle"></p>
      </div>
      <div class="vhdr-acts">
        <button class="btn btn-purple" onclick="printViewModal()">🖨️ چاپ</button>
        <button id="vApproveBtn" class="btn btn-green" onclick="approveFromView()" style="display:none;">✅ تأیید</button>
        <button class="btn btn-gray btn-sm" onclick="closeView()">✕ بستن</button>
      </div>
    </div>
    <div id="vApprovalBar" class="v-approval-bar"></div>
    <div id="vContent" class="view-content">
      <div class="spinner">⏳ در حال بارگذاری...</div>
    </div>
    <div id="vPrintFooter" class="vprint-footer"></div>
  </div>
</div>

<script>{_JS}</script>
</body></html>'''


# ══════════════════════════════════════════════════════════
# CSS (بدون تغییر عمده)
# ══════════════════════════════════════════════════════════

_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:Tahoma,'Segoe UI',sans-serif;direction:rtl;background:#f8fafc;color:#1e293b;min-height:100vh;}
.container{max-width:1000px;margin:0 auto;padding:16px;}

.header{background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;border-radius:12px;
  padding:16px 20px;margin-bottom:14px;display:flex;justify-content:space-between;
  align-items:center;flex-wrap:wrap;gap:8px;}
.header h2{font-size:16px;margin:0;}
.header p{font-size:12px;opacity:.85;margin:3px 0 0;}
.back-btn{color:white;padding:7px 16px;border:1px solid rgba(255,255,255,.4);border-radius:8px;
  text-decoration:none;font-size:13px;white-space:nowrap;}
.back-btn:hover{background:rgba(255,255,255,.15);}

.tabs{display:flex;border-bottom:2px solid #e2e8f0;margin-bottom:14px;}
.tab{padding:11px 20px;font-size:14px;font-weight:600;cursor:pointer;color:#64748b;
  border-bottom:3px solid transparent;margin-bottom:-2px;transition:.15s;}
.tab.active{color:#0f766e;border-bottom-color:#0f766e;}
.tab-badge{background:#ef4444;color:white;border-radius:10px;padding:1px 7px;font-size:11px;margin-right:6px;}
.tab-pane{display:none;}.tab-pane.active{display:block;}

.filter-bar{background:white;border-radius:10px;border:1px solid #e2e8f0;
  padding:11px 16px;margin-bottom:14px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;}
.filter-bar label{font-size:13px;font-weight:600;}
.filter-bar select{padding:6px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;}

.card{background:white;border-radius:10px;border:1px solid #e2e8f0;margin-bottom:10px;overflow:hidden;transition:.2s;}
.card:hover{box-shadow:0 4px 14px rgba(0,0,0,.08);transform:translateY(-1px);}
.card-head{padding:14px 16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
.dname{font-weight:bold;font-size:15px;}
.dmeta{font-size:12px;color:#64748b;margin-top:3px;}
.actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;}
.prev-bar{background:linear-gradient(90deg,#f0fdf4,#f8fafc);border-top:1px solid #bbf7d0;
  padding:8px 16px;font-size:12px;color:#166534;}

.badge{display:inline-flex;align-items:center;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;}
.badge-done{background:#d1fae5;color:#065f46;}
.badge-level{background:#dbeafe;color:#1e40af;}

.btn{display:inline-flex;align-items:center;gap:5px;padding:8px 16px;border:none;
  border-radius:8px;font-size:13px;font-weight:bold;cursor:pointer;transition:.15s;white-space:nowrap;}
.btn:hover{filter:brightness(.9);}
.btn-teal{background:#0f766e;color:white;}.btn-green{background:#10b981;color:white;}
.btn-red{background:#ef4444;color:white;}.btn-gray{background:#64748b;color:white;}
.btn-purple{background:#7c3aed;color:white;}.btn-sm{padding:6px 12px;font-size:12px;}

.empty{text-align:center;padding:52px 20px;color:#94a3b8;}
.empty .ico{font-size:46px;margin-bottom:12px;}
.spinner{text-align:center;padding:32px;color:#0f766e;font-weight:bold;}

.toast-box{position:fixed;top:14px;left:50%;transform:translateX(-50%);z-index:9999;
  display:flex;flex-direction:column;gap:8px;min-width:260px;}
.toast{padding:11px 18px;border-radius:10px;color:white;font-weight:600;font-size:13px;
  box-shadow:0 6px 18px rgba(0,0,0,.18);animation:tin .2s ease;}
.toast.ok{background:linear-gradient(135deg,#059669,#10b981);}
.toast.er{background:linear-gradient(135deg,#dc2626,#ef4444);}
@keyframes tin{from{opacity:0;transform:translateY(-10px);}to{opacity:1;transform:translateY(0);}}

/* Modal تأیید */
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:400;
  align-items:center;justify-content:center;}
.modal.open{display:flex;}
.mbox{background:white;padding:24px;border-radius:14px;width:95%;max-width:440px;
  box-shadow:0 20px 50px rgba(0,0,0,.22);}
.mbox h3{font-size:16px;margin-bottom:8px;}
.minfo{color:#0f766e;font-weight:700;font-size:14px;margin-bottom:16px;padding:10px;
  background:#f0fdf4;border-radius:8px;border-right:3px solid #10b981;}
.mbox label{display:block;font-size:13px;font-weight:600;color:#64748b;margin-bottom:4px;margin-top:12px;}
.mbox textarea{width:100%;padding:9px;border:2px solid #e2e8f0;border-radius:8px;font-size:13px;resize:vertical;font-family:inherit;}
.mact{margin-top:18px;display:flex;gap:10px;}
.mact .btn{flex:1;justify-content:center;}

/* Modal مشاهده */
.view-mbox{background:white;border-radius:14px;width:98vw;max-width:1200px;
  max-height:94vh;display:flex;flex-direction:column;
  box-shadow:0 24px 60px rgba(0,0,0,.28);overflow:hidden;}
.view-header{background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;
  padding:14px 20px;display:flex;justify-content:space-between;align-items:center;
  flex-wrap:wrap;gap:10px;flex-shrink:0;}
.view-header h3{font-size:15px;margin:0;}
.view-header p{font-size:11px;opacity:.85;margin:2px 0 0;}
.vhdr-acts{display:flex;gap:8px;align-items:center;flex-wrap:wrap;}
.v-approval-bar{background:#f0fdf4;border-bottom:2px solid #d1fae5;padding:10px 16px;
  display:flex;gap:8px;flex-wrap:wrap;align-items:center;flex-shrink:0;}
.v-approval-bar .bar-lbl{font-weight:bold;font-size:13px;color:#374151;margin-left:6px;white-space:nowrap;}
.ap-chip{display:inline-flex;align-items:center;gap:5px;padding:5px 12px;border-radius:20px;
  font-size:12px;font-weight:600;border:2px solid;}
.ap-chip.done{background:#d1fae5;color:#065f46;border-color:#6ee7b7;}
.ap-chip.wait{background:#fef3c7;color:#92400e;border-color:#fcd34d;}
.view-content{overflow:auto;flex:1;padding:16px;}

/* جدول readonly */
.ro-wrap{overflow-x:auto;}
.ro-table{width:100%;border-collapse:collapse;font-size:11px;}
.ro-table th,.ro-table td{border:1px solid #cbd5e1;padding:3px 2px;text-align:center;min-width:44px;}
.ro-table th{background:#f1f5f9;position:sticky;top:0;z-index:2;white-space:nowrap;}
.ro-table th .dn{font-size:12px;font-weight:bold;line-height:1.3;}
.ro-table th .dw{font-size:10px;color:#64748b;font-weight:normal;}
.ro-table th.fri .dn{color:#dc2626;}.ro-table th.fri .dw{color:#fca5a5;}
.ro-table th.thu .dn{color:#7c3aed;}
.ro-table td:first-child{position:sticky;right:0;background:#f8fafc;font-weight:bold;
  text-align:right;padding-right:8px;min-width:150px;z-index:1;white-space:nowrap;font-size:12px;}
.sc{display:flex;flex-direction:column;gap:2px;min-height:20px;}
.sm{border-radius:3px;padding:2px 4px;font-size:10px;font-weight:bold;color:#fff;text-align:center;}
.sx{background:#be185d;color:white;border-radius:3px;padding:1px 3px;font-size:9px;font-weight:bold;}

/* فوتر چاپ در modal */
.vprint-footer{flex-shrink:0;border-top:3px solid #0f766e;padding:12px 16px;background:#f8fafc;display:none;}
.vprint-footer.visible{display:block;}
.vpf-title{font-size:13px;font-weight:bold;color:#0f766e;margin-bottom:10px;text-align:center;}
.vpf-grid{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;}
.vpf-cell{flex:1;min-width:130px;max-width:220px;border:1px solid #e2e8f0;border-radius:10px;
  padding:12px 10px;text-align:center;}
.vpf-cell.signed{background:#f0fdf4;border-color:#6ee7b7;}
.vpf-cell.unsigned{background:#fff;border-color:#e2e8f0;}
.vpf-lvl{font-size:11px;color:#64748b;margin-bottom:6px;font-weight:600;}
.vpf-name{font-size:13px;font-weight:bold;color:#0f172a;}
.vpf-dt{font-size:11px;color:#0f766e;margin-top:4px;direction:ltr;}
.vpf-sig{margin-top:14px;border-top:1px dashed #cbd5e1;padding-top:8px;font-size:11px;color:#94a3b8;}
.vpf-sig-img{max-width:100px;max-height:40px;margin-top:6px;}

/* ─── چاپ ─── */
@media print {
  @page { size: A4 landscape; margin: 8mm 6mm; }
  body > *:not(#viewModal) { display: none !important; }
  #viewModal {
    position: relative !important; display: block !important; width: 100% !important;
    max-width: none !important; height: auto !important; overflow: visible !important;
    background: none !important; margin: 0 !important; padding: 0 !important;
  }
  .view-mbox {
    position: static !important; width: 100% !important; max-width: none !important;
    max-height: none !important; height: auto !important; box-shadow: none !important;
    border-radius: 0 !important; overflow: visible !important; display: block !important;
  }
  .view-header { display: none !important; }
  .v-approval-bar { break-inside: avoid; }
  .view-content { overflow: visible !important; max-height: none !important; padding: 0 !important; }
  .ro-wrap { overflow: visible !important; }
  .ro-table {
    font-size: 9px !important; table-layout: fixed; width: 100% !important;
  }
  .ro-table th, .ro-table td {
    min-width: 28px !important; padding: 2px 1px !important; position: static !important;
  }
  .ro-table td:first-child {
    min-width: 110px !important; font-size: 9px !important; position: static !important;
  }
  .sm { font-size: 8px !important; padding: 1px 2px !important; }
  .vprint-footer { display: block !important; visibility: visible !important; }
  thead { display: table-header-group; }
  tbody { display: table-row-group; }
  tr { page-break-inside: avoid; }
}
"""


# ══════════════════════════════════════════════════════════
# JavaScript (تغییر در نمایش امضا)
# ══════════════════════════════════════════════════════════

_JS = r"""
const MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور',
                'مهر','آبان','آذر','دی','بهمن','اسفند'];
const WD = ['ش','ی','د','س','چ','پ','ج'];

let _pending  = [];
let _approved = [];
let _vCtx = null;

function csrf() { return document.querySelector('meta[name="csrf-token"]')?.content || ''; }

async function apiPost(url, data) {
  const p = new URLSearchParams(data), t = csrf();
  if (t) p.append('csrf_token', t);
  const r = await fetch(url, {
    method:'POST', body:p.toString(), credentials:'include',
    headers:{'Content-Type':'application/x-www-form-urlencoded',
             'X-CSRFToken':t, 'X-Requested-With':'XMLHttpRequest'}
  });
  if (!r.ok) throw new Error('خطای سرور ' + r.status);
  const d = await r.json();
  if (!d.success) throw new Error(d.message || 'خطا');
  return d;
}

function toast(msg, type) {
  const b = document.getElementById('toastBox');
  const e = document.createElement('div');
  e.className = 'toast ' + (type || 'ok');
  e.textContent = msg;
  b.appendChild(e);
  setTimeout(() => e.remove(), 4500);
}

function showTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.toggle('active', p.id === 'pane-' + name));
}

function getF() {
  return { year: +document.getElementById('fYear').value,
           month: document.getElementById('fMonth').value };
}

async function loadAll() { await Promise.all([loadPending(), loadApproved()]); }

async function loadPending() {
  const box = document.getElementById('pendingList');
  box.innerHTML = '<div class="spinner">⏳ در حال بارگذاری...</div>';
  const f = getF();
  try {
    const r = await fetch('/module/manager/shift_review/pending?year=' + f.year + (f.month ? '&month=' + f.month : ''));
    const d = await r.json();
    if (!d.success) throw new Error(d.message);
    _pending = d.pending || [];
    const badge = document.getElementById('pendingCount');
    if (_pending.length) { badge.textContent = _pending.length; badge.style.display = 'inline-block'; }
    else { badge.style.display = 'none'; }
    if (!_pending.length) {
      box.innerHTML = '<div class="empty"><div class="ico">✅</div><p>موردی در انتظار تأیید شما نیست</p></div>';
      return;
    }
    box.innerHTML = _pending.map((row, i) => {
      const mn  = MONTHS[row.month - 1] || row.month;
      const lbl = 'سطح ' + row.level_no + (row.level_label ? ' — ' + row.level_label : '');
      const pd  = row.prev_approved_at ? row.prev_approved_at.slice(0, 16) : '';
      const plbl = row.prev_level_label || ('سطح ' + (row.level_no - 1));
      return `<div class="card">
        <div class="card-head">
          <div>
            <div class="dname">🏥 ${row.nam_bakhsh}</div>
            <div class="dmeta">📅 ${row.year} — ${mn}</div>
          </div>
          <div class="actions">
            <span class="badge badge-level">${lbl}</span>
            <button class="btn btn-teal btn-sm" onclick="openViewModal(${i},'pending')">👁 مشاهده</button>
            <button class="btn btn-green btn-sm" onclick="openConfirm(${i})">✅ تأیید</button>
          </div>
        </div>
        ${pd ? `<div class="prev-bar">✔️ ${plbl} تأیید شده توسط ${row.prev_approver_name || '—'} در ${pd}</div>` : ''}
      </div>`;
    }).join('');
  } catch(e) { box.innerHTML = `<div style="color:red;padding:16px;">${e.message}</div>`; }
}

async function loadApproved() {
  const box = document.getElementById('approvedList');
  box.innerHTML = '<div class="spinner">⏳ در حال بارگذاری...</div>';
  const f = getF();
  try {
    const r = await fetch('/module/manager/shift_review/approved?year=' + f.year + (f.month ? '&month=' + f.month : ''));
    const d = await r.json();
    if (!d.success) throw new Error(d.message);
    _approved = d.approved || [];
    if (!_approved.length) {
      box.innerHTML = '<div class="empty"><div class="ico">📋</div><p>تأییدی ثبت نشده است</p></div>';
      return;
    }
    box.innerHTML = _approved.map((row, i) => {
      const mn  = MONTHS[row.month - 1] || row.month;
      const dt  = row.approved_at ? row.approved_at.slice(0, 16) : '';
      const lbl = 'سطح ' + row.level_no + (row.level_label ? ' — ' + row.level_label : '');
      return `<div class="card">
        <div class="card-head">
          <div>
            <div class="dname">🏥 ${row.nam_bakhsh}</div>
            <div class="dmeta">📅 ${row.year} — ${mn} &nbsp;|&nbsp; ✔️ ${dt}</div>
            ${row.note ? `<div class="dmeta" style="color:#0f766e;margin-top:2px;">💬 ${row.note}</div>` : ''}
          </div>
          <div class="actions">
            <span class="badge badge-done">✅ ${lbl}</span>
            <button class="btn btn-teal btn-sm" onclick="openViewModal(${i},'approved')">👁 مشاهده</button>
            <button class="btn btn-red btn-sm" onclick="openRevoke(${i})">↩️ لغو</button>
          </div>
        </div>
      </div>`;
    }).join('');
  } catch(e) { box.innerHTML = `<div style="color:red;padding:16px;">${e.message}</div>`; }
}

/* ──── Modal مشاهده ──── */
async function openViewModal(idx, src) {
  const row = src === 'pending' ? _pending[idx] : _approved[idx];
  _vCtx = { row, src, idx };

  const mn = MONTHS[row.month - 1] || row.month;
  document.getElementById('vTitle').textContent    = `📋 ${row.nam_bakhsh}`;
  document.getElementById('vSubtitle').textContent = `${row.year} — ${mn}`;
  document.getElementById('vContent').innerHTML    = '<div class="spinner">⏳ در حال بارگذاری...</div>';
  document.getElementById('vApprovalBar').innerHTML = '';
  document.getElementById('vPrintFooter').className = 'vprint-footer';

  const btn = document.getElementById('vApproveBtn');
  btn.style.display = 'none';

  document.getElementById('viewModal').classList.add('open');

  try {
    const url = `/module/manager/shift_review/view_data?dep_id=${row.dep_id}&year=${row.year}&month=${row.month}`;
    const d   = await (await fetch(url)).json();
    if (!d.success) throw new Error(d.message);

    _vCtx.data = d;

    renderVApprovalBar(d);
    renderVTable(d, row.year, row.month);
    renderVPrintFooter(d, row.year, row.month);

    if (src === 'pending' && d.my_level_no) {
      const alreadyDone = (d.approvals || []).find(a => a.level_no === d.my_level_no);
      if (!alreadyDone) {
        btn.style.display = 'inline-flex';
      }
    }
  } catch(e) {
    document.getElementById('vContent').innerHTML = `<div style="color:red;padding:20px;">${e.message}</div>`;
  }
}

function renderVApprovalBar(d) {
  const bar = document.getElementById('vApprovalBar');
  const approvals = d.approvals || [];
  const cfgs      = d.approvers_cfg || [];

  let html = '<span class="bar-lbl">📋 وضعیت تأیید:</span>';
  if (!cfgs.length) {
    bar.innerHTML = html + '<span style="color:#94a3b8;font-size:12px;">تأییدکننده‌ای تعریف نشده</span>';
    return;
  }
  cfgs.forEach(c => {
    const ap  = approvals.find(a => a.level_no === c.level_no);
    const lbl = c.level_label || ('سطح ' + c.level_no);
    if (ap) {
      const dt = ap.approved_at ? ap.approved_at.slice(0, 16) : '';
      html += `<span class="ap-chip done" title="${dt}">✅ ${lbl} — ${ap.approver_name}</span>`;
    } else {
      html += `<span class="ap-chip wait">⬜ ${lbl} — ${c.FullName}</span>`;
    }
  });
  bar.innerHTML = html;
}

function renderVTable(d, year, month) {
  const { personnel, shifts, assigns, extras, days } = d;
  const sm = new Map(shifts.map(s => [String(s.ID_onvan_shift), s]));

  let hCells = '<th style="min-width:150px;position:sticky;right:0;background:#f1f5f9;z-index:3;">پرسنل / روز</th>';
  for (let day = 1; day <= days; day++) {
    const wd  = sw(year, month, day);
    const cls = wd === 6 ? 'fri' : wd === 5 ? 'thu' : '';
    hCells += `<th class="${cls}"><div class="dn">${day}</div><div class="dw">${WD[wd]}</div></th>`;
  }

  let rows = '';
  (personnel || []).forEach(p => {
    let cells = `<td style="min-width:150px;position:sticky;right:0;background:#f8fafc;z-index:1;text-align:right;padding-right:8px;">👤 ${p.nam} ${p.famil}</td>`;
    for (let day = 1; day <= days; day++) {
      const date = `${year}${String(month).padStart(2,'0')}${String(day).padStart(2,'0')}`;
      const key  = `${p.ID_person}_${date}`;
      const main = assigns[key];
      const exs  = extras[key] || [];
      const s    = main ? sm.get(String(main)) : null;
      const bg   = s ? (s.color_code || '#e2e8f0') : (sw(year,month,day)===6 ? '#fff5f5' : '#fff');
      let inner  = '';
      if (s) inner += `<div class="sm" style="background:${s.color_code||'#64748b'};">${s.shift_code}</div>`;
      exs.forEach(ex => { const es = sm.get(String(ex)); if(es) inner += `<div class="sx">${es.shift_code}</div>`; });
      cells += `<td style="background:${bg};"><div class="sc">${inner}</div></td>`;
    }
    rows += `<tr>${cells}</tr>`;
  });

  document.getElementById('vContent').innerHTML =
    `<div class="ro-wrap"><table class="ro-table">
      <thead><tr>${hCells}</tr></thead>
      <tbody>${rows}</tbody>
    </table></div>`;
}

function renderVPrintFooter(d, year, month) {
  const footer = document.getElementById('vPrintFooter');
  const mn     = MONTHS[month - 1] || month;
  const cfgs   = d.approvers_cfg || [];
  const apps   = d.approvals || [];
  const sigs   = d.signatures || {};

  let cells = cfgs.map(c => {
    const ap   = apps.find(a => a.level_no === c.level_no);
    const lbl  = c.level_label || ('سطح ' + c.level_no);
    const name = ap ? ap.approver_name : c.FullName;
    const dt   = ap && ap.approved_at ? ap.approved_at.slice(0, 16) : '';
    const cls  = ap ? 'signed' : 'unsigned';
    const uid  = c.UserID;
    // امضا
    let sigImg = '';
    if (ap && sigs[uid]) {
      sigImg = `<img src="${sigs[uid]}" class="vpf-sig-img" alt="امضا">`;
    }
    return `<div class="vpf-cell ${cls}">
      <div class="vpf-lvl">${lbl}</div>
      <div class="vpf-name">${name}</div>
      ${dt ? `<div class="vpf-dt">🕐 ${dt}</div>` : ''}
      ${sigImg ? sigImg : `<div class="vpf-sig">${ap ? '✅ تأیید شده' : 'مهر و امضا'}</div>`}
    </div>`;
  }).join('');

  if (!cells) cells = '<div class="vpf-cell unsigned"><div class="vpf-lvl">تأییدکننده‌ای تعریف نشده</div></div>';

  footer.innerHTML = `
    <div class="vpf-title">✅ وضعیت تأیید — ${d.dept_name} — ${year} ${mn}</div>
    <div class="vpf-grid">${cells}</div>`;
  footer.className = 'vprint-footer visible';
}

function closeView() {
  document.getElementById('viewModal').classList.remove('open');
  _vCtx = null;
}

function printViewModal() { window.print(); }

async function approveFromView() {
  if (!_vCtx || _vCtx.src !== 'pending') return;
  const row = _vCtx.row;
  const d   = _vCtx.data;
  if (!d || !d.my_level_no) { toast('⛔ اطلاعات تأیید در دسترس نیست', 'er'); return; }

  document.getElementById('mDepId').value  = row.dep_id;
  document.getElementById('mYear').value   = row.year;
  document.getElementById('mMonth').value  = row.month;
  document.getElementById('mLevel').value  = d.my_level_no;
  document.getElementById('mAction').value = 'approve';
  document.getElementById('mInfo').textContent = row.nam_bakhsh + ' — ' + MONTHS[row.month - 1] + ' ' + row.year;
  document.getElementById('mNote').value   = '';
  document.getElementById('mTitle').textContent = '✅ تأیید شیفت‌بندی';
  document.getElementById('mBtn').textContent   = '✅ ثبت تأیید';
  document.getElementById('mBtn').className     = 'btn btn-green';

  closeView();
  document.getElementById('confirmModal').classList.add('open');
}

/* ──── Modal تأیید/لغو ──── */
function openConfirm(idx) {
  const row = _pending[idx];
  const mn  = MONTHS[row.month - 1] || row.month;
  document.getElementById('mDepId').value  = row.dep_id;
  document.getElementById('mYear').value   = row.year;
  document.getElementById('mMonth').value  = row.month;
  document.getElementById('mLevel').value  = row.level_no;
  document.getElementById('mAction').value = 'approve';
  document.getElementById('mInfo').textContent  = row.nam_bakhsh + ' — ' + mn + ' ' + row.year;
  document.getElementById('mNote').value   = '';
  document.getElementById('mTitle').textContent = '✅ تأیید شیفت‌بندی';
  document.getElementById('mBtn').textContent   = '✅ ثبت تأیید';
  document.getElementById('mBtn').className     = 'btn btn-green';
  document.getElementById('confirmModal').classList.add('open');
}

function openRevoke(idx) {
  const row = _approved[idx];
  const mn  = MONTHS[row.month - 1] || row.month;
  document.getElementById('mDepId').value  = row.dep_id;
  document.getElementById('mYear').value   = row.year;
  document.getElementById('mMonth').value  = row.month;
  document.getElementById('mLevel').value  = row.level_no;
  document.getElementById('mAction').value = 'revoke';
  document.getElementById('mInfo').textContent  = row.nam_bakhsh + ' — ' + mn + ' ' + row.year;
  document.getElementById('mNote').value   = '';
  document.getElementById('mTitle').textContent = '↩️ لغو تأیید';
  document.getElementById('mBtn').textContent   = '↩️ لغو تأیید';
  document.getElementById('mBtn').className     = 'btn btn-red';
  document.getElementById('confirmModal').classList.add('open');
}

function closeConfirm() { document.getElementById('confirmModal').classList.remove('open'); }

async function submitAction() {
  const action = document.getElementById('mAction').value;
  const url    = '/module/manager/shift_review/' + (action === 'approve' ? 'approve' : 'revoke');
  const btn    = document.getElementById('mBtn');
  btn.disabled = true;
  try {
    await apiPost(url, {
      dep_id:   document.getElementById('mDepId').value,
      year:     document.getElementById('mYear').value,
      month:    document.getElementById('mMonth').value,
      level_no: document.getElementById('mLevel').value,
      note:     document.getElementById('mNote').value,
    });
    closeConfirm();
    await loadAll();
    toast(action === 'approve' ? '✅ تأیید با موفقیت ثبت شد' : '↩️ تأیید لغو شد');
  } catch(e) { toast('⛔ ' + e.message, 'er'); }
  finally { btn.disabled = false; }
}

function sw(jy, jm, jd) {
  const [gy,gm,gd] = j2g(jy,jm,jd);
  return [1,2,3,4,5,6,0][new Date(gy,gm-1,gd).getDay()];
}
function j2g(jy,jm,jd){
  let a=jy-979,b=jm-1,c=jd-1,n=365*a+(~~(a/33))*8+~~(((a%33)+3)/4);
  for(let i=0;i<b;i++) n+=[31,31,31,31,31,31,30,30,30,30,30,29][i];
  n+=c; let g=n+79,gy=1600+400*~~(g/146097); g%=146097;
  let lp=true;
  if(g>=36525){g--;gy+=100*~~(g/36524);g%=36524;if(g>=365)g++;else lp=false;}
  gy+=4*~~(g/1461); g%=1461;
  if(g>=366){lp=false;g--;gy+=~~(g/365);g%=365;}
  const dm=[31,lp?29:28,31,30,31,30,31,31,30,31,30,31];
  let gm=0,gd_=0;
  for(let i=0;i<12;i++){if(g<dm[i]){gm=i+1;gd_=g+1;break;}g-=dm[i];}
  return [gy,gm,gd_];
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('confirmModal').addEventListener('click', e => {
    if (e.target === document.getElementById('confirmModal')) closeConfirm();
  });
  document.getElementById('viewModal').addEventListener('click', e => {
    if (e.target === document.getElementById('viewModal')) closeView();
  });
  loadAll();
});
"""

