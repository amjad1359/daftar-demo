"""
modules/admin/users_form.py — نسخه نهایی و کامل
پشتیبانی از انتخاب چندگانه واحد و بخش، امضای دیجیتال، جستجو و ویرایش
"""

import os, json, base64, logging
from datetime import datetime
from models.database import query, get_connection
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from utils.auto_log import log_crud

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = os.path.join("uploads", "signatures")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

# --------------------------------------------------------------------
#  راه‌اندازی جداول کمکی (فقط یک‌بار)
# --------------------------------------------------------------------
_tables_initialized = False

def _init_tables():
    global _tables_initialized
    if _tables_initialized:
        return
    try:
        query("""
            CREATE TABLE IF NOT EXISTS tbl_user_units (
                id       INT AUTO_INCREMENT PRIMARY KEY,
                user_id  INT NOT NULL,
                unit_id  INT NOT NULL,
                UNIQUE KEY uq_uu (user_id, unit_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, commit=True)
        query("""
            CREATE TABLE IF NOT EXISTS tbl_user_depts (
                id       INT AUTO_INCREMENT PRIMARY KEY,
                user_id  INT NOT NULL,
                dep_id   INT NOT NULL,
                UNIQUE KEY uq_ud (user_id, dep_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, commit=True)
        col = query("SHOW COLUMNS FROM users LIKE 'emza_path'", fetch_one=True)
        if not col:
            query("ALTER TABLE users ADD COLUMN emza_path VARCHAR(255) DEFAULT NULL", commit=True)
        _tables_initialized = True
    except Exception:
        logger.exception("Error initializing users tables")

# --------------------------------------------------------------------
#  ابزارهای کمکی
# --------------------------------------------------------------------
def to_eng_digits(text):
    if not text:
        return ""
    return text.translate(
        str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
    )

def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def _get_user_units(user_id):
    rows = query("SELECT unit_id FROM tbl_user_units WHERE user_id=%s", (user_id,), fetch_all=True) or []
    return [r["unit_id"] for r in rows]

def _get_user_depts(user_id):
    rows = query("SELECT dep_id FROM tbl_user_depts WHERE user_id=%s", (user_id,), fetch_all=True) or []
    return [r["dep_id"] for r in rows]

def _save_user_units_txn(cur, user_id, unit_ids):
    cur.execute("DELETE FROM tbl_user_units WHERE user_id=%s", (user_id,))
    for uid in unit_ids:
        cur.execute("INSERT IGNORE INTO tbl_user_units (user_id,unit_id) VALUES(%s,%s)", (user_id, uid))

def _save_user_depts_txn(cur, user_id, dep_ids):
    cur.execute("DELETE FROM tbl_user_depts WHERE user_id=%s", (user_id,))
    for did in dep_ids:
        cur.execute("INSERT IGNORE INTO tbl_user_depts (user_id,dep_id) VALUES(%s,%s)", (user_id, did))

# --------------------------------------------------------------------
#  API Functions (دقیقاً مطابق مسیرهای قبلی)
# --------------------------------------------------------------------
def get_users_list_api():
    users = query("""
        SELECT u.UserID, u.FullName, u.Username, u.IsActive, u.AccessLevelID,
               a.AccessLevelName, u.postmodir, m.nam_modiriat AS unit_name,
               u.dep_id, b.nam_bakhsh AS department_name, u.emza_path
        FROM users u
        LEFT JOIN accesslevels a ON u.AccessLevelID = a.AccessLevelID
        LEFT JOIN tbl_nam_modiriat m ON u.postmodir = m.ID_nam_modirit
        LEFT JOIN tbl_bakhsh b ON u.dep_id = b.ID_nam_bakhsh
        ORDER BY u.UserID DESC
    """, fetch_all=True) or []
    return {"success": True, "users": users}

def get_user_detail(user_id):
    _init_tables()
    u = query("SELECT * FROM users WHERE UserID=%s", (user_id,), fetch_one=True)
    if not u:
        return {"success": False, "message": "کاربر یافت نشد"}
    for k in list(u.keys()):
        if isinstance(u[k], (bytearray, bytes)):
            u[k] = u[k].decode("utf-8", errors="ignore")
    u["unit_ids"] = _get_user_units(user_id)
    u["dep_ids"] = _get_user_depts(user_id)
    return {"success": True, "user": u}

def save_user(form_data, files=None):
    """
    ذخیره کاربر جدید یا ویرایش کاربر موجود
    برای آپلود امضا باید files=request.files ارسال شود.
    """
    _init_tables()
    user_id = form_data.get("user_id") or None
    fullname = (form_data.get("fullname") or "").strip()
    raw_username = (form_data.get("username") or "").strip()
    username = to_eng_digits(raw_username)
    password = (form_data.get("password") or "").strip()
    access_level = form_data.get("access_level", "")
    is_active = form_data.get("is_active", "1")

    # دریافت چندگانه‌ها
    unit_ids = [int(x) for x in (form_data.getlist("unit_ids") if hasattr(form_data, "getlist") else []) if x]
    dep_ids = [int(x) for x in (form_data.getlist("dep_ids") if hasattr(form_data, "getlist") else []) if x]

    # پشتیبانی از حالت تک‌مقداری (برای سازگاری با قدیم)
    old_unit = form_data.get("unit", "0")
    if not unit_ids and old_unit and old_unit != "0":
        unit_ids = [int(old_unit)]
    old_dep = form_data.get("dep_id", "")
    if not dep_ids and old_dep:
        dep_ids = [int(old_dep)]

    # اعتبارسنجی
    if not fullname:
        return {"success": False, "message": "نام کامل الزامی است"}
    if not username or not username.isdigit() or len(username) != 10:
        return {"success": False, "message": f"کد ملی نامعتبر است. مقدار دریافتی: '{username}'"}
    if not user_id and not password:
        return {"success": False, "message": "رمز عبور الزامی است"}
    if password and len(password) < 4:
        return {"success": False, "message": "رمز عبور حداقل ۴ کاراکتر باشد"}
    if not access_level:
        return {"success": False, "message": "سطح دسترسی الزامی است"}

    # بررسی تکراری بودن کد ملی
    existing = query(
        "SELECT UserID FROM users WHERE Username=%s" + (" AND UserID!=%s" if user_id else ""),
        (username, int(user_id)) if user_id else (username,),
        fetch_one=True
    )
    if existing:
        return {"success": False, "message": "این کد ملی قبلاً ثبت شده است"}

    # ذخیره امضا (در صورت ارسال)
    emza_path = None
    if files:
        sig_file = files.get("signature")
        if sig_file and sig_file.filename and _allowed(sig_file.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            fname = secure_filename(
                f"sig_{username}_{int(datetime.now().timestamp())}."
                f"{sig_file.filename.rsplit(chr(46), 1)[1].lower()}"
            )
            path = os.path.join(UPLOAD_FOLDER, fname)
            sig_file.save(path)
            emza_path = path.replace("\\", "/")

    hashed = generate_password_hash(password) if password else None

    primary_unit = unit_ids[0] if unit_ids else 0
    primary_dep = dep_ids[0] if dep_ids else None

    conn = get_connection()
    cur = conn.cursor()
    try:
        if user_id:  # ویرایش
            if hashed:
                sql = ("UPDATE users SET FullName=%s,Username=%s,PasswordHash=%s,"
                       "AccessLevelID=%s,postmodir=%s,dep_id=%s,IsActive=%s")
                params = [fullname, username, hashed, access_level, primary_unit, primary_dep, is_active]
            else:
                sql = ("UPDATE users SET FullName=%s,Username=%s,"
                       "AccessLevelID=%s,postmodir=%s,dep_id=%s,IsActive=%s")
                params = [fullname, username, access_level, primary_unit, primary_dep, is_active]
            if emza_path:
                sql += ",emza_path=%s"
                params.append(emza_path)
            sql += " WHERE UserID=%s"
            params.append(int(user_id))
            cur.execute(sql, params)
            new_id = int(user_id)
        else:  # ثبت جدید
            cur.execute(
                "INSERT INTO users (FullName,Username,PasswordHash,AccessLevelID,"
                "postmodir,dep_id,IsActive,emza_path,CreatedDate) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (fullname, username, hashed, access_level, primary_unit, primary_dep,
                 is_active, emza_path, datetime.now())
            )
            new_id = cur.lastrowid

        # ذخیره‌ی ارتباطات چندگانه
        _save_user_units_txn(cur, new_id, unit_ids)
        _save_user_depts_txn(cur, new_id, dep_ids)

        conn.commit()

        # لاگ
        log_crud("save_user", new_id, key_value=new_id,
                 new_value=json.dumps({"fullname": fullname, "username": username}, ensure_ascii=False))
        return {"success": True, "message": "کاربر با موفقیت ذخیره شد"}
    except Exception as e:
        conn.rollback()
        logger.exception("save_user transaction failed")
        return {"success": False, "message": f"خطا در ثبت پایگاه داده: {e}"}
    finally:
        cur.close()
        conn.close()

def get_user_signature(user_id):
    u = query("SELECT emza_path FROM users WHERE UserID=%s", (user_id,), fetch_one=True)
    if not u or not u.get("emza_path"):
        return {"success": False}
    path = u["emza_path"]
    if not os.path.exists(path):
        return {"success": False}
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(ext, "png")
    return {"success": True, "data": f"data:image/{mime};base64,{data}"}

def _get_csrf():
    import secrets
    from flask import session as _s
    if "_csrf_token" not in _s:
        _s["_csrf_token"] = secrets.token_hex(32)
    return _s["_csrf_token"]

# --------------------------------------------------------------------
#  HTML – کاملاً مستقل و بدون نیاز به render_page
# --------------------------------------------------------------------
def get_users_form(user):
    _init_tables()
    csrf = _get_csrf()

    # سطوح دسترسی
    access_levels = query(
        "SELECT AccessLevelID, AccessLevelName, Description FROM accesslevels ORDER BY AccessLevelID",
        fetch_all=True
    ) or []
    level_desc = {str(lv["AccessLevelID"]): lv.get("Description", "") for lv in access_levels}

    # واحدها
    units = query(
        "SELECT ID_nam_modirit, nam_modiriat FROM tbl_nam_modiriat ORDER BY nam_modiriat",
        fetch_all=True
    ) or []
    # بخش‌ها
    depts = query(
        "SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh",
        fetch_all=True
    ) or []

    # امن‌سازی برای جاوااسکریپت
    units_json = json.dumps(
        [{"id": u["ID_nam_modirit"], "name": u["nam_modiriat"]} for u in units],
        ensure_ascii=False
    ).replace("<", "\\u003c")
    depts_json = json.dumps(
        [{"id": d["ID_nam_bakhsh"], "name": d["nam_bakhsh"]} for d in depts],
        ensure_ascii=False
    ).replace("<", "\\u003c")
    level_json = json.dumps(level_desc, ensure_ascii=False).replace("<", "\\u003c")

    level_opts = '<option value="">--- سطح دسترسی ---</option>'
    for lv in access_levels:
        _id = str(lv['AccessLevelID'])
        _nm = lv['AccessLevelName']
        level_opts += f'<option value="{_id}">{_nm}</option>'

    guide_html = ""
    for lv in access_levels:
        desc = (lv.get("Description") or "بدون توضیحات").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        name = lv["AccessLevelName"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        guide_html += f'<div style="padding:8px 0;border-bottom:1px solid #e2e8f0;"><strong>{name}</strong>: {desc}</div>'
    if not guide_html:
        guide_html = '<p style="color:#94a3b8;">سطح دسترسی تعریف نشده</p>'

    # --------------------------------------------------------------------
    html = f"""<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="csrf-token" content="{csrf}">
<title>مدیریت کاربران</title>
<style>
:root{{--pr:#1e3a8a;--pl:#3b82f6;--su:#10b981;--da:#ef4444;--wa:#f59e0b;
      --dk:#1e293b;--gr:#64748b;--bd:#e2e8f0;--bg:#f1f5f9;--wh:#fff;--rd:12px;}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:Tahoma,"Segoe UI",sans-serif;direction:rtl;background:var(--bg);color:var(--dk);}}
.fade-in{{animation:fi .4s ease;}}
@keyframes fi{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
.con{{max-width:1400px;margin:0 auto;padding:20px;}}
.hdr{{background:linear-gradient(135deg,#1e3c72,#2a5298);color:#fff;border-radius:16px;
     padding:25px 30px;margin-bottom:25px;display:flex;justify-content:space-between;align-items:center;
     box-shadow:0 8px 30px rgba(30,60,114,.25);}}
.hdr h2{{font-size:22px;}}
.back{{color:#fff;text-decoration:none;padding:8px 16px;border:1px solid rgba(255,255,255,.4);border-radius:8px;}}
.back:hover{{background:rgba(255,255,255,.2);}}
.card{{background:var(--wh);border-radius:var(--rd);padding:25px;border:1px solid var(--bd);
      box-shadow:0 1px 3px rgba(0,0,0,.05);margin-bottom:25px;}}
.card-title{{font-weight:700;color:var(--dk);margin-bottom:15px;padding-bottom:10px;border-bottom:2px solid var(--bd);}}
.row{{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-start;}}
.fg{{margin-bottom:16px;flex:1;min-width:200px;}}
.fg label{{display:block;font-size:13px;font-weight:600;color:var(--gr);margin-bottom:6px;}}
.fi,.fs{{width:100%;padding:11px 13px;border:2px solid var(--bd);border-radius:8px;
         font-size:14px;font-family:inherit;background:var(--wh);transition:.2s;}}
.fi:focus,.fs:focus{{border-color:var(--pl);outline:none;box-shadow:0 0 0 3px rgba(59,130,246,.15);}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:10px 20px;
     border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;transition:.2s;}}
.btn-pr{{background:var(--pr);color:#fff;}}.btn-pr:hover{{background:var(--pl);}}
.btn-su{{background:var(--su);color:#fff;}}
.btn-da{{background:var(--da);color:#fff;}}
.btn-sm{{padding:6px 12px;font-size:12px;}}
.toggle-switch{{position:relative;display:inline-block;width:52px;height:26px;}}
.toggle-switch input{{opacity:0;width:0;height:0;}}
.slider{{position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background:#ccc;transition:.4s;border-radius:34px;}}
.slider::before{{position:absolute;content:"";height:20px;width:20px;left:3px;bottom:3px;
               background:#fff;transition:.4s;border-radius:50%;}}
input:checked+.slider{{background:var(--su);}}
input:checked+.slider::before{{transform:translateX(26px);}}

/* multi-select tag box */
.ms-box{{border:2px solid var(--bd);border-radius:8px;padding:8px;min-height:46px;
         display:flex;flex-wrap:wrap;gap:6px;cursor:text;transition:.2s;background:#fff;}}
.ms-box:focus-within{{border-color:var(--pl);box-shadow:0 0 0 3px rgba(59,130,246,.15);}}
.ms-tag{{display:inline-flex;align-items:center;gap:4px;background:#dbeafe;color:#1e40af;
         border-radius:6px;padding:3px 8px;font-size:12px;font-weight:600;}}
.ms-tag .rm{{cursor:pointer;color:#3b82f6;font-size:14px;line-height:1;}}
.ms-tag .rm:hover{{color:#1e3a8a;}}
.ms-drop{{position:absolute;z-index:100;background:#fff;border:2px solid var(--pl);
          border-radius:8px;max-height:220px;overflow-y:auto;min-width:250px;
          box-shadow:0 8px 24px rgba(0,0,0,.12);display:none;}}
.ms-drop.open{{display:block;}}
.ms-item{{padding:9px 14px;cursor:pointer;font-size:13px;display:flex;align-items:center;gap:8px;}}
.ms-item:hover{{background:#eff6ff;}}
.ms-item.sel{{background:#dbeafe;color:#1e40af;font-weight:600;}}
.ms-search{{width:100%;padding:8px 12px;border:none;border-bottom:1px solid var(--bd);
            font-size:13px;outline:none;font-family:inherit;}}
.ms-wrap{{position:relative;}}

/* امضا */
.sig-area{{border:2px dashed var(--bd);border-radius:10px;padding:20px;text-align:center;
           background:#fafafa;transition:.2s;cursor:pointer;}}
.sig-area:hover{{border-color:var(--pl);background:#eff6ff;}}
.sig-area.has-img{{border-style:solid;border-color:var(--su);background:#f0fdf4;}}
.sig-preview{{max-height:100px;max-width:280px;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,.1);}}
.sig-placeholder{{color:var(--gr);font-size:13px;}}

/* جدول */
.srch{{background:var(--bg);padding:12px 15px;border-radius:8px;margin-bottom:14px;}}
.tbl{{width:100%;border-collapse:collapse;}}
.tbl th{{background:var(--pr);color:#fff;padding:11px;font-size:13px;text-align:center;white-space:nowrap;}}
.tbl td{{padding:9px;text-align:center;border-bottom:1px solid var(--bd);font-size:13px;}}
.tbl tr:hover{{background:#f8fafc;cursor:pointer;}}
.tbl tr.sel{{background:#eef2ff;}}
.act{{background:#d4edda;color:#155724;padding:3px 12px;border-radius:12px;font-size:12px;font-weight:600;display:inline-block;}}
.inact{{background:#f8d7da;color:#721c24;padding:3px 12px;border-radius:12px;font-size:12px;font-weight:600;display:inline-block;}}
.edit-cb{{display:flex;align-items:center;gap:8px;margin:14px 0;background:#f0f0f0;padding:10px 15px;border-radius:8px;}}

.toast-c{{position:fixed;top:20px;left:50%;transform:translateX(-50%);z-index:10000;
          display:flex;flex-direction:column;gap:10px;pointer-events:none;min-width:280px;}}
.toast{{display:flex;align-items:center;gap:12px;padding:14px 22px;border-radius:12px;color:#fff;
        font-weight:600;box-shadow:0 10px 30px rgba(0,0,0,.2);animation:sd .4s ease;}}
.toast.success{{background:linear-gradient(135deg,#059669,#10b981);}}
.toast.error{{background:linear-gradient(135deg,#dc2626,#ef4444);}}
@keyframes sd{{from{{opacity:0;transform:translateY(-30px);}}to{{opacity:1;transform:translateY(0);}}}}
@media(max-width:768px){{.hdr{{flex-direction:column;gap:14px;text-align:center;}}}}
</style>
</head>
<body>
<div class="toast-c" id="tc"></div>
<div class="con fade-in">

<div class="hdr">
    <h2>👤 مدیریت کاربران</h2>
    <a href="/module/admin" class="back">⬅️ بازگشت</a>
</div>

<div class="card" id="form-card">
    <div class="card-title" id="form-title">📝 ثبت کاربر جدید</div>
    <form id="uf" enctype="multipart/form-data">
        <input type="hidden" id="eid" value="">

        <div class="row">
            <div class="fg"><label>👤 نام کامل</label>
                <input type="text" id="fn" class="fi" placeholder="نام و نام خانوادگی" required></div>
            <div class="fg"><label>🔑 کد ملی (نام کاربری)</label>
                <input type="text" id="un" class="fi" placeholder="۱۰ رقمی" maxlength="10" required></div>
        </div>

        <div class="row">
            <div class="fg"><label>🔒 رمز عبور <small id="ph">(حداقل ۴ کاراکتر)</small></label>
                <input type="password" id="pw" class="fi" placeholder="رمز عبور" minlength="4"></div>

            <div class="fg"><label>📋 سطح دسترسی</label>
                <select id="al" class="fs">
                    {level_opts}
                </select>
                <small id="ld" style="color:var(--gr);margin-top:5px;display:none;"></small>
            </div>
                
            <div class="fg" style="max-width:120px;">
                <label>🔔 فعال</label>
                <label class="toggle-switch" style="display:block;margin-top:10px;">
                    <input type="checkbox" id="ia" checked><span class="slider"></span>
                </label>
            </div>
        </div>

        <div class="row">
            <div class="fg">
                <label>🏢 واحد مدیریت <small style="color:#94a3b8;">(چند انتخابی)</small></label>
                <div class="ms-wrap" id="unit-wrap">
                    <div class="ms-box" id="unit-box" tabindex="0">
                        <span id="unit-ph" style="color:#94a3b8;font-size:13px;padding:2px 4px;">انتخاب واحد...</span>
                    </div>
                    <div class="ms-drop" id="unit-drop">
                        <input class="ms-search" id="unit-search" placeholder="جستجو...">
                        <div id="unit-list"></div>
                    </div>
                </div>
                <input type="hidden" id="unit-hidden">
            </div>
            <div class="fg">
                <label>🏥 بخش <small style="color:#94a3b8;">(چند انتخابی)</small></label>
                <div class="ms-wrap" id="dept-wrap">
                    <div class="ms-box" id="dept-box" tabindex="0">
                        <span id="dept-ph" style="color:#94a3b8;font-size:13px;padding:2px 4px;">انتخاب بخش...</span>
                    </div>
                    <div class="ms-drop" id="dept-drop">
                        <input class="ms-search" id="dept-search" placeholder="جستجو...">
                        <div id="dept-list"></div>
                    </div>
                </div>
                <input type="hidden" id="dept-hidden">
            </div>
        </div>

        <div class="row">
            <div class="fg">
                <label>✍️ امضا <small style="color:#94a3b8;">(تصویر PNG/JPG)</small></label>
                <div class="sig-area" id="sig-area">
                    <img id="sig-preview" class="sig-preview" style="display:none;">
                    <div class="sig-placeholder" id="sig-ph">
                        <div style="font-size:32px;">📤</div>
                        <div style="margin-top:8px;">برای آپلود امضا کلیک کنید</div>
                        <div style="font-size:11px;color:#cbd5e1;margin-top:4px;">PNG, JPG, WEBP — حداکثر ۲ مگابایت</div>
                    </div>
                </div>
                <input type="file" id="sig-file" accept="image/*" style="display:none;">
                <button type="button" class="btn btn-sm btn-da" style="margin-top:6px;display:none;" id="sig-rm">🗑️ حذف امضا</button>
            </div>
            <div class="fg"></div>
        </div>

        <div class="row" style="margin-top:15px;">
            <button type="button" class="btn btn-pr" id="save-btn">
                <span id="st">💾 ثبت کاربر جدید</span>
                <span id="sl" style="display:none;">⏳ ...</span>
            </button>
            <button type="button" class="btn btn-sm" id="clear-btn">🔄 فرم جدید</button>
        </div>
    </form>
</div>

<div class="card">
    <div class="card-title">📋 لیست کاربران</div>
    <div class="srch row">
        <input type="text" id="si" class="fi" placeholder="🔍 جستجو..." style="flex:1;">
        <span id="tc2" style="font-weight:700;white-space:nowrap;">۰ کاربر</span>
    </div>
    <div class="edit-cb">
        <input type="checkbox" id="ecb">
        <label for="ecb">🔔 فعال‌سازی ویرایش — سپس روی ردیف کلیک کنید</label>
    </div>
    <div style="overflow-x:auto;">
        <table class="tbl">
            <thead><tr>
                <th>کد</th><th>نام</th><th>کد ملی</th>
                <th>سطح دسترسی</th><th>واحد</th><th>بخش</th>
                <th>امضا</th><th>وضعیت</th>
            </tr></thead>
            <tbody id="tb"></tbody>
        </table>
    </div>
</div>

<div class="card">
    <div class="card-title">📖 راهنمای سطوح دسترسی</div>
    <div>{guide_html}</div>
</div>
</div>

<script>
const UNITS  = {units_json};
const DEPTS  = {depts_json};
const LVDESC = {level_json};

function escapeHtml(text) {{
    const map = {{
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '`': '&#x60;',
        '$': '&#36;'
    }};
    return String(text).replace(/[&<>"'`$]/g, m => map[m]);
}}

let allUsers=[], editMode=false, selId=null;
let unitSel=[], deptSel=[];

function toast(msg, type) {{
    const c = document.getElementById("tc");
    const t = document.createElement("div");
    t.className = "toast " + (type || "success");
    t.innerHTML = "<span>" + (type === "error" ? "❌" : "✅") + "</span><span>" + escapeHtml(msg) + "</span>"
                + "<span style='cursor:pointer;margin-right:auto;' onclick='this.parentElement.remove()'>✕</span>";
    c.appendChild(t);
    setTimeout(() => {{ if (t.parentElement) {{ t.style.opacity = "0"; setTimeout(() => t.remove(), 300); }} }}, 4000);
}}

function setLoading(btn, loading) {{
    const st = btn.querySelector('#st');
    const sl = btn.querySelector('#sl');
    if (loading) {{
        st.style.display = 'none';
        sl.style.display = 'inline';
    }} else {{
        st.style.display = 'inline';
        sl.style.display = 'none';
    }}
}}

function showLvDesc() {{
    const lv = document.getElementById("al").value;
    const el = document.getElementById("ld");
    if (lv && LVDESC[lv]) {{
        el.textContent = "📝 " + LVDESC[lv];
        el.style.display = "block";
    }} else {{
        el.style.display = "none";
    }}
}}

// ──── مدیریت انتخاب چندگانه (واحد/بخش) ────
function renderTags(name) {{
    const arr = name === "unit" ? unitSel : deptSel;
    const data = name === "unit" ? UNITS : DEPTS;
    const box = document.getElementById(name + "-box");
    const ph = document.getElementById(name + "-ph");
    box.querySelectorAll(".ms-tag").forEach(t => t.remove());
    if (arr.length === 0) {{
        ph.style.display = "inline";
        return;
    }}
    ph.style.display = "none";
    arr.forEach(id => {{
        const item = data.find(d => d.id === id);
        if (!item) return;
        const tag = document.createElement("div");
        tag.className = "ms-tag";
        tag.innerHTML = escapeHtml(item.name) + '<span class="rm">×</span>';
        tag.querySelector('.rm').addEventListener('click', (e) => {{
            e.stopPropagation();
            removeItem(name, id);
        }});
        box.insertBefore(tag, ph);
    }});
    document.getElementById(name + "-hidden").value = arr.join(",");
}}

function toggleItem(name, id) {{
    const arr = name === "unit" ? unitSel : deptSel;
    const idx = arr.indexOf(id);
    if (idx === -1) arr.push(id);
    else arr.splice(idx, 1);
    renderTags(name);
    renderDrop(name);
}}

function removeItem(name, id) {{
    const arr = name === "unit" ? unitSel : deptSel;
    const idx = arr.indexOf(id);
    if (idx !== -1) arr.splice(idx, 1);
    renderTags(name);
    renderDrop(name);
}}

function renderDrop(name) {{
    const arr = name === "unit" ? unitSel : deptSel;
    const data = name === "unit" ? UNITS : DEPTS;
    const listEl = document.getElementById(name + "-list");
    const searchEl = document.getElementById(name + "-search");
    const q = (searchEl.value || "").trim().toLowerCase();
    const filtered = data.filter(d => d.name.toLowerCase().includes(q));
    listEl.innerHTML = "";
    if (filtered.length > 0) {{
        const selectAllDiv = document.createElement("div");
        selectAllDiv.className = "ms-item";
        const isAllSelected = filtered.every(d => arr.includes(d.id));
        selectAllDiv.innerHTML = isAllSelected ? "❌ <strong>لغو انتخاب همه موارد</strong>" : "✅ <strong>انتخاب همه موارد این لیست</strong>";
        selectAllDiv.style.borderBottom = "1px dashed var(--bd)";
        selectAllDiv.style.background = "#f8fafc";
        selectAllDiv.style.color = isAllSelected ? "var(--da)" : "var(--pr)";
        selectAllDiv.addEventListener("click", (e) => {{
            e.stopPropagation();
            if (isAllSelected) {{
                filtered.forEach(d => {{
                    const idx = arr.indexOf(d.id);
                    if (idx !== -1) arr.splice(idx, 1);
                }});
            }} else {{
                filtered.forEach(d => {{
                    if (!arr.includes(d.id)) arr.push(d.id);
                }});
            }}
            renderTags(name);
            renderDrop(name);
        }});
        listEl.appendChild(selectAllDiv);
    }}
    filtered.forEach(d => {{
        const div = document.createElement("div");
        div.className = "ms-item" + (arr.includes(d.id) ? " sel" : "");
        div.textContent = (arr.includes(d.id) ? "✅ " : "") + d.name;
        div.addEventListener("click", () => toggleItem(name, d.id));
        listEl.appendChild(div);
    }});
}}

function openDrop(name) {{
    const drop = document.getElementById(name + "-drop");
    ["unit", "dept"].filter(n => n !== name).forEach(n => document.getElementById(n + "-drop").classList.remove("open"));
    const isOpen = !drop.classList.contains("open");
    drop.classList.toggle("open", isOpen);
    if (isOpen) {{
        renderDrop(name);
        document.getElementById(name + "-search").focus();
    }}
}}

document.addEventListener("click", (e) => {{
    if (!e.target.closest(".ms-wrap")) {{
        document.querySelectorAll(".ms-drop").forEach(d => d.classList.remove("open"));
    }}
}});

document.getElementById("unit-box").addEventListener("click", (e) => {{ e.stopPropagation(); openDrop("unit"); }});
document.getElementById("dept-box").addEventListener("click", (e) => {{ e.stopPropagation(); openDrop("dept"); }});
document.getElementById("unit-search").addEventListener("input", () => renderDrop("unit"));
document.getElementById("dept-search").addEventListener("input", () => renderDrop("dept"));

// ──── مدیریت امضا ────
const sigArea = document.getElementById("sig-area");
const sigFile = document.getElementById("sig-file");
const sigPreview = document.getElementById("sig-preview");
const sigPh = document.getElementById("sig-ph");
const sigRm = document.getElementById("sig-rm");

sigArea.addEventListener("click", () => sigFile.click());
sigFile.addEventListener("change", () => {{
    const file = sigFile.files[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {{
        toast("فایل امضا نباید بیشتر از ۲ مگابایت باشد", "error");
        sigFile.value = "";
        return;
    }}
    const reader = new FileReader();
    reader.onload = (e) => {{
        sigPreview.src = e.target.result;
        sigPreview.style.display = "block";
        sigPh.style.display = "none";
        sigArea.classList.add("has-img");
        sigRm.style.display = "inline-flex";
    }};
    reader.readAsDataURL(file);
}});
sigRm.addEventListener("click", (e) => {{
    e.stopPropagation();
    sigFile.value = "";
    sigPreview.src = "";
    sigPreview.style.display = "none";
    sigPh.style.display = "block";
    sigArea.classList.remove("has-img");
    sigRm.style.display = "none";
}});

// ──── ذخیره کاربر (با پشتیبانی از فایل امضا) ────
document.getElementById("save-btn").addEventListener("click", async () => {{
    const fn = document.getElementById("fn").value.trim();
    let rawUn = document.getElementById("un").value.trim();
    const un = rawUn.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
                    .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d));
    const pw = document.getElementById("pw").value;
    const al = document.getElementById("al").value;
    const ia = document.getElementById("ia").checked ? "1" : "0";
    const eid = document.getElementById("eid").value;

    if (!fn) {{ toast("نام کامل الزامی است", "error"); return; }}
    if (!un || !/^\\d{{10}}$/.test(un)) {{ toast("کد ملی باید دقیقاً ۱۰ عدد باشد", "error"); return; }}
    if (!eid && (!pw || pw.length < 4)) {{ toast("رمز عبور حداقل ۴ کاراکتر باشد", "error"); return; }}
    if (pw && pw.length < 4) {{ toast("رمز عبور حداقل ۴ کاراکتر باشد", "error"); return; }}
    if (!al) {{ toast("سطح دسترسی الزامی است", "error"); return; }}

    const fd = new FormData();
    fd.append("fullname", fn);
    fd.append("username", un);
    fd.append("password", pw);
    fd.append("access_level", al);
    fd.append("is_active", ia);
    if (eid) fd.append("user_id", eid);
    unitSel.forEach(id => fd.append("unit_ids", id));
    deptSel.forEach(id => fd.append("dep_ids", id));
    const sigF = sigFile.files[0];
    if (sigF) fd.append("signature", sigF);

    const btn = document.getElementById("save-btn");
    setLoading(btn, true);
    const csrf = document.querySelector("meta[name='csrf-token']")?.content || "";
    try {{
        const r = await fetch("/module/admin/users/save", {{
            method: "POST", body: fd,
            headers: {{ ...(csrf ? {{"X-CSRFToken": csrf, "X-Requested-With": "XMLHttpRequest"}} : {{}}) }}
        }});
        const d = await r.json();
        if (d.success) {{
            toast("✅ " + d.message, "success");
            clearForm();
            loadUsers();
        }} else toast("⛔ " + d.message, "error");
    }} catch (e) {{ toast("خطای ارتباطی", "error"); }}
    finally {{ setLoading(btn, false); }}
}});

function clearForm() {{
    document.getElementById("uf").reset();
    document.getElementById("eid").value = "";
    document.getElementById("form-title").textContent = "📝 ثبت کاربر جدید";
    document.getElementById("st").textContent = "💾 ثبت کاربر جدید";
    document.getElementById("pw").required = true;
    document.getElementById("ph").textContent = "(حداقل ۴ کاراکتر)";
    document.getElementById("ld").style.display = "none";
    unitSel = []; deptSel = [];
    renderTags("unit");
    renderTags("dept");
    sigFile.value = "";
    sigPreview.style.display = "none";
    sigPh.style.display = "block";
    sigArea.classList.remove("has-img");
    sigRm.style.display = "none";
    selId = null;
    renderTbl(allUsers);
}}

document.getElementById("clear-btn").addEventListener("click", clearForm);
document.getElementById("al").addEventListener("change", showLvDesc);

// ──── بارگذاری و جستجوی کاربران ────
async function loadUsers() {{
    try {{
        const r = await fetch("/module/admin/users/list");
        const d = await r.json();
        if (d.success) {{
            allUsers = d.users || [];
            document.getElementById("tc2").textContent = allUsers.length + " کاربر";
            renderTbl(allUsers);
        }}
    }} catch (e) {{ console.error(e); }}
}}

function filterTbl() {{
    const q = document.getElementById("si").value.trim().toLowerCase();
    renderTbl(allUsers.filter(u =>
        (u.FullName || "").toLowerCase().includes(q) ||
        (u.Username || "").includes(q) ||
        (u.AccessLevelName || "").toLowerCase().includes(q) ||
        (u.unit_name || "").toLowerCase().includes(q) ||
        (u.department_name || "").toLowerCase().includes(q)
    ));
}}

document.getElementById("si").addEventListener("input", filterTbl);

function renderTbl(users) {{
    const tb = document.getElementById("tb");
    if (!users.length) {{
        tb.innerHTML = `<tr><td colspan="8" style="text-align:center;color:#94a3b8;">کاربری یافت نشد</td></tr>`;
        return;
    }}
    tb.innerHTML = users.map(u => {{
        const esc = (str) => escapeHtml(String(str || ""));
        return `<tr class="${{selId == u.UserID ? "sel" : ""}}" data-id="${{u.UserID}}">
            <td>${{u.UserID}}</td>
            <td style="text-align:right;">${{esc(u.FullName)}}</td>
            <td>${{esc(u.Username)}}</td>
            <td>${{esc(u.AccessLevelName)}}</td>
            <td>${{esc(u.unit_name || "—")}}</td>
            <td>${{esc(u.department_name || "—")}}</td>
            <td>${{u.emza_path ? "✅" : "—"}}</td>
            <td>${{u.IsActive == 1 ? "<span class='act'>فعال</span>" : "<span class='inact'>غیرفعال</span>"}}</td>
        </tr>`;
    }}).join("");

    tb.querySelectorAll("tr[data-id]").forEach(row => {{
        row.addEventListener("click", () => onRow(Number(row.dataset.id)));
    }});
}}

document.getElementById("ecb").addEventListener("change", function() {{
    editMode = this.checked;
}});

async function onRow(uid) {{
    if (!editMode) return;
    selId = uid;
    try {{
        const r = await fetch("/module/admin/users/get/" + uid);
        const d = await r.json();
        if (!d.success) {{ toast(d.message, "error"); return; }}
        const u = d.user;
        document.getElementById("eid").value = u.UserID;
        document.getElementById("fn").value = u.FullName || "";
        document.getElementById("un").value = u.Username || "";
        document.getElementById("pw").value = "";
        document.getElementById("pw").required = false;
        document.getElementById("ph").textContent = "(برای تغییر رمز پر کنید)";
        document.getElementById("al").value = u.AccessLevelID || "";
        document.getElementById("ia").checked = u.IsActive == 1;
        document.getElementById("form-title").textContent = "✏️ ویرایش کاربر";
        document.getElementById("st").textContent = "💾 بروزرسانی";
        showLvDesc();

        unitSel = (u.unit_ids || [u.postmodir]).filter(Boolean).map(Number);
        if (u.postmodir && !unitSel.includes(Number(u.postmodir))) unitSel.push(Number(u.postmodir));
        unitSel = [...new Set(unitSel)];
        renderTags("unit");

        deptSel = (u.dep_ids || [u.dep_id]).filter(Boolean).map(Number);
        if (u.dep_id && !deptSel.includes(Number(u.dep_id))) deptSel.push(Number(u.dep_id));
        deptSel = [...new Set(deptSel)];
        renderTags("dept");

        if (u.emza_path) {{
            const sigR = await fetch("/module/admin/users/signature/" + u.UserID);
            const sigD = await sigR.json();
            if (sigD.success) {{
                sigPreview.src = sigD.data;
                sigPreview.style.display = "block";
                sigPh.style.display = "none";
                sigArea.classList.add("has-img");
                sigRm.style.display = "inline-flex";
            }}
        }} else {{
            sigFile.value = "";
            sigPreview.style.display = "none";
            sigPh.style.display = "block";
            sigArea.classList.remove("has-img");
            sigRm.style.display = "none";
        }}

        renderTbl(allUsers);
        document.getElementById("form-card").scrollIntoView({{ behavior: "smooth", block: "start" }});
        toast("✅ اطلاعات بارگذاری شد", "success");
    }} catch (e) {{ toast("خطا", "error"); }}
}}

document.addEventListener("DOMContentLoaded", () => {{
    renderTags("unit");
    renderTags("dept");
    loadUsers();
}});
</script>
</body>
</html>"""
    return html
    



