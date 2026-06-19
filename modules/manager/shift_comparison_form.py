"""
modules/manager/shift_comparison_form.py — نسخهٔ نهایی
مقایسهٔ برنامهٔ شیفت با حضور واقعی
ویژگی‌ها:
  ✅ نمایش چند شیفت در یک روز (لیست)
  ✅ تاریخ دقیق از shift_namt.dat_sabt
  ✅ رنگ متن خودکار بر اساس روشنایی پس‌زمینه
  ✅ صفحه‌بندی، چاپ، راهنما، خلاصهٔ آماری
"""

import json
from datetime import timedelta
import jdatetime
from models.database import query

PERSIAN_MONTHS = [
    'فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور',
    'مهر','آبان','آذر','دی','بهمن','اسفند'
]

# ═══════════════════════ تابع‌های کمکی ═══════════════════════

def _time_to_seconds(t):
    if not t:
        return 0
    if isinstance(t, int):
        return t
    if isinstance(t, timedelta):
        return int(t.total_seconds())
    s = str(t).strip()
    parts = s.split(':')
    try:
        if len(parts) >= 2:
            return int(parts[0]) * 3600 + int(parts[1]) * 60
    except (ValueError, IndexError):
        pass
    return 0


def _secs_to_hhmm(secs):
    if not secs:
        return '—'
    secs = int(secs)
    h = abs(secs) // 3600
    m = (abs(secs) % 3600) // 60
    sign = '-' if secs < 0 else ''
    return f"{sign}{h}:{m:02d}"


def get_jalali_days(year, month):
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    try:
        jdatetime.date(year, 12, 30)
        return 30
    except ValueError:
        return 29


def _shamsi_weekday_py(year, month, day):
    try:
        return jdatetime.date(year, month, day).weekday()
    except Exception:
        return 0


def _fetch_personnel(dept_id):
    return query("""
        SELECT DISTINCT p.ID_person, p.nam, p.famil
        FROM   tbl_person p
        JOIN   tbl_sazema_person s ON p.ID_person = s.nam_person
        WHERE  s.nam_bakhsh = %s AND p.isActiv = 1
          AND (s.payani_sazmandehi = 0 OR s.payani_sazmandehi IS NULL)
        ORDER  BY p.famil, p.nam
    """, (dept_id,), fetch_all=True) or []


def _fetch_shifts():
    rows = query(
        "SELECT ID_onvan_shift, shift_code, color_code, time_duration "
        "FROM onvan_shift ORDER BY ID_onvan_shift",
        fetch_all=True) or []
    shift_map = {}
    for s in rows:
        sid = str(s['ID_onvan_shift'])
        shift_map[sid] = {
            'shift_code': s['shift_code'] or '',
            'color_code': s['color_code'] or '#94a3b8',
            'duration':   _time_to_seconds(s['time_duration']),
        }
    return shift_map


def _fetch_planned(pids, year, month, days):
    if not pids:
        return {}, {}
    s_date = int(f"{year}{month:02d}01")
    e_date = int(f"{year}{month:02d}{days:02d}")
    ph     = ','.join(['%s'] * len(pids))
    rows   = query(
        f"SELECT ID_person, shift_date, ID_onvan_shift, is_extra "
        f"FROM tbl_personnel_shifts "
        f"WHERE ID_person IN ({ph}) AND shift_date BETWEEN %s AND %s",
        (*pids, s_date, e_date), fetch_all=True) or []
    planned, extras = {}, {}
    for r in rows:
        key = f"{r['ID_person']}_{r['shift_date']}"
        if r['is_extra']:
            extras.setdefault(key, []).append(str(r['ID_onvan_shift']))
        else:
            planned[key] = str(r['ID_onvan_shift'])
    return planned, extras


def _fetch_actual(dept_id, pids, year, month, days, shift_map):
    """حضور واقعی – تاریخ از shift_namt.dat_sabt"""
    if not pids:
        return {}
    s_date = int(f"{year}{month:02d}01")
    e_date = int(f"{year}{month:02d}{days:02d}")

    rows = query("""
        SELECT h.id_person, sn.dat_sabt, h.rizshift
        FROM   tbl_hozor h
        JOIN   shift_namt sn ON h.nam_shift = sn.ID_shift
        WHERE  h.nam_bakhsh = %s
          AND  h.ispresent  = 1
          AND  sn.dat_sabt BETWEEN %s AND %s
    """, (dept_id, s_date, e_date), fetch_all=True) or []

    actual = {}
    for r in rows:
        pid = r['id_person']
        if pid not in pids:
            continue
        date_int = r['dat_sabt']
        rid = r['rizshift']
        if rid is not None:
            sid = str(rid)
            if sid in shift_map:
                key = f"{pid}_{date_int}"
                if key not in actual:
                    actual[key] = []
                if sid not in actual[key]:
                    actual[key].append(sid)
    return actual


# ═══════════════════════ صفحه HTML ═══════════════════════

