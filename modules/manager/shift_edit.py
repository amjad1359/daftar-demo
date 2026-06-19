"""
modules/manager/shift_edit.py — فرم مستقل ویرایش شیفت
ویژگی‌ها:
  - همیشه در حالت ویرایش (بدون محدودیت تأیید)
  - بدون بخش تأیید / لغو تأیید
  - کاملاً جدا از shifts_form.py
"""

import json, logging, secrets, jdatetime
from typing import Optional
from datetime import datetime
from models.database import query

logger = logging.getLogger(__name__)

PERSIAN_MONTHS = [
    'فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور',
    'مهر','آبان','آذر','دی','بهمن','اسفند'
]
WEEKDAY_SHORT = ['ش','ی','د','س','چ','پ','ج']

# ════════════════════ helpers ════════════════════
def get_jalali_days(year, month):
    if month <= 6:  return 31
    if month <= 11: return 30
    try: jdatetime.date(year, 12, 30); return 30
    except ValueError: return 29

def _safe_int(v, name='مقدار'):
    try: return int(v)
    except (TypeError, ValueError): raise ValueError(f'مقدار نامعتبر برای «{name}»')

def _require_fields(form_data, *fields):
    result = {}
    for f in fields:
        val = form_data.get(f)
        if val is None or str(val).strip() == '':
            raise ValueError(f'فیلد اجباری «{f}» ارسال نشده است')
        result[f] = val
    return result

def _csrf_token():
    try:
        from flask import session as _s
        if '_csrf_token' not in _s:
            _s['_csrf_token'] = secrets.token_hex(32)
        return _s['_csrf_token']
    except Exception:
        return ''

# ════════════════════ API (مستقل) ════════════════════
def _personnel_by_dep(dep_id):
    rows = query("""
        SELECT DISTINCT p.ID_person, p.nam, p.famil
        FROM tbl_person p
        JOIN tbl_sazema_person s ON p.ID_person = s.nam_person
        WHERE s.nam_bakhsh=%s AND s.payani_sazmandehi=0 AND p.isActiv=1
        ORDER BY p.famil, p.nam
    """, (dep_id,), fetch_all=True) or []
    return {'success': True, 'personnel': rows}

def _assignments(year, month, dep_id):
    if not year or not month:
        return {'success': False, 'message': 'سال و ماه الزامی هستند'}
    try:
        year  = _safe_int(year, 'سال')
        month = _safe_int(month, 'ماه')
        pr = _personnel_by_dep(dep_id)
        if not pr['success']: return pr
        pids = [r['ID_person'] for r in pr['personnel']]
        days = get_jalali_days(year, month)
        if not pids:
            return {'success': True, 'assignments': {}, 'extras': {}, 'month_days': days}
        s_date = int(f"{year}{month:02d}01")
        e_date = int(f"{year}{month:02d}{days:02d}")
        ph = ','.join(['%s'] * len(pids))
        rows = query(f"""
            SELECT ID_person, shift_date, ID_onvan_shift, is_extra
            FROM tbl_personnel_shifts
            WHERE ID_person IN ({ph}) AND shift_date BETWEEN %s AND %s
        """, (*pids, s_date, e_date), fetch_all=True) or []
        assigns, extras = {}, {}
        for r in rows:
            key = f"{r['ID_person']}_{r['shift_date']}"
            if r['is_extra']: extras.setdefault(key, []).append(r['ID_onvan_shift'])
            else: assigns[key] = r['ID_onvan_shift']
        return {'success': True, 'assignments': assigns, 'extras': extras, 'month_days': days}
    except Exception:
        logger.exception('خطا در _assignments')
        return {'success': False, 'message': 'خطای داخلی سرور'}

