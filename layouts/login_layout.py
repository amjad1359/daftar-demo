"""
صفحه لاگین - HTML + CSS
"""
def get_hospital_logo():
    from models.database import query
    res = query(
        "SELECT setting_value FROM site_settings WHERE setting_key = 'hospital_logo'",
        fetch_one=True
    )
    return res['setting_value'] if res else None


LOGIN_HTML = '''
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود | دفتر پرستاری</title>
    <meta name="csrf-token" content="{{ csrf_token }}">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:Tahoma,Arial,sans-serif}
        body{background:linear-gradient(135deg,#1e3a8a,#3b82f6);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
        .login-card{background:#fff;border-radius:20px;padding:40px 30px;width:100%;max-width:400px;box-shadow:0 20px 60px rgba(0,0,0,0.3)}
        .login-card .icon{font-size:50px;text-align:center;margin-bottom:15px}
        .login-card h2{font-size:22px;font-weight:bold;color:#1e293b;text-align:center;margin-bottom:5px}
        .login-card p{font-size:13px;color:#94a3b8;text-align:center;margin-bottom:25px}
        .login-card label{font-size:13px;font-weight:bold;color:#64748b;display:block;margin-bottom:5px}
        .login-card input{width:100%;padding:13px 15px;border:2px solid #e2e8f0;border-radius:12px;font-size:14px;background:#f8fafc;margin-bottom:15px;transition:0.2s}
        .login-card input:focus{border-color:#3b82f6;background:#fff;outline:none;box-shadow:0 0 0 3px rgba(59,130,246,0.1)}
        .login-card button{width:100%;padding:14px;border:none;border-radius:12px;font-size:16px;font-weight:bold;color:#fff;background:linear-gradient(135deg,#1e3a8a,#3b82f6);cursor:pointer;transition:0.2s}
        .login-card button:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(30,58,138,0.4)}
        .login-card .hint{text-align:center;font-size:11px;color:#94a3b8;margin-top:10px}
        .alert{padding:12px;border-radius:12px;font-size:13px;text-align:center;margin-top:15px;display:none}
        .alert.show{display:block}
        .alert.error{background:#fee2e2;color:#991b1b}
        .alert.warn{background:#fef3c7;color:#92400e}
    </style>
</head>
<body>
    <div class="login-card">
          
        {% if logo_url %}
        <div style="text-align:center; margin-bottom:20px;">
            <img src="{{ logo_url }}" alt="لوگوی بیمارستان" style="max-height:80px; max-width:200px;">
        </div>
        {% endif %}
    

        {% if logo_url %}
            <!-- لوگوی سفارشی نمایش داده می‌شود -->
        {% else %}
            <div class="icon">🏥</div>
        {% endif %}    
    
        
        <h2>سامانه دفتر پرستاری</h2>
        <p>برای ادامه، وارد حساب کاربری خود شوید</p>
        <form method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            <label>👤 نام کاربری (کد ملی)</label>
            <input type="text" name="username" placeholder="کد ملی ۱۰ رقمی" required autofocus>
            <label>🔑 رمز عبور</label>
            <input type="password" name="password" placeholder="••••••••" required>
            <button type="submit">⚡ ورود به سیستم</button>
        </form>
        <p class="hint">⏎ کلید Enter را بزنید</p>
        {% if error %}
        <div class="alert {{ 'warn' if 'خالی' in error else 'error' }} show">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
'''