def get_shift_comparison_page(user):
    user_id = user.get('UserID', 0)
    dept_id = user.get('dep_id')

    if not dept_id:
        rec = query("SELECT dep_id FROM users WHERE UserID=%s", (user_id,), fetch_one=True)
        if rec and rec.get('dep_id'):
            dept_id = rec['dep_id']

    if not dept_id:
        return ('<div style="padding:60px;text-align:center;color:#dc2626;">'
                '<h2>⛔ بخش شما در پروفایل مشخص نیست</h2></div>')

    dept_info = query(
        "SELECT nam_bakhsh FROM tbl_bakhsh WHERE ID_nam_bakhsh=%s",
        (dept_id,), fetch_one=True)
    dept_name = dept_info['nam_bakhsh'] if dept_info else 'نامشخص'

    user_depts = query("""
        SELECT d.ID_nam_bakhsh, d.nam_bakhsh
        FROM   tbl_user_depts ud
        JOIN   tbl_bakhsh d ON ud.dep_id = d.ID_nam_bakhsh
        WHERE  ud.user_id = %s
        ORDER  BY d.nam_bakhsh
    """, (user_id,), fetch_all=True) or []
    if not user_depts:
        user_depts = [{'ID_nam_bakhsh': dept_id, 'nam_bakhsh': dept_name}]

    dept_options = ''.join(
        f'<option value="{d["ID_nam_bakhsh"]}"'
        f'{"selected" if d["ID_nam_bakhsh"] == dept_id else ""}>'
        f'{d["nam_bakhsh"]}</option>'
        for d in user_depts
    )

    today = jdatetime.date.today()
    cy, cm = today.year, today.month
    year_opts  = ''.join(
        f'<option value="{y}"{"selected" if y==cy else ""}>{y}</option>'
        for y in range(cy - 1, cy + 2))
    month_opts = ''.join(
        f'<option value="{m}"{"selected" if m==cm else ""}>'
        f'{PERSIAN_MONTHS[m-1]}</option>'
        for m in range(1, 13))

    months_js = json.dumps(PERSIAN_MONTHS, ensure_ascii=False)
    PAGE_CSS = _PAGE_CSS
    PAGE_JS  = _PAGE_JS.replace('__MONTHS_JSON__', months_js)

    return (
        '<!DOCTYPE html><html dir="rtl" lang="fa"><head>'
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<title>مقایسه شیفت و حضور</title>'
        '<style>' + PAGE_CSS + '</style>'
        '</head><body>'
        '<div class="toast-wrap" id="tw"></div>'
        '<div class="page">'

        # Header
        '<div class="hdr">'
        '<div><h2>⚖️ مقایسه شیفت‌بندی و حضور</h2>'
        f'<p>🏥 {dept_name}</p></div>'
        '<div class="hdr-acts">'
        '<button class="btn btn-print" onclick="printPage()">🖨️ چاپ</button>'
        '<a href="/module/manager" class="btn btn-back">⬅️ بازگشت</a>'
        '</div></div>'

        # Controls
        '<div class="ctrl-bar">'
        '<div class="ctrl-group"><label>بخش</label>'
        f'<select id="deptSel">{dept_options}</select></div>'
        '<div class="ctrl-group"><label>سال</label>'
        f'<select id="yearSel">{year_opts}</select></div>'
        '<div class="ctrl-group"><label>ماه</label>'
        f'<select id="monthSel">{month_opts}</select></div>'
        '<button class="btn btn-apply" onclick="loadActive()">🔄 نمایش</button>'
        '</div>'

        # Legend
        '<div class="legend" id="legend"></div>'

        # Tabs
        '<div class="tabs">'
        '<button class="tab active" data-tab="t1" onclick="switchTab(this)">🗓 برنامه شیفت</button>'
        '<button class="tab" data-tab="t2" onclick="switchTab(this)">📋 حضور واقعی</button>'
        '<button class="tab" data-tab="t3" onclick="switchTab(this)">⚖️ مقایسه مغایرت</button>'
        '</div>'

        '<div id="t1" class="tab-pane active"><div class="tbl-wrap" id="g1"></div></div>'
        '<div id="t2" class="tab-pane"><div class="tbl-wrap" id="g2"></div></div>'
        '<div id="t3" class="tab-pane">'
        '<div class="tbl-wrap" id="g3"></div>'
        '<div id="summary" class="summary"></div>'
        '</div>'

        '</div>'  # /page
        '<iframe id="pf" style="display:none"></iframe>'
        '<script>' + PAGE_JS + '</script>'
        '</body></html>'
    )


# ═══════════════════════ CSS ═══════════════════════