def save_assignment_force(user, form_data):
    """ذخیره شیفت اصلی – همیشه با force_edit=True"""
    try:
        f = _require_fields(form_data, 'person_id', 'shift_date', 'dep_id')
        pid  = _safe_int(f['person_id'], 'person_id')
        date = _safe_int(f['shift_date'], 'shift_date')
        dep_id = _safe_int(f['dep_id'], 'dep_id')
        sid  = form_data.get('shift_id') or None
        uid  = user.get('UserID')

        if sid:
            sid  = _safe_int(sid, 'shift_id')
            old  = query("SELECT ID_onvan_shift FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date=%s AND is_extra=0",
                         (pid, date), fetch_one=True)
            if old:
                query("UPDATE tbl_personnel_shifts SET ID_onvan_shift=%s,assigned_by=%s,zaman_sabt=NOW() WHERE ID_person=%s AND shift_date=%s AND is_extra=0",
                      (sid, uid, pid, date), commit=True)
            else:
                query("INSERT INTO tbl_personnel_shifts (ID_person,shift_date,ID_onvan_shift,is_extra,assigned_by,zaman_sabt) VALUES (%s,%s,%s,0,%s,NOW())",
                      (pid, date, sid, uid), commit=True)
        else:
            query("DELETE FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date=%s AND is_extra=0",
                  (pid, date), commit=True)
        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در save_assignment_force')
        return {'success': False, 'message': 'خطای داخلی سرور'}

def bulk_save_force(user, form_data):
    try:
        f = _require_fields(form_data, 'person_id','year','month','start_day','end_day','dep_id')
        pid   = _safe_int(f['person_id'], 'person_id')
        year  = _safe_int(f['year'], 'year')
        month = _safe_int(f['month'], 'month')
        sd    = _safe_int(f['start_day'], 'start_day')
        ed    = _safe_int(f['end_day'], 'end_day')
        dep_id = _safe_int(f['dep_id'], 'dep_id')
        sid   = form_data.get('shift_id') or None
        uid   = user.get('UserID')

        if sd > ed:
            return {'success': False, 'message': 'روز شروع باید کوچکتر باشد'}
        maxd  = get_jalali_days(year, month)
        sd, ed = max(1, min(sd, maxd)), max(1, min(ed, maxd))
        dates = [int(f"{year}{month:02d}{d:02d}") for d in range(sd, ed + 1)]
        if not dates: return {'success': True}
        ph = ','.join(['%s'] * len(dates))
        query(f"DELETE FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date IN ({ph}) AND is_extra=0",
              (pid, *dates), commit=True)
        if sid and sid != 'DELETE':
            sid = _safe_int(sid, 'shift_id')
            vals = ','.join(['(%s,%s,%s,0,%s,NOW())'] * len(dates))
            params = []
            for d in dates: params.extend([pid, d, sid, uid])
            query(f"INSERT INTO tbl_personnel_shifts (ID_person,shift_date,ID_onvan_shift,is_extra,assigned_by,zaman_sabt) VALUES {vals}",
                  params, commit=True)
        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در bulk_save_force')
        return {'success': False, 'message': 'خطای داخلی سرور'}

def extra_save_force(user, form_data):
    try:
        f = _require_fields(form_data, 'person_id','shift_date','shift_id','dep_id')
        pid = _safe_int(f['person_id'], 'person_id')
        date= _safe_int(f['shift_date'], 'shift_date')
        sid = _safe_int(f['shift_id'], 'shift_id')
        dep_id = _safe_int(f['dep_id'], 'dep_id')
        uid = user.get('UserID')
        query("INSERT INTO tbl_personnel_shifts (ID_person,shift_date,ID_onvan_shift,is_extra,assigned_by,zaman_sabt) VALUES (%s,%s,%s,1,%s,NOW())",
              (pid, date, sid, uid), commit=True)
        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در extra_save_force')
        return {'success': False, 'message': 'خطای داخلی سرور'}

