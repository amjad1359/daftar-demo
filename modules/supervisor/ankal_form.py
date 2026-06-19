"""
فرم ثبت آنکالی پزشکان - سوپروایزر
نسخه کامل Flask با Toast Notification
"""

from models.database import query
import jdatetime
from datetime import datetime
import json
from utils.auto_log import log_crud

# ==========================================
# ۱. تابع اصلی نمایش فرم آنکال
# ==========================================

def get_ankal_form(user, message=None, error=None):
    """فرم مدیریت آنکالی پزشکان"""
    
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')
    
    # ========== دریافت شیفت فعال ==========
    active_shift = query(
        "SELECT ID_shift, tarkib, nam_shift FROM shift_namt ORDER BY ID_shift DESC LIMIT 1",
        fetch_one=True
    )
    
    if not active_shift:
        return '''
        <div class="content-card fade-in">
            <div style="text-align:center;padding:60px 20px;">
                <div style="font-size:64px;margin-bottom:15px;">⚠️</div>
                <h3 style="color:#1e293b;">شیفت فعالی یافت نشد</h3>
                <p style="color:#94a3b8;margin-bottom:25px;">لطفاً ابتدا یک شیفت ثبت کنید</p>
                <a href="/module/supervisor/shift" class="btn btn-primary btn-lg">📅 ثبت شیفت جدید</a>
            </div>
        </div>
        '''
    
    shift_id = active_shift['ID_shift']
    shift_name = active_shift['tarkib'] or active_shift.get('nam_shift', '---')
    
    # ========== دریافت لیست تخصص‌های آنکال ==========
    specialties = query(
        "SELECT ID_onvan_takhasos, nam_takhasos FROM tbl_onvan_takhasos WHERE IS_Ankal = 1 ORDER BY nam_takhasos",
        fetch_all=True
    )
    
    if not specialties:
        specialties = []
    
    # ========== گزینه‌های تخصص ==========
    spec_options = '<option value="">--- انتخاب تخصص ---</option>'
    for spec in specialties:
        spec_options += f'<option value="{spec["ID_onvan_takhasos"]}">{spec["nam_takhasos"]}</option>'
    
    # ========== ساخت JSON تخصص‌ها و پزشکان ==========
    specialties_json = _build_specialties_json(specialties)
    
    # ========== لیست آنکال‌های ثبت شده در این شیفت ==========
    ankal_list = query("""
        SELECT a.ID_ankal, a.no_rispons, a.tozihat,
               CONCAT(p.nam, ' ', p.famil) as dr_name,
               t.nam_takhasos,
               a.zaman_sabt
        FROM tbl_ankal a
        JOIN tbl_onvan_takhasos t ON a.nam_takhasos = t.ID_onvan_takhasos
        JOIN tbl_person p ON a.nam_pezshk = p.ID_person
        WHERE a.nam_shift = %s
        ORDER BY a.ID_ankal DESC
    """, params=(shift_id,), fetch_all=True)
    
    # ========== آمار ==========
    total_ankal = len(ankal_list) if ankal_list else 0
    no_response = sum(1 for a in ankal_list if a['no_rispons'] == 1) if ankal_list else 0
    responded = total_ankal - no_response
    
    # ========== HTML ==========
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --primary: #1e3a8a;
                --primary-light: #3b82f6;
                --success: #10b981;
                --danger: #ef4444;
                --warning: #f59e0b;
                --dark: #1e293b;
                --gray: #64748b;
                --light-gray: #94a3b8;
                --border: #e2e8f0;
                --bg-light: #f8fafc;
                --radius: 12px;
                --transition: 0.2s ease;
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; background: #f1f5f9; color: var(--dark); }}
            
            .fade-in {{ animation: fadeIn 0.4s ease; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            .content-card {{ max-width: 1400px; margin: 0 auto; }}
            
            /* ==================== هدر ==================== */
            .ankal-header {{
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                color: white;
                padding: 25px 30px;
                border-radius: 16px;
                margin-bottom: 25px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 8px 30px rgba(79, 70, 229, 0.25);
            }}
            .ankal-header h2 {{ font-size: 22px; margin: 0 0 5px 0; }}
            .ankal-header p {{ opacity: 0.85; font-size: 13px; margin: 0; }}
            .shift-badge {{
                background: rgba(255,255,255,0.15);
                padding: 10px 20px;
                border-radius: 30px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid rgba(255,255,255,0.2);
            }}
            .back-btn {{
                color: white; text-decoration: none;
                padding: 8px 16px; border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px; font-size: 13px; transition: var(--transition);
            }}
            .back-btn:hover {{ background: rgba(255,255,255,0.15); }}
            
            /* ==================== KPI ==================== */
            .kpi-row {{
                display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;
            }}
            .kpi-card {{
                background: white; border-radius: 14px; padding: 20px; text-align: center;
                border: 1px solid var(--border); transition: var(--transition);
            }}
            .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }}
            .kpi-value {{ font-size: 28px; font-weight: bold; }}
            .kpi-label {{ font-size: 12px; color: var(--gray); margin-top: 4px; }}
            
            /* ==================== چیدمان اصلی ==================== */
            .main-grid {{
                display: grid; grid-template-columns: 1fr 1.2fr; gap: 25px;
            }}
            
            /* ==================== پنل ثبت ==================== */
            .register-panel {{
                background: white; border-radius: 14px; padding: 25px;
                border: 1px solid var(--border);
            }}
            .panel-title {{
                font-size: 16px; font-weight: bold; color: var(--dark);
                margin-bottom: 20px; padding-bottom: 12px;
                border-bottom: 2px solid var(--border);
                display: flex; align-items: center; gap: 8px;
            }}
            
            .form-group {{ margin-bottom: 18px; }}
            .form-group label {{
                display: block; font-size: 13px; font-weight: 600;
                color: var(--gray); margin-bottom: 6px;
            }}
            .form-select, .form-input {{
                width: 100%; padding: 12px 14px; border: 2px solid var(--border);
                border-radius: 10px; font-size: 14px; font-family: Tahoma;
                background: white; transition: var(--transition);
            }}
            .form-select:focus, .form-input:focus {{
                border-color: var(--primary-light); outline: none;
                box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
            }}
            .form-select:disabled, .form-input:disabled {{
                background: #f1f5f9; color: #94a3b8; cursor: not-allowed;
            }}
            
            /* ==================== رادیو باتن ==================== */
            .radio-group {{
                display: flex; gap: 10px;
            }}
            .radio-option {{
                flex: 1;
            }}
            .radio-option input {{ display: none; }}
            .radio-option label {{
                display: flex; align-items: center; justify-content: center; gap: 6px;
                padding: 12px; border: 2px solid var(--border); border-radius: 10px;
                cursor: pointer; font-weight: 600; font-size: 13px; transition: var(--transition);
                text-align: center;
            }}
            .radio-option input:checked + label.response-yes {{
                border-color: var(--success); background: #d1fae5; color: #065f46;
            }}
            .radio-option input:checked + label.response-no {{
                border-color: var(--danger); background: #fee2e2; color: #991b1b;
            }}
            .radio-option label:hover {{ border-color: var(--primary-light); }}
            
            /* ==================== دکمه‌ها ==================== */
            .btn {{
                display: inline-flex; align-items: center; justify-content: center; gap: 6px;
                padding: 12px 24px; border: none; border-radius: 10px;
                font-size: 14px; font-weight: 600; cursor: pointer;
                font-family: Tahoma; transition: var(--transition); text-decoration: none;
            }}
            .btn-primary {{
                background: linear-gradient(135deg, var(--primary), var(--primary-light));
                color: white; box-shadow: 0 4px 15px rgba(30,58,138,0.2);
            }}
            .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(30,58,138,0.3); }}
            .btn-danger {{ background: var(--danger); color: white; }}
            .btn-danger:hover {{ background: #dc2626; }}
            .btn-sm {{ padding: 6px 12px; font-size: 12px; border-radius: 8px; }}
            .btn-xs {{ padding: 4px 10px; font-size: 11px; border-radius: 6px; }}
            
            /* ==================== لیست آنکال‌ها ==================== */
            .list-panel {{
                background: white; border-radius: 14px; padding: 25px;
                border: 1px solid var(--border); max-height: 600px; overflow-y: auto;
            }}
            
            .ankal-item {{
                background: var(--bg-light); border: 1px solid var(--border);
                border-radius: 10px; padding: 15px; margin-bottom: 10px;
                transition: var(--transition);
            }}
            .ankal-item:hover {{ border-color: var(--primary-light); }}
            .ankal-item.status-ok {{ border-right: 4px solid var(--success); }}
            .ankal-item.status-no {{ border-right: 4px solid var(--danger); }}
            
            .ankal-item-header {{
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 8px;
            }}
            .ankal-doctor-name {{ font-weight: bold; font-size: 14px; color: var(--dark); }}
            .ankal-specialty {{
                font-size: 12px; color: var(--primary-light);
                background: #dbeafe; padding: 3px 10px; border-radius: 15px;
            }}
            .ankal-status {{
                font-size: 12px; padding: 3px 10px; border-radius: 15px; font-weight: 600;
            }}
            .ankal-status.ok {{ background: #d1fae5; color: #065f46; }}
            .ankal-status.no {{ background: #fee2e2; color: #991b1b; }}
            
            .ankal-item-details {{
                display: flex; justify-content: space-between; align-items: center;
                font-size: 12px; color: var(--gray);
            }}
            
            .ankal-item-actions {{
                display: flex; gap: 5px; margin-top: 8px;
            }}
            
            .edit-inline {{
                display: none; margin-top: 10px; padding-top: 10px;
                border-top: 1px dashed var(--border);
            }}
            .edit-inline.show {{ display: block; }}
            
            .empty-list {{
                text-align: center; padding: 40px 20px; color: var(--light-gray);
            }}
            
            /* ==================== Toast ==================== */
            .toast-container {{
                position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
                z-index: 10000; display: flex; flex-direction: column; gap: 10px;
                pointer-events: none;
            }}
            .toast {{
                display: flex; align-items: center; gap: 12px;
                padding: 14px 22px; border-radius: 12px; color: white;
                font-size: 14px; font-weight: 600;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                animation: slideDown 0.4s ease;
                pointer-events: auto;
            }}
            .toast.success {{ background: linear-gradient(135deg, #059669, #10b981); }}
            .toast.error {{ background: linear-gradient(135deg, #dc2626, #ef4444); }}
            .toast .toast-close {{
                margin-right: auto; cursor: pointer; opacity: 0.7; font-size: 16px;
            }}
            .toast .toast-close:hover {{ opacity: 1; }}
            
            @keyframes slideDown {{
                from {{ opacity: 0; transform: translateY(-30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            /* ==================== رسپانسیو ==================== */
            @media (max-width: 992px) {{
                .main-grid {{ grid-template-columns: 1fr; }}
                .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
            }}
            @media (max-width: 576px) {{
                .ankal-header {{ flex-direction: column; gap: 15px; text-align: center; }}
                .radio-group {{ flex-direction: column; }}
            }}
        </style>
    </head>
    <body>
        
        <!-- ==================== Toast ==================== -->
        <div class="toast-container" id="toast-container"></div>
        
        <div class="content-card fade-in">
            
            <!-- هدر -->
            <div class="ankal-header">
                <div>
                    <h2>📞 مدیریت آنکالی پزشکان</h2>
                    <p>ثبت و پیگیری وضعیت پاسخگویی پزشکان در شیفت جاری</p>
                </div>
                <div style="display:flex;align-items:center;gap:15px;">
                    <span class="shift-badge">🕒 شیفت: {shift_name}</span>
                    <a href="/module/supervisor" class="back-btn">⬅️ بازگشت</a>
                </div>
            </div>
            
            <!-- KPI -->
            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-icon">📋</div>
                    <div class="kpi-value" style="color:#3b82f6;">{total_ankal}</div>
                    <div class="kpi-label">کل آنکال‌ها</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">✅</div>
                    <div class="kpi-value" style="color:#10b981;">{responded}</div>
                    <div class="kpi-label">پاسخگو</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">⚠️</div>
                    <div class="kpi-value" style="color:#ef4444;">{no_response}</div>
                    <div class="kpi-label">عدم پاسخ</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-value" style="color:#7c3aed;">{int(responded/total_ankal*100) if total_ankal > 0 else 0}%</div>
                    <div class="kpi-label">پاسخگویی</div>
                </div>
            </div>
            
            <!-- چیدمان اصلی -->
            <div class="main-grid">
                
                <!-- پنل ثبت -->
                <div class="register-panel">
                    <div class="panel-title">📝 ثبت آنکال جدید</div>
                    
                    <form id="ankal-form">
                        <input type="hidden" name="shift_id" value="{shift_id}">
                        
                        <div class="form-group">
                            <label>🩺 تخصص پزشک</label>
                            <select name="specialty_id" id="specialty-select" class="form-select" onchange="loadDoctors()">
                                {spec_options}
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>👨‍⚕️ پزشک</label>
                            <select name="doctor_id" id="doctor-select" class="form-select" disabled>
                                <option value="">ابتدا تخصص را انتخاب کنید</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>🔔 وضعیت پاسخگویی</label>
                            <div class="radio-group">
                                <div class="radio-option">
                                    <input type="radio" name="response_status" value="0" id="resp-ok" checked>
                                    <label for="resp-ok" class="response-yes">✅ پاسخگو</label>
                                </div>
                                <div class="radio-option">
                                    <input type="radio" name="response_status" value="1" id="resp-no">
                                    <label for="resp-no" class="response-no">❌ عدم پاسخ</label>
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>📝 توضیحات</label>
                            <input type="text" name="description" class="form-input" 
                                   placeholder="توضیحات تکمیلی...">
                        </div>
                        
                        <button type="submit" class="btn btn-primary" style="width:100%;" id="save-btn">
                            <span id="save-text">💾 ثبت نهایی آنکال</span>
                            <span id="save-loading" style="display:none;">⏳ در حال ذخیره...</span>
                        </button>
                    </form>
                </div>
                
                <!-- پنل لیست -->
                <div class="list-panel">
                    <div class="panel-title">📋 لیست آنکال‌های این شیفت <span style="font-size:12px;color:var(--gray);font-weight:normal;">({total_ankal} مورد)</span></div>
                    
                    {_build_ankal_list_html(ankal_list)}
                </div>
                
            </div>
            
        </div>
        
        <!-- ==================== داده‌های JSON ==================== -->
        <script>
            var specialtiesData = {specialties_json};
            
            // ========== Toast ==========
            function showToast(message, type) {{
                var container = document.getElementById('toast-container');
                var icons = {{ success: '✅', error: '❌', info: 'ℹ️' }};
                
                var toast = document.createElement('div');
                toast.className = 'toast ' + (type || 'info');
                toast.innerHTML = 
                    '<span>' + (icons[type] || '') + '</span>' +
                    '<span>' + message + '</span>' +
                    '<span class="toast-close" onclick="this.parentElement.remove()">✕</span>';
                
                container.appendChild(toast);
                
                setTimeout(function() {{
                    if (toast.parentElement) {{
                        toast.style.animation = 'slideUp 0.3s ease forwards';
                        setTimeout(function() {{ toast.remove(); }}, 300);
                    }}
                }}, 4000);
            }}
            
            // ========== لود پزشکان ==========
            function loadDoctors() {{
                var specId = document.getElementById('specialty-select').value;
                var doctorSelect = document.getElementById('doctor-select');
                
                doctorSelect.innerHTML = '<option value="">--- انتخاب پزشک ---</option>';
                doctorSelect.disabled = true;
                
                if (!specId || !specialtiesData[specId]) return;
                
                var doctors = specialtiesData[specId].doctors;
                
                if (doctors.length === 0) {{
                    doctorSelect.innerHTML = '<option value="">پزشکی در این تخصص یافت نشد</option>';
                    return;
                }}
                
                doctors.forEach(function(doc) {{
                    doctorSelect.innerHTML += '<option value="' + doc.ID_person + '">' + doc.full_name + '</option>';
                }});
                
                doctorSelect.disabled = false;
            }}
            
            // ========== ثبت با AJAX ==========
            document.getElementById('ankal-form').addEventListener('submit', function(e) {{
                e.preventDefault();
                
                var specId = document.getElementById('specialty-select').value;
                var docId = document.getElementById('doctor-select').value;
                
                if (!specId) {{ showToast('⛔ لطفاً تخصص را انتخاب کنید', 'error'); return; }}
                if (!docId) {{ showToast('⛔ لطفاً پزشک را انتخاب کنید', 'error'); return; }}
                
                var formData = new FormData(this);
                
                document.getElementById('save-text').style.display = 'none';
                document.getElementById('save-loading').style.display = 'inline';
                document.getElementById('save-btn').disabled = true;
                
                fetch('/module/supervisor/ankal/save', {{
                    method: 'POST',
                    body: formData
                }})
                .then(function(r) {{ return r.json(); }})
                .then(function(data) {{
                    document.getElementById('save-text').style.display = 'inline';
                    document.getElementById('save-loading').style.display = 'none';
                    document.getElementById('save-btn').disabled = false;
                    
                    if (data.success) {{
                        showToast('✅ ' + data.message, 'success');
                        setTimeout(function() {{ location.reload(); }}, 1000);
                    }} else {{
                        showToast('⛔ ' + data.message, 'error');
                    }}
                }})
                .catch(function() {{
                    document.getElementById('save-text').style.display = 'inline';
                    document.getElementById('save-loading').style.display = 'none';
                    document.getElementById('save-btn').disabled = false;
                    showToast('⛔ خطا در ارتباط با سرور', 'error');
                }});
            }});
            
            // ========== ویرایش inline ==========
            function toggleEdit(ankalId) {{
                var editDiv = document.getElementById('edit-' + ankalId);
                editDiv.classList.toggle('show');
            }}
            
            function saveEdit(ankalId) {{
                var status = document.getElementById('edit-status-' + ankalId).value;
                var desc = document.getElementById('edit-desc-' + ankalId).value;
                
                var formData = new FormData();
                formData.append('ankal_id', ankalId);
                formData.append('response_status', status);
                formData.append('description', desc);
                
                fetch('/module/supervisor/ankal/update', {{
                    method: 'POST',
                    body: formData
                }})
                .then(function(r) {{ return r.json(); }})
                .then(function(data) {{
                    if (data.success) {{
                        showToast('✅ ' + data.message, 'success');
                        setTimeout(function() {{ location.reload(); }}, 800);
                    }} else {{
                        showToast('⛔ ' + data.message, 'error');
                    }}
                }});
            }}
            
            function deleteAnkal(ankalId) {{
                if (!confirm('آیا از حذف این آیتم اطمینان دارید؟')) return;
                
                var formData = new FormData();
                formData.append('ankal_id', ankalId);
                
                fetch('/module/supervisor/ankal/delete', {{
                    method: 'POST',
                    body: formData
                }})
                .then(function(r) {{ return r.json(); }})
                .then(function(data) {{
                    if (data.success) {{
                        showToast('✅ ' + data.message, 'success');
                        setTimeout(function() {{ location.reload(); }}, 800);
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


# ==========================================
# ۲. ساخت JSON تخصص‌ها و پزشکان
# ==========================================

def _build_specialties_json(specialties):
    """ساخت JSON تخصص‌ها همراه با لیست پزشکان"""
    
    data = {}
    for spec in specialties:
        spec_id = spec['ID_onvan_takhasos']
        
        doctors = query("""
            SELECT ID_person, CONCAT(nam, ' ', famil) as full_name
            FROM tbl_person
            WHERE specialty_id = %s AND list_pezeshk = 1 AND isActiv = 1
            ORDER BY famil, nam
        """, params=(spec_id,), fetch_all=True)
        
        data[str(spec_id)] = {
            'name': spec['nam_takhasos'],
            'doctors': doctors if doctors else []
        }
    
    return json.dumps(data, ensure_ascii=False)


# ==========================================
# ۳. ساخت HTML لیست آنکال‌ها
# ==========================================

def _build_ankal_list_html(ankal_list):
    """ساخت HTML لیست آنکال‌های ثبت شده"""
    
    if not ankal_list:
        return '<div class="empty-list"><div style="font-size:40px;">📭</div><p>هیچ آیتمی ثبت نشده است</p></div>'
    
    html = ''
    for a in ankal_list:
        status_class = 'ok' if a['no_rispons'] == 0 else 'no'
        status_text = '✅ پاسخگو' if a['no_rispons'] == 0 else '❌ عدم پاسخ'
        time_str = str(a['zaman_sabt'])[:16] if a.get('zaman_sabt') else '-'
        
        html += f'''
        <div class="ankal-item status-{status_class}">
            <div class="ankal-item-header">
                <span class="ankal-doctor-name">{a['dr_name']}</span>
                <span class="ankal-specialty">🩺 {a['nam_takhasos']}</span>
            </div>
            
            <div class="ankal-item-details">
                <span class="ankal-status {status_class}">{status_text}</span>
                <span>{time_str}</span>
            </div>
            
            <div style="font-size:12px;color:var(--gray);margin-top:5px;">
                {a.get('tozihat', 'بدون توضیح')}
            </div>
            
            <div class="ankal-item-actions">
                <button class="btn btn-sm btn-primary" onclick="toggleEdit({a['ID_ankal']})">✏️ ویرایش</button>
                <button class="btn btn-sm btn-danger" onclick="deleteAnkal({a['ID_ankal']})">🗑️ حذف</button>
            </div>
            
            <div class="edit-inline" id="edit-{a['ID_ankal']}">
                <select id="edit-status-{a['ID_ankal']}" class="form-select" style="margin-bottom:8px;">
                    <option value="0" {"selected" if a['no_rispons'] == 0 else ""}>✅ پاسخگو</option>
                    <option value="1" {"selected" if a['no_rispons'] == 1 else ""}>❌ عدم پاسخ</option>
                </select>
                <input type="text" id="edit-desc-{a['ID_ankal']}" class="form-input" 
                       value="{a.get('tozihat', '')}" placeholder="توضیحات" style="margin-bottom:8px;">
                <button class="btn btn-sm btn-primary" onclick="saveEdit({a['ID_ankal']})">💾 ذخیره</button>
            </div>
        </div>
        '''
    
    return html


# ==========================================
# ۴. ذخیره آنکال جدید
# ==========================================

def save_ankal(user, form_data):
    user_id = user.get('UserID', 0)          # این خط نباید فراموش شود!
    shift_id = form_data.get('shift_id', '')
    specialty_id = form_data.get('specialty_id', '')
    doctor_id = form_data.get('doctor_id', '')
    response = form_data.get('response_status', '0')
    description = form_data.get('description', '')
    
    if not specialty_id:
        return {'success': False, 'message': 'تخصص انتخاب نشده'}
    if not doctor_id:
        return {'success': False, 'message': 'پزشک انتخاب نشده'}
    
    # 👇 جلوگیری از ثبت تکراری یک تخصص در یک شیفت
    existing = query(
        "SELECT ID_ankal FROM tbl_ankal WHERE nam_takhasos = %s AND nam_shift = %s",
        params=(specialty_id, shift_id),
        fetch_one=True
    )
    if existing:
        return {'success': False, 'message': 'این تخصص قبلاً در این شیفت ثبت شده است'}
    # 👆

    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now()
    
    try:
        query("""
            INSERT INTO tbl_ankal (nam_pezshk, nam_takhasos, nam_shift, no_rispons, tozihat, dat_sabt, zaman_sabt, UserID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, params=(doctor_id, specialty_id, shift_id, response, description, today, now, user_id), commit=True)
        
        log_crud('save_ankal', user_id, key_value=None,
                 new_value=f"پزشک:{doctor_id}, تخصص:{specialty_id}, وضعیت پاسخ:{response}")
        return {'success': True, 'message': 'آنکال با موفقیت ثبت شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


# ==========================================
# ۵. بروزرسانی آنکال
# ==========================================

def update_ankal(user, form_data):
    """بروزرسانی آنکال"""
    user_id = user.get('UserID', 0)
    ankal_id = form_data.get('ankal_id', '')
    response = form_data.get('response_status', '0')
    description = form_data.get('description', '')
    
    if not ankal_id:
        return {'success': False, 'message': 'شناسه نامعتبر'}
    
    try:
        query(
            "UPDATE tbl_ankal SET no_rispons = %s, tozihat = %s WHERE ID_ankal = %s",
            params=(response, description, ankal_id),
            commit=True
        )
        log_crud('update_ankal', user_id, key_value=ankal_id,
                 new_value=f"وضعیت پاسخ:{response}, توضیحات:{description}")        
        return {'success': True, 'message': 'بروزرسانی شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


# ==========================================
# ۶. حذف آنکال
# ==========================================

def delete_ankal(user, form_data):
    """حذف آنکال"""
    user_id = user.get('UserID', 0)
    ankal_id = form_data.get('ankal_id', '')
    
    if not ankal_id:
        return {'success': False, 'message': 'شناسه نامعتبر'}
    
    try:
        query("DELETE FROM tbl_ankal WHERE ID_ankal = %s", params=(ankal_id,), commit=True)
        log_crud('delete_ankal', user_id, key_value=ankal_id)
        return {'success': True, 'message': 'حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}