_PAGE_CSS = (
    ":root{"
    "--pri:#1e3a8a;--pri2:#3b82f6;--suc:#10b981;--dan:#ef4444;"
    "--war:#f59e0b;--pur:#7c3aed;--bdr:#e2e8f0;--bg:#f1f5f9;"
    "--card:#fff;--txt:#1e293b;--muted:#64748b;--R:10px;"
    "}"
    "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}"
    "body{font-family:Tahoma,'Segoe UI',sans-serif;direction:rtl;"
    "background:var(--bg);color:var(--txt);min-height:100vh;}"

    ".page{max-width:1600px;margin:0 auto;padding:14px 16px;}"

    # Header
    ".hdr{background:linear-gradient(135deg,#0f4c81,#1e3a8a,#2563eb);"
    "color:#fff;border-radius:16px;padding:18px 24px;"
    "display:flex;justify-content:space-between;align-items:center;"
    "flex-wrap:wrap;gap:12px;margin-bottom:14px;"
    "box-shadow:0 8px 28px rgba(30,58,138,.3);}"
    ".hdr h2{font-size:18px;font-weight:700;margin:0;}"
    ".hdr p{font-size:12px;opacity:.8;margin:3px 0 0;}"
    ".hdr-acts{display:flex;gap:8px;}"

    # Buttons
    ".btn{display:inline-flex;align-items:center;gap:5px;padding:8px 16px;"
    "border:none;border-radius:8px;font-size:13px;font-weight:600;"
    "cursor:pointer;font-family:inherit;transition:.18s;white-space:nowrap;}"
    ".btn:hover{filter:brightness(.9);transform:translateY(-1px);}"
    ".btn-back{background:rgba(255,255,255,.15);color:#fff;"
    "border:1px solid rgba(255,255,255,.3);text-decoration:none;}"
    ".btn-print{background:#7c3aed;color:#fff;}"
    ".btn-apply{background:#0f766e;color:#fff;padding:9px 22px;}"

    # Controls
    ".ctrl-bar{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;"
    "background:#fff;border:1px solid var(--bdr);border-radius:var(--R);"
    "padding:12px 16px;margin-bottom:12px;"
    "box-shadow:0 2px 8px rgba(0,0,0,.04);}"
    ".ctrl-group{display:flex;flex-direction:column;gap:4px;}"
    ".ctrl-group label{font-size:11px;font-weight:700;color:var(--muted);}"
    ".ctrl-group select{padding:7px 10px;border:2px solid var(--bdr);"
    "border-radius:7px;font-size:13px;font-family:inherit;"
    "transition:.18s;background:#fff;min-width:120px;}"
    ".ctrl-group select:focus{border-color:var(--pri2);outline:none;}"

    # Legend
    ".legend{display:flex;flex-wrap:wrap;gap:8px;padding:8px 12px;"
    "background:#fff;border:1px solid var(--bdr);border-radius:8px;"
    "margin-bottom:10px;min-height:36px;}"
    ".leg-item{display:flex;align-items:center;gap:5px;font-size:11px;font-weight:600;}"
    ".leg-dot{width:20px;height:20px;border-radius:4px;flex-shrink:0;}"

    # Tabs
    ".tabs{display:flex;gap:2px;border-bottom:2px solid var(--bdr);"
    "margin-bottom:10px;}"
    ".tab{padding:10px 20px;border:none;background:none;cursor:pointer;"
    "font-family:inherit;font-size:13px;font-weight:600;color:var(--muted);"
    "border-bottom:3px solid transparent;transition:.18s;}"
    ".tab:hover{color:var(--txt);}"
    ".tab.active{color:var(--pri);border-bottom-color:var(--pri);}"
    ".tab-pane{display:none;}"
    ".tab-pane.active{display:block;animation:fadeIn .25s ease;}"
    "@keyframes fadeIn{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:translateY(0);}}"

    # Table
    ".tbl-wrap{overflow-x:auto;border:1px solid var(--bdr);border-radius:10px;"
    "max-height:65vh;background:#fff;}"
    ".tbl-wrap::-webkit-scrollbar{height:6px;width:6px;}"
    ".tbl-wrap::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:4px;}"
    "table{width:100%;border-collapse:collapse;font-size:11px;}"
    "thead th{background:#1e3a8a;color:#fff;padding:6px 3px;"
    "position:sticky;top:0;z-index:3;white-space:nowrap;font-size:11px;}"
    "thead th:first-child{z-index:4;position:sticky;top:0;right:0;}"
    "tbody tr:nth-child(even){background:#f8fafc;}"
    "tbody tr:hover{background:#eff6ff;}"
    "td{border:1px solid #e8edf2;padding:3px 2px;text-align:center;"
    "vertical-align:middle;}"
    "td:first-child{position:sticky;right:0;background:inherit;"
    "font-weight:700;text-align:right;padding-right:10px;"
    "min-width:140px;max-width:160px;z-index:1;"
    "font-size:11px;white-space:nowrap;border-left:2px solid var(--bdr);}"
    "tbody tr:nth-child(even) td:first-child{background:#f8fafc;}"
    "tbody tr:hover td:first-child{background:#eff6ff;}"
    ".th-day{font-size:12px;font-weight:700;line-height:1.3;}"
    ".th-wd{font-size:9px;opacity:.8;font-weight:400;}"
    ".th-fri{color:#fca5a5;}"
    ".th-thu{color:#c4b5fd;}"
    ".col-fri{background:rgba(254,242,242,.5)!important;}"
    ".col-thu{background:rgba(245,243,255,.4)!important;}"

    # Shift chips
    ".sc{display:flex;flex-direction:column;gap:2px;min-height:18px;"
    "align-items:center;justify-content:center;}"
    ".sp{display:inline-block;border-radius:3px;padding:1px 5px;"
    "font-size:10px;font-weight:700;color:#fff;line-height:1.4;"
    "min-width:22px;text-align:center;}"
    ".sx{background:#be185d;}"

    # Comparison cells
    ".cmp-cell{display:flex;flex-direction:column;gap:1px;"
    "align-items:center;justify-content:center;padding:2px;}"
    ".cmp-plan{font-size:9px;color:#475569;}"
    ".cmp-act{font-size:10px;font-weight:700;}"
    ".diff{background:rgba(254,226,226,.6)!important;}"
    ".match{background:rgba(220,252,231,.5)!important;}"
    ".absent{background:rgba(255,247,237,.6)!important;}"

    # Summary
    ".summary{margin-top:12px;background:#fff;border:1px solid var(--bdr);"
    "border-radius:10px;padding:16px;}"
    ".sum-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin-top:12px;}"
    ".sum-card{border-radius:8px;padding:12px;text-align:center;border:1px solid var(--bdr);}"
    ".sum-val{font-size:22px;font-weight:800;}"
    ".sum-lbl{font-size:11px;color:var(--muted);margin-top:3px;font-weight:600;}"

    # Toast
    ".toast-wrap{position:fixed;top:16px;left:50%;transform:translateX(-50%);"
    "z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none;}"
    ".toast{padding:12px 20px;border-radius:10px;color:#fff;font-weight:600;"
    "font-size:13px;box-shadow:0 8px 24px rgba(0,0,0,.2);pointer-events:auto;"
    "display:flex;align-items:center;gap:8px;"
    "animation:tin .25s ease;}"
    ".tok{background:linear-gradient(135deg,#059669,#10b981);}"
    ".ter{background:linear-gradient(135deg,#dc2626,#ef4444);}"
    "@keyframes tin{from{opacity:0;transform:translateY(-10px);}to{opacity:1;transform:translateY(0);}}"

    # Spinner
    ".spin-wrap{display:flex;justify-content:center;align-items:center;"
    "padding:48px;}"
    ".spin{width:32px;height:32px;border:3px solid var(--bdr);"
    "border-top-color:var(--pri);border-radius:50%;"
    "animation:sp .7s linear infinite;}"
    "@keyframes sp{to{transform:rotate(360deg);}}"

    # Print
    "@media print{"
    "@page{size:A4 landscape;margin:6mm;}"
    "body{background:#fff;}"
    ".hdr .hdr-acts,.ctrl-bar,.tabs,.toast-wrap,.legend{display:none!important;}"
    ".tab-pane{display:block!important;}"
    ".tbl-wrap{max-height:none!important;overflow:visible!important;"
    "border:none!important;}"
    "table{font-size:8px!important;}"
    "td,th{padding:2px 1px!important;}"
    "td:first-child{min-width:80px!important;}"
    "}"

    "@media(max-width:640px){"
    ".hdr{flex-direction:column;text-align:center;gap:10px;}"
    ".ctrl-bar{flex-direction:column;}"
    ".summary .sum-grid{grid-template-columns:repeat(2,1fr);}"
    "}"
)


