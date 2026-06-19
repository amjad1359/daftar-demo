"""
فرم ثبت تزریق خون و فرآورده‌های خونی - سوپروایزر
نسخه کامل Flask با AJAX، Toast و قابلیت افزودن/حذف فرآورده‌ها
"""

from models.database import query, get_connection
import jdatetime
from datetime import datetime
import json
from utils.auto_log import log_crud

BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-", "Unknown"]
PRODUCT_TYPES = ["Packed Cell", "FFP", "Platelet", "Cryo", "Whole Blood", "Washed RBC"]


def get_blood_form(user):
    """صفحه اصلی ثبت تزریق خون و فرآورده‌ها"""

    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')

    active_shift = query(
        "SELECT ID_shift, tarkib FROM shift_namt ORDER BY ID_shift DESC LIMIT 1",
        fetch_one=True
    )
    if not active_shift:
        return '''
        <div class="content-card fade-in">
            <div style="text-align:center;padding:60px;">
                <div style="font-size:64px;">⚠️</div>
                <h3>شیفت فعالی یافت نشد</h3>
                <a href="/module/supervisor/shift" class="btn btn-primary">📅 ثبت شیفت</a>
            </div>
        </div>'''

    shift_id = active_shift['ID_shift']
    shift_name = active_shift['tarkib']

    departments = query(
        "SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh",
        fetch_all=True
    ) or []

    dept_options = '<option value="">--- انتخاب بخش ---</option>'
    for d in departments:
        dept_options += f'<option value="{d["ID_nam_bakhsh"]}">{d["nam_bakhsh"]}</option>'

    bg_options = ''.join([f'<option value="{bg}">{bg}</option>' for bg in BLOOD_GROUPS])

    patients = query(
        "SELECT ID_blood, nam_bimar, shomar_parvandeh FROM tbl_blood_trans WHERE nam_shift = %s ORDER BY ID_blood DESC",
        params=(shift_id,), fetch_all=True
    ) or []

    # ========== HTML ==========
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --primary: #1e3a8a; --primary-light: #3b82f6; --success: #10b981;
                --danger: #ef4444; --warning: #f59e0b; --dark: #1e293b;
                --gray: #64748b; --light-gray: #94a3b8; --border: #e2e8f0;
                --bg-light: #f8fafc; --radius: 12px; --transition: 0.2s ease;
            }}
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family:Tahoma,Arial,sans-serif; direction:rtl; background:#f1f5f9; color:var(--dark); }}
            .fade-in {{ animation:fadeIn 0.4s ease; }}
            @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

            .content-card {{ max-width:1400px; margin:0 auto; }}

            .bl-header {{
                background:linear-gradient(135deg, #991b1b, #dc2626);
                color:white; padding:25px 30px; border-radius:16px;
                margin-bottom:25px; display:flex; justify-content:space-between;
                align-items:center; box-shadow:0 8px 30px rgba(153,27,27,0.3);
            }}
            .bl-header h2 {{ font-size:22px; margin:0 0 5px 0; }}
            .bl-header p {{ opacity:0.85; font-size:13px; margin:0; }}
            .shift-badge {{
                background:rgba(255,255,255,0.15); padding:10px 20px;
                border-radius:30px; font-size:14px; font-weight:bold;
                border:1px solid rgba(255,255,255,0.2);
            }}
            .back-btn {{
                color:white; text-decoration:none; padding:8px 16px;
                border:1px solid rgba(255,255,255,0.3); border-radius:8px;
                font-size:13px; transition:var(--transition);
            }}
            .back-btn:hover {{ background:rgba(255,255,255,0.15); }}

            .tabs {{ display:flex; gap:5px; margin-bottom:25px; border-bottom:2px solid var(--border); }}
            .tab {{ padding:12px 24px; font-size:14px; font-weight:600; border:none; background:none;
                color:var(--light-gray); cursor:pointer; border-bottom:2px solid transparent;
                margin-bottom:-2px; transition:var(--transition); font-family:Tahoma; }}
            .tab:hover {{ color:var(--dark); }}
            .tab.active {{ color:var(--primary-light); border-bottom-color:var(--primary-light); }}
            .tab-content {{ display:none; }}
            .tab-content.active {{ display:block; }}

            .main-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:25px; }}

            .form-panel {{
                background:white; border-radius:14px; padding:25px;
                border:1px solid var(--border);
            }}
            .form-title {{
                font-size:16px; font-weight:bold; color:var(--dark);
                margin-bottom:20px; padding-bottom:12px;
                border-bottom:2px solid var(--border);
            }}

            .form-group {{ margin-bottom:18px; }}
            .form-group label {{
                display:block; font-size:13px; font-weight:600;
                color:var(--gray); margin-bottom:6px;
            }}
            .form-select, .form-input {{
                width:100%; padding:12px 14px; border:2px solid var(--border);
                border-radius:10px; font-size:14px; font-family:Tahoma;
                background:white; transition:var(--transition);
            }}
            .form-select:focus, .form-input:focus {{
                border-color:var(--primary-light); outline:none;
                box-shadow:0 0 0 3px rgba(59,130,246,0.1);
            }}

            .btn {{
                display:inline-flex; align-items:center; justify-content:center;
                gap:6px; padding:12px 24px; border:none; border-radius:10px;
                font-size:14px; font-weight:600; cursor:pointer;
                font-family:Tahoma; transition:var(--transition); text-decoration:none;
            }}
            .btn-primary {{
                background:linear-gradient(135deg, var(--primary), var(--primary-light));
                color:white; box-shadow:0 4px 15px rgba(30,58,138,0.2);
            }}
            .btn-primary:hover {{ transform:translateY(-2px); box-shadow:0 8px 25px rgba(30,58,138,0.3); }}
            .btn-danger {{ background:var(--danger); color:white; }}
            .btn-sm {{ padding:6px 12px; font-size:12px; border-radius:8px; }}
            .btn-xs {{ padding:4px 10px; font-size:11px; border-radius:6px; }}

            .product-list {{ margin-top:15px; }}
            .product-item {{
                display:flex; gap:10px; align-items:center;
                background:var(--bg-light); border:1px solid var(--border);
                padding:10px; border-radius:8px; margin-bottom:8px;
            }}
            .product-item span {{ flex:1; font-size:13px; color:var(--dark); }}
            .add-product-row {{
                display:flex; gap:10px; align-items:center;
                margin-top:15px;
            }}
            .add-product-row select, .add-product-row input {{
                width:auto; flex:1;
            }}

            .list-panel {{
                background:white; border-radius:14px; padding:25px;
                border:1px solid var(--border); max-height:600px; overflow-y:auto;
            }}
            .patient-item {{
                background:var(--bg-light); border:1px solid var(--border);
                border-radius:10px; padding:15px; margin-bottom:10px;
                transition:var(--transition);
            }}
            .patient-item:hover {{ border-color:var(--primary-light); }}
            .patient-name {{ font-weight:bold; font-size:14px; color:var(--dark); }}
            .patient-file {{ font-size:12px; color:var(--gray); }}
            .patient-actions {{ display:flex; gap:5px; margin-top:10px; justify-content:flex-end; }}

            .toast-container {{
                position:fixed; top:20px; left:50%; transform:translateX(-50%);
                z-index:10000; display:flex; flex-direction:column; gap:10px;
                pointer-events:none;
            }}
            .toast {{
                display:flex; align-items:center; gap:12px;
                padding:14px 22px; border-radius:12px; color:white;
                font-size:14px; font-weight:600;
                box-shadow:0 10px 30px rgba(0,0,0,0.2);
                animation:slideDown 0.4s ease; pointer-events:auto;
            }}
            .toast.success {{ background:linear-gradient(135deg, #059669, #10b981); }}
            .toast.error {{ background:linear-gradient(135deg, #dc2626, #ef4444); }}
            .toast .toast-close {{ margin-right:auto; cursor:pointer; opacity:0.7; font-size:16px; }}
            @keyframes slideDown {{
                from {{ opacity:0; transform:translateY(-30px); }}
                to {{ opacity:1; transform:translateY(0); }}
            }}

            @media (max-width:768px) {{
                .main-grid {{ grid-template-columns:1fr; }}
                .bl-header {{ flex-direction:column; gap:15px; text-align:center; }}
            }}
        </style>
    </head>
    <body>
        <div class="toast-container" id="toast-container"></div>

        <div class="content-card fade-in">
            <div class="bl-header">
                <div>
                    <h2>🩸 ثبت ترانسفوزیون خون و فرآورده‌ها</h2>
                    <p>شیفت: {shift_name}</p>
                </div>
                <a href="/module/supervisor" class="back-btn">⬅️ بازگشت</a>
            </div>

            <div class="tabs">
                <button class="tab active" onclick="switchTab('form')">📝 ثبت/ویرایش</button>
                <button class="tab" onclick="switchTab('list')">📋 بیماران ثبت شده</button>
            </div>

            <div id="tab-form" class="tab-content active">
                <div class="main-grid">
                    <div class="form-panel">
                        <div class="form-title">👤 اطلاعات بیمار</div>
                        <form id="blood-form">
                            <input type="hidden" name="shift_id" value="{shift_id}">
                            <input type="hidden" name="edit_id" id="edit_id" value="">

                            <div class="form-group">
                                <label>نام بیمار</label>
                                <input type="text" name="patient_name" id="patient_name" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label>شماره پرونده</label>
                                <input type="text" name="file_number" id="file_number" class="form-input">
                            </div>
                            <div class="form-group">
                                <label>بخش</label>
                                <select name="dept_id" id="dept_id" class="form-select" required>
                                    {dept_options}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>گروه خونی بیمار</label>
                                <select name="blood_group" id="blood_group" class="form-select">
                                    {bg_options}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>توضیحات واکنش‌ها</label>
                                <input type="text" name="reaction_note" id="reaction_note" class="form-input">
                            </div>
                        </form>
                    </div>

                    <div class="form-panel">
                        <div class="form-title">📦 فرآورده‌های خونی</div>
                        <div class="product-list" id="product-list">
                            <p style="color:var(--light-gray);">هنوز فرآورده‌ای اضافه نشده است</p>
                        </div>
                        <div class="add-product-row">
                            <select id="product-type" class="form-select" style="flex:2;">
                                {''.join([f'<option value="{p}">{p}</option>' for p in PRODUCT_TYPES])}
                            </select>
                            <select id="product-group" class="form-select" style="flex:1;">
                                {bg_options}
                            </select>
                            <input type="number" id="product-count" class="form-input" value="1" min="1" max="10" style="width:70px;">
                            <select id="product-reaction" class="form-select" style="flex:1;">
                                <option value="0">ندارد</option>
                                <option value="1">دارد</option>
                            </select>
                            <button type="button" class="btn btn-primary btn-sm" onclick="addProduct()">➕ افزودن</button>
                        </div>
                        <div style="margin-top:25px;">
                            <button type="button" class="btn btn-primary" style="width:100%;" onclick="submitForm()">
                                <span id="save-text">💾 ثبت نهایی</span>
                                <span id="save-loading" style="display:none;">⏳ ...</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div id="tab-list" class="tab-content">
                <div class="list-panel" id="patients-list">
                    {_build_patients_html(patients)}
                </div>
            </div>
        </div>

        <script>
            var products = [];

            function switchTab(tab) {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                if (tab === 'form') {{
                    document.querySelectorAll('.tab')[0].classList.add('active');
                    document.getElementById('tab-form').classList.add('active');
                }} else {{
                    document.querySelectorAll('.tab')[1].classList.add('active');
                    document.getElementById('tab-list').classList.add('active');
                }}
            }}

            function showToast(msg, type) {{
                var c = document.getElementById('toast-container');
                var t = document.createElement('div');
                t.className = 'toast ' + (type||'info');
                t.innerHTML = '<span>' + (type==='success'?'✅':'❌') + '</span><span>' + msg + '</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>';
                c.appendChild(t);
                setTimeout(function(){{ if(t.parentElement){{ t.style.opacity='0'; setTimeout(function(){{t.remove()}},300); }} }}, 4000);
            }}

            function renderProducts() {{
                var list = document.getElementById('product-list');
                var html = '';
                products.forEach(function(p, idx) {{
                    html += '<div class="product-item">';
                    html += '<span>' + p.type + '</span>';
                    html += '<span>' + p.group + '</span>';
                    html += '<span>' + p.count + ' واحد</span>';
                    html += '<span>' + (p.reaction == 1 ? '⚠️ واکنش دارد' : '✅ بدون واکنش') + '</span>';
                    html += '<button type="button" class="btn btn-danger btn-xs" onclick="removeProduct(' + idx + ')">🗑️</button>';
                    html += '</div>';
                }});
                list.innerHTML = html || '<p style="color:var(--light-gray);">هنوز فرآورده‌ای اضافه نشده است</p>';
            }}

            function addProduct() {{
                var type = document.getElementById('product-type').value;
                var group = document.getElementById('product-group').value;
                var count = document.getElementById('product-count').value;
                var reaction = document.getElementById('product-reaction').value;
                products.push({{ type: type, group: group, count: count, reaction: reaction }});
                renderProducts();
            }}

            function removeProduct(idx) {{
                products.splice(idx, 1);
                renderProducts();
            }}

            function submitForm() {{
                var form = document.getElementById('blood-form');
                var formData = new FormData(form);
                formData.append('products', JSON.stringify(products));

                var patientName = document.getElementById('patient_name').value;
                var deptId = document.getElementById('dept_id').value;
                if (!patientName || !deptId) {{
                    showToast('⛔ نام بیمار و بخش الزامی است', 'error');
                    return;
                }}
                if (products.length === 0) {{
                    showToast('⛔ حداقل یک فرآورده اضافه کنید', 'error');
                    return;
                }}

                document.getElementById('save-text').style.display = 'none';
                document.getElementById('save-loading').style.display = 'inline';

                fetch('/module/supervisor/blood/save', {{
                    method: 'POST',
                    body: formData
                }})
                .then(function(r) {{ return r.json(); }})
                .then(function(data) {{
                    document.getElementById('save-text').style.display = 'inline';
                    document.getElementById('save-loading').style.display = 'none';
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
                    showToast('⛔ خطا در ارتباط با سرور', 'error');
                }});
            }}

            function editPatient(bloodId) {{
                fetch('/module/supervisor/blood/get/' + bloodId)
                .then(function(r) {{ return r.json(); }})
                .then(function(data) {{
                    if (data.success) {{
                        document.getElementById('edit_id').value = data.record.ID_blood;
                        document.getElementById('patient_name').value = data.record.nam_bimar;
                        document.getElementById('file_number').value = data.record.shomar_parvandeh || '';
                        document.getElementById('dept_id').value = data.record.nam_bakhsh;
                        document.getElementById('blood_group').value = data.record.groh_khoni_bimar;
                        document.getElementById('reaction_note').value = data.record.vakonsh_tavzih || '';
                        products = data.products || [];
                        renderProducts();
                        switchTab('form');
                        window.scrollTo({{ top: 0, behavior: 'smooth' }});
                    }} else {{
                        showToast('⛔ خطا در دریافت اطلاعات', 'error');
                    }}
                }});
            }}

            function deletePatient(bloodId) {{
                if (!confirm('آیا از حذف این بیمار و تمام فرآورده‌هایش اطمینان دارید؟')) return;
                var formData = new FormData();
                formData.append('blood_id', bloodId);
                fetch('/module/supervisor/blood/delete', {{
                    method: 'POST',
                    body: formData
                }})
                .then(function(r) {{ return r.json(); }})
                .then(function(data) {{
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
    </html>
    '''
    return html


def _build_patients_html(patients):
    if not patients:
        return '<p style="text-align:center;color:var(--light-gray);padding:30px;">📭 بیمار ثبت شده‌ای وجود ندارد</p>'

    html = ''
    for p in patients:
        html += f'''
        <div class="patient-item">
            <div class="patient-name">👤 {p['nam_bimar']}</div>
            <div class="patient-file">📁 پرونده: {p['shomar_parvandeh'] or '---'}</div>
            <div class="patient-actions">
                <button class="btn btn-sm btn-primary" onclick="editPatient({p['ID_blood']})">✏️ ویرایش</button>
                <button class="btn btn-sm btn-danger" onclick="deletePatient({p['ID_blood']})">🗑️ حذف</button>
            </div>
        </div>
        '''
    return html


def save_blood(user, form_data):
    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id')
    edit_id = form_data.get('edit_id')
    name = form_data.get('patient_name')
    file_num = form_data.get('file_number')
    dept_id = form_data.get('dept_id')
    bg = form_data.get('blood_group')
    react_note = form_data.get('reaction_note')
    products_json = form_data.get('products', '[]')

    try:
        products = json.loads(products_json)
    except:
        products = []

    if not name or not dept_id:
        return {'success': False, 'message': 'نام بیمار و بخش الزامی است'}
    if not products:
        return {'success': False, 'message': 'حداقل یک فرآورده اضافه کنید'}

    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()

    # برای ثبت، از connection مستقیم استفاده می‌کنیم تا بتوانیم lastrowid را بگیریم
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if edit_id:
            cursor.execute("""
                UPDATE tbl_blood_trans SET
                    nam_bimar=%s, shomar_parvandeh=%s, nam_bakhsh=%s,
                    groh_khoni_bimar=%s, vakonsh_tavzih=%s, nam_shift=%s
                WHERE ID_blood=%s
            """, (name, file_num, dept_id, bg, react_note, shift_id, edit_id))
            cursor.execute("DELETE FROM tbl_blood_faravardeh WHERE bloodT_key=%s", (edit_id,))
            blood_id = int(edit_id)
        else:
            cursor.execute("""
                INSERT INTO tbl_blood_trans
                (dat_sabt, groh_khoni_bimar, nam_bakhsh, nam_bimar, nam_shift,
                 shomar_parvandeh, UserID, vakonsh_tavzih, zaman_sabt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (today, bg, dept_id, name, shift_id, file_num, user_id, react_note, now))
            blood_id = cursor.lastrowid

        for p in products:
            cursor.execute("""
                INSERT INTO tbl_blood_faravardeh
                (bloodT_key, dat_sabt, groh_khoni_f, `nam_faravardeh`, teda_vahed,
                 UserID, vakonsh, zaman_sabt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (blood_id, today, p['group'], p['type'], p['count'], user_id, int(p['reaction']), now))

        conn.commit()

        log_crud('save_blood', user_id, key_value=blood_id,
                 new_value=f"بیمار:{name}, بخش:{dept_id}, فرآورده‌ها:{len(products)}")        
        return {'success': True, 'message': 'اطلاعات با موفقیت ثبت شد'}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'خطا: {str(e)}'}
    finally:
        cursor.close()
        conn.close()


def get_blood_record(blood_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tbl_blood_trans WHERE ID_blood = %s", (blood_id,))
        record = cursor.fetchone()
        if not record:
            return {'success': False, 'message': 'رکورد یافت نشد'}

        cursor.execute("SELECT * FROM tbl_blood_faravardeh WHERE bloodT_key = %s", (blood_id,))
        products_rows = cursor.fetchall()

        products_list = []
        for p in products_rows:
            products_list.append({
                'type': p['nam_faravardeh'],
                'group': p['groh_khoni_f'],
                'count': p['teda_vahed'],
                'reaction': p['vakonsh']
            })

        # Convert bytearray fields if necessary
        for key in list(record.keys()):
            if isinstance(record[key], bytearray):
                record[key] = record[key].decode('utf-8')

        return {
            'success': True,
            'record': record,
            'products': products_list
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        cursor.close()
        conn.close()


def delete_blood(user, form_data):
    user_id = user.get('UserID', 0)
    blood_id = form_data.get('blood_id')
    if not blood_id:
        return {'success': False, 'message': 'شناسه نامعتبر'}
    try:
        query("DELETE FROM tbl_blood_faravardeh WHERE bloodT_key = %s", (blood_id,), commit=True)
        query("DELETE FROM tbl_blood_trans WHERE ID_blood = %s", (blood_id,), commit=True)
        log_crud('delete_blood', user_id, key_value=blood_id)
        return {'success': True, 'message': 'رکورد حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}