def extra_delete_force(user, form_data):
    try:
        f = _require_fields(form_data, 'person_id','shift_date','shift_id','dep_id')
        pid = _safe_int(f['person_id'], 'person_id')
        date= _safe_int(f['shift_date'], 'shift_date')
        sid = _safe_int(f['shift_id'], 'shift_id')
        dep_id = _safe_int(f['dep_id'], 'dep_id')
        uid = user.get('UserID')
        query("DELETE FROM tbl_personnel_shifts WHERE ID_person=%s AND shift_date=%s AND ID_onvan_shift=%s AND is_extra=1 LIMIT 1",
              (pid, date, sid), commit=True)
        return {'success': True}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception:
        logger.exception('خطا در extra_delete_force')
        return {'success': False, 'message': 'خطای داخلی سرور'}

# ════════════════════ HTML ════════════════════
_SHIFT_EDIT_CSS = """
:root{--primary:#0f766e;--success:#10b981;--danger:#ef4444;--warning:#f59e0b;
  --border:#cbd5e1;--bg:#f8fafc;--text:#1e293b;--radius:8px;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:Tahoma,'Segoe UI',sans-serif;direction:rtl;}

.container{padding:14px;max-width:100%;}
.header{background:linear-gradient(135deg,#b45309,#d97706);color:white;
  padding:16px 20px;border-radius:12px;
  display:flex;justify-content:space-between;align-items:center;
  margin-bottom:12px;gap:10px;flex-wrap:wrap;}
.header h2{font-size:15px;}

.controls{background:white;padding:10px 14px;border-radius:var(--radius);
  display:flex;gap:10px;align-items:center;margin-bottom:10px;
  border:1px solid var(--border);flex-wrap:wrap;}
.controls label{font-weight:bold;font-size:13px;white-space:nowrap;}
.controls select{padding:6px 10px;border:1px solid var(--border);border-radius:6px;font-size:13px;min-width:90px;}

.btn{padding:7px 14px;border-radius:var(--radius);border:none;cursor:pointer;
  font-weight:bold;color:white;font-size:13px;transition:filter .15s;display:inline-flex;align-items:center;gap:5px;}
.btn:hover{filter:brightness(.9);}
.btn-green{background:var(--success);}
.btn-gray{background:#64748b;}
.btn-ghost{background:rgba(255,255,255,.18);color:white;border:1px solid rgba(255,255,255,.4);}
.btn-purple{background:#7c3aed;}

.table-wrapper{overflow-x:auto;background:white;border:1px solid var(--border);
  border-radius:var(--radius);max-height:68vh;}
.shift-table{width:100%;border-collapse:collapse;font-size:12px;}
.shift-table th,.shift-table td{border:1px solid var(--border);padding:4px 3px;text-align:center;min-width:54px;vertical-align:top;}
.shift-table th{background:#f1f5f9;position:sticky;top:0;z-index:2;padding:6px 3px;white-space:nowrap;}
.shift-table th .day-num{font-size:13px;font-weight:bold;line-height:1.2;}
.shift-table th .day-wd{font-size:10px;color:#64748b;font-weight:normal;}
.shift-table th.friday .day-num{color:#dc2626;}
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

.toast-box{position:fixed;top:14px;left:50%;transform:translateX(-50%);z-index:10000;
  display:flex;flex-direction:column;gap:8px;min-width:260px;}
.toast{padding:10px 18px;border-radius:10px;color:white;font-weight:600;font-size:13px;
  box-shadow:0 6px 18px rgba(0,0,0,.18);animation:tsd .25s ease;}
.toast.s{background:linear-gradient(135deg,#059669,#10b981);}
.toast.e{background:linear-gradient(135deg,#dc2626,#ef4444);}
@keyframes tsd{from{opacity:0;transform:translateY(-12px);}to{opacity:1;transform:translateY(0);}}

.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:200;align-items:center;justify-content:center;}
.modal.open{display:flex;}
.modal-box{background:white;padding:22px;border-radius:14px;width:95%;max-width:440px;box-shadow:0 20px 50px rgba(0,0,0,.2);}
.modal-box h3{margin-bottom:4px;}
.modal-box label{display:block;margin-top:12px;margin-bottom:4px;font-weight:bold;font-size:13px;}
.modal-box select,.modal-box textarea{width:100%;padding:9px;border:1px solid var(--border);border-radius:6px;font-size:13px;}
.modal-box textarea{resize:vertical;font-family:inherit;}
.modal-actions{margin-top:18px;display:flex;gap:10px;}

.print-only{display:none;}
.print-title{font-size:14px;font-weight:bold;text-align:center;padding:6px 0 8px;color:#0f766e;border-bottom:2px solid #0f766e;margin-bottom:8px;}

@media print {
  @page { size: A4 landscape; margin: 8mm 6mm; }
  .no-print { display: none !important; }
  .print-only { display: block !important; }
  body { background: white !important; font-size: 10px; }
  .container { padding: 0 !important; }
  .table-wrapper { max-height: none !important; border: none !important; overflow: visible !important; }
  .shift-table { font-size: 8.5px !important; width: 100% !important; table-layout: fixed; }
  .shift-table th, .shift-table td { min-width: 0 !important; padding: 2px 1px !important; word-break: break-all; }
  .shift-table th { position: static !important; }
  .shift-table td:first-child { position: static !important; }
  .shift-select { display: none !important; }
  .cell-print-val { display: block !important; font-size: 8px; font-weight: bold; border-radius: 2px; padding: 1px 2px; text-align: center; }
  .inline-add, .btn-plus, .extra-sel, .rm-btn, .action-icon { display: none !important; }
  .extra-badge { font-size: 7px !important; padding: 1px 2px !important; }
  thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
}
"""