# ═══════════════════════ JavaScript ═══════════════════════

_PAGE_JS = r"""
const MONTHS = __MONTHS_JSON__;
const WD = ['ش','ی','د','س','چ','پ','ج'];

function sel(id){ return document.getElementById(id); }
function getP(){
  return {
    dept:  sel('deptSel').value,
    year:  +sel('yearSel').value,
    month: +sel('monthSel').value
  };
}

function toast(msg, ok=true){
  const w = sel('tw'), d = document.createElement('div');
  d.className = 'toast ' + (ok?'tok':'ter');
  d.innerHTML = (ok?'✅ ':'❌ ') + msg;
  w.appendChild(d);
  setTimeout(()=>d.remove(), 4000);
}

function spin(id){ sel(id).innerHTML = '<div class="spin-wrap"><div class="spin"></div></div>'; }

function switchTab(btn){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p=>p.classList.remove('active'));
  btn.classList.add('active');
  const pane = sel(btn.dataset.tab);
  pane.classList.add('active');
  if(btn.dataset.tab==='t1') loadSchedule();
  else if(btn.dataset.tab==='t2') loadAttendance();
  else if(btn.dataset.tab==='t3') loadComparison();
}

function loadActive(){
  const activeTab = document.querySelector('.tab.active');
  if(activeTab) activeTab.click();
}

function shamsiWD(jy, jm, jd){
  const [gy,gm,gd] = j2g(jy,jm,jd);
  return [1,2,3,4,5,6,0][new Date(gy,gm-1,gd).getDay()];
}
function j2g(jy,jm,jd){
  let a=jy-979,b=jm-1,c=jd-1,n=365*a+Math.floor(a/33)*8+Math.floor(((a%33)+3)/4);
  for(let i=0;i<b;i++) n+=[31,31,31,31,31,31,30,30,30,30,30,29][i];
  n+=c; let g=n+79,gy=1600+400*Math.floor(g/146097); g%=146097;
  let lp=true;
  if(g>=36525){g--;gy+=100*Math.floor(g/36524);g%=36524;if(g>=365)g++;else lp=false;}
  gy+=4*Math.floor(g/1461); g%=1461;
  if(g>=366){lp=false;g--;gy+=Math.floor(g/365);g%=365;}
  const dm=[31,lp?29:28,31,30,31,30,31,31,30,31,30,31];
  let gm=0,gd_=0;
  for(let i=0;i<12;i++){if(g<dm[i]){gm=i+1;gd_=g+1;break;}g-=dm[i];}
  return [gy,gm,gd_];
}

function secsToHHMM(s){
  if(!s && s!==0) return '—';
  const neg = s<0; s=Math.abs(s);
  const h=Math.floor(s/3600), m=Math.floor((s%3600)/60);
  return (neg?'-':'')+h+':'+(m<10?'0':'')+m;
}

function textColor(hex){
  if(!hex || hex.length<7) return '#fff';
  const r = parseInt(hex.substring(1,3),16);
  const g = parseInt(hex.substring(3,5),16);
  const b = parseInt(hex.substring(5,7),16);
  const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
  return luminance > 150 ? '#1e293b' : '#fff';
}

function buildLegend(shiftMap){
  const lg = sel('legend');
  lg.innerHTML = Object.values(shiftMap).map(s=>{
    const bg = s.color_code || '#94a3b8';
    const tc = textColor(bg);
    return `<div class="leg-item">
       <div class="leg-dot" style="background:${bg}"></div>
       <span style="color:${tc}">${s.shift_code}</span>
     </div>`;
  }).join('');
}

function buildHeader(days, year, month){
  let h = '<tr><th style="min-width:140px;right:0;position:sticky;z-index:4;">پرسنل / روز</th>';
  for(let d=1;d<=days;d++){
    const wd = shamsiWD(year,month,d);
    const cls = wd===6?'th-fri':wd===5?'th-thu':'';
    h += `<th class="${cls}"><div class="th-day">${d}</div><div class="th-wd">${WD[wd]}</div></th>`;
  }
  return h + '</tr>';
}

function colClass(wd){ return wd===6?'col-fri':wd===5?'col-thu':''; }

/* ──────── تب ۱: برنامه شیفت ──────── */
async function loadSchedule(){
  const p = getP();
  spin('g1');
  try{
    const d = await fetch(
      `/module/manager/shift_comparison/schedule?dept=${p.dept}&year=${p.year}&month=${p.month}`
    ).then(r=>r.json());
    if(!d.success){ sel('g1').innerHTML=`<div class="spin-wrap">${d.message}</div>`; return; }
    buildLegend(d.shiftMap);

    let rows = '<thead>' + buildHeader(d.days,p.year,p.month) + '</thead><tbody>';
    d.personnel.forEach(per => {
      rows += `<tr><td>${per.name}</td>`;
      for(let day=1;day<=d.days;day++){
        const date = `${p.year}${String(p.month).padStart(2,'0')}${String(day).padStart(2,'0')}`;
        const key  = `${per.id}_${date}`;
        const sid  = d.assigns[key];
        const exs  = d.extras[key] || [];
        const s    = sid ? d.shiftMap[String(sid)] : null;
        const wd   = shamsiWD(p.year,p.month,day);
        const bg   = s ? s.color_code : '';
        const tc   = textColor(bg || '#f1f5f9');
        let inner  = '';
        if(s) inner += `<span class="sp" style="background:${s.color_code};color:${tc}">${s.shift_code}</span>`;
        exs.forEach(ex => {
          const es = d.shiftMap[String(ex)];
          if(es) inner += `<span class="sp sx" title="اضافه" style="color:${textColor(es.color_code)}">${es.shift_code}</span>`;
        });
        rows += `<td class="${colClass(wd)}" style="${bg?'background:'+bg+'22':''}">
                   <div class="sc">${inner}</div></td>`;
      }
      rows += '</tr>';
    });
    rows += '</tbody>';
    sel('g1').innerHTML = `<table>${rows}</table>`;
  } catch(e){ sel('g1').innerHTML=`<div class="spin-wrap">خطا: ${e.message}</div>`; toast(e.message,false); }
}

/* ──────── تب ۲: حضور واقعی (چند شیفت در روز) ──────── */
async function loadAttendance(){
  const p = getP();
  spin('g2');
  try{
    const d = await fetch(
      `/module/manager/shift_comparison/attendance?dept=${p.dept}&year=${p.year}&month=${p.month}`
    ).then(r=>r.json());
    if(!d.success){ sel('g2').innerHTML=`<div class="spin-wrap">${d.message}</div>`; return; }

    let rows = '<thead>' + buildHeader(d.days,p.year,p.month) + '</thead><tbody>';
    d.personnel.forEach(per => {
      rows += `<tr><td>${per.name}</td>`;
      for(let day=1;day<=d.days;day++){
        const date = `${p.year}${String(p.month).padStart(2,'0')}${String(day).padStart(2,'0')}`;
        const key  = `${per.id}_${date}`;
        const codes = d.attendance[key] || [];   // همیشه آرایه
        const wd   = shamsiWD(p.year,p.month,day);
        let inner = '';
        codes.forEach(code => {
          const color = d.shiftColors[code] || '#94a3b8';
          const tc = textColor(color);
          inner += `<span class="sp" style="background:${color};color:${tc};margin:1px;">${code}</span>`;
        });
        rows += `<td class="${colClass(wd)}">
                   <div class="sc">${inner}</div></td>`;
      }
      rows += '</tr>';
    });
    rows += '</tbody>';
    sel('g2').innerHTML = `<table>${rows}</table>`;
  } catch(e){ sel('g2').innerHTML=`<div class="spin-wrap">خطا: ${e.message}</div>`; toast(e.message,false); }
}

/* ──────── تب ۳: مقایسه مغایرت (چند شیفت) ──────── */
async function loadComparison(){
  const p = getP();
  spin('g3');
  sel('summary').innerHTML = '';
  try{
    const d = await fetch(
      `/module/manager/shift_comparison/comparison?dept=${p.dept}&year=${p.year}&month=${p.month}`
    ).then(r=>r.json());
    if(!d.success){ sel('g3').innerHTML=`<div class="spin-wrap">${d.message}</div>`; return; }

    let totalDiff=0, totalMatch=0, totalAbsent=0, totalExtra=0;
    let totalPlanSecs=0, totalActSecs=0;

    let rows = '<thead>';
    rows += '<tr><th rowspan="2" style="min-width:140px;position:sticky;right:0;z-index:4;">پرسنل</th>';
    for(let day=1;day<=d.days;day++){
      const wd=shamsiWD(p.year,p.month,day);
      const cls=wd===6?'th-fri':wd===5?'th-thu':'';
      rows += `<th class="${cls}" colspan="1"><div class="th-day">${day}</div><div class="th-wd">${WD[wd]}</div></th>`;
    }
    rows += '<th rowspan="2">ساعت<br>برنامه</th><th rowspan="2">ساعت<br>واقعی</th><th rowspan="2">اختلاف</th></tr>';
    rows += '<tr>';
    for(let day=1;day<=d.days;day++){
      rows += '<th style="font-size:8px;background:#1e40af;padding:2px;">ب/و</th>';
    }
    rows += '</tr></thead><tbody>';

    d.personnel.forEach(per => {
      let planSecs=0, actSecs=0;
      rows += `<tr><td>${per.name}</td>`;
      for(let day=1;day<=d.days;day++){
        const date  = String(p.year) + String(p.month).padStart(2,'0') + String(day).padStart(2,'0');
        const dint  = parseInt(date);
        const plannedIds = per.planned[dint] || [];
        const actualIds = per.actual[dint] || [];
        const wd    = shamsiWD(p.year,p.month,day);

        // محاسبهٔ ساعت
        plannedIds.forEach(sid => { if(d.shiftMap[String(sid)]) planSecs += d.shiftMap[String(sid)].duration; });
        actualIds.forEach(sid => { if(d.shiftMap[String(sid)]) actSecs += d.shiftMap[String(sid)].duration; });

        // تعیین وضعیت سلول (بر اساس مجموعه کدها)
        let cellCls = colClass(wd);
        if(plannedIds.length > 0 && actualIds.length > 0){
          // مقایسهٔ مجموعه‌ها: اگر عیناً برابر باشند match، وگرنه diff
          const setEqual = (a,b) => a.length===b.length && a.every(v=>b.includes(v));
          if(setEqual(plannedIds, actualIds)){ cellCls += ' match'; totalMatch++; }
          else { cellCls += ' diff'; totalDiff++; }
        } else if(plannedIds.length > 0 && actualIds.length===0){
          cellCls += ' absent'; totalAbsent++;
        } else if(plannedIds.length===0 && actualIds.length > 0){
          cellCls += ' diff'; totalExtra++;
        }

        // ساخت محتوای سلول: نمایش همهٔ کدها
        let planHtml = plannedIds.map(sid => {
          const s = d.shiftMap[String(sid)];
          if(s) return `<span class="sp" style="background:${s.color_code||'#94a3b8'};color:${textColor(s.color_code||'#94a3b8')};font-size:9px;">${s.shift_code}</span>`;
          return '';
        }).join('');
        let actHtml = actualIds.map(sid => {
          const s = d.shiftMap[String(sid)];
          if(s) return `<span class="sp" style="background:${s.color_code||'#94a3b8'};color:${textColor(s.color_code||'#94a3b8')};font-size:9px;">${s.shift_code}</span>`;
          return '';
        }).join('');
        if(!planHtml) planHtml = '<span style="font-size:9px;color:#94a3b8;">—</span>';
        if(!actHtml) actHtml = '<span style="font-size:9px;color:#94a3b8;">—</span>';

        rows += `<td class="${cellCls}">
          <div class="cmp-cell">
            <div class="cmp-plan" title="برنامه">${planHtml}</div>
            <div class="cmp-act"  title="واقعی">${actHtml}</div>
          </div></td>`;
      }
      totalPlanSecs += planSecs;
      totalActSecs  += actSecs;
      const diff = actSecs - planSecs;
      const diffColor = diff>=0 ? '#059669' : '#dc2626';
      rows += `<td style="font-weight:700;">${secsToHHMM(planSecs)}</td>
               <td style="font-weight:700;">${secsToHHMM(actSecs)}</td>
               <td style="color:${diffColor};font-weight:700;">${(diff>=0?'+':'')+secsToHHMM(diff)}</td></tr>`;
    });
    rows += '</tbody>';
    sel('g3').innerHTML = `<table>${rows}</table>`;

    const grandDiff = totalActSecs - totalPlanSecs;
    sel('summary').innerHTML = `
      <strong>📊 خلاصه ماه ${MONTHS[p.month-1]} ${p.year}</strong>
      <div class="sum-grid">
        <div class="sum-card" style="background:#d1fae5;border-color:#6ee7b7;">
          <div class="sum-val" style="color:#065f46;">${totalMatch}</div>
          <div class="sum-lbl">✅ مطابق برنامه</div>
        </div>
        <div class="sum-card" style="background:#fee2e2;border-color:#fca5a5;">
          <div class="sum-val" style="color:#dc2626;">${totalDiff}</div>
          <div class="sum-lbl">⚠️ مغایرت شیفت</div>
        </div>
        <div class="sum-card" style="background:#fef3c7;border-color:#fcd34d;">
          <div class="sum-val" style="color:#92400e;">${totalAbsent}</div>
          <div class="sum-lbl">❌ غیبت از برنامه</div>
        </div>
        <div class="sum-card" style="background:#ede9fe;border-color:#c4b5fd;">
          <div class="sum-val" style="color:#5b21b6;">${totalExtra}</div>
          <div class="sum-lbl">➕ حضور اضافه</div>
        </div>
        <div class="sum-card" style="background:#dbeafe;border-color:#93c5fd;">
          <div class="sum-val" style="color:#1e40af;">${secsToHHMM(totalPlanSecs)}</div>
          <div class="sum-lbl">🗓 کل ساعت برنامه</div>
        </div>
        <div class="sum-card" style="background:#d1fae5;border-color:#6ee7b7;">
          <div class="sum-val" style="color:#065f46;">${secsToHHMM(totalActSecs)}</div>
          <div class="sum-lbl">⏱ کل ساعت واقعی</div>
        </div>
        <div class="sum-card" style="background:${grandDiff>=0?'#d1fae5':'#fee2e2'};border-color:${grandDiff>=0?'#6ee7b7':'#fca5a5'};">
          <div class="sum-val" style="color:${grandDiff>=0?'#065f46':'#dc2626'};">${(grandDiff>=0?'+':'')+secsToHHMM(grandDiff)}</div>
          <div class="sum-lbl">⚖️ مجموع اختلاف</div>
        </div>
      </div>
      <div style="margin-top:12px;font-size:12px;color:#64748b;display:flex;gap:16px;flex-wrap:wrap;">
        <span><span style="background:#d1fae5;padding:2px 8px;border-radius:4px;">■</span> مطابق برنامه</span>
        <span><span style="background:rgba(254,226,226,.8);padding:2px 8px;border-radius:4px;">■</span> مغایرت شیفت</span>
        <span><span style="background:rgba(255,247,237,.8);padding:2px 8px;border-radius:4px;">■</span> غیبت از برنامه</span>
        <span style="font-size:11px;">ب = برنامه &nbsp;|&nbsp; و = واقعی</span>
      </div>`;
  } catch(e){ sel('g3').innerHTML=`<div class="spin-wrap">خطا: ${e.message}</div>`; toast(e.message,false); }
}

function printPage(){
  const activePane = document.querySelector('.tab-pane.active');
  if(!activePane){ toast('هیچ جدولی نمایش داده نشده',false); return; }
  const p    = getP();
  const mn   = MONTHS[p.month-1];
  const tbl  = activePane.querySelector('table');
  const smry = sel('summary')?.outerHTML || '';
  const html = `<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8">
<style>
@page{size:A4 landscape;margin:6mm;}
*{box-sizing:border-box;margin:0;padding:0;font-family:Tahoma,sans-serif;}
body{direction:rtl;font-size:8.5px;background:#fff;}
h1{font-size:13px;text-align:center;color:#1e3a8a;padding:4px 0 8px;border-bottom:2px solid #1e3a8a;margin-bottom:8px;}
table{width:100%;border-collapse:collapse;}
th,td{border:1px solid #cbd5e1;padding:2px 1px;text-align:center;font-size:8px;}
th{background:#1e3a8a;color:#fff;}
td:first-child{text-align:right;padding-right:4px;font-weight:700;background:#f8fafc;min-width:80px;}
thead{display:table-header-group;}
tr{page-break-inside:avoid;}
.sp{display:inline-block;border-radius:2px;padding:1px 3px;font-size:7px;font-weight:700;color:#fff;}
.cmp-cell{display:flex;flex-direction:column;gap:1px;align-items:center;}
.cmp-plan{font-size:7px;color:#475569;}
.match{background:rgba(220,252,231,.5);}
.diff{background:rgba(254,226,226,.6);}
.absent{background:rgba(255,247,237,.6);}
.sum-grid{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;}
.sum-card{border:1px solid #e2e8f0;border-radius:6px;padding:8px;text-align:center;min-width:100px;}
.sum-val{font-size:18px;font-weight:800;}
.sum-lbl{font-size:10px;color:#64748b;margin-top:2px;}
</style>
</head><body>
<h1>مقایسه شیفت‌بندی و حضور — ${p.year} ${mn}</h1>
${tbl ? tbl.outerHTML : ''}
${smry}
</body></html>`;

  const fr = sel('pf');
  fr.style.cssText = 'display:block;position:fixed;top:-9999px;width:1px;height:1px;';
  const doc = fr.contentWindow.document;
  doc.open(); doc.write(html); doc.close();
  fr.contentWindow.focus();
  setTimeout(()=>{ fr.contentWindow.print(); setTimeout(()=>fr.style.display='none',500); }, 450);
}

document.addEventListener('DOMContentLoaded', ()=> loadSchedule());
"""


