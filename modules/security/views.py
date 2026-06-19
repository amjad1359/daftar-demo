"""
ماژول امنیت – تغییر رمز عبور
حداقل ۴ کاراکتر (حرف یا عدد)
نسخه Flask با AJAX و Toast
"""

from models.database import query
from utils.audit import log_action
from werkzeug.security import check_password_hash, generate_password_hash   # <-- اضافه‌شده


def get_security_page(user):
    """صفحه تغییر رمز عبور"""

    full_name = user.get('FullName', 'کاربر')
    username = user.get('Username', '')

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
        --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
        --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
        --bg: #f1f5f9; --white: #fff; --radius: 16px; --transition: 0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.5s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(15px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:500px; margin:0 auto; padding:20px; }}

    .page-header {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color:white; border-radius:var(--radius); padding:25px 30px; margin-bottom:25px;
        text-align:center; box-shadow:0 10px 40px rgba(30,58,138,0.25);
    }}
    .page-header .icon {{ font-size:48px; margin-bottom:10px; }}
    .page-header h2 {{ font-size:22px; margin:0 0 5px 0; }}
    .page-header p {{ opacity:0.8; font-size:13px; }}

    .card {{
        background:var(--white); border-radius:var(--radius); padding:30px;
        border:1px solid var(--border); box-shadow:0 2px 8px rgba(0,0,0,0.05);
    }}

    .user-info {{
        display:flex; align-items:center; gap:12px;
        background:var(--bg); padding:14px 18px; border-radius:12px;
        margin-bottom:25px; border-right:4px solid var(--primary);
    }}
    .user-avatar {{
        width:44px; height:44px; background:var(--primary); color:white;
        border-radius:50%; display:flex; align-items:center; justify-content:center;
        font-size:20px; font-weight:bold; flex-shrink:0;
    }}
    .user-detail {{ flex:1; }}
    .user-detail .name {{ font-weight:bold; font-size:14px; }}
    .user-detail .uid {{ font-size:11px; color:var(--gray); }}

    .form-group {{ margin-bottom:20px; position:relative; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:7px; }}
    .form-group input {{
        width:100%; padding:14px 45px 14px 16px;
        border:2px solid var(--border); border-radius:10px;
        font-size:14px; font-family:inherit; transition:var(--transition);
    }}
    .form-group input:focus {{
        border-color:var(--primary-light); outline:none;
        box-shadow:0 0 0 4px rgba(59,130,246,0.1);
    }}
    .form-group .toggle-password {{
        position:absolute; right:14px; top:38px; font-size:16px;
        cursor:pointer; color:var(--gray); transition:var(--transition);
        z-index:2;
    }}
    .form-group .toggle-password:hover {{ color:var(--primary); }}

    .hint {{
        font-size:11px; color:var(--light-gray); margin-top:5px;
    }}

    .btn {{
        width:100%; padding:14px; border:none; border-radius:10px;
        font-size:15px; font-weight:700; cursor:pointer; font-family:inherit;
        transition:var(--transition); display:flex; align-items:center;
        justify-content:center; gap:8px;
    }}
    .btn-primary {{
        background:linear-gradient(135deg, var(--primary), var(--primary-light));
        color:white; box-shadow:0 6px 20px rgba(30,58,138,0.2);
    }}
    .btn-primary:hover {{ transform:translateY(-2px); box-shadow:0 10px 30px rgba(30,58,138,0.3); }}
    .btn-primary:disabled {{ opacity:0.5; cursor:not-allowed; transform:none; }}

    .message {{
        padding:14px 18px; border-radius:10px; font-size:13px;
        margin-bottom:20px; display:none; text-align:center;
    }}
    .message.show {{ display:block; animation:fadeIn 0.3s ease; }}
    .message.success {{ background:#d1fae5; color:#065f46; border-right:4px solid #10b981; }}
    .message.error {{ background:#fee2e2; color:#991b1b; border-right:4px solid #ef4444; }}

    /* Toast */
    .toast-box {{
        position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000;
        display:flex; flex-direction:column; gap:8px; pointer-events:none;
    }}
    .toast {{
        display:flex; align-items:center; gap:10px; padding:14px 22px;
        border-radius:12px; color:white; font-size:14px; font-weight:600;
        box-shadow:0 10px 30px rgba(0,0,0,0.2); animation:slideDown 0.4s ease;
        pointer-events:auto;
    }}
    .toast.ok {{ background:linear-gradient(135deg, #059669, #10b981); }}
    .toast.err {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
    .toast .close {{ margin-right:auto; cursor:pointer; opacity:0.7; }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-25px); }} to {{ opacity:1; transform:translateY(0); }} }}

    @media (max-width:600px) {{
        .container {{ padding:12px; }}
        .card {{ padding:20px; }}
    }}
</style>
</head>
<body>
<div class="toast-box" id="toast-box"></div>

<div class="container fade-in">
    <div class="page-header">
        <div class="icon">🔐</div>
        <h2>تغییر رمز عبور</h2>
        <p>امنیت حساب کاربری خود را حفظ کنید</p>
    </div>

    <div class="card">
        <div class="user-info">
            <div class="user-avatar">{full_name[0] if full_name else '?'}</div>
            <div class="user-detail">
                <div class="name">{full_name}</div>
                <div class="uid">👤 نام کاربری: {username}</div>
            </div>
        </div>

        <div id="message" class="message"></div>

        <form id="password-form" onsubmit="return false;">
            <div class="form-group">
                <label>🔒 رمز عبور فعلی</label>
                <input type="password" id="current-password" placeholder="رمز عبور فعلی" autocomplete="current-password">
                <span class="toggle-password" onclick="togglePass('current-password', this)">👁️</span>
            </div>

            <div class="form-group">
                <label>🔑 رمز عبور جدید</label>
                <input type="password" id="new-password" placeholder="حداقل ۴ کاراکتر" autocomplete="new-password">
                <span class="toggle-password" onclick="togglePass('new-password', this)">👁️</span>
                <div class="hint">حداقل ۴ حرف یا عدد</div>
            </div>

            <div class="form-group">
                <label>✅ تکرار رمز عبور جدید</label>
                <input type="password" id="confirm-password" placeholder="دوباره بنویسید" autocomplete="new-password">
                <span class="toggle-password" onclick="togglePass('confirm-password', this)">👁️</span>
            </div>

            <button class="btn btn-primary" id="submit-btn" onclick="changePassword()">
                <span id="submit-text">🔄 بروزرسانی رمز عبور</span>
                <span id="submit-loading" style="display:none;">⏳ در حال بررسی...</span>
            </button>
        </form>
    </div>
</div>

<script>
    function toast(msg, type) {{
        const box = document.getElementById('toast-box');
        const t = document.createElement('div');
        t.className = 'toast ' + (type==='ok'?'ok':'err');
        t.innerHTML = '<span>' + (type==='ok'?'✅':'❌') + '</span><span>' + msg + '</span><span class="close" onclick="this.parentElement.remove()">✕</span>';
        box.appendChild(t);
        setTimeout(function() {{ if(t.parentElement) t.remove(); }}, 4000);
    }}

    function showMessage(msg, type) {{
        const el = document.getElementById('message');
        el.textContent = msg;
        el.className = 'message ' + type + ' show';
        setTimeout(function() {{ el.classList.remove('show'); }}, 5000);
    }}

    function togglePass(id, icon) {{
        const inp = document.getElementById(id);
        if (inp.type === 'password') {{
            inp.type = 'text';
            icon.textContent = '🙈';
        }} else {{
            inp.type = 'password';
            icon.textContent = '👁️';
        }}
    }}

    async function changePassword() {{
        const current = document.getElementById('current-password').value;
        const newPass = document.getElementById('new-password').value;
        const confirm = document.getElementById('confirm-password').value;

        // اعتبارسنجی
        if (!current) {{ showMessage('⛔ رمز عبور فعلی را وارد کنید', 'error'); return; }}
        if (!newPass) {{ showMessage('⛔ رمز عبور جدید را وارد کنید', 'error'); return; }}
        if (newPass.length < 4) {{ showMessage('⛔ رمز عبور جدید باید حداقل ۴ کاراکتر باشد', 'error'); return; }}
        if (newPass !== confirm) {{ showMessage('⛔ تکرار رمز جدید مطابقت ندارد', 'error'); return; }}
        if (newPass === current) {{ showMessage('⛔ رمز جدید با رمز فعلی یکسان است', 'error'); return; }}

        const submitText = document.getElementById('submit-text');
        const submitLoading = document.getElementById('submit-loading');
        const submitBtn = document.getElementById('submit-btn');
        submitText.style.display = 'none';
        submitLoading.style.display = 'inline';
        submitBtn.disabled = true;

        try {{
            const fd = new FormData();
            fd.append('current_password', current);
            fd.append('new_password', newPass);

            const r = await fetch('/module/security/change-password', {{ method:'POST', body:fd }});
            const d = await r.json();

            if (d.success) {{
                showMessage('✅ ' + d.message, 'success');
                toast(d.message, 'ok');
                document.getElementById('password-form').reset();
            }} else {{
                showMessage('⛔ ' + d.message, 'error');
            }}
        }} catch(e) {{
            showMessage('⛔ خطا در ارتباط با سرور', 'error');
        }} finally {{
            submitText.style.display = 'inline';
            submitLoading.style.display = 'none';
            submitBtn.disabled = false;
        }}
    }}
</script>
</body>
</html>'''
    return html


def change_user_password(user, form_data):
    """تغییر رمز عبور - حداقل ۴ کاراکتر، با هش"""
    user_id = user.get('UserID', 0)
    current_password = form_data.get('current_password', '')
    new_password = form_data.get('new_password', '')

    if not current_password or not new_password:
        return {'success': False, 'message': 'همه فیلدها الزامی هستند'}

    if len(new_password) < 4:
        return {'success': False, 'message': 'رمز عبور جدید باید حداقل ۴ کاراکتر باشد'}

    if current_password == new_password:
        return {'success': False, 'message': 'رمز عبور جدید با رمز فعلی یکسان است'}

    # دریافت هش فعلی کاربر از دیتابیس
    user_record = query(
        "SELECT UserID, PasswordHash FROM users WHERE UserID = %s",
        params=(user_id,),
        fetch_one=True
    )
    if not user_record:
        return {'success': False, 'message': 'کاربر یافت نشد'}

    # بررسی رمز فعلی با تابع check_password_hash (و fallback plain text)
    stored = user_record['PasswordHash']
    if not check_password_hash(stored, current_password):
        if stored != current_password:   # fallback برای رمزهای قدیمی
            log_action("Change Password Failed", user_id=user_id, status="Failed", error_msg="Wrong current password")
            return {'success': False, 'message': 'رمز عبور فعلی اشتباه است'}

    # ذخیره رمز جدید به صورت هش
    hashed_new = generate_password_hash(new_password)
    try:
        query("UPDATE users SET PasswordHash = %s WHERE UserID = %s", params=(hashed_new, user_id), commit=True)
        log_action("Change Password", user_id=user_id, status="Success")
        return {'success': True, 'message': '✅ رمز عبور با موفقیت تغییر یافت'}
    except Exception as e:
        log_action("Change Password Failed", user_id=user_id, status="Failed", error_msg=str(e))
        return {'success': False, 'message': f'خطا: {str(e)}'}
        
        