# ════════════════════ JS ════════════════════
_SHIFT_EDIT_JS = r"""
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

function onDeptChange() {
    const sel = document.getElementById('deptSelector');
    if (!sel) return;
    currentDepId = parseInt(sel.value);
    const name = sel.options[sel.selectedIndex].text;
    document.getElementById('deptNameHeader').textContent = name;
    loadGrid();
}

async function loadGrid() {
    setLoading(true);
    const year  = +document.getElementById('yearSel').value;
    const month = +document.getElementById('monthSel').value;
    try {
        const [pd, ad] = await Promise.all([
            fetch(`/module/manager/shifts_edit/api/personnel?dep_id=${currentDepId}`).then(r => r.json()),
            fetch(`/module/manager/shifts_edit/api/assignments?dep_id=${currentDepId}&year=${year}&month=${month}`).then(r => r.json())
        ]);
        if (!pd.success) throw new Error(pd.message);
        if (!ad.success) throw new Error(ad.message);

        const personnel = pd.personnel ?? [];
        const assigns   = ad.assignments ?? {};
        const extras    = ad.extras ?? {};
        const days      = ad.month_days ?? 30;

        populateDays('bulkStart', days);
        populateDays('bulkEnd', days);

        const hCells = Array.from({length:days}, (_, i) => {
            const d  = i + 1;
            const wd = _shamsiWeekday(year, month, d);
            const cls = wd===6?'friday':wd===5?'thursday':'';
            return `<th class="${cls}"><div class="day-num">${d}</div><div class="day-wd">${WD_SHORT[wd]}</div></th>`;
        }).join('');
        document.getElementById('gridHead').innerHTML = `<tr><th>پرسنل / روز</th>${hCells}</tr>`;

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
                return `<td style="background:${bg};">
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
    } catch(e) {
        toast('⛔ ' + e.message, 'e');
    } finally { setLoading(false); }
}

// ════════ ذخیره‌سازی ════════
async function saveMain(sel) {
    const pid = sel.dataset.pid, date = sel.dataset.date, shiftId = sel.value;
    const td  = sel.closest('td');
    try {
        await api('/module/manager/shifts_edit/api/save', {person_id:pid, shift_date:date, shift_id:shiftId, dep_id:currentDepId});
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
        await api('/module/manager/shifts_edit/api/extra', {person_id:pid, shift_date:date, shift_id:shiftId, dep_id:currentDepId});
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
        await api('/module/manager/shifts_edit/api/extra/delete', {person_id:pid, shift_date:date, shift_id:shiftId, dep_id:currentDepId});
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
        await api('/module/manager/shifts_edit/api/bulk_save', {
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
document.querySelectorAll('.modal').forEach(m => m.addEventListener('click', e => {
    if (e.target === m) closeModal(m.id);
}));
"""