# ═══════════════════════ API ═══════════════════════

def get_schedule_data(dept_id, year, month):
    try:
        dept_id = int(dept_id)
        year    = int(year)
        month   = int(month)
    except (TypeError, ValueError):
        return {'success': False, 'message': 'پارامترهای نامعتبر'}

    days      = get_jalali_days(year, month)
    personnel = _fetch_personnel(dept_id)
    shift_map = _fetch_shifts()
    pids      = [p['ID_person'] for p in personnel]
    planned, extras = _fetch_planned(pids, year, month, days)

    return {
        'success':   True,
        'days':      days,
        'personnel': [{'id': p['ID_person'], 'name': f"{p['nam']} {p['famil']}"} for p in personnel],
        'assigns':   planned,
        'extras':    extras,
        'shiftMap':  shift_map,
    }


def get_attendance_data(dept_id, year, month):
    try:
        dept_id = int(dept_id)
        year    = int(year)
        month   = int(month)
    except (TypeError, ValueError):
        return {'success': False, 'message': 'پارامترهای نامعتبر'}

    days      = get_jalali_days(year, month)
    personnel = _fetch_personnel(dept_id)
    shift_map = _fetch_shifts()
    pids      = {p['ID_person'] for p in personnel}
    actual    = _fetch_actual(dept_id, pids, year, month, days, shift_map)

    id_to_code  = {k: v['shift_code'] for k, v in shift_map.items()}
    id_to_color = {k: v['color_code'] for k, v in shift_map.items()}

    attendance_codes = {}
    shift_colors_map = {}
    for key, sid_list in actual.items():
        codes = []
        for sid in sid_list:
            code = id_to_code.get(str(sid), '')
            if code:
                codes.append(code)
                shift_colors_map[code] = id_to_color.get(str(sid), '#94a3b8')
        attendance_codes[key] = codes

    return {
        'success':       True,
        'days':          days,
        'personnel':     [{'id': p['ID_person'], 'name': f"{p['nam']} {p['famil']}"} for p in personnel],
        'attendance':    attendance_codes,
        'shiftColors':   shift_colors_map,
    }


