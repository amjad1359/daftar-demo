"""
modules/admin/shift_approval_form.py
تنظیم سه سطح تایید شیفت‌بندی برای هر بخش — پنل ادمین
"""
import logging
from models.database import query

logger = logging.getLogger(__name__)
_tables_ready = False


def _init_tables():
    global _tables_ready
    if _tables_ready:
        return
    try:
        query("""
            CREATE TABLE IF NOT EXISTS tbl_shift_approvers (
                ID          INT AUTO_INCREMENT PRIMARY KEY,
                dep_id      INT NOT NULL,
                level_no    TINYINT NOT NULL COMMENT '1=مسئول بخش 2=تایید دوم 3=تایید سوم',
                level_label VARCHAR(60) NOT NULL DEFAULT '',
                user_id     INT NOT NULL,
                UNIQUE KEY uq_dep_level (dep_id, level_no),
                INDEX idx_dep (dep_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, commit=True)

        query("""
            CREATE TABLE IF NOT EXISTS tbl_shift_approvals (
                ID           INT AUTO_INCREMENT PRIMARY KEY,
                dep_id       INT NOT NULL,
                year         SMALLINT NOT NULL,
                month        TINYINT NOT NULL,
                level_no     TINYINT NOT NULL,
                approved_by  INT NOT NULL,
                approved_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                note         TEXT DEFAULT NULL,
                UNIQUE KEY uq_dep_ym_level (dep_id, year, month, level_no)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, commit=True)

        query("""
            CREATE TABLE IF NOT EXISTS tbl_shift_audit (
                ID          INT AUTO_INCREMENT PRIMARY KEY,
                dep_id      INT NOT NULL,
                person_id   INT NOT NULL,
                shift_date  INT NOT NULL,
                action      VARCHAR(20) NOT NULL,
                old_shift   INT DEFAULT NULL,
                new_shift   INT DEFAULT NULL,
                is_extra    TINYINT DEFAULT 0,
                changed_by  INT NOT NULL,
                changed_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                note        TEXT DEFAULT NULL,
                INDEX idx_dep_date (dep_id, shift_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, commit=True)

        _tables_ready = True
    except Exception:
        logger.exception('خطا در ساخت جداول تایید شیفت')
        raise


def get_approvers_config() -> dict:
    _init_tables()
    rows = query("""
        SELECT a.dep_id, b.nam_bakhsh, a.level_no, a.level_label,
               a.user_id, u.FullName
        FROM   tbl_shift_approvers a
        LEFT JOIN tbl_bakhsh b ON b.ID_nam_bakhsh = a.dep_id
        LEFT JOIN users u      ON u.UserID = a.user_id
        ORDER  BY b.nam_bakhsh, a.level_no
    """, fetch_all=True) or []
    return {'success': True, 'data': rows}


def get_approvers_for_dept(dep_id: int) -> dict:
    _init_tables()
    if not dep_id:
        return {'success': False, 'message': 'dep_id الزامی است'}
    rows = query("""
        SELECT a.level_no, a.level_label, a.user_id, u.FullName
        FROM   tbl_shift_approvers a
        LEFT JOIN users u ON u.UserID = a.user_id
        WHERE  a.dep_id = %s
        ORDER  BY a.level_no
    """, (dep_id,), fetch_all=True) or []
    return {'success': True, 'approvers': rows}


def save_approver(user: dict, form_data) -> dict:
    _init_tables()
    try:
        dep_id      = int(form_data.get('dep_id', 0))
        level_no    = int(form_data.get('level_no', 0))
        level_label = (form_data.get('level_label') or '').strip()
        approver_id = int(form_data.get('user_id', 0))
        if not dep_id or not level_no or not approver_id:
            return {'success': False, 'message': 'اطلاعات ناقص است'}
        if level_no not in (1, 2, 3):
            return {'success': False, 'message': 'سطح باید ۱، ۲ یا ۳ باشد'}
        query("""
            INSERT INTO tbl_shift_approvers (dep_id, level_no, level_label, user_id)
            VALUES (%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE user_id=%s, level_label=%s
        """, (dep_id, level_no, level_label, approver_id, approver_id, level_label), commit=True)
        return {'success': True}
    except Exception:
        logger.exception('خطا در save_approver')
        return {'success': False, 'message': 'خطای داخلی سرور'}


def delete_approver(form_data) -> dict:
    _init_tables()
    try:
        dep_id   = int(form_data.get('dep_id', 0))
        level_no = int(form_data.get('level_no', 0))
        query("DELETE FROM tbl_shift_approvers WHERE dep_id=%s AND level_no=%s",
              (dep_id, level_no), commit=True)
        return {'success': True}
    except Exception:
        logger.exception('خطا در delete_approver')
        return {'success': False, 'message': 'خطای داخلی سرور'}



_APPROVAL_CSS = ':root{--primary:#1e3a8a;--pl:#3b82f6;--success:#10b981;--danger:#ef4444;--border:#e2e8f0;--bg:#f1f5f9;--radius:12px;}*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}body{font-family:Tahoma,sans-serif;direction:rtl;background:var(--bg);color:#1e293b;}.container{max-width:1100px;margin:0 auto;padding:20px;}.page-header{background:linear-gradient(135deg,#1e3c72,#2a5298);color:white;border-radius:16px;padding:22px 28px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;}.page-header h2{font-size:18px;}.back-btn{color:white;padding:7px 16px;border:1px solid rgba(255,255,255,.4);border-radius:8px;text-decoration:none;font-size:13px;}.card{background:white;border-radius:var(--radius);padding:20px;border:1px solid var(--border);margin-bottom:18px;}.card-title{font-weight:bold;font-size:14px;margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid var(--border);}.dept-tabs{display:flex;gap:8px;flex-wrap:wrap;}.dept-tab{padding:7px 14px;border-radius:20px;border:2px solid var(--border);font-size:13px;cursor:pointer;transition:.2s;background:white;}.dept-tab.active{background:var(--primary);color:white;border-color:var(--primary);}.dept-tab:hover:not(.active){border-color:var(--pl);color:var(--pl);}.levels-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;}.level-card{border-radius:10px;border:2px solid var(--border);overflow:hidden;transition:.2s;}.level-card:hover{border-color:var(--pl);box-shadow:0 4px 16px rgba(59,130,246,.12);}.lv-header{padding:11px 15px;display:flex;align-items:center;gap:8px;font-weight:bold;font-size:14px;}.lv-1 .lv-header{background:#dbeafe;color:#1e40af;}.lv-2 .lv-header{background:#d1fae5;color:#065f46;}.lv-3 .lv-header{background:#fef3c7;color:#92400e;}.lv-body{padding:13px 15px;background:white;}.lv-user{font-size:14px;color:#374151;font-weight:600;margin-bottom:3px;}.lv-label,.lv-empty{font-size:12px;color:#94a3b8;}.lv-empty{font-style:italic;}.lv-actions{display:flex;gap:6px;margin-top:10px;}.btn{display:inline-flex;align-items:center;gap:5px;padding:8px 16px;border:none;border-radius:8px;font-size:13px;font-weight:bold;cursor:pointer;}.btn-primary{background:var(--primary);color:white;}.btn-danger{background:#ef4444;color:white;}.btn-sm{padding:5px 10px;font-size:12px;}.toast-box{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:9999;display:flex;flex-direction:column;gap:8px;min-width:260px;}.toast{padding:10px 18px;border-radius:10px;color:white;font-weight:600;font-size:13px;}.toast.s{background:linear-gradient(135deg,#059669,#10b981);}.toast.e{background:linear-gradient(135deg,#dc2626,#ef4444);}.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:200;align-items:center;justify-content:center;}.modal.open{display:flex;}.modal-box{background:white;padding:24px;border-radius:14px;width:95%;max-width:460px;}.modal-box h3{margin-bottom:16px;font-size:16px;}.modal-box label{display:block;font-size:13px;font-weight:600;color:#64748b;margin-bottom:5px;margin-top:14px;}.modal-box select,.modal-box input{width:100%;padding:10px;border:2px solid var(--border);border-radius:8px;font-size:13px;}.modal-actions{margin-top:20px;display:flex;gap:10px;}.modal-actions .btn{flex:1;justify-content:center;}'
_APPROVAL_JS = 'const LEVEL_META=[{no:1,label:\'سطح 1 (مسئول بخش)\',color:\'lv-1\',icon:\'👤\'},{no:2,label:\'سطح 2 (مدیر مستقیم )\',color:\'lv-2\',icon:\'👥\'},{no:3,label:\'سطح 3 (مدیر منابع انسانی)\',color:\'lv-3\',icon:\'🏅\'}];\nlet curDep=null;\nfunction csrf(){return document.querySelector(\'meta[name="csrf-token"]\')?.content??\'\';}\nasync function api(url,data){\n  const p=new URLSearchParams(data),t=csrf();\n  if(t)p.append(\'csrf_token\',t);\n  const r=await fetch(url,{method:\'POST\',body:p.toString(),credentials:\'include\',\n    headers:{\'Content-Type\':\'application/x-www-form-urlencoded\',\'X-CSRFToken\':t,\'X-Requested-With\':\'XMLHttpRequest\'}});\n  if(!r.ok)throw new Error(\'خطای سرور \'+r.status);\n  const d=await r.json();\n  if(!d.success)throw new Error(d.message||\'خطا\');\n  return d;\n}\nfunction toast(msg,type=\'s\'){\n  const b=document.getElementById(\'toastBox\');\n  const e=Object.assign(document.createElement(\'div\'),{className:\'toast \'+type,textContent:msg});\n  b.appendChild(e);setTimeout(()=>e.remove(),4000);\n}\nfunction closeModal(){document.getElementById(\'editModal\').classList.remove(\'open\');}\ndocument.getElementById(\'editModal\').addEventListener(\'click\',e=>{\n  if(e.target===document.getElementById(\'editModal\'))closeModal();\n});\nfunction selectDept(depId,depName){\n  curDep=depId;\n  document.querySelectorAll(\'.dept-tab\').forEach(t=>t.classList.toggle(\'active\',+t.dataset.dep===depId));\n  document.getElementById(\'levelsCard\').style.display=\'\';\n  document.getElementById(\'levelsTitle\').textContent=\'سطوح تایید — \'+depName;\n  loadLevels(depId);\n}\nasync function loadLevels(depId){\n  const box=document.getElementById(\'levelsGrid\');\n  box.innerHTML=\'<p style="color:#94a3b8;">در حال بارگذاری...</p>\';\n  try{\n    const r=await fetch(\'/module/admin/shift_approvers/get?dep_id=\'+depId);\n    const d=await r.json();\n    if(!d.success)throw new Error(d.message);\n    const map={};\n    (d.approvers||[]).forEach(a=>map[a.level_no]=a);\n    box.innerHTML=LEVEL_META.map(m=>{\n      const a=map[m.no];\n      const uid=a?a.user_id:\'\';\n      const lbl=a&&a.level_label?a.level_label:\'\';\n      const btnEdit="<button class=\'btn btn-primary btn-sm\' "\n        +"onclick=\'openModal("+depId+","+m.no+",\\""+lbl+"\\","+uid+")\'>✏️ "+(a?\'ویرایش\':\'تعریف\')+"</button>";\n      const btnDel=a?"<button class=\'btn btn-danger btn-sm\' onclick=\'delApprover("+depId+","+m.no+")\'>🗑️</button>":\'\';\n      return "<div class=\'level-card "+m.color+"\'><div class=\'lv-header\'>"+m.icon+" "+m.label+"</div>"\n        +"<div class=\'lv-body\'>"\n        +(a?"<div class=\'lv-user\'>👤 "+a.FullName+"</div><div class=\'lv-label\'>"+(a.level_label||\'بدون عنوان\')+"</div>":"<div class=\'lv-empty\'>تعریف نشده</div>")\n        +"<div class=\'lv-actions\'>"+btnEdit+btnDel+"</div></div></div>";\n    }).join(\'\');\n  }catch(e){box.innerHTML=\'<p style="color:red;">\'+e.message+\'</p>\';}\n}\nfunction openModal(depId,levelNo,label,userId){\n  document.getElementById(\'mDep\').value=depId;\n  document.getElementById(\'mLevel\').value=levelNo;\n  document.getElementById(\'mLabel\').value=label||\'\';\n  document.getElementById(\'mUser\').value=userId||\'\';\n  document.getElementById(\'modalTitle\').textContent=\'تنظیم \'+LEVEL_META.find(m=>m.no===levelNo)?.label;\n  document.getElementById(\'editModal\').classList.add(\'open\');\n}\nasync function submitApprover(){\n  const userId=document.getElementById(\'mUser\').value;\n  if(!userId){toast(\'کاربر را انتخاب کنید\',\'e\');return;}\n  try{\n    await api(\'/module/admin/shift_approvers/save\',{\n      dep_id:document.getElementById(\'mDep\').value,\n      level_no:document.getElementById(\'mLevel\').value,\n      level_label:document.getElementById(\'mLabel\').value,\n      user_id:userId\n    });\n    closeModal();loadLevels(+document.getElementById(\'mDep\').value);toast(\'ذخیره شد\');\n  }catch(e){toast(\'خطا: \'+e.message,\'e\');}\n}\nasync function delApprover(depId,levelNo){\n  if(!confirm(\'حذف شود؟\'))return;\n  try{\n    await api(\'/module/admin/shift_approvers/delete\',{dep_id:depId,level_no:levelNo});\n    loadLevels(depId);toast(\'حذف شد\');\n  }catch(e){toast(\'خطا: \'+e.message,\'e\');}\n}\n'


def get_shift_approval_form(user: dict) -> str:
    import json, secrets
    from flask import session as _s
    _init_tables()

    if '_csrf_token' not in _s:
        _s['_csrf_token'] = secrets.token_hex(32)
    csrf_token = _s['_csrf_token']

    departments = query(
        "SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh",
        fetch_all=True
    ) or []

    users_list = query(
        "SELECT UserID, FullName FROM users WHERE IsActive=1 ORDER BY FullName",
        fetch_all=True
    ) or []

    depts_json = json.dumps(
        [{'id': d['ID_nam_bakhsh'], 'name': d['nam_bakhsh']} for d in departments],
        ensure_ascii=False
    )

    tabs_html = ''
    for d in departments:
        did  = d['ID_nam_bakhsh']
        name = d['nam_bakhsh']
        tabs_html += (
            '<div class="dept-tab" data-dep="' + str(did) + '"'
            + ' onclick="selectDeptById(' + str(did) + ')">'
            + name + '</div>'
        )

    user_opts = '<option value="">-- انتخاب کاربر --</option>'
    for u in users_list:
        user_opts += '<option value="' + str(u['UserID']) + '">' + u['FullName'] + '</option>'

    parts = []
    parts.append('<!DOCTYPE html><html dir="rtl" lang="fa"><head>')
    parts.append('<meta charset="UTF-8">')
    parts.append('<meta name="viewport" content="width=device-width,initial-scale=1.0">')
    parts.append('<meta name="csrf-token" content="' + csrf_token + '">')
    parts.append('<title>تنظیم تاییدکننده‌های شیفت</title>')
    parts.append('<style>' + _APPROVAL_CSS + '</style>')
    parts.append('</head><body>')
    parts.append('<div class="toast-box" id="toastBox"></div>')
    parts.append('<div class="container">')
    parts.append('<div class="page-header">')
    parts.append('<h2>✅ تنظیم تاییدکننده‌های شیفت‌بندی</h2>')
    parts.append('<a href="/module/admin" class="back-btn">⬅️ بازگشت</a>')
    parts.append('</div>')
    parts.append('<div class="card">')
    parts.append('<div class="card-title">🏥 انتخاب بخش</div>')
    parts.append('<div class="dept-tabs" id="deptTabs">' + tabs_html + '</div>')
    parts.append('</div>')
    parts.append('<div class="card" id="levelsCard" style="display:none;">')
    parts.append('<div class="card-title" id="levelsTitle">سطوح تایید</div>')
    parts.append('<div class="levels-grid" id="levelsGrid"></div>')
    parts.append('</div>')
    parts.append('</div>')
    parts.append('<div class="modal" id="editModal"><div class="modal-box">')
    parts.append('<h3 id="modalTitle">✏️ تنظیم تاییدکننده</h3>')
    parts.append('<input type="hidden" id="mDep"><input type="hidden" id="mLevel">')
    parts.append('<label>عنوان سطح (اختیاری)</label>')
    parts.append('<input type="text" id="mLabel" placeholder="مثلاً: مسئول بخش">')
    parts.append('<label>کاربر تاییدکننده</label>')
    parts.append('<select id="mUser">' + user_opts + '</select>')
    parts.append('<div class="modal-actions">')
    parts.append('<button class="btn btn-primary" onclick="submitApprover()">💾 ذخیره</button>')
    parts.append('<button class="btn" style="background:#64748b;color:white;" onclick="closeModal()">انصراف</button>')
    parts.append('</div></div></div>')
    parts.append('<script>')
    parts.append('const DEPTS=' + depts_json + ';')
    parts.append('const DEPT_MAP=new Map(DEPTS.map(d=>[d.id,d.name]));')
    parts.append('function selectDeptById(id){selectDept(id,DEPT_MAP.get(id)||"بخش "+id);}')
    parts.append(_APPROVAL_JS)
    parts.append('</script>')
    parts.append('</body></html>')
    return '\n'.join(parts)