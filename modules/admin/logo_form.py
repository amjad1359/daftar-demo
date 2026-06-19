"""
مدیریت لوگوی بیمارستان – پنل ادمین
"""
import os
import jdatetime
from datetime import datetime
from werkzeug.utils import secure_filename
from models.database import query, get_connection
from flask import jsonify, request


UPLOAD_DIR = "uploads/logo"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}


def get_logo_form(user):
    """صفحه مدیریت لوگو و نام مراکز"""

    # خواندن مقادیر فعلی از دیتابیس
    logo_path = None
    center_name = ''
    sub_center_name = ''

    try:
        logo_res = query(
            "SELECT setting_value FROM site_settings WHERE setting_key = 'hospital_logo'",
            fetch_one=True
        )
        if logo_res and logo_res['setting_value']:
            logo_path = logo_res['setting_value']

        center_res = query(
            "SELECT setting_value FROM site_settings WHERE setting_key = 'center_name'",
            fetch_one=True
        )
        if center_res:
            center_name = center_res['setting_value']

        sub_center_res = query(
            "SELECT setting_value FROM site_settings WHERE setting_key = 'sub_center_name'",
            fetch_one=True
        )
        if sub_center_res:
            sub_center_name = sub_center_res['setting_value']
    except:
        pass

    # پیش‌نمایش لوگو
    logo_display = f"/{logo_path}" if logo_path else ""
    logo_preview = f'<img src="{logo_display}" alt="لوگوی بیمارستان" style="max-height:120px;">' if logo_path else '<div class="empty">هنوز لوگویی بارگذاری نشده است</div>'

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {{
        --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
        --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
        --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
        --bg: #f1f5f9; --white: #fff; --radius: 12px; --transition: 0.2s ease;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial, sans-serif; direction:rtl; background:var(--bg); color:var(--dark); }}
    .fade-in {{ animation:fadeIn 0.4s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .container {{ max-width:800px; margin:0 auto; padding:20px; }}
    .page-header {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color:white; border-radius:var(--radius); padding:22px 28px; margin-bottom:22px;
        display:flex; justify-content:space-between; align-items:center;
        box-shadow:0 8px 30px rgba(30,58,138,0.25);
    }}
    .page-header h2 {{ font-size:22px; }}
    .back-btn {{ color:white; text-decoration:none; padding:8px 16px; border:1px solid rgba(255,255,255,0.4); border-radius:8px; }}
    .back-btn:hover {{ background:rgba(255,255,255,0.2); }}

    .card {{
        background:var(--white); border-radius:var(--radius); padding:25px;
        border:1px solid var(--border); box-shadow:0 2px 8px rgba(0,0,0,0.05);
        margin-bottom:20px;
    }}
    .card-title {{ font-weight:bold; color:var(--dark); margin-bottom:15px; padding-bottom:10px; border-bottom:2px solid var(--border); }}

    .upload-area {{
        border:2px dashed var(--border); border-radius:12px; padding:40px;
        text-align:center; cursor:pointer; transition:all 0.3s ease; background:var(--bg);
        margin-bottom:20px;
    }}
    .upload-area:hover, .upload-area.dragover {{ border-color:var(--primary-light); background:#eef2ff; }}
    .upload-area input[type="file"] {{ display:none; }}
    .upload-icon {{ font-size:48px; margin-bottom:10px; }}
    .upload-hint {{ font-size:12px; color:var(--gray); }}

    .preview-box {{
        text-align:center; padding:20px; background:var(--white);
        border:1px solid var(--border); border-radius:8px; margin-bottom:20px;
    }}
    .preview-box img {{ max-height:120px; max-width:100%; }}
    .preview-box .empty {{ color:var(--light-gray); padding:30px; }}

    .form-group {{ margin-bottom:18px; }}
    .form-group label {{ display:block; font-size:13px; font-weight:600; color:var(--gray); margin-bottom:6px; }}
    .form-input {{
        width:100%; padding:12px 14px; border:2px solid var(--border);
        border-radius:8px; font-size:14px; font-family:Tahoma; background:var(--white);
        transition:var(--transition);
    }}
    .form-input:focus {{ border-color:var(--primary-light); outline:none; }}

    .btn {{
        display:inline-flex; align-items:center; justify-content:center; gap:6px;
        padding:12px 24px; border:none; border-radius:10px; font-size:14px;
        font-weight:600; cursor:pointer; font-family:Tahoma; transition:var(--transition);
    }}
    .btn-primary {{ background:linear-gradient(135deg, var(--primary), var(--primary-light)); color:white; }}
    .btn-primary:hover {{ transform:translateY(-2px); box-shadow:0 6px 20px rgba(30,58,138,0.3); }}
    .btn-danger {{ background:var(--danger); color:white; }}

    .toast-box {{ position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; display:flex; flex-direction:column; gap:8px; }}
    .toast {{ padding:12px 18px; border-radius:10px; color:white; font-size:13px; font-weight:600; box-shadow:0 8px 25px rgba(0,0,0,0.2); animation:slideDown 0.4s ease; }}
    .toast.ok {{ background:#10b981; }}
    .toast.err {{ background:#ef4444; }}
    @keyframes slideDown {{ from {{ opacity:0; transform:translateY(-25px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .row {{ display:flex; gap:10px; }}
    .flex-1 {{ flex:1; }}
</style>
</head>
<body>
<div class="toast-box" id="toastBox"></div>
<div class="container fade-in">
    <div class="page-header">
        <h2>🏥 مدیریت لوگو و نام مراکز درمانی</h2>
        <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
    </div>

    <!-- کارت نام مراکز -->
    <div class="card">
        <div class="card-title">🏛️ نام مراکز درمانی</div>
        <div class="form-group">
            <label>نام مرکز اصلی (منطقه‌ای)</label>
            <input type="text" id="centerName" class="form-input" value="{center_name}" placeholder="مثلاً دانشگاه علوم پزشکی غرب ">
        </div>
        <div class="form-group">
            <label>نام مرکز زیرمجموعه (بیمارستان)</label>
            <input type="text" id="subCenterName" class="form-input" value="{sub_center_name}" placeholder="مثلا بیمارستان امام حسین ع ">
        </div>
    </div>

    <!-- کارت لوگو -->
    <div class="card">
        <div class="card-title">📷 لوگوی بیمارستان</div>
        <div class="preview-box" id="previewBox">
            {logo_preview}
        </div>

        <div class="upload-area" id="dropZone">
            <div class="upload-icon">🏞️</div>
            <div>فایل لوگو را اینجا رها کنید یا کلیک کنید</div>
            <div class="upload-hint">فرمت‌های مجاز: PNG, JPG, JPEG, GIF, SVG (حداکثر ۵ مگابایت)</div>
            <input type="file" id="fileInput" accept=".png,.jpg,.jpeg,.gif,.svg">
        </div>

        <div class="row">
            <button class="btn btn-primary flex-1" onclick="saveAllSettings()">
                <span id="saveText">💾 ذخیره همه تنظیمات</span>
                <span id="saveLoading" style="display:none;">⏳...</span>
            </button>
            <button class="btn btn-danger" onclick="deleteLogo()">🗑️ حذف لوگو</button>
        </div>
    </div>
</div>

<script>
    let selectedFile = null;

    const dropZone = document.getElementById('dropZone');
    dropZone.addEventListener('click', () => document.getElementById('fileInput').click());
    dropZone.addEventListener('dragover', (e) => {{ e.preventDefault(); dropZone.classList.add('dragover'); }});
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {{
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    }});
    document.getElementById('fileInput').addEventListener('change', (e) => handleFiles(e.target.files));

    function handleFiles(files) {{
        if (!files.length) return;
        const file = files[0];
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['png','jpg','jpeg','gif','svg'].includes(ext)) {{
            toast('فرمت فایل مجاز نیست', 'err');
            return;
        }}
        if (file.size > 5 * 1024 * 1024) {{
            toast('حجم فایل بیش از ۵ مگابایت است', 'err');
            return;
        }}
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {{
            document.getElementById('previewBox').innerHTML = `<img src="${{e.target.result}}" alt="پیش‌نمایش">`;
        }};
        reader.readAsDataURL(file);
    }}

    function toast(msg, type) {{
        const box = document.getElementById('toastBox');
        const t = document.createElement('div');
        t.className = 'toast ' + (type==='ok'?'ok':'err');
        t.innerHTML = '<span>' + (type==='ok'?'✅':'❌') + '</span><span>' + msg + '</span>';
        box.appendChild(t);
        setTimeout(() => t.remove(), 4000);
    }}

    async function saveAllSettings() {{
        const centerName = document.getElementById('centerName').value.trim();
        const subCenterName = document.getElementById('subCenterName').value.trim();

        const formData = new FormData();
        // اگر فایلی انتخاب شده باشد
        if (selectedFile) {{
            formData.append('logo', selectedFile);
        }}
        formData.append('centerName', centerName);
        formData.append('subCenterName', subCenterName);

        document.getElementById('saveText').style.display = 'none';
        document.getElementById('saveLoading').style.display = 'inline';

        try {{
            const res = await fetch('/module/admin/logo/save', {{ method:'POST', body:formData }});
            const data = await res.json();
            if (data.success) {{
                toast('✅ تنظیمات با موفقیت ذخیره شدند', 'ok');
                setTimeout(() => location.reload(), 1000);
            }} else {{
                toast('⛔ ' + data.message, 'err');
            }}
        }} catch(e) {{
            toast('خطا در ارتباط با سرور', 'err');
        }} finally {{
            document.getElementById('saveText').style.display = 'inline';
            document.getElementById('saveLoading').style.display = 'none';
        }}
    }}

    async function deleteLogo() {{
        if (!confirm('آیا از حذف لوگو اطمینان دارید؟')) return;
        try {{
            const res = await fetch('/module/admin/logo/delete', {{ method:'POST' }});
            const data = await res.json();
            if (data.success) {{
                toast('✅ لوگو حذف شد', 'ok');
                setTimeout(() => location.reload(), 800);
            }} else {{
                toast('⛔ ' + data.message, 'err');
            }}
        }} catch(e) {{
            toast('خطا در ارتباط با سرور', 'err');
        }}
    }}
</script>
</body>
</html>'''
    return html


def save_logo(user, file):
    """
    ذخیره فایل لوگو و نام مراکز در دیتابیس.
    اگر فایلی ارسال نشود، فقط نام مراکز بروز می‌شود.
    """
    # دریافت فایل (ممکن است None باشد)
    logo_file = request.files.get('logo')
    
    # ========== ۱. اگر فایلی ارسال شده باشد، بررسی و ذخیره شود ==========
    if logo_file and logo_file.filename != '':
        ext = logo_file.filename.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return {'success': False, 'message': 'فرمت فایل مجاز نیست'}
        
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"logo.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        logo_file.save(filepath)
        
        # ذخیره مسیر لوگو در دیتابیس
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO site_settings (setting_key, setting_value)
                   VALUES ('hospital_logo', %s)
                   ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)""",
                (f"uploads/logo/{filename}",)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'خطا در ذخیره لوگو: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    # ========== ۲. همیشه نام مراکز را ذخیره کن ==========
    center_name = request.form.get('centerName', '').strip()
    sub_center_name = request.form.get('subCenterName', '').strip()

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO site_settings (setting_key, setting_value)
               VALUES ('center_name', %s)
               ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)""",
            (center_name,)
        )
        cursor.execute(
            """INSERT INTO site_settings (setting_key, setting_value)
               VALUES ('sub_center_name', %s)
               ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)""",
            (sub_center_name,)
        )
        conn.commit()
        return {'success': True, 'message': 'تنظیمات با موفقیت ذخیره شدند'}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'خطا در ذخیره نام مراکز: {str(e)}'}
    finally:
        cursor.close()
        conn.close()



def delete_logo():
    """حذف لوگو از دیتابیس و دیسک"""
    current_logo = query(
        "SELECT setting_value FROM site_settings WHERE setting_key = 'hospital_logo'",
        fetch_one=True
    )
    if current_logo:
        logo_path = current_logo['setting_value']
        if os.path.exists(logo_path):
            os.remove(logo_path)
        query(
            "DELETE FROM site_settings WHERE setting_key = 'hospital_logo'",
            commit=True
        )
    return {'success': True, 'message': 'لوگو حذف شد'}
    
    