def get_comparison_data(dept_id, year, month):
    try:
        dept_id = int(dept_id)
        year    = int(year)
        month   = int(month)
    except (TypeError, ValueError):
        return {'success': False, 'message': 'پارامترهای نامعتبر'}

    days      = get_jalali_days(year, month)
    personnel = _fetch_personnel(dept_id)
    shift_map = _fetch_shifts()
    pids      = [p['ID_person'] for p in personnel]
    pids_set  = set(pids)

    planned_main, extras = _fetch_planned(pids, year, month, days)
    # ترکیب اصلی و اضافی در یک لیست
    planned = {}
    for key, sid in planned_main.items():
        planned[key] = [str(sid)]
    for key, ex_list in extras.items():
        if key in planned:
            planned[key].extend([str(x) for x in ex_list])
        else:
            planned[key] = [str(x) for x in ex_list]

    actual_dict = _fetch_actual(dept_id, pids_set, year, month, days, shift_map)

    personnel_list = []
    for p in personnel:
        pid = p['ID_person']
        planned_d, actual_d = {}, {}
        for day in range(1, days + 1):
            date_int = int(f"{year}{month:02d}{day:02d}")
            key      = f"{pid}_{date_int}"
            planned_d[date_int] = planned.get(key, [])
            actual_d[date_int]  = actual_dict.get(key, [])
        personnel_list.append({
            'id':      pid,
            'name':    f"{p['nam']} {p['famil']}",
            'planned': planned_d,
            'actual':  actual_d,
        })

    return {
        'success':   True,
        'days':      days,
        'personnel': personnel_list,
        'shiftMap':  shift_map,
    }
    
    