# ════════════════════ صفحه ════════════════════
def get_shifts_edit_form(user):
    user_id = user.get('UserID')
    from flask import session as flask_session

    user_depts = query("""
        SELECT d.ID_nam_bakhsh AS id, d.nam_bakhsh AS name
        FROM tbl_user_depts ud
        JOIN tbl_bakhsh d ON ud.dep_id = d.ID_nam_bakhsh
        WHERE ud.user_id = %s
        ORDER BY d.nam_bakhsh
    """, (user_id,), fetch_all=True) or []

    if not user_depts:
        return '<div style="padding:60px;text-align:center;color:#dc2626;"><h2>⛔ دسترسی محدود</h2></div>'

    default_dep = user_depts[0]['id']
    if 'shift_dep_id' in flask_session and any(d['id'] == flask_session['shift_dep_id'] for d in user_depts):
        default_dep = flask_session['shift_dep_id']

    dept_options = ''.join(
        f'<option value="{d["id"]}" {"selected" if d["id"]==default_dep else ""}>{d["name"]}</option>'
        for d in user_depts
    )

    dept_info = query("SELECT nam_bakhsh FROM tbl_bakhsh WHERE ID_nam_bakhsh=%s", (default_dep,), fetch_one=True)
    dept_name = dept_info['nam_bakhsh'] if dept_info else 'نامشخص'

    shift_titles = query("SELECT ID_onvan_shift, shift_code, color_code FROM onvan_shift ORDER BY ID_onvan_shift", fetch_all=True) or []
    shift_json = json.dumps(shift_titles, ensure_ascii=False)
    shift_sel_rows = ''.join(f'<option value="{s["ID_onvan_shift"]}">{s["shift_code"]}</option>' for s in shift_titles)

    csrf = _csrf_token()

    today = jdatetime.date.today()
    cy, cm = today.year, today.month
    year_opts = ''.join(f'<option value="{y}" {"selected" if y==cy else ""}>{y}</option>' for y in range(cy-1, cy+2))
    month_opts = ''.join(f'<option value="{m}" {"selected" if m==cm else ""}">{PERSIAN_MONTHS[m-1]}</option>' for m in range(1,13))

    return f'''<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="csrf-token" content="{csrf}">
<title>ویرایش شیفت – {dept_name}</title>
<style>{_SHIFT_EDIT_CSS}</style>
</head>
<body>
<div class="toast-box" id="toastBox"></div>
<div class="container">
<div class="header">
    <div><h2>🔧 ویرایش شیفت‌بندی — <span id="deptNameHeader">{dept_name}</span></h2></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
        <select id="deptSelector" class="no-print" onchange="onDeptChange()" style="padding:6px 10px;border-radius:6px;font-weight:bold;">
            {dept_options}
        </select>
        <button class="btn btn-purple no-print" onclick="window.print()">🖨️ چاپ</button>
        <a href="/module/manager" class="btn btn-ghost no-print">⬅️ بازگشت</a>
    </div>
</div>

<div class="controls no-print">
    <label>سال:</label><select id="yearSel" onchange="loadGrid()">{year_opts}</select>
    <label>ماه:</label><select id="monthSel" onchange="loadGrid()">{month_opts}</select>
    <span id="loadTxt" style="display:none;color:var(--primary);font-weight:bold;">⏳...</span>
</div>

<div class="print-only print-title" id="printTitle"></div>

<div class="table-wrapper">
    <table class="shift-table">
        <thead id="gridHead"></thead>
        <tbody id="gridBody"></tbody>
    </table>
</div>

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

</div>

<script>
const SHIFTS = {shift_json};
let currentDepId = {default_dep};
{_SHIFT_EDIT_JS}
</script>
</body>
